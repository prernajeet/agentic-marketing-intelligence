import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Dict, Any


def compute_segmentation(customer_features: pd.DataFrame, n_clusters: int = 5) -> Dict[str, Any]:
    """K-Means customer segmentation on numeric customer features."""
    df = customer_features.copy()
    feature_cols = ["recency_days", "frequency", "monetary", "avg_order_value"]
    feature_cols = [c for c in feature_cols if c in df.columns]

    if not feature_cols:
        return {"error": "No segmentation features available"}

    X = df[feature_cols].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_clusters = min(n_clusters, len(df))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    df["segment_cluster"] = labels

    cluster_profiles = df.groupby("segment_cluster")[feature_cols].mean().round(2)

    segment_labels = {}
    for cluster_id, row in cluster_profiles.iterrows():
        recency = row.get("recency_days", 999)
        frequency = row.get("frequency", 0)
        monetary = row.get("monetary", 0)
        
        # 1. Inactive / Churned (over 180 days of silence)
        if recency > 180:
            if monetary > 500:
                label = "Lost High Spenders (Churned)"
            else:
                label = "Inactive / Churned"
        # 2. At Risk (90 to 180 days of silence)
        elif recency > 90:
            if monetary > 500:
                label = "At Risk High Spenders"
            else:
                label = "At Risk / Slipping"
        # 3. High Value Active
        elif recency <= 45 and frequency > 4 and monetary > 500:
            label = "High-Value Active (Champions)"
        # 4. Active Regulars
        elif recency <= 90 and frequency > 2 and monetary > 300:
            label = "Regular Spenders (Active)"
        elif recency <= 90 and frequency > 2:
            label = "Regular Buyers"
        # 5. Low frequency but high ticket
        elif monetary > 300:
            label = "Occasional High Spenders"
        # 6. Fallback
        else:
            label = "Low-Spend / New Customers"
            
        segment_labels[cluster_id] = label

    df["segment_label"] = df["segment_cluster"].map(segment_labels)

    return {
        "segments": df[["customer_id", "segment_cluster", "segment_label"] + feature_cols].to_dict(orient="records"),
        "segment_counts": df["segment_label"].value_counts().to_dict(),
        "cluster_profiles": cluster_profiles.to_dict(),
        "segment_labels": segment_labels,
        "inertia": float(kmeans.inertia_),
        "n_clusters": n_clusters,
    }
