"""
ml/local_shap.py
Compute per-customer (local) SHAP explanations for churn models.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px


def compute_local_shap(
    customer_id: str,
    customer_features: pd.DataFrame,
    model_results: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Compute local SHAP values for a single customer.

    Args:
        customer_id: The customer identifier string.
        customer_features: DataFrame of engineered customer features.
        model_results: Dict returned by ml.churn.train_churn_model.

    Returns:
        Dict with keys:
          - customer_id
          - churn_probability (float)
          - shap_dict  (feature → shap_value)
          - top_drivers (list of dicts)
          - base_value  (float)
          - fig_waterfall (Plotly Figure)
    """
    try:
        import shap  # optional dep - graceful fallback below
    except ImportError:
        return _fallback_local_importance(customer_id, customer_features, model_results)

    # Pick the champion model by ROC-AUC
    best_name, best = _pick_champion(model_results)
    if best is None:
        return None

    model = best["model"]
    feature_cols = best["feature_cols"]
    scaler = best.get("scaler")

    # Cast customer_id to match df's customer_id type
    if not customer_features.empty:
        df_id_type = customer_features["customer_id"].dtype
        if np.issubdtype(df_id_type, np.integer):
            try:
                customer_id = int(customer_id)
            except ValueError:
                pass

    cust_row = customer_features[customer_features["customer_id"] == customer_id]
    if cust_row.empty:
        return None

    X_all = customer_features[feature_cols].fillna(0)
    X_single = cust_row[feature_cols].fillna(0)

    if scaler:
        X_all = pd.DataFrame(scaler.transform(X_all), columns=feature_cols)
        X_single = pd.DataFrame(scaler.transform(X_single), columns=feature_cols)

    try:
        explainer = shap.TreeExplainer(model)
        sv = explainer.shap_values(X_single)
        base = float(explainer.expected_value) if not hasattr(explainer.expected_value, '__len__') else float(explainer.expected_value[1])
        # For binary classifiers shap_values is a list[array]
        if isinstance(sv, list):
            sv = sv[1]
        sv_arr = np.array(sv).flatten()
    except Exception:
        return _fallback_local_importance(customer_id, customer_features, model_results)

    shap_dict = {f: round(float(v), 6) for f, v in zip(feature_cols, sv_arr)}
    top_drivers = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:10]

    # Churn probability for this customer
    prob = float(model.predict_proba(cust_row[feature_cols].fillna(0))[:, 1][0])

    fig = _waterfall_chart(shap_dict, base, feature_cols, customer_id)

    return {
        "customer_id": customer_id,
        "churn_probability": round(prob, 4),
        "shap_dict": shap_dict,
        "top_drivers": [{"feature": k, "shap": v} for k, v in top_drivers],
        "base_value": round(base, 4),
        "champion_model": best_name,
        "fig_waterfall": fig,
    }


def _fallback_local_importance(customer_id, customer_features, model_results):
    """Fallback: use feature importances weighted by customer feature values."""
    best_name, best = _pick_champion(model_results)
    if best is None:
        return None

    model = best["model"]
    feature_cols = best["feature_cols"]

    cust_row = customer_features[customer_features["customer_id"] == customer_id]
    if cust_row.empty:
        return None

    prob = float(model.predict_proba(cust_row[feature_cols].fillna(0))[:, 1][0])

    # Feature importance * normalised feature value
    try:
        fi = model.feature_importances_
    except AttributeError:
        fi = np.abs(model.coef_[0]) if hasattr(model, "coef_") else np.ones(len(feature_cols))

    vals = cust_row[feature_cols].fillna(0).values.flatten()
    pseudo_shap = fi * vals
    shap_dict = {f: round(float(v), 6) for f, v in zip(feature_cols, pseudo_shap)}
    top_drivers = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:10]

    fig = _waterfall_chart(shap_dict, 0.0, feature_cols, customer_id)

    return {
        "customer_id": customer_id,
        "churn_probability": round(prob, 4),
        "shap_dict": shap_dict,
        "top_drivers": [{"feature": k, "shap": v} for k, v in top_drivers],
        "base_value": 0.0,
        "champion_model": best_name,
        "fig_waterfall": fig,
    }


def _pick_champion(model_results):
    best_name, best, best_auc = None, None, -1
    for name, res in model_results.items():
        auc = res.get("metrics", {}).get("roc_auc", 0)
        if auc > best_auc:
            best_auc, best_name, best = auc, name, res
    return best_name, best


def _waterfall_chart(shap_dict: dict, base: float, feature_cols, customer_id: str) -> go.Figure:
    top = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
    features = [t[0] for t in top]
    values = [t[1] for t in top]
    colors = ["#ef4444" if v > 0 else "#10b981" for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.4f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"SHAP Drivers for Customer {customer_id}",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        xaxis_title="SHAP Value (impact on churn probability)",
        yaxis=dict(autorange="reversed"),
        height=420,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig
