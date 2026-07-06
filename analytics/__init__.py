from .rfm import compute_rfm
from .segmentation import compute_segmentation
from .customer import compute_customer_analytics
from .revenue import compute_revenue_analytics
from .campaign import compute_campaign_analytics
from .product import compute_product_analytics
__all__ = [
    "compute_rfm", "compute_segmentation", "compute_customer_analytics",
    "compute_revenue_analytics", "compute_campaign_analytics", "compute_product_analytics"
]
