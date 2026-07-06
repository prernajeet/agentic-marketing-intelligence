import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from config.settings import settings
from analytics.product import compute_product_analytics

st.set_page_config(page_title="Product Analytics", page_icon="📦", layout="wide")
st.title("📦 Product Analytics")

@st.cache_data(ttl=300)
def load_data():
    raw_dir = settings.raw_data_path
    raw_data = {}
    for table in ["order_items", "products", "categories"]:
        fp = raw_dir / f"{table}.csv"
        if fp.exists():
            raw_data[table] = pd.read_csv(fp).to_dict(orient="records")
    return raw_data

try:
    raw_data = load_data()
    prod = compute_product_analytics(raw_data)

    col1, col2 = st.columns(2)
    col1.metric("Unique Products Sold", prod.get("total_products_sold", "N/A"))
    col2.metric("Total Units Sold", f"{prod.get('total_units_sold', 0):,}")

    st.markdown("---")
    top = prod.get("top_products_named", prod.get("top_products_by_revenue", []))
    if top:
        st.subheader("Top Products by Revenue")
        st.dataframe(pd.DataFrame(top), use_container_width=True)

except Exception as e:
    st.error(f"Product analytics error: {e}")
