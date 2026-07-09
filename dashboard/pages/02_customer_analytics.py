import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from config.settings import settings
from utils.styling import apply_premium_styling, page_header, section_header, glass_card, kpi_row
from analytics.customer import compute_customer_analytics, compute_cohort_retention
from analytics.rfm import compute_rfm
from analytics.segmentation import compute_segmentation
from nodes.feature_engineering import feature_engineering_node
from visualizations.charts import rfm_segment_pie, segment_scatter, cohort_retention_heatmap
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Customer Analytics", page_icon="👥", layout="wide")
page_header("👥", "Customer Analytics", "Deep-dive into RFM segmentation, K-Means clustering, and cohort retention lifecycle.")

@st.cache_data(ttl=300)
def load_data():
    raw_dir = settings.raw_data_path
    raw_data = {}
    for table in ["customers", "transactions", "order_items", "products"]:
        fp = raw_dir / f"{table}.csv"
        if fp.exists():
            raw_data[table] = pd.read_csv(fp).to_dict(orient="records")
    return raw_data

@st.cache_data(ttl=300)
def get_features(raw_data_key: int):
    """Run feature engineering — use a hash key to avoid re-running."""
    raw_data = load_data()
    state = {"raw_data": raw_data, "validated": True, "errors": [], "warnings": []}
    state = feature_engineering_node(state)
    return state.get("features", {})

