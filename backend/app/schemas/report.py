"""
InvestiLens — Intelligence Report Schema

The final synthesized intelligence report combining all analyses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class ReportEvidence(BaseModel):
    """Evidence item in the final report."""

    claim: str
    document: str
    page: Optional[int] = None
    section: Optional[str] = None
    text: Optional[str] = None


class IntelligenceReport(BaseModel):
    """Final synthesized intelligence report for a company."""

    company: str
    period: Optional[str] = None
    generated_at: Optional[str] = None

    executive_summary: Optional[str] = None
    company_overview: Optional[str] = None
    business_model: Optional[str] = None
    products_and_services: Optional[str] = None
    market_presence: Optional[str] = None

    financial_performance: Optional[str] = None
    financial_insights: List[Dict[str, Any]] = Field(default_factory=list)
    performance_trends: List[Dict[str, Any]] = Field(default_factory=list)

    positive_indicators: List[str] = Field(default_factory=list)
    warning_indicators: List[str] = Field(default_factory=list)

    key_risks: List[Dict[str, Any]] = Field(default_factory=list)
    strategic_outlook: List[Dict[str, Any]] = Field(default_factory=list)
    management_outlook: Optional[str] = None

    cross_year_comparison: Optional[Dict[str, Any]] = None
    evidence: List[ReportEvidence] = Field(default_factory=list)

    overall_summary: Optional[str] = None
    disclaimer: str = (
        "InvestiLens provides document-based research and decision-support insights. "
        "It does not provide personalized financial advice, investment recommendations, "
        "or guarantees of future performance."
    )
