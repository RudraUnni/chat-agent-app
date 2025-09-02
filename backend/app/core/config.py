"""
Simple application configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import field_validator
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Medical Assistant API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: str = '["http://localhost:3000", "http://localhost:5173"]'
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    
    # Database
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "chatapp_db"
    database_user: str = "chatapp"
    database_password: str = "chatapp_password"
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    default_llm_model: str = "gpt-4o-mini"
    default_llm_provider: str = "openai"
    
    # PubMed Configuration
    pubmed_max_results: int = 5
    pubmed_timeout: int = 15
    
    # Additional environment variables that might be passed from Docker
    environment: Optional[str] = None
    api_host: Optional[str] = None
    api_port: Optional[str] = None
    session_expire_hours: Optional[str] = None
    redis_host: Optional[str] = None
    redis_port: Optional[str] = None
    
    @field_validator('pubmed_timeout', mode='before')
    @classmethod
    def parse_pubmed_timeout(cls, v):
        """Parse pubmed_timeout, handling common formatting issues"""
        if isinstance(v, str):
            # Remove trailing dots and convert to int
            v = v.rstrip('.')
            return int(float(v))
        return v
    
    model_config = {
        "env_file": [".env", "../.env", "../../.env"],
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra environment variables
    }
        
    @property
    def async_database_url(self) -> str:
        """Get async database URL for SQLAlchemy"""
        return f"postgresql+asyncpg://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

settings = get_settings()
    

