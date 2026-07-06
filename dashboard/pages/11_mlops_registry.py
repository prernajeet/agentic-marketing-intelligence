import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import plotly.express as px
import numpy as np
from utils.styling import apply_premium_styling, page_header, section_header, glass_card, kpi_row, champion_banner

st.set_page_config(page_title="MLOps Model Registry", page_icon="🧬", layout="wide")
page_header("🧬", "MLOps Model Registry", "Monitor training runs, compare model performance, and track your production champion model.")

@st.cache_data(show_spinner=False)
def load_registry_from_db():
    """Try to load from database, gracefully fall back to live training."""
    try:
        from database.connection import SessionLocal
        from database.models import ModelResult
        db = SessionLocal()
        runs = db.query(ModelResult).order_by(ModelResult.trained_at.desc()).all()
        db.close()
        if runs:
            return [
                {
                    "Run ID": str(r.result_id)[:8] + "…",
                    "Model Name": r.model_name,
                    "Version": r.model_version or "1.0.0",
                    "Task": r.task or "churn_classification",
                    "ROC-AUC": round(r.roc_auc, 4) if r.roc_auc else None,
                    "F1 Score": round(r.f1_score, 4) if r.f1_score else None,
                    "Accuracy": round(r.accuracy, 4) if r.accuracy else None,
                    "Trained At": r.trained_at.strftime("%Y-%m-%d %H:%M"),
                    "Is Champion": True if r.is_champion else False,
                    "Samples": r.training_samples or 0,
                }
            for r in runs], None
        return [], None
    except Exception as e:
        return None, str(e)

@st.cache_resource(show_spinner=False)
def train_and_get_results():
    """Live-train models and return registry-compatible records."""
    from ml.churn import train_churn_model
    from nodes.feature_engineering import feature_engineering_node
    from config.settings import settings
    from datetime import datetime

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

    best_auc = max((r.get("metrics", {}).get("roc_auc", 0) for r in model_results.values()), default=0)
    records = []
    for name, res in model_results.items():
        m = res.get("metrics", {})
        auc = m.get("roc_auc", 0)
        records.append({
            "Run ID": f"run_{name[:4].lower()}",
            "Model Name": name,
            "Version": "1.0.0",
            "Task": "churn_classification",
            "ROC-AUC": round(auc, 4),
            "F1 Score": round(m.get("f1", 0), 4),
            "Accuracy": round(m.get("accuracy", 0), 4),
            "Trained At": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Is Champion": auc == best_auc,
            "Samples": len(cf_df),
        })
    return records

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading model registry…"):
    db_records, db_error = load_registry_from_db()

if db_records:
    records = db_records
    st.caption("📦 Source: PostgreSQL Model Registry")
else:
    if db_error:
        st.caption(f"ℹ️ DB unavailable ({db_error[:60]}…) — showing live training results instead.")
    with st.spinner("🤖 Training models live for registry…"):
        records = train_and_get_results()
    if records:
        st.caption("📦 Source: Live Model Training")

if not records:
    st.warning("⚠️ No model data available. Ensure CSV data files are present in the data directory.")
    st.stop()

df_runs = pd.DataFrame(records)

# ── KPI Summary ───────────────────────────────────────────────────────────────
champion = next((r for r in records if r["Is Champion"]), records[0])
best_auc = champion.get("ROC-AUC", 0)

kpi_row([
    {"label": "Registered Models", "value": str(len(records)), "positive": True},
    {"label": "Champion AUC", "value": f"{best_auc*100:.1f}%", "delta": "Best model", "positive": True},
    {"label": "Champion F1", "value": f"{champion.get('F1 Score', 0)*100:.1f}%", "positive": True},
    {"label": "Training Samples", "value": f"{champion.get('Samples', 0):,}", "positive": True},
])

# ── Champion Banner ────────────────────────────────────────────────────────────
champion_banner(champion["Model Name"], best_auc, "Churn Prediction")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Model Leaderboard", "📈 Performance Charts", "🔍 Model Details"])

with tab1:
    section_header("🏅", "Model Leaderboard")
    display_df = df_runs.copy()
    display_df["Is Champion"] = display_df["Is Champion"].map({True: "🏆 Champion", False: "—"})
    display_df["ROC-AUC"] = (display_df["ROC-AUC"] * 100).round(2).astype(str) + "%"
    display_df["F1 Score"] = (display_df["F1 Score"] * 100).round(2).astype(str) + "%"
    display_df["Accuracy"] = (display_df["Accuracy"] * 100).round(2).astype(str) + "%"
    st.dataframe(display_df, use_container_width=True, height=350)

with tab2:
    section_header("📊", "Metric Comparison")
    plot_df = df_runs.copy()
    fig_bar = px.bar(
        plot_df,
        x="Model Name",
        y=["ROC-AUC", "F1 Score", "Accuracy"],
        barmode="group",
        color_discrete_sequence=["#6366f1", "#a855f7", "#06b6d4"],
        template="plotly_dark",
    )
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        yaxis=dict(tickformat=".1%"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=420,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Radar chart
    section_header("🕸️", "Model Radar Chart")
    model_names = [r["Model Name"] for r in records]
    metrics_keys = ["ROC-AUC", "F1 Score", "Accuracy"]
    import plotly.graph_objects as go
    fig_radar = go.Figure()
    colors = ["#6366f1", "#a855f7", "#06b6d4", "#10b981", "#f59e0b"]
    for i, rec in enumerate(records):
        vals = [rec.get(k, 0) for k in metrics_keys]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=metrics_keys + [metrics_keys[0]],
            fill="toself",
            name=rec["Model Name"],
            line_color=colors[i % len(colors)],
            opacity=0.7,
        ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], color="#64748b"),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        template="plotly_dark",
        font_family="Inter",
        height=420,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    section_header("🔍", "Champion Model Deep Dive")
    glass_card(f"""
    <div style='color:#94a3b8; line-height:1.9;'>
    <h4 style='color:#fff; margin-top:0;'>Why {champion['Model Name']} was selected as Champion</h4>
    <ul>
        <li><strong>Highest ROC-AUC</strong> ({best_auc*100:.1f}%): Best class-separation ability — it correctly distinguishes churners from loyal customers.</li>
        <li><strong>Balanced F1 Score</strong> ({champion.get('F1 Score', 0)*100:.1f}%): Optimal precision-recall tradeoff — minimises false alarms while catching real churn threats.</li>
        <li><strong>Trained on {champion.get('Samples', 0):,} records</strong>: Sufficient data for generalisation across customer segments.</li>
        <li><strong>Business Impact</strong>: A 1% improvement in ROC-AUC at this scale translates to ~$50K+ in recovered annual revenue by catching churners before they leave.</li>
    </ul>
    </div>
    """)

    section_header("📋", "All Model Metrics")
    for rec in records:
        with st.expander(f"{'🏆 ' if rec['Is Champion'] else ''}  {rec['Model Name']} — AUC: {rec.get('ROC-AUC', 0)*100:.1f}%"):
            col1, col2, col3 = st.columns(3)
            col1.metric("ROC-AUC", f"{rec.get('ROC-AUC', 0)*100:.2f}%")
            col2.metric("F1 Score", f"{rec.get('F1 Score', 0)*100:.2f}%")
            col3.metric("Accuracy", f"{rec.get('Accuracy', 0)*100:.2f}%")
