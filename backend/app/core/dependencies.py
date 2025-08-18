from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.connection import get_db
from app.services.llm.factory import LLMFactory
from app.services.chat.manager import ChatManager
from app.services.database.chat_service import DatabaseChatService
from app.services.workflow.registry import WorkflowRegistry

settings = get_settings()


def get_llm_service():
    """Dependency for LLM service"""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No LLM API key configured"
        )
    return LLMFactory.create("openai")


def get_chat_manager():
    """Dependency for chat manager (legacy in-memory)"""
    return ChatManager()


def get_database_chat_service(db: AsyncSession = Depends(get_db)) -> DatabaseChatService:
    """Dependency for database-backed chat service"""
    return DatabaseChatService(db)


def get_workflow_registry():
    """Dependency for workflow registry"""
    from workflows import register_all_workflows
    registry = WorkflowRegistry()
    register_all_workflows(registry)
    return registry