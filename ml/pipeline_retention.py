"""
ml/pipeline_retention.py
Compute cohort retention matrix from transaction data.
"""

import pandas as pd
import numpy as np
from typing import Optional, Literal


def compute_cohort_retention(
    transactions: pd.DataFrame,
    granularity: Literal["monthly", "weekly"] = "monthly",
) -> pd.DataFrame:
    """
    Given a transactions DataFrame with columns [customer_id, order_date],
    compute a cohort retention matrix.

    Returns a pivot DataFrame where:
      - rows   = cohort period (first purchase period)
      - columns = period offset (0, 1, 2, ...)
      - values  = retention rate (0.0 – 1.0)
    """
    df = transactions.copy()

    # Ensure datetime
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date", "customer_id"])

    if granularity == "weekly":
        period_col = df["order_date"].dt.to_period("W")
    else:
        period_col = df["order_date"].dt.to_period("M")

    df["order_period"] = period_col

    # Cohort = first purchase period
    df["cohort"] = df.groupby("customer_id")["order_period"].transform("min")

    # Period offset (integer)
    df["period_offset"] = (df["order_period"] - df["cohort"]).apply(lambda x: x.n if hasattr(x, 'n') else int(str(x).split()[0]))

    # Unique customers per cohort + offset
    cohort_data = df.groupby(["cohort", "period_offset"])["customer_id"].nunique().reset_index()
    cohort_data.columns = ["cohort", "period_offset", "customers"]

    cohort_pivot = cohort_data.pivot_table(index="cohort", columns="period_offset", values="customers")

    # Cohort sizes (period 0)
    cohort_sizes = cohort_pivot[0]

    # Divide by cohort size to get retention rates
    retention = cohort_pivot.divide(cohort_sizes, axis=0)

    return retention


def retention_to_plotly(retention: pd.DataFrame, granularity: str = "monthly"):
    """Convert retention DataFrame to a Plotly heatmap figure."""
    import plotly.graph_objects as go

    z = retention.values
    x_labels = [f"Period {i}" for i in retention.columns]
    y_labels = [str(idx) for idx in retention.index]

    text = [[f"{v*100:.1f}%" if not np.isnan(v) else "" for v in row] for row in z]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=x_labels,
        y=y_labels,
        text=text,
        texttemplate="%{text}",
        colorscale=[
            [0.0,  "#0f172a"],
            [0.2,  "#1e3a5f"],
            [0.5,  "#2563eb"],
            [0.75, "#6366f1"],
            [1.0,  "#a855f7"],
        ],
        zmin=0, zmax=1,
        showscale=True,
        colorbar=dict(
            title="Retention",
            tickformat=".0%",
            tickfont=dict(color="#e2e8f0"),
            titlefont=dict(color="#e2e8f0"),
        ),
        hovertemplate="Cohort: %{y}<br>%{x}<br>Retention: %{text}<extra></extra>",
    ))

    fig.update_layout(
        title=f"Cohort Retention Heatmap ({granularity.title()})",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        xaxis=dict(title="Period Offset", color="#94a3b8"),
        yaxis=dict(title=f"Cohort ({granularity.title()})", color="#94a3b8", autorange="reversed"),
        height=520,
        margin=dict(l=20, r=20, t=60, b=40),
    )
    return fig
