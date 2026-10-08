"""
InvestiLens — Cross-Document Comparison Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class ComparisonItem(BaseModel):
    """A single comparison point across years/documents."""

    area: str = Field(description="Area being compared, e.g. Revenue, Debt")
    values: List[str] = Field(default_factory=list, description="Values per period")
    periods: List[str] = Field(default_factory=list, description="Period labels")
    trend: Optional[str] = Field(None, description="Positive, Negative, Stable, Mixed")
    interpretation: Optional[str] = None
    evidence: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    confidence: str = "Medium"


class CrossYearComparison(BaseModel):
    """Full cross-year comparison analysis."""

    company: str
    periods_compared: List[str] = Field(default_factory=list)
    comparisons: List[ComparisonItem] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    declines: List[str] = Field(default_factory=list)
    new_risks: List[str] = Field(default_factory=list)
    removed_risks: List[str] = Field(default_factory=list)
    stable_areas: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
