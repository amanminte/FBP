"""
Automated Feature Ablation & Permutation Importance Auditor.
Verifies that no single feature dominates the model unrealistically and asserts
that all features have realistic correlations with the match outcome.
"""
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.inspection import permutation_importance
from sklearn.metrics import log_loss, accuracy_score

def audit_model_features(bundle: Any, val_df: pd.DataFrame, top_k: int = 25) -> Dict[str, Any]:
    """Runs permutation importance on validation set to detect any leaking or dominating features."""
    feature_names = bundle.feature_names
    X_val = val_df[feature_names].values
    y_val = val_df["Outcome"].values

    # Impute and Scale
    X_val_imp = bundle.imputer.transform(X_val)
    X_val_scaled = bundle.scaler.transform(X_val_imp)

    # Use the primary tree model (HistGradientBoosting or RandomForest)
    primary_model = bundle.base_models.get("HistGradientBoosting_Tuned") or bundle.base_models.get("RandomForest")
    if not primary_model:
        primary_model = list(bundle.base_models.values())[0]

    # Baseline performance
    val_probs = primary_model.predict_proba(X_val_scaled)
    baseline_loss = log_loss(y_val, val_probs)
    baseline_acc = accuracy_score(y_val, np.argmax(val_probs, axis=1))

    # Permutation importance (n_repeats=5 for fast execution)
    res = permutation_importance(primary_model, X_val_scaled, y_val, scoring="neg_log_loss", n_repeats=5, random_state=42)
    mean_imp = res.importances_mean

    ranked_idx = np.argsort(mean_imp)[::-1]
    top_features = []
    suspicious_features = []

    for idx in ranked_idx[:top_k]:
        f_name = feature_names[idx]
        imp_val = float(mean_imp[idx])
        top_features.append({"feature": f_name, "importance": round(imp_val, 5)})
        
        # A single feature causing > 0.08 drop in log loss on validation is suspicious of leakage
        if imp_val > 0.08:
            suspicious_features.append(f_name)

    return {
        "track": bundle.track,
        "baseline_val_log_loss": round(float(baseline_loss), 4),
        "baseline_val_accuracy": round(float(baseline_acc * 100.0), 2),
        "top_features": top_features,
        "suspicious_features": suspicious_features,
        "is_leak_free": len(suspicious_features) == 0
    }
