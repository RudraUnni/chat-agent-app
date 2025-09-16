from pydantic import BaseModel, Field
import requests
import json

class Pipeline:
    class Valves(BaseModel):
        SUMMARIZER_ENABLED: bool = Field(default=True, description="Enable PDF summarizer")
        FASTAPI_BASE_URL: str = Field(default="http://backend:8000", description="Backend FastAPI URL")
        API_ENDPOINT: str = Field(default="/api/v1/chat", description="Chat API endpoint")
        WORKFLOW: str = Field(default="pubmed_research", description="Medical workflow")
        
    def __init__(self):
        self.name = "PDF Summarizer"
        self.valves = self.Valves()

    def pipe(self, body: dict) -> str:
        """
        PDF summarization tool that integrates with your medical assistant workflow
        """
        if not self.valves.SUMMARIZER_ENABLED:
            return "PDF Summarizer is currently disabled"
            
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
                "session_id": f"pdf_pipeline_{hash(str(messages))}",
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
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    summary = result.get("response", "")
                    return f"""**📄 PDF Summarizer Tool - Medical Assistant Analysis**

{summary}

---
*Processed by Medical Assistant Workflow | Tool: PDF Summarizer*"""
                else:
                    return f"**PDF Summarizer Error:** {result.get('error', 'Unknown error')}"
            else:
                return f"**PDF Summarizer Error:** Unable to process request (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "**PDF Summarizer Timeout:** Document processing took too long."
        except requests.exceptions.ConnectionError:
            return "**PDF Summarizer Error:** Unable to connect to the medical assistant backend."
        except Exception as e:
            return f"**PDF Summarizer Error:** {str(e)}"