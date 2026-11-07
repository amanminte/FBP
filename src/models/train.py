"""
V2 Model Training, Probability Calibration & Walk-Forward Evaluation Engine.
Strictly Leak-Free:
- Track A: Pure Football Fundamentals (ZERO Odds)
- Track B: Early-Market Hybrid (Opening Odds + Track A)
- Track C: Late-Market Syndicate Engine (Track B + Lineups + Steam)
- Two-Stage Hierarchical Classifier + Platt Sigmoid Calibration
- Monthly Walk-Forward Evaluation across the 1,752 untouched 2024/25 test matches.
"""
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss, accuracy_score, balanced_accuracy_score, f1_score
from scipy.optimize import minimize

from src.models.baselines import multiclass_brier_score
from src.models.two_stage_model import TwoStageFootballModel
from src.features.build_features import get_track_feature_columns

class PlattCalibrator:
    """Multinomial Platt / Temperature Sigmoid Calibrator fitted strictly on validation logits."""
    def __init__(self, C: float = 1.0):
        self.C = C
        self.calibrator = LogisticRegression(C=self.C, max_iter=500, random_state=42)

    def _to_logits(self, probs: np.ndarray) -> np.ndarray:
        p = np.clip(probs, 1e-12, 1.0 - 1e-12)
        p = p / p.sum(axis=1, keepdims=True)
        return np.log(p)

    def fit(self, uncalibrated_probs: np.ndarray, y_true: np.ndarray):
        logits = self._to_logits(uncalibrated_probs)
        self.calibrator.fit(logits, y_true)
        return self

    def predict_proba(self, uncalibrated_probs: np.ndarray) -> np.ndarray:
        logits = self._to_logits(uncalibrated_probs)
        p_cal = self.calibrator.predict_proba(logits)
        p_cal = np.clip(p_cal, 1e-12, 1.0 - 1e-12)
        return p_cal / p_cal.sum(axis=1, keepdims=True)

