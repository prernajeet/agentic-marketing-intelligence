import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import pandas as pd


def rfm_segment_pie(segment_distribution: Dict[str, int]) -> go.Figure:
    """Pie chart of RFM segments."""
    labels = list(segment_distribution.keys())
    values = list(segment_distribution.values())
    fig = px.pie(
        names=labels, values=values,
        title="Customer RFM Segments",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(template="plotly_dark", showlegend=True)
    return fig


def revenue_trend_line(monthly_revenue: Dict[str, float]) -> go.Figure:
    """Line chart of monthly revenue."""
    df = pd.DataFrame(list(monthly_revenue.items()), columns=["Month", "Revenue"])
    df = df.sort_values("Month")
    fig = px.line(
        df, x="Month", y="Revenue",
        title="Monthly Revenue Trend",
        markers=True,
    )
    fig.update_layout(template="plotly_dark", xaxis_tickangle=-45)
    return fig


def churn_gauge(churn_rate: float) -> go.Figure:
    """Gauge chart for churn rate."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=churn_rate * 100,
        title={"text": "Churn Rate (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#EF553B"},
            "steps": [
                {"range": [0, 20], "color": "#2ecc71"},
                {"range": [20, 50], "color": "#f39c12"},
                {"range": [50, 100], "color": "#e74c3c"},
            ],
        },
    ))
    fig.update_layout(template="plotly_dark")
    return fig


def feature_importance_bar(importances: Dict[str, float], model_name: str = "") -> go.Figure:
    """Horizontal bar chart of feature importances."""
    items = sorted(importances.items(), key=lambda x: abs(x[1]), reverse=True)[:15]
    features = [x[0] for x in items]
    values = [x[1] for x in items]
    fig = px.bar(
        x=values, y=features,
        orientation="h",
        title=f"Feature Importances — {model_name}",
        color=values,
        color_continuous_scale="Viridis",
    )
    fig.update_layout(template="plotly_dark", yaxis={"autorange": "reversed"})
    return fig


def segment_scatter(segments_data: List[Dict], x_col: str = "recency_days",
                    y_col: str = "monetary", color_col: str = "segment_label") -> go.Figure:
    """Scatter plot of customer segments with bar-chart fallback."""
    df = pd.DataFrame(segments_data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No segment data available", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(color="#94a3b8", size=14))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", height=350)
        return fig

    # Dynamically find available numeric columns for x/y
    available_numeric = [c for c in ["recency_days", "frequency", "monetary",
                                      "avg_order_value", "clv_12m"] if c in df.columns]

    if x_col not in df.columns:
        x_col = available_numeric[0] if len(available_numeric) > 0 else None
    if y_col not in df.columns:
        y_col = available_numeric[1] if len(available_numeric) > 1 else None

    # If we have both axes → scatter
    if x_col and y_col:
        fig = px.scatter(
            df, x=x_col, y=y_col,
            color=color_col if color_col in df.columns else None,
            title="Customer Segments",
            opacity=0.7,
            color_discrete_sequence=px.colors.qualitative.Bold,
            hover_data=[c for c in ["customer_id", "segment_label"] if c in df.columns],
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
        )
        return fig

    # Fallback → bar chart of segment counts
    if color_col in df.columns:
        counts = df[color_col].value_counts().reset_index()
        counts.columns = ["Segment", "Count"]
        fig = px.bar(
            counts, x="Segment", y="Count",
            title="Customer Segment Distribution",
            color="Segment",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            showlegend=False,
        )
        return fig

    # Ultimate fallback — empty annotated chart
    fig = go.Figure()
    fig.add_annotation(text="Insufficient data for segmentation chart",
                       xref="paper", yref="paper", x=0.5, y=0.5,
                       showarrow=False, font=dict(color="#94a3b8", size=13))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", height=350)
    return fig


def campaign_funnel(campaign_data: Dict[str, Any]) -> go.Figure:
    """Funnel chart for campaign performance."""
    summary = campaign_data.get("summary", {})
    total_campaigns = campaign_data.get("total_campaigns", 0)
    total_responses = summary.get("total_responses", 0)
    total_conversions = summary.get("total_conversions", 0)

    fig = go.Figure(go.Funnel(
        y=["Campaigns", "Responses", "Conversions"],
        x=[total_campaigns, total_responses, total_conversions],
        textinfo="value+percent initial",
        marker={"color": ["#636EFA", "#EF553B", "#00CC96"]},
    ))
    fig.update_layout(title="Campaign Funnel", template="plotly_dark")
    return fig


def cohort_retention_heatmap(retention_df: pd.DataFrame) -> go.Figure:
    """Create a Plotly Heatmap for Cohort Retention."""
    if retention_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No Cohort Data", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
        
    text_labels = []
    for val_row in retention_df.values:
        row_labels = []
        for val in val_row:
            if pd.isna(val):
                row_labels.append("")
            else:
                row_labels.append(f"{val*100:.1f}%")
        text_labels.append(row_labels)
        
    fig = go.Figure(data=go.Heatmap(
        z=retention_df.values * 100,
        x=[f"Month {col}" for col in retention_df.columns],
        y=retention_df.index,
        colorscale="RdPu",
        text=text_labels,
        texttemplate="%{text}",
        hoverinfo="z",
        showscale=True,
    ))
    
    fig.update_layout(
        title="Customer Cohort Monthly Retention Rate (%)",
        xaxis_title="Lifetime Month Index",
        yaxis_title="Cohort Registration Month",
        template="plotly_dark",
    )
    return fig
