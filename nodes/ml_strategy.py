# from graph.state import WorkflowState
from llm.gemini_client import gemini_client
from utils.logger import logger
import json

ML_STRATEGY_PROMPT = """You are an ML strategy advisor for marketing analytics.
Given the user intent and available data, recommend the ML approach.
Respond in JSON with:
- models_to_train: list of model names (e.g. ["XGBoost", "LightGBM", "RandomForest"])
- primary_task: "classification" or "regression"
- target_variable: field name to predict
- evaluation_metrics: list of metrics
- feature_selection_strategy: brief description
- rationale: one paragraph explanation

Intent: {intent}
Available features: {features}
Respond ONLY with valid JSON."""


def ml_strategy_node(state: dict) -> dict:
    """Gemini-powered ML strategy selection node."""
    logger.info("ML strategy node running")
    intent = state.get("intent", "churn")
    features = list(state.get("features", {}).keys())
    try:
        prompt = ML_STRATEGY_PROMPT.format(intent=intent, features=features)
        response = gemini_client.generate(prompt)
        text = response.strip().lstrip("```json").rstrip("```").strip()
        strategy = json.loads(text)
        state["ml_plan"] = strategy
    except Exception as e:
        logger.warning(f"ML strategy error: {e}")
        state["ml_plan"] = {
            "model_type": "RandomForest",
            "hyperparameters": {"n_estimators": 100}
        }
        state["errors"].append(f"ML Strategy fallback used due to: {e}")
        
    return state
