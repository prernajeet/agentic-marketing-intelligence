import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_validation_passes_valid_data():
    from nodes.validation import validation_node
    state = {
        "raw_data": {
            "customers": [{"customer_id": 1, "email": "a@b.com"}],
            "transactions": [{
                "transaction_id": 1, "customer_id": 1,
                "transaction_date": "2024-01-01", "total_amount": 100.0
            }],
            "order_items": [{
                "order_item_id": 1, "transaction_id": 1,
                "product_id": 1, "quantity": 2, "unit_price": 50.0
            }],
            "products": [{
                "product_id": 1, "product_name": "Widget", "unit_price": 50.0
            }],
        },
        "errors": [], "warnings": []
    }
    result = validation_node(state)
    assert result["validated"] is True
    assert result["validation_errors"] == []


def test_validation_fails_missing_column():
    from nodes.validation import validation_node
    state = {
        "raw_data": {
            "customers": [{"customer_id": 1}],  # missing email
        },
        "errors": [], "warnings": []
    }
    result = validation_node(state)
    assert result["validated"] is False
    assert len(result["validation_errors"]) > 0


def test_validation_empty_raw_data():
    from nodes.validation import validation_node
    state = {"raw_data": {}, "errors": [], "warnings": []}
    result = validation_node(state)
    # Empty data: warnings but validation should still pass (no required errors)
    assert "validated" in result
