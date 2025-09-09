from typing import AsyncGenerator, List, Optional
import openai
from openai import AsyncOpenAI
from app.services.llm.base import BaseLLMProvider, LLMResponse, Message


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter LLM provider implementation"""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", default_model: str = "openai/gpt-4o-mini"):
        super().__init__(api_key, default_model)
        self.base_url = base_url
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    async def generate(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a single response from OpenRouter"""
        try:
            # Add OpenRouter-specific headers if provided
            extra_headers = {}
            if "http_referer" in kwargs:
                extra_headers["HTTP-Referer"] = kwargs.pop("http_referer")
            if "x_title" in kwargs:
                extra_headers["X-Title"] = kwargs.pop("x_title")
            
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=self.format_messages(messages),
                temperature=temperature,
                max_tokens=max_tokens,
                extra_headers=extra_headers,
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            )
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")
    
    async def stream(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from OpenRouter"""
        try:
            # Add OpenRouter-specific headers if provided
            extra_headers = {}
            if "http_referer" in kwargs:
                extra_headers["HTTP-Referer"] = kwargs.pop("http_referer")
            if "x_title" in kwargs:
                extra_headers["X-Title"] = kwargs.pop("x_title")
            
            stream = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=self.format_messages(messages),
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                extra_headers=extra_headers,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"OpenRouter streaming error: {str(e)}")