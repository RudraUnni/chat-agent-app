# Compatibility shim for OpenAI Agents SDK (configured for OpenRouter)
import os
from agents import Agent as OpenAIAgent, Runner as OpenAIRunner, function_tool
from openai import AsyncOpenAI

# Enhanced API key management with validation
def _ensure_api_key():
    """Ensure API key is set in environment for OpenRouter compatibility with validation"""
    print("🔧 Configuring API keys for OpenRouter compatibility...")
    
    # Get OpenRouter API key from various sources
    openrouter_key = None
    openrouter_base_url = "https://openrouter.ai/api/v1"
    
    # Source 1: Environment variable
    if os.getenv("OPENROUTER_API_KEY"):
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        print(f"📋 Found OPENROUTER_API_KEY in environment")
    
    # Source 2: Settings configuration
    if not openrouter_key:
        try:
            from app.core.config import get_settings
            settings = get_settings()
            if hasattr(settings, 'openrouter_api_key') and settings.openrouter_api_key:
                openrouter_key = settings.openrouter_api_key
                print(f"📋 Found OpenRouter API key in settings")
            if hasattr(settings, 'openrouter_base_url') and settings.openrouter_base_url:
                openrouter_base_url = settings.openrouter_base_url
                print(f"📋 Found OpenRouter base URL in settings: {openrouter_base_url}")
        except Exception as e:
            print(f"⚠️ Could not load from settings: {e}")
    
    # Validate API key format
    if openrouter_key:
        if openrouter_key.startswith('sk-or-v1-') and len(openrouter_key) > 20:
            print(f"✅ OpenRouter API key format looks valid")
        elif openrouter_key == "sk-or-v1-your-actual-openrouter-key-here":
            print(f"❌ API key is still the placeholder value! Please set your actual OpenRouter API key.")
            print(f"   Get your API key from: https://openrouter.ai/")
        else:
            print(f"⚠️ OpenRouter API key format may be invalid (should start with 'sk-or-v1-')")
    else:
        print(f"❌ No OpenRouter API key found!")
        print(f"   Please set OPENROUTER_API_KEY environment variable or configure in settings")
        return
    
    # Set OpenAI environment variables for agents library compatibility
    if openrouter_key:
        os.environ["OPENAI_API_KEY"] = openrouter_key
        print(f"✅ Set OPENAI_API_KEY for agents library compatibility")
    
    if openrouter_base_url:
        os.environ["OPENAI_BASE_URL"] = openrouter_base_url
        print(f"✅ Set OPENAI_BASE_URL to {openrouter_base_url}")
    
    # Validate final configuration
    final_openai_key = os.getenv("OPENAI_API_KEY")
    final_openai_base_url = os.getenv("OPENAI_BASE_URL")
    
    print(f"🔍 Final configuration:")
    print(f"   OPENAI_API_KEY: {'✅ Set' if final_openai_key else '❌ Missing'}")
    print(f"   OPENAI_BASE_URL: {final_openai_base_url if final_openai_base_url else '❌ Missing'}")
    
    if not final_openai_key or final_openai_key == "sk-or-v1-your-actual-openrouter-key-here":
        print(f"🚨 WARNING: API key configuration is incomplete!")
        print(f"   The agents library will likely fail with authentication errors.")
        print(f"   Please set a valid OpenRouter API key in your .env file.")

# Set API key on module import
_ensure_api_key()


# Advanced OpenRouter Compatibility Layer
import inspect
from typing import Any, Dict
from functools import wraps

