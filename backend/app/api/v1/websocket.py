from fastapi import APIRouter, WebSocket
import json

router = APIRouter()

@router.websocket("/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """Simple WebSocket endpoint for testing"""
    # Accept the connection
    await websocket.accept()
    print("Client connected!")
    
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            print(f"📨 Received: {data}")
            
            # Parse the message
            try:
                message_data = json.loads(data)
                user_message = message_data.get("content", "")
                
                # Echo back a simple response
                response = {
                    "type": "agent_message",
                    "content": f"You said: {user_message}",
                    "timestamp": message_data.get("timestamp")
                }
                
                # Send response back to client
                await websocket.send_text(json.dumps(response))
                print(f"Sent: {response}")
                
            except json.JSONDecodeError:
                # Handle invalid JSON
                error_response = {
                    "type": "error",
                    "message": "Invalid message format"
                }
                await websocket.send_text(json.dumps(error_response))
    
    except Exception as e:
        print(f"Connection closed: {e}")