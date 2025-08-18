"""
Database models for the chat application.
Designed for scalability with proper indexing and relationships.
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    preferences = Column(JSONB, default={}, nullable=False)  # User preferences, settings
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_users_active_created', 'is_active', 'created_at'),
        Index('ix_users_last_login', 'last_login'),
    )


class Conversation(Base):
    """Conversation model - container for related messages"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)  # Auto-generated or user-set title
    workflow_type = Column(String(50), nullable=False, default="general_assistant")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_message_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    metadata = Column(JSONB, default={}, nullable=False)  # Conversation-specific metadata
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_conversations_user_updated', 'user_id', 'updated_at'),
        Index('ix_conversations_workflow_created', 'workflow_type', 'created_at'),
        Index('ix_conversations_active', 'is_archived', 'last_message_at'),
    )


class Message(Base):
    """Message model - individual chat messages with rich metadata"""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system', 'tool'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sequence_number = Column(Integer, nullable=False)  # Order within conversation
    
    # Message processing metadata
    workflow_execution_id = Column(UUID(as_uuid=True), nullable=True)  # Link to workflow execution
    processing_time_ms = Column(Integer, nullable=True)  # Time taken to generate response
    token_count = Column(Integer, nullable=True)  # Token usage for LLM calls
    
    # Rich metadata for extensibility
    metadata = Column(JSONB, default={}, nullable=False)  # Tool calls, citations, etc.
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_messages_conversation_sequence', 'conversation_id', 'sequence_number'),
        Index('ix_messages_conversation_created', 'conversation_id', 'created_at'),
        Index('ix_messages_role_created', 'role', 'created_at'),
        Index('ix_messages_workflow_execution', 'workflow_execution_id'),
    )


class Session(Base):
    """Session model for WebSocket and API session management"""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Anonymous sessions allowed
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    connection_type = Column(String(20), nullable=False)  # 'websocket', 'api', 'hybrid'
    
    # Session metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    metadata = Column(JSONB, default={}, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_sessions_user_activity', 'user_id', 'last_activity'),
        Index('ix_sessions_active_expires', 'is_active', 'expires_at'),
        Index('ix_sessions_token_active', 'session_token', 'is_active'),
    )


class WorkflowExecution(Base):
    """Workflow execution history for analytics and debugging"""
    __tablename__ = "workflow_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    workflow_name = Column(String(100), nullable=False)
    input_data = Column(JSONB, nullable=False)
    output_data = Column(JSONB, nullable=True)
    status = Column(String(20), nullable=False)  # 'pending', 'running', 'completed', 'failed'
    
    # Timing and performance
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    
    # Resource usage
    tokens_used = Column(Integer, nullable=True)
    api_calls_made = Column(Integer, default=0, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_workflow_executions_conversation', 'conversation_id', 'started_at'),
        Index('ix_workflow_executions_workflow_status', 'workflow_name', 'status'),
        Index('ix_workflow_executions_status_started', 'status', 'started_at'),
    )