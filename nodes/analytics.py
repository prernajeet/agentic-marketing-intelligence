# from graph.state import WorkflowState
from analytics.rfm import compute_rfm
from analytics.segmentation import compute_segmentation
from analytics.customer import compute_customer_analytics
from analytics.revenue import compute_revenue_analytics
from analytics.campaign import compute_campaign_analytics
from analytics.product import compute_product_analytics
from utils.logger import logger
import pandas as pd


def analytics_node(state: dict) -> dict:
    """Run all analytics modules and store results in state."""
    logger.info("Analytics node running")
    features = state.get("features", {})
    raw_data = state.get("raw_data", {})

    try:
        if "customer_features" in features:
            cf_df = pd.DataFrame(features["customer_features"])
            rfm = compute_rfm(cf_df)
            state["rfm_results"] = rfm
            state["segment_results"] = compute_segmentation(cf_df)
    except Exception as e:
        logger.error(f"RFM/Segmentation error: {e}")
        state["errors"] = state.get("errors", []) + [str(e)]

    try:
        state["customer_analytics"] = compute_customer_analytics(raw_data)
    except Exception as e:
        logger.error(f"Customer analytics error: {e}")

    try:
        state["revenue_analytics"] = compute_revenue_analytics(raw_data)
    except Exception as e:
        logger.error(f"Revenue analytics error: {e}")

    try:
        state["campaign_analytics"] = compute_campaign_analytics(raw_data)
    except Exception as e:
        logger.error(f"Campaign analytics error: {e}")

    try:
        state["product_analytics"] = compute_product_analytics(raw_data)
    except Exception as e:
        logger.error(f"Product analytics error: {e}")

    return state
