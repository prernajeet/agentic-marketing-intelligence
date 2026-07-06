import pandas as pd
from typing import Dict, Any


def compute_product_analytics(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute product performance analytics."""
    if "order_items" not in raw_data:
        return {"error": "No order items data"}

    items_df = pd.DataFrame(raw_data["order_items"])
    items_df["unit_price"] = pd.to_numeric(items_df["unit_price"], errors="coerce")
    items_df["quantity"] = pd.to_numeric(items_df["quantity"], errors="coerce")
    items_df["revenue"] = items_df["unit_price"] * items_df["quantity"]

    product_revenue = items_df.groupby("product_id").agg(
        total_revenue=("revenue", "sum"),
        total_units=("quantity", "sum"),
        order_count=("transaction_id", "nunique"),
    ).reset_index().sort_values("total_revenue", ascending=False)

    result = {
        "total_products_sold": int(items_df["product_id"].nunique()),
        "total_units_sold": int(items_df["quantity"].sum()),
        "top_products_by_revenue": product_revenue.head(10).round(2).to_dict(orient="records"),
    }

    if "products" in raw_data:
        prod_df = pd.DataFrame(raw_data["products"])
        merged = product_revenue.merge(prod_df[["product_id", "product_name"]], on="product_id", how="left")
        result["top_products_named"] = merged.head(10).to_dict(orient="records")

    return result
