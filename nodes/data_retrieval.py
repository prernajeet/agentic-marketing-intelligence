import pandas as pd
from pathlib import Path
# from graph.state import WorkflowState
from utils.logger import logger
from config.settings import settings


def data_retrieval_node(state: dict) -> dict:
    """Load CSV data into state as dicts of records."""
    logger.info("Data retrieval node running")
    data_sources = state.get("plan", {}).get("data_sources", [])
    if not data_sources:
        data_sources = ["customers", "transactions", "order_items", "products"]

    raw_data = {}
    raw_dir = settings.raw_data_path

    for source in data_sources:
        filepath = raw_dir / f"{source}.csv"
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                raw_data[source] = df.to_dict(orient="records")
                logger.info(f"Loaded {source}: {len(df)} rows")
            except Exception as e:
                logger.error(f"Error reading {source}: {e}")
                state["errors"] = state.get("errors", []) + [f"Data retrieval {source}: {e}"]
        else:
            logger.warning(f"File not found: {filepath}")
            state["warnings"] = state.get("warnings", []) + [f"{source}.csv not found"]

    state["raw_data"] = raw_data
    return state
