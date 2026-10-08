"""
InvestiLens — Retriever

Semantic retrieval with metadata filtering via ChromaDB.
Wraps the vectorstore search with LangChain-compatible interface.
"""

from typing import Optional, List, Dict, Any

from app.core.config import get_settings
from app.core.logging import logger
from app.rag import vectorstore


def retrieve(
    query: str,
    company: Optional[str] = None,
    year: Optional[int] = None,
    years: Optional[List[int]] = None,
    document_type: Optional[str] = None,
    top_k: int = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant document chunks for a query.

    Supports filtering by company, year(s), and document type.

    Returns:
        List of dicts with: text, metadata, score
    """
    settings = get_settings()
    top_k = top_k or settings.TOP_K

    # If multiple years, perform separate searches and merge
    if years and len(years) > 1:
        all_results = []
        per_year_k = max(top_k // len(years), 2)

        for yr in years:
            results = vectorstore.search(
                query=query,
                top_k=per_year_k,
                company=company,
                year=yr,
                document_type=document_type,
            )
            all_results.extend(results)

        # Sort by score descending and take top_k
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return all_results[:top_k]

    return vectorstore.search(
        query=query,
        top_k=top_k,
        company=company,
        year=year,
        document_type=document_type,
    )


def retrieve_for_analysis(
    queries: List[str],
    company: str,
    year: Optional[int] = None,
    years: Optional[List[int]] = None,
    top_k_per_query: int = 3,
) -> List[Dict[str, Any]]:
    """
    Retrieve evidence for multiple analysis queries.
    Deduplicates results by chunk_id.
    """
    seen_ids = set()
    all_results = []

    for query in queries:
        results = retrieve(
            query=query,
            company=company,
            year=year,
            years=years,
            top_k=top_k_per_query,
        )
        for result in results:
            chunk_id = result.get("metadata", {}).get("chunk_id", "")
            if chunk_id and chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                all_results.append(result)

    logger.info(f"Retrieved {len(all_results)} unique chunks for {len(queries)} queries")
    return all_results
