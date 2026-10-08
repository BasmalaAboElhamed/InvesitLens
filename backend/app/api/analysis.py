"""
InvestiLens — Analysis API
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional

from app.models.analysis import Analysis, AnalysisStatus
from app.services import db_service
from app.services import analysis_orchestrator

router = APIRouter()


@router.get("/company/{company_id}", response_model=List[Analysis])
def get_company_analyses(company_id: str):
    """Get all analysis runs for a company."""
    company = db_service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    return db_service.get_analyses_for_company(company_id)


@router.get("/{analysis_id}", response_model=Analysis)
def get_analysis(analysis_id: str):
    """Get a specific analysis run."""
    analysis = db_service.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@router.post("/start", response_model=Analysis)
async def start_analysis(
    background_tasks: BackgroundTasks,
    company_id: str = Query(...),
    years: Optional[List[int]] = Query(None)
):
    """Start a new analysis pipeline run."""
    company = db_service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    # Check if documents exist
    docs = db_service.get_documents_for_company(company_id)
    if not docs:
        raise HTTPException(status_code=400, detail="Company has no uploaded documents to analyze")
        
    # Create analysis record
    analysis = Analysis(
        company_id=company.id,
        company_name=company.name,
        status=AnalysisStatus.PROCESSING,
        current_step="Initializing..."
    )
    analysis = db_service.create_analysis(analysis)
    
    # Start pipeline in background
    background_tasks.add_task(
        analysis_orchestrator.run_analysis_pipeline,
        analysis_id=analysis.id,
        company_name=company.name,
        years=years
    )
    
    return analysis
