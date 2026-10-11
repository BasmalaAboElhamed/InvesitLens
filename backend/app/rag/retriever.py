"""
InvestiLens — Retriever

Semantic retrieval with metadata filtering via ChromaDB.
Wraps the vectorstore search with LangChain-compatible interface.
"""

from typing import Optional, List, Dict, Any

from app.core.config import get_settings
from app.core.logging import logger
from app.rag import vectorstore

# When searching several years, each year gets at least this many results
MIN_RESULTS_PER_YEAR = 2


def retrieve(
    query: str,
    company: Optional[str] = None,
    year: Optional[int] = None,
    years: Optional[List[int]] = None,
    document_type: Optional[str] = None,
    top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant document chunks for a query.

    Supports filtering by company, year(s), and document type.
    If `years` has more than one year it takes priority over `year`.

    Returns:
        List of dicts with: text, metadata, score
    """
    settings = get_settings()
    top_k = top_k or settings.TOP_K

    if years and len(years) > 1:
        return _retrieve_across_years(query, company, years, document_type, top_k)

    return vectorstore.search(
        query=query,
        top_k=top_k,
        company=company,
        year=year,
        document_type=document_type,
    )


def _retrieve_across_years(
    query: str,
    company: Optional[str],
    years: List[int],
    document_type: Optional[str],
    top_k: int,
) -> List[Dict[str, Any]]:
    """
    Search each year separately (so every year is represented),
    then merge and keep the `top_k` best-scoring chunks overall.
    """
    results_per_year = max(top_k // len(years), MIN_RESULTS_PER_YEAR)
    merged_results = []

    for single_year in years:
        merged_results.extend(
            vectorstore.search(
                query=query,
                top_k=results_per_year,
                company=company,
                year=single_year,
                document_type=document_type,
            )
        )

    # Sort by score descending and take top_k
    merged_results.sort(key=lambda result: result.get("score", 0), reverse=True)
    return merged_results[:top_k]


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
    seen_chunk_ids = set()
    unique_results = []

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
            if chunk_id and chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk_id)
                unique_results.append(result)

    logger.info(f"Retrieved {len(unique_results)} unique chunks for {len(queries)} queries")
    return unique_results
