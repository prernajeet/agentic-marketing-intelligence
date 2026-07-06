from fastapi import APIRouter, HTTPException
from api.schemas import WorkflowRequest, WorkflowResponse
from graph.workflow import run_workflow
from utils.logger import logger
import uuid

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])


@router.post("/run", response_model=WorkflowResponse)
def run_workflow_endpoint(request: WorkflowRequest):
    """Run the full LangGraph marketing analytics workflow."""
    session_id = request.session_id or str(uuid.uuid4())
    logger.info(f"Workflow request: {request.query[:80]}")
    try:
        result = run_workflow(query=request.query, session_id=session_id)
        return WorkflowResponse(
            session_id=session_id,
            query=request.query,
            intent=result.get("intent"),
            nodes_run=result.get("nodes_to_run", []),
            business_insights=result.get("business_insights"),
            recommendations=result.get("recommendations"),
            executive_report=result.get("executive_report"),
            errors=result.get("errors", []),
            warnings=result.get("warnings", []),
            champion_model=result.get("champion_model"),
        )
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
