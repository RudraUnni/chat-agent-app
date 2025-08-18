from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Chat, Message


class DatabaseChatService:
    """Database-backed chat service for persistent chat storage"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_chat(self, title: str = "New Chat") -> Chat:
        """Create a new chat session"""
        chat = Chat(title=title)
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat
    
    async def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get a chat by ID"""
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalar_one_or_none()
    
    async def get_chats(self) -> List[Chat]:
        """Get all chats"""
        result = await self.db.execute(select(Chat).order_by(Chat.created_at.desc()))
        return result.scalars().all()
    
    async def add_message(self, chat_id: int, content: str, role: str = "user") -> Message:
        """Add a message to a chat"""
        message = Message(chat_id=chat_id, content=content, role=role)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_messages(self, chat_id: int) -> List[Message]:
        """Get all messages for a chat"""
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()