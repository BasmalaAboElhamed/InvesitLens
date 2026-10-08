from fastapi import APIRouter, status
from app.services import db_service
from app.rag import vectorstore
from app.core.config import get_settings
from pathlib import Path
from app.core.logging import logger

router = APIRouter()

@router.delete("/", status_code=status.HTTP_200_OK)
def reset_all_data():
    """Completely reset all user data for testing."""
    # 1. Clear database
    db_service.reset_all()
    
    # 2. Clear vectorstore
    vectorstore.reset_collection()
    
    # 3. Delete uploaded files
    settings = get_settings()
    doc_dir = Path(settings.DOCUMENT_DIRECTORY)
    if doc_dir.exists():
        for item in doc_dir.iterdir():
            if item.is_file() and item.name.endswith(".pdf"):
                try:
                    item.unlink()
                except Exception as e:
                    logger.error(f"Failed to delete file {item}: {e}")
                    
    return {"success": True, "message": "All InvestiLens user data has been reset successfully"}
