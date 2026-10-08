"""
InvestiLens — Application Configuration

Centralized configuration using Pydantic Settings.
All values are loaded from environment variables or .env file.
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "qwen2.5:7b"
    LLM_BASE_URL: str = "http://localhost:11434"

    # Embedding Model
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"

    # RAG Configuration
    TOP_K: int = 5
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 120

    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Document Storage
    DOCUMENT_DIRECTORY: str = "./data/documents"

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def chroma_path(self) -> Path:
        return Path(self.CHROMA_PERSIST_DIRECTORY)

    @property
    def documents_path(self) -> Path:
        return Path(self.DOCUMENT_DIRECTORY)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
