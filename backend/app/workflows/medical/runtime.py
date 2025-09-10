# Compatibility shim for OpenAI Agents SDK (configured for OpenRouter)
import os
from agents import Agent as OpenAIAgent, Runner as OpenAIRunner, function_tool
from openai import AsyncOpenAI

# Ensure API key is available for the SDK (updated for OpenRouter)
def _ensure_api_key():
    """Ensure API key is set in environment for OpenRouter compatibility"""
    # OpenAI API key handling (commented out for OpenRouter migration)
    # if not os.getenv("OPENAI_API_KEY"):
    #     # Try to load from config
    #     try:
    #         from app.core.config import get_settings
    #         settings = get_settings()
    #         if settings.openai_api_key:
    #             os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    #     except Exception:
    #         pass
    
    # Set OpenRouter API key as OPENAI_API_KEY for compatibility (commented out for OpenRouter migration)
    # if not os.getenv("OPENAI_API_KEY"):
    #     try:
    #         from app.core.config import get_settings
    #         settings = get_settings()
    #         if settings.openrouter_api_key:
    #             os.environ["OPENAI_API_KEY"] = settings.openrouter_api_key
    #             # Also set the base URL for OpenRouter
    #             os.environ["OPENAI_BASE_URL"] = settings.openrouter_base_url
    #     except Exception:
    #         pass

# Set API key on module import
_ensure_api_key()


class AgentResponse:
    """Response wrapper to maintain compatibility with expected interface"""
    def __init__(self, text: str):
        self.output = text
        self.final_output = text


class OpenRouterRunner:
    """OpenRouter-compatible runner that mimics OpenAI Agents SDK interface"""
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Get or create AsyncOpenAI client configured for OpenRouter"""
        if self.client is None:
            # Get OpenRouter API key
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                # Try to get from settings
                try:
                    from app.core.config import get_settings
                    settings = get_settings()
                    api_key = settings.openrouter_api_key
                except Exception:
                    pass
            
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not found in environment or settings")
            
            # Get base URL
            base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            try:
                from app.core.config import get_settings
                settings = get_settings()
                base_url = settings.openrouter_base_url
            except Exception:
                pass
            
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
        
        return self.client
    
    async def run(self, agent, user_input: str) -> AgentResponse:
        """Run agent with OpenRouter backend"""
        client = self._get_client()
        
        # Extract model from agent if available, otherwise use default
        model = getattr(agent, 'model', 'openai/gpt-4o-mini')
        
        # Extract instructions from agent if available
        instructions = getattr(agent, 'instructions', '')
        
        # Prepare messages
        messages = []
        if instructions:
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Call OpenRouter API
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            
            # Return wrapped response
            return AgentResponse(content)
            
        except Exception as e:
            # Return error as response to maintain compatibility
            error_msg = f"OpenRouter API error: {str(e)}"
            return AgentResponse(error_msg)


class Agent(OpenAIAgent):
    """Wrapper to maintain backward compatibility while using OpenRouter instead of OpenAI"""
    
    def __init__(self, *args, **kwargs):
        """Initialize agent and ensure API key is set"""
        _ensure_api_key()
        super().__init__(*args, **kwargs)
        # Create OpenRouter runner instance
        self._openrouter_runner = OpenRouterRunner()
    
    async def invoke(self, user_input: str, conversation_history: list = None, **kwargs) -> str:
        """Async wrapper for Agent execution with conversation history (via OpenRouter)"""
        if conversation_history:
            # Format conversation history for the agent
            # We'll pass the history as part of the user input context
            history_context = self._format_conversation_history(conversation_history)
            
            # Combine history context with current user input
            if history_context:
                full_input = f"{history_context}\n\nCurrent message: {user_input}"
            else:
                full_input = user_input
        else:
            full_input = user_input
            
        # Use OpenRouter runner instead of OpenAI runner
        result = await self._openrouter_runner.run(self, full_input)
        return result.final_output
    
    def _format_conversation_history(self, conversation_history: list) -> str:
        """Format conversation history for agent context"""
        if not conversation_history:
            return ""
        
        formatted_messages = []
        for msg in conversation_history[:-1]:  # Exclude the current message (last one)
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                formatted_messages.append(f"User: {content}")
            elif role == "assistant":
                formatted_messages.append(f"Assistant: {content}")
        
        if formatted_messages:
            return "Previous conversation:\n" + "\n".join(formatted_messages)
        return ""
    
    def as_tool(self, name: str, description: str):
        """Convert agent to a tool for use by other agents"""
        agent_ref = self
        
        @function_tool
        def tool_func(query: str) -> str:
            """Tool wrapper for agent execution"""
            import asyncio
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(agent_ref.invoke(query))
            else:
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, agent_ref.invoke(query))
                    return future.result()
        
        tool_func.__name__ = name
        tool_func.__doc__ = description
        return tool_func


class Runner(OpenRouterRunner):
    """Compatibility wrapper for OpenRouter Runner"""
    pass


class RunnerResult:
    """Compatibility class for result handling"""
    def __init__(self, final_output: str):
        self.final_output = final_output