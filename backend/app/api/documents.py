"""
InvestiLens — Documents API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional
import shutil
from pathlib import Path
import os
import traceback

from app.core.config import get_settings
from app.core.logging import logger
from app.models.document import Document
from app.services import db_service
from app.rag.ingestion import ingest_document

router = APIRouter()
settings = get_settings()


@router.get("/company/{company_id}", response_model=List[Document])
def get_company_documents(company_id: str):
    """Get all documents for a company."""
    company = db_service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    return db_service.get_documents_for_company(company_id)


def process_document_bg(document_id: str, file_path: str, company_name: str, year: int, doc_name: str, doc_type: str):
    """Background task to run the ingestion pipeline."""
    try:
        db_service.update_document(document_id, {"status": "processing"})
        
        result = ingest_document(
            file_path=file_path,
            company=company_name,
            year=year,
            document_name=doc_name,
            document_type=doc_type
        )
        
        db_service.update_document(document_id, {
            "status": "indexed",
            "page_count": result["page_count"],
            "chunk_count": result["chunk_count"],
            "file_hash": result["file_hash"]
        })
        logger.info(f"Successfully processed document {document_id}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to process document {document_id}: {error_msg}")
        logger.error(traceback.format_exc())
        
        db_service.update_document(document_id, {
            "status": "failed",
            "error_message": error_msg
        })


@router.post("/upload", response_model=Document)
def upload_document(
    background_tasks: BackgroundTasks,
    company_id: str = Form(...),
    document_name: str = Form(...),
    document_type: str = Form("annual_report"),
    year: Optional[int] = Form(None),
    file: UploadFile = File(...)
):
    """Upload and start processing a PDF document."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    company = db_service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create safe filename and save location
    safe_filename = f"{company_id}_{file.filename}"
    file_path = Path(settings.DOCUMENT_DIRECTORY) / safe_filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Create document record
    doc = Document(
        company_id=company_id,
        company_name=company.name,
        filename=file.filename,
        document_name=document_name,
        document_type=document_type,
        year=year,
        file_path=str(file_path),
        status="uploaded"
    )
    
    doc = db_service.create_document(doc)
    
    # Start background processing
    background_tasks.add_task(
        process_document_bg,
        document_id=doc.id,
        file_path=str(file_path),
        company_name=company.name,
        year=year,
        doc_name=document_name,
        doc_type=document_type
    )
    
    return doc


@router.delete("/{document_id}")
def delete_document(document_id: str):
    """Delete a document."""
    doc = db_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Remove file
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception as e:
        logger.warning(f"Failed to remove file {doc.file_path}: {e}")
        
    # We would also need to delete chunks from ChromaDB here in a real app,
    # but for simplicity we'll just remove the record.
        
    db_service.delete_document(document_id)
    return {"status": "success"}
