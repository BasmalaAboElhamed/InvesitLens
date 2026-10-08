"""
InvestiLens — API Router Configuration
"""

from fastapi import APIRouter
from app.api import companies
from app.api import documents
from app.api import analysis
from app.api import chat
from app.api import reset

router = APIRouter()

router.include_router(companies.router, prefix="/companies", tags=["Companies"])
router.include_router(documents.router, prefix="/documents", tags=["Documents"])
router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(reset.router, prefix="/reset", tags=["System"])
