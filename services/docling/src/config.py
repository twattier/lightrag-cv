"""Configuration management via environment variables."""

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
    MAX_FILE_SIZE_MB: int = 50  # Maximum file size for document uploads

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
