"""
Medical Model Integration for OpenWebUI
Creates a custom medical model that routes to FastAPI backend
"""

from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import requests
import json
import uuid


class Message(BaseModel):
    role: str
    content: str


def pipe(
    body: dict,
    __user__: dict = {},
    __model__: str = "medical-assistant",
    __messages__: List[Message] = [],
    __task__: str = "",
) -> Union[str, Generator, Iterator]:
    """
    Medical Assistant Model Pipeline
    
    Routes chat requests to the FastAPI medical backend and returns responses.
    This creates a custom "model" in OpenWebUI that actually calls your medical workflow.
    """
    
    try:
        # Extract the user's message
        if __messages__ and len(__messages__) > 0:
            user_message = __messages__[-1].content
        else:
            user_message = body.get("messages", [{}])[-1].get("content", "")
        
        if not user_message:
            return "Please provide a medical question or query."
        
        # Generate session ID
        user_id = __user__.get("id", "anonymous")
        session_id = f"openwebui_{user_id}_{str(uuid.uuid4())[:8]}"
        
        # Build conversation history
        conversation_history = []
        for msg in __messages__[:-1]:  # All messages except the current one
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare request to FastAPI backend
        backend_url = "http://backend:8000/api/v1/chat"
        
        payload = {
            "message": user_message,
            "workflow": "pubmed_research",
            "session_id": session_id,
            "parameters": {
                "conversation_history": conversation_history,
                "user_id": user_id,
                "openwebui_integration": True
            }
        }
        
        # Make request to backend
        response = requests.post(
            backend_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes for medical research
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                medical_response = result.get("response", "No response received")
                
                # Add medical disclaimer
                disclaimer = "\n\n---\n*⚠️ This AI-powered medical information is for educational purposes only. Always consult with qualified healthcare providers for medical decisions.*"
                
                return medical_response + disclaimer
            else:
                error_msg = result.get("error", "Unknown error")
                return f"❌ Medical consultation error: {error_msg}"
        else:
            return f"❌ Backend error (HTTP {response.status_code}): Unable to process medical query"
    
    except requests.exceptions.Timeout:
        return "⏱️ Medical research timeout: Query took too long. Please try a more specific question."
    
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error: Medical backend unavailable. Please ensure the backend service is running."
    
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Metadata for OpenWebUI
pipe.type = "pipe"
pipe.id = "medical-assistant"
pipe.name = "Medical Assistant Pro"
pipe.description = "AI-powered medical consultation with PubMed research capabilities"