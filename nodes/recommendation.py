# from graph.state import WorkflowState
from llm.gemini_client import gemini_client
from utils.logger import logger
import json

RECO_PROMPT = """You are a marketing strategy consultant. Based on the analytics and insights below, generate 5 specific, actionable marketing recommendations.
Format as JSON array with objects having: title, description, priority (1-5), expected_impact, actions (list of steps).

Insights: {insights}
Churn Rate: {churn_rate}
Top Segments: {segments}

Respond ONLY with a valid JSON array."""


def recommendation_node(state: dict) -> dict:
    """Gemini-powered recommendation generation."""
    logger.info("Recommendation node running")
    try:
        insights = state.get("business_insights", "")
        churn = state.get("churn_predictions") or {}
        segments = state.get("segment_results") or {}

        prompt = RECO_PROMPT.format(
            insights=insights[:1000],
            churn_rate=churn.get("churn_rate", "N/A"),
            segments=str(segments.get("segment_counts", {})),
        )
        response = gemini_client.generate(prompt)
        text = response.strip().lstrip("```json").rstrip("```").strip()
        recommendations = json.loads(text)
        state["recommendations"] = recommendations
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        state["recommendations"] = [
            {"title": "Review churn risk customers", "description": "Focus retention efforts",
             "priority": 1, "expected_impact": "5-10% churn reduction", "actions": ["Identify at-risk customers", "Send retention offers"]}
        ]
    return state
