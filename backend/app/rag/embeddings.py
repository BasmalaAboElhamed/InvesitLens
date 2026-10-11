"""
InvestiLens — HuggingFace Embedding Integration

Uses BAAI/bge-base-en-v1.5 (or configurable alternative) via LangChain.
"""

import threading

from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import get_settings
from app.core.logging import logger

# Loaded lazily on first use, then reused (loading the model is slow)
_embeddings_instance = None
_embeddings_lock = threading.Lock()


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Return a cached HuggingFace embeddings instance.
    Uses the model specified in configuration.
    """
    global _embeddings_instance

    if _embeddings_instance is None:
        # The lock makes sure the model is loaded only once even if two
        # worker threads (e.g. chat + analysis) ask for it at the same time.
        with _embeddings_lock:
            if _embeddings_instance is None:
                settings = get_settings()
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")

                _embeddings_instance = HuggingFaceEmbeddings(
                    model_name=settings.EMBEDDING_MODEL,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},  # unit vectors -> cosine similarity
                )

                logger.info("Embedding model loaded successfully")

    return _embeddings_instance
