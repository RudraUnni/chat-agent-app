"""
User management endpoints for the chat application.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
import uuid

from app.database.connection import get_db
from app.services.database.chat_service import DatabaseChatService
from app.core.exceptions import DatabaseError

router = APIRouter(prefix="/users", tags=["users"])


class CreateUserRequest(BaseModel):
    """Request model for creating a user"""
    username: str
    email: str


class UserResponse(BaseModel):
    """Response model for user data"""
    id: str
    username: str
    email: str
    created_at: str


@router.get("/", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all users"""
    try:
        chat_service = DatabaseChatService(db)
        users = await chat_service.list_users()
        
        return [
            UserResponse(
                id=str(user.id),
                username=user.username,
                email=user.email,
                created_at=user.created_at.isoformat()
            )
            for user in users
        ]
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: CreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    try:
        chat_service = DatabaseChatService(db)
        user = await chat_service.create_user(user_data.username, user_data.email)
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
    except DatabaseError as e:
        if e.error_code == "USER_ALREADY_EXISTS":
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dummy", response_model=UserResponse)
async def create_dummy_user(db: AsyncSession = Depends(get_db)):
    """Create a dummy user for testing"""
    dummy_id = str(uuid.uuid4())[:8]
    username = f"test_user_{dummy_id}"
    email = f"test_{dummy_id}@example.com"
    
    try:
        chat_service = DatabaseChatService(db)
        user = await chat_service.create_user(username, email)
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
    except DatabaseError as e:
        if e.error_code == "USER_ALREADY_EXISTS":
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/default", response_model=UserResponse)
async def get_default_user(db: AsyncSession = Depends(get_db)):
    """Get the default test user"""
    try:
        from app.database.seed import get_default_user
        user = await get_default_user(db)
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get a user by ID"""
    try:
        user_uuid = uuid.UUID(user_id)
        chat_service = DatabaseChatService(db)
        user = await chat_service.get_user(user_uuid)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))