import pytest
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def sample_customer_features():
    return pd.DataFrame({
        "customer_id": range(1, 51),
        "recency_days": [i * 3 for i in range(1, 51)],
        "frequency": [max(1, 20 - i) for i in range(50)],
        "monetary": [float(100 * (50 - i)) for i in range(50)],
        "avg_order_value": [float(50 + i * 2) for i in range(50)],
        "std_order_value": [10.0] * 50,
        "customer_lifetime_days": [365] * 50,
        "purchase_rate": [0.05] * 50,
    })


def test_compute_rfm_returns_dict(sample_customer_features):
    from analytics.rfm import compute_rfm
    result = compute_rfm(sample_customer_features)
    assert isinstance(result, dict)
    assert "scores" in result
    assert "segment_distribution" in result
    assert "total_customers" in result


def test_compute_rfm_correct_count(sample_customer_features):
    from analytics.rfm import compute_rfm
    result = compute_rfm(sample_customer_features)
    assert result["total_customers"] == 50


def test_compute_rfm_segments_valid(sample_customer_features):
    from analytics.rfm import compute_rfm
    result = compute_rfm(sample_customer_features)
    valid_segments = {
        "Champions", "Loyal Customers", "Potential Loyalists",
        "At Risk", "Lost Customers", "New Customers", "Promising", "Need Attention"
    }
    for score in result["scores"]:
        assert score["rfm_segment"] in valid_segments


def test_compute_rfm_missing_column():
    from analytics.rfm import compute_rfm
    bad_df = pd.DataFrame({"customer_id": [1, 2], "recency_days": [10, 20]})
    with pytest.raises(ValueError):
        compute_rfm(bad_df)
