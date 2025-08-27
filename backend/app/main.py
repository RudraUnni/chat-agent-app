# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.database.connection import init_db, close_db
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 STARTING MINIMALISTIC HISTORY PERSISTENCE BACKEND")
    print("=" * 55)
    print(f"📋 Default user: {settings.default_user_username}")
    print(f"📧 Default email: {settings.default_user_email}")
    print(f"🗃️ Database: {settings.database_name}")
    print("=" * 55)
    
    await init_db()
    print("✅ Database initialized with default user")
    print("🎯 Ready for history persistence testing!")
    print("💡 Test: curl http://localhost:8000/api/v1/users/default")
    
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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Minimalistic History Persistence Backend", 
        "default_user": settings.default_user_username,
        "features": ["user_management", "history_persistence", "websocket_chat"],
        "endpoints": {
            "default_user": "/api/v1/users/default",
            "list_users": "/api/v1/users/",
            "websocket": "/ws/chat?user_id=<user_id>"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Include WebSocket directly (not under API prefix)
from app.api.v1.websocket import router as websocket_router
app.include_router(websocket_router, prefix="/ws")

# Show available endpoints for minimalistic testing
print("🔗 MINIMALISTIC HISTORY PERSISTENCE ENDPOINTS:")
key_routes = [
    ("GET", "/", "Root - shows backend info"),
    ("GET", "/api/v1/users/default", "Get default test user"),
    ("GET", "/api/v1/users/", "List all users"), 
    ("POST", "/api/v1/users/dummy", "Create dummy user"),
    ("WS", "/ws/chat", "WebSocket chat with history")
]
for method, path, desc in key_routes:
    print(f"   {method:4} {path:25} - {desc}")
print("🎯 Start testing with: curl http://localhost:8000/api/v1/users/default")