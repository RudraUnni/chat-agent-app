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
    
    async def invoke(self, user_input: str, **kwargs) -> str:
        """Async wrapper for OpenAI Agent execution"""
        result = await OpenAIRunner.run(self, user_input)
        return result.final_output
    
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