"""Configuration management via environment variables."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    LOG_LEVEL: str = "INFO"
    SERVICE_NAME: str = "docling-service"

    # Docling Configuration
    GPU_ENABLED: bool = False
    MAX_CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
