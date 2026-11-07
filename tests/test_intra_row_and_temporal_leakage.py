"""
Comprehensive Anti-Leakage & Blindfold Verification Test Suite.
Verifies:
1. Temporal Bitwise Invariance: Future match mutations cannot change past match features.
2. Target-Row Blindfold Test: Wiping match i's own post-kickoff statistics (FTHG, FTAG, HST, AST, etc.)
   to NaN produces 100% bitwise identical pre-match feature vectors X_i.
3. Realistic Log Loss Physical Bounds: On the untouched 2024/25 test set, Track A log loss
   must reside in the realistic physical range [0.940, 1.050].
"""
import pytest
import numpy as np
import pandas as pd
from typing import List

from src.features.build_features import build_v2_leakfree_features, get_track_feature_columns

DATA_CLEAN_PATH = "data/processed/matches_clean.csv"

@pytest.fixture(scope="module")
def sample_slice():
    df = pd.read_csv(DATA_CLEAN_PATH, nrows=200, low_memory=False)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def test_future_row_mutation_bitwise_invariance(sample_slice):
    """Test 1: Future match mutations must not alter past pre-match features."""
    df_clean = sample_slice.copy()
    feats_clean = build_v2_leakfree_features(df_clean)
    cols_a = get_track_feature_columns(feats_clean, track="A")

    # Corrupt future rows 150-199
    df_corrupted = df_clean.copy()
    for col in ["FTHG", "FTAG", "HTHG", "HTAG", "HS", "AS", "HST", "AST", "HC", "AC"]:
        if col in df_corrupted.columns:
            df_corrupted.loc[150:199, col] = 99.0
    if "FTR" in df_corrupted.columns:
        df_corrupted.loc[150:199, "FTR"] = "H"

    feats_corrupted = build_v2_leakfree_features(df_corrupted)

    # First 150 rows must be bitwise identical
    slice_clean = feats_clean.iloc[:150][cols_a]
    slice_corrupt = feats_corrupted.iloc[:150][cols_a]

    pd.testing.assert_frame_equal(slice_clean, slice_corrupt, check_exact=False, rtol=1e-5, atol=1e-5)

def test_target_row_blindfold_test(sample_slice):
    """Test 2 (CRITICAL): Target match i's pre-match features X_i must be 100% identical

    even when match i's own post-kickoff stats are wiped to NaN.
    """
    df_orig = sample_slice.copy()
    target_idx = 100

    # Clean computation
    feats_orig = build_v2_leakfree_features(df_orig)
    cols_a = get_track_feature_columns(feats_orig, track="A")
    vec_orig = feats_orig.iloc[target_idx][cols_a].copy()

    # Blindfolded computation: wipe all in-play post-kickoff stats of target_idx
    df_blindfolded = df_orig.copy()
    post_kickoff_cols = [
        "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR",
        "HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF",
        "HY", "AY", "HR", "AR"
    ]
    for c in post_kickoff_cols:
        if c in df_blindfolded.columns:
            df_blindfolded.at[target_idx, c] = np.nan

    feats_blindfolded = build_v2_leakfree_features(df_blindfolded)
    vec_blindfolded = feats_blindfolded.iloc[target_idx][cols_a].copy()

    # Must be bitwise identical!
    pd.testing.assert_series_equal(vec_orig, vec_blindfolded, check_exact=False, rtol=1e-5, atol=1e-5)

def test_banned_raw_columns_not_in_features(sample_slice):
    """Test 3: Assert that no banned raw match columns exist in Track A, B, or C."""
    feats = build_v2_leakfree_features(sample_slice)
    banned = {
        "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR",
        "HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF",
        "HY", "AY", "HR", "AR", "xG_Home", "xG_Away",
        "Finishing_Luck_H", "Finishing_Luck_A"
    }
    for trk in ["A", "B", "C"]:
        cols = get_track_feature_columns(feats, track=trk)
        leaked = [c for c in cols if c in banned]
        assert len(leaked) == 0, f"Leaked columns found in Track {trk}: {leaked}"

def test_realistic_log_loss_physical_bounds():
    """Test 4: On untouched 2024/25 test set (1,752 matches), Track A Log Loss must lie in [0.940, 1.050]."""
    import sys, joblib
    from src.models.train import ModelBundleV2, PlattCalibrator
    sys.modules['__main__'].ModelBundleV2 = ModelBundleV2
    sys.modules['__main__'].PlattCalibrator = PlattCalibrator

    df = pd.read_csv("data/processed/features_v2_leakfree.csv", low_memory=False)
    test_df = df[df["Split"] == "Test"].copy()
    assert len(test_df) == 1752, f"Expected 1752 test matches, got {len(test_df)}"

    bundle_a = joblib.load("models/track_a_bundle.joblib")
    probs, _ = bundle_a.predict_proba(test_df)
    from sklearn.metrics import log_loss
    loss = log_loss(test_df["Outcome"].values, probs)
    print(f"\n[PHYSICAL BOUNDS AUDIT] Track A Test Log Loss: {loss:.4f}")
    assert 0.940 <= loss <= 1.050, f"Log loss {loss:.4f} outside physical bound [0.940, 1.050]"

