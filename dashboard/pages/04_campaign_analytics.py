import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from config.settings import settings
from analytics.campaign import compute_campaign_analytics
from visualizations.charts import campaign_funnel

st.set_page_config(page_title="Campaign Analytics", page_icon="📣", layout="wide")
st.title("📣 Campaign Analytics")

@st.cache_data(ttl=300)
def load_data():
    raw_dir = settings.raw_data_path
    raw_data = {}
    for table in ["campaigns", "campaign_responses"]:
        fp = raw_dir / f"{table}.csv"
        if fp.exists():
            raw_data[table] = pd.read_csv(fp).to_dict(orient="records")
    return raw_data

try:
    raw_data = load_data()
    camp = compute_campaign_analytics(raw_data)
    summary = camp.get("summary", {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Campaigns", camp.get("total_campaigns", "N/A"))
    col2.metric("Total Responses", summary.get("total_responses", "N/A"))
    col3.metric("Conversions", summary.get("total_conversions", "N/A"))
    col4.metric("Conv. Rate", f"{summary.get('conversion_rate_pct', 0):.1f}%")

    st.markdown("---")
    st.plotly_chart(campaign_funnel(camp), use_container_width=True)
    
    with st.expander("🔍 Campaign Funnel Explanations"):
        c_pe, c_tech = st.columns(2)
        c_pe.markdown("""
        **Plain English Interpretation:**
        * **What it means:** Measures how campaigns convert from exposure to response to final purchases.
        * **Business Insight:** Pinpoints where prospects drop off in the conversion funnel to optimize copy or offer value.
        """)
        c_tech.markdown("""
        **Technical Implementation:**
        * **Logic:** Joins campaign targets with responses, calculating conversion rate percent.
        * **Rendering:** Uses Plotly Graph Objects `Funnel` with custom sequential color mappings.
        """)

    if camp.get("by_channel"):
        st.subheader("Campaigns by Channel")
        st.bar_chart(pd.DataFrame(list(camp["by_channel"].items()), columns=["Channel", "Count"]).set_index("Channel"))
        
        with st.expander("🔍 Channel Chart Explanations"):
            c_pe, c_tech = st.columns(2)
            c_pe.markdown("""
            **Plain English Interpretation:**
            * **What it means:** Distribution of running marketing campaigns across different media channels (e.g., social, email, SMS).
            """)
            c_tech.markdown("""
            **Technical Implementation:**
            * **Logic:** Counts occurrences of each channel column in campaigns dataset and renders using Streamlit's native `.bar_chart()`.
            """)

except Exception as e:
    st.error(f"Campaign analytics error: {e}")
