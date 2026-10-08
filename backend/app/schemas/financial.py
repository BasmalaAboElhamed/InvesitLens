"""
InvestiLens — Financial Analysis Schemas

Pydantic models for structured financial intelligence output.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class FinancialInsight(BaseModel):
    """A single financial metric insight with evidence."""

    metric: str = Field(description="Financial metric name, e.g. Revenue, Net Income")
    current_value: Optional[str] = Field(None, description="Most recent reported value")
    previous_value: Optional[str] = Field(None, description="Prior period value")
    change: Optional[str] = Field(None, description="Absolute or percentage change")
    interpretation: Optional[str] = Field(None, description="What this metric change means")
    evidence: Optional[str] = Field(None, description="Relevant text from the document")
    source: Optional[str] = Field(None, description="Source document name")
    page: Optional[int] = Field(None, description="Page number in source document")
    confidence: str = Field("Medium", description="Evidence quality: High, Medium, Low")


class FinancialAnalysis(BaseModel):
    """Complete financial analysis output."""

    company: str = Field(description="Company name")
    period: Optional[str] = Field(None, description="Analysis period")
    insights: List[FinancialInsight] = Field(default_factory=list)
    summary: Optional[str] = Field(None, description="Overall financial performance summary")
    positive_indicators: List[str] = Field(default_factory=list)
    warning_indicators: List[str] = Field(default_factory=list)


class TrendItem(BaseModel):
    """A single trend observation."""

    metric: str = Field(description="Metric being tracked")
    direction: str = Field(description="Increasing, Decreasing, Stable")
    values: Optional[List[str]] = Field(None, description="Values over time periods")
    periods: Optional[List[str]] = Field(None, description="Corresponding time periods")
    interpretation: Optional[str] = None
    evidence: Optional[str] = None
    source: Optional[str] = None
    page: Optional[int] = None
    confidence: str = "Medium"


class TrendAnalysis(BaseModel):
    """Complete trend analysis output."""

    company: str
    trends: List[TrendItem] = Field(default_factory=list)
    summary: Optional[str] = None
