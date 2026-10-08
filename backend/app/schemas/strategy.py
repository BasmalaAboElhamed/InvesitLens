"""
InvestiLens — Strategy Analysis Schemas

Structured strategic intelligence output models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class StrategyItem(BaseModel):
    """A single strategic priority or initiative."""

    priority: str = Field(description="Strategic priority or initiative name")
    category: Optional[str] = Field(
        None,
        description="Category: Market expansion, Product development, R&D, Acquisitions, Partnerships, Cost optimization, Geographic expansion, Infrastructure investment, Digital transformation"
    )
    description: Optional[str] = Field(None, description="Detailed description")
    expected_impact: Optional[str] = Field(None, description="Expected business impact")
    evidence: Optional[str] = Field(None, description="Supporting text from documents")
    source: Optional[str] = Field(None, description="Source document name")
    page: Optional[int] = Field(None, description="Page number")
    confidence: str = Field("Medium", description="Evidence quality: High, Medium, Low")


class StrategyAnalysis(BaseModel):
    """Complete strategy analysis output."""

    company: str
    strategies: List[StrategyItem] = Field(default_factory=list)
    summary: Optional[str] = None


class ManagementOutlook(BaseModel):
    """Management outlook analysis."""

    company: str
    outlook_summary: Optional[str] = None
    growth_expectations: Optional[str] = None
    expected_challenges: Optional[str] = None
    strategic_priorities: Optional[str] = None
    market_outlook: Optional[str] = None
    investment_plans: Optional[str] = None
    risk_awareness: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    confidence: str = "Medium"
