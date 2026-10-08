"""
InvestiLens — Companies API
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.company import Company, CompanyCreate, CompanySummary
from app.services import db_service

router = APIRouter()


@router.get("/", response_model=List[CompanySummary])
def get_companies():
    """Get all company workspaces."""
    return db_service.get_companies()


@router.post("/", response_model=Company)
def create_company(company_in: CompanyCreate):
    """Create a new company workspace."""
    company = Company(
        name=company_in.name,
        industry=company_in.industry,
        ticker=company_in.ticker,
        country=company_in.country,
        analysis_period=company_in.analysis_period
    )
    return db_service.create_company(company)


@router.get("/{company_id}", response_model=Company)
def get_company(company_id: str):
    """Get a specific company workspace."""
    company = db_service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: str):
    """Delete a company workspace."""
    if not db_service.delete_company(company_id):
        raise HTTPException(status_code=404, detail="Company not found")
