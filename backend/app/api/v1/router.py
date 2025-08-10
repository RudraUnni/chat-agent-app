from fastapi import APIRouter
from app.api.v1 import websocket

# Create main API router
api_router = APIRouter()

# Include WebSocket routes
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@api_router.get("/")
async def api_root():
    return {"message": "Chat Agent API v1"}