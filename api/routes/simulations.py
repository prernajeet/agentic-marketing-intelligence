from fastapi import APIRouter, HTTPException
from api.schemas import SimulationRequest, SimulationResponse
from graph.workflow import run_workflow
from utils.logger import logger
import uuid

router = APIRouter(prefix="/api/v1/simulations", tags=["Simulations"])


@router.post("/what-if", response_model=SimulationResponse)
def what_if_simulation(request: SimulationRequest):
    """Run a what-if simulation with parameter changes."""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        query = f"Run a what-if simulation with parameters: {request.parameters}"
        # Inject simulation params into context via query
        result = run_workflow(query=query, session_id=session_id)
        sim_results = result.get("simulation_results", {"message": "Simulation completed"})
        return SimulationResponse(
            parameters_applied=request.parameters,
            results=sim_results,
        )
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
