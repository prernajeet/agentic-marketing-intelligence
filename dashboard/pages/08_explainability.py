import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import numpy as np
from config.settings import settings
from ml.churn import train_churn_model
from nodes.feature_engineering import feature_engineering_node
from nodes.explainability import explainability_node
from visualizations.charts import feature_importance_bar
from utils.styling import apply_premium_styling

st.set_page_config(page_title="Explainability", page_icon="🔍", layout="wide")
st.title("🔍 Model Explainability")
st.markdown("SHAP values and feature importances for trained models.")

# Apply premium styling
apply_premium_styling()

def compute_local_shap(model_result, cf_df, customer_id):
    """Compute local SHAP values for a specific customer ID."""
    model = model_result.get("model")
    feature_cols = model_result.get("feature_cols")
    
    if model is None or not feature_cols:
        return None, "Model or features not found"
        
    # Find customer row
    cust_row = cf_df[cf_df["customer_id"] == customer_id]
    if cust_row.empty:
        return None, f"Customer ID {customer_id} not found in database."
        
    import shap
    try:
        X_row = cust_row[feature_cols].fillna(0)
        try:
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer.shap_values(X_row)
        except Exception:
            try:
                explainer = shap.LinearExplainer(model, cf_df[feature_cols].fillna(0))
                shap_vals = explainer.shap_values(X_row)
            except Exception:
                explainer = shap.Explainer(model, cf_df[feature_cols].fillna(0))
                shap_vals = explainer(X_row).values
        
        if hasattr(shap_vals, "values"):
            shap_vals = shap_vals.values
            
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]
            
        if not isinstance(shap_vals, np.ndarray):
            shap_vals = np.array(shap_vals)
            
        if len(shap_vals.shape) == 3:
            shap_vals = shap_vals[:, :, 1] if shap_vals.shape[2] > 1 else shap_vals[:, :, 0]
            
        row_shap = shap_vals[0].tolist()
        feature_values = X_row.iloc[0].tolist()
        
        local_contributions = {}
        for col, val, shap_val in zip(feature_cols, feature_values, row_shap):
            local_contributions[col] = {
                "value": val,
                "shap": shap_val
            }
        return local_contributions, None
    except Exception as e:
        return None, f"SHAP force calculation error: {e}"

def plot_local_shap(contributions, customer_name):
    """Draw a horizontal bar chart showing what pushed this customer to churn or stay."""
    import plotly.graph_objects as go
    
    sorted_items = sorted(contributions.items(), key=lambda x: abs(x[1]["shap"]), reverse=True)
    features = [f"{x[0]} (val: {x[1]['value']:.1f})" for x in sorted_items]
    shap_vals = [x[1]["shap"] for x in sorted_items]
    
    colors = ["#EF553B" if v > 0 else "#636EFA" for v in shap_vals]
    
    fig = go.Figure(go.Bar(
        x=shap_vals,
        y=features,
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.3f}" for v in shap_vals],
        textposition="outside",
    ))
    
    fig.update_layout(
        title=f"Personalized Retention Drivers for {customer_name}",
        xaxis_title="SHAP Value (Positive pushes to Churn, Negative pulls to Stay)",
        yaxis_title="Feature Name & Value",
        template="plotly_dark",
        yaxis={"autorange": "reversed"},
    )
    return fig

# Load raw data
raw_dir = settings.raw_data_path
raw_data = {}
for t in ["customers", "transactions"]:
    fp = raw_dir / f"{t}.csv"
    if fp.exists():
        raw_data[t] = pd.read_csv(fp).to_dict(orient="records")

state = {"raw_data": raw_data, "validated": True, "errors": [], "warnings": []}
state = feature_engineering_node(state)
features = state.get("features", {})

if "customer_features" in features:
    cf_df = pd.DataFrame(features["customer_features"])
    
    tab1, tab2 = st.tabs(["🌎 Global Explainability", "👤 Individual Customer Deep-Dive"])
    
    with tab1:
        st.markdown("### Global Model Features Analysis")
        if st.button("Compute Explainability"):
            with st.spinner("Computing SHAP values..."):
                try:
                    model_results = train_churn_model(cf_df)
                    state["model_results"] = model_results
                    state["features"] = features
                    state = explainability_node(state)
                    fi = state.get("feature_importances", {})
                    shap_vals = state.get("shap_values", {})
                    
                    for model_name, importances in fi.items():
                        st.markdown(f"#### Feature Importances — {model_name}")
                        fig = feature_importance_bar(importances, model_name)
                        fig.update_layout(title=None)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    for model_name, shap_m in shap_vals.items():
                        st.markdown(f"#### SHAP Values — {model_name}")
                        fig = feature_importance_bar(shap_m, f"{model_name} (SHAP)")
                        fig.update_layout(title=None)
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Explainability error: {e}")
                    
    with tab2:
        st.markdown("### Personalized Local Churn Explanations")
        
        # Load customer names for dropdown
        cust_csv_fp = raw_dir / "customers.csv"
        if cust_csv_fp.exists():
            cust_df = pd.read_csv(cust_csv_fp)
            cust_df["display_name"] = cust_df["first_name"] + " " + cust_df["last_name"] + " (ID: " + cust_df["customer_id"].astype(str) + ")"
            selected_cust = st.selectbox("Select Customer to Analyze:", cust_df["display_name"].tolist())
            selected_id = int(selected_cust.split("(ID: ")[1].split(")")[0])
            selected_name = selected_cust.split(" (ID:")[0]
        else:
            selected_id = st.number_input("Enter Customer ID:", min_value=1, value=1, step=1)
            selected_name = f"Customer #{selected_id}"
            
        if st.button("🔍 Run Local SHAP Analysis"):
            with st.spinner("Analyzing individual customer behavioral weights..."):
                try:
                    model_results = train_churn_model(cf_df)
                    best_name = "RandomForest"
                    if "XGBoost" in model_results:
                        best_name = "XGBoost"
                    elif len(model_results) > 0:
                        best_name = list(model_results.keys())[0]
                        
                    model_res = model_results[best_name]
                    contributions, err = compute_local_shap(model_res, cf_df, selected_id)
                    
                    if err:
                        st.error(err)
                    else:
                        st.markdown("---")
                        # Plot local SHAP chart
                        fig_local = plot_local_shap(contributions, selected_name)
                        st.plotly_chart(fig_local, use_container_width=True)
                        
                        # Interpret the SHAP values
                        st.markdown("#### 💡 Personalized Retention Diagnostic")
                        churn_pushes = [k for k, v in contributions.items() if v["shap"] > 0.02]
                        stay_pulls = [k for k, v in contributions.items() if v["shap"] < -0.02]
                        
                        diag_text = f"**Diagnostic for {selected_name}:**\n"
                        if churn_pushes:
                            diag_text += f"- ⚠️ **Risk Factors**: The primary features pushing this customer toward churn are **{', '.join(churn_pushes)}**.\n"
                        if stay_pulls:
                            diag_text += f"- ✅ **Loyalty Anchors**: The primary features anchoring this customer to the brand are **{', '.join(stay_pulls)}**.\n"
                        
                        rec_shap = contributions.get("recency_days", {}).get("shap", 0)
                        rec_val = contributions.get("recency_days", {}).get("value", 0)
                        if rec_shap > 0:
                            diag_text += f"- **Why?**: The customer has been inactive for **{rec_val:.0f} days**, which exceeds the safe threshold, causing a positive risk shift.\n"
                            
                        st.info(diag_text)
                except Exception as e:
                    st.error(f"Local explainability error: {e}")
else:
    st.warning("No features available.")
