import pandas as pd
from typing import Dict, Any


def compute_revenue_analytics(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute revenue analytics from transaction data."""
    if "transactions" not in raw_data:
        return {"error": "No transaction data"}

    txn_df = pd.DataFrame(raw_data["transactions"])
    txn_df["transaction_date"] = pd.to_datetime(txn_df["transaction_date"], errors="coerce")
    txn_df["total_amount"] = pd.to_numeric(txn_df["total_amount"], errors="coerce")

    total_revenue = float(txn_df["total_amount"].sum())
    avg_order = float(txn_df["total_amount"].mean())
    total_orders = len(txn_df)

    monthly = txn_df.groupby(txn_df["transaction_date"].dt.to_period("M"))["total_amount"].sum()
    monthly_revenue = {str(k): round(float(v), 2) for k, v in monthly.items()}

    result = {
        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "avg_order_value": round(avg_order, 2),
            "revenue_per_customer": round(total_revenue / max(txn_df["customer_id"].nunique(), 1), 2),
        },
        "monthly_revenue": monthly_revenue,
    }

    if "payment_method" in txn_df.columns:
        result["revenue_by_payment"] = txn_df.groupby("payment_method")["total_amount"].sum().round(2).to_dict()

    if "channel" in txn_df.columns:
        result["revenue_by_channel"] = txn_df.groupby("channel")["total_amount"].sum().round(2).to_dict()

    return result
