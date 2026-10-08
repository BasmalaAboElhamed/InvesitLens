"""
InvestiLens — Output Parsers

Parses LLM JSON responses into validated Pydantic models.
Handles malformed output gracefully.
"""

import json
import re
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


def extract_json_from_response(text: str) -> Optional[dict]:
    """
    Extract JSON object from LLM response text.
    Handles responses that include markdown code blocks or extra text.
    """
    if not text:
        return None

    # Try direct JSON parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to extract from markdown code block
    code_block_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try to find JSON object in the text
    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    logger.warning(f"Failed to extract JSON from response: {text[:200]}...")
    return None


def parse_response(text: str, model_class: Type[T]) -> Optional[T]:
    """
    Parse LLM response text into a Pydantic model.

    Args:
        text: Raw LLM response string
        model_class: Target Pydantic model class

    Returns:
        Validated Pydantic model instance or None
    """
    data = extract_json_from_response(text)

    if data is None:
        logger.error(f"Could not extract JSON for {model_class.__name__}")
        return None

    try:
        instance = model_class.model_validate(data)
        logger.info(f"Successfully parsed response into {model_class.__name__}")
        return instance
    except Exception as e:
        logger.error(f"Validation error for {model_class.__name__}: {e}")
        # Try partial parse - fill in what we can
        try:
            instance = model_class.model_validate(data)
            return instance
        except Exception:
            return None


def parse_response_or_default(text: str, model_class: Type[T], **defaults) -> T:
    """
    Parse LLM response or return a default instance.
    """
    result = parse_response(text, model_class)
    if result is not None:
        return result

    logger.warning(f"Using default instance for {model_class.__name__}")
    return model_class(**defaults)
