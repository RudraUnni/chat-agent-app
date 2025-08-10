# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router

# Create FastAPI app
app = FastAPI(title="Chat Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # More specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chat Agent API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Include WebSocket directly (not under API prefix)
from app.api.v1.websocket import router as websocket_router
app.include_router(websocket_router, prefix="/ws")