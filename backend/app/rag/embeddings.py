"""
InvestiLens — HuggingFace Embedding Integration

Uses BAAI/bge-base-en-v1.5 (or configurable alternative) via LangChain.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import get_settings
from app.core.logging import logger

_embeddings_instance = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Return a cached HuggingFace embeddings instance.
    Uses the model specified in configuration.
    """
    global _embeddings_instance

    if _embeddings_instance is None:
        settings = get_settings()
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")

        _embeddings_instance = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        logger.info("Embedding model loaded successfully")

    return _embeddings_instance
