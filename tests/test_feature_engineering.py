import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def raw_state():
    return {
        "raw_data": {
            "customers": [
                {"customer_id": i, "email": f"user{i}@test.com",
                 "registration_date": "2022-01-01", "gender": "M", "country": "US"}
                for i in range(1, 21)
            ],
            "transactions": [
                {"transaction_id": j, "customer_id": (j % 20) + 1,
                 "transaction_date": f"2024-0{(j%9)+1}-01",
                 "total_amount": float(50 + j * 10)}
                for j in range(1, 51)
            ],
        },
        "validated": True, "errors": [], "warnings": []
    }


def test_feature_engineering_produces_features(raw_state):
    from nodes.feature_engineering import feature_engineering_node
    result = feature_engineering_node(raw_state)
    assert "features" in result
    assert "customer_features" in result["features"]


def test_feature_engineering_correct_columns(raw_state):
    from nodes.feature_engineering import feature_engineering_node
    import pandas as pd
    result = feature_engineering_node(raw_state)
    features = result["features"]["customer_features"]
    df = pd.DataFrame(features)
    assert "customer_id" in df.columns
    assert "recency_days" in df.columns
    assert "frequency" in df.columns
    assert "monetary" in df.columns
