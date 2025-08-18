"""
Repository pattern implementation for database operations.
Provides clean abstraction layer for data access.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc, asc, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import uuid

from app.database.models import User, Conversation, Message, Session, WorkflowExecution


class BaseRepository:
    """Base repository with common database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db


class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    async def create_user(
        self, 
        username: str, 
        email: str, 
        full_name: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            preferences=preferences or {}
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Update user's last login timestamp"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )


class ConversationRepository(BaseRepository):
    """Repository for conversation operations"""
    
    async def create_conversation(
        self,
        user_id: uuid.UUID,
        workflow_type: str = "general_assistant",
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            workflow_type=workflow_type,
            title=title,
            metadata=metadata or {}
        )
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation
    
    async def get_conversation_by_id(
        self, 
        conversation_id: uuid.UUID,
        include_messages: bool = False
    ) -> Optional[Conversation]:
        """Get conversation by ID with optional message loading"""
        query = select(Conversation).where(Conversation.id == conversation_id)
        
        if include_messages:
            query = query.options(selectinload(Conversation.messages))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_conversations(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Conversation]:
        """Get user's conversations with pagination"""
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        
        if not include_archived:
            query = query.where(Conversation.is_archived == False)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_conversation_activity(self, conversation_id: uuid.UUID) -> None:
        """Update conversation's last activity timestamp and increment message count"""
        await self.db.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(
                last_message_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                message_count=Conversation.message_count + 1
            )
        )


class MessageRepository(BaseRepository):
    """Repository for message operations"""
    
    async def create_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        workflow_execution_id: Optional[uuid.UUID] = None,
        processing_time_ms: Optional[int] = None,
        token_count: Optional[int] = None
    ) -> Message:
        """Create a new message"""
        # Get next sequence number
        result = await self.db.execute(
            select(func.coalesce(func.max(Message.sequence_number), 0) + 1)
            .where(Message.conversation_id == conversation_id)
        )
        sequence_number = result.scalar()
        
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            metadata=metadata or {},
            workflow_execution_id=workflow_execution_id,
            processing_time_ms=processing_time_ms,
            token_count=token_count
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message
    
    async def get_conversation_messages(
        self,
        conversation_id: uuid.UUID,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a conversation"""
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(asc(Message.sequence_number))
            .offset(offset)
        )
        
        if limit:
            query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_recent_messages(
        self,
        conversation_id: uuid.UUID,
        count: int = 10
    ) -> List[Message]:
        """Get the most recent messages from a conversation"""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.sequence_number))
            .limit(count)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order


class SessionRepository(BaseRepository):
    """Repository for session operations"""
    
    async def create_session(
        self,
        session_token: str,
        user_id: Optional[uuid.UUID] = None,
        connection_type: str = "api",
        expires_at: Optional[datetime] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new session"""
        session = Session(
            session_token=session_token,
            user_id=user_id,
            connection_type=connection_type,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            metadata=metadata or {}
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session
    
    async def get_session_by_token(self, session_token: str) -> Optional[Session]:
        """Get active session by token"""
        result = await self.db.execute(
            select(Session)
            .where(
                and_(
                    Session.session_token == session_token,
                    Session.is_active == True,
                    or_(
                        Session.expires_at.is_(None),
                        Session.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_session_activity(self, session_id: uuid.UUID) -> None:
        """Update session's last activity timestamp"""
        await self.db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(last_activity=datetime.utcnow())
        )
    
    async def deactivate_session(self, session_token: str) -> None:
        """Deactivate a session"""
        await self.db.execute(
            update(Session)
            .where(Session.session_token == session_token)
            .values(is_active=False)
        )


class WorkflowExecutionRepository(BaseRepository):
    """Repository for workflow execution tracking"""
    
    async def create_execution(
        self,
        workflow_name: str,
        input_data: Dict[str, Any],
        conversation_id: Optional[uuid.UUID] = None
    ) -> WorkflowExecution:
        """Create a new workflow execution record"""
        execution = WorkflowExecution(
            conversation_id=conversation_id,
            workflow_name=workflow_name,
            input_data=input_data,
            status="pending"
        )
        self.db.add(execution)
        await self.db.flush()
        await self.db.refresh(execution)
        return execution
    
    async def update_execution_status(
        self,
        execution_id: uuid.UUID,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
        tokens_used: Optional[int] = None,
        api_calls_made: Optional[int] = None
    ) -> None:
        """Update workflow execution status and results"""
        update_data = {
            "status": status,
            "completed_at": datetime.utcnow() if status in ["completed", "failed"] else None
        }
        
        if output_data is not None:
            update_data["output_data"] = output_data
        if error_message is not None:
            update_data["error_message"] = error_message
        if error_details is not None:
            update_data["error_details"] = error_details
        if tokens_used is not None:
            update_data["tokens_used"] = tokens_used
        if api_calls_made is not None:
            update_data["api_calls_made"] = api_calls_made
        
        # Calculate execution time if completed
        if status in ["completed", "failed"]:
            result = await self.db.execute(
                select(WorkflowExecution.started_at)
                .where(WorkflowExecution.id == execution_id)
            )
            started_at = result.scalar()
            if started_at:
                execution_time = (datetime.utcnow() - started_at).total_seconds() * 1000
                update_data["execution_time_ms"] = int(execution_time)
        
        await self.db.execute(
            update(WorkflowExecution)
            .where(WorkflowExecution.id == execution_id)
            .values(**update_data)
        )