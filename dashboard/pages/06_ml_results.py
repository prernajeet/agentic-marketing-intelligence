import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from config.settings import settings
from ml.churn import train_churn_model
from nodes.feature_engineering import feature_engineering_node

st.set_page_config(page_title="ML Results", page_icon="🤖", layout="wide")
st.title("🤖 ML Model Results")

if st.button("Train & Compare Models"):
    raw_dir = settings.raw_data_path
    raw_data = {}
    for t in ["customers", "transactions"]:
        fp = raw_dir / f"{t}.csv"
        if fp.exists():
            raw_data[t] = pd.read_csv(fp).to_dict(orient="records")

    state = {"raw_data": raw_data, "validated": True, "errors": [], "warnings": []}
    state = feature_engineering_node(state)
    features = state.get("features", {})

    if "customer_features" in features:
        with st.spinner("Training models..."):
            cf_df = pd.DataFrame(features["customer_features"])
            try:
                results = train_churn_model(cf_df)
                rows = []
                for name, res in results.items():
                    if "metrics" in res:
                        row = {"Model": name}
                        row.update(res["metrics"])
                        rows.append(row)
                if rows:
                    df = pd.DataFrame(rows).set_index("Model")
                    st.subheader("Model Comparison")
                    st.dataframe(df.style.highlight_max(axis=0, color="#2ecc71"), use_container_width=True)
                    champion = df["roc_auc"].idxmax()
                    st.success(f"🏆 Champion Model: **{champion}** (ROC-AUC: {df.loc[champion, 'roc_auc']:.4f})")
            except Exception as e:
                st.error(f"Training error: {e}")
    else:
        st.warning("No customer features available. Ensure data CSVs are in data/raw/.")
