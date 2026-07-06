import pandas as pd
import numpy as np
from typing import Dict, Any


def compute_rfm(customer_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute RFM scores from customer features DataFrame.
    Expects columns: customer_id, recency_days, frequency, monetary
    """
    df = customer_features.copy()
    required = ["customer_id", "recency_days", "frequency", "monetary"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Score recency (lower days = higher score)
    df["recency_score"] = pd.qcut(df["recency_days"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    df["frequency_score"] = pd.qcut(df["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    df["monetary_score"] = pd.qcut(df["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    df["rfm_score"] = df["recency_score"] + df["frequency_score"] + df["monetary_score"]

    # Segment labels
    def label_segment(row):
        r, f, m = row["recency_score"], row["frequency_score"], row["monetary_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 4 and f >= 3:
            return "Loyal Customers"
        elif r >= 3 and f <= 2:
            return "Potential Loyalists"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2 and m <= 2:
            return "Lost Customers"
        elif r >= 4 and f == 1:
            return "New Customers"
        elif r >= 3:
            return "Promising"
        else:
            return "Need Attention"

    df["rfm_segment"] = df.apply(label_segment, axis=1)

    segment_dist = df["rfm_segment"].value_counts().to_dict()
    segment_monetary = df.groupby("rfm_segment")["monetary"].mean().round(2).to_dict()

    return {
        "scores": df[["customer_id", "recency_score", "frequency_score", "monetary_score",
                       "rfm_score", "rfm_segment"]].to_dict(orient="records"),
        "segment_distribution": segment_dist,
        "segment_avg_monetary": segment_monetary,
        "total_customers": len(df),
        "avg_rfm_score": float(df["rfm_score"].mean()),
        "champions_count": int(segment_dist.get("Champions", 0)),
        "at_risk_count": int(segment_dist.get("At Risk", 0)),
    }
