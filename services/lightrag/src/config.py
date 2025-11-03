"""Configuration management via environment variables."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # PostgreSQL Configuration
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "lightrag_cv"
    POSTGRES_USER: str = "lightrag"
    POSTGRES_PASSWORD: str

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    OLLAMA_LLM_MODEL: str = "qwen3:8b"
    OLLAMA_EMBEDDING_MODEL: str = "bge-m3:latest"
    OLLAMA_RERANKER_MODEL: str = "xitao/bge-reranker-v2-m3"
    OLLAMA_LLM_NUM_CTX: int = 40960

    # Service Configuration
    LOG_LEVEL: str = "INFO"
    SERVICE_NAME: str = "lightrag-service"

    # LightRAG Configuration
    LIGHTRAG_WORKING_DIR: str = "/app/data/lightrag"
    LIGHTRAG_EMBEDDING_DIM: int = 1024
    LIGHTRAG_MAX_TOKENS: int = 32768
    LIGHTRAG_TOP_K: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def postgres_dsn(self) -> str:
        """PostgreSQL connection string."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Global settings instance
settings = Settings()
