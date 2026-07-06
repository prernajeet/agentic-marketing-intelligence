# from graph.state import WorkflowState
from ml.churn import predict_churn
from ml.clv import predict_clv
from utils.logger import logger
import pandas as pd


def prediction_node(state: dict) -> dict:
    """Run churn and CLV predictions."""
    logger.info("Prediction node running")
    features = state.get("features", {})
    model_results = state.get("model_results", {})
    intent = state.get("intent", "churn")

    if "customer_features" not in features:
        return state

    cf_df = pd.DataFrame(features["customer_features"])

    try:
        if intent in ["churn", "general"]:
            preds = predict_churn(cf_df, model_results)
            state["churn_predictions"] = preds
    except Exception as e:
        logger.error(f"Churn prediction error: {e}")

    try:
        if intent in ["clv", "general"]:
            preds = predict_clv(cf_df, model_results)
            state["clv_predictions"] = preds
    except Exception as e:
        logger.error(f"CLV prediction error: {e}")

    return state
