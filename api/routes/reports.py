from fastapi import APIRouter, HTTPException
from api.schemas import ReportResponse
from config.settings import settings
from pathlib import Path
from utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.get("/latest", response_model=ReportResponse)
def get_latest_report():
    """Retrieve the latest generated executive report."""
    try:
        reports_dir = Path(settings.model_registry_path).parent.parent / "reports"
        if not reports_dir.exists():
            return ReportResponse(
                report="No reports generated yet. Run a workflow first.",
                generated_at=datetime.utcnow().isoformat(),
            )
        reports = sorted(reports_dir.glob("report_*.md"), reverse=True)
        if not reports:
            return ReportResponse(
                report="No reports found.",
                generated_at=datetime.utcnow().isoformat(),
            )
        latest = reports[0]
        content = latest.read_text(encoding="utf-8")
        ts = latest.stem.replace("report_", "")
        return ReportResponse(report=content, generated_at=ts)
    except Exception as e:
        logger.error(f"Report retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
