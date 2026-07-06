import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_workflow_planning_mock():
    """Test that planning node handles missing API key gracefully."""
    from nodes.planning import planning_node
    state = {
        "query": "Analyze customer churn",
        "session_id": "test",
        "errors": [], "warnings": [], "history": [], "memory": {}
    }
    result = planning_node(state)
    assert "plan" in result
    assert "intent" in result
    assert "nodes_to_run" in result


def test_workflow_memory_node():
    """Test memory node persists history."""
    from nodes.memory import memory_node
    state = {
        "query": "test query",
        "session_id": "s1",
        "intent": "churn",
        "nodes_to_run": ["analytics"],
        "errors": [], "history": [], "memory": {}
    }
    result = memory_node(state)
    assert len(result["history"]) == 1
    assert result["memory"]["total_runs"] == 1


def test_router_after_validation_pass():
    from graph.router import route_after_validation
    state = {"validated": True}
    assert route_after_validation(state) == "feature_engineering"


def test_router_after_validation_fail():
    from graph.router import route_after_validation
    state = {"validated": False}
    assert route_after_validation(state) == "__end__"


def test_router_after_decision_train():
    from graph.router import route_after_decision
    state = {"should_train": True}
    assert route_after_decision(state) == "training"


def test_router_after_decision_predict():
    from graph.router import route_after_decision
    state = {"should_train": False}
    assert route_after_decision(state) == "prediction"
