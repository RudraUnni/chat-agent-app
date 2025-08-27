from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import Conversation, Message, User
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/conversations", tags=["conversations"])


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sequence_number: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_preview: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationWithMessagesResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


def parse_conversation_id(conversation_id: str) -> UUID:
    """Parse conversation ID - handle both UUID and custom formats"""
    try:
        # Try to parse as UUID first
        return UUID(conversation_id)
    except ValueError:
        # If not UUID, check if it's a custom format like conv_timestamp_random
        if conversation_id.startswith('conv_'):
            # For custom format, we need to either:
            # 1. Convert to a deterministic UUID, or 
            # 2. Store mapping in database, or
            # 3. Generate a new UUID and return it
            # For now, let's generate a deterministic UUID from the string
            import hashlib
            namespace = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Standard namespace UUID
            return UUID(bytes=hashlib.md5(conversation_id.encode()).digest())
        else:
            raise ValueError(f"Invalid conversation ID format: {conversation_id}")


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a specific conversation"""
    try:
        conversation_uuid = parse_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Check if conversation exists
    conv_stmt = select(Conversation).where(Conversation.id == conversation_uuid)
    conv_result = await db.execute(conv_stmt)
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_uuid)
        .order_by(Message.sequence_number.asc())
        .offset(offset)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    return [
        MessageResponse(
            id=str(msg.id),
            role=msg.role,
            content=msg.content,
            sequence_number=msg.sequence_number,
            created_at=msg.created_at
        )
        for msg in messages
    ]


@router.get("/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation_with_messages(
    conversation_id: str,
    include_messages: bool = Query(True),
    message_limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation details with optional messages"""
    try:
        conversation_uuid = parse_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Get conversation with messages
    if include_messages:
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_uuid)
        )
    else:
        stmt = select(Conversation).where(Conversation.id == conversation_uuid)
    
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = []
    if include_messages and conversation.messages:
        # Sort messages by sequence_number and limit
        sorted_messages = sorted(conversation.messages, key=lambda m: m.sequence_number)
        limited_messages = sorted_messages[-message_limit:] if message_limit else sorted_messages
        
        messages = [
            MessageResponse(
                id=str(msg.id),
                role=msg.role,
                content=msg.content,
                sequence_number=msg.sequence_number,
                created_at=msg.created_at
            )
            for msg in limited_messages
        ]
    
    return ConversationWithMessagesResponse(
        id=str(conversation.id),
        user_id=str(conversation.user_id),
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=messages
    )


@router.get("/", response_model=List[ConversationResponse])
async def list_user_conversations(
    user_id: str = Query(..., description="User ID to get conversations for"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List conversations for a specific user"""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Check if user exists
    user_stmt = select(User).where(User.id == user_uuid)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get conversations with message count and preview
    from sqlalchemy import func, desc
    
    stmt = (
        select(
            Conversation,
            func.count(Message.id).label('message_count'),
            func.max(Message.content).label('last_message')
        )
        .outerjoin(Message)
        .where(Conversation.user_id == user_uuid)
        .group_by(Conversation.id)
        .order_by(desc(Conversation.updated_at))
        .offset(offset)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    conversations_data = result.all()
    
    return [
        ConversationResponse(
            id=str(conv.Conversation.id),
            user_id=str(conv.Conversation.user_id),
            title=conv.Conversation.title,
            created_at=conv.Conversation.created_at,
            updated_at=conv.Conversation.updated_at,
            message_count=conv.message_count or 0,
            last_message_preview=(conv.last_message[:100] + "..." if conv.last_message and len(conv.last_message) > 100 else conv.last_message)
        )
        for conv in conversations_data
    ]


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    try:
        conversation_uuid = parse_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Get conversation
    stmt = select(Conversation).where(Conversation.id == conversation_uuid)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Delete conversation (messages will be deleted due to cascade)
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "Conversation deleted successfully"}


@router.patch("/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    title: str = Query(..., max_length=200),
    db: AsyncSession = Depends(get_db)
):
    """Update conversation title"""
    try:
        conversation_uuid = parse_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Get conversation
    stmt = select(Conversation).where(Conversation.id == conversation_uuid)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Update title
    conversation.title = title
    await db.commit()
    
    return {"message": "Conversation title updated successfully", "title": title}