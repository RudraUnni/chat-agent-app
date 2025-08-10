from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

# Create FastAPI app
app = FastAPI(title="Chat Agent API", version="1.0.0")

# Add CORS middleware with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Set to False for WebSocket
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chat Agent API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/")
async def api_root():
    return {"message": "API v1 is working"}

# WebSocket endpoint - simplified path
@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """Simple WebSocket endpoint for testing"""
    try:
        # Accept the connection
        await websocket.accept()
        print("✅ Client connected!")
        
        # Send welcome message
        welcome_msg = {
            "type": "system",
            "message": "Connected to chat server",
            "timestamp": "now"
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            print(f"📨 Received: {data}")
            
            # Parse the message
            try:
                message_data = json.loads(data)
                user_message = message_data.get("content", "")
                
                if user_message:
                    # Echo back a simple response
                    response = {
                        "type": "agent_message",
                        "content": f"Echo: {user_message}",
                        "timestamp": message_data.get("timestamp", "now")
                    }
                    
                    # Send response back to client
                    await websocket.send_text(json.dumps(response))
                    print(f"📤 Sent: {response}")
                
            except json.JSONDecodeError:
                print("❌ Invalid JSON received")
                error_response = {
                    "type": "error",
                    "message": "Invalid message format"
                }
                await websocket.send_text(json.dumps(error_response))
    
    except WebSocketDisconnect:
        print("🔌 Client disconnected normally")
    except Exception as e:
        print(f"❌ Connection error: {e}")