from typing import Optional
from fastapi import Depends, HTTPException, status
from app.core.config import settings
from app.services.llm.factory import LLMFactory
from app.services.chat.manager import ChatManager
from app.services.workflow.registry import WorkflowRegistry


def get_llm_service():
    """Dependency for LLM service"""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No LLM API key configured"
        )
    return LLMFactory.create("openai")


def get_chat_manager():
    """Dependency for chat manager"""
    return ChatManager()


def get_workflow_registry():
    """Dependency for workflow registry"""
    from workflows import register_all_workflows
    registry = WorkflowRegistry()
    register_all_workflows(registry)
    return registry