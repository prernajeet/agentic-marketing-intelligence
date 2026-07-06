from typing import Dict, Any


def compare_models(model_results: Dict[str, Any]) -> Dict[str, Any]:
    """Compare all trained models and return a summary comparison."""
    comparison = {}
    for name, result in model_results.items():
        if "error" in result:
            comparison[name] = {"status": "error", "error": result["error"]}
        else:
            comparison[name] = {
                "status": "ok",
                "task": result.get("task", "unknown"),
                "metrics": result.get("metrics", {}),
            }
    return comparison


def select_champion(comparison: Dict[str, Any]) -> str:
    """Select the champion model by best primary metric."""
    best_name = None
    best_score = -999

    for name, result in comparison.items():
        if result.get("status") != "ok":
            continue
        metrics = result.get("metrics", {})
        # For classification: use roc_auc; for regression: use r2
        score = metrics.get("roc_auc", metrics.get("r2", -999))
        if score > best_score:
            best_score = score
            best_name = name

    return best_name or "Unknown"
