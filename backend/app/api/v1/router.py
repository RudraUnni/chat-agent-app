from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1 import chat, conversations, users
from app.database.connection import get_db
from app.services.database.chat_service import DatabaseChatService
import uuid

# Create main API router
api_router = APIRouter()

@api_router.get("/")
async def api_root():
    return {"message": "Chat Agent API v1"}



# Include routers
api_router.include_router(users.router)
api_router.include_router(chat.router)
api_router.include_router(conversations.router)