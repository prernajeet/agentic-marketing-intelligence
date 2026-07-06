import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from database.models import (
    Customer, Product, Category, Supplier, Transaction, OrderItem,
    Campaign, CampaignResponse, WebsiteSession, CustomerBehavior
)
from utils.logger import logger
from config.settings import settings


def load_csv_to_db(db: Session, data_dir: Path | None = None) -> dict:
    """Load all source CSV files into PostgreSQL."""
    data_dir = data_dir or settings.raw_data_path
    results = {}

    model_map = {
        "categories.csv": Category,
        "suppliers.csv": Supplier,
        "products.csv": Product,
        "customers.csv": Customer,
        "transactions.csv": Transaction,
        "order_items.csv": OrderItem,
        "campaigns.csv": Campaign,
        "campaign_responses.csv": CampaignResponse,
        "website_sessions.csv": WebsiteSession,
        "customer_behavior.csv": CustomerBehavior,
    }

    for filename, model_cls in model_map.items():
        filepath = data_dir / filename
        if not filepath.exists():
            logger.warning(f"CSV not found: {filepath}")
            results[filename] = {"status": "skipped", "rows": 0}
            continue
        try:
            df = pd.read_csv(filepath)
            rows = df.to_dict(orient="records")
            cleaned_rows = []
            for row in rows:
                cleaned_row = {}
                for k, v in row.items():
                    if pd.isna(v):
                        cleaned_row[k] = None
                    elif isinstance(v, float) and v.is_integer():
                        cleaned_row[k] = int(v)
                    else:
                        cleaned_row[k] = v
                cleaned_rows.append(cleaned_row)
                
            db.bulk_insert_mappings(model_cls, cleaned_rows)
            db.commit()
            results[filename] = {"status": "ok", "rows": len(cleaned_rows)}
            logger.info(f"Loaded {len(cleaned_rows)} rows into {model_cls.__tablename__}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading {filename}: {e}")
            results[filename] = {"status": "error", "message": str(e)}
    return results
