"""
config/constants.py
=====================
Static constants, enums and fixed values shared across the platform.
Keeping these centralized avoids magic strings scattered through
nodes, analytics, and ml modules.
"""

from enum import Enum


class NodeName(str, Enum):
    """Canonical names of every LangGraph node in the workflow."""

    PLANNING = "planning_node"
    CONTEXT = "context_node"
    DATA_RETRIEVAL = "data_retrieval_node"
    DATA_VALIDATION = "data_validation_node"
    FEATURE_ENGINEERING = "feature_engineering_node"
    ANALYTICS = "analytics_node"
    ML_STRATEGY = "ml_strategy_node"
    MODEL_TRAINING = "model_training_node"
    MODEL_EVALUATION = "model_evaluation_node"
    DECISION = "decision_node"
    PREDICTION = "prediction_node"
    EXPLAINABILITY = "explainability_node"
    SIMULATION = "simulation_node"
    BUSINESS_INSIGHT = "business_insight_node"
    RECOMMENDATION = "recommendation_node"
    REPORTING = "reporting_node"
    MEMORY = "memory_node"


class BusinessDomain(str, Enum):
    """Business context categories the Context Node can classify a request into."""

    CUSTOMER = "customer"
    CAMPAIGN = "campaign"
    REVENUE = "revenue"
    PRODUCT = "product"
    MARKETING = "marketing"
    GENERAL = "general"


class MLTaskType(str, Enum):
    """ML strategy categories chosen by the ML Strategy Node."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"


class ModelName(str, Enum):
    """Supported model algorithms across the ML layer."""

    LOGISTIC_REGRESSION = "logistic_regression"
    DECISION_TREE = "decision_tree"
    RANDOM_FOREST = "random_forest"
    EXTRA_TREES = "extra_trees"
    ADABOOST = "adaboost"
    KNN = "knn"
    SVM = "svm"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CATBOOST = "catboost"
    HIST_GRADIENT_BOOSTING = "hist_gradient_boosting"
    KMEANS = "kmeans"


class DatasetName(str, Enum):
    """Canonical dataset identifiers loaded by the Data Retrieval Node."""

    CUSTOMERS = "customers"
    TRANSACTIONS = "transactions"
    PRODUCTS = "products"
    CATEGORIES = "categories"
    CAMPAIGNS = "campaigns"
    CAMPAIGN_RESPONSES = "campaign_responses"
    WEBSITE_SESSIONS = "website_sessions"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    ORDER_ITEMS = "order_items"
    SUPPLIERS = "suppliers"


class ReportFormat(str, Enum):
    """Supported executive report output formats."""

    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "markdown"


# Evaluation metrics tracked by the Model Evaluation Node
CLASSIFICATION_METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc"]
REGRESSION_METRICS = ["mae", "rmse", "r2"]
CLUSTERING_METRICS = ["silhouette_score", "davies_bouldin_score", "calinski_harabasz_score"]

# Default cross-validation folds used in Model Evaluation Node
DEFAULT_CV_FOLDS = 5

# Random state for reproducibility across all ML modules
RANDOM_STATE = 42
