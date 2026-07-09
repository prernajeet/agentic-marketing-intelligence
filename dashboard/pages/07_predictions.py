import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from config.settings import settings
from ml.churn import train_churn_model, predict_churn
from ml.clv import train_clv_model, predict_clv
from nodes.feature_engineering import feature_engineering_node
from visualizations.charts import churn_gauge

from utils.styling import apply_premium_styling

st.set_page_config(page_title="Predictions", page_icon="🔮", layout="wide")
st.title("🔮 Predictions")

# Apply styling
apply_premium_styling()

# Initialize session state keys for predictions persistence
if "churn_results" not in st.session_state:
    st.session_state.churn_results = None
if "email_copy" not in st.session_state:
    st.session_state.email_copy = None
if "clv_results" not in st.session_state:
    st.session_state.clv_results = None

tab1, tab2 = st.tabs(["Churn Prediction", "CLV Prediction"])

def load_features():
    raw_dir = settings.raw_data_path
    raw_data = {}
    for t in ["customers", "transactions", "order_items"]:
        fp = raw_dir / f"{t}.csv"
        if fp.exists():
            raw_data[t] = pd.read_csv(fp).to_dict(orient="records")
    state = {"raw_data": raw_data, "validated": True, "errors": [], "warnings": []}
    state = feature_engineering_node(state)
    return pd.DataFrame(state["features"].get("customer_features", []))

with tab1:
    st.subheader("Customer Churn Predictions")
    if st.button("Run Churn Prediction"):
        with st.spinner("Predicting churn..."):
            try:
                cf_df = load_features()
                model_results = train_churn_model(cf_df)
                result = predict_churn(cf_df, model_results)
                st.session_state.churn_results = result
                # Reset previous email copy on new run
                st.session_state.email_copy = None
            except Exception as e:
                st.error(f"Prediction error: {e}")

    if st.session_state.churn_results is not None:
        result = st.session_state.churn_results
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Churn Rate", f"{result['churn_rate']*100:.1f}%")
        col2.metric("At Risk Customers", result["churned_count"])
        col3.metric("High Risk (>70%)", result["high_risk_count"])
        
        st.plotly_chart(churn_gauge(result["churn_rate"]), use_container_width=True)
        
        with st.expander("🔍 Churn Gauge Explanations"):
            c_pe, c_tech = st.columns(2)
            c_pe.markdown("""
            **Plain English Interpretation:**
            * **What it means:** The overall percentage of registered customers flagged as inactive/churned (quiet for 90+ days).
            * **Business Target:** Keep this gauge in the green zone (<20%) through win-back re-engagement triggers.
            """)
            c_tech.markdown("""
            **Technical Implementation:**
            * **Calculation:** Divides number of users with recency > 90 by total customer count.
            * **Gauge Zones:** Green (0-20% healthy), Yellow (20-50% warning), Red (50-100% critical).
            """)
        
        st.subheader("🎯 Automated Retention Action Hub")
        # Display predictions for ALL customers instead of just the top 20 high risk ones
        preds_list = result.get("predictions", [])
        hr_df = pd.DataFrame(preds_list)
        
        cust_csv = settings.raw_data_path / "customers.csv"
        if cust_csv.exists() and not hr_df.empty:
            cust_df = pd.read_csv(cust_csv)
            hr_df = hr_df.merge(cust_df[["customer_id", "first_name", "last_name", "email"]], on="customer_id", how="left")
            hr_df["Customer Name"] = hr_df["first_name"] + " " + hr_df["last_name"]
            hr_df = hr_df[["customer_id", "Customer Name", "email", "churn_probability"]]
            hr_df = hr_df.sort_values("churn_probability", ascending=False)
        
        if not hr_df.empty:
            st.dataframe(hr_df, use_container_width=True)
            
            st.markdown("#### ⚡ Proactive Customer Re-Engagement")
            col_sel, col_act = st.columns([2, 1])
            with col_sel:
                selected_cust = st.selectbox(
                    "Select customer to target:",
                    [f"{row['Customer Name']} (ID: {row['customer_id']}) - Prob: {row['churn_probability']*100:.1f}%" for idx, row in hr_df.iterrows()]
                )
                target_id = int(selected_cust.split("(ID: ")[1].split(")")[0])
                target_row = hr_df[hr_df["customer_id"] == target_id].iloc[0]
                target_email = target_row["email"]
                target_name = target_row["Customer Name"]
                target_prob = target_row["churn_probability"]
                
            with col_act:
                st.write("") # spacing
                trigger_sync = st.button("🔗 Sync to HubSpot CRM")
                
            generate_copy = st.button("✉️ Generate Personalized Win-Back Email")
            
            if trigger_sync:
                from utils.webhooks import trigger_crm_webhook
                if trigger_crm_webhook(target_id, target_email, target_name, target_prob):
                    st.success(f"✅ Successfully triggered CRM webhook for {target_name} (ID: {target_id}). Enrolled in HubSpot Win-Back Flow!")
                    
            if generate_copy:
                with st.spinner("Generating personalized email copy via AI..."):
                    from llm.gemini_client import gemini_client
                    prompt = f"""Write a personalized win-back email to {target_name} ({target_email}) who has a {target_prob*100:.1f}% churn probability.
                    The email should be warm, offer a 15% discount code 'COMEBACK15', highlight our new arrivals, and encourage them to reactivate their account.
                    Keep it to 150-200 words, highly professional, with placeholders for sender signature."""
                    st.session_state.email_copy = gemini_client.generate(prompt)
                    
            if st.session_state.email_copy:
                st.markdown("##### 📄 Generated Email Draft")
                st.info(st.session_state.email_copy)
        else:
            st.write("No churn predictions available.")

with tab2:
    st.subheader("Customer Lifetime Value Predictions")
    if st.button("Run CLV Prediction"):
        with st.spinner("Predicting CLV..."):
            try:
                cf_df = load_features()
                model_results = train_clv_model(cf_df)
                result = predict_clv(cf_df, model_results)
                st.session_state.clv_results = result
            except Exception as e:
                st.error(f"CLV prediction error: {e}")

    if st.session_state.clv_results is not None:
        result = st.session_state.clv_results
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Customers", result["total_customers"])
        col2.metric("Avg CLV (12m)", f"${result['avg_clv_12m']:,.2f}")
        col3.metric("Avg Lifetime CLV", f"${result['avg_clv_lifetime']:,.2f}")
        st.subheader("Sample Predictions")
        st.dataframe(pd.DataFrame(result["predictions"]).head(20), use_container_width=True)
        
        with st.expander("🔍 CLV Table Explanations"):
            c_pe, c_tech = st.columns(2)
            c_pe.markdown("""
            **Plain English Interpretation:**
            * **What it means:** Forecasts the monetary value that each customer will spend over 12-month, 24-month, and lifetime horizons.
            * **Business Goal:** Directs high-cost personalized loyalty offers to Platinum (highest value) cohorts.
            """)
            c_tech.markdown("""
            **Technical Implementation:**
            * **Logic:** Extrapolates 12m forecasts through fixed multipliers (24m = ×1.8, Lifetime = ×5.0).
            * **Model:** Trains Ridge, RandomForest, GradientBoosting, XGBoost, and LightGBM; selects champion on highest test R² score.
            """)
