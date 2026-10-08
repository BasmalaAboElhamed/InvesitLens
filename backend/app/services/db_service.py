"""
InvestiLens — Memory Storage Service

Simple in-memory storage for MVP, mimicking a database.
Tracks companies, documents, and analysis state.
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.models.company import Company, CompanySummary
from app.models.document import Document
from app.models.analysis import Analysis, AnalysisStatus
from app.core.logging import logger

# In-memory "database"
_companies: Dict[str, Company] = {}
_documents: Dict[str, Document] = {}
_analyses: Dict[str, Analysis] = {}


# --- Company Operations ---

def get_companies() -> List[CompanySummary]:
    """Get summaries for all companies."""
    summaries = []
    for company in _companies.values():
        # Find latest analysis
        company_analyses = get_analyses_for_company(company.id)
        latest = None
        high_risk_count = 0
        
        if company_analyses:
            # Sort by completed_at or started_at
            company_analyses.sort(
                key=lambda x: x.completed_at or x.started_at, reverse=True
            )
            latest_analysis = company_analyses[0]
            if latest_analysis.status == AnalysisStatus.COMPLETED:
                latest = latest_analysis.id
                
            # Extract high risks if available
            if latest_analysis.risk_analysis:
                high_risk_count = latest_analysis.risk_analysis.get("high_risk_count", 0) + \
                                  latest_analysis.risk_analysis.get("critical_risk_count", 0)
        
        doc_count = len(get_documents_for_company(company.id))
        
        summary = CompanySummary(
            id=company.id,
            name=company.name,
            industry=company.industry,
            ticker=company.ticker,
            document_count=doc_count,
            analysis_count=len(company_analyses),
            high_risk_count=high_risk_count,
            latest_analysis=latest
        )
        summaries.append(summary)
        
    return sorted(summaries, key=lambda x: x.name)


def get_company(company_id: str) -> Optional[Company]:
    """Get a company by ID."""
    return _companies.get(company_id)


def create_company(company: Company) -> Company:
    """Create a new company."""
    _companies[company.id] = company
    logger.info(f"Created company: {company.name} ({company.id})")
    return company


def delete_company(company_id: str) -> bool:
    """Delete a company and all its documents and analyses."""
    if company_id not in _companies:
        return False
        
    # Remove documents
    docs_to_remove = [d_id for d_id, d in _documents.items() if d.company_id == company_id]
    for d_id in docs_to_remove:
        del _documents[d_id]
        
    # Remove analyses
    analyses_to_remove = [a_id for a_id, a in _analyses.items() if a.company_id == company_id]
    for a_id in analyses_to_remove:
        del _analyses[a_id]
        
    # Remove company
    del _companies[company_id]
    logger.info(f"Deleted company {company_id} and related data")
    return True


# --- Document Operations ---

def get_document(document_id: str) -> Optional[Document]:
    """Get a document by ID."""
    return _documents.get(document_id)


def get_documents_for_company(company_id: str) -> List[Document]:
    """Get all documents for a company."""
    return [doc for doc in _documents.values() if doc.company_id == company_id]


def create_document(document: Document) -> Document:
    """Create a new document record."""
    _documents[document.id] = document
    
    # Update company doc count
    if document.company_id in _companies:
        _companies[document.company_id].document_count += 1
        _companies[document.company_id].updated_at = datetime.utcnow()
        
    logger.info(f"Created document record: {document.filename} ({document.id})")
    return document


def update_document(document_id: str, updates: Dict) -> Optional[Document]:
    """Update a document record."""
    doc = _documents.get(document_id)
    if not doc:
        return None
        
    for key, value in updates.items():
        if hasattr(doc, key):
            setattr(doc, key, value)
            
    _documents[document_id] = doc
    return doc


def delete_document(document_id: str) -> bool:
    """Delete a document record."""
    doc = _documents.get(document_id)
    if not doc:
        return False
        
    company_id = doc.company_id
    del _documents[document_id]
    
    # Update company doc count
    if company_id in _companies:
        _companies[company_id].document_count = max(0, _companies[company_id].document_count - 1)
        
    logger.info(f"Deleted document record: {document_id}")
    return True


# --- Analysis Operations ---

def get_analysis(analysis_id: str) -> Optional[Analysis]:
    """Get an analysis by ID."""
    return _analyses.get(analysis_id)


def get_analyses_for_company(company_id: str) -> List[Analysis]:
    """Get all analyses for a company."""
    return [a for a in _analyses.values() if a.company_id == company_id]


def create_analysis(analysis: Analysis) -> Analysis:
    """Create a new analysis record."""
    _analyses[analysis.id] = analysis
    
    # Update company analysis count
    if analysis.company_id in _companies:
        _companies[analysis.company_id].analysis_count += 1
        _companies[analysis.company_id].updated_at = datetime.utcnow()
        
    logger.info(f"Created analysis record: {analysis.id}")
    return analysis


def update_analysis(analysis_id: str, updates: Dict) -> Optional[Analysis]:
    """Update an analysis record."""
    analysis = _analyses.get(analysis_id)
    if not analysis:
        return None
        
    for key, value in updates.items():
        if hasattr(analysis, key):
            setattr(analysis, key, value)
            
    _analyses[analysis_id] = analysis
    return analysis

def reset_all() -> bool:
    """Clear all data from the database."""
    _companies.clear()
    _documents.clear()
    _analyses.clear()
    logger.info("Cleared all in-memory database records.")
    return True
