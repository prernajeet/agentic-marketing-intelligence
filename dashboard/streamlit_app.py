import streamlit as st
import sys
from pathlib import Path

# Ensure project root is on path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from utils.styling import apply_premium_styling, section_header, glass_card, kpi_row

st.set_page_config(
    page_title="Agentic Marketing Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_premium_styling()

# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header" style="text-align:center; padding: 3rem 2.5rem;">
    <div style="font-size:3rem; margin-bottom:0.5rem;">🚀</div>
    <h1 style="font-size:3rem; margin-bottom:0.5rem;">Agentic Marketing Intelligence</h1>
    <p style="font-size:1.1rem; max-width:600px; margin:0 auto;">
        Enterprise AI-powered marketing analytics. Predict churn, forecast lifetime value,
        generate campaigns, and automate CRM actions — all from one intelligent platform.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Quick KPI Strip ───────────────────────────────────────────────────────────
kpi_row([
    {"label": "ML Models", "value": "5+", "delta": "XGBoost · RF · LightGBM", "positive": True},
    {"label": "Platform Pages", "value": "12", "delta": "Analytics to CRM", "positive": True},
    {"label": "AI Features", "value": "Local SHAP · Cohort Retention · Copy Writer · Webhooks", "positive": True},
    {"label": "Stack", "value": "Python · Streamlit · LangGraph · Gemini", "positive": True},
])

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature Grid ──────────────────────────────────────────────────────────────
section_header("⚡", "Platform Capabilities", badge="OVERVIEW")

col1, col2, col3 = st.columns(3)
with col1:
    glass_card("""
    <h4 style='color:#6366f1; margin-top:0;'>📊 Analytics Suite</h4>
    <ul style='color:#94a3b8; line-height:1.9; padding-left:1.2rem;'>
        <li>Customer behaviour & RFM segmentation</li>
        <li>Revenue trends & product analytics</li>
        <li>Campaign performance & ROI</li>
        <li>Cohort retention heatmap</li>
    </ul>
    """)
    glass_card("""
    <h4 style='color:#a855f7; margin-top:0;'>🤖 ML Predictions</h4>
    <ul style='color:#94a3b8; line-height:1.9; padding-left:1.2rem;'>
        <li>Churn classification (5 models)</li>
        <li>Customer lifetime value (CLV)</li>
        <li>What-If simulation engine</li>
        <li>MLOps model registry & tracking</li>
    </ul>
    """)

with col2:
    glass_card("""
    <h4 style='color:#06b6d4; margin-top:0;'>🔎 Explainability</h4>
    <ul style='color:#94a3b8; line-height:1.9; padding-left:1.2rem;'>
        <li>Global feature importance (all customers)</li>
        <li>Local SHAP — per-customer "why churn?"</li>
        <li>AI-powered behavioral narrative</li>
        <li>Risk level classification & actions</li>
    </ul>
    """)
    glass_card("""
    <h4 style='color:#10b981; margin-top:0;'>📄 Executive Reports</h4>
    <ul style='color:#94a3b8; line-height:1.9; padding-left:1.2rem;'>
        <li>AI-generated executive narrative</li>
        <li>KPI dashboards with live data</li>
        <li>Strategic recommendations</li>
        <li>Downloadable PDF/Markdown reports</li>
    </ul>
    """)

with col3:
    glass_card("""
    <h4 style='color:#f59e0b; margin-top:0;'>✍️ Campaign Copy Writer</h4>
    <ul style='color:#94a3b8; line-height:1.9; padding-left:1.2rem;'>
        <li>7 content types (email, SMS, ads…)</li>
        <li>Tone & urgency controls</li>
        <li>A/B variation generation</li>
        <li>Churn-context targeting mode</li>
    </ul>
    """)
    glass_card("""
    <h4 style='color:#ef4444; margin-top:0;'>🔗 CRM Integration</h4>
    <ul style='color:#94a3b8; line-height:1.9; padding-left:1.2rem;'>
        <li>Webhook to HubSpot / Mailchimp / Slack</li>
        <li>Auto-sync high-risk churn customers</li>
        <li>Configurable risk threshold</li>
        <li>Dry-run preview mode</li>
    </ul>
    """)

# ── Navigation Guide ──────────────────────────────────────────────────────────
section_header("🗺️", "How to Navigate", badge="QUICK START")
glass_card("""
<div style='color:#94a3b8; line-height:1.9;'>
Use the <strong style='color:#fff'>sidebar</strong> to navigate between platform sections:<br><br>
<strong style='color:#6366f1'>01 Business Query</strong> → Ask any natural language question to the AI agent<br>
<strong style='color:#a855f7'>02–05 Analytics</strong> → Customer, Revenue, Campaign, Product dashboards<br>
<strong style='color:#06b6d4'>06–09 ML</strong> → Model results, predictions, explainability, what-if simulation<br>
<strong style='color:#10b981'>10 Executive Report</strong> → Full AI-powered executive report with all models<br>
<strong style='color:#f59e0b'>11 MLOps Registry</strong> → Compare all trained models with performance charts<br>
<strong style='color:#ef4444'>20 Customer Explainability</strong> → Local SHAP per-customer churn explanation<br>
<strong style='color:#6366f1'>40 Retention Heatmap</strong> → Monthly/weekly cohort retention analysis<br>
<strong style='color:#a855f7'>50 Campaign Copy Writer</strong> → Generate AI marketing copy in seconds<br>
<strong style='color:#06b6d4'>60 CRM Webhooks</strong> → Sync high-risk customers to your CRM platform<br>
</div>
""")

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center; padding:1rem 0;'>
    <div style='font-size:2rem;'>🚀</div>
    <strong style='font-size:1.1rem;'>AMI Platform</strong><br>
    <span style='font-size:0.8rem; color:#64748b;'>v2.0 — Advanced Edition</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("**Select a page above to get started.**")
