from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class WorkflowContext(BaseModel):
    """Context passed between workflow steps"""
    session_id: str
    user_id: Optional[str] = None
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = {}
    history: List[Dict[str, Any]] = []


class WorkflowResult(BaseModel):
    """Standard result from workflow execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseWorkflow(ABC):
    """Base class for all workflows"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: Optional[WorkflowContext] = None) -> WorkflowResult:
        """Execute the workflow with given input"""
        pass
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data before execution"""
        return True
    
    async def pre_execute(self, input_data: Dict[str, Any], context: WorkflowContext):
        """Hook called before execution"""
        pass
    
    async def post_execute(self, result: WorkflowResult, context: WorkflowContext):
        """Hook called after execution"""
        pass