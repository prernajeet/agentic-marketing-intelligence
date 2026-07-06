import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_settings_loads():
    from config.settings import settings, get_settings
    s = get_settings()
    assert s is not None
    assert hasattr(s, "database_url")
    assert hasattr(s, "gemini_api_key")
    assert hasattr(s, "gemini_model")
    assert hasattr(s, "api_port")
    assert s.api_port == 8000


def test_settings_paths():
    from config.settings import settings
    assert settings.raw_data_path is not None
    assert settings.processed_data_path is not None
    assert settings.model_registry_path is not None


def test_settings_defaults():
    from config.settings import settings
    assert settings.gemini_model == "gemini-2.5-flash"
    assert settings.api_host == "0.0.0.0"
