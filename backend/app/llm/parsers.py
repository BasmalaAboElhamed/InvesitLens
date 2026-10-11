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

# Marker meaning "this text is not valid JSON" (None can't be used, because
# the JSON text "null" is valid and parses to None).
_NOT_JSON = object()

# ```json ... ```  (the "json" label is optional)
CODE_BLOCK_PATTERN = r'```(?:json)?\s*\n?(.*?)\n?```'
# Everything from the first "{" to the last "}"
JSON_OBJECT_PATTERN = r'\{.*\}'


def _try_json_loads(text: str):
    """Parse `text` as JSON, returning _NOT_JSON if it is invalid."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _NOT_JSON


def extract_json_from_response(text: str) -> Optional[dict]:
    """
    Extract JSON object from LLM response text.
    Handles responses that include markdown code blocks or extra text.

    Tries three strategies, in order:
        1. The whole response is JSON
        2. The JSON is inside a ```json code block
        3. The JSON is the part between the first "{" and the last "}"
    """
    if not text:
        return None

    # Strategy 1: the whole response is JSON
    parsed = _try_json_loads(text.strip())
    if parsed is not _NOT_JSON:
        return parsed

    # Strategy 2: JSON inside a markdown code block
    code_block_match = re.search(CODE_BLOCK_PATTERN, text, re.DOTALL)
    if code_block_match:
        parsed = _try_json_loads(code_block_match.group(1).strip())
        if parsed is not _NOT_JSON:
            return parsed

    # Strategy 3: JSON object embedded in surrounding text
    brace_match = re.search(JSON_OBJECT_PATTERN, text, re.DOTALL)
    if brace_match:
        parsed = _try_json_loads(brace_match.group(0))
        if parsed is not _NOT_JSON:
            return parsed

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
        return None


def parse_response_or_default(text: str, model_class: Type[T], **defaults) -> T:
    """
    Parse LLM response or return a default instance
    built from `defaults` (e.g. company name).
    """
    result = parse_response(text, model_class)
    if result is not None:
        return result

    logger.warning(f"Using default instance for {model_class.__name__}")
    return model_class(**defaults)
