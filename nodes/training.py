# from graph.state import WorkflowState
from ml.churn import train_churn_model
from ml.clv import train_clv_model
from utils.logger import logger
import pandas as pd


def training_node(state: dict) -> dict:
    """Train ML models based on strategy and intent."""
    logger.info("Training node running")
    intent = state.get("intent", "churn")
    features = state.get("features", {})
    strategy = state.get("ml_plan", {})

    if "customer_features" not in features:
        state["errors"] = state.get("errors", []) + ["No customer features for training"]
        state["model_results"] = {}
        return state

    cf_df = pd.DataFrame(features["customer_features"])
    try:
        if intent in ["churn", "general"]:
            results = train_churn_model(cf_df, strategy)
            state["model_results"] = results
        elif intent == "clv":
            results = train_clv_model(cf_df, strategy)
            state["model_results"] = results
        else:
            results = train_churn_model(cf_df, strategy)
            state["model_results"] = results
    except Exception as e:
        logger.error(f"Training error: {e}")
        state["errors"] = state.get("errors", []) + [f"Training: {e}"]
        state["model_results"] = {}
    return state
