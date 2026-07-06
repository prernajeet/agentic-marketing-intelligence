import httpx
from utils.logger import logger

def trigger_crm_webhook(customer_id: int, email: str, name: str, churn_prob: float) -> bool:
    """Dispatches a payload mock webhook to trigger CRM retention campaigns (e.g. HubSpot)."""
    payload = {
        "event": "customer.high_risk_churn",
        "customer_id": customer_id,
        "email": email,
        "name": name,
        "churn_probability": round(churn_prob, 4),
        "trigger_source": "Agentic Marketing Intelligence Platform",
        "actions_required": ["Enroll in Win-Back Email Sequence", "Assign Customer Success Rep"]
    }
    logger.info(f"Triggering outbound CRM Webhook for customer {customer_id} to HubSpot: {payload}")
    return True
