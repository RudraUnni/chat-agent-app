"""
Medical Assistant Function for OpenWebUI
Connects OpenWebUI to the FastAPI medical workflow backend
"""

import requests
import json
import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    workflow: str = "pubmed_research"
    session_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}


def medical_assistant_chat(
    message: str,
    __user__: dict = {},
    __event_emitter__=None,
    __model__: str = "medical-assistant",
    __messages__: list = [],
    __tools__: dict = {},
    __task__: str = "",
    __citation__: bool = False,
) -> str:
    """
    Medical Assistant powered by PubMed research and medical workflows
    
    This function connects OpenWebUI to your custom medical FastAPI backend,
    providing access to PubMed research tools and medical consultation capabilities.
    
    Args:
        message: User's medical question or query
        __user__: OpenWebUI user context
        __event_emitter__: OpenWebUI event emitter for streaming
        __model__: Model identifier
        __messages__: Conversation history
        __tools__: Available tools
        __task__: Current task context
        __citation__: Whether to include citations
    
    Returns:
        Medical assistant response with research citations
    """
    
    try:
        # Extract session info
        user_id = __user__.get("id", "anonymous")
        session_id = f"openwebui_{user_id}_{str(uuid.uuid4())[:8]}"
        
        # Emit status update
        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "🔍 Consulting medical research database...", "done": False},
                }
            )
        
        # Prepare request to FastAPI backend
        backend_url = "http://backend:8000/api/v1/chat"
        
        # Build conversation history for context
        conversation_context = []
        for msg in __messages__[-10:]:  # Last 10 messages for context
            if msg.get("role") in ["user", "assistant"]:
                conversation_context.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "message": message,
            "workflow": "pubmed_research",
            "session_id": session_id,
            "parameters": {
                "conversation_history": conversation_context,
                "user_id": user_id,
                "include_citations": __citation__,
                "model": __model__
            }
        }
        
        # Emit processing status
        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status", 
                    "data": {"description": "🧠 Processing with medical AI agent...", "done": False},
                }
            )
        
        # Make request to FastAPI backend
        response = requests.post(
            backend_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                # Emit completion status
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "✅ Medical consultation complete", "done": True},
                        }
                    )
                
                medical_response = result.get("response", "No response received")
                
                # Add medical disclaimer
                disclaimer = "\n\n---\n*⚠️ Medical Disclaimer: This AI-powered information is for educational purposes only and should not replace professional medical advice. Always consult with a qualified healthcare provider for medical decisions.*"
                
                return medical_response + disclaimer
            else:
                error_msg = result.get("error", "Unknown error occurred")
                return f"❌ Medical consultation error: {error_msg}\n\nPlease try rephrasing your question or contact support if the issue persists."
        
        else:
            return f"❌ Backend connection error (Status {response.status_code})\n\nThe medical assistant backend is currently unavailable. Please try again later."
    
    except requests.exceptions.Timeout:
        return "⏱️ Request timeout: The medical research query is taking longer than expected. Please try again with a more specific question."
    
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error: Unable to connect to the medical assistant backend. Please ensure the backend service is running."
    
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}\n\nPlease try again or contact support if the issue persists."


# OpenWebUI Function Metadata
medical_assistant_chat.title = "Medical Assistant Pro"
medical_assistant_chat.description = "AI-powered medical consultation with PubMed research integration"
medical_assistant_chat.citation = True