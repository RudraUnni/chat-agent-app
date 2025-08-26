from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1 import chat, conversations
from app.database.connection import get_db
from app.services.database.chat_service import DatabaseChatService
import uuid

# Create main API router
api_router = APIRouter()

@api_router.get("/")
async def api_root():
    return {"message": "Chat Agent API v1"}

@api_router.post("/users/dummy")
async def create_dummy_user(db: AsyncSession = Depends(get_db)):
    """Create a dummy user for testing"""
    dummy_id = str(uuid.uuid4())[:8]
    username = f"test_user_{dummy_id}"
    email = f"test_{dummy_id}@example.com"
    
    chat_service = DatabaseChatService(db)
    user = await chat_service.create_user(username, email)
    
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }

# Include routers
api_router.include_router(chat.router)
api_router.include_router(conversations.router)