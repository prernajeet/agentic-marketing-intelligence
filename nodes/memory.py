# from graph.state import WorkflowState
from utils.logger import logger
from datetime import datetime


def memory_node(state: dict) -> dict:
    """Persist workflow history and key results to state memory."""
    logger.info("Memory node running")
    history_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": state.get("session_id", ""),
        "query": state.get("query", ""),
        "intent": state.get("intent", ""),
        "nodes_run": state.get("nodes_to_run", []),
        "errors": state.get("errors", []),
        "champion_model": state.get("champion_model", ""),
        "churn_rate": (state.get("churn_predictions") or {}).get("churn_rate"),
    }
    history = state.get("history", [])
    history.append(history_entry)
    state["history"] = history[-50:]  # Keep last 50 entries
    memory = state.get("session_memory") or {}
    memory["last_run"] = history_entry
    memory["total_runs"] = memory.get("total_runs", 0) + 1
    state["session_memory"] = memory
    return state
