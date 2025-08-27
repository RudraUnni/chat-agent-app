from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict
from app.services.workflow.registry import WorkflowRegistry
from app.services.chat.manager import ChatManager
from app.services.llm.factory import LLMFactory
from app.core.config import get_settings
from app.core.workflow_utils import extract_workflow_response, format_workflow_error
from app.database.connection import AsyncSessionLocal
from app.database.models import Message, User
from sqlalchemy.future import select
from sqlalchemy import func
from uuid import UUID
import hashlib

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                self.disconnect(session_id)
                raise

manager = ConnectionManager()


def parse_conversation_id_for_websocket(conversation_id: str) -> str:
    """Parse conversation ID for WebSocket - convert custom formats to UUID strings"""
    try:
        # Try to parse as UUID first
        uuid_obj = UUID(conversation_id)
        return str(uuid_obj)
    except ValueError:
        # If not UUID, check if it's a custom format like conv_timestamp_random
        if conversation_id.startswith('conv_'):
            # Generate a deterministic UUID from the string
            namespace = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Standard namespace UUID
            uuid_obj = UUID(bytes=hashlib.md5(conversation_id.encode()).digest())
            return str(uuid_obj)
        else:
            # For other formats, generate a UUID from the string
            uuid_obj = UUID(bytes=hashlib.md5(conversation_id.encode()).digest())
            return str(uuid_obj)


