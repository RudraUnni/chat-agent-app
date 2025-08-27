# Compatibility shim for OpenAI Agents SDK
import os
from agents import Agent as OpenAIAgent, Runner as OpenAIRunner, function_tool

# Ensure OpenAI API key is available for the SDK
def _ensure_api_key():
    """Ensure OpenAI API key is set in environment"""
    if not os.getenv("OPENAI_API_KEY"):
        # Try to load from config
        try:
            from app.core.config import get_settings
            settings = get_settings()
            if settings.openai_api_key:
                os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        except Exception:
            pass

# Set API key on module import
_ensure_api_key()


class Agent(OpenAIAgent):
    """Wrapper to maintain backward compatibility while using OpenAI Agents SDK"""
    
    def __init__(self, *args, **kwargs):
        """Initialize agent and ensure API key is set"""
        _ensure_api_key()
        super().__init__(*args, **kwargs)
    
    async def invoke(self, user_input: str, conversation_history: list = None, **kwargs) -> str:
        """Async wrapper for OpenAI Agent execution with conversation history"""
        if conversation_history:
            # Format conversation history for the agent
            # The OpenAI Agents SDK expects a specific format for conversation history
            # We'll pass the history as part of the user input context
            history_context = self._format_conversation_history(conversation_history)
            
            # Combine history context with current user input
            if history_context:
                full_input = f"{history_context}\n\nCurrent message: {user_input}"
            else:
                full_input = user_input
        else:
            full_input = user_input
            
        result = await OpenAIRunner.run(self, full_input)
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


class Runner(OpenAIRunner):
    """Compatibility wrapper for OpenAI Runner"""
    pass


class RunnerResult:
    """Compatibility class for result handling"""
    def __init__(self, final_output: str):
        self.final_output = final_output