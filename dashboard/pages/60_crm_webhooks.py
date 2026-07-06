"""
dashboard/pages/60_crm_webhooks.py
CRM Webhook Integration — fire churn alerts to HubSpot / Mailchimp / Slack.
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import json
import os
import requests
from datetime import datetime
from config.settings import settings
from utils.styling import apply_premium_styling, page_header, section_header, glass_card, kpi_row

st.set_page_config(page_title="CRM Webhook Integration", page_icon="🔗", layout="wide")
page_header("🔗", "CRM Webhook Integration", "Automatically sync high-risk churn predictions to your CRM or marketing automation platform.")

# ── Sidebar config ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Webhook Settings")
    crm_platform = st.selectbox("Target Platform", ["HubSpot", "Mailchimp", "Slack", "Custom Webhook"])
    risk_threshold = st.slider("Churn Score Threshold", min_value=0.50, max_value=0.95, value=0.75, step=0.05,
                               help="Only customers above this churn probability will be synced.")
    webhook_url = st.text_input(
        "Webhook URL",
        value=os.environ.get("WEBHOOK_URL", ""),
        type="password",
        placeholder="https://hooks.example.com/...",
    )
    dry_run = st.checkbox("🧪 Dry Run (preview without sending)", value=True)
    sync_btn = st.button("🚀 Sync High-Risk Customers", use_container_width=True)

# ── How It Works ───────────────────────────────────────────────────────────────
section_header("ℹ️", "How It Works", badge="AUTOMATION")
glass_card("""
<div style='color:#94a3b8; line-height:1.9;'>
<ol>
<li>The platform loads the <strong>latest churn predictions</strong> from the database.</li>
<li>It filters customers above the configured <strong>risk threshold</strong>.</li>
<li>For each high-risk customer, it builds a <strong>structured payload</strong> (customer ID, name, email, churn score, recommended action).</li>
<li>The payload is <strong>POSTed to your CRM webhook URL</strong> — triggering an automated win-back sequence in HubSpot, Mailchimp, or Slack.</li>
</ol>
<strong style='color:#f59e0b'>⚡ Pro Tip:</strong> Enable this as a nightly scheduled job to continuously push at-risk customers into your marketing automation workflows.
</div>
""")

# ── Load predictions ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_high_risk_customers(threshold: float):
    try:
        from ml.churn import train_churn_model, predict_churn
        from nodes.feature_engineering import feature_engineering_node

        raw_dir = settings.raw_data_path
        raw_data = {}
        for table in ["customers", "transactions", "order_items", "products"]:
            fp = raw_dir / f"{table}.csv"
            if fp.exists():
                raw_data[table] = pd.read_csv(fp).to_dict(orient="records")

        if not raw_data:
            return None

        state = {"raw_data": raw_data, "validated": True, "errors": [], "warnings": []}
        state = feature_engineering_node(state)
        cf_df = pd.DataFrame(state.get("features", {}).get("customer_features", []))

        if cf_df.empty:
            return None

        model_results = train_churn_model(cf_df)
        preds = predict_churn(cf_df, model_results)

        if "predictions" not in preds:
            return None

        preds_df = pd.DataFrame(preds["predictions"])
        high_risk = preds_df[preds_df["churn_probability"] >= threshold].copy()

        # Merge with customer names/email
        if "customers" in raw_data:
            cust_df = pd.DataFrame(raw_data["customers"])
            cols = [c for c in ["customer_id", "first_name", "last_name", "email", "country"] if c in cust_df.columns]
            high_risk = high_risk.merge(cust_df[cols], on="customer_id", how="left")

        high_risk = high_risk.sort_values("churn_probability", ascending=False)
        return high_risk, preds.get("champion_model", "Unknown")
    except Exception as e:
        st.error(f"Error loading predictions: {e}")
        return None

# ── Preview Section ────────────────────────────────────────────────────────────
section_header("👁️", f"High-Risk Customers (Threshold ≥ {risk_threshold*100:.0f}%)", badge="PREVIEW")

with st.spinner("Loading predictions…"):
    result = load_high_risk_customers(risk_threshold)

if result is None:
    st.warning("⚠️ No prediction data found. Please run model training first.")
else:
    high_risk_df, champion = result

    kpi_row([
        {"label": "High-Risk Customers", "value": str(len(high_risk_df)), "delta": f"≥{risk_threshold*100:.0f}% threshold", "positive": False},
        {"label": "Champion Model", "value": champion, "positive": True},
        {"label": "Sync Mode", "value": "DRY RUN" if dry_run else "LIVE SYNC", "positive": dry_run},
        {"label": "Platform", "value": crm_platform, "positive": True},
    ])

    display_cols = [c for c in ["customer_id", "first_name", "last_name", "email", "churn_probability", "country"] if c in high_risk_df.columns]
    st.dataframe(high_risk_df[display_cols].head(20), use_container_width=True)

    # ── Payload preview ────────────────────────────────────────────────────────
    with st.expander("📦 Preview Webhook Payload (first customer)"):
        if not high_risk_df.empty:
            sample = high_risk_df.iloc[0]
            payload = {
                "customer_id": sample.get("customer_id", ""),
                "first_name": sample.get("first_name", ""),
                "last_name": sample.get("last_name", ""),
                "email": sample.get("email", ""),
                "churn_probability": float(sample.get("churn_probability", 0)),
                "risk_level": "HIGH" if sample.get("churn_probability", 0) > 0.8 else "MEDIUM",
                "recommended_action": "Send 20% discount win-back email sequence",
                "platform_source": "Agentic Marketing Intelligence",
                "triggered_at": datetime.utcnow().isoformat() + "Z",
            }
            st.json(payload)

    # ── Sync Action ────────────────────────────────────────────────────────────
    if sync_btn:
        if dry_run:
            section_header("✅", "Dry Run Complete", badge="PREVIEW ONLY")
            glass_card(f"""
            <div style='color:#94a3b8; line-height:1.8;'>
            🧪 <strong>Dry Run Results:</strong><br>
            Would have synced <strong style='color:#f59e0b'>{len(high_risk_df)}</strong> high-risk customers to <strong>{crm_platform}</strong>.<br>
            No actual requests were sent. Disable <em>Dry Run</em> in the sidebar to send live webhook calls.
            </div>
            """)
        elif not webhook_url:
            st.error("❌ Please enter a Webhook URL to send live requests.")
        else:
            progress = st.progress(0)
            success_count = 0
            errors = []

            for i, (_, row) in enumerate(high_risk_df.head(50).iterrows()):
                payload = {
                    "customer_id": str(row.get("customer_id", "")),
                    "email": str(row.get("email", "")),
                    "first_name": str(row.get("first_name", "")),
                    "last_name": str(row.get("last_name", "")),
                    "churn_probability": float(row.get("churn_probability", 0)),
                    "risk_level": "HIGH" if row.get("churn_probability", 0) > 0.8 else "MEDIUM",
                    "recommended_action": "Send win-back campaign",
                    "triggered_at": datetime.utcnow().isoformat() + "Z",
                }
                try:
                    resp = requests.post(webhook_url, json=payload, timeout=5)
                    if resp.ok:
                        success_count += 1
                    else:
                        errors.append(f"Customer {payload['customer_id']}: HTTP {resp.status_code}")
                except Exception as e:
                    errors.append(f"Customer {payload['customer_id']}: {str(e)}")

                progress.progress((i + 1) / min(50, len(high_risk_df)))

            st.success(f"✅ Synced {success_count} customers to {crm_platform}.")
            if errors:
                with st.expander(f"⚠️ {len(errors)} errors"):
                    for err in errors:
                        st.error(err)

# ── Integration Guide ──────────────────────────────────────────────────────────
section_header("📖", "Integration Guide")
tabs = st.tabs(["HubSpot", "Mailchimp", "Slack", "Custom"])

with tabs[0]:
    glass_card("""
    <h4 style='color:#6366f1; margin-top:0'>HubSpot Setup</h4>
    <ol style='color:#94a3b8; line-height:1.9;'>
    <li>Go to <strong>HubSpot → Settings → Integrations → Private Apps</strong></li>
    <li>Create a new Private App with <em>contacts.write</em> scope</li>
    <li>Copy your App Token</li>
    <li>Use the webhook URL: <code style='color:#06b6d4'>https://api.hubapi.com/contacts/v1/contact/createOrUpdate/email/{email}</code></li>
    <li>Each payload will create or update a contact with the churn score as a custom property</li>
    </ol>
    """)

with tabs[1]:
    glass_card("""
    <h4 style='color:#a855f7; margin-top:0'>Mailchimp Setup</h4>
    <ol style='color:#94a3b8; line-height:1.9;'>
    <li>Go to <strong>Mailchimp → Account → Extras → API Keys</strong></li>
    <li>Create an API key</li>
    <li>Use endpoint: <code style='color:#06b6d4'>https://usX.api.mailchimp.com/3.0/lists/{list_id}/members</code></li>
    <li>Tag synced customers with <strong>churn-risk-high</strong> to trigger automated journey flows</li>
    </ol>
    """)

with tabs[2]:
    glass_card("""
    <h4 style='color:#10b981; margin-top:0'>Slack Alerts Setup</h4>
    <ol style='color:#94a3b8; line-height:1.9;'>
    <li>Go to <strong>api.slack.com/apps</strong> → Create New App → From Scratch</li>
    <li>Add <em>Incoming Webhooks</em> feature and activate it</li>
    <li>Copy the Webhook URL for your chosen channel</li>
    <li>Paste the URL in the sidebar — each high-risk customer triggers a formatted Slack alert</li>
    </ol>
    """)

with tabs[3]:
    glass_card("""
    <h4 style='color:#f59e0b; margin-top:0'>Custom Webhook</h4>
    <p style='color:#94a3b8; line-height:1.9;'>
    Any endpoint accepting <strong>HTTP POST with JSON body</strong> will work.<br>
    The payload schema includes: <code>customer_id, email, first_name, last_name, churn_probability, risk_level, recommended_action, triggered_at</code>.<br><br>
    Use this to integrate with: <strong>ActiveCampaign, Klaviyo, Braze, Iterable, SendGrid, Zapier</strong>, or your own internal microservices.
    </p>
    """)
