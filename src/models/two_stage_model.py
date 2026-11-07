"""
Two-Stage Hierarchical Football Match Outcome Classifier.
Stage 1: Binary Draw Detector (Stalemate vs Decisive).
Stage 2: Conditional Decisive Classifier (Home Win vs Away Win).
Recombination:
    P(Draw) = P_stage1(Draw)
    P(Home) = (1 - P(Draw)) * P_stage2(Home | Decisive)
    P(Away) = (1 - P(Draw)) * (1 - P_stage2(Home | Decisive))
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss, accuracy_score

class TwoStageFootballModel:
    def __init__(self, track: str = "B"):
        self.track = track
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()

        # Stage 1: Draw Detector
        self.stage1_clf = HistGradientBoostingClassifier(
            max_iter=150, max_depth=4, min_samples_leaf=35,
            l2_regularization=2.0, class_weight="balanced", random_state=42
        )
        self.stage1_calib = LogisticRegression(C=1.0, max_iter=500, random_state=42)

        # Stage 2: Decisive Matchup (Home vs Away)
        self.stage2_clf = HistGradientBoostingClassifier(
            max_iter=150, max_depth=5, min_samples_leaf=25,
            l2_regularization=1.5, random_state=42
        )
        self.stage2_calib = LogisticRegression(C=1.0, max_iter=500, random_state=42)

    def fit_and_calibrate(self, X_train: np.ndarray, y_train: np.ndarray,
                          X_val: np.ndarray, y_val: np.ndarray):
        # 1. Fit Imputer & Scaler
        X_train_imp = self.imputer.fit_transform(X_train)
        X_val_imp = self.imputer.transform(X_val)

        # -------------------------------------------------------------
        # STAGE 1: Draw Detector (y == 1 -> Draw)
        # -------------------------------------------------------------
        y_train_draw = (y_train == 1).astype(int)
        y_val_draw = (y_val == 1).astype(int)

        self.stage1_clf.fit(X_train_imp, y_train_draw)
        val_draw_preds = self.stage1_clf.predict_proba(X_val_imp)[:, 1:2]
        val_draw_logits = np.log(np.clip(val_draw_preds, 1e-12, 1.0 - 1e-12))
        self.stage1_calib.fit(val_draw_logits, y_val_draw)

        # -------------------------------------------------------------
        # STAGE 2: Decisive Matchup (Home=0 vs Away=2)
        # -------------------------------------------------------------
        decisive_train_mask = (y_train != 1)
        X_train_dec = X_train_imp[decisive_train_mask]
        # Target: 1 for Home (y==0), 0 for Away (y==2)
        y_train_dec = (y_train[decisive_train_mask] == 0).astype(int)

        self.stage2_clf.fit(X_train_dec, y_train_dec)

        decisive_val_mask = (y_val != 1)
        X_val_dec = X_val_imp[decisive_val_mask]
        y_val_dec = (y_val[decisive_val_mask] == 0).astype(int)

        val_dec_preds = self.stage2_clf.predict_proba(X_val_dec)[:, 1:2]
        val_dec_logits = np.log(np.clip(val_dec_preds, 1e-12, 1.0 - 1e-12))
        self.stage2_calib.fit(val_dec_logits, y_val_dec)

        # Evaluate combined probabilities on Validation Set
        probs_val = self.predict_proba(X_val)
        ll = log_loss(y_val, probs_val)
        acc = accuracy_score(y_val, np.argmax(probs_val, axis=1))
        print(f"     [TWO-STAGE HIERARCHICAL MODEL] Calibrated Val LogLoss: {ll:.4f}, Acc: {acc*100:.2f}%", flush=True)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X_imp = self.imputer.transform(X)

        # Stage 1: P(Draw)
        s1_raw = self.stage1_clf.predict_proba(X_imp)[:, 1:2]
        s1_logits = np.log(np.clip(s1_raw, 1e-12, 1.0 - 1e-12))
        p_draw = self.stage1_calib.predict_proba(s1_logits)[:, 1]

        # Stage 2: P(Home | Decisive)
        s2_raw = self.stage2_clf.predict_proba(X_imp)[:, 1:2]
        s2_logits = np.log(np.clip(s2_raw, 1e-12, 1.0 - 1e-12))
        p_home_dec = self.stage2_calib.predict_proba(s2_logits)[:, 1]

        # Recombine into 3 classes [Home, Draw, Away]
        p_home = (1.0 - p_draw) * p_home_dec
        p_away = (1.0 - p_draw) * (1.0 - p_home_dec)

        probs = np.column_stack([p_home, p_draw, p_away])
        probs = np.clip(probs, 1e-12, 1.0 - 1e-12)
        return probs / probs.sum(axis=1, keepdims=True)
