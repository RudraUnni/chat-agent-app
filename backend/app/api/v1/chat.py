from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging
import json
import redis.asyncio as redis
from app.core.dependencies import get_workflow_registry
from app.services.workflow.registry import WorkflowRegistry
from app.core.workflow_utils import extract_workflow_response, format_workflow_error
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Redis client for session persistence
redis_client = None

async def get_redis_client():
    """Get or create Redis client"""
    global redis_client
    if redis_client is None:
        redis_host = getattr(settings, 'redis_host', 'localhost')
        redis_port = int(getattr(settings, 'redis_port', 6379))
        redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    return redis_client

async def store_session_history(session_id: str, messages: List[Dict[str, Any]]):
    """Store session history in Redis"""
    try:
        client = await get_redis_client()
        key = f"chat_session:{session_id}"
        value = json.dumps(messages)
        # Store with 24 hour expiration
        await client.setex(key, 86400, value)
    except Exception as e:
        logger.error(f"Failed to store session history: {e}")

async def get_session_history(session_id: str) -> List[Dict[str, Any]]:
    """Get session history from Redis"""
    try:
        client = await get_redis_client()
        key = f"chat_session:{session_id}"
        value = await client.get(key)
        if value:
            return json.loads(value)
        return []
    except Exception as e:
        logger.error(f"Failed to get session history: {e}")
        return []

async def add_message_to_session(session_id: str, role: str, content: str):
    """Add a message to session history"""
    try:
        messages = await get_session_history(session_id)
        messages.append({
            "role": role,
            "content": content,
            "timestamp": str(int(__import__('time').time()))
        })
        await store_session_history(session_id, messages)
    except Exception as e:
        logger.error(f"Failed to add message to session: {e}")

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    workflow: str = "pubmed_research"  # Default to Medical Assistant
    session_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}
    
    class Config:
        schema_extra = {
            "example": {
                "message": "What are the latest treatments for diabetes?",
                "workflow": "pubmed_research",
                "session_id": "optional-session-id",
                "parameters": {}
            }
        }


class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    workflow_registry: WorkflowRegistry = Depends(get_workflow_registry)
):
    """
    Process a chat message through a workflow with Redis-persisted conversation history.
    
    - Rehydrates session history from Redis before building prompts
    - Stores user messages in Redis before processing
    - Stores assistant responses in Redis after processing
    - Maintains chronological order of all messages per session_id
    """
    
    # Generate session_id if not provided
    session_id = request.session_id or f"session_{int(__import__('time').time())}"
    
    # Store user message in Redis
    await add_message_to_session(session_id, "user", request.message)
    logger.debug(f"Added user message to Redis session {session_id}")
    
    # Get workflow
    workflow = workflow_registry.get_workflow(request.workflow)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{request.workflow}' not found"
        )
    
    # Rehydrate conversation history from Redis
    conversation_history = await get_session_history(session_id)
    
    # Prepare input data with conversation history
    input_data = {
        'message': request.message,
        'conversation_history': conversation_history,
        **request.parameters
    }
    
    # Create minimal context
    from app.workflows.base import WorkflowContext
    context = WorkflowContext(
        session_id=session_id,
        history=conversation_history
    )
    
    # Execute workflow
    result = await workflow.execute(input_data, context)
    
    if result.success:
        response_text = extract_workflow_response(result, request.workflow)
        
        # Store assistant response in Redis
        await add_message_to_session(session_id, "assistant", response_text)
        logger.debug(f"Added assistant response to Redis session {session_id}")
        
        return ChatResponse(
            success=True,
            response=response_text,
            data=result.data,
            session_id=session_id
        )
    else:
        error_message = format_workflow_error(result, request.workflow)
        
        # Store error as assistant message for context
        await add_message_to_session(session_id, "assistant", f"Error: {error_message}")
        
        return ChatResponse(
            success=False,
            error=error_message,
            session_id=session_id
        )


