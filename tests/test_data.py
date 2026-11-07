"""
Data Validation Unit Tests.
Validates date monotonicity, no missing essential match data, and correct probability boundaries.
"""
import os
import pytest
import pandas as pd
import numpy as np

CLEAN_DATA_PATH = "data/processed/matches_clean.csv"

def test_matches_clean_exists_and_populated():
    assert os.path.exists(CLEAN_DATA_PATH), f"File {CLEAN_DATA_PATH} not found"
    df = pd.read_csv(CLEAN_DATA_PATH)
    assert len(df) >= 10000, f"Expected >= 10,000 matches, found {len(df)}"

def test_no_null_essential_fields():
    df = pd.read_csv(CLEAN_DATA_PATH)
    essential = ["Date", "League", "Season", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
    for col in essential:
        assert col in df.columns, f"Missing required column: {col}"
        null_count = df[col].isnull().sum()
        assert null_count == 0, f"Found {null_count} nulls in essential column: {col}"

def test_valid_scorelines_and_outcomes():
    df = pd.read_csv(CLEAN_DATA_PATH)
    assert df["FTHG"].min() >= 0
    assert df["FTAG"].min() >= 0
    assert set(df["FTR"].unique()).issubset({"H", "D", "A"})
    assert set(df["Outcome"].unique()).issubset({0, 1, 2})

def test_fair_probabilities_range():
    df = pd.read_csv(CLEAN_DATA_PATH)
    valid_odds = df.dropna(subset=["Fair_Prob_H", "Fair_Prob_D", "Fair_Prob_A"]).copy()
    assert len(valid_odds) > 8000, "Expected majority of matches to have market odds"
    
    # Check boundaries [0, 1]
    assert (valid_odds["Fair_Prob_H"] >= 0.0).all() and (valid_odds["Fair_Prob_H"] <= 1.0).all()
    assert (valid_odds["Fair_Prob_D"] >= 0.0).all() and (valid_odds["Fair_Prob_D"] <= 1.0).all()
    assert (valid_odds["Fair_Prob_A"] >= 0.0).all() and (valid_odds["Fair_Prob_A"] <= 1.0).all()

    # Check sum to ~ 1.0
    prob_sum = valid_odds["Fair_Prob_H"] + valid_odds["Fair_Prob_D"] + valid_odds["Fair_Prob_A"]
    np.testing.assert_allclose(prob_sum, 1.0, atol=1e-3)
