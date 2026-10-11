"""
InvestiLens — Context Builder

Transforms retrieved chunks into a controlled context format
for LLM prompts, making citations easier and improving grounding.
"""

from typing import List, Dict, Any

NO_EVIDENCE_MESSAGE = "No relevant evidence was found in the documents."
SOURCE_SEPARATOR = "\n\n---\n\n"
SOURCE_PREVIEW_LENGTH = 300  # Max characters of chunk text sent to the frontend


def build_context(results: List[Dict[str, Any]]) -> str:
    """
    Format retrieved document chunks into numbered source blocks
    suitable for LLM consumption.

    Example output:
        [Source 1]
        Document: Apple Annual Report 2025
        Page: 47
        Section: Risk Factors

        Relevant Text:
        ...
    """
    if not results:
        return NO_EVIDENCE_MESSAGE

    source_blocks = [
        _format_source_block(number, result)
        for number, result in enumerate(results, 1)
    ]

    return SOURCE_SEPARATOR.join(source_blocks)


def _format_source_block(number: int, result: Dict[str, Any]) -> str:
    """Format one retrieved chunk as a numbered "[Source N]" block."""
    metadata = result.get("metadata", {})
    text = result.get("text", "")

    doc_name = metadata.get("document_name", "Unknown Document")
    page = metadata.get("page", "N/A")
    section = metadata.get("section", "General")
    company = metadata.get("company", "")
    year = metadata.get("year", "")

    return f"""[Source {number}]
Document: {doc_name}
Company: {company}
Year: {year}
Page: {page}
Section: {section}

Relevant Text:
{text}"""


def extract_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract clean source citations from retrieval results.

    Returns a list of source dicts suitable for the frontend evidence UI.
    """
    sources = []

    for result in results:
        metadata = result.get("metadata", {})
        sources.append({
            "document": metadata.get("document_name", "Unknown"),
            "page": metadata.get("page"),
            "section": metadata.get("section", "General"),
            "company": metadata.get("company", ""),
            "year": metadata.get("year"),
            "text": result.get("text", "")[:SOURCE_PREVIEW_LENGTH],  # Preview only
            "score": result.get("score"),
        })

    return sources
