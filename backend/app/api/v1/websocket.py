from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import uuid
import logging
from datetime import datetime
from typing import Optional
from app.services.workflow.registry import WorkflowRegistry
from app.services.chat.manager import ChatManager
from app.services.llm.factory import LLMFactory
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
    session_id: Optional[str] = None
):
    """
    WebSocket endpoint for real-time chat with workflows and conversation history.
    
    Now maintains full conversation history per session and provides complete
    context to agents for coherent multi-turn conversations.
    
    Message format:
    {
        "content": "Your message here",
        "workflow": "pubmed_research",
        "parameters": {}
    }
    """
    
    # Get dependencies using the same pattern as REST endpoints
    from app.core.dependencies import get_workflow_registry, get_chat_manager
    workflow_registry = get_workflow_registry()
    chat_manager = get_chat_manager()
    
    # Generate session_id if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get or create session
    session = chat_manager.get_or_create_session(session_id)
    
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
                    
                    # Store user message in session history
                    session.add_user_message(user_message)
                    logger.debug(f"Added user message to session {session_id}. Total messages: {len(session.messages)}")
                    
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
                    
                    # Prepare input data with conversation history
                    input_data = {
                        'message': user_message,
                        'conversation_history': session.get_messages_for_agent(),
                        **parameters
                    }
                    
                    # Update context with conversation history
                    session.context.history = [
                        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat() if msg.timestamp else None}
                        for msg in session.get_conversation_history()
                    ]
                    
                    result = await workflow.execute(input_data, session.context)
                    logger.debug(f"Workflow result: success={result.success}")
                    
                    if result.success:
                        response_text = extract_workflow_response(result, workflow_name)
                        
                        # Store assistant response in session history
                        session.add_assistant_message(response_text)
                        logger.debug(f"Added assistant response to session {session_id}. Total messages: {len(session.messages)}")
                        
                        response = {
                            "type": "assistant",
                            "content": response_text,
                            "workflow": workflow_name,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_message = format_workflow_error(result, workflow_name)
                        
                        # Store error as assistant message for context
                        session.add_assistant_message(f"Error: {error_message}")
                        
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
        logger.error(f"WebSocket error: session_id={session_id}, error={e}")
        manager.disconnect(session_id)
