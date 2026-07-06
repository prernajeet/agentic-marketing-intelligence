# from graph.state import WorkflowState
from utils.logger import logger
import pandas as pd
import numpy as np


def simulation_node(state: dict) -> dict:
    """What-if simulation based on parameter changes."""
    logger.info("Simulation node running")
    features = state.get("features", {})
    model_results = state.get("model_results", {})
    simulation_params = state.get("env_context", {}).get("simulation_params", {})

    if not simulation_params or "customer_features" not in features:
        state["simulation_results"] = {"message": "No simulation parameters provided"}
        return state

    try:
        cf_df = pd.DataFrame(features["customer_features"])
        # Apply parameter changes to numerical features
        cf_df_sim = cf_df.copy()
        for col, delta in simulation_params.items():
            if col in cf_df_sim.columns:
                cf_df_sim[col] = cf_df_sim[col] * (1 + delta / 100.0)

        results = {}
        for model_name, result in model_results.items():
            model = result.get("model")
            if model is None:
                continue
            feature_cols = result.get("feature_cols")
            if not feature_cols:
                continue
            try:
                X_model = cf_df[feature_cols].fillna(0)
                X_sim_model = cf_df_sim[feature_cols].fillna(0)
                
                scaler = result.get("scaler")
                if scaler:
                    X_model_s = scaler.transform(X_model)
                    X_sim_model_s = scaler.transform(X_sim_model)
                    baseline_preds = model.predict_proba(X_model_s)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_model_s)
                    sim_preds = model.predict_proba(X_sim_model_s)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_sim_model_s)
                else:
                    baseline_preds = model.predict_proba(X_model)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_model)
                    sim_preds = model.predict_proba(X_sim_model)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_sim_model)
                
                results[model_name] = {
                    "baseline_mean": float(np.mean(baseline_preds)),
                    "simulated_mean": float(np.mean(sim_preds)),
                    "delta": float(np.mean(sim_preds) - np.mean(baseline_preds)),
                    "affected_customers": int(np.sum(sim_preds > 0.5)),
                }
            except Exception as e:
                logger.warning(f"Simulation error for {model_name}: {e}")

        state["simulation_results"] = {
            "parameters_applied": simulation_params,
            "results": results,
        }
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        state["simulation_results"] = {"error": str(e)}
    return state