@router.get("/workflows")
async def list_workflows(
    workflow_registry: WorkflowRegistry = Depends(get_workflow_registry)
):
    """List available workflows"""
    return {
        "workflows": workflow_registry.list_workflows()
    }


@router.get("/sessions/{session_id}/history")
async def get_session_history_endpoint(session_id: str):
    """Get conversation history for a session from Redis"""
    try:
        messages = await get_session_history(session_id)
        return {
            "session_id": session_id,
            "messages": messages
        }
    except Exception as e:
        logger.error(f"Failed to get session history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session history"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session from Redis"""
    try:
        client = await get_redis_client()
        key = f"chat_session:{session_id}"
        await client.delete(key)
        return {"message": "Session deleted"}
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


# OpenAI-compatible endpoints for Open WebUI integration
@router.get("/models")
async def get_models():
    """
    OpenAI-compatible endpoint for Open WebUI to discover available models
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "medical-assistant",
                "object": "model",
                "created": 1677610602,
                "owned_by": "medical-assistant",
                "permission": [],
                "root": "medical-assistant",
                "parent": None
            },
            {
                "id": "pubmed-research",
                "object": "model", 
                "created": 1677610602,
                "owned_by": "medical-assistant",
                "permission": [],
                "root": "pubmed-research",
                "parent": None
            }
        ]
    }


class OpenAIChatMessage(BaseModel):
    role: str
    content: str
    
    class Config:
        # Allow extra fields that OpenWebUI might send
        extra = "allow"


class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIChatMessage]
    stream: bool = False
    temperature: float = 0.7
    max_tokens: int = 1000
    
    class Config:
        # Allow extra fields that OpenWebUI might send
        extra = "allow"


@router.post("/chat/completions")
async def openai_chat_completions(
    request: OpenAIChatRequest,
    workflow_registry: WorkflowRegistry = Depends(get_workflow_registry)
):
    """
    OpenAI-compatible chat completions endpoint for Open WebUI integration with Redis persistence
    """
    logger.info(f"Received chat completions request for model: {request.model}")
    logger.info(f"Request messages count: {len(request.messages)}")
    
    try:
        # Convert OpenAI format to our internal format
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages cannot be empty")
        
        # Get the last user message
        last_message = request.messages[-1]
        if last_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")
        
        # Generate session_id for this conversation
        session_id = f"openai_session_{int(__import__('time').time())}"
        
        # Store conversation history in Redis
        for msg in request.messages:
            if msg.role in ["user", "assistant", "system"]:
                await add_message_to_session(session_id, msg.role, msg.content)
        
        # Determine workflow based on model name
        workflow_name = "pubmed_research"  # Default
        if "research" in request.model.lower():
            workflow_name = "pubmed_research"
        
        # Get workflow
        workflow = workflow_registry.get_workflow(workflow_name)
        if not workflow:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow '{workflow_name}' not found"
            )
        
        # Get conversation history from Redis
        conversation_history = await get_session_history(session_id)
        
        # Prepare input data
        input_data = {
            'message': last_message.content,
            'conversation_history': conversation_history,
            'temperature': request.temperature,
            'max_tokens': request.max_tokens
        }
        
        # Create minimal context
        from app.workflows.base import WorkflowContext
        context = WorkflowContext(
            session_id=session_id,
            history=conversation_history
        )
        
        # Execute workflow
        result = await workflow.execute(input_data, context)
        
        if result.success:
            response_text = extract_workflow_response(result, workflow_name)
            
            # Store assistant response in Redis
            await add_message_to_session(session_id, "assistant", response_text)
            
            # Return OpenAI-compatible response
            return {
                "id": f"chatcmpl-{session_id}",
                "object": "chat.completion",
                "created": int(__import__('time').time()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response_text
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(last_message.content.split()),
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": len(last_message.content.split()) + len(response_text.split())
                }
            }
        else:
            error_message = format_workflow_error(result, workflow_name)
            raise HTTPException(status_code=500, detail=error_message)
            
    except HTTPException as e:
        logger.error(f"HTTP error in chat completions: {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in chat completions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")