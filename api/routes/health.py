from fastapi import APIRouter
from datetime import datetime
from api.schemas import HealthResponse
from database.connection import engine
from sqlalchemy import text

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        database=db_status,
    )
