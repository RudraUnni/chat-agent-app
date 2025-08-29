# backend/app/api/v1/openwebui.py
"""
Open WebUI Integration API
Provides compatibility layer between Open WebUI and Medical Assistant backend
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, List, AsyncGenerator
from pydantic import BaseModel, Field
import logging
import json
import asyncio
from datetime import datetime
import sys
import os

# Add security config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from security_config.input_validation import validate_openwebui_input, validate_model_request, rate_limiter

from app.core.dependencies import get_workflow_registry, get_chat_manager
from app.services.workflow.registry import WorkflowRegistry
from app.services.chat.manager import ChatManager
from app.core.workflow_utils import extract_workflow_response, format_workflow_error

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openwebui", tags=["openwebui"])


# Open WebUI Compatible Models
class OpenWebUIMessage(BaseModel):
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    
class OpenWebUIChatRequest(BaseModel):
    model: str = Field(default="medical-assistant", description="Model to use")
    messages: List[OpenWebUIMessage] = Field(..., description="Chat messages")
    stream: bool = Field(default=False, description="Enable streaming response")
    temperature: Optional[float] = Field(default=0.7, description="Response temperature")
    max_tokens: Optional[int] = Field(default=1000, description="Maximum tokens")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    
    # Medical Assistant specific parameters
    workflow: str = Field(default="pubmed_research", description="Workflow to use")
    pubmed_search: bool = Field(default=True, description="Enable PubMed search")
    evidence_based: bool = Field(default=True, description="Require evidence-based responses")

class OpenWebUIResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, int]] = None

class OpenWebUIStreamChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]


@router.get("/models")
async def get_models():
    """
    Return available models for Open WebUI
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "medical-assistant",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "medical-assistant",
                "permission": [],
                "root": "medical-assistant",
                "parent": None,
                "name": "Medical Assistant",
                "description": "AI-powered medical research assistant with PubMed integration"
            },
            {
                "id": "pubmed-research",
                "object": "model", 
                "created": int(datetime.now().timestamp()),
                "owned_by": "medical-assistant",
                "permission": [],
                "root": "pubmed-research",
                "parent": None,
                "name": "PubMed Research",
                "description": "Specialized model for medical literature research"
            },
            {
                "id": "medical-analysis",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "medical-assistant",
                "permission": [],
                "root": "medical-analysis", 
                "parent": None,
                "name": "Medical Analysis",
                "description": "Advanced medical case analysis and diagnosis support"
            }
        ]
    }


