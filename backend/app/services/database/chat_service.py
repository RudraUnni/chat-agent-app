from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import UUID
import logging

from app.database.models import User, Conversation, Message
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class DatabaseChatService:
    """Database-backed chat service for persistent chat storage"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, username: str, email: str, user_id: Optional[UUID] = None) -> User:
        """Create a new user"""
        try:
            user_data = {"username": username, "email": email}
            if user_id:
                user_data["id"] = user_id
            user = User(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"User creation failed due to integrity error: {e}")
            raise DatabaseError(
                f"User with username '{username}' or email '{email}' already exists",
                error_code="USER_ALREADY_EXISTS"
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during user creation: {e}")
            raise DatabaseError("Failed to create user", error_code="DB_CREATE_ERROR")
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID"""
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error during user retrieval: {e}")
            raise DatabaseError("Failed to retrieve user", error_code="DB_READ_ERROR")
    
    async def create_conversation(self, user_id: UUID, title: str = "New Conversation") -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(user_id=user_id, title=title)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
    
    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get a conversation by ID"""
        result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        return result.scalar_one_or_none()
    
    async def get_conversations(self, user_id: UUID) -> List[Conversation]:
        """Get all conversations for a user"""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        return result.scalars().all()
    
    async def add_message(self, conversation_id: UUID, content: str, role: str = "user") -> Message:
        """Add a message to a conversation"""
        # Get current message count for sequence number
        result = await self.db.execute(
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation_id)
        )
        sequence_number = result.scalar() + 1
        
        message = Message(
            conversation_id=conversation_id,
            content=content,
            role=role,
            sequence_number=sequence_number
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_messages(self, conversation_id: UUID) -> List[Message]:
        """Get all messages for a conversation"""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence_number.asc())
        )
        return result.scalars().all()
    
    async def get_recent_messages(self, conversation_id: UUID, limit: int = 10) -> List[Message]:
        """Get recent messages for a conversation"""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence_number.desc())
            .limit(limit)
        )
        # Return in chronological order (oldest first)
        messages = result.scalars().all()
        return list(reversed(messages))