async def get_or_create_default_test_user() -> str:
    """Get or create a default test user for development/testing purposes"""
    async with AsyncSessionLocal() as db:
        try:
            # Try to find existing default test user
            stmt = select(User).where(User.username == "default_test_user")
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                logger.info(f"Using existing default test user: {user.id}")
                return str(user.id)
            
            # Create new default test user
            user = User(
                username="default_test_user",
                email="test@example.com"
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Created new default test user: {user.id}")
            return str(user.id)
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to get/create default test user: {e}")
            raise


async def store_message(conversation_id: str, role: str, content: str) -> None:
    """Store a message in the database"""
    async with AsyncSessionLocal() as db:
        try:
            # Convert conversation_id to UUID
            conversation_uuid = UUID(conversation_id)
            
            # Get next sequence number
            stmt = select(func.coalesce(func.max(Message.sequence_number), 0) + 1).where(
                Message.conversation_id == conversation_uuid
            )
            result = await db.execute(stmt)
            sequence_number = result.scalar()
            
            # Create and store message
            message = Message(
                conversation_id=conversation_uuid,
                role=role,
                content=content,
                sequence_number=sequence_number
            )
            db.add(message)
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to store message: {e}")
            raise


async def get_conversation_history(conversation_id: str, limit: int = 20) -> List[Dict[str, str]]:
    """Retrieve conversation history formatted for agent"""
    async with AsyncSessionLocal() as db:
        try:
            # Convert conversation_id to UUID
            conversation_uuid = UUID(conversation_id)
            
            stmt = (
                select(Message)
                .where(Message.conversation_id == conversation_uuid)
                .order_by(Message.sequence_number.desc())
                .limit(limit)
            )
            result = await db.execute(stmt)
            messages = result.scalars().all()
            
            # Return in chronological order, formatted for agent
            return [
                {"role": msg.role, "content": msg.content}
                for msg in reversed(messages)
            ]
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []

@router.websocket("/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
):
    """WebSocket endpoint for real-time chat with workflows"""
    print(f"🚀🚀🚀 IMMEDIATE: WebSocket /chat endpoint HIT! session_id={session_id}, user_id={user_id}")
    logger.info(f"🚀 WebSocket endpoint /chat called with session_id={session_id}, user_id={user_id}")
    await websocket_chat_with_conversation(websocket, None, session_id, user_id)


@router.websocket("/chat/{conversation_id}")
async def websocket_chat_endpoint_with_conversation(
    websocket: WebSocket,
    conversation_id: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
):
    """WebSocket endpoint for real-time chat with specific conversation"""
    print(f"🎯🎯🎯 IMMEDIATE: WebSocket /chat/{conversation_id} endpoint HIT! session_id={session_id}, user_id={user_id}")
    await websocket_chat_with_conversation(websocket, conversation_id, session_id, user_id)


async def websocket_chat_with_conversation(
    websocket: WebSocket,
    conversation_id: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
):
    """WebSocket endpoint for real-time chat with workflows"""
    
    print(f"💥💥💥 IMMEDIATE: ENTERING websocket_chat_with_conversation: conversation_id={conversation_id}, session_id={session_id}, user_id={user_id}")
    logger.info(f"🔥 ENTERING websocket_chat_with_conversation: conversation_id={conversation_id}, session_id={session_id}, user_id={user_id}")
    
    # CRITICAL: Accept WebSocket connection FIRST before any other operations
    print(f"💥 ABOUT TO ACCEPT WebSocket connection: session_id={session_id}")
    logger.info(f"WebSocket connection attempt: session_id={session_id}")
    await websocket.accept()
    print(f"💥 WebSocket ACCEPTED successfully: session_id={session_id}")
    logger.info(f"WebSocket handshake completed successfully: session_id={session_id}")
    
    # Generate session_id if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session_id: {session_id}")
    
    # Use conversation_id if provided, otherwise use session_id
    if not conversation_id:
        conversation_id = session_id
        logger.info(f"Using session_id as conversation_id: {conversation_id}")
    else:
        # Parse and normalize conversation_id to UUID format
        conversation_id = parse_conversation_id_for_websocket(conversation_id)
        logger.info(f"Parsed conversation_id to UUID format: {conversation_id}")
    
    logger.info(f"WebSocket params: session_id={session_id}, conversation_id={conversation_id}, user_id={user_id}")
    
    # Get dependencies using the same pattern as REST endpoints
    from app.core.dependencies import get_workflow_registry, get_chat_manager
    workflow_registry = get_workflow_registry()
    chat_manager = get_chat_manager()
    
    # Setup session and database - MUST succeed for persistence to work
    session = None
    try:
        # If no user_id provided, use default test user for persistence
        if not user_id:
            user_id = await get_or_create_default_test_user()
            logger.info(f"No user_id provided, using default test user: {user_id}")
        
        # Get or create session with user_id and conversation_id
        session = chat_manager.get_or_create_session(session_id, user_id)
        session.conversation_id = conversation_id  # Override conversation_id
        logger.info(f"Session created/retrieved: session_id={session_id}, user_id={user_id}, conversation_id={conversation_id}")
        
        # Ensure database conversation exists - this should now always succeed
        await chat_manager.ensure_conversation_exists(session)
        logger.info(f"Database conversation ensured: conversation_id={session.conversation_id}")
        
    except Exception as e:
        logger.error(f"Failed to setup session/database for {session_id}: {e}")
        # Send error message to client and close connection
        error_msg = {
            "type": "error",
            "content": f"Failed to initialize conversation: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(error_msg))
        await websocket.close(code=1011, reason="Database setup failed")
        return
    
    # Register connection after accept
    manager.active_connections[session_id] = websocket
    logger.info(f"WebSocket registered: session_id={session_id}")
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "system",
            "content": "Connected to chat server",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_msg))
        logger.info(f"Welcome message sent: session_id={session_id}")
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")
        # Continue anyway
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print(f"💬💬💬 RECEIVED MESSAGE: session_id={session_id}, data={data[:100]}...")
            logger.debug(f"Received message: session_id={session_id}, data={data[:100]}...")
            
            try:
                message_data = json.loads(data)
                print(f"💬 PARSED MESSAGE: {message_data}")
                user_message = message_data.get("content", "")
                workflow_name = message_data.get("workflow", "pubmed_research")  # Default to Medical Assistant
                parameters = message_data.get("parameters", {})
                
                if user_message.strip():
                    print(f"💬 Processing message: workflow={workflow_name}, message_length={len(user_message)}")
                    logger.info(f"Processing: workflow={workflow_name}, message_length={len(user_message)}")
                    
                    try:
                        # Store user message in database (with fallback if DB fails)
                        conversation_history = []
                        print(f"💾 Attempting to store message in database...")
                        try:
                            await store_message(session.conversation_id, "user", user_message)
                            print(f"💾 Message stored successfully")
                            # Get conversation history
                            conversation_history = await get_conversation_history(session.conversation_id, limit=20)
                            print(f"📚 Retrieved {len(conversation_history)} messages from history")
                            logger.debug(f"Retrieved {len(conversation_history)} messages from history")
                        except Exception as db_error:
                            print(f"💾 Database operation failed: {db_error}")
                            logger.error(f"Database operation failed, continuing without history: {db_error}")
                        
                        # Get workflow
                        print(f"🔧 Getting workflow: {workflow_name}")
                        workflow = workflow_registry.get_workflow(workflow_name)
                        
                        if not workflow:
                            print(f"❌ Workflow '{workflow_name}' not found")
                            error_response = {
                                "type": "error",
                                "content": f"Workflow '{workflow_name}' not found",
                                "timestamp": datetime.now().isoformat()
                            }
                            await websocket.send_text(json.dumps(error_response))
                            continue
                        
                        # Execute workflow with conversation history
                        print(f"🚀 Executing workflow with {len(conversation_history)} history messages")
                        input_data = {
                            'message': user_message,
                            'conversation_history': conversation_history,
                            **parameters
                        }
                        
                        print(f"🚀 About to execute workflow...")
                        result = await workflow.execute(input_data, session.context)
                        print(f"🚀 Workflow executed: success={result.success}")
                        logger.debug(f"Workflow result: success={result.success}")
                        
                        if result.success:
                            print(f"✅ Workflow success, extracting response...")
                            response_text = extract_workflow_response(result, workflow_name)
                            print(f"📝 Response text length: {len(response_text)}")
                            
                            # Store assistant response in database (with fallback)
                            print(f"💾 Storing assistant response...")
                            try:
                                await store_message(session.conversation_id, "assistant", response_text)
                                print(f"💾 Assistant response stored successfully")
                            except Exception as db_error:
                                print(f"💾 Failed to store assistant response: {db_error}")
                                logger.error(f"Failed to store assistant response: {db_error}")
                            
                            response = {
                                "type": "assistant",
                                "content": response_text,
                                "workflow": workflow_name,
                                "timestamp": datetime.now().isoformat()
                            }
                            print(f"📤 Sending response to frontend: {len(response['content'])} chars")
                        else:
                            error_message = format_workflow_error(result, workflow_name)
                            response = {
                                "type": "error",
                                "content": error_message,
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        print(f"📤 About to send WebSocket response...")
                        await websocket.send_text(json.dumps(response))
                        print(f"✅ WebSocket response sent successfully")
                        
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        error_response = {
                            "type": "error",
                            "content": "Failed to process message",
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send_text(json.dumps(error_response))
                
            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "content": "Invalid message format",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(error_response))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session_id={session_id}")
        if session_id in manager.active_connections:
            del manager.active_connections[session_id]
    except Exception as e:
        logger.error(f"WebSocket error: session_id={session_id}, error={e}")
        if session_id in manager.active_connections:
            del manager.active_connections[session_id]