@router.post("/chat/completions")
async def chat_completions(
    request: OpenWebUIChatRequest,
    http_request: Request,
    workflow_registry: WorkflowRegistry = Depends(get_workflow_registry),
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    OpenAI-compatible chat completions endpoint for Open WebUI
    """
    try:
        # Security: Rate limiting
        client_ip = http_request.client.host if http_request.client else "unknown"
        if not rate_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Security: Input validation
        request_dict = request.dict()
        validated_request = validate_model_request(request_dict)
        
        if "error" in validated_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validated_request["error"]
            )
        # Extract the latest user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        latest_message = user_messages[-1].content
        
        # Determine workflow based on model
        workflow_map = {
            "medical-assistant": "pubmed_research",
            "pubmed-research": "pubmed_research", 
            "medical-analysis": "medical_analysis"
        }
        workflow = workflow_map.get(request.model, "pubmed_research")
        
        # Generate session ID if not provided
        session_id = request.session_id or f"openwebui_{int(datetime.now().timestamp())}"
        
        # Prepare parameters
        parameters = {
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "pubmed_search": request.pubmed_search,
            "evidence_based": request.evidence_based
        }
        
        if request.stream:
            return StreamingResponse(
                stream_chat_response(
                    latest_message, workflow, session_id, parameters,
                    workflow_registry, chat_manager, request.model
                ),
                media_type="text/plain"
            )
        else:
            # Non-streaming response
            result = await workflow_registry.execute_workflow(
                workflow, latest_message, session_id, parameters
            )
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)
            
            response_content = extract_workflow_response(result.data)
            
            return OpenWebUIResponse(
                id=f"chatcmpl-{session_id}",
                created=int(datetime.now().timestamp()),
                model=request.model,
                choices=[{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }],
                usage={
                    "prompt_tokens": len(latest_message.split()),
                    "completion_tokens": len(response_content.split()),
                    "total_tokens": len(latest_message.split()) + len(response_content.split())
                }
            )
            
    except Exception as e:
        logger.error(f"Error in chat completions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def stream_chat_response(
    message: str,
    workflow: str,
    session_id: str,
    parameters: Dict[str, Any],
    workflow_registry: WorkflowRegistry,
    chat_manager: ChatManager,
    model: str
) -> AsyncGenerator[str, None]:
    """
    Stream chat response in OpenAI format for Open WebUI
    """
    try:
        # Execute workflow
        result = await workflow_registry.execute_workflow(
            workflow, message, session_id, parameters
        )
        
        if not result.success:
            error_chunk = OpenWebUIStreamChunk(
                id=f"chatcmpl-{session_id}",
                created=int(datetime.now().timestamp()),
                model=model,
                choices=[{
                    "index": 0,
                    "delta": {
                        "content": f"Error: {result.error}"
                    },
                    "finish_reason": "stop"
                }]
            )
            yield f"data: {error_chunk.json()}\n\n"
            yield "data: [DONE]\n\n"
            return
        
        response_content = extract_workflow_response(result.data)
        
        # Split response into chunks for streaming
        words = response_content.split()
        chunk_size = 3  # Words per chunk
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_content = " " + " ".join(chunk_words) if i > 0 else " ".join(chunk_words)
            
            chunk = OpenWebUIStreamChunk(
                id=f"chatcmpl-{session_id}",
                created=int(datetime.now().timestamp()),
                model=model,
                choices=[{
                    "index": 0,
                    "delta": {
                        "content": chunk_content
                    },
                    "finish_reason": None
                }]
            )
            
            yield f"data: {chunk.json()}\n\n"
            await asyncio.sleep(0.1)  # Add small delay for realistic streaming
        
        # Final chunk
        final_chunk = OpenWebUIStreamChunk(
            id=f"chatcmpl-{session_id}",
            created=int(datetime.now().timestamp()),
            model=model,
            choices=[{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        )
        
        yield f"data: {final_chunk.json()}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Error in streaming response: {str(e)}")
        error_chunk = OpenWebUIStreamChunk(
            id=f"chatcmpl-{session_id}",
            created=int(datetime.now().timestamp()),
            model=model,
            choices=[{
                "index": 0,
                "delta": {
                    "content": f"Error: {str(e)}"
                },
                "finish_reason": "stop"
            }]
        )
        yield f"data: {error_chunk.json()}\n\n"
        yield "data: [DONE]\n\n"


@router.get("/config")
async def get_config():
    """
    Return Medical Assistant configuration for Open WebUI
    """
    return {
        "medical_assistant": {
            "version": "1.0.0",
            "features": {
                "pubmed_integration": True,
                "evidence_based_responses": True,
                "medical_workflows": True,
                "streaming": True
            },
            "models": ["medical-assistant", "pubmed-research", "medical-analysis"],
            "default_model": "medical-assistant"
        },
        "api_endpoints": {
            "chat": "/api/v1/openwebui/chat/completions",
            "models": "/api/v1/openwebui/models", 
            "config": "/api/v1/openwebui/config",
            "health": "/health"
        }
    }


@router.get("/health")
async def openwebui_health():
    """
    Health check endpoint for Open WebUI integration
    """
    return {
        "status": "healthy",
        "service": "medical-assistant-openwebui-bridge",
        "timestamp": datetime.now().isoformat(),
        "integrations": {
            "pubmed": "available",
            "workflow_engine": "running",
            "database": "connected"
        }
    }


@router.post("/pubmed/search")
async def pubmed_search_endpoint(
    request: Dict[str, Any],
    workflow_registry: WorkflowRegistry = Depends(get_workflow_registry)
):
    """
    Direct PubMed search endpoint for Open WebUI tools integration
    """
    try:
        query = request.get("query", "")
        max_results = request.get("max_results", 10)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        # Execute PubMed search workflow
        result = await workflow_registry.execute_workflow(
            "pubmed_research",
            f"Search PubMed for: {query}",
            f"pubmed_{int(datetime.now().timestamp())}",
            {"max_results": max_results}
        )
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return {
            "success": True,
            "query": query,
            "results": result.data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in PubMed search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))