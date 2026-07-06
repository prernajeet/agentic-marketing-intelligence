from langgraph.graph import StateGraph, END
from .state import WorkflowState
from .router import (
    route_after_planning,
    route_after_validation,
    route_after_decision,
    route_after_analytics,
    route_after_evaluation,
)
from nodes.planning import planning_node
from nodes.context import context_node as ctx_gather_node
from nodes.data_retrieval import data_retrieval_node
from nodes.validation import validation_node
from nodes.feature_engineering import feature_engineering_node
from nodes.analytics import analytics_node
from nodes.ml_strategy import ml_strategy_node
from nodes.training import training_node
from nodes.evaluation import evaluation_node
from nodes.decision import decision_node
from nodes.prediction import prediction_node
from nodes.explainability import explainability_node
from nodes.simulation import simulation_node
from nodes.business_insight import business_insight_node
from nodes.recommendation import recommendation_node
from nodes.reporting import reporting_node
from nodes.memory import memory_node
from utils.logger import logger


def build_workflow() -> StateGraph:
    graph = StateGraph(WorkflowState)

    # Register all nodes
    graph.add_node("planning", planning_node)
    graph.add_node("ctx_gather", ctx_gather_node)
    graph.add_node("data_retrieval", data_retrieval_node)
    graph.add_node("validation", validation_node)
    graph.add_node("feature_engineering", feature_engineering_node)
    graph.add_node("analytics", analytics_node)
    graph.add_node("ml_strategy", ml_strategy_node)
    graph.add_node("decision", decision_node)
    graph.add_node("training", training_node)
    graph.add_node("evaluation", evaluation_node)
    graph.add_node("prediction", prediction_node)
    graph.add_node("explainability", explainability_node)
    graph.add_node("simulation", simulation_node)
    graph.add_node("business_insight", business_insight_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("reporting", reporting_node)
    graph.add_node("memory", memory_node)

    # Entry point
    graph.set_entry_point("planning")

    # Edges
    graph.add_conditional_edges(
        "planning",
        route_after_planning,
        {"context": "ctx_gather", "__end__": END},
    )
    graph.add_edge("ctx_gather", "data_retrieval")
    graph.add_edge("data_retrieval", "validation")
    graph.add_conditional_edges(
        "validation",
        route_after_validation,
        {"feature_engineering": "feature_engineering", "__end__": END},
    )
    graph.add_edge("feature_engineering", "analytics")
    graph.add_conditional_edges(
        "analytics",
        route_after_analytics,
        {"ml_strategy": "ml_strategy", "business_insight": "business_insight"},
    )
    graph.add_edge("ml_strategy", "decision")
    graph.add_conditional_edges(
        "decision",
        route_after_decision,
        {"training": "training", "prediction": "prediction"},
    )
    graph.add_edge("training", "evaluation")
    graph.add_conditional_edges(
        "evaluation",
        route_after_evaluation,
        {"prediction": "prediction", "explainability": "explainability"},
    )
    graph.add_edge("prediction", "explainability")
    graph.add_edge("explainability", "simulation")
    graph.add_edge("simulation", "business_insight")
    graph.add_edge("business_insight", "recommendation")
    graph.add_edge("recommendation", "reporting")
    graph.add_edge("reporting", "memory")
    graph.add_edge("memory", END)

    return graph


def run_workflow(query: str, session_id: str = "default") -> WorkflowState:
    """Build, compile, and run the full workflow."""
    logger.info(f"Starting workflow for query: {query[:80]}")
    graph = build_workflow()
    app = graph.compile()
    initial_state: WorkflowState = {
        "query": query,
        "session_id": session_id,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "plan": {},
        "nodes_to_run": [],
        "intent": "general",
        "env_context": {},
        "data_sources_available": [],
        "raw_data": {},
        "validated": False,
        "validation_errors": [],
        "features": {},
        "rfm_results": {},
        "segment_results": {},
        "customer_analytics": {},
        "revenue_analytics": {},
        "campaign_analytics": {},
        "product_analytics": {},
        "ml_plan": {},
        "model_results": {},
        "champion_model": "",
        "evaluation_report": {},
        "should_train": False,
        "churn_predictions": {},
        "clv_predictions": {},
        "shap_values": {},
        "feature_importances": {},
        "simulation_results": {},
        "business_insights": "",
        "recommendations": [],
        "executive_report": "",
        "session_memory": {},
        "history": [],
        "errors": [],
        "warnings": [],
    }
    result = app.invoke(initial_state)
    logger.info("Workflow completed")
    return result
