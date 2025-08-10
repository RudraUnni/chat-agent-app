# backend/app/api/v1/router.py
from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

@api_router.get("/")
async def api_root():
    return {"message": "Chat Agent API v1"}