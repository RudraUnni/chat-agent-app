#!/usr/bin/env python3
"""
Simple test backend for Medical Assistant Pro
Minimal FastAPI server for testing without complex dependencies
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Medical Assistant Pro - Test Backend",
    version="1.0.0",
    description="Simple test backend for Medical Assistant Pro"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    workflow: str = "pubmed_research"
    session_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Medical Assistant Pro Test Backend is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "medical-assistant-pro", "version": "1.0.0"}

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Simple chat endpoint for testing
    """
    try:
        # Generate a simple response based on the message
        user_message = request.message.lower()
        
        if "health" in user_message or "diabetes" in user_message:
            response_text = """Based on current medical research, diabetes management typically involves:

1. **Lifestyle Modifications**:
   - Regular physical activity (150 minutes/week moderate exercise)
   - Balanced diet with controlled carbohydrate intake
   - Weight management if overweight

2. **Medications** (as prescribed by healthcare provider):
   - Metformin (first-line treatment for Type 2)
   - Insulin therapy (for Type 1 and advanced Type 2)
   - Other medications as indicated

3. **Monitoring**:
   - Regular blood glucose monitoring
   - HbA1c testing every 3-6 months
   - Regular check-ups with healthcare team

4. **Complications Prevention**:
   - Regular eye exams
   - Foot care and inspection
   - Cardiovascular risk management

*Note: This is a simplified test response. For actual medical advice, consult healthcare professionals.*"""
        
        elif "hello" in user_message or "test" in user_message:
            response_text = """Hello! I'm the Medical Assistant Pro test backend. I'm working correctly!

This is a simplified version for testing purposes. In the full system, I would:
- Search PubMed for relevant medical research
- Analyze research papers and provide citations
- Maintain conversation context across multiple queries
- Provide evidence-based medical information

For this test, I'm confirming that the backend API is functioning properly."""

        elif "treatments" in user_message:
            response_text = """I understand you're asking about medical treatments. In the full system, I would:

1. Search PubMed database for recent research papers
2. Analyze relevant studies and clinical trials  
3. Provide evidence-based treatment options with citations
4. Include safety information and contraindications

For this test version, I'm demonstrating that the medical workflow endpoint is accessible and responding correctly."""

        else:
            response_text = f"""Thank you for your message: "{request.message}"

This is the Medical Assistant Pro test backend. I'm successfully:
- Receiving your request via the /api/v1/chat endpoint
- Processing the medical workflow: {request.workflow}
- Managing session: {request.session_id or 'auto-generated'}
- Returning a structured response

In the full system, I would provide detailed medical research and analysis."""

        # Add medical disclaimer
        disclaimer = "\n\n---\n⚠️ **Medical Disclaimer**: This is a test system. For actual medical advice, always consult with qualified healthcare professionals."
        
        return ChatResponse(
            success=True,
            response=response_text + disclaimer,
            data={
                "workflow": request.workflow,
                "message_length": len(request.message),
                "test_mode": True
            },
            session_id=request.session_id or "test_session_123"
        )
        
    except Exception as e:
        return ChatResponse(
            success=False,
            error=f"Test backend error: {str(e)}",
            session_id=request.session_id or "error_session"
        )

@app.get("/api/v1/workflows")
async def list_workflows():
    """List available workflows"""
    return {
        "workflows": [
            {
                "name": "pubmed_research",
                "description": "Medical research using PubMed database",
                "status": "test_mode"
            }
        ]
    }

if __name__ == "__main__":
    print("🏥 Starting Medical Assistant Pro Test Backend...")
    print("🔍 This is a simplified version for testing without Docker")
    print("📱 Access points:")
    print("   • Health: http://localhost:8000/health")
    print("   • API Docs: http://localhost:8000/docs") 
    print("   • Chat: POST http://localhost:8000/api/v1/chat")
    print("")
    
    uvicorn.run(
        "simple_test_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )