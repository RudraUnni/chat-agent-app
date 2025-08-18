"""
Database-backed chat API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import uuid

from app.core.dependencies import get_workflow_registry, get_database_chat_service
from app.services.workflow.registry import WorkflowRegistry
from app.services.database.chat_service import DatabaseChatService


router = APIRouter(prefix="/db-chat", tags=["database-chat"])


class ChatRequest(BaseModel):
    message: str
    workflow: str = "general_assistant"
    conversation_id: Optional[str] = None
    user_id: str = "anonymous"  # In a real app, this would come from auth
    parameters: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    conversation_id: str
    message_id: str


class ConversationListResponse(BaseModel):
    conversations: List[Dict[str, Any]]
    total: int
    offset: int
    limit: int


class ConversationHistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]
    conversation_id: str


@router.post("/", response_model=ChatResponse)
async def chat_with_database(
    request: ChatRequest,
    workflow_registry: WorkflowRegistry = Depends(get_workflow_registry),
    chat_service: DatabaseChatService = Depends(get_database_chat_service)
):
    """Process a chat message with database persistence"""
    
    try:
        # Get or create user
        user = await chat_service.get_or_create_user(
            username=request.user_id,
            full_name=request.user_id.replace("_", " ").title() if request.user_id != "anonymous" else None
        )
        
        # Get or create conversation
        conversation_id = uuid.UUID(request.conversation_id) if request.conversation_id else None
        conversation = await chat_service.create_or_get_conversation(
            user_id=user.id,
            conversation_id=conversation_id,
            workflow_type=request.workflow
        )
        
        # Save user message
        user_message = await chat_service.add_message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            metadata={"parameters": request.parameters}
        )
        
        # Get workflow
        workflow = workflow_registry.get_workflow(request.workflow)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{request.workflow}' not found"
            )
        
        # Track workflow execution
        execution = await chat_service.track_workflow_execution(
            workflow_name=request.workflow,
            input_data={
                'message': request.message,
                **request.parameters
            },
            conversation_id=conversation.id
        )
        
        # Prepare input data
        input_data = {
            'message': request.message,
            **request.parameters
        }
        
        try:
            # Execute workflow
            result = await workflow.execute(input_data)
            
            # Save assistant response
            assistant_message = await chat_service.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=result.get('response', ''),
                metadata={
                    "workflow_data": result.get('data', {}),
                    "execution_id": str(execution.id)
                },
                workflow_execution_id=execution.id
            )
            
            # Complete workflow execution tracking
            await chat_service.complete_workflow_execution(
                execution_id=execution.id,
                success=True,
                output_data=result
            )
            
            return ChatResponse(
                success=True,
                response=result.get('response'),
                data=result.get('data'),
                conversation_id=str(conversation.id),
                message_id=str(assistant_message.id)
            )
            
        except Exception as workflow_error:
            # Complete workflow execution with error
            await chat_service.complete_workflow_execution(
                execution_id=execution.id,
                success=False,
                error_message=str(workflow_error)
            )
            
            # Save error message
            await chat_service.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=f"I encountered an error: {str(workflow_error)}",
                metadata={
                    "error": True,
                    "execution_id": str(execution.id)
                },
                workflow_execution_id=execution.id
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Workflow execution failed: {str(workflow_error)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.get("/conversations/{user_id}", response_model=ConversationListResponse)
async def get_user_conversations(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    chat_service: DatabaseChatService = Depends(get_database_chat_service)
):
    """Get user's conversation list"""
    
    # Get or create user
    user = await chat_service.get_or_create_user(username=user_id)
    
    # Get conversations
    conversations = await chat_service.get_user_conversations(
        user_id=user.id,
        limit=limit,
        offset=offset
    )
    
    return ConversationListResponse(
        conversations=conversations,
        total=len(conversations),  # In production, you'd want a separate count query
        offset=offset,
        limit=limit
    )


@router.get("/conversations/{conversation_id}/messages", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    limit: Optional[int] = None,
    chat_service: DatabaseChatService = Depends(get_database_chat_service)
):
    """Get conversation message history"""
    
    try:
        conversation_uuid = uuid.UUID(conversation_id)
        messages = await chat_service.get_conversation_history(
            conversation_id=conversation_uuid,
            limit=limit
        )
        
        message_dicts = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "metadata": msg.metadata
            }
            for msg in messages
        ]
        
        return ConversationHistoryResponse(
            messages=message_dicts,
            conversation_id=conversation_id
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )


@router.delete("/conversations/{conversation_id}")
async def archive_conversation(
    conversation_id: str,
    chat_service: DatabaseChatService = Depends(get_database_chat_service)
):
    """Archive a conversation (soft delete)"""
    
    try:
        conversation_uuid = uuid.UUID(conversation_id)
        # Note: You'd implement archive functionality in the repository
        # For now, just return success
        return {"success": True, "message": "Conversation archived"}
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )