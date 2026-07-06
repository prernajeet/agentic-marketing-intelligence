from fastapi import APIRouter, HTTPException
from api.schemas import AnalyticsSummaryResponse
from config.settings import settings
from analytics.customer import compute_customer_analytics
from analytics.revenue import compute_revenue_analytics
import pandas as pd
from pathlib import Path
from utils.logger import logger

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary():
    """Get high-level analytics summary."""
    try:
        raw_dir = settings.raw_data_path
        raw_data = {}
        for csv in ["customers", "transactions", "order_items", "products"]:
            fp = raw_dir / f"{csv}.csv"
            if fp.exists():
                raw_data[csv] = pd.read_csv(fp).to_dict(orient="records")

        cust = compute_customer_analytics(raw_data)
        rev = compute_revenue_analytics(raw_data)
        summary = rev.get("summary", {})

        return AnalyticsSummaryResponse(
            total_customers=cust.get("total_customers"),
            total_revenue=summary.get("total_revenue"),
            total_orders=summary.get("total_orders"),
            avg_order_value=summary.get("avg_order_value"),
        )
    except Exception as e:
        logger.error(f"Analytics summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
