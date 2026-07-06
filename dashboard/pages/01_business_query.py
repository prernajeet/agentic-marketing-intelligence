import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from graph.workflow import run_workflow
from utils.styling import apply_premium_styling, page_header, section_header, glass_card

st.set_page_config(page_title="Business Query", page_icon="💬", layout="wide")
page_header("💬", "Business Query", "Ask a natural language question and let the AI agent orchestrate the full analytics workflow.")

# Use session state to persist query across reruns
if "biz_query_text" not in st.session_state:
    st.session_state.biz_query_text = ""

query = st.text_area(
    "Enter your business question:",
    value=st.session_state.biz_query_text,
    placeholder="e.g. Which customers are most likely to churn next month and what should we do about it?",
    height=120,
    key="biz_query_input",
)
# Always sync back to session state immediately
st.session_state.biz_query_text = query

run_btn = st.button("🚀 Run Analysis", use_container_width=False)

if run_btn and query.strip():
    with st.spinner("Running AI workflow... This may take a moment."):
        try:
            result = run_workflow(query=query)
            st.success("✅ Workflow completed!")

            if result.get("intent"):
                st.info(f"**Detected Intent:** {result['intent']}")

            if result.get("business_insights"):
                with st.expander("📊 Business Insights", expanded=True):
                    st.markdown(result["business_insights"])

            import pandas as pd
            from config.settings import settings

            if result.get("churn_predictions") and result.get("intent") in ["churn", "general"]:
                with st.expander("🎯 Predicted High-Risk Churn Customers", expanded=True):
                    preds_info = result["churn_predictions"]
                    st.metric("Total High-Risk Customers (Prob > 70%)", preds_info.get("high_risk_count", 0))
                    high_risk = preds_info.get("high_risk_customers", [])
                    if high_risk:
                        hr_df = pd.DataFrame(high_risk)
                        raw_dir = settings.raw_data_path
                        cust_fp = raw_dir / "customers.csv"
                        if cust_fp.exists():
                            cust_df = pd.read_csv(cust_fp)
                            hr_df = hr_df.merge(cust_df[["customer_id", "first_name", "last_name", "email"]], on="customer_id", how="left")
                            hr_df["Customer Name"] = hr_df["first_name"] + " " + hr_df["last_name"]
                            hr_df = hr_df[["customer_id", "Customer Name", "email", "churn_probability"]]
                            hr_df = hr_df.sort_values("churn_probability", ascending=False)
                        st.dataframe(hr_df, use_container_width=True)
                    else:
                        st.write("No high-risk churn customers identified.")

            if result.get("clv_predictions") and result.get("intent") in ["clv", "general"]:
                with st.expander("💎 Top Predicted CLV (Customer Lifetime Value) Customers", expanded=True):
                    preds_info = result["clv_predictions"]
                    predictions = preds_info.get("predictions", [])
                    if predictions:
                        clv_df = pd.DataFrame(predictions).sort_values("clv_12m", ascending=False).head(20)
                        raw_dir = settings.raw_data_path
                        cust_fp = raw_dir / "customers.csv"
                        if cust_fp.exists():
                            cust_df = pd.read_csv(cust_fp)
                            clv_df = clv_df.merge(cust_df[["customer_id", "first_name", "last_name", "email"]], on="customer_id", how="left")
                            clv_df["Customer Name"] = clv_df["first_name"] + " " + clv_df["last_name"]
                            clv_df = clv_df[["customer_id", "Customer Name", "email", "clv_12m"]]
                        st.dataframe(clv_df, use_container_width=True)
                    else:
                        st.write("No CLV predictions available.")

            # Model Transparency & Selection Justification
            if result.get("intent") in ["churn", "clv", "general"]:
                with st.expander("🎯 ML Model Selection & Justification", expanded=True):
                    if result.get("churn_predictions") and result.get("intent") in ["churn", "general"]:
                        champion = result["churn_predictions"].get("champion_model", "XGBoost")
                        st.success(f"🤖 **Selected Champion Model for Churn: {champion}**")
                        st.markdown(f"""
                        **Business & Technical Justification for using {champion}:**
                        - **Class Separation**: {champion} uses an ensemble of gradient-boosted decision trees, which excels at handling imbalanced classes (since churners represent a small minority of the base).
                        - **Financial Precision**: It optimizes the Area Under the ROC Curve (ROC-AUC), ensuring we capture maximum churners (high recall) while minimizing marketing waste on customers who would have stayed anyway (high precision).
                        - **Feature Interaction**: It natively captures complex, non-linear relationships (e.g. how a combined drop in shopping frequency and drop in order size drastically accelerates churn probability).
                        """)
                    if result.get("clv_predictions") and result.get("intent") in ["clv", "general"]:
                        champion = result["clv_predictions"].get("champion_model", "RandomForest")
                        st.success(f"🤖 **Selected Champion Model for CLV: {champion}**")
                        st.markdown(f"""
                        **Business & Technical Justification for using {champion}:**
                        - **Handling Outliers**: Customer Lifetime Value is typically skewed by high-value VIP spenders. {champion} (RandomForest Regressor) averages predictions over multiple decision trees, which natively bounds outlier variance and prevents model bias.
                        - **Decision Stability**: By using bootstrap aggregation (bagging), it prevents local noise in recent transactions from skewing the long-term 12-month value forecast, securing stable ROI metrics for budget planning.
                        """)

            if result.get("recommendations"):
                with st.expander("💡 Recommendations"):
                    for reco in result["recommendations"]:
                        st.markdown(f"**{reco.get('title')}** (Priority: {reco.get('priority')})")
                        st.markdown(reco.get("description", ""))
                        if reco.get("actions"):
                            for action in reco["actions"]:
                                st.markdown(f"  - {action}")
                        st.markdown("---")

            if result.get("executive_report"):
                with st.expander("📄 Executive Report"):
                    st.markdown(result["executive_report"])

            if result.get("errors"):
                with st.expander("⚠️ Errors"):
                    for err in result["errors"]:
                        st.error(err)
        except Exception as e:
            st.error(f"Workflow error: {e}")

elif run_btn:
    st.warning("⚠️ Please enter a business question before running the analysis.")
