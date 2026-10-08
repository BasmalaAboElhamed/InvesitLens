"""
InvestiLens — Document Ingestion Pipeline

Full pipeline: PDF → Extract → Clean → Chunk → Embed → Store in ChromaDB.
"""

import fitz  # PyMuPDF
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.core.config import get_settings
from app.core.logging import logger
from app.rag.preprocessing import clean_text, remove_repeated_headers_footers
from app.rag.chunking import chunk_document
from app.rag import vectorstore


def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of a file for duplicate detection."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            sha256.update(block)
    return sha256.hexdigest()


def extract_pdf_pages(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from each page of a PDF using PyMuPDF.

    Returns list of dicts: {page: int, text: str}
    """
    pages = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            pages.append({
                "page": page_num + 1,
                "text": text,
            })
        doc.close()
        logger.info(f"Extracted {len(pages)} pages from: {file_path}")
    except Exception as e:
        logger.error(f"PDF extraction failed for {file_path}: {e}")
        raise

    return pages


def ingest_document(
    file_path: str,
    company: str,
    year: Optional[int] = None,
    document_name: Optional[str] = None,
    document_type: str = "annual_report",
) -> Dict[str, Any]:
    """
    Full ingestion pipeline for a single PDF document.

    Returns:
        Dict with ingestion results: page_count, chunk_count, file_hash
    """
    file_path = str(Path(file_path).resolve())
    logger.info(f"Starting ingestion: {file_path}")

    # Step 1: Compute file hash for duplicate detection
    file_hash = compute_file_hash(file_path)
    logger.info(f"File hash: {file_hash}")

    # Step 2: Extract pages
    raw_pages = extract_pdf_pages(file_path)
    page_count = len(raw_pages)

    if page_count == 0:
        raise ValueError(f"No text extracted from: {file_path}")

    # Step 3: Clean text & remove repeated headers/footers
    page_texts = [p["text"] for p in raw_pages]
    cleaned_texts = remove_repeated_headers_footers(page_texts)

    cleaned_pages = []
    for i, page_data in enumerate(raw_pages):
        cleaned_text_content = clean_text(cleaned_texts[i] if i < len(cleaned_texts) else page_data["text"])
        if cleaned_text_content.strip():
            cleaned_pages.append({
                "text": cleaned_text_content,
                "page": page_data["page"],
                "metadata": {
                    "company": company,
                    "year": year or 0,
                    "document_name": document_name or Path(file_path).stem,
                    "document_type": document_type,
                },
            })

    logger.info(f"Cleaned {len(cleaned_pages)} pages (from {page_count} raw)")

    # Step 4: Chunk documents
    chunks = chunk_document(cleaned_pages)
    logger.info(f"Created {len(chunks)} chunks")

    # Step 5: Store in ChromaDB
    added = vectorstore.add_documents(chunks)
    logger.info(f"Indexed {added} chunks in ChromaDB")

    return {
        "file_hash": file_hash,
        "page_count": page_count,
        "chunk_count": len(chunks),
        "indexed_count": added,
    }


def ingest_directory(
    directory: str,
    company: str,
    year: Optional[int] = None,
    document_type: str = "annual_report",
) -> List[Dict[str, Any]]:
    """
    Ingest all PDF files in a directory.

    Returns list of ingestion results.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    results = []
    pdf_files = sorted(dir_path.glob("*.pdf"))

    for pdf_file in pdf_files:
        try:
            result = ingest_document(
                file_path=str(pdf_file),
                company=company,
                year=year,
                document_name=pdf_file.stem,
                document_type=document_type,
            )
            result["filename"] = pdf_file.name
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to ingest {pdf_file.name}: {e}")
            results.append({
                "filename": pdf_file.name,
                "error": str(e),
            })

    return results
