from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas import DataImportRequest, DataImportResponse
from database.connection import get_db
from database.loader import load_csv_to_db
from database.models import Base
from database.connection import engine
from pathlib import Path
from utils.logger import logger

router = APIRouter(prefix="/api/v1/data", tags=["Data"])


@router.post("/import", response_model=DataImportResponse)
def import_data(request: DataImportRequest, db: Session = Depends(get_db)):
    """Import CSV data files into PostgreSQL."""
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        data_dir = Path(request.data_dir) if request.data_dir else None
        results = load_csv_to_db(db, data_dir=data_dir)
        successful = sum(1 for v in results.values() if v.get("status") == "ok")
        failed = sum(1 for v in results.values() if v.get("status") == "error")
        return DataImportResponse(
            results=results,
            total_tables=len(results),
            successful=successful,
            failed=failed,
        )
    except Exception as e:
        logger.error(f"Data import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
