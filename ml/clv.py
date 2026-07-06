import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, Any
import warnings
warnings.filterwarnings("ignore")

try:
    from xgboost import XGBRegressor
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    from lightgbm import LGBMRegressor
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False


def _get_feature_cols(df: pd.DataFrame) -> list:
    exclude = ["customer_id", "last_purchase_date", "first_purchase_date",
               "gender", "country", "monetary"]
    return [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]


def train_clv_model(customer_features: pd.DataFrame, strategy: Dict = None) -> Dict[str, Any]:
    """Train CLV regression models."""
    df = customer_features.copy()
    if "monetary" not in df.columns:
        raise ValueError("Missing monetary column for CLV training")

    feature_cols = _get_feature_cols(df)
    X = df[feature_cols].fillna(0)
    y = df["monetary"].fillna(0)

    if len(X) < 20:
        raise ValueError("Not enough data for CLV model")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "Ridge": Ridge(alpha=1.0),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
    }
    if XGB_AVAILABLE:
        models["XGBoost"] = XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
    if LGB_AVAILABLE:
        models["LightGBM"] = LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)

    results = {}
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            mae = float(mean_absolute_error(y_test, y_pred))
            r2 = float(r2_score(y_test, y_pred))
            results[name] = {
                "model": model,
                "feature_cols": feature_cols,
                "metrics": {"rmse": round(rmse, 4), "mae": round(mae, 4), "r2": round(r2, 4)},
                "task": "clv_regression",
            }
        except Exception as e:
            results[name] = {"error": str(e)}
    return results


def predict_clv(customer_features: pd.DataFrame, model_results: Dict) -> Dict[str, Any]:
    """Predict CLV using best regression model."""
    if not model_results:
        return {"error": "No trained CLV models"}

    best_name = None
    best_r2 = -999
    for name, res in model_results.items():
        r2 = res.get("metrics", {}).get("r2", -999)
        if r2 > best_r2:
            best_r2 = r2
            best_name = name

    if best_name is None:
        return {"error": "No valid CLV models"}

    best = model_results[best_name]
    model = best["model"]
    feature_cols = best["feature_cols"]
    df = customer_features.copy()
    X = df[feature_cols].fillna(0)

    clv_12m = model.predict(X)
    clv_24m = clv_12m * 1.8
    clv_lifetime = clv_12m * 5.0

    df["clv_12m"] = clv_12m.round(2)
    df["clv_24m"] = clv_24m.round(2)
    df["clv_lifetime"] = clv_lifetime.round(2)

    return {
        "champion_model": best_name,
        "total_customers": len(df),
        "avg_clv_12m": round(float(clv_12m.mean()), 2),
        "avg_clv_lifetime": round(float(clv_lifetime.mean()), 2),
        "predictions": df[["customer_id", "clv_12m", "clv_24m", "clv_lifetime"]].to_dict(orient="records"),
    }
