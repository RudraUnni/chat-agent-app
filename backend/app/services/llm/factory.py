from typing import Optional
from app.services.llm.base import BaseLLMProvider
from app.core.config import settings


class LLMFactory:
    """Factory for creating LLM provider instances"""
    
    @staticmethod
    def create(provider: str, api_key: Optional[str] = None) -> BaseLLMProvider:
        """Create an LLM provider instance"""
        
        if provider == "openai":
            from app.services.llm.openai import OpenAIProvider
            key = api_key or settings.openai_api_key
            if not key:
                raise ValueError("OpenAI API key not provided")
            return OpenAIProvider(key, settings.default_llm_model)
        
        elif provider == "anthropic":
            from app.services.llm.anthropic import AnthropicProvider
            key = api_key or settings.anthropic_api_key
            if not key:
                raise ValueError("Anthropic API key not provided")
            return AnthropicProvider(key)
        
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    @staticmethod
    def get_available_providers():
        """Get list of available providers based on configured API keys"""
        providers = []
        if settings.openai_api_key:
            providers.append("openai")
        if settings.anthropic_api_key:
            providers.append("anthropic")
        return providers