import pandas as pd
from typing import Dict, Any


def compute_campaign_analytics(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute campaign performance analytics."""
    if "campaigns" not in raw_data:
        return {"error": "No campaign data"}

    camp_df = pd.DataFrame(raw_data["campaigns"])
    result = {"total_campaigns": len(camp_df)}

    if "campaign_type" in camp_df.columns:
        result["by_type"] = camp_df["campaign_type"].value_counts().to_dict()

    if "channel" in camp_df.columns:
        result["by_channel"] = camp_df["channel"].value_counts().to_dict()

    if "campaign_responses" in raw_data:
        resp_df = pd.DataFrame(raw_data["campaign_responses"])
        total_responses = len(resp_df)
        conversions = int(resp_df["converted"].sum()) if "converted" in resp_df.columns else 0
        conv_rate = round(conversions / max(total_responses, 1) * 100, 2)
        total_revenue = float(resp_df["revenue_generated"].sum()) if "revenue_generated" in resp_df.columns else 0.0

        result["summary"] = {
            "total_responses": total_responses,
            "total_conversions": conversions,
            "conversion_rate_pct": conv_rate,
            "total_revenue_generated": round(total_revenue, 2),
        }

        if "campaign_id" in resp_df.columns:
            camp_perf = resp_df.groupby("campaign_id").agg(
                responses=("response_id" if "response_id" in resp_df.columns else "campaign_id", "count"),
                conversions=("converted", "sum"),
            ).reset_index()
            result["campaign_performance"] = camp_perf.head(20).to_dict(orient="records")

    return result
