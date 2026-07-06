from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"
    database: str = "unknown"


class WorkflowRequest(BaseModel):
    query: str = Field(..., description="Natural language business query")
    session_id: Optional[str] = Field(default="default")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    session_id: str
    query: str
    intent: Optional[str] = None
    nodes_run: Optional[List[str]] = None
    business_insights: Optional[str] = None
    recommendations: Optional[List[Dict]] = None
    executive_report: Optional[str] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    champion_model: Optional[str] = None


class DataImportRequest(BaseModel):
    data_dir: Optional[str] = None
    tables: Optional[List[str]] = None


class DataImportResponse(BaseModel):
    results: Dict[str, Any]
    total_tables: int
    successful: int
    failed: int


class AnalyticsSummaryResponse(BaseModel):
    total_customers: Optional[int] = None
    total_revenue: Optional[float] = None
    total_orders: Optional[int] = None
    avg_order_value: Optional[float] = None
    churn_rate: Optional[float] = None
    top_segments: Optional[Dict] = None
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ChurnPredictionRequest(BaseModel):
    customer_ids: Optional[List[int]] = None
    retrain: bool = False


class ChurnPredictionResponse(BaseModel):
    churn_rate: float
    total_customers: int
    churned_count: int
    high_risk_count: int
    champion_model: str
    high_risk_customers: List[Dict]


class CLVPredictionRequest(BaseModel):
    customer_ids: Optional[List[int]] = None
    retrain: bool = False


class CLVPredictionResponse(BaseModel):
    total_customers: int
    avg_clv_12m: float
    avg_clv_lifetime: float
    champion_model: str
    sample_predictions: List[Dict]


class SimulationRequest(BaseModel):
    parameters: Dict[str, float] = Field(
        ...,
        description="Parameter changes in percent, e.g. {'frequency': 10, 'monetary': 5}"
    )
    session_id: Optional[str] = None


class SimulationResponse(BaseModel):
    parameters_applied: Dict[str, float]
    results: Dict[str, Any]


class ReportResponse(BaseModel):
    report: str
    generated_at: str
