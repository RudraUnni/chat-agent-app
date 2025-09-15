"""
Clean OpenRouter client wrapper with health checks and response formatting.
"""
import os
import asyncio
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import httpx
import logging

logger = logging.getLogger(__name__)


class OpenRouterResponse:
    """Compatible response wrapper for agents library"""
    
    def __init__(self, content: str, model: str = None, usage: Dict = None):
        self.content = content
        self.output = content  # For agents library compatibility
        self.final_output = content  # For agents library compatibility
        self.model = model
        self.usage = usage or {}
        
    def __str__(self):
        return self.content
        
    def __repr__(self):
        return f"OpenRouterResponse(content='{self.content[:50]}...')"


class OpenRouterClient:
    """Clean OpenRouter client with health checks and response formatting"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
            
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": "https://medical-assistant.local",
                "X-Title": "Medical Assistant API"
            }
        )
        
        # Set OpenAI environment variables for agents library compatibility
        os.environ["OPENAI_API_KEY"] = self.api_key
        os.environ["OPENAI_BASE_URL"] = self.base_url
        
        logger.info(f"OpenRouter client initialized: {self.base_url}")
    
    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> OpenRouterResponse:
        """Create a chat completion with OpenRouter"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
            
            return OpenRouterResponse(content=content, model=response.model, usage=usage)
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise Exception(f"OpenRouter API error: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenRouter API connectivity and key validity"""
        try:
            # Test with a minimal request
            response = await self.client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            
            return {
                "status": "healthy",
                "api_key_valid": True,
                "base_url": self.base_url,
                "model_tested": "openai/gpt-4o-mini"
            }
            
        except Exception as e:
            logger.error(f"OpenRouter health check failed: {e}")
            return {
                "status": "unhealthy",
                "api_key_valid": False,
                "base_url": self.base_url,
                "error": str(e)
            }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from OpenRouter"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []


# Global client instance
_client: Optional[OpenRouterClient] = None


def get_openrouter_client() -> OpenRouterClient:
    """Get or create the global OpenRouter client"""
    global _client
    if _client is None:
        _client = OpenRouterClient()
    return _client


async def create_response(messages: List[Dict[str, str]], **kwargs) -> OpenRouterResponse:
    """Convenience function for creating responses"""
    client = get_openrouter_client()
    return await client.create_completion(messages, **kwargs)