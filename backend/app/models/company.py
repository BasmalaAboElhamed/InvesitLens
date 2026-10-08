"""
InvestiLens — Company Model

Represents a company workspace in the system.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class Company(BaseModel):
    """Company workspace model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    industry: Optional[str] = None
    ticker: Optional[str] = None
    country: Optional[str] = None
    analysis_period: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    document_count: int = 0
    analysis_count: int = 0


class CompanyCreate(BaseModel):
    """Schema for creating a new company workspace."""

    name: str
    industry: Optional[str] = None
    ticker: Optional[str] = None
    country: Optional[str] = None
    analysis_period: Optional[str] = None


class CompanySummary(BaseModel):
    """Lightweight company summary for dashboard lists."""

    id: str
    name: str
    industry: Optional[str] = None
    ticker: Optional[str] = None
    document_count: int = 0
    analysis_count: int = 0
    high_risk_count: int = 0
    latest_analysis: Optional[str] = None
