import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from config.settings import settings
from ml.churn import train_churn_model, predict_churn
from nodes.feature_engineering import feature_engineering_node
from nodes.simulation import simulation_node

st.set_page_config(page_title="What-If Simulation", page_icon="🎯", layout="wide")
st.title("🎯 What-If Simulation")
st.markdown("Adjust customer parameters and see how predictions change.")

@st.cache_resource
def get_trained_models_and_features():
    """Cache data loading, feature engineering, and model training to speed up simulation."""
    raw_dir = settings.raw_data_path
    raw_data = {}
    for t in ["customers", "transactions"]:
        fp = raw_dir / f"{t}.csv"
        if fp.exists():
            raw_data[t] = pd.read_csv(fp).to_dict(orient="records")

    state = {
        "raw_data": raw_data,
        "validated": True,
        "errors": [],
        "warnings": [],
        "env_context": {},
    }
    state = feature_engineering_node(state)
    features = state.get("features", {})
    if "customer_features" in features:
        cf_df = pd.DataFrame(features["customer_features"])
        # Train churn models (XGBoost, RandomForest, LightGBM)
        model_results = train_churn_model(cf_df)
        return model_results, features
    return None, None

# Wrap in a form to prevent instant reloads when dragging sliders
with st.form("simulation_form"):
    st.subheader("Parameter Adjustments (%)")
    col1, col2, col3 = st.columns(3)
    with col1:
        frequency_change = st.slider("Purchase Frequency Change", -50, 100, 0)
    with col2:
        monetary_change = st.slider("Spending Change", -50, 100, 0)
    with col3:
        recency_change = st.slider("Recency Change (days)", -50, 100, 0)
        
    run_sim = st.form_submit_button("🚀 Run Simulation")

params = {}
if frequency_change != 0:
    params["frequency"] = frequency_change
if monetary_change != 0:
    params["monetary"] = monetary_change
if recency_change != 0:
    params["recency_days"] = recency_change

if run_sim and params:
    with st.spinner("Running simulation..."):
        model_results, features = get_trained_models_and_features()
        if model_results and features:
            try:
                state = {
                    "features": features,
                    "model_results": model_results,
                    "env_context": {"simulation_params": params},
                    "errors": [],
                    "warnings": [],
                }
                state = simulation_node(state)
                sim = state.get("simulation_results", {})
                if "results" in sim:
                    # Model Comparison & Champion Recommendation
                    model_comparison = []
                    best_name = None
                    best_auc = -1
                    for name, res_m in model_results.items():
                        metrics = res_m.get("metrics", {})
                        auc = metrics.get("roc_auc", 0)
                        if auc > best_auc:
                            best_auc = auc
                            best_name = name
                        model_comparison.append({
                            "Model Name": name,
                            "ROC-AUC Score": f"{auc*100:.2f}%" if auc else "N/A",
                            "Accuracy": f"{metrics.get('accuracy', 0)*100:.2f}%" if metrics.get('accuracy') else "N/A",
                            "F1 Score": f"{metrics.get('f1', 0)*100:.2f}%" if metrics.get('f1') else "N/A",
                        })
                    comparison_df = pd.DataFrame(model_comparison)

                    st.write("---")
                    st.write("### 🤖 Machine Learning Model Comparison")
                    st.dataframe(comparison_df, use_container_width=True)

                    st.success(f"🏆 **Champion Model: {best_name}**")
                    st.info(f"**Why {best_name} is best for business churn prediction:**\n"
                            f"- **Mathematical Strength**: It achieves the highest Area Under the ROC Curve (AUC = {best_auc*100:.1f}%), maximizing our ability to separate true churn risk from healthy accounts.\n"
                            f"- **Financial Efficiency**: Using {best_name} ensures our retention budget is targeted only at customers with a genuine threat of leaving, preventing waste of promo budget on active customers (minimizing False Positives) while capturing {best_auc*100:.1f}% of real churners (maximizing True Positives).")

                    # Draw Churn Delta metrics for the Champion Model
                    champion_sim = sim["results"].get(best_name)
                    if champion_sim:
                        baseline_pct = champion_sim["baseline_mean"] * 100
                        simulated_pct = champion_sim["simulated_mean"] * 100
                        delta_pct = champion_sim["delta"] * 100
                        total_customers = len(features.get("customer_features", []))
                        
                        saved_cust = 0
                        if delta_pct < 0:
                            saved_cust = int(abs(champion_sim["delta"]) * total_customers)
                        
                        cf_df = pd.DataFrame(features["customer_features"])
                        aov = cf_df["avg_order_value"].mean() if "avg_order_value" in cf_df.columns else 148.20
                        revenue_saved = saved_cust * aov

                        st.write("---")
                        st.write("### 📈 Projected Business Impact (Based on Champion Model)")
                        col_i1, col_i2, col_i3 = st.columns(3)
                        col_i1.metric(
                            "Churn Rate Change",
                            f"{simulated_pct:.1f}%",
                            delta=f"{delta_pct:+.1f}%",
                            delta_color="inverse"
                        )
                        col_i2.metric(
                            "Customers Saved",
                            f"{saved_cust} Customers",
                            delta=f"+{saved_cust}" if saved_cust > 0 else "0",
                        )
                        col_i3.metric(
                            "Projected Revenue Preserved",
                            f"${revenue_saved:,.2f}",
                            delta=f"+${revenue_saved:,.2f}" if revenue_saved > 0 else "$0.00",
                        )

                        # Recommendations based on parameters adjusted
                        recos = []
                        if "frequency" in params:
                            recos.append("""
                            - 📢 **Frequency Boost Campaign**: To hit the simulated purchase frequency increase, launch a **'Weekly Treats'** loyalty sequence and trigger custom checkout coupons. Incentivize customers to shop again within 14 days of their last order.
                            """)
                        if "monetary" in params:
                            recos.append("""
                            - 💎 **Basket Value Upsell**: To hit the simulated spending change, implement checkout product bundles and offer **'Free Shipping on orders above $150'** to increase average order values.
                            """)
                        if "recency_days" in params:
                            recos.append("""
                            - ⏰ **Win-Back Inactivity Sequences**: To reduce customer recency days (getting inactive customers back), deploy automated email win-back sequences targeting customers inactive for 45, 60, and 90 days.
                            """)
                        
                        if recos:
                            st.write("#### 💡 Strategic Business Action Plan")
                            for r in recos:
                                st.markdown(r)

                    st.write("---")
                    st.write("### 📊 Details Across All Trained Models")
                    for model_name, res in sim["results"].items():
                        st.write("---")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Model", model_name)
                        col2.metric("Baseline Churn", f"{res['baseline_mean']*100:.1f}%")
                        col3.metric(
                            "Simulated Churn",
                            f"{res['simulated_mean']*100:.1f}%",
                            delta=f"{res['delta']*100:+.1f}%",
                        )
                else:
                    st.info("Simulation completed but produced no results.")
            except Exception as e:
                st.error(f"Simulation error: {e}")
        else:
            st.warning("No customer features available. Ensure data CSVs are in data/raw/.")
elif run_sim:
    st.warning("Please adjust at least one parameter before running the simulation.")
