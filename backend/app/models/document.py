"""
InvestiLens — Document Model

Represents uploaded and processed documents.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Document(BaseModel):
    """Represents a processed document in the system."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    company_name: str
    filename: str
    document_name: str
    document_type: str = "annual_report"
    year: Optional[int] = None
    file_path: str
    file_hash: Optional[str] = None
    page_count: int = 0
    chunk_count: int = 0
    status: str = "uploaded"  # uploaded, processing, indexed, failed
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class DocumentUpload(BaseModel):
    """Schema for document upload metadata."""

    company_id: str
    document_name: str
    document_type: str = "annual_report"
    year: Optional[int] = None


class DocumentChunk(BaseModel):
    """Represents a single chunk of a document stored in the vector DB."""

    chunk_id: str
    document_id: str
    company: str
    year: Optional[int] = None
    document_name: str
    document_type: str
    page: int
    section: Optional[str] = None
    text: str