try:
    raw_data = load_data()

    if not raw_data:
        st.warning("⚠️ No data files found. Please ensure CSV files are in the data/raw directory.")
        st.stop()

    cust_analytics = compute_customer_analytics(raw_data)

    # ── KPI Row ───────────────────────────────────────────────────────────────
    total_c = cust_analytics.get("total_customers", 0)
    active_c = cust_analytics.get("active_customers", 0)
    with_tx   = cust_analytics.get("customers_with_transactions", 0)
    countries = len(cust_analytics.get("top_countries", {}))

    kpi_row([
        {"label": "Total Customers",          "value": f"{total_c:,}",  "positive": True},
        {"label": "Active Customers",          "value": f"{active_c:,}", "delta": f"{active_c/max(total_c,1)*100:.1f}% active", "positive": True},
        {"label": "Customers with Purchases",  "value": f"{with_tx:,}",  "positive": True},
        {"label": "Countries",                 "value": str(countries),  "positive": True},
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Feature Engineering ────────────────────────────────────────────────────
    features = get_features(hash(str(list(raw_data.keys()))))

    if "customer_features" not in features:
        st.warning("⚠️ Customer feature engineering returned no data. Check that transactions.csv is populated.")
        st.stop()

    cf_df = pd.DataFrame(features["customer_features"])

    # ── RFM + Segmentation ──────────────────────────────────────────────────────
    section_header("🎯", "Customer Segmentation", badge="RFM + K-MEANS")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 RFM Segmentation")
        try:
            rfm = compute_rfm(cf_df)
            seg_dist = rfm.get("segment_distribution", {})
            if seg_dist:
                fig_pie = rfm_segment_pie(seg_dist)
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                st.plotly_chart(fig_pie, use_container_width=True)
                
                with st.expander("🔍 RFM Chart Explanations"):
                    c_pe, c_tech = st.columns(2)
                    c_pe.markdown("""
                    **Plain English Interpretation:**
                    * **What it means:** Groups customers into 8 behavior segments based on transaction history.
                    * **Targeting Implication:** Spotlights 'Champions' (high spend, high frequency, recent) who drive revenue, and 'Lost / At Risk' customers who require win-back campaigns.
                    """)
                    c_tech.markdown("""
                    **Technical Implementation:**
                    * **Logic:** Computes Recency, Frequency, and Monetary metrics from raw transactions.
                    * **Score:** Ranks each metric into equal quintiles (1-5), sums them to get an RFM score (3-15), and maps scores to named segments.
                    """)
            else:
                st.info("RFM segment distribution is empty.")
        except Exception as e:
            st.error(f"RFM error: {e}")

    with col2:
        st.markdown("#### 🗂️ K-Means Customer Clusters")
        try:
            seg = compute_segmentation(cf_df)
            if "error" in seg:
                st.warning(seg["error"])
            else:
                segments_list = seg.get("segments", [])
                seg_counts    = seg.get("segment_counts", {})

                if seg_counts:
                    # Always show a bar chart of segment counts — reliable and clear
                    counts_df = pd.DataFrame(
                        list(seg_counts.items()),
                        columns=["Segment", "Customers"]
                    ).sort_values("Customers", ascending=False)

                    fig_bar = px.bar(
                        counts_df,
                        x="Segment", y="Customers",
                        color="Segment",
                        title="Customer Segment Distribution",
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        text="Customers",
                    )
                    fig_bar.update_traces(textposition="outside")
                    fig_bar.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Inter",
                        showlegend=False,
                        xaxis_tickangle=-20,
                        height=380,
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with st.expander("🔍 K-Means Chart Explanations"):
                        c_pe, c_tech = st.columns(2)
                        c_pe.markdown("""
                        **Plain English Interpretation:**
                        * **What it means:** Discovers natural clusters in customer behavior (like high spending but low frequency) without manual rules.
                        * **Insights:** Reveals cluster sizes so you know which behavioral segments are largest and most valuable.
                        """)
                        c_tech.markdown("""
                        **Technical Implementation:**
                        * **Algorithm:** Runs `scikit-learn` KMeans with k=5 clusters.
                        * **Features:** Standardizes Recency, Frequency, Monetary, and Avg Order Value using `StandardScaler` to balance numeric weights.
                        """)
                else:
                    # Fallback to scatter if no counts
                    fig2 = segment_scatter(segments_list)
                    st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.error(f"Segmentation error: {e}")

    # ── Segment scatter (recency vs monetary) ─────────────────────────────────
    section_header("🔵", "Segment Scatter: Recency vs Revenue", badge="K-MEANS")
    try:
        seg = compute_segmentation(cf_df)
        segments_list = seg.get("segments", [])
        if segments_list:
            fig_scatter = segment_scatter(segments_list)
            fig_scatter.update_layout(height=420)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            with st.expander("🔍 Scatter Explanations"):
                c_pe, c_tech = st.columns(2)
                c_pe.markdown("""
                **Plain English Interpretation:**
                * **Visual Grid:** Every dot is a customer. Left side = bought recently. Top side = spent a lot.
                * **Goal:** Moves customers to the top-left quadrant (High Spend, High Recency) using targeted actions.
                """)
                c_tech.markdown("""
                **Technical Implementation:**
                * **Variables:** Recency (days since last purchase) vs. Monetary (lifetime spend), color-coded by the K-Means cluster label.
                * **Rendering:** Uses Plotly Express `scatter()` with transparency overrides.
                """)

            # Segment profiles table
            with st.expander("📋 Segment Cluster Profiles"):
                profiles = seg.get("cluster_profiles", {})
                if profiles:
                    profile_rows = []
                    seg_labels   = seg.get("segment_labels", {})
                    for cluster_id, metrics in profiles.get("recency_days", {}).items():
                        profile_rows.append({
                            "Cluster": cluster_id,
                            "Label": seg_labels.get(cluster_id, f"Segment {cluster_id}"),
                            "Avg Recency (days)": round(profiles.get("recency_days", {}).get(cluster_id, 0), 1),
                            "Avg Frequency":      round(profiles.get("frequency", {}).get(cluster_id, 0), 1),
                            "Avg Monetary ($)":   round(profiles.get("monetary", {}).get(cluster_id, 0), 2),
                        })
                    st.dataframe(pd.DataFrame(profile_rows), use_container_width=True)
    except Exception as e:
        st.error(f"Scatter error: {e}")

    # ── RFM Score Table ───────────────────────────────────────────────────────
    section_header("📋", "Customer RFM Scores & Segments", badge="ALL CUSTOMERS")
    try:
        rfm = compute_rfm(cf_df)
        rfm_scores = rfm.get("scores", [])
        if rfm_scores:
            rfm_df = pd.DataFrame(rfm_scores)
            # Merge customer names if available
            if "customers" in raw_data:
                cust_df_raw = pd.DataFrame(raw_data["customers"])
                name_cols = [c for c in ["customer_id", "first_name", "last_name", "email"] if c in cust_df_raw.columns]
                if "customer_id" in rfm_df.columns and "customer_id" in cust_df_raw.columns:
                    rfm_df = rfm_df.merge(cust_df_raw[name_cols], on="customer_id", how="left")
                    if "first_name" in rfm_df.columns:
                        rfm_df["Name"] = rfm_df["first_name"] + " " + rfm_df["last_name"]
            display_cols = [c for c in ["customer_id", "Name", "rfm_score", "rfm_segment",
                                         "recency_days", "frequency", "monetary"] if c in rfm_df.columns]
            
            # Show the entire customer RFM scores table
            st.dataframe(rfm_df[display_cols], use_container_width=True)
            
            # Downloader form for entire dataset
            csv = rfm_df[display_cols].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full RFM Customer Report (CSV)",
                data=csv,
                file_name="rfm_customer_segments.csv",
                mime="text/csv",
            )
            
            with st.expander("🔍 RFM Table Explanations"):
                c_pe, c_tech = st.columns(2)
                c_pe.markdown("""
                **Plain English Interpretation:**
                * **What this table shows:** The specific segment assignment and computed metrics for every customer.
                * **How to use:** Export this list to target specific user groups via email or CRM tools.
                """)
                c_tech.markdown("""
                **Technical Implementation:**
                * **Data Aggregation:** Joins feature engineering outputs with static customer profiles.
                * **Download Mode:** Encodes pandas DataFrame to CSV stream for client-side downloading.
                """)
        else:
            st.info("No RFM scores computed.")
    except Exception as e:
        st.error(f"RFM table error: {e}")

    # ── Cohort Retention ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📅", "Customer Cohort Retention", badge="LIFECYCLE")
    try:
        retention_df = compute_cohort_retention(raw_data)
        if retention_df is not None and not retention_df.empty:
            fig_cohort = cohort_retention_heatmap(retention_df)
            fig_cohort.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="Inter")
            st.plotly_chart(fig_cohort, use_container_width=True)
            
            with st.expander("🔍 Cohort Heatmap Explanations"):
                c_pe, c_tech = st.columns(2)
                c_pe.markdown("""
                **Plain English Interpretation:**
                * **What it means:** Measures customer loyalty over time. Tracks how long users continue buying month-after-month.
                * **Implication:** If retention drops steeply in Month 1, focus on onboarding; if it drops in Month 3, focus on product quality and re-engagement.
                """)
                c_tech.markdown("""
                **Technical Implementation:**
                * **Logic:** Groups customers by registration month. Tracks what percentage make purchases in month 1, 2, 3... relative to month 0.
                * **Colorscale:** Uses a 'RdPu' (Red-Purple) sequential colorscale to highlight high (darker) vs low (lighter) retention rates.
                """)
        else:
            st.info("ℹ️ Not enough transaction data to compute cohort retention. Need at least 2 cohort periods.")
    except Exception as e:
        st.error(f"Cohort retention error: {e}")

    # ── Top Countries ─────────────────────────────────────────────────────────
    section_header("🌍", "Top Countries by Customers")
    top_countries = cust_analytics.get("top_countries", {})
    if top_countries:
        ct_df = pd.DataFrame(list(top_countries.items()), columns=["Country", "Customers"])
        fig_ct = px.bar(
            ct_df.sort_values("Customers", ascending=True).tail(10),
            x="Customers", y="Country", orientation="h",
            color="Customers",
            color_continuous_scale=["#1e293b", "#6366f1"],
            title="Top 10 Countries",
        )
        fig_ct.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            coloraxis_showscale=False,
            height=380,
        )
        st.plotly_chart(fig_ct, use_container_width=True)
        
        with st.expander("🔍 Country Chart Explanations"):
            c_pe, c_tech = st.columns(2)
            c_pe.markdown("""
            **Plain English Interpretation:**
            * **What it means:** Ranks geographic locations based on the volume of registered customers.
            * **Goal:** Directs marketing localized budgets where customer counts are densest.
            """)
            c_tech.markdown("""
            **Technical Implementation:**
            * **Method:** Sorts customer locations, counts occurrences using pandas aggregation, and renders a horizontal bar chart via Plotly.
            """)

except Exception as e:
    st.error(f"Error loading customer analytics: {e}")
    import traceback
    with st.expander("🐛 Debug Info"):
        st.code(traceback.format_exc())
    st.info("Please ensure CSV data files exist in the data/raw directory.")
