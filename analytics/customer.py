import pandas as pd
from typing import Dict, Any


def compute_customer_analytics(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute customer-level analytics."""
    result = {}

    if "customers" not in raw_data:
        return {"error": "No customer data"}

    cust_df = pd.DataFrame(raw_data["customers"])
    result["total_customers"] = len(cust_df)
    result["active_customers"] = int(cust_df.get("is_active", pd.Series([True] * len(cust_df))).sum())

    if "gender" in cust_df.columns:
        result["gender_distribution"] = cust_df["gender"].value_counts().to_dict()

    if "country" in cust_df.columns:
        result["top_countries"] = cust_df["country"].value_counts().head(10).to_dict()

    if "registration_date" in cust_df.columns:
        cust_df["registration_date"] = pd.to_datetime(cust_df["registration_date"], errors="coerce")
        monthly = cust_df.groupby(cust_df["registration_date"].dt.to_period("M")).size()
        result["monthly_registrations"] = {str(k): int(v) for k, v in monthly.items()}

    if "transactions" in raw_data:
        txn_df = pd.DataFrame(raw_data["transactions"])
        result["customers_with_transactions"] = int(txn_df["customer_id"].nunique())

    return result


def compute_cohort_retention(raw_data: Dict[str, Any]) -> pd.DataFrame:
    """Compute monthly customer cohort retention matrix."""
    import numpy as np
    if "transactions" not in raw_data or "customers" not in raw_data:
        return pd.DataFrame()
        
    tx_df = pd.DataFrame(raw_data["transactions"])
    cust_df = pd.DataFrame(raw_data["customers"])
    
    if tx_df.empty or cust_df.empty:
        return pd.DataFrame()
        
    tx_df["transaction_date"] = pd.to_datetime(tx_df["transaction_date"], errors="coerce")
    cust_df["registration_date"] = pd.to_datetime(cust_df["registration_date"], errors="coerce")
    
    # Merge registration date into transactions
    df = tx_df.merge(cust_df[["customer_id", "registration_date"]], on="customer_id", how="inner")
    
    # Calculate cohort month and transaction month
    df["cohort_month"] = df["registration_date"].dt.to_period("M")
    df["tx_month"] = df["transaction_date"].dt.to_period("M")
    
    # Calculate difference in months
    df["month_index"] = (df["tx_month"] - df["cohort_month"]).apply(lambda x: x.n if pd.notnull(x) else np.nan)
    df = df[df["month_index"] >= 0]
    
    # Group by cohort and month index, count unique customers
    cohort_group = df.groupby(["cohort_month", "month_index"])["customer_id"].nunique().reset_index()
    
    # Pivot
    cohort_pivot = cohort_group.pivot(index="cohort_month", columns="month_index", values="customer_id")
    
    # Calculate percentage
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0)
    
    # Index to string for Plotly
    retention.index = retention.index.astype(str)
    return retention
