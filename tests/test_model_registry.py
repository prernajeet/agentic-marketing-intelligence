import pytest
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def tmp_registry(tmp_path):
    from ml.model_registry import ModelRegistry
    return ModelRegistry(registry_dir=tmp_path)


class MockModel:
    def predict(self, X):
        return [0] * len(X)


def test_registry_register(tmp_registry):
    model = MockModel()
    version = tmp_registry.register(
        model=model, name="TestModel", task="churn",
        metrics={"roc_auc": 0.85}, version="v1"
    )
    assert version == "v1"
    models = tmp_registry.list_models()
    assert "TestModel_v1" in models


def test_registry_promote_champion(tmp_registry):
    model = MockModel()
    version = tmp_registry.register(
        model=model, name="TestModel", task="churn",
        metrics={"roc_auc": 0.85}, version="v2"
    )
    tmp_registry.promote_to_champion("TestModel", version, "churn")
    champion = tmp_registry.load_champion("churn")
    assert champion is not None


def test_registry_load_nonexistent_champion(tmp_registry):
    champion = tmp_registry.load_champion("unknown_task")
    assert champion is None
