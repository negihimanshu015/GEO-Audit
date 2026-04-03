from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List, Union
import os

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and .env file.
    """
    
    GEMINI_API_KEY: str = Field(default="", min_length=1)
    
    ALLOWED_ORIGINS: Union[List[str], str] = Field(default_factory=list)
    APP_PORT: int = Field(default=8000, ge=1024, le=65535)
    RATE_LIMIT: str = Field(default="10 per minute")

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip().rstrip("/") for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(i).rstrip("/") for i in v]
        return v
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        env_parse_list_separator=","
    )

@lru_cache()
def get_settings():
    """
    Returns a cached instance of the settings.
    """
    return Settings()