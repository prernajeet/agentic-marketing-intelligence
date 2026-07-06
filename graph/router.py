from typing import Literal
from .state import WorkflowState


def route_after_planning(state: WorkflowState) -> Literal[
    "context", "data_retrieval", "__end__"
]:
    """Route from planning node."""
    plan = state.get("plan", {})
    if not plan or plan.get("error"):
        return "__end__"
    return "context"


def route_after_validation(state: WorkflowState) -> Literal[
    "feature_engineering", "__end__"
]:
    """Only proceed if data is valid."""
    if not state.get("validated", False):
        return "__end__"
    return "feature_engineering"


def route_after_decision(state: WorkflowState) -> Literal[
    "training", "prediction"
]:
    """Train or skip directly to prediction."""
    if state.get("should_train", True):
        return "training"
    return "prediction"


def route_after_analytics(state: WorkflowState) -> Literal[
    "ml_strategy", "business_insight"
]:
    """If ML is needed route to ml_strategy, else skip to insights."""
    nodes = state.get("nodes_to_run", [])
    if any(n in nodes for n in ["training", "prediction", "churn", "clv"]):
        return "ml_strategy"
    return "business_insight"


def route_after_evaluation(state: WorkflowState) -> Literal[
    "prediction", "explainability"
]:
    """After evaluation decide if we need predictions."""
    nodes = state.get("nodes_to_run", [])
    if "prediction" in nodes:
        return "prediction"
    return "explainability"
