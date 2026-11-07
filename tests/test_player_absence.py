"""
Unit tests for Module 3: Key Player Absence Penalty Architecture.
Verifies penalty calculation bounds, Dixon-Coles adjustments, and absence logic.
"""
import pytest
import numpy as np
from src.features.player_absence import (
    KEY_PLAYERS_DB,
    get_club_key_players,
    calculate_absence_penalty,
    compute_dixon_coles_matrix,
    apply_lineup_absence_adjustments
)

def test_key_players_db_structure():
    """Verify key players database exists for major European clubs with valid ranges."""
    assert len(KEY_PLAYERS_DB) >= 8
    for club, roster in KEY_PLAYERS_DB.items():
        assert len(roster) >= 4
        for player, stats in roster.items():
            assert "pos" in stats
            assert 0.0 <= stats["goal_share"] <= 1.0
            assert 0.0 <= stats["assist_share"] <= 1.0
            assert 0.0 <= stats["def_impact"] <= 1.0

def test_absence_penalty_calculation():
    """Verify absence penalty computes positive penalties and respects caps."""
    # Test Manchester City missing Erling Haaland & Rodri
    att_pen, def_pen, details = calculate_absence_penalty(
        "Manchester City", ["Erling Haaland", "Rodri"]
    )
    assert att_pen > 0.20
    assert def_pen > 0.20
    assert att_pen <= 0.40  # Capped at 40%
    assert def_pen <= 0.35  # Capped at 35%
    assert len(details) == 2

def test_unknown_player_fallback():
    """Verify unknown squad players receive a conservative baseline absence penalty."""
    att_pen, def_pen, details = calculate_absence_penalty(
        "Arsenal", ["Random Nonexistent Player"]
    )
    assert att_pen == 0.04
    assert def_pen == 0.04
    assert len(details) == 1
    assert "Unknown" in details[0]["position"]

def test_compute_dixon_coles_matrix():
    """Verify Dixon-Coles bivariate matrix sums to 1.0 and has non-negative entries."""
    matrix = compute_dixon_coles_matrix(lambda_h=1.85, lambda_a=1.10)
    assert matrix.shape == (8, 8)
    assert np.isclose(np.sum(matrix), 1.0, atol=1e-4)
    assert np.all(matrix >= 0.0)

def test_apply_lineup_absence_directionality():
    """Verify that removing home stars decreases home win probability and lambda."""
    base_probs = np.array([0.55, 0.25, 0.20])
    res = apply_lineup_absence_adjustments(
        home_team="Manchester City",
        away_team="Arsenal",
        base_lambda_h=2.20,
        base_lambda_a=1.10,
        base_probs=base_probs,
        home_missing=["Erling Haaland", "Rodri"],
        away_missing=[]
    )
    # Home expected goals should strictly drop
    assert res["adj_lambda_h"] < res["base_lambda_h"]
    # Home win probability should decrease
    assert res["adj_probs"]["H"] < res["base_probs"]["H"]
    # Away win probability should increase
    assert res["adj_probs"]["A"] > res["base_probs"]["A"]
    # Total adjusted probabilities must sum to 100%
    tot = res["adj_probs"]["H"] + res["adj_probs"]["D"] + res["adj_probs"]["A"]
    assert np.isclose(tot, 100.0, atol=0.5)
