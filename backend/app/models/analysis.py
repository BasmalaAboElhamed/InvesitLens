"""
InvestiLens — Analysis State Model

Tracks the state and results of an analysis run.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum
import uuid


class AnalysisStatus(str, Enum):
    """Analysis pipeline states."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    INDEXING = "indexing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class Analysis(BaseModel):
    """Represents a full analysis run for a company."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    company_name: str
    status: AnalysisStatus = AnalysisStatus.UPLOADING
    progress: int = 0  # 0-100
    current_step: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    # Analysis results stored as JSON-serializable dicts
    company_analysis: Optional[Dict[str, Any]] = None
    financial_analysis: Optional[Dict[str, Any]] = None
    trend_analysis: Optional[Dict[str, Any]] = None
    risk_analysis: Optional[Dict[str, Any]] = None
    strategy_analysis: Optional[Dict[str, Any]] = None
    management_outlook: Optional[Dict[str, Any]] = None
    comparison_analysis: Optional[Dict[str, Any]] = None
    report: Optional[Dict[str, Any]] = None
