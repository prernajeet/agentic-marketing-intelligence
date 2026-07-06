import json
from datetime import datetime, timezone
from typing import Any, Dict


def flatten_dict(d: Dict, parent_key: str = "", sep: str = ".") -> Dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def safe_json_loads(s: str) -> Any:
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return {}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
