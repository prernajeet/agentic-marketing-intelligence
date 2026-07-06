"""
dashboard/pages/40_retention_heatmap.py
Cohort Retention Heatmap — visualise customer retention across monthly/weekly cohorts.
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from config.settings import settings
from utils.styling import apply_premium_styling, page_header, section_header, glass_card, kpi_row

st.set_page_config(page_title="Cohort Retention Heatmap", page_icon="🔥", layout="wide")
page_header("🔥", "Cohort Retention Heatmap", "Track how well each acquisition cohort retains over time — month by month or week by week.")

# ── Sidebar Controls ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Heatmap Settings")
    granularity = st.radio("Cohort Granularity", ["monthly", "weekly"], index=0)
    max_periods = st.slider("Max Periods to Display", min_value=3, max_value=18, value=12)
    run_btn = st.button("🔄 Generate Heatmap", use_container_width=True)

# ── Load transactions ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_transactions():
    raw_dir = settings.raw_data_path
    fp = raw_dir / "transactions.csv"
    if not fp.exists():
        return None
    df = pd.read_csv(fp)
    return df

section_header("ℹ️", "About Cohort Analysis", badge="ANALYTICS")
glass_card("""
<p style='color:#94a3b8; margin:0; line-height:1.8;'>
A <strong>cohort</strong> is a group of customers who made their <em>first purchase in the same period</em>.
The heatmap shows what <strong>percentage of each cohort returned to purchase</strong> in subsequent periods.<br><br>
📌 <strong>Period 0</strong> is always 100% (first purchase).<br>
📉 <strong>Darker cells</strong> = fewer customers retained.<br>
💡 <strong>Look for cohorts with unusually fast drop-off</strong> — these often correspond to poor campaign quality or seasonal mismatch.
</p>
""")

if run_btn:
    with st.spinner("📊 Computing cohort retention matrix…"):
        df = load_transactions()
        if df is None:
            st.error("❌ transactions.csv not found in the data directory.")
            st.stop()

        from ml.pipeline_retention import compute_cohort_retention, retention_to_plotly

        # Detect the date column
        date_col = None
        for col in ["order_date", "transaction_date", "date", "created_at"]:
            if col in df.columns:
                date_col = col
                break

        if date_col is None:
            st.error("❌ No date column found in transactions.csv. Expected: order_date, transaction_date, date, or created_at.")
            st.stop()

        customer_col = "customer_id" if "customer_id" in df.columns else df.columns[0]

        retention_df = compute_cohort_retention(
            df.rename(columns={date_col: "order_date", customer_col: "customer_id"})[["order_date", "customer_id"]],
            granularity=granularity,
        )

        # Limit periods
        max_col = min(max_periods, len(retention_df.columns))
        retention_df = retention_df.iloc[:, :max_col]

        # ── KPI Summary ───────────────────────────────────────────────────────
        avg_period1 = retention_df[1].mean() if 1 in retention_df.columns else 0
        avg_period3 = retention_df[3].mean() if 3 in retention_df.columns else 0
        num_cohorts = len(retention_df)

        kpi_row([
            {"label": "Total Cohorts", "value": str(num_cohorts), "positive": True},
            {"label": "Avg Month-1 Retention", "value": f"{avg_period1*100:.1f}%", "positive": avg_period1 > 0.3},
            {"label": "Avg Month-3 Retention", "value": f"{avg_period3*100:.1f}%", "positive": avg_period3 > 0.2},
            {"label": "Granularity", "value": granularity.title(), "positive": True},
        ])

        # ── Heatmap Chart ─────────────────────────────────────────────────────
        section_header("📊", "Retention Heatmap")
        fig = retention_to_plotly(retention_df, granularity)
        st.plotly_chart(fig, use_container_width=True)

        # ── Raw Data Table ────────────────────────────────────────────────────
        with st.expander("📋 View Raw Retention Matrix"):
            display_df = (retention_df * 100).round(1).astype(str) + "%"
            st.dataframe(display_df, use_container_width=True)

        # ── Insights ──────────────────────────────────────────────────────────
        section_header("💡", "Automated Retention Insights")

        # Find best and worst cohort
        period1_col = retention_df[1] if 1 in retention_df.columns else None
        if period1_col is not None:
            best_cohort = period1_col.idxmax()
            worst_cohort = period1_col.idxmin()
            best_val = period1_col.max()
            worst_val = period1_col.min()

            glass_card(f"""
            <div style='line-height:1.9; color:#94a3b8;'>
            📈 <strong>Best Performing Cohort:</strong> <span style='color:#10b981'>{best_cohort}</span>
            — {best_val*100:.1f}% of customers returned in the next period.<br>
            📉 <strong>Worst Performing Cohort:</strong> <span style='color:#ef4444'>{worst_cohort}</span>
            — Only {worst_val*100:.1f}% of customers returned.<br><br>
            💡 <strong>Recommendation:</strong> Investigate what campaign or external factor drove the
            <em>{worst_cohort}</em> cohort's low retention. A targeted win-back campaign with a 15% discount
            could recapture up to 30% of those dormant customers.
            </div>
            """)
else:
    st.info("👈 Configure settings in the sidebar and click **Generate Heatmap** to begin.")
