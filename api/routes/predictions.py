from fastapi import APIRouter, HTTPException
from api.schemas import (
    ChurnPredictionRequest,
    ChurnPredictionResponse,
    CLVPredictionRequest,
    CLVPredictionResponse,
)
from config.settings import settings
from ml.churn import train_churn_model, predict_churn
from ml.clv import train_clv_model, predict_clv
from nodes.feature_engineering import feature_engineering_node
import pandas as pd
from pathlib import Path
from utils.logger import logger

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])


def _load_customer_features():
    """Load and engineer customer features from raw CSV data."""
    raw_dir = settings.raw_data_path
    raw_data = {}
    for csv in ["customers", "transactions", "order_items"]:
        fp = raw_dir / f"{csv}.csv"
        if fp.exists():
            raw_data[csv] = pd.read_csv(fp).to_dict(orient="records")
    state = {"raw_data": raw_data, "validated": True, "errors": [], "warnings": []}
    state = feature_engineering_node(state)
    features = state.get("features", {})
    if "customer_features" not in features:
        raise HTTPException(status_code=400, detail="No customer features available")
    return pd.DataFrame(features["customer_features"])


@router.post("/churn", response_model=ChurnPredictionResponse)
def predict_churn_endpoint(request: ChurnPredictionRequest):
    """Run churn predictions."""
    try:
        cf_df = _load_customer_features()
        model_results = train_churn_model(cf_df)
        result = predict_churn(cf_df, model_results)
        return ChurnPredictionResponse(
            churn_rate=result["churn_rate"],
            total_customers=result["total_customers"],
            churned_count=result["churned_count"],
            high_risk_count=result["high_risk_count"],
            champion_model=result["champion_model"],
            high_risk_customers=result["high_risk_customers"],
        )
    except Exception as e:
        logger.error(f"Churn prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clv", response_model=CLVPredictionResponse)
def predict_clv_endpoint(request: CLVPredictionRequest):
    """Run CLV predictions."""
    try:
        cf_df = _load_customer_features()
        model_results = train_clv_model(cf_df)
        result = predict_clv(cf_df, model_results)
        return CLVPredictionResponse(
            total_customers=result["total_customers"],
            avg_clv_12m=result["avg_clv_12m"],
            avg_clv_lifetime=result["avg_clv_lifetime"],
            champion_model=result["champion_model"],
            sample_predictions=result["predictions"][:10],
        )
    except Exception as e:
        logger.error(f"CLV prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
