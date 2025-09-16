# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.workflows.medical.runtime import Agent
from app.api.v1.router import api_router
from app.database.connection import init_db, close_db
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    print("Database initialized")
    
    yield
    
    # Shutdown
    await close_db()
    print("Database connections closed")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://localhost:3001",  # Open WebUI local
        "http://open-webui:8080",  # Open WebUI container internal
        "http://chatapp_open_webui:8080",  # Open WebUI container name
        "http://0.0.0.0:3001",  # Docker host binding
        "*"  # Allow all origins for OpenWebUI compatibility
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chat Agent API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Add OpenAI-compatible endpoints at root level for OpenWebUI discovery
@app.get("/models")
async def root_models():
    """Root level models endpoint for OpenWebUI compatibility"""
    return {
        "object": "list",
        "data": [
            {
                "id": "openai/gpt-4o-mini",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai",
                "permission": [],
                "root": "openai/gpt-4o-mini",
                "parent": None
            },
            {
                "id": "openai/gpt-4o",
                "object": "model", 
                "created": 1677610602,
                "owned_by": "openai",
                "permission": [],
                "root": "openai/gpt-4o",
                "parent": None
            },
            {
                "id": "medical-assistant",
                "object": "model",
                "created": 1677610602,
                "owned_by": "medical-assistant",
                "permission": [],
                "root": "medical-assistant",
                "parent": None
            }
        ]
    }

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Include OpenAI-compatible endpoints for OpenWebUI
from app.api.v1.chat import router as chat_router
app.include_router(chat_router, prefix="/v1", tags=["openai-compatible"])  # Standard OpenAI path for OpenWebUI

# Include WebSocket directly (not under API prefix)
from app.api.v1.websocket import router as websocket_router
app.include_router(websocket_router, prefix="/ws")