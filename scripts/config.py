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

    # Ollama configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL: str = os.getenv("OLLAMA_LLM_MODEL", "qwen2.5:7b-instruct-q4_K_M")
    OLLAMA_HOST_PORT: int = int(os.getenv("OLLAMA_HOST_PORT", "11434"))
    LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "1200"))

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