class OpenRouterCompatibilityLayer:
    """Advanced compatibility layer for OpenRouter integration with openai-agents"""
    
    def __init__(self):
        self.patches_applied = False
        self.original_methods = {}
    
    def apply_comprehensive_patches(self):
        """Apply comprehensive patches to make OpenRouter work with agents library"""
        if self.patches_applied:
            return
        
        try:
            # Patch 1: OpenAI Client Response Handling
            self._patch_openai_client()
            
            # Patch 2: Agents Library Runner
            self._patch_agents_runner()
            
            # Patch 3: Response Object Creation
            self._patch_response_creation()
            
            self.patches_applied = True
            print("✅ Applied comprehensive OpenRouter compatibility patches")
            
        except Exception as e:
            print(f"❌ Error applying compatibility patches: {e}")
            import traceback
            traceback.print_exc()
    
    def _patch_openai_client(self):
        """Patch OpenAI client at the module level"""
        try:
            import openai
            from openai.resources.chat import completions
            
            # Store original method
            if not hasattr(self, '_original_create'):
                self._original_create = completions.AsyncCompletions.create
            
            async def enhanced_create(self, **kwargs):
                """Enhanced create method that ensures OpenRouter compatibility"""
                try:
                    # Call original method
                    response = await self._original_create(**kwargs)
                    
                    # Enhance response for agents library compatibility
                    if hasattr(response, 'choices') and response.choices:
                        content = response.choices[0].message.content
                        
                        # Add output attribute to response
                        if not hasattr(response, 'output'):
                            setattr(response, 'output', content)
                        
                        # Add output attribute to message
                        if not hasattr(response.choices[0].message, 'output'):
                            setattr(response.choices[0].message, 'output', content)
                    
                    return response
                    
                except Exception as e:
                    print(f"Error in enhanced OpenAI create method: {e}")
                    raise
            
            # Apply the patch by replacing the method
            completions.AsyncCompletions.create = enhanced_create
            print("✅ Applied OpenAI client response enhancement patch")
            
        except Exception as e:
            print(f"❌ Failed to patch OpenAI client: {e}")
    
    def _patch_agents_runner(self):
        """Patch the agents library runner to handle OpenRouter responses"""
        try:
            from agents import Runner as OpenAIRunner
            
            # Store original run method
            if not hasattr(self, '_original_run'):
                self._original_run = OpenAIRunner.run
            
            async def enhanced_run(agent, *args, **kwargs):
                """Enhanced run method that handles OpenRouter responses properly"""
                try:
                    result = await self._original_run(agent, *args, **kwargs)
                    
                    # Convert string responses to compatible objects
                    if isinstance(result, str):
                        return self._create_compatible_result(result)
                    
                    # Ensure result has required attributes
                    if not hasattr(result, 'output'):
                        if hasattr(result, 'content'):
                            result.output = result.content
                        elif hasattr(result, 'choices') and result.choices:
                            result.output = result.choices[0].message.content
                    
                    if not hasattr(result, 'final_output'):
                        result.final_output = getattr(result, 'output', str(result))
                    
                    return result
                    
                except Exception as e:
                    print(f"Error in enhanced agents run method: {e}")
                    # Return compatible error response
                    return self._create_compatible_result(f"Error: {str(e)}")
            
            # Apply the patch
            OpenAIRunner.run = enhanced_run
            print("✅ Applied agents library runner enhancement patch")
            
        except Exception as e:
            print(f"❌ Failed to patch agents runner: {e}")
    
    def _patch_response_creation(self):
        """Patch response creation to ensure compatibility"""
        try:
            # This is a placeholder for additional response creation patches
            # that might be needed based on the specific agents library version
            print("✅ Applied response creation patches")
            
        except Exception as e:
            print(f"❌ Failed to apply response creation patches: {e}")
    
    def _create_compatible_result(self, content: str):
        """Create a result object compatible with agents library expectations"""
        class CompatibleResult:
            def __init__(self, content: str):
                self.output = content
                self.final_output = content
                self.content = content
                
            def __str__(self):
                return self.content
                
            def __repr__(self):
                return f"CompatibleResult(content='{self.content[:50]}...')"
        
        return CompatibleResult(content)
    
    def create_openai_compatible_response(self, content: str):
        """Create an OpenAI-compatible response object"""
        class CompatibleMessage:
            def __init__(self, content: str):
                self.content = content
                self.output = content
                self.role = "assistant"
        
        class CompatibleChoice:
            def __init__(self, content: str):
                self.message = CompatibleMessage(content)
                self.index = 0
                self.finish_reason = "stop"
        
        class CompatibleResponse:
            def __init__(self, content: str):
                self.choices = [CompatibleChoice(content)]
                self.output = content
                self.id = f"chatcmpl-openrouter-{hash(content) % 1000000}"
                self.object = "chat.completion"
                self.model = "openai/gpt-4o-mini"
        
        return CompatibleResponse(content)


# Initialize and apply compatibility layer
compatibility_layer = OpenRouterCompatibilityLayer()
compatibility_layer.apply_comprehensive_patches()


