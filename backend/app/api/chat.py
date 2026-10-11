"""
InvestiLens — Chat API
"""

from fastapi import APIRouter, HTTPException
import traceback

from app.core.logging import logger
from app.schemas.chat import ChatRequest, ChatResponse, EvidenceSource
from app.services import db_service
from app.rag.retriever import retrieve
from app.rag.context_builder import build_context, extract_sources
from app.llm import chains

router = APIRouter()


def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace/quotes so quotes can be compared loosely."""
    return " ".join((text or "").lower().replace('"', " ").replace("\u201c", " ").replace("\u201d", " ").split())


def _ground_evidence(llm_evidence, chunks):
    """
    Keep only LLM-cited evidence that really comes from a retrieved chunk, and take
    document name, page and section from that chunk's metadata (never from the LLM,
    which can invent names such as "Apple_2025_10-K" or wrong page numbers).
    """
    grounded = []
    for item in llm_evidence or []:
        quote = _normalize(item.text)
        if not quote:
            continue
        quote_words = set(quote.split())
        best_chunk, best_score = None, 0.0
        for chunk in chunks:
            chunk_text = _normalize(chunk.get("text", ""))
            if quote in chunk_text:
                best_chunk, best_score = chunk, 1.0
                break
            overlap = len(quote_words & set(chunk_text.split())) / len(quote_words)
            if overlap > best_score:
                best_chunk, best_score = chunk, overlap
        if best_chunk is not None and best_score >= 0.7:
            metadata = best_chunk.get("metadata", {})
            grounded.append(EvidenceSource(
                document=metadata.get("document_name", "Unknown"),
                page=metadata.get("page"),
                section=metadata.get("section", "General"),
                text=item.text,
            ))
    return grounded


@router.post("/", response_model=ChatResponse)
def chat_with_documents(request: ChatRequest):
    """
    Interactive Q&A against company documents.
    """
    company = db_service.get_company(request.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    try:
        # Step 1: Classify Intent
        intent = chains.classify_intent(request.question)
        
        # Step 2: Retrieve Evidence
        filters = request.filters or {}
        year = filters.get("year")
        years = filters.get("years")
        
        chunks = retrieve(
            query=request.question,
            company=company.name,
            year=year,
            years=years,
            top_k=5
        )
        
        if not chunks:
            return ChatResponse(
                answer="I could not find sufficient evidence in the documents to answer this question.",
                confidence="Low",
                intent=intent
            )
            
        # Step 3: Build Context & Extract Sources
        context = build_context(chunks)
        sources_raw = extract_sources(chunks)
        
        # Format sources for response
        evidence = []
        for s in sources_raw:
            evidence.append(EvidenceSource(
                document=s["document"],
                page=s["page"],
                section=s["section"],
                text=s["text"]
            ))
            
        # Format history
        history_text = ""
        if request.history:
            for msg in request.history:
                role = msg.get("role", "user").capitalize()
                content = msg.get("content", "")
                if role == "User":
                    history_text += f"User: {content}\n"
                elif role == "Assistant":
                    history_text += f"InvestiLens: {content}\n"
                    
        # Step 4: Generate Answer
        response = chains.run_chat(
            question=request.question,
            company=company.name,
            context=context,
            history=history_text
        )
        
        # Ensure we return the intent and our formatted evidence if the LLM missed it
        response.intent = intent
        # LLM-written citations are verified against the retrieved chunks; if none
        # survive, fall back to the retrieved sources themselves.
        response.evidence = _ground_evidence(response.evidence, chunks) or evidence
            
        return response
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))