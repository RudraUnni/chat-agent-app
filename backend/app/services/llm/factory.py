from typing import Optional
from app.services.llm.base import BaseLLMProvider
from app.core.config import get_settings
from app.core.exceptions import ConfigurationError, LLMError

settings = get_settings()


class LLMFactory:
    """Factory for creating LLM provider instances"""
    
    @staticmethod
    def create(provider: str, api_key: Optional[str] = None) -> BaseLLMProvider:
        """Create an LLM provider instance"""
        
        if provider == "openai":
            from app.services.llm.openai import OpenAIProvider
            key = api_key or settings.openai_api_key
            if not key:
                raise ConfigurationError(
                    "OpenAI API key not provided",
                    error_code="MISSING_API_KEY",
                    details={"provider": provider}
                )
            try:
                return OpenAIProvider(key, settings.default_llm_model)
            except Exception as e:
                raise LLMError(
                    f"Failed to initialize OpenAI provider: {str(e)}",
                    error_code="PROVIDER_INIT_ERROR",
                    details={"provider": provider}
                )
        else:
            raise ConfigurationError(
                f"Unknown LLM provider: {provider}",
                error_code="UNKNOWN_PROVIDER",
                details={"provider": provider, "available_providers": LLMFactory.get_available_providers()}
            )
    
    @staticmethod
    def get_available_providers():
        """Get list of available providers based on configured API keys"""
        providers = []
        if settings.openai_api_key:
            providers.append("openai")
        return providers