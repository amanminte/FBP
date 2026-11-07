"""
Mandatory Zero Data Leakage Automated Unit Test.
Verifies that mutating future match outcomes has zero effect on past match pre-match features.
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from src.features.build_features import build_all_features

def create_synthetic_match_slice(n_matches: int = 200) -> pd.DataFrame:
    """Creates a deterministic chronological slice of 200 matches."""
    teams = ["Arsenal", "Chelsea", "Liverpool", "Man City", "Man United", "Tottenham", "Aston Villa", "Newcastle"]
    base_date = datetime(2022, 8, 1)

    records = []
    rng = np.random.RandomState(42)

    for i in range(n_matches):
        match_date = base_date + timedelta(days=i // 4, hours=(i % 4) * 3)
        h_idx = rng.choice(len(teams))
        a_idx = rng.choice([x for x in range(len(teams)) if x != h_idx])
        ht = teams[h_idx]
        at = teams[a_idx]
        fthg = int(rng.poisson(1.4))
        ftag = int(rng.poisson(1.1))
        hthg = int(min(fthg, rng.poisson(0.6)))
        htag = int(min(ftag, rng.poisson(0.5)))
        ftr = "H" if fthg > ftag else ("D" if fthg == ftag else "A")

        records.append({
            "Date": match_date,
            "League": "E0",
            "Season": "2223",
            "HomeTeam": ht,
            "AwayTeam": at,
            "FTHG": fthg,
            "FTAG": ftag,
            "HTHG": hthg,
            "HTAG": htag,
            "FTR": ftr,
            "HS": int(rng.randint(8, 20)),
            "AS": int(rng.randint(6, 18)),
            "HST": int(rng.randint(2, 9)),
            "AST": int(rng.randint(1, 8)),
            "HC": int(rng.randint(2, 10)),
            "AC": int(rng.randint(1, 9)),
            "HF": 10,
            "AF": 10,
            "HY": 1,
            "AY": 2,
            "HR": 0,
            "AR": 0,
            "Odds_H": 2.10,
            "Odds_D": 3.40,
            "Odds_A": 3.60,
            "Fair_Prob_H": 0.45,
            "Fair_Prob_D": 0.28,
            "Fair_Prob_A": 0.27,
            "Fair_Prob_Over25": 0.52,
            "Fair_Prob_Under25": 0.48
        })

    df = pd.DataFrame(records)
    df = df.sort_values(["Date", "HomeTeam"]).reset_index(drop=True)
    return df

def test_zero_leakage_bitwise_invariance():
    """Asserts that features for matches 0 to 149 are 100% bitwise identical after corrupting matches 150 to 199."""
    df_clean = create_synthetic_match_slice(200)

    # 1. Run feature engineering on clean slice
    features_clean = build_all_features(df_clean.copy())

    # 2. Corrupt future matches (last 50 matches: set FTHG = 99, FTAG = 0, FTR = 'H')
    df_corrupted = df_clean.copy()
    df_corrupted.loc[150:, "FTHG"] = 99
    df_corrupted.loc[150:, "FTAG"] = 0
    df_corrupted.loc[150:, "HTHG"] = 45
    df_corrupted.loc[150:, "HTAG"] = 0
    df_corrupted.loc[150:, "FTR"] = "H"
    df_corrupted.loc[150:, "HST"] = 50
    df_corrupted.loc[150:, "AST"] = 0

    # 3. Re-run feature engineering on corrupted slice
    features_corrupted = build_all_features(df_corrupted)

    # 4. Check feature columns for past 150 matches
    # Identify engineered feature columns
    feat_cols = [c for c in features_clean.columns if c not in ["Date", "League", "Season", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "HTHG", "HTAG", "FTR", "Split"]]

    past_clean = features_clean.iloc[:150][feat_cols].reset_index(drop=True)
    past_corrupted = features_corrupted.iloc[:150][feat_cols].reset_index(drop=True)

    # Bitwise exact equality check
    pd.testing.assert_frame_equal(past_clean, past_corrupted, check_exact=True)
    print("\n[LEAKAGE TEST PASSED] 100% bitwise invariance verified for all pre-match features!")

if __name__ == "__main__":
    test_zero_leakage_bitwise_invariance()
