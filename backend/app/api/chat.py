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
        if not response.evidence:
            response.evidence = evidence
            
        return response
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
