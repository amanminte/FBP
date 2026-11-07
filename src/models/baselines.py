"""
Baseline Suite for 1X2 and Goal Line Outcome Benchmarking.
Evaluates:
1. Majority Class (Home Win)
2. League-Specific Historical Class Frequencies
3. Pure Elo + Dixon-Coles Statistical Ratings
4. Bookmaker Fair Implied Odds Ceiling
"""
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, accuracy_score, f1_score
from typing import Dict, Tuple

def multiclass_brier_score(y_true: np.ndarray, y_prob: np.ndarray, n_classes: int = 3) -> float:
    """Computes exact multiclass Brier score: (1/N) * sum_i sum_k (p_ik - y_ik)^2."""
    y_one_hot = np.zeros((len(y_true), n_classes))
    for i, val in enumerate(y_true):
        y_one_hot[i, int(val)] = 1.0
    return float(np.mean(np.sum((y_prob - y_one_hot) ** 2, axis=1)))

def evaluate_baseline_predictions(y_true: np.ndarray, y_prob: np.ndarray, name: str) -> Dict[str, float]:
    """Computes standard benchmark metrics."""
    # Clip probabilities for stable log loss
    y_prob_clipped = np.clip(y_prob, 1e-12, 1.0 - 1e-12)
    y_prob_clipped = y_prob_clipped / y_prob_clipped.sum(axis=1, keepdims=True)

    y_pred = np.argmax(y_prob_clipped, axis=1)
    acc = float(accuracy_score(y_true, y_pred))
    ll = float(log_loss(y_true, y_prob_clipped))
    brier = multiclass_brier_score(y_true, y_prob_clipped, n_classes=3)
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    return {
        "Model": name,
        "Accuracy (%)": round(acc * 100.0, 2),
        "Log Loss": round(ll, 4),
        "Brier Score": round(brier, 4),
        "Macro F1": round(macro_f1, 4)
    }

def run_all_baselines(features_path: str = "data/processed/matches_features.csv") -> Tuple[pd.DataFrame, pd.DataFrame]:
    cols = ["Split", "League", "Outcome", "Elo_Prob_H", "Elo_Prob_D", "Elo_Prob_A",
            "DC_Prob_H", "DC_Prob_D", "DC_Prob_A", "Fair_Prob_H", "Fair_Prob_D", "Fair_Prob_A"]
    df = pd.read_csv(features_path, usecols=cols)
    train_df = df[df["Split"] == "Train"].copy()
    val_df = df[df["Split"] == "Val"].copy()
    test_df = df[df["Split"] == "Test"].copy()

    # Targets: Outcome 0 = H, 1 = D, 2 = A
    y_train = train_df["Outcome"].values
    y_val = val_df["Outcome"].values
    y_test = test_df["Outcome"].values

    # 1. Majority Class Baseline
    # Historical train frequencies
    h_freq = np.mean(y_train == 0)
    d_freq = np.mean(y_train == 1)
    a_freq = np.mean(y_train == 2)
    maj_probs_train = np.array([h_freq, d_freq, a_freq])

    maj_val_probs = np.tile(maj_probs_train, (len(val_df), 1))
    maj_test_probs = np.tile(maj_probs_train, (len(test_df), 1))

    # 2. League Frequency Baseline
    league_freqs = {}
    for lg, grp in train_df.groupby("League"):
        lh = np.mean(grp["Outcome"] == 0)
        ld = np.mean(grp["Outcome"] == 1)
        la = np.mean(grp["Outcome"] == 2)
        league_freqs[lg] = np.array([lh, ld, la])

    lg_val_probs = np.array([league_freqs.get(lg, maj_probs_train) for lg in val_df["League"]])
    lg_test_probs = np.array([league_freqs.get(lg, maj_probs_train) for lg in test_df["League"]])

    # 3. Pure Statistical Baseline (Elo + Dixon-Coles blended 50/50)
    def extract_stat_probs(sub_df):
        elo_p = sub_df[["Elo_Prob_H", "Elo_Prob_D", "Elo_Prob_A"]].values
        dc_p = sub_df[["DC_Prob_H", "DC_Prob_D", "DC_Prob_A"]].values
        stat_p = 0.5 * elo_p + 0.5 * dc_p
        return stat_p / stat_p.sum(axis=1, keepdims=True)

    stat_val_probs = extract_stat_probs(val_df)
    stat_test_probs = extract_stat_probs(test_df)

    # 4. Fair Bookmaker Odds Ceiling
    def extract_fair_probs(sub_df):
        fair_p = sub_df[["Fair_Prob_H", "Fair_Prob_D", "Fair_Prob_A"]].values
        # Fill missing with stat probs
        mask = np.isnan(fair_p).any(axis=1)
        if mask.any():
            stat_p = extract_stat_probs(sub_df)
            fair_p[mask] = stat_p[mask]
        return fair_p / fair_p.sum(axis=1, keepdims=True)

    fair_val_probs = extract_fair_probs(val_df)
    fair_test_probs = extract_fair_probs(test_df)

    # Compile Val Results
    val_results = [
        evaluate_baseline_predictions(y_val, maj_val_probs, "1. Majority Class (Home Win)"),
        evaluate_baseline_predictions(y_val, lg_val_probs, "2. League Historical Frequency"),
        evaluate_baseline_predictions(y_val, stat_val_probs, "3. Pure Statistical (Elo + Dixon-Coles)"),
        evaluate_baseline_predictions(y_val, fair_val_probs, "4. Bookmaker Fair Market Ceiling"),
    ]

    # Compile Test Results
    test_results = [
        evaluate_baseline_predictions(y_test, maj_test_probs, "1. Majority Class (Home Win)"),
        evaluate_baseline_predictions(y_test, lg_test_probs, "2. League Historical Frequency"),
        evaluate_baseline_predictions(y_test, stat_test_probs, "3. Pure Statistical (Elo + Dixon-Coles)"),
        evaluate_baseline_predictions(y_test, fair_test_probs, "4. Bookmaker Fair Market Ceiling"),
    ]

    val_df_metrics = pd.DataFrame(val_results)
    test_df_metrics = pd.DataFrame(test_results)

    print("\n" + "=" * 65)
    print("BASELINE METRICS — VALIDATION SET (Jan 2024 - May 2024, N = 899)")
    print("=" * 65)
    print(val_df_metrics.to_string(index=False))

    print("\n" + "=" * 65)
    print("BASELINE METRICS — UNTOUCHED TEST SET (2024/25 Season, N = 1,752)")
    print("=" * 65)
    print(test_df_metrics.to_string(index=False))

    return val_df_metrics, test_df_metrics

if __name__ == "__main__":
    run_all_baselines()
