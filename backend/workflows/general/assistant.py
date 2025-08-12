from typing import Dict, Any, Optional
from workflows.base import BaseWorkflow, WorkflowContext, WorkflowResult
from app.services.llm.factory import LLMFactory
from app.services.llm.base import Message
from app.core.config import settings


class GeneralAssistantWorkflow(BaseWorkflow):
    """General purpose chat assistant workflow"""
    
    def __init__(self):
        super().__init__(
            name="General Assistant",
            description="General purpose conversational assistant"
        )
    
    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[WorkflowContext] = None
    ) -> WorkflowResult:
        """Execute general assistant workflow"""
        
        try:
            user_message = input_data.get('message', '')
            if not user_message:
                return WorkflowResult(
                    success=False,
                    error="Message is required"
                )
            
            # Get conversation history from context
            history = []
            if context and context.history:
                history = context.history[-10:]  # Keep last 10 messages
            
            # Create LLM messages
            messages = [
                Message(
                    role="system",
                    content="You are a helpful AI assistant. Provide clear, accurate, and helpful responses."
                )
            ]
            
            # Add history
            for h in history:
                messages.append(Message(
                    role=h.get('role', 'user'),
                    content=h.get('content', '')
                ))
            
            # Add current message
            messages.append(Message(role="user", content=user_message))
            
            # Get LLM response
            llm = LLMFactory.create(settings.default_llm_provider)
            response = await llm.generate(
                messages,
                temperature=input_data.get('temperature', 0.7),
                max_tokens=input_data.get('max_tokens')
            )
            
            # Update context history
            if context:
                context.history.append({'role': 'user', 'content': user_message})
                context.history.append({'role': 'assistant', 'content': response.content})
            
            return WorkflowResult(
                success=True,
                data={
                    'response': response.content,
                    'model': response.model,
                    'usage': response.usage
                }
            )
            
        except Exception as e:
            return WorkflowResult(
                success=False,
                error=str(e)
            )