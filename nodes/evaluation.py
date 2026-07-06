# from graph.state import WorkflowState
from ml.comparison import compare_models, select_champion
from utils.logger import logger


def evaluation_node(state: dict) -> dict:
    """Evaluate and compare all trained models, select champion."""
    logger.info("Evaluation node running")
    model_results = state.get("model_results", {})

    if not model_results:
        state["evaluation_report"] = {"error": "No models to evaluate"}
        return state

    try:
        comparison = compare_models(model_results)
        champion = select_champion(comparison)
        state["evaluation_report"] = comparison
        state["champion_model"] = champion
        logger.info(f"Champion model: {champion}")
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        state["errors"] = state.get("errors", []) + [f"Evaluation: {e}"]
    return state
