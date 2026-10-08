"""
InvestiLens — FastAPI App Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import logger
from app.api import router as api_router

settings = get_settings()

app = FastAPI(
    title="InvestiLens API",
    description="AI-Powered Investor Intelligence Platform",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Run initial setup tasks."""
    logger.info("Starting InvestiLens API...")
    
    # Ensure directories exist
    Path(settings.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)
    Path(settings.DOCUMENT_DIRECTORY).mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "InvestiLens API"}
