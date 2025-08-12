# backend/app/api/v1/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from datetime import datetime

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"⚠️ Failed to send message: {e}")
            self.disconnect(websocket)
            raise

manager = ConnectionManager()

@router.websocket("/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat functionality"""
    await manager.connect(websocket)
    print("✅ Client connected!")
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "system",
            "content": "Connected to chat server",
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_personal_message(welcome_msg, websocket)
    except Exception as e:
        print(f"⚠️ Could not send welcome message: {e}")
        # Connection might already be closed, continue anyway
    
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            print(f"📨 Received: {data}")
            
            try:
                message_data = json.loads(data)
                user_message = message_data.get("content", "")
                
                if user_message.strip():
                    # Simple echo response (we'll replace this with agent logic later)
                    response = {
                        "type": "assistant",
                        "content": f"Echo: {user_message}",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    try:
                        await manager.send_personal_message(response, websocket)
                        print(f"📤 Sent: {response}")
                    except Exception:
                        print("❌ Failed to send response, client disconnected")
                        break
                
            except json.JSONDecodeError:
                print("❌ Invalid JSON received")
                error_response = {
                    "type": "error",
                    "content": "Invalid message format",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(error_response, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🔌 Client disconnected normally")
    except ConnectionResetError:
        manager.disconnect(websocket)
        print("🔌 Client connection reset")
    except Exception as e:
        manager.disconnect(websocket)
        if "no close frame received" not in str(e).lower():
            print(f"❌ Connection error: {e}")
