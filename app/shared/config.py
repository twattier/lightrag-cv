"""
Centralized configuration for ingestion scripts.

This module provides a single source of truth for environment variables
and configuration settings, following RULE 2: All Environment Variables via config.py
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Centralized configuration settings for ingestion scripts."""

    # PostgreSQL configuration
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5434"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "lightrag_cv")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "lightrag")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "lightrag_dev_2024")

    # LightRAG configuration
    LIGHTRAG_HOST: str = os.getenv("LIGHTRAG_HOST", "localhost")
    LIGHTRAG_PORT: int = int(os.getenv("LIGHTRAG_PORT", "9621"))

    # LLM Provider Configuration (unified multi-provider support)
    LLM_BINDING: str = os.getenv("LLM_BINDING", "ollama")  # Options: ollama, openai, litellm
    LLM_BINDING_HOST: str = os.getenv("LLM_BINDING_HOST", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct-q4_K_M")
    LLM_BINDING_API_KEY: Optional[str] = os.getenv("LLM_BINDING_API_KEY")  # Required for openai/litellm
    LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "1200"))

    # Embedding Provider Configuration
    EMBEDDING_BINDING: str = os.getenv("EMBEDDING_BINDING", "ollama")
    EMBEDDING_BINDING_HOST: str = os.getenv("EMBEDDING_BINDING_HOST", "http://localhost:11434")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "bge-m3:latest")
    EMBEDDING_BINDING_API_KEY: Optional[str] = os.getenv("EMBEDDING_BINDING_API_KEY")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "1024"))  # bge-m3 default
    EMBEDDING_TIMEOUT: float = float(os.getenv("EMBEDDING_TIMEOUT", "600"))

    # Data paths
    DATA_DIR: Path = Path("/home/wsluser/dev/lightrag-cv/data")
    CIGREF_DIR: Path = DATA_DIR / "cigref"
    CIGREF_PARSED_FILE: Path = CIGREF_DIR / "cigref-parsed.json"

    # Processing configuration
    INGESTION_TIMEOUT: float = 600.0  # 10 minutes
    STATUS_POLL_INTERVAL: int = 10  # seconds
    STATUS_MAX_ATTEMPTS: int = 60  # 10 minutes total

    # Batch processing configuration
    DEFAULT_BATCH_SIZE: int = 85  # chunks per batch
    MAX_RETRIES: int = 3

    @property
    def postgres_dsn(self) -> str:
        """PostgreSQL connection string."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def lightrag_url(self) -> str:
        """LightRAG service base URL."""
        return f"http://{self.LIGHTRAG_HOST}:{self.LIGHTRAG_PORT}"


# Global settings instance
settings = Settings()
