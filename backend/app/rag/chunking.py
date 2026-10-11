"""
InvestiLens — Document-Aware Chunking

Semantic/document-aware chunking that preserves paragraph boundaries,
section metadata, and maintains configurable overlap.
"""

from typing import List, Dict, Any, Optional
from app.core.config import get_settings
from app.rag.preprocessing import detect_section

# Paragraphs are separated by a blank line; when two paragraphs are joined
# into one chunk, this separator adds 2 characters to the chunk length.
PARAGRAPH_SEPARATOR = "\n\n"
SEPARATOR_LENGTH = len(PARAGRAPH_SEPARATOR)


def chunk_document(
    pages: List[Dict[str, Any]],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Chunk a document's pages into semantically coherent chunks.

    Chunks never span more than one page. Within a page, paragraphs are
    packed together until adding the next one would exceed `chunk_size`;
    the tail of each finished chunk is carried into the next one as overlap.

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
    chunk_counter = 0  # Running counter across the whole document (not per page)

    for page_data in pages:
        page_text = page_data["text"]
        page_num = page_data.get("page", 0)
        metadata = page_data.get("metadata", {})

        if not page_text.strip():
            continue

        section = detect_section(page_text)

        # Split by paragraph boundaries first
        paragraphs = [p.strip() for p in page_text.split(PARAGRAPH_SEPARATOR) if p.strip()]

        current_chunk = ""

        for paragraph in paragraphs:
            would_exceed_size = (
                len(current_chunk) + len(paragraph) + SEPARATOR_LENGTH > chunk_size
            )

            if current_chunk and would_exceed_size:
                # Current chunk is full: save it, then start a new one
                chunk_counter += 1
                chunks.append(
                    _make_chunk(current_chunk, chunk_counter, page_num, section, metadata)
                )

                # The new chunk starts with the tail of the previous one (overlap)
                if chunk_overlap > 0:
                    current_chunk = current_chunk[-chunk_overlap:] + PARAGRAPH_SEPARATOR + paragraph
                else:
                    current_chunk = paragraph
            elif current_chunk:
                current_chunk += PARAGRAPH_SEPARATOR + paragraph
            else:
                current_chunk = paragraph

        # Save whatever is left at the end of the page
        if current_chunk.strip():
            chunk_counter += 1
            chunks.append(
                _make_chunk(current_chunk, chunk_counter, page_num, section, metadata)
            )

    return chunks


def _make_chunk(
    text: str,
    chunk_number: int,
    page_num: int,
    section: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Build one chunk dict (text + id + page + section + document metadata)."""
    company = metadata.get("company", "unknown")
    year = metadata.get("year", "")
    chunk_id = f"{company.lower().replace(' ', '_')}_{year}_p{page_num}_c{chunk_number:03d}"

    return {
        "chunk_id": chunk_id,
        "text": text.strip(),
        "page": page_num,
        "section": section,
        **metadata,
    }


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

        # Last piece: take everything that is left
        if end >= len(text):
            pieces.append(text[start:])
            break

        # Prefer to break at a sentence end, then at a space, else hard cut
        break_point = text.rfind('. ', start, end)
        if break_point == -1 or break_point <= start:
            break_point = text.rfind(' ', start, end)
        if break_point == -1 or break_point <= start:
            break_point = end

        pieces.append(text[start:break_point + 1])
        start = break_point + 1 - overlap

    return pieces
