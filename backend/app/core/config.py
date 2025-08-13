from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "Chat Agent API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    default_llm_model: str = "gpt-4o-mini"
    
    # API Configuration
    api_prefix: str = "/api/v1"
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # seconds
    
    # PubMed API
    pubmed_max_results: int = 5
    pubmed_timeout: int = 15
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


settings = Settings()