from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Conversation, Message


class DatabaseChatService:
    """Database-backed chat service for persistent chat storage"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(self, title: str = "New Chat") -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(title=title)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_conversations(self) -> List[Conversation]:
        """Get all conversations"""
        result = await self.db.execute(
            select(Conversation).order_by(Conversation.created_at.desc())
        )
        return result.scalars().all()
    
    async def add_message(self, conversation_id: str, content: str, role: str = "user") -> Message:
        """Add a message to a conversation"""
        message = Message(conversation_id=conversation_id, content=content, role=role, sequence_number=0)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages for a conversation"""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()
