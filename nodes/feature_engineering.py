import pandas as pd
import numpy as np
from datetime import datetime
# from graph.state import WorkflowState
from utils.logger import logger


def feature_engineering_node(state: dict) -> dict:
    """Engineer features from raw data for analytics and ML."""
    logger.info("Feature engineering node running")
    raw_data = state.get("raw_data", {})
    features = {}

    try:
        # Build customer-level feature table
        if "transactions" in raw_data and "customers" in raw_data:
            txn_df = pd.DataFrame(raw_data["transactions"])
            cust_df = pd.DataFrame(raw_data["customers"])

            txn_df["transaction_date"] = pd.to_datetime(txn_df["transaction_date"], errors="coerce")
            txn_df["total_amount"] = pd.to_numeric(txn_df["total_amount"], errors="coerce")

            reference_date = txn_df["transaction_date"].max()

            customer_features = txn_df.groupby("customer_id").agg(
                recency_days=("transaction_date", lambda x: (reference_date - x.max()).days),
                frequency=("transaction_id", "count"),
                monetary=("total_amount", "sum"),
                avg_order_value=("total_amount", "mean"),
                std_order_value=("total_amount", "std"),
                last_purchase_date=("transaction_date", "max"),
                first_purchase_date=("transaction_date", "min"),
            ).reset_index()

            customer_features["customer_lifetime_days"] = (
                customer_features["last_purchase_date"] - customer_features["first_purchase_date"]
            ).dt.days

            customer_features["purchase_rate"] = (
                customer_features["frequency"] /
                (customer_features["customer_lifetime_days"].replace(0, 1))
            )

            # Merge with customer demographics
            if "registration_date" in cust_df.columns:
                cust_df["registration_date"] = pd.to_datetime(cust_df["registration_date"], errors="coerce")
                cust_df["customer_age_days"] = (reference_date - cust_df["registration_date"]).dt.days
                customer_features = customer_features.merge(
                    cust_df[["customer_id", "gender", "country", "customer_age_days"]],
                    on="customer_id", how="left"
                )

            customer_features = customer_features.fillna(0)
            features["customer_features"] = customer_features.to_dict(orient="records")
            features["reference_date"] = str(reference_date)
            logger.info(f"Customer features engineered: {len(customer_features)} customers")

    except Exception as e:
        logger.error(f"Feature engineering error: {e}")
        state["errors"] = state.get("errors", []) + [f"Feature engineering: {e}"]

    state["features"] = features
    return state
