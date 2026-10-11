"""
InvestiLens — LLM Model Setup

Configures Ollama LLM via LangChain with configurable model selection.
"""

import threading

from langchain_ollama import ChatOllama
from app.core.config import get_settings
from app.core.logging import logger

# Generation settings (the model name and URL come from config)
LLM_TEMPERATURE = 0.1       # low = consistent, factual output
LLM_MAX_OUTPUT_TOKENS = 4096  # maximum tokens the model may generate per call

# Created lazily on first use, then reused by every chain
_llm_instance = None
_llm_lock = threading.Lock()


def get_llm() -> ChatOllama:
    """Return a cached ChatOllama instance."""
    global _llm_instance

    if _llm_instance is None:
        # Lock: only one thread creates the instance (calls can now run in worker threads)
        with _llm_lock:
            if _llm_instance is None:
                settings = get_settings()
                logger.info(f"Initializing Ollama LLM: {settings.LLM_MODEL} at {settings.LLM_BASE_URL}")

                _llm_instance = ChatOllama(
                    model=settings.LLM_MODEL,
                    base_url=settings.LLM_BASE_URL,
                    temperature=LLM_TEMPERATURE,
                    num_predict=LLM_MAX_OUTPUT_TOKENS,
                )

                logger.info("Ollama LLM initialized successfully")

    return _llm_instance
