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
from app.database.models import Message
from sqlalchemy.future import select
from sqlalchemy import func

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


async def store_message(conversation_id: str, role: str, content: str) -> None:
    """Store a message in the database"""
    async with AsyncSessionLocal() as db:
        try:
            # Get next sequence number
            stmt = select(func.coalesce(func.max(Message.sequence_number), 0) + 1).where(
                Message.conversation_id == conversation_id
            )
            result = await db.execute(stmt)
            sequence_number = result.scalar()
            
            # Create and store message
            message = Message(
                conversation_id=conversation_id,
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
            stmt = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
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
    session_id: Optional[str] = None
):
    """WebSocket endpoint for real-time chat with workflows"""
    
    # Get dependencies using the same pattern as REST endpoints
    from app.core.dependencies import get_workflow_registry, get_chat_manager
    workflow_registry = get_workflow_registry()
    chat_manager = get_chat_manager()
    
    # Generate session_id if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get or create session
    session = chat_manager.get_or_create_session(session_id)
    
    # Ensure database conversation exists
    await chat_manager.ensure_conversation_exists(session)
    
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
                    
                    try:
                        # Store user message in database
                        await store_message(session.conversation_id, "user", user_message)
                        
                        # Get conversation history
                        conversation_history = await get_conversation_history(session.conversation_id, limit=20)
                        logger.debug(f"Retrieved {len(conversation_history)} messages from history")
                        
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
                        
                        # Execute workflow with conversation history
                        input_data = {
                            'message': user_message,
                            'conversation_history': conversation_history,
                            **parameters
                        }
                        
                        result = await workflow.execute(input_data, session.context)
                        logger.debug(f"Workflow result: success={result.success}")
                        
                        if result.success:
                            response_text = extract_workflow_response(result, workflow_name)
                            
                            # Store assistant response in database
                            await store_message(session.conversation_id, "assistant", response_text)
                            
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
                        
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        error_response = {
                            "type": "error",
                            "content": "Failed to process message",
                            "timestamp": datetime.now().isoformat()
                        }
                        await manager.send_message(session_id, error_response)
                
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
