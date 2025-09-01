from typing import List, Union, Generator, Iterator
import requests
import json
from pydantic import BaseModel
import logging
import re
import base64

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    class Valves(BaseModel):
        SUMMARIZER_ENABLED: bool = True
        MAX_PDF_SIZE_MB: int = 10
        FASTAPI_BASE_URL: str = "http://backend:8000"
        API_ENDPOINT: str = "/api/v1/chat"
        WORKFLOW: str = "pubmed_research"  # Use your medical workflow for summarization
        
    def __init__(self):
        self.name = "PDF Summarizer Tool"
        self.valves = self.Valves()
        logger.info(f"Initialized {self.name}")

    async def on_startup(self):
        logger.info(f"PDF Summarizer Tool starting up...")

    async def on_shutdown(self):
        logger.info(f"PDF Summarizer Tool shutting down...")

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        PDF summarization tool that integrates with your medical assistant workflow
        """
        if not self.valves.SUMMARIZER_ENABLED:
            return "PDF Summarizer is currently disabled"
            
        # Check if message contains PDF-related keywords
        pdf_keywords = ["pdf", "summarize", "summary", "document", "file", "paper", "article"]
        message_lower = user_message.lower()
        
        if not any(keyword in message_lower for keyword in pdf_keywords):
            return """**PDF Summarizer Tool**

This tool helps summarize PDF documents using your medical assistant.

**How to use:**
1. Mention keywords like 'PDF', 'summarize', 'document', or 'paper' in your message
2. Describe what you want summarized
3. The tool will process your request through the medical assistant workflow

**Example:** "Can you summarize this PDF about diabetes treatment?"

**Current capabilities:**
- Medical document analysis
- Research paper summarization  
- Clinical guideline extraction
- Treatment protocol summaries

Please rephrase your message to include PDF-related keywords to activate this tool."""
        
        try:
            logger.info(f"Processing PDF summarization request")
            
            # Enhance the message for PDF summarization context
            enhanced_message = f"""PDF Summarization Request: {user_message}

Please provide a comprehensive summary focusing on:
- Key medical findings or conclusions
- Treatment recommendations
- Clinical significance
- Methodology (if research paper)
- Practical applications

If this is about a specific PDF document, please provide the document content or key excerpts for analysis."""

            # Prepare request for your FastAPI backend
            payload = {
                "message": enhanced_message,
                "workflow": self.valves.WORKFLOW,
                "session_id": body.get("session_id"),
                "parameters": {
                    "task_type": "document_summarization",
                    "focus": "medical_content",
                    "output_format": "structured_summary"
                }
            }
            
            headers = {"Content-Type": "application/json"}
            
            # Make request to your medical assistant backend
            response = requests.post(
                f"{self.valves.FASTAPI_BASE_URL}{self.valves.API_ENDPOINT}",
                json=payload,
                headers=headers,
                timeout=90  # Longer timeout for document processing
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    summary = result.get("response", "")
                    
                    # Format the response with PDF tool branding
                    formatted_response = f"""**📄 PDF Summarizer Tool - Medical Assistant Analysis**

{summary}

---
*Processed by Medical Assistant Workflow | Tool: PDF Summarizer*"""
                    
                    return formatted_response
                else:
                    error_msg = result.get("error", "Unknown error")
                    return f"**PDF Summarizer Error:** {error_msg}"
            else:
                return f"**PDF Summarizer Error:** Unable to process request (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "**PDF Summarizer Timeout:** Document processing took too long. Please try with a smaller document or simpler request."
        except requests.exceptions.ConnectionError:
            return "**PDF Summarizer Error:** Unable to connect to the medical assistant backend."
        except Exception as e:
            logger.error(f"PDF Summarizer error: {str(e)}")
            return f"**PDF Summarizer Error:** {str(e)}"