from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import uuid
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.workflow.registry import WorkflowRegistry
from app.services.chat.manager import ChatManager
from app.services.database.chat_service import DatabaseChatService
from app.services.conversation.context_builder import get_conversation_context
from app.database.connection import get_db
from app.workflows.base import WorkflowContext
from app.core.config import get_settings
from app.core.workflow_utils import extract_workflow_response, format_workflow_error

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

@router.websocket("/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time chat with workflows"""
    
    # Get dependencies using the same pattern as REST endpoints
    from app.core.dependencies import get_workflow_registry, get_chat_manager
    workflow_registry = get_workflow_registry()
    chat_manager = get_chat_manager()
    db_chat_service = DatabaseChatService(db)
    
    # Generate session_id if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get or create session
    session = chat_manager.get_or_create_session(session_id)
    
    # Create or get database conversation for this session
    conversation = None
    try:
        # For simplicity, create a default user for demo purposes
        # In production, this would come from authentication
        default_user_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
        
        # Try to create default user if it doesn't exist
        try:
            # Check if user exists, if not create it
            existing_user = await db_chat_service.get_user(default_user_id)
            if not existing_user:
                # Create user with specific ID
                await db_chat_service.create_user(
                    username="default_user",
                    email="default@example.com",
                    user_id=default_user_id
                )
        except Exception:
            # User probably already exists or creation failed, continue
            pass
        
        # Create a new conversation for this session
        conversation = await db_chat_service.create_conversation(
            user_id=default_user_id, 
            title=f"Chat Session {session_id[:8]}"
        )
        logger.info(f"Created conversation {conversation.id} for session {session_id}")
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        # Continue without database - fallback to in-memory only
        pass
    
    await manager.connect(session_id, websocket)
    logger.info(f"WebSocket connected: session_id={session_id}")
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "system",
            "content": "Connected to chat server",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_message(session_id, welcome_msg)
    except Exception:
        pass
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.debug(f"Received message: session_id={session_id}, data={data[:100]}...")
            
            try:
                message_data = json.loads(data)
                user_message = message_data.get("content", "")
                workflow_name = message_data.get("workflow", "pubmed_research")  # Default to Medical Assistant
                parameters = message_data.get("parameters", {})
                
                if user_message.strip():
                    logger.info(f"Processing: workflow={workflow_name}, message_length={len(user_message)}")
                    
                    # Store user message in database
                    if conversation:
                        try:
                            await db_chat_service.add_message(
                                conversation_id=conversation.id,
                                content=user_message,
                                role="user"
                            )
                            logger.debug(f"Stored user message in conversation {conversation.id}")
                        except Exception as e:
                            logger.error(f"Failed to store user message: {e}")
                    
                    # Get workflow
                    workflow = workflow_registry.get_workflow(workflow_name)
                    
                    if not workflow:
                        error_response = {
                            "type": "error",
                            "content": f"Workflow '{workflow_name}' not found",
                            "timestamp": datetime.now().isoformat()
                        }
                        await manager.send_message(session_id, error_response)
                        continue
                    
                    # Get conversation history and prepare context
                    context = session.context
                    if conversation:
                        try:
                            # Get recent messages for context
                            recent_messages = await db_chat_service.get_recent_messages(
                                conversation_id=conversation.id,
                                limit=10
                            )
                            
                            # Format conversation history for agent
                            conversation_history = get_conversation_context(
                                messages=recent_messages,
                                current_message=user_message,
                                max_messages=10
                            )
                            
                            # Update context with conversation history
                            context.history = conversation_history
                            logger.debug(f"Added {len(conversation_history)} messages to context")
                            
                        except Exception as e:
                            logger.error(f"Failed to retrieve conversation history: {e}")
                            # Continue without history if retrieval fails
                    
                    # Execute workflow
                    input_data = {
                        'message': user_message,
                        **parameters
                    }
                    
                    result = await workflow.execute(input_data, context)
                    logger.debug(f"Workflow result: success={result.success}")
                    
                    if result.success:
                        response_text = extract_workflow_response(result, workflow_name)
                        
                        # Store assistant response in database
                        if conversation:
                            try:
                                await db_chat_service.add_message(
                                    conversation_id=conversation.id,
                                    content=response_text,
                                    role="assistant"
                                )
                                logger.debug(f"Stored assistant response in conversation {conversation.id}")
                            except Exception as e:
                                logger.error(f"Failed to store assistant response: {e}")
                        
                        response = {
                            "type": "assistant",
                            "content": response_text,
                            "workflow": workflow_name,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_message = format_workflow_error(result, workflow_name)
                        response = {
                            "type": "error",
                            "content": error_message,
                            "timestamp": datetime.now().isoformat()
                        }
                    
                    await manager.send_message(session_id, response)
                
            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "content": "Invalid message format",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_message(session_id, error_response)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session_id={session_id}")
        manager.disconnect(session_id)
    except Exception as e:
        manager.error(f"WebSocket error: session_id={session_id}, error={e}")
        manager.disconnect(session_id)
