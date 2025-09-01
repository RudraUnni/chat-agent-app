from typing import List, Union, Generator, Iterator
import requests
import json
from pydantic import BaseModel
import logging
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    class Valves(BaseModel):
        FASTAPI_BASE_URL: str = "http://backend:8000"  # Docker service name
        API_ENDPOINT: str = "/api/v1/chat"
        WORKFLOW: str = "pubmed_research"  # Default workflow from your backend
        API_KEY: str = ""  # Optional API key for your FastAPI
        
    def __init__(self):
        self.name = "Medical Assistant Pipeline"
        self.valves = self.Valves()
        logger.info(f"Initialized {self.name}")

    async def on_startup(self):
        logger.info(f"Medical Assistant Pipeline starting up...")

    async def on_shutdown(self):
        logger.info(f"Medical Assistant Pipeline shutting down...")

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Main pipeline function that forwards requests to your FastAPI backend
        Integrates with your existing workflow system and chat management
        """
        try:
            logger.info(f"Processing message for model: {model_id}")
            
            # Extract session_id from body or generate new one
            session_id = body.get("session_id") or str(uuid.uuid4())
            
            # Convert Open WebUI messages format to your backend format
            conversation_history = []
            for msg in messages:
                if msg.get("role") in ["user", "assistant", "system"]:
                    conversation_history.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Prepare the request payload for your FastAPI endpoint
            payload = {
                "message": user_message,
                "workflow": self.valves.WORKFLOW,
                "session_id": session_id,
                "parameters": {
                    "conversation_history": conversation_history,
                    "model_id": model_id
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.valves.API_KEY:
                headers["Authorization"] = f"Bearer {self.valves.API_KEY}"
            
            logger.info(f"Sending request to {self.valves.FASTAPI_BASE_URL}{self.valves.API_ENDPOINT}")
            
            # Make request to your FastAPI backend
            response = requests.post(
                f"{self.valves.FASTAPI_BASE_URL}{self.valves.API_ENDPOINT}",
                json=payload,
                headers=headers,
                timeout=60  # 60 second timeout for medical queries
            )
            
            logger.info(f"Received response with status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    response_text = result.get("response", "No response from medical assistant")
                    logger.info(f"Successful response received")
                    return response_text
                else:
                    error_msg = result.get("error", "Unknown error from medical assistant")
                    logger.error(f"Backend error: {error_msg}")
                    return f"Medical Assistant Error: {error_msg}"
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"HTTP error: {error_msg}")
                return f"Connection Error: Failed to reach medical assistant ({response.status_code})"
                
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return "Timeout Error: The medical assistant took too long to respond. Please try again."
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return "Connection Error: Unable to connect to the medical assistant backend. Please check if the backend service is running."
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"Unexpected Error: {str(e)}"