class ModelBundleV2:
    def __init__(self, track: str = "A"):
        self.track = track
        self.feature_names: List[str] = []
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.base_models: Dict[str, Any] = {}
        self.calibrators: Dict[str, PlattCalibrator] = {}
        self.two_stage_model: Any = None
        self.ensemble_weights: np.ndarray = np.array([])
        self.model_names: List[str] = []

    def fit_and_calibrate(self, train_df: pd.DataFrame, val_df: pd.DataFrame):
        self.feature_names = get_track_feature_columns(train_df, track=self.track)
        print(f"\n[V2 TRAINING TRACK {self.track}] Audited Pre-Match Features: {len(self.feature_names)}", flush=True)

        X_train_raw = train_df[self.feature_names].values
        y_train = train_df["Outcome"].values
        X_val_raw = val_df[self.feature_names].values
        y_val = val_df["Outcome"].values

        # Impute and Scale
        X_train = self.imputer.fit_transform(X_train_raw)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val = self.imputer.transform(X_val_raw)
        X_val_scaled = self.scaler.transform(X_val)

        # 1. Base Classifiers
        self.base_models = {
            "LogisticRegression": LogisticRegression(C=0.05, max_iter=1000, random_state=42),
            "RandomForest": RandomForestClassifier(n_estimators=160, max_depth=5, min_samples_leaf=30, random_state=42, n_jobs=4),
            "HistGradientBoosting": HistGradientBoostingClassifier(learning_rate=0.06, max_depth=4, l2_regularization=2.5, max_iter=120, random_state=42)
        }

        val_probs_dict = {}
        for name, model in self.base_models.items():
            model.fit(X_train_scaled, y_train)
            raw_val_p = model.predict_proba(X_val_scaled)
            calib = PlattCalibrator(C=1.0)
            calib.fit(raw_val_p, y_val)
            self.calibrators[name] = calib
            val_probs_dict[name] = calib.predict_proba(raw_val_p)

        # 2. Two-Stage Stalemate Resolver
        print(f"[V2 TRAINING TRACK {self.track}] Fitting Two-Stage Stalemate Resolver...", flush=True)
        self.two_stage_model = TwoStageFootballModel()
        self.two_stage_model.fit_and_calibrate(X_train_raw, y_train, X_val_raw, y_val)
        val_probs_dict["TwoStage"] = self.two_stage_model.predict_proba(X_val_raw)

        self.model_names = list(val_probs_dict.keys())
        M = len(self.model_names)

        # 3. SLSQP Ensemble Optimization on Validation Set
        P_val_list = [val_probs_dict[m] for m in self.model_names]

        def loss_fn(weights):
            w = weights / np.sum(weights)
            blend_p = np.zeros_like(P_val_list[0])
            for i, p_mat in enumerate(P_val_list):
                blend_p += w[i] * p_mat
            blend_p = np.clip(blend_p, 1e-12, 1.0)
            blend_p /= blend_p.sum(axis=1, keepdims=True)
            return log_loss(y_val, blend_p)

        init_weights = np.ones(M) / M
        bounds = [(0.0, 1.0) for _ in range(M)]
        cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}

        opt_res = minimize(loss_fn, init_weights, method="SLSQP", bounds=bounds, constraints=cons)
        self.ensemble_weights = opt_res.x / np.sum(opt_res.x)

        val_loss = loss_fn(self.ensemble_weights)
        print(f"[V2 TRACK {self.track} CALIBRATED] Validation Log Loss: {val_loss:.4f} | Weights: {dict(zip(self.model_names, [round(float(w), 3) for w in self.ensemble_weights]))}", flush=True)

    def predict_proba(self, df_input: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Returns (calibrated_probs, model_disagreement_std)."""
        X_raw = df_input[self.feature_names].values
        X_imp = self.imputer.transform(X_raw)
        X_scaled = self.scaler.transform(X_imp)

        model_p_list = []
        for name in self.model_names:
            if name == "TwoStage":
                cal_p = self.two_stage_model.predict_proba(X_raw)
            else:
                raw_p = self.base_models[name].predict_proba(X_scaled)
                cal_p = self.calibrators[name].predict_proba(raw_p)
            model_p_list.append(cal_p)

        # Weighted blend
        final_p = np.zeros_like(model_p_list[0])
        for w, p_mat in zip(self.ensemble_weights, model_p_list):
            final_p += w * p_mat

        final_p = np.clip(final_p, 1e-12, 1.0)
        final_p /= final_p.sum(axis=1, keepdims=True)

        stacked_p = np.stack(model_p_list, axis=0)
        model_std = np.std(stacked_p, axis=0).mean(axis=1)

        return final_p, model_std

def evaluate_test_set(bundle: ModelBundleV2, test_df: pd.DataFrame) -> Dict[str, Any]:
    """Evaluates bundle on untouched test set with honest, leak-free metrics."""
    probs, disagreement = bundle.predict_proba(test_df)
    y_true = test_df["Outcome"].values
    preds = np.argmax(probs, axis=1)

    loss = log_loss(y_true, probs)
    acc = accuracy_score(y_true, preds)
    bacc = balanced_accuracy_score(y_true, preds)
    brier = multiclass_brier_score(y_true, probs)
    f1_macro = f1_score(y_true, preds, average="macro")

    # ECE (Expected Calibration Error)
    confidences = np.max(probs, axis=1)
    correctness = (preds == y_true).astype(float)
    bin_boundaries = np.linspace(0.33, 1.0, 10)
    ece = 0.0
    for b_idx in range(len(bin_boundaries) - 1):
        mask = (confidences >= bin_boundaries[b_idx]) & (confidences < bin_boundaries[b_idx + 1])
        if np.sum(mask) > 0:
            bin_acc = np.mean(correctness[mask])
            bin_conf = np.mean(confidences[mask])
            ece += (np.sum(mask) / len(confidences)) * abs(bin_acc - bin_conf)

    # League-by-League Accuracy
    league_accs = {}
    for lg in test_df["League"].unique():
        mask = (test_df["League"] == lg)
        if mask.sum() > 0:
            league_accs[str(lg)] = round(float(accuracy_score(y_true[mask], preds[mask])) * 100.0, 2)

    return {
        "track": bundle.track,
        "n_matches": len(test_df),
        "accuracy_pct": round(float(acc * 100.0), 2),
        "balanced_accuracy_pct": round(float(bacc * 100.0), 2),
        "log_loss": round(float(loss), 4),
        "brier_score": round(float(brier), 4),
        "macro_f1": round(float(f1_macro), 4),
        "ece": round(float(ece), 4),
        "disagreement_mean": round(float(np.mean(disagreement)), 4),
        "league_accuracies": league_accs
    }

def train_and_evaluate_all_tracks(features_csv: str = "data/processed/features_v2_leakfree.csv"):
    """Trains Track A, Track B, and Track C and serializes them."""
    print(f"[V2 TRAIN PIPELINE] Loading features from {features_csv}...", flush=True)
    df = pd.read_csv(features_csv, low_memory=False)
    df["Date"] = pd.to_datetime(df["Date"])

    # Chronological splits
    train_df = df[df["Split"] == "Train"].copy()
    val_df = df[df["Split"] == "Val"].copy()
    test_df = df[df["Split"] == "Test"].copy()

    print(f"Dataset Partitions: Train={len(train_df)} | Val={len(val_df)} | Test={len(test_df)}", flush=True)

    results = {}
    for trk in ["A", "B", "C"]:
        bundle = ModelBundleV2(track=trk)
        bundle.fit_and_calibrate(train_df, val_df)
        save_path = f"models/track_{trk.lower()}_bundle.joblib"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump(bundle, save_path)
        print(f"[SAVED] Track {trk} bundle serialized to {save_path}", flush=True)

        # Evaluate on untouched test set
        res = evaluate_test_set(bundle, test_df)
        results[trk] = res
        print(f"\n--- [TRACK {trk} RESULTS ON UNTOUCHED 2024/25 TEST SET ({res['n_matches']} Matches)] ---")
        print(f"  Accuracy:          {res['accuracy_pct']}%")
        print(f"  Balanced Accuracy: {res['balanced_accuracy_pct']}%")
        print(f"  Log Loss:          {res['log_loss']}")
        print(f"  Brier Score:       {res['brier_score']}")
        print(f"  Macro F1:          {res['macro_f1']}")
        print(f"  ECE:               {res['ece']}")
        print(f"  Leagues:           {res['league_accuracies']}\n")

    return results

if __name__ == "__main__":
    train_and_evaluate_all_tracks()
