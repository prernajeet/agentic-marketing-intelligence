# from graph.state import WorkflowState
from llm.gemini_client import gemini_client
from utils.logger import logger
import json

PLANNING_PROMPT = """You are the planning brain of an Agentic Marketing Intelligence Platform.
Given the user query below, output a JSON object with these fields:
- intent: one of [rfm, segmentation, churn, clv, revenue, campaign, product, customer, simulation, report, general]
- nodes_to_run: list of node names required (from: [data_retrieval, validation, feature_engineering, analytics, ml_strategy, training, evaluation, prediction, explainability, simulation, business_insight, recommendation, reporting])
- data_sources: list of tables needed (from: [customers, products, categories, suppliers, transactions, order_items, campaigns, campaign_responses, website_sessions, customer_behavior])
- should_train: true/false whether new model training is required
- summary: one sentence summary of what you will do

User Query: {query}

Respond ONLY with valid JSON, no markdown."""


def planning_node(state: dict) -> dict:
    """Gemini-powered planning node that decides the workflow path."""
    query = state.get("query", "")
    logger.info(f"Planning node: {query[:60]}")
    try:
        prompt = PLANNING_PROMPT.format(query=query)
        response = gemini_client.generate(prompt)
        # Extract JSON from response
        text = response.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        plan = json.loads(text)
        state["plan"] = plan
        state["intent"] = plan.get("intent", "general")
        state["nodes_to_run"] = plan.get("nodes_to_run", [])
    except Exception as e:
        logger.error(f"Planning node error: {e}")
        state["plan"] = {"error": str(e)}
        state["intent"] = "general"
        state["nodes_to_run"] = ["data_retrieval", "validation", "feature_engineering", "analytics", "business_insight", "recommendation", "reporting"]
        state["errors"] = state.get("errors", []) + [f"Planning error: {e}"]
    return state
