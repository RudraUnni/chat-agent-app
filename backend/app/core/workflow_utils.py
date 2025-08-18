"""
Utilities for standardizing workflow response handling.
"""

from typing import Dict, Any, Optional
from workflows.base import WorkflowResult


def extract_workflow_response(result: WorkflowResult, workflow_name: str) -> str:
    """
    Extract a standardized response from workflow result data.
    
    Args:
        result: The workflow execution result
        workflow_name: Name of the workflow that was executed
        
    Returns:
        Formatted response string
    """
    if not result.success or not result.data:
        return ""
    
    # Try workflow-specific response extraction first
    response_text = ""
    
    if workflow_name == "general_assistant":
        response_text = result.data.get('response', '')
    elif workflow_name == "pubmed_research":
        response_text = (
            result.data.get('formatted_summary') or 
            result.data.get('analysis') or 
            result.data.get('output', '')
        )
    
    # Fallback to common response fields
    if not response_text:
        response_text = (
            result.data.get('response') or
            result.data.get('output') or
            result.data.get('content') or
            result.data.get('text', '')
        )
    
    # Last resort: convert data to string if it's simple enough
    if not response_text and isinstance(result.data, dict) and len(result.data) == 1:
        key, value = next(iter(result.data.items()))
        if isinstance(value, str):
            response_text = value
    
    return response_text or "No response generated"


def format_workflow_error(result: WorkflowResult, workflow_name: str) -> str:
    """
    Format workflow error message in a standardized way.
    
    Args:
        result: The workflow execution result
        workflow_name: Name of the workflow that failed
        
    Returns:
        Formatted error message
    """
    if result.error:
        return f"Workflow '{workflow_name}' failed: {result.error}"
    else:
        return f"Workflow '{workflow_name}' execution failed with unknown error"