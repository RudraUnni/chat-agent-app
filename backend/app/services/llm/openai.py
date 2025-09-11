# OpenAI Provider - COMMENTED OUT FOR OPENROUTER MIGRATION
# This file is kept for reference but all functionality is disabled

from typing import AsyncGenerator, List, Optional
# import openai
# from openai import AsyncOpenAI
from app.services.llm.base import BaseLLMProvider, LLMResponse, Message


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation - DISABLED FOR OPENROUTER MIGRATION"""
    
    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini"):
        # super().__init__(api_key, default_model)
        # self.client = AsyncOpenAI(api_key=api_key)
        raise NotImplementedError("OpenAI provider is disabled. Use OpenRouter provider instead.")
    
    async def generate(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a single response from OpenAI - DISABLED"""
        # try:
        #     response = await self.client.chat.completions.create(
        #         model=model or self.default_model,
        #         messages=self.format_messages(messages),
        #         temperature=temperature,
        #         max_tokens=max_tokens,
        #         **kwargs
        #     )
        #     
        #     return LLMResponse(
        #         content=response.choices[0].message.content,
        #         model=response.model,
        #         usage={
        #             "prompt_tokens": response.usage.prompt_tokens,
        #             "completion_tokens": response.usage.completion_tokens,
        #             "total_tokens": response.usage.total_tokens
        #         } if response.usage else None
        #     )
        # except Exception as e:
        #     raise Exception(f"OpenAI API error: {str(e)}")
        raise NotImplementedError("OpenAI provider is disabled. Use OpenRouter provider instead.")
    
    async def stream(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from OpenAI - DISABLED"""
        # try:
        #     stream = await self.client.chat.completions.create(
        #         model=model or self.default_model,
        #         messages=self.format_messages(messages),
        #         temperature=temperature,
        #         max_tokens=max_tokens,
        #         stream=True,
        #         **kwargs
        #     )
        #     
        #     async for chunk in stream:
        #         if chunk.choices[0].delta.content:
        #             yield chunk.choices[0].delta.content
        # except Exception as e:
        #     raise Exception(f"OpenAI streaming error: {str(e)}")
        raise NotImplementedError("OpenAI provider is disabled. Use OpenRouter provider instead.")