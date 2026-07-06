# from graph.state import WorkflowState
from llm.gemini_client import gemini_client
from utils.logger import logger
from pathlib import Path
from config.settings import settings
import json
from datetime import datetime

REPORT_PROMPT = """You are a Chief Marketing Analytics Officer. Write a comprehensive executive report (400-600 words) summarizing:
1. Executive Summary
2. Key Findings (bullet points)
3. Customer Intelligence (RFM, segments, churn)
4. Revenue Performance
5. Campaign Effectiveness
6. ML Model Performance
7. Strategic Recommendations
8. Next Steps

Query: {query}
Insights: {insights}
Recommendations: {recommendations}
Churn Rate: {churn_rate}
Champion Model: {champion_model}

Write in professional executive tone."""


def reporting_node(state: dict) -> dict:
    """Gemini-powered executive report generation."""
    logger.info("Reporting node running")
    try:
        recommendations = state.get("recommendations", [])
        reco_text = json.dumps(recommendations[:3], indent=2) if recommendations else "N/A"
        churn = state.get("churn_predictions") or {}

        prompt = REPORT_PROMPT.format(
            query=state.get("query", ""),
            insights=state.get("business_insights", "")[:1500],
            recommendations=reco_text,
            churn_rate=churn.get("churn_rate", "N/A"),
            champion_model=state.get("champion_model", "N/A"),
        )
        report = gemini_client.generate(prompt)
        state["executive_report"] = report

        # Save report to disk
        reports_dir = Path(settings.model_registry_path).parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"report_{ts}.md"
        report_path.write_text(report, encoding="utf-8")
        logger.info(f"Report saved to {report_path}")
    except Exception as e:
        logger.error(f"Reporting error: {e}")
        state["executive_report"] = "Report generation failed."
    return state
