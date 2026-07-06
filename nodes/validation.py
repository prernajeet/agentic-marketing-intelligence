import pandas as pd
# from graph.state import WorkflowState
from utils.logger import logger


REQUIRED_COLUMNS = {
    "customers": ["customer_id", "email"],
    "transactions": ["transaction_id", "customer_id", "transaction_date", "total_amount"],
    "order_items": ["order_item_id", "transaction_id", "product_id", "quantity", "unit_price"],
    "products": ["product_id", "product_name", "unit_price"],
}


def validation_node(state: dict) -> dict:
    """Validate data quality and required columns."""
    logger.info("Validation node running")
    raw_data = state.get("raw_data") or {}
    errors = []
    warnings = []

    for table, required_cols in REQUIRED_COLUMNS.items():
        if table not in raw_data:
            warnings.append(f"Table {table} not loaded")
            continue
        df = pd.DataFrame(raw_data[table])
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"{table}: missing columns {missing}")
        
        # Only check nulls on columns that are actually present to avoid KeyError
        present_cols = [c for c in required_cols if c in df.columns]
        if present_cols:
            null_counts = df[present_cols].isnull().sum()
            for col, cnt in null_counts.items():
                if cnt > 0:
                    warnings.append(f"{table}.{col}: {cnt} nulls")

    state["validation_errors"] = errors
    state["warnings"] = state.get("warnings", []) + warnings
    state["validated"] = len(errors) == 0
    logger.info(f"Validation: {'PASS' if state['validated'] else 'FAIL'} — {errors}")
    return state
