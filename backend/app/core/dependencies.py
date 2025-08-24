from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.connection import get_db
from app.services.llm.factory import LLMFactory
from app.services.chat.manager import ChatManager
from app.services.database.chat_service import DatabaseChatService
from app.services.workflow.registry import WorkflowRegistry
from app.core.exceptions import handle_service_error, ConfigurationError, LLMError

settings = get_settings()


def get_llm_service():
    """Dependency for LLM service"""
    try:
        if not settings.openai_api_key:
            raise ConfigurationError(
                "No LLM API key configured",
                error_code="MISSING_API_KEY"
            )
        return LLMFactory.create(settings.default_llm_provider)
    except (ConfigurationError, LLMError) as e:
        raise handle_service_error(e)


def get_chat_manager():
    """Dependency for chat manager (legacy in-memory)"""
    return ChatManager()


def get_database_chat_service(db: AsyncSession = Depends(get_db)) -> DatabaseChatService:
    """Dependency for database-backed chat service"""
    return DatabaseChatService(db)


def get_workflow_registry():
    """Dependency for workflow registry"""
    try:
        from app.workflows import register_all_workflows
        registry = WorkflowRegistry()
        register_all_workflows(registry)
        return registry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to initialize workflow registry",
                "error_code": "WORKFLOW_REGISTRY_ERROR",
                "details": {"error": str(e)}
            }
        )