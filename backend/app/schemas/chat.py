"""
InvestiLens — Chat Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class EvidenceSource(BaseModel):
    """A single evidence citation from a document."""

    document: str
    page: Optional[int] = None
    section: Optional[str] = None
    text: Optional[str] = None


class ChatRequest(BaseModel):
    """Incoming chat request from the user."""

    company_id: str
    question: str
    filters: Optional[dict] = None
    history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    """Structured AI chat response."""

    answer: str
    evidence: List[EvidenceSource] = Field(default_factory=list)
    confidence: str = "Medium"
    intent: Optional[str] = None
    suggested_questions: List[str] = Field(default_factory=list)
