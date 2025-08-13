from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.core.dependencies import get_workflow_registry, get_chat_manager
from app.services.workflow.registry import WorkflowRegistry
from app.services.chat.manager import ChatManager


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    workflow: str = "general_assistant"
    session_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}


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
    """Process a chat message through a workflow"""
    
    # Get or create session
    session = chat_manager.get_or_create_session(request.session_id)
    
    # Get workflow
    workflow = workflow_registry.get_workflow(request.workflow)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{request.workflow}' not found"
        )
    
    # Prepare input data
    input_data = {
        'message': request.message,
        **request.parameters
    }
    
    # Execute workflow
    result = await workflow.execute(input_data, session.context)
    
    if result.success:
        response_text = None
        if result.data:
            # Extract response based on workflow type
            if request.workflow == "general_assistant":
                response_text = result.data.get('response')
            elif request.workflow == "pubmed_research":
                response_text = result.data.get('formatted_summary') or result.data.get('analysis')
        
        return ChatResponse(
            success=True,
            response=response_text,
            data=result.data,
            session_id=session.session_id
        )
    else:
        return ChatResponse(
            success=False,
            error=result.error,
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


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """Delete a chat session"""
    chat_manager.delete_session(session_id)
    return {"message": "Session deleted"}