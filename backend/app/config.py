from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List
import os

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and .env file.
    """
    
    GEMINI_API_KEY: str = Field(default="", min_length=1)
    
    ALLOWED_ORIGINS: List[str] = Field(default_factory=list)
    APP_PORT: int = Field(default=8000, ge=1024, le=65535)
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings():
    """
    Returns a cached instance of the settings.
    """
    return Settings()