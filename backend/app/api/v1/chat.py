from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging
import json
import asyncio
from app.core.dependencies import get_workflow_registry, get_chat_manager
from app.services.workflow.registry import WorkflowRegistry
from app.services.chat.manager import ChatManager
from app.core.workflow_utils import extract_workflow_response, format_workflow_error

logger = logging.getLogger(__name__)


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


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class AssistantUIRequest(BaseModel):
    messages: List[Message]
    workflow: str = "pubmed_research"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    workflow_registry: WorkflowRegistry = Depends(get_workflow_registry),
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    Process a chat message through a workflow with full conversation history.
    
    The system now maintains conversation history per session and provides
    complete context to agents, enabling more coherent multi-turn conversations.
    
    - Stores user messages in session history before processing
    - Passes full conversation history to the workflow/agent
    - Stores assistant responses after processing
    - Maintains chronological order of all messages
    """
    
    # Get or create session
    session = chat_manager.get_or_create_session(request.session_id)
    
    # Store user message in session history
    session.add_user_message(request.message)
    logger.debug(f"Added user message to session {session.session_id}. Total messages: {len(session.messages)}")
    
    # Get workflow
    workflow = workflow_registry.get_workflow(request.workflow)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{request.workflow}' not found"
        )
    
    # Prepare input data with conversation history
    input_data = {
        'message': request.message,
        'conversation_history': session.get_messages_for_agent(),
        **request.parameters
    }
    
    # Update context with conversation history
    session.context.history = [
        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat() if msg.timestamp else None}
        for msg in session.get_conversation_history()
    ]
    
    # Execute workflow
    result = await workflow.execute(input_data, session.context)
    
    if result.success:
        response_text = extract_workflow_response(result, request.workflow)
        
        # Store assistant response in session history
        session.add_assistant_message(response_text)
        logger.debug(f"Added assistant response to session {session.session_id}. Total messages: {len(session.messages)}")
        
        return ChatResponse(
            success=True,
            response=response_text,
            data=result.data,
            session_id=session.session_id
        )
    else:
        error_message = format_workflow_error(result, request.workflow)
        
        # Store error as assistant message for context
        session.add_assistant_message(f"Error: {error_message}")
        
        return ChatResponse(
            success=False,
            error=error_message,
            session_id=session.session_id
        )


@router.get("/workflows")
async def list_workflows(
    workflow_registry: WorkflowRegistry = Depends(get_workflow_registry)
):
    """List available workflows"""
    return {
        "workflows": workflow_registry.list_workflows()
    }


@router.get("/sessions")
async def list_sessions(
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """List active chat sessions"""
    return {
        "sessions": chat_manager.list_sessions()
    }


@router.get("/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """Get conversation history for a session"""
    session = chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in session.get_conversation_history()
        ]
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """Delete a chat session"""
    chat_manager.delete_session(session_id)
    return {"message": "Session deleted"}


async def stream_response(text: str):
    """Stream text response word by word for ChatGPT-like effect"""
    words = text.split()
    for i, word in enumerate(words):
        chunk = {
            "type": "text",
            "content": word + (" " if i < len(words) - 1 else "")
        }
        yield f"{json.dumps(chunk)}\n"
        await asyncio.sleep(0.05)  # Small delay for streaming effect


@router.post("/stream")
async def chat_stream(
    request: AssistantUIRequest,
    workflow_registry: WorkflowRegistry = Depends(get_workflow_registry),
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    Stream chat responses for assistant-ui integration.
    Compatible with assistant-ui's expected message format.
    """
    
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided"
        )
    
    # Get the latest user message
    user_message = None
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.content
            break
    
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user message found"
        )
    
    # Get or create session
    session = chat_manager.get_or_create_session(request.session_id)
    
    # Store user message in session history
    session.add_user_message(user_message)
    logger.debug(f"Added user message to session {session.session_id}. Total messages: {len(session.messages)}")
    
    # Get workflow
    workflow = workflow_registry.get_workflow(request.workflow)
    if not workflow:
        error_text = f"Workflow '{request.workflow}' not found"
        async def error_stream():
            yield f'{{"type": "text", "content": "{error_text}"}}\n'
        
        return StreamingResponse(
            error_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    
    # Prepare input data with conversation history
    input_data = {
        'message': user_message,
        'conversation_history': session.get_messages_for_agent(),
    }
    
    # Update context with conversation history
    session.context.history = [
        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat() if msg.timestamp else None}
        for msg in session.get_conversation_history()
    ]
    
    async def generate_stream():
        try:
            # Execute workflow
            result = await workflow.execute(input_data, session.context)
            
            if result.success:
                response_text = extract_workflow_response(result, request.workflow)
                
                # Store assistant response in session history
                session.add_assistant_message(response_text)
                logger.debug(f"Added assistant response to session {session.session_id}. Total messages: {len(session.messages)}")
                
                # Stream the response
                async for chunk in stream_response(response_text):
                    yield chunk
            else:
                error_message = format_workflow_error(result, request.workflow)
                
                # Store error as assistant message for context
                session.add_assistant_message(f"Error: {error_message}")
                
                # Stream the error
                async for chunk in stream_response(f"Error: {error_message}"):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Error in chat stream: {str(e)}")
            error_text = f"An error occurred: {str(e)}"
            async for chunk in stream_response(error_text):
                yield chunk
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )