# from graph.state import WorkflowState
from utils.logger import logger
from pathlib import Path
from config.settings import settings


def decision_node(state: dict) -> dict:
    """Decide whether to train a new model or use existing champion."""
    logger.info("Decision node running")
    strategy = state.get("ml_plan", {})
    nodes_to_run = state.get("nodes_to_run", [])

    # Check if a champion model already exists
    model_dir = settings.model_registry_path
    intent = state.get("intent", "churn")
    champion_path = model_dir / f"{intent}_champion.joblib"

    if champion_path.exists() and "training" not in nodes_to_run:
        state["should_train"] = False
        state["champion_model"] = str(champion_path)
        logger.info(f"Using existing champion model: {champion_path}")
    else:
        state["should_train"] = True
        logger.info("Will train new models")
    return state
