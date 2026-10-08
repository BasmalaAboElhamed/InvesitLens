"""
InvestiLens — Context Builder

Transforms retrieved chunks into a controlled context format
for LLM prompts, making citations easier and improving grounding.
"""

from typing import List, Dict, Any


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
        return "No relevant evidence was found in the documents."

    context_parts = []

    for i, result in enumerate(results, 1):
        metadata = result.get("metadata", {})
        text = result.get("text", "")

        doc_name = metadata.get("document_name", "Unknown Document")
        page = metadata.get("page", "N/A")
        section = metadata.get("section", "General")
        company = metadata.get("company", "")
        year = metadata.get("year", "")

        source_block = f"""[Source {i}]
Document: {doc_name}
Company: {company}
Year: {year}
Page: {page}
Section: {section}

Relevant Text:
{text}"""

        context_parts.append(source_block)

    return "\n\n---\n\n".join(context_parts)


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
            "text": result.get("text", "")[:300],  # Preview only
            "score": result.get("score"),
        })

    return sources
