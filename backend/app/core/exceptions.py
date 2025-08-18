"""
Standard exception classes and error handling utilities.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class ChatServiceError(Exception):
    """Base exception for chat service errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(ChatServiceError):
    """Database-related errors"""
    pass


class WorkflowError(ChatServiceError):
    """Workflow execution errors"""
    pass


class LLMError(ChatServiceError):
    """LLM provider errors"""
    pass


class ConfigurationError(ChatServiceError):
    """Configuration-related errors"""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create a standardized HTTP exception"""
    detail = {
        "message": message,
        "error_code": error_code,
        "details": details or {}
    }
    return HTTPException(status_code=status_code, detail=detail)


def handle_service_error(error: ChatServiceError) -> HTTPException:
    """Convert service errors to HTTP exceptions"""
    if isinstance(error, DatabaseError):
        return create_http_exception(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            error.message,
            error.error_code,
            error.details
        )
    elif isinstance(error, WorkflowError):
        return create_http_exception(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            error.message,
            error.error_code,
            error.details
        )
    elif isinstance(error, LLMError):
        return create_http_exception(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            error.message,
            error.error_code,
            error.details
        )
    elif isinstance(error, ConfigurationError):
        return create_http_exception(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            error.message,
            error.error_code,
            error.details
        )
    else:
        return create_http_exception(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            str(error),
            "UNKNOWN_ERROR"
        )