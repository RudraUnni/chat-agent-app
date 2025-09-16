from pydantic import BaseModel, Field
import requests
import json
import logging

class Pipeline:
    class Valves(BaseModel):
        FASTAPI_BASE_URL: str = Field(default="http://backend:8000", description="Backend FastAPI URL")
        API_ENDPOINT: str = Field(default="/api/v1/chat", description="Chat API endpoint")
        WORKFLOW: str = Field(default="pubmed_research", description="Default workflow")
        API_KEY: str = Field(default="", description="Optional API key")
        
    def __init__(self):
        self.name = "Medical Assistant"
        self.valves = self.Valves()

    def pipe(self, body: dict) -> str:
        """
        Main pipeline function that forwards requests to your FastAPI backend
        """
        try:
            # Extract message from body
            messages = body.get("messages", [])
            if not messages:
                return "No messages provided"
            
            # Get the last user message
            user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            if not user_message:
                return "No user message found"
            
            # Prepare the request payload for your FastAPI endpoint
            payload = {
                "message": user_message,
                "workflow": self.valves.WORKFLOW,
                "session_id": f"pipeline_{hash(str(messages))}",
                "parameters": {
                    "conversation_history": messages
                }
            }
            
            headers = {"Content-Type": "application/json"}
            if self.valves.API_KEY:
                headers["Authorization"] = f"Bearer {self.valves.API_KEY}"
            
            # Make request to your FastAPI backend
            response = requests.post(
                f"{self.valves.FASTAPI_BASE_URL}{self.valves.API_ENDPOINT}",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("response", "No response from medical assistant")
                else:
                    return f"Medical Assistant Error: {result.get('error', 'Unknown error')}"
            else:
                return f"Connection Error: Failed to reach medical assistant (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "Timeout Error: The medical assistant took too long to respond. Please try again."
        except requests.exceptions.ConnectionError:
            return "Connection Error: Unable to connect to the medical assistant backend."
        except Exception as e:
            return f"Unexpected Error: {str(e)}"