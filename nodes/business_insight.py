# from graph.state import WorkflowState
from llm.gemini_client import gemini_client
from utils.logger import logger
import json

INSIGHT_PROMPT = """You are a senior marketing analyst. Based on the analytics results below, provide 5-7 concise, actionable business insights. Focus on revenue impact, customer behavior patterns, and growth opportunities.

Query: {query}
Intent: {intent}
RFM Summary: {rfm_summary}
Churn Rate: {churn_rate}
Revenue Summary: {revenue_summary}
Campaign Performance: {campaign_summary}

Provide insights as numbered list. Be specific and data-driven."""


def business_insight_node(state: dict) -> dict:
    """Gemini-powered business insights generation."""
    logger.info("Business insight node running")
    try:
        rfm = state.get("rfm_results") or {}
        churn = state.get("churn_predictions") or {}
        revenue = state.get("revenue_analytics") or {}
        campaign = state.get("campaign_analytics") or {}

        rfm_summary = str(rfm.get("segment_distribution", {}))
        churn_rate = churn.get("churn_rate", "N/A")
        revenue_summary = str(revenue.get("summary", {}))
        campaign_summary = str(campaign.get("summary", {}))

        prompt = INSIGHT_PROMPT.format(
            query=state.get("query", ""),
            intent=state.get("intent", ""),
            rfm_summary=rfm_summary,
            churn_rate=churn_rate,
            revenue_summary=revenue_summary,
            campaign_summary=campaign_summary,
        )
        insights = gemini_client.generate(prompt)
        state["business_insights"] = insights
    except Exception as e:
        logger.error(f"Business insight error: {e}")
        state["business_insights"] = "Unable to generate insights due to an error."
        state["errors"] = state.get("errors", []) + [f"Insights: {e}"]
    return state
