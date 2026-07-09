"""
dashboard/pages/20_customer_explainability.py
Per-customer Local SHAP Explainability — "Why will THIS customer churn?"
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from config.settings import settings
from utils.styling import apply_premium_styling, page_header, section_header, glass_card, kpi_row

st.set_page_config(page_title="Customer Explainability", page_icon="🔎", layout="wide")
page_header("🔎", "Customer-Level Explainability", "Discover WHY a specific customer is likely to churn using AI-powered local SHAP analysis.")

@st.cache_resource(show_spinner=False)
def load_model_and_data():
    try:
        from ml.churn import train_churn_model
        from nodes.feature_engineering import feature_engineering_node

        raw_dir = settings.raw_data_path
        raw_data = {}
        for table in ["customers", "transactions", "order_items", "products"]:
            fp = raw_dir / f"{table}.csv"
            if fp.exists():
                raw_data[table] = pd.read_csv(fp).to_dict(orient="records")

        if not raw_data:
            return None, None, None

        state = {"raw_data": raw_data, "validated": True, "errors": [], "warnings": []}
        state = feature_engineering_node(state)
        cf_df = pd.DataFrame(state.get("features", {}).get("customer_features", []))

        if cf_df.empty:
            return None, None, None

        model_results = train_churn_model(cf_df)
        return model_results, cf_df, raw_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None


# ── Sidebar controls ────────────────────────────────────────────────────────
st.sidebar.markdown("### 🔎 Customer Lookup")
with st.sidebar:
    customer_input = st.text_input(
        "Enter Customer ID:",
        placeholder="e.g. CUST_0001",
        help="Type a customer ID from your database to get a personal churn explanation."
    )
    analyze_btn = st.button("🚀 Analyze Customer", use_container_width=True)

# ── Main content ────────────────────────────────────────────────────────────
section_header("📋", "How It Works", badge="AI POWERED")
glass_card("""
<p style='color:#94a3b8; margin:0;'>
Unlike <strong>global</strong> feature importance (which shows what drives churn across <em>all</em> customers),
this page uses <strong>Local SHAP</strong> to answer the specific question:
<em>"For <u>this particular customer</u>, which behaviours push their churn risk up — and which protect them?"</em><br><br>
Each bar in the chart represents a feature's individual contribution to that customer's predicted churn probability.
<span style='color:#ef4444'>Red bars ▶ increase churn risk.</span>
<span style='color:#10b981'>Green bars ▶ reduce churn risk.</span>
</p>
""")

if analyze_btn and customer_input.strip():
    with st.spinner("🤖 Training models & computing SHAP explanations…"):
        model_results, cf_df, raw_data = load_model_and_data()

    if model_results is None or cf_df is None:
        st.error("❌ Could not load data. Please ensure CSV files are present.")
        st.stop()

    from ml.local_shap import compute_local_shap
    result = compute_local_shap(customer_input.strip(), cf_df, model_results)

    if result is None:
        st.warning(f"⚠️ Customer ID **{customer_input}** not found. Please check the ID and try again.")

        # Show sample IDs
        st.markdown("**Available Customer IDs (sample):**")
        sample_ids = cf_df["customer_id"].head(10).tolist()
        st.code(", ".join(sample_ids))
    else:
        prob = result["churn_probability"]
        risk_color = "#ef4444" if prob > 0.7 else "#f59e0b" if prob > 0.4 else "#10b981"
        risk_label = "🔴 HIGH RISK" if prob > 0.7 else "🟡 MEDIUM RISK" if prob > 0.4 else "🟢 LOW RISK"

        # ── KPI row ──────────────────────────────────────────────────────────
        kpi_row([
            {"label": "Churn Probability", "value": f"{prob*100:.1f}%", "delta": risk_label, "positive": prob < 0.5},
            {"label": "Risk Level", "value": risk_label.split()[1] + " " + risk_label.split()[2], "positive": prob < 0.5},
            {"label": "Champion Model", "value": result["champion_model"], "positive": True},
            {"label": "Base Rate (avg)", "value": f"{result['base_value']*100:.1f}%" if result['base_value'] else "N/A", "positive": True},
        ])

        # ── Customer profile ─────────────────────────────────────────────────
        if raw_data and "customers" in raw_data:
            cust_df_raw = pd.DataFrame(raw_data["customers"])
            cust_row = cust_df_raw[cust_df_raw["customer_id"] == customer_input.strip()]
            if not cust_row.empty:
                row = cust_row.iloc[0]
                section_header("👤", "Customer Profile")
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"**Name:** {row.get('first_name','')} {row.get('last_name','')}")
                col2.markdown(f"**Email:** {row.get('email', 'N/A')}")
                col3.markdown(f"**Country:** {row.get('country', 'N/A')}")

        # ── SHAP Waterfall Chart ─────────────────────────────────────────────
        section_header("📊", "SHAP Explanation Chart", badge="LOCAL SHAP")
        st.plotly_chart(result["fig_waterfall"], use_container_width=True)
        
        with st.expander("🔍 SHAP Waterfall Chart Explanations"):
            c_pe, c_tech = st.columns(2)
            c_pe.markdown("""
            **Plain English Interpretation:**
            * **Red bars (pointing right):** Customer behaviors that increase their likelihood of leaving.
            * **Blue/Green bars (pointing left):** Customer behaviors that make them more likely to stay.
            """)
            c_tech.markdown("""
            **Technical Implementation:**
            * **Logic:** Renders a horizontal bar chart mapping SHAP values relative to the database average (base value).
            * **SHAP Library:** Leverages TreeExplainer / Explainer outputs generated by the python explainability node.
            """)

        # ── Top drivers table ────────────────────────────────────────────────
        section_header("🔑", "Top Churn Drivers for This Customer")
        drivers_df = pd.DataFrame(result["top_drivers"])
        drivers_df["Direction"] = drivers_df["shap"].apply(
            lambda v: "⬆️ Increases Churn" if v > 0 else "⬇️ Reduces Churn"
        )
        drivers_df["SHAP Value"] = drivers_df["shap"].round(4)
        drivers_df["Feature"] = drivers_df["feature"]
        st.dataframe(
            drivers_df[["Feature", "SHAP Value", "Direction"]],
            use_container_width=True
        )

        # ── Narrative explanation ─────────────────────────────────────────────
        section_header("💬", "AI Narrative Explanation")
        top3 = result["top_drivers"][:3]
        narrative = f"""
        <div style='color:#94a3b8; line-height:1.8;'>
        Customer <strong style='color:#fff'>{customer_input}</strong> has a predicted churn probability of
        <strong style='color:{risk_color}'>{prob*100:.1f}%</strong>.<br><br>
        The three most influential factors driving this prediction are:
        <ol>
            <li><strong>{top3[0]['feature']}</strong>: SHAP value {top3[0]['shap']:+.4f} — {'pushing churn probability <span style="color:#ef4444">UP</span>' if top3[0]['shap'] > 0 else 'pulling churn probability <span style="color:#10b981">DOWN</span>'}</li>
            <li><strong>{top3[1]['feature']}</strong>: SHAP value {top3[1]['shap']:+.4f} — {'pushing churn probability <span style="color:#ef4444">UP</span>' if top3[1]['shap'] > 0 else 'pulling churn probability <span style="color:#10b981">DOWN</span>'}</li>
            <li><strong>{top3[2]['feature']}</strong>: SHAP value {top3[2]['shap']:+.4f} — {'pushing churn probability <span style="color:#ef4444">UP</span>' if top3[2]['shap'] > 0 else 'pulling churn probability <span style="color:#10b981">DOWN</span>'}</li>
        </ol>
        <strong>Recommended Action:</strong>
        {'Immediate outreach recommended — trigger a win-back sequence with a personalised discount offer within 48 hours.' if prob > 0.7 else 'Monitor this customer closely — consider a loyalty reward nudge within 30 days.' if prob > 0.4 else 'Customer appears stable — continue standard engagement nurturing.'}
        </div>
        """
        glass_card(narrative)

elif analyze_btn:
    st.warning("⚠️ Please enter a Customer ID to analyze.")
else:
    st.info("👈 Enter a Customer ID in the sidebar and click **Analyze Customer** to get started.")
    # Show a sample of available customer IDs
    with st.expander("📋 View available Customer IDs"):
        model_results, cf_df, _ = load_model_and_data()
        if cf_df is not None and not cf_df.empty:
            sample = cf_df[["customer_id"]].head(20)
            st.dataframe(sample, use_container_width=True)
        else:
            st.info("Load data to see customer IDs.")
