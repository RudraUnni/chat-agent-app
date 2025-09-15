"""
Clean OpenRouter runtime with function tools and simplified agent wrapper.
"""
import os
import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from app.services.llm.openrouter_client import get_openrouter_client, OpenRouterResponse

logger = logging.getLogger(__name__)

# Function tool registry for local fallback
_function_registry: Dict[str, Callable] = {}


def function_tool(name: str, description: str):
    """Decorator to register functions as tools with agents fallback + local registry"""
    def decorator(func: Callable) -> Callable:
        # Register in local registry for fallback
        _function_registry[name] = func
        
        # Try to register with agents library if available
        try:
            from agents import function
            # Apply agents decorator
            agents_decorated = function(name=name, description=description)(func)
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return agents_decorated(*args, **kwargs)
            
            return wrapper
            
        except ImportError:
            logger.info(f"Agents library not available, using local registry for {name}")
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
    
    return decorator


def get_function_tool(name: str) -> Optional[Callable]:
    """Get a function tool from the registry"""
    return _function_registry.get(name)


def list_function_tools() -> List[str]:
    """List all registered function tools"""
    return list(_function_registry.keys())


class Agent:
    """Clean Agent wrapper using OpenRouter client"""
    
    def __init__(self, name: str, instructions: str = "", model: str = "openai/gpt-4o-mini", tools: List = None):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.tools = tools or []
        self.client = get_openrouter_client()
        
        logger.info(f"Initialized agent '{name}' with model '{model}'")
    
    async def invoke(self, user_input: str, conversation_history: List[Dict[str, str]] = None, **kwargs) -> str:
        """Execute agent with conversation history support"""
        try:
            # Build messages from conversation history and current input
            messages = []
            
            # Add system message if instructions provided
            if self.instructions:
                messages.append({"role": "system", "content": self.instructions})
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    if msg.get("role") in ["user", "assistant", "system"]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Create completion
            response = await self.client.create_completion(
                messages=messages,
                model=self.model,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000)
            )
            
            logger.debug(f"Agent '{self.name}' completed request")
            return response.content
            
        except Exception as e:
            logger.error(f"Agent '{self.name}' error: {e}")
            return f"Error: {str(e)}"
    
    def as_tool(self, name: str, description: str) -> Callable:
        """Convert agent to a tool function"""
        agent_ref = self
        
        @function_tool(name=name, description=description)
        def tool_func(query: str) -> str:
            """Tool wrapper for agent execution"""
            try:
                # Handle async execution in sync context
                loop = asyncio.get_running_loop()
                return asyncio.create_task(agent_ref.invoke(query)).result()
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                return asyncio.run(agent_ref.invoke(query))
            except Exception as e:
                return f"Tool execution error: {str(e)}"
        
        return tool_func


# Compatibility classes for existing code
class AgentResponse:
    """Response wrapper for compatibility"""
    def __init__(self, text: str):
        self.output = text
        self.final_output = text


class RunnerResult:
    """Result wrapper for compatibility"""
    def __init__(self, final_output: str):
        self.final_output = final_output
        self.output = final_output


# Initialize OpenRouter client on module import
try:
    client = get_openrouter_client()
    logger.info("OpenRouter runtime initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenRouter runtime: {e}")