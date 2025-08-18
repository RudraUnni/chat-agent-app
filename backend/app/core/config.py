"""
Simple application configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Chat Agent API"
    debug: bool = False
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
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