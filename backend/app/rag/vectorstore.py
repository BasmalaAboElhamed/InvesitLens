"""
InvestiLens — ChromaDB Vector Store Integration

Manages the vector database: storing embeddings, documents, metadata,
and performing semantic retrieval with metadata filtering.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from typing import Optional, List, Dict, Any
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import logger
from app.rag.embeddings import get_embeddings

_chroma_client = None
_vectorstore = None

COLLECTION_NAME = "investilens_documents"


def get_chroma_client() -> chromadb.ClientAPI:
    """Return a persistent ChromaDB client."""
    global _chroma_client

    if _chroma_client is None:
        settings = get_settings()
        persist_dir = str(Path(settings.CHROMA_PERSIST_DIRECTORY).resolve())
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        _chroma_client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info(f"ChromaDB client initialized at: {persist_dir}")

    return _chroma_client


def get_vectorstore() -> Chroma:
    """Return the LangChain Chroma vectorstore wrapper."""
    global _vectorstore

    if _vectorstore is None:
        client = get_chroma_client()

        _vectorstore = Chroma(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding_function=get_embeddings(),
        )

        logger.info("LangChain Chroma vectorstore initialized")

    return _vectorstore


def add_documents(chunks: List[Dict[str, Any]]) -> int:
    """
    Add document chunks to ChromaDB.

    Args:
        chunks: List of dicts with keys: chunk_id, text, page, section, company, year, etc.

    Returns:
        Number of chunks added.
    """
    if not chunks:
        return 0

    vectorstore = get_vectorstore()

    texts = []
    metadatas = []
    ids = []

    for chunk in chunks:
        texts.append(chunk["text"])
        ids.append(chunk["chunk_id"])

        metadata = {
            "company": chunk.get("company", ""),
            "year": chunk.get("year", 0),
            "document_name": chunk.get("document_name", ""),
            "document_type": chunk.get("document_type", ""),
            "page": chunk.get("page", 0),
            "section": chunk.get("section", "General"),
            "chunk_id": chunk["chunk_id"],
        }
        # ChromaDB requires string/int/float values
        metadata = {k: v for k, v in metadata.items() if v is not None}
        metadatas.append(metadata)

    vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    logger.info(f"Added {len(texts)} chunks to ChromaDB")

    return len(texts)


def search(
    query: str,
    top_k: int = None,
    company: Optional[str] = None,
    year: Optional[int] = None,
    document_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Perform semantic search with optional metadata filtering.

    Returns list of dicts with: text, metadata, score.
    """
    settings = get_settings()
    top_k = top_k or settings.TOP_K

    vectorstore = get_vectorstore()

    # Build metadata filter
    where_filter = _build_filter(company, year, document_type)

    if where_filter:
        results = vectorstore.similarity_search_with_relevance_scores(
            query, k=top_k, filter=where_filter
        )
    else:
        results = vectorstore.similarity_search_with_relevance_scores(
            query, k=top_k
        )

    output = []
    for doc, score in results:
        output.append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": score,
        })

    logger.info(f"Search returned {len(output)} results (top_k={top_k})")
    return output


def _build_filter(
    company: Optional[str] = None,
    year: Optional[int] = None,
    document_type: Optional[str] = None,
) -> Optional[Dict]:
    """Build a ChromaDB where-filter from optional parameters."""
    conditions = []

    if company:
        conditions.append({"company": {"$eq": company}})
    if year:
        conditions.append({"year": {"$eq": year}})
    if document_type:
        conditions.append({"document_type": {"$eq": document_type}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def get_collection_stats() -> Dict[str, Any]:
    """Return basic statistics about the vector store."""
    client = get_chroma_client()
    try:
        collection = client.get_collection(COLLECTION_NAME)
        count = collection.count()
        return {"collection": COLLECTION_NAME, "document_count": count}
    except Exception:
        return {"collection": COLLECTION_NAME, "document_count": 0}


def delete_company_documents(company: str) -> int:
    """Delete all chunks belonging to a company."""
    client = get_chroma_client()
    try:
        collection = client.get_collection(COLLECTION_NAME)
        results = collection.get(where={"company": {"$eq": company}})
        if results and results["ids"]:
            collection.delete(ids=results["ids"])
            logger.info(f"Deleted {len(results['ids'])} chunks for company: {company}")
            return len(results["ids"])
    except Exception as e:
        logger.error(f"Error deleting company documents: {e}")
    return 0

def reset_collection() -> bool:
    """Delete and recreate the ChromaDB collection to clear all data."""
    global _vectorstore
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info(f"Deleted Chroma collection: {COLLECTION_NAME}")
        _vectorstore = None
        return True
    except Exception as e:
        logger.error(f"Error deleting Chroma collection: {e}")
        return False
