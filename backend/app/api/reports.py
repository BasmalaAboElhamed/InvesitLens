"""
InvestiLens — Reports API
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.schemas.report import IntelligenceReport
from app.services import db_service

router = APIRouter()


@router.get("/{analysis_id}", response_model=IntelligenceReport)
def get_report(analysis_id: str):
    """
    Get the synthesized intelligence report for a completed analysis.
    """
    analysis = db_service.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    if analysis.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Report not available. Analysis status is: {analysis.status}"
        )
        
    if not analysis.report:
        raise HTTPException(status_code=404, detail="Report generation failed or is missing")
        
    # We parse the dict back into the Pydantic model for validation
    try:
        report = IntelligenceReport.model_validate(analysis.report)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate report: {e}")
