"""
Database-backed chat service for persistent conversation management.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uuid

from app.database.models import User, Conversation, Message, Session, WorkflowExecution
from app.database.repositories import (
    UserRepository, 
    ConversationRepository, 
    MessageRepository, 
    SessionRepository,
    WorkflowExecutionRepository
)
from app.models.chat import ChatMessage, ChatSession as ChatSessionModel


class DatabaseChatService:
    """Database-backed chat service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)
        self.session_repo = SessionRepository(db)
        self.workflow_repo = WorkflowExecutionRepository(db)
    
    async def get_or_create_user(
        self, 
        username: str, 
        email: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> User:
        """Get existing user or create new one"""
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            # For demo purposes, create user with email = username@local if not provided
            email = email or f"{username}@local"
            user = await self.user_repo.create_user(
                username=username,
                email=email,
                full_name=full_name
            )
            await self.db.commit()
        return user
    
    async def create_or_get_conversation(
        self,
        user_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None,
        workflow_type: str = "general_assistant",
        title: Optional[str] = None
    ) -> Conversation:
        """Create new conversation or get existing one"""
        if conversation_id:
            conversation = await self.conversation_repo.get_conversation_by_id(conversation_id)
            if conversation and conversation.user_id == user_id:
                return conversation
        
        # Create new conversation
        conversation = await self.conversation_repo.create_conversation(
            user_id=user_id,
            workflow_type=workflow_type,
            title=title
        )
        await self.db.commit()
        return conversation
    
    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        workflow_execution_id: Optional[uuid.UUID] = None,
        processing_time_ms: Optional[int] = None,
        token_count: Optional[int] = None
    ) -> Message:
        """Add a message to a conversation"""
        message = await self.message_repo.create_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata,
            workflow_execution_id=workflow_execution_id,
            processing_time_ms=processing_time_ms,
            token_count=token_count
        )
        
        # Update conversation activity
        await self.conversation_repo.update_conversation_activity(conversation_id)
        await self.db.commit()
        return message
    
    async def get_conversation_history(
        self,
        conversation_id: uuid.UUID,
        limit: Optional[int] = None,
        include_system: bool = True
    ) -> List[ChatMessage]:
        """Get conversation message history"""
        messages = await self.message_repo.get_conversation_messages(
            conversation_id=conversation_id,
            limit=limit
        )
        
        chat_messages = []
        for msg in messages:
            if not include_system and msg.role == "system":
                continue
            
            chat_messages.append(ChatMessage(
                role=msg.role,
                content=msg.content,
                timestamp=msg.created_at,
                metadata=msg.metadata
            ))
        
        return chat_messages
    
    async def get_user_conversations(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's conversation list"""
        conversations = await self.conversation_repo.get_user_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return [
            {
                "id": str(conv.id),
                "title": conv.title or "Untitled Conversation",
                "workflow_type": conv.workflow_type,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": conv.message_count,
                "last_message_at": conv.last_message_at.isoformat()
            }
            for conv in conversations
        ]
    
    async def create_session(
        self,
        session_token: str,
        user_id: Optional[uuid.UUID] = None,
        connection_type: str = "api",
        expires_hours: int = 24,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Session:
        """Create a new session"""
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        session = await self.session_repo.create_session(
            session_token=session_token,
            user_id=user_id,
            connection_type=connection_type,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        await self.db.commit()
        return session
    
    async def get_active_session(self, session_token: str) -> Optional[Session]:
        """Get active session by token"""
        return await self.session_repo.get_session_by_token(session_token)
    
    async def track_workflow_execution(
        self,
        workflow_name: str,
        input_data: Dict[str, Any],
        conversation_id: Optional[uuid.UUID] = None
    ) -> WorkflowExecution:
        """Start tracking a workflow execution"""
        execution = await self.workflow_repo.create_execution(
            workflow_name=workflow_name,
            input_data=input_data,
            conversation_id=conversation_id
        )
        await self.db.commit()
        return execution
    
    async def complete_workflow_execution(
        self,
        execution_id: uuid.UUID,
        success: bool,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        tokens_used: Optional[int] = None,
        api_calls_made: Optional[int] = None
    ) -> None:
        """Complete a workflow execution"""
        status = "completed" if success else "failed"
        await self.workflow_repo.update_execution_status(
            execution_id=execution_id,
            status=status,
            output_data=output_data,
            error_message=error_message,
            tokens_used=tokens_used,
            api_calls_made=api_calls_made
        )
        await self.db.commit()