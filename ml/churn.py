import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, accuracy_score
from typing import Dict, Any
import warnings
warnings.filterwarnings("ignore")

try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False


def _build_churn_target(df: pd.DataFrame) -> pd.Series:
    """Create binary churn target: 1 if recency_days > 90."""
    return (df["recency_days"] > 90).astype(int)


def _get_feature_cols(df: pd.DataFrame) -> list:
    exclude = ["customer_id", "last_purchase_date", "first_purchase_date",
               "gender", "country", "segment_cluster", "segment_label",
               "rfm_segment", "rfm_score"]
    return [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]


def train_churn_model(customer_features: pd.DataFrame, strategy: Dict = None) -> Dict[str, Any]:
    """Train multiple classifiers for churn prediction and return all results."""
    df = customer_features.copy()
    feature_cols = _get_feature_cols(df)
    target = _build_churn_target(df)

    X = df[feature_cols].fillna(0)
    y = target

    if len(X) < 20:
        raise ValueError("Not enough data to train churn model")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
    }

    if XGB_AVAILABLE:
        models["XGBoost"] = XGBClassifier(n_estimators=100, random_state=42,
                                           eval_metric="logloss", verbosity=0)
    if LGB_AVAILABLE:
        models["LightGBM"] = LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)

    results = {}
    for name, model in models.items():
        try:
            if name in ["LogisticRegression"]:
                model.fit(X_train_s, y_train)
                y_pred = model.predict(X_test_s)
                y_prob = model.predict_proba(X_test_s)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_prob = model.predict_proba(X_test)[:, 1]

            results[name] = {
                "model": model,
                "scaler": scaler if name == "LogisticRegression" else None,
                "feature_cols": feature_cols,
                "metrics": {
                    "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
                    "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
                    "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
                    "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
                    "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
                },
                "task": "churn_classification",
            }
        except Exception as e:
            results[name] = {"error": str(e)}

    return results


def predict_churn(customer_features: pd.DataFrame, model_results: Dict) -> Dict[str, Any]:
    """Run churn predictions using the best available model."""
    if not model_results:
        return {"error": "No trained models available"}

    # Pick best model by ROC AUC
    best_name = None
    best_auc = -1
    for name, res in model_results.items():
        auc = res.get("metrics", {}).get("roc_auc", 0)
        if auc > best_auc:
            best_auc = auc
            best_name = name

    if best_name is None:
        return {"error": "No valid models"}

    best = model_results[best_name]
    model = best["model"]
    feature_cols = best["feature_cols"]
    scaler = best.get("scaler")

    df = customer_features.copy()
    X = df[feature_cols].fillna(0)
    if scaler:
        X = scaler.transform(X)

    probs = model.predict_proba(X)[:, 1]
    labels = (probs > 0.5).astype(int)

    df["churn_probability"] = probs.round(4)
    df["churn_label"] = labels

    churn_rate = float(labels.mean())
    high_risk = df[df["churn_probability"] > 0.7][["customer_id", "churn_probability"]]

    return {
        "churn_rate": round(churn_rate, 4),
        "total_customers": len(df),
        "churned_count": int(labels.sum()),
        "high_risk_count": len(high_risk),
        "champion_model": best_name,
        "predictions": df[["customer_id", "churn_probability", "churn_label"]].to_dict(orient="records"),
        "high_risk_customers": high_risk.head(20).to_dict(orient="records"),
    }
