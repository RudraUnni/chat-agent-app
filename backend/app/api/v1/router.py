from fastapi import APIRouter
from app.api.v1 import chat, openwebui, auth_bridge

# Create main API router
api_router = APIRouter()

@api_router.get("/")
async def api_root():
    return {"message": "Medical Assistant API v1 - Now with Open WebUI Integration"}

# Include chat router
api_router.include_router(chat.router)

# Include Open WebUI integration router
api_router.include_router(openwebui.router)

# Include authentication bridge router
api_router.include_router(auth_bridge.router)