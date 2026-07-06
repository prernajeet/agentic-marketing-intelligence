from typing import TypedDict, Optional, Any, List, Dict
from datetime import datetime


class WorkflowState(TypedDict, total=False):
    # Input
    query: str
    user_id: Optional[str]
    session_id: str
    timestamp: str

    # Planning
    plan: Dict[str, Any]          # Gemini planning output
    nodes_to_run: List[str]       # which nodes are activated
    intent: str                   # e.g. 'churn_analysis', 'clv', 'rfm'

    # Context
    env_context: Dict[str, Any]
    data_sources_available: List[str]

    # Data
    raw_data: Dict[str, Any]       # DataFrames serialized as dicts
    validated: bool
    validation_errors: List[str]

    # Feature Engineering
    features: Dict[str, Any]

    # Analytics results
    rfm_results: Dict[str, Any]
    segment_results: Dict[str, Any]
    customer_analytics: Dict[str, Any]
    revenue_analytics: Dict[str, Any]
    campaign_analytics: Dict[str, Any]
    product_analytics: Dict[str, Any]

    # ML
    ml_plan: Dict[str, Any]   # Gemini ML strategy
    model_results: Dict[str, Any]
    champion_model: str
    evaluation_report: Dict[str, Any]
    should_train: bool

    # Predictions
    churn_predictions: Dict[str, Any]
    clv_predictions: Dict[str, Any]

    # Explainability
    shap_values: Dict[str, Any]
    feature_importances: Dict[str, Any]

    # Simulation
    simulation_results: Dict[str, Any]

    # Insights and recommendations
    business_insights: str
    recommendations: List[Dict[str, Any]]

    # Report
    executive_report: str

    # Memory
    session_memory: Dict[str, Any]
    history: List[Dict[str, Any]]

    # Status
    errors: List[str]
    warnings: List[str]
