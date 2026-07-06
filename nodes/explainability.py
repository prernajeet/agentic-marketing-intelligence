# from graph.state import WorkflowState
from utils.logger import logger
import pandas as pd
import numpy as np
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


def explainability_node(state: dict) -> dict:
    """Compute SHAP values and feature importances."""
    logger.info("Explainability node running")
    model_results = state.get("model_results", {})
    features = state.get("features", {})

    if not model_results or "customer_features" not in features:
        state["shap_values"] = {}
        state["feature_importances"] = {}
        return state

    cf_df = pd.DataFrame(features["customer_features"])

    fi_dict = {}
    shap_dict = {}

    for model_name, result in model_results.items():
        model = result.get("model")
        if model is None:
            continue
        feature_cols = result.get("feature_cols")
        if not feature_cols:
            continue
            
        try:
            X_model = cf_df[feature_cols].fillna(0)

            # Feature Importances alignment
            if hasattr(model, "feature_importances_"):
                fi = dict(zip(feature_cols, model.feature_importances_.tolist()))
                fi_dict[model_name] = fi

            # SHAP Values alignment and extraction
            if SHAP_AVAILABLE and hasattr(model, "predict"):
                explainer = shap.TreeExplainer(model)
                shap_vals = explainer.shap_values(X_model.head(100))
                
                if hasattr(shap_vals, "values"):
                    shap_vals = shap_vals.values
                
                # If shap_vals is a list (often [class_0_vals, class_1_vals])
                if isinstance(shap_vals, list):
                    shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]
                
                # Convert to numpy array safely
                if not isinstance(shap_vals, np.ndarray):
                    shap_vals = np.array(shap_vals)
                
                # If shape is 3D (samples, features, classes)
                if len(shap_vals.shape) == 3:
                    shap_vals = shap_vals[:, :, 1] if shap_vals.shape[2] > 1 else shap_vals[:, :, 0]
                
                mean_shap = np.abs(shap_vals).mean(axis=0).tolist()
                shap_dict[model_name] = dict(zip(feature_cols, mean_shap))
        except Exception as e:
            logger.warning(f"SHAP error for {model_name}: {e}")

    state["feature_importances"] = fi_dict
    state["shap_values"] = shap_dict
    return state