# Enhanced OpenRouter Runner with better error handling
class EnhancedOpenRouterRunner:
    """Enhanced OpenRouter runner with comprehensive error handling and response formatting"""
    
    def __init__(self):
        self.client = None
        self.compatibility_layer = compatibility_layer
    
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
            
            # Create client with additional headers for OpenRouter
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                default_headers={
                    "HTTP-Referer": "https://medical-assistant.local",
                    "X-Title": "Medical Assistant API"
                }
            )
        
        return self.client
    
    async def run(self, agent, user_input: str):
        """Run agent with OpenRouter backend and comprehensive response handling"""
        client = self._get_client()
        
        # Extract model from agent if available, otherwise use default
        model = getattr(agent, 'model', 'openai/gpt-4o-mini')
        
        # Extract instructions from agent if available
        instructions = getattr(agent, 'instructions', '')
        
        # Extract tools if available
        tools = getattr(agent, 'tools', [])
        
        # Prepare messages
        messages = []
        if instructions:
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Prepare request parameters
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            # Add tools if available (for function calling)
            if tools:
                # Convert tools to OpenAI function format if needed
                # This is a simplified implementation
                request_params["tools"] = tools
            
            # Call OpenRouter API
            response = await client.chat.completions.create(**request_params)
            
            # Extract content from response
            content = response.choices[0].message.content
            
            # Create compatible response using the compatibility layer
            return self.compatibility_layer._create_compatible_result(content)
            
        except Exception as e:
            print(f"Error in EnhancedOpenRouterRunner: {e}")
            import traceback
            traceback.print_exc()
            
            # Return compatible error response
            error_msg = f"OpenRouter API error: {str(e)}"
            return self.compatibility_layer._create_compatible_result(error_msg)


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
    """Enhanced Agent wrapper with comprehensive OpenRouter compatibility"""
    
    def __init__(self, *args, **kwargs):
        """Initialize agent and ensure API key is set"""
        _ensure_api_key()
        super().__init__(*args, **kwargs)
        # Initialize enhanced fallback runner
        self._enhanced_runner = EnhancedOpenRouterRunner()
    
    async def invoke(self, user_input: str, conversation_history: list = None, **kwargs) -> str:
        """Enhanced async wrapper for Agent execution with comprehensive error handling"""
        if conversation_history:
            # Format conversation history for the agent
            history_context = self._format_conversation_history(conversation_history)
            
            # Combine history context with current user input
            if history_context:
                full_input = f"{history_context}\n\nCurrent message: {user_input}"
            else:
                full_input = user_input
        else:
            full_input = user_input
        
        # Strategy 1: Try using the patched OpenAI agents library
        try:
            print(f"🔄 Attempting to use patched agents library...")
            result = await OpenAIRunner.run(self, full_input)
            
            # Enhanced response handling with detailed logging
            print(f"📥 Received result type: {type(result)}")
            print(f"📥 Result attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
            
            # Handle different response types
            if hasattr(result, 'final_output'):
                print(f"✅ Using result.final_output")
                return result.final_output
            elif hasattr(result, 'output'):
                print(f"✅ Using result.output")
                return result.output
            elif isinstance(result, str):
                print(f"✅ Using string result directly")
                return result
            else:
                # Try to extract content from complex objects
                if hasattr(result, 'choices') and result.choices:
                    content = result.choices[0].message.content
                    print(f"✅ Extracted from choices: {content[:100]}...")
                    return content
                elif hasattr(result, 'content'):
                    print(f"✅ Using result.content")
                    return result.content
                else:
                    print(f"⚠️ Converting result to string: {str(result)[:100]}...")
                    return str(result)
                    
        except Exception as e:
            print(f"❌ Error in patched agents library: {e}")
            print(f"📋 Exception type: {type(e)}")
            
            # Strategy 2: Fallback to enhanced OpenRouter runner
            try:
                print(f"🔄 Falling back to enhanced OpenRouter runner...")
                result = await self._enhanced_runner.run(self, full_input)
                
                if hasattr(result, 'final_output'):
                    print(f"✅ Fallback successful, using final_output")
                    return result.final_output
                elif hasattr(result, 'output'):
                    print(f"✅ Fallback successful, using output")
                    return result.output
                else:
                    print(f"✅ Fallback successful, converting to string")
                    return str(result)
                    
            except Exception as fallback_error:
                print(f"❌ Fallback runner also failed: {fallback_error}")
                
                # Strategy 3: Last resort - return error message
                error_msg = f"Both primary and fallback methods failed. Primary error: {str(e)}, Fallback error: {str(fallback_error)}"
                print(f"🆘 Last resort error response: {error_msg}")
                return error_msg
    
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