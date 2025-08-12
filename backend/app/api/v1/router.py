from fastapi import APIRouter
from app.api.v1 import chat

# Create main API router
api_router = APIRouter()

@api_router.get("/")
async def api_root():
    return {"message": "Chat Agent API v1"}

# Include chat router
api_router.include_router(chat.router)