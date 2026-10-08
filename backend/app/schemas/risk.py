"""
InvestiLens — Risk Analysis Schemas

Structured risk intelligence output models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class RiskItem(BaseModel):
    """A single identified risk with evidence."""

    risk: str = Field(description="Short risk description")
    category: str = Field(
        description="Risk category: Financial, Business, Market, Operational, Regulatory, Strategic, Competitive"
    )
    severity: str = Field(description="Low, Medium, High, Critical")
    explanation: Optional[str] = Field(None, description="Detailed explanation of the risk")
    potential_impact: Optional[str] = Field(None, description="How the risk could affect the company")
    evidence: Optional[str] = Field(None, description="Supporting text from documents")
    source: Optional[str] = Field(None, description="Source document name")
    page: Optional[int] = Field(None, description="Page number")
    confidence: str = Field("Medium", description="Evidence quality: High, Medium, Low")


class RiskAnalysis(BaseModel):
    """Complete risk analysis output."""

    company: str
    risks: List[RiskItem] = Field(default_factory=list)
    summary: Optional[str] = None
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    critical_risk_count: int = 0

    def compute_counts(self):
        """Compute risk severity counts from the risks list."""
        self.critical_risk_count = sum(1 for r in self.risks if r.severity == "Critical")
        self.high_risk_count = sum(1 for r in self.risks if r.severity == "High")
        self.medium_risk_count = sum(1 for r in self.risks if r.severity == "Medium")
        self.low_risk_count = sum(1 for r in self.risks if r.severity == "Low")
        return self
