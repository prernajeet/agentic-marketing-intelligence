import joblib
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
from config.settings import settings
from utils.logger import logger


class ModelRegistry:
    """Simple file-based model registry for saving and loading trained models."""

    def __init__(self, registry_dir: Optional[Path] = None):
        self.registry_dir = registry_dir or settings.model_registry_path
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_path = self.registry_dir / "registry.json"
        self._metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        if self.metadata_path.exists():
            return json.loads(self.metadata_path.read_text())
        return {}

    def _save_metadata(self):
        self.metadata_path.write_text(json.dumps(self._metadata, indent=2, default=str))

    def register(self, model: Any, name: str, task: str, metrics: Dict, version: str = None) -> str:
        """Save a model and register its metadata."""
        version = version or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_path = self.registry_dir / f"{name}_{version}.joblib"
        joblib.dump(model, model_path)

        self._metadata[f"{name}_{version}"] = {
            "name": name,
            "version": version,
            "task": task,
            "metrics": metrics,
            "path": str(model_path),
            "registered_at": datetime.utcnow().isoformat(),
            "is_champion": False,
        }
        self._save_metadata()
        logger.info(f"Registered model: {name} v{version}")
        return version

    def promote_to_champion(self, name: str, version: str, task: str):
        """Mark a model version as the champion for its task."""
        champion_path = self.registry_dir / f"{task}_champion.joblib"
        model_key = f"{name}_{version}"
        if model_key in self._metadata:
            model = joblib.load(self._metadata[model_key]["path"])
            joblib.dump(model, champion_path)
            self._metadata[model_key]["is_champion"] = True
            self._save_metadata()
            logger.info(f"Champion promoted: {name} v{version} for task {task}")

    def load_champion(self, task: str) -> Optional[Any]:
        """Load the champion model for a task."""
        champion_path = self.registry_dir / f"{task}_champion.joblib"
        if champion_path.exists():
            return joblib.load(champion_path)
        return None

    def list_models(self) -> Dict:
        return self._metadata
