from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
import uuid

from app.database.connection import get_db
from app.services.database.chat_service import DatabaseChatService
from app.database.models import User

router = APIRouter(prefix="/users", tags=["users"])


class CreateUserRequest(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user for testing purposes"""
    chat_service = DatabaseChatService(db)
    
    try:
        user = await chat_service.create_user(request.username, request.email)
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all users"""
    from sqlalchemy.future import select
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
        for user in users
    ]


@router.post("/dummy", response_model=UserResponse)
async def create_dummy_user(db: AsyncSession = Depends(get_db)):
    """Create a dummy user for testing"""
    dummy_id = str(uuid.uuid4())[:8]
    username = f"test_user_{dummy_id}"
    email = f"test_{dummy_id}@example.com"
    
    chat_service = DatabaseChatService(db)
    user = await chat_service.create_user(username, email)
    
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        created_at=user.created_at.isoformat()
    )