import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from config.settings import settings
from analytics.revenue import compute_revenue_analytics
from visualizations.charts import revenue_trend_line

st.set_page_config(page_title="Revenue Analytics", page_icon="💰", layout="wide")
st.title("💰 Revenue Analytics")

@st.cache_data(ttl=300)
def load_data():
    raw_dir = settings.raw_data_path
    raw_data = {}
    for table in ["transactions", "order_items", "products"]:
        fp = raw_dir / f"{table}.csv"
        if fp.exists():
            raw_data[table] = pd.read_csv(fp).to_dict(orient="records")
    return raw_data

try:
    raw_data = load_data()
    rev = compute_revenue_analytics(raw_data)
    summary = rev.get("summary", {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${summary.get('total_revenue', 0):,.0f}")
    col2.metric("Total Orders", f"{summary.get('total_orders', 0):,}")
    col3.metric("Avg Order Value", f"${summary.get('avg_order_value', 0):,.2f}")
    col4.metric("Revenue/Customer", f"${summary.get('revenue_per_customer', 0):,.2f}")

    st.markdown("---")
    if rev.get("monthly_revenue"):
        st.plotly_chart(revenue_trend_line(rev["monthly_revenue"]), use_container_width=True)
        
        with st.expander("🔍 Revenue Trend Explanations"):
            c_pe, c_tech = st.columns(2)
            c_pe.markdown("""
            **Plain English Interpretation:**
            * **What it means:** Tracks total sales revenue on a month-by-month basis.
            * **Business Insight:** Shows seasonal growth patterns, baseline run-rate trends, and transaction velocity.
            """)
            c_tech.markdown("""
            **Technical Implementation:**
            * **Variables:** X-axis is time (month index), Y-axis is monetary sales volume ($).
            * **Logic:** Aggregates transaction amounts by date formatted to month strings (YYYY-MM).
            """)

    col1, col2 = st.columns(2)
    with col1:
        if rev.get("revenue_by_channel"):
            st.subheader("Revenue by Channel")
            st.dataframe(pd.DataFrame(list(rev["revenue_by_channel"].items()),
                                       columns=["Channel", "Revenue"]), use_container_width=True)
    with col2:
        if rev.get("revenue_by_payment"):
            st.subheader("Revenue by Payment Method")
            st.dataframe(pd.DataFrame(list(rev["revenue_by_payment"].items()),
                                       columns=["Method", "Revenue"]), use_container_width=True)

except Exception as e:
    st.error(f"Revenue analytics error: {e}")
