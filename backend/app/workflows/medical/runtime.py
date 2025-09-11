# Compatibility shim for OpenAI Agents SDK (configured for OpenRouter)
import os
from agents import Agent as OpenAIAgent, Runner as OpenAIRunner, function_tool
from openai import AsyncOpenAI

# Ensure API key is available for the SDK (updated for OpenRouter)
def _ensure_api_key():
    """Ensure API key is set in environment for OpenRouter compatibility"""
    # For the agents library to work with OpenRouter, we need to set the OpenAI environment variables
    # to point to OpenRouter's API
    
    if not os.getenv("OPENAI_API_KEY"):
        try:
            from app.core.config import get_settings
            settings = get_settings()
            if settings.openrouter_api_key:
                # Set OpenRouter API key as OPENAI_API_KEY for agents library compatibility
                os.environ["OPENAI_API_KEY"] = settings.openrouter_api_key
                print(f"Set OPENAI_API_KEY from settings for agents library compatibility")
        except Exception as e:
            print(f"Could not load OpenRouter API key from settings: {e}")
    
    if not os.getenv("OPENAI_BASE_URL"):
        try:
            from app.core.config import get_settings
            settings = get_settings()
            if settings.openrouter_base_url:
                # Set OpenRouter base URL as OPENAI_BASE_URL for agents library compatibility
                os.environ["OPENAI_BASE_URL"] = settings.openrouter_base_url
                print(f"Set OPENAI_BASE_URL to {settings.openrouter_base_url} for agents library compatibility")
        except Exception as e:
            print(f"Could not load OpenRouter base URL from settings: {e}")
    
    # Also try to get from environment directly
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = openrouter_key
        print("Set OPENAI_API_KEY from OPENROUTER_API_KEY environment variable")
    
    openrouter_base_url = os.getenv("OPENROUTER_BASE_URL")
    if openrouter_base_url and not os.getenv("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = openrouter_base_url
        print(f"Set OPENAI_BASE_URL to {openrouter_base_url} from environment variable")

# Set API key on module import
_ensure_api_key()


# Response compatibility adapter for OpenRouter
class OpenRouterResponseAdapter:
    """Adapter to make OpenRouter responses compatible with openai-agents library expectations"""
    
    @staticmethod
    def patch_openai_client():
        """Monkey patch the OpenAI client to handle OpenRouter responses properly"""
        try:
            import openai
            from openai.types.chat import ChatCompletion
            
            # Store original create method
            original_create = openai.AsyncOpenAI.chat.completions.create
            
            async def patched_create(self, **kwargs):
                """Patched create method that ensures response compatibility"""
                try:
                    response = await original_create(self, **kwargs)
                    
                    # Ensure the response has the expected structure for agents library
                    if hasattr(response, 'choices') and response.choices:
                        choice = response.choices[0]
                        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                            # Add output attribute if it doesn't exist
                            if not hasattr(response, 'output'):
                                response.output = choice.message.content
                            if not hasattr(choice.message, 'output'):
                                choice.message.output = choice.message.content
                    
                    return response
                except Exception as e:
                    print(f"Error in patched OpenAI client: {e}")
                    raise
            
            # Apply the patch
            openai.AsyncOpenAI.chat.completions.create = patched_create
            print("Applied OpenRouter response compatibility patch to OpenAI client")
            
        except Exception as e:
            print(f"Could not apply OpenRouter response patch: {e}")
    
    @staticmethod
    def create_compatible_response(content: str):
        """Create a response object that's compatible with agents library expectations"""
        class CompatibleMessage:
            def __init__(self, content: str):
                self.content = content
                self.output = content  # Add output attribute for compatibility
        
        class CompatibleChoice:
            def __init__(self, content: str):
                self.message = CompatibleMessage(content)
        
        class CompatibleResponse:
            def __init__(self, content: str):
                self.choices = [CompatibleChoice(content)]
                self.output = content  # Add output attribute for compatibility
        
        return CompatibleResponse(content)


# Apply the response adapter patch
adapter = OpenRouterResponseAdapter()
adapter.patch_openai_client()


# Additional monkey patches for agents library compatibility
def patch_agents_library():
    """Apply additional patches to the agents library for OpenRouter compatibility"""
    try:
        # Import agents library modules that might need patching
        import agents
        from agents import Runner as OpenAIRunner
        
        # Store original run method
        if hasattr(OpenAIRunner, 'run'):
            original_run = OpenAIRunner.run
            
            async def patched_run(agent, *args, **kwargs):
                """Patched run method that handles OpenRouter responses properly"""
                try:
                    result = await original_run(agent, *args, **kwargs)
                    
                    # If result is a string, wrap it in a compatible object
                    if isinstance(result, str):
                        class CompatibleResult:
                            def __init__(self, content):
                                self.output = content
                                self.final_output = content
                                self.content = content
                        
                        return CompatibleResult(result)
                    
                    # If result doesn't have expected attributes, add them
                    if not hasattr(result, 'output') and hasattr(result, 'content'):
                        result.output = result.content
                    if not hasattr(result, 'final_output'):
                        if hasattr(result, 'output'):
                            result.final_output = result.output
                        elif hasattr(result, 'content'):
                            result.final_output = result.content
                    
                    return result
                    
                except Exception as e:
                    print(f"Error in patched agents run method: {e}")
                    # Return a compatible error response
                    class ErrorResult:
                        def __init__(self, error_msg):
                            self.output = f"Error: {error_msg}"
                            self.final_output = f"Error: {error_msg}"
                    
                    return ErrorResult(str(e))
            
            # Apply the patch
            OpenAIRunner.run = patched_run
            print("Applied agents library run method compatibility patch")
    
    except Exception as e:
        print(f"Could not apply agents library patches: {e}")


# Apply additional patches
patch_agents_library()


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
            
        try:
            # Use the original OpenAI agents library, but with our compatibility patches
            result = await OpenAIRunner.run(self, full_input)
            
            # Handle different response types that might come from OpenRouter
            if hasattr(result, 'final_output'):
                return result.final_output
            elif hasattr(result, 'output'):
                return result.output
            elif isinstance(result, str):
                return result
            else:
                # If it's some other type, try to extract content
                if hasattr(result, 'choices') and result.choices:
                    return result.choices[0].message.content
                elif hasattr(result, 'content'):
                    return result.content
                else:
                    return str(result)
        except Exception as e:
            print(f"Error in Agent.invoke: {e}")
            # Fallback: use our custom OpenRouter runner
            fallback_runner = OpenRouterRunner()
            result = await fallback_runner.run(self, full_input)
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
    """Compatibility wrapper for OpenAI Runner with OpenRouter support"""
    
    def __init__(self, *args, **kwargs):
        """Initialize runner and ensure API key is set"""
        _ensure_api_key()
        super().__init__(*args, **kwargs)


class RunnerResult:
    """Compatibility class for result handling"""
    def __init__(self, final_output: str):
        self.final_output = final_output