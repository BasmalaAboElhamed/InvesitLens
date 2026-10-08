"""
InvestiLens — Document-Aware Chunking

Semantic/document-aware chunking that preserves paragraph boundaries,
section metadata, and maintains configurable overlap.
"""

from typing import List, Dict, Any
from app.core.config import get_settings
from app.rag.preprocessing import detect_section


def chunk_document(
    pages: List[Dict[str, Any]],
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[Dict[str, Any]]:
    """
    Chunk a document's pages into semantically coherent chunks.

    Args:
        pages: List of dicts with keys: text, page, metadata (company, year, etc.)
        chunk_size: Max characters per chunk (default from config)
        chunk_overlap: Overlap between chunks (default from config)

    Returns:
        List of chunk dicts with text, metadata, chunk_id
    """
    settings = get_settings()
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    chunks = []
    chunk_counter = 0

    for page_data in pages:
        page_text = page_data["text"]
        page_num = page_data.get("page", 0)
        metadata = page_data.get("metadata", {})

        if not page_text.strip():
            continue

        # Detect section for this page
        section = detect_section(page_text)

        # Split by paragraph boundaries first
        paragraphs = [p.strip() for p in page_text.split('\n\n') if p.strip()]

        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph exceeds chunk_size, finalize current chunk
            if current_chunk and len(current_chunk) + len(paragraph) + 2 > chunk_size:
                chunk_counter += 1
                company = metadata.get("company", "unknown")
                year = metadata.get("year", "")
                chunk_id = f"{company.lower().replace(' ', '_')}_{year}_p{page_num}_c{chunk_counter:03d}"

                chunks.append({
                    "chunk_id": chunk_id,
                    "text": current_chunk.strip(),
                    "page": page_num,
                    "section": section,
                    **metadata,
                })

                # Keep overlap from end of current chunk
                if chunk_overlap > 0:
                    current_chunk = current_chunk[-chunk_overlap:] + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Finalize the last chunk from this page
        if current_chunk.strip():
            chunk_counter += 1
            company = metadata.get("company", "unknown")
            year = metadata.get("year", "")
            chunk_id = f"{company.lower().replace(' ', '_')}_{year}_p{page_num}_c{chunk_counter:03d}"

            chunks.append({
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "page": page_num,
                "section": section,
                **metadata,
            })

    return chunks


def split_large_text(text: str, max_size: int, overlap: int) -> List[str]:
    """
    Split a single large text block into smaller pieces
    respecting sentence boundaries where possible.
    """
    if len(text) <= max_size:
        return [text]

    pieces = []
    start = 0

    while start < len(text):
        end = start + max_size

        if end >= len(text):
            pieces.append(text[start:])
            break

        # Try to break at sentence boundary
        break_point = text.rfind('. ', start, end)
        if break_point == -1 or break_point <= start:
            break_point = text.rfind(' ', start, end)
        if break_point == -1 or break_point <= start:
            break_point = end

        pieces.append(text[start:break_point + 1])
        start = break_point + 1 - overlap

    return pieces
