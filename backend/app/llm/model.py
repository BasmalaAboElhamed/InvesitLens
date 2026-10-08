"""
InvestiLens — LLM Model Setup

Configures Ollama LLM via LangChain with configurable model selection.
"""

from langchain_ollama import ChatOllama
from app.core.config import get_settings
from app.core.logging import logger

_llm_instance = None


def get_llm() -> ChatOllama:
    """Return a cached ChatOllama instance."""
    global _llm_instance

    if _llm_instance is None:
        settings = get_settings()
        logger.info(f"Initializing Ollama LLM: {settings.LLM_MODEL} at {settings.LLM_BASE_URL}")

        _llm_instance = ChatOllama(
            model=settings.LLM_MODEL,
            base_url=settings.LLM_BASE_URL,
            temperature=0.1,
            num_predict=4096,
        )

        logger.info("Ollama LLM initialized successfully")

    return _llm_instance
