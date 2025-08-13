from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChatMessage(BaseModel):
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = {}


class ChatSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    metadata: Optional[Dict[str, Any]] = {}


class WorkflowRequest(BaseModel):
    workflow: str
    input_data: Dict[str, Any]
    session_id: Optional[str] = None
    stream: bool = False


class WorkflowResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: str
    workflow: str