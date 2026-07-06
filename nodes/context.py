# from graph.state import WorkflowState
from utils.logger import logger
from config.settings import settings
from pathlib import Path


def context_node(state: dict) -> dict:
    """Gather context: available data sources, environment."""
    logger.info("Context node running")
    raw_dir = settings.raw_data_path
    available = []
    for csv_file in raw_dir.glob("*.csv"):
        available.append(csv_file.stem)
    state["data_sources_available"] = available
    state["env_context"] = {
        "raw_data_dir": str(raw_dir),
        "available_tables": available,
        "environment": "production",
    }
    logger.info(f"Available data sources: {available}")
    return state
