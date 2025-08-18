from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import uuid
from datetime import datetime
from typing import Optional
from app.services.workflow.registry import WorkflowRegistry
from app.services.chat.manager import ChatManager
from app.services.llm.factory import LLMFactory
from app.core.config import get_settings
from app.core.workflow_utils import extract_workflow_response, format_workflow_error

settings = get_settings()

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
    
    await manager.connect(session_id, websocket)
    
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
            
            try:
                message_data = json.loads(data)
                user_message = message_data.get("content", "")
                workflow_name = message_data.get("workflow", "general_assistant")
                parameters = message_data.get("parameters", {})
                
                if user_message.strip():
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
                    
                    # Execute workflow
                    input_data = {
                        'message': user_message,
                        **parameters
                    }
                    
                    result = await workflow.execute(input_data, session.context)
                    
                    if result.success:
                        response_text = extract_workflow_response(result, workflow_name)
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
        manager.disconnect(session_id)
    except Exception as e:
        manager.disconnect(session_id)
        if "no close frame received" not in str(e).lower():
            print(f"Connection error: {e}")
