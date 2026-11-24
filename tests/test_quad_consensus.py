"""
Unit tests for Understat, WhoScored, and Quad-Consensus Convergence Engines.
Validates:
1. Understat xG, NPxG, and xPTS calculation bounds.
2. WhoScored match ratings, departmental mismatches, and strengths/weaknesses generation.
3. 4-Way Convergence logic (Quad-Lock Diamond for 4/4 agreement, Gold for 3/4, Split for divergence).
"""
import pytest
from src.models.understat_whoscored import compute_understat_metrics, compute_whoscored_metrics
from src.models.quad_consensus import evaluate_quad_consensus
from src.models.forebet_fusion import compute_forebet_prediction

def test_understat_metrics_validity():
    us = compute_understat_metrics(
        home_team="Arsenal",
        away_team="Hull City",
        rank_h=1,
        pts_h=28,
        gd_h=18,
        rank_a=18,
        pts_a=9,
        gd_a=-9,
        lambda_h=2.15,
        lambda_a=0.70
    )
    assert us["xg_h"] > us["xg_a"], "Top team Arsenal must have higher xG than Hull City"
    assert us["npxg_h"] <= us["xg_h"], "NPxG cannot exceed total xG"
    assert us["xpts_h"] > us["xpts_a"], "Arsenal must have higher xPTS than Hull City"
    assert us["verdict"] == "Home Win", "Understat should pick Home Win for heavy favorite"
    assert 0 <= us["confidence"] <= 100

def test_whoscored_metrics_validity():
    ws = compute_whoscored_metrics(
        home_team="Arsenal",
        away_team="Hull City",
        rank_h=1,
        pts_h=28,
        gd_h=18,
        rank_a=18,
        pts_a=9,
        gd_a=-9
    )
    assert ws["rating_h"] > ws["rating_a"], "League leader must have higher rating than relegation tier"
    assert ws["poss_h"] > ws["poss_a"], "Arsenal should project majority possession"
    assert ws["verdict"] == "Home Win"
    assert len(ws["strengths_h"]) > 0
    assert len(ws["weaknesses_a"]) > 0

def test_quad_consensus_diamond_convergence():
    # When all 4 agree on Home Win
    forebet_data = {
        "forebet_probs": {"home": 75.0, "draw": 18.0, "away": 7.0},
        "predicted_score": "2 - 0",
        "recommended_pick": "Home Win (1)"
    }
    understat_data = {
        "xg_h": 2.45,
        "xg_a": 0.55,
        "xpts_h": 2.45,
        "xpts_a": 0.35,
        "xg_diff": 1.90,
        "verdict": "Home Win"
    }
    whoscored_data = {
        "rating_h": 7.18,
        "rating_a": 6.38,
        "poss_h": 65.0,
        "positional_mismatches": 4,
        "verdict": "Home Win"
    }

    qc = evaluate_quad_consensus(
        home_team="Arsenal",
        away_team="Hull City",
        ml_prediction="Home Win",
        ml_confidence=78.5,
        forebet_data=forebet_data,
        understat_data=understat_data,
        whoscored_data=whoscored_data
    )

    assert qc["consensus_count"] == 4, "All 4 must agree"
    assert qc["tier_level"] == 1, "Must be Tier 1 Diamond"
    assert "DIAMOND" in qc["consensus_tier"]
    assert qc["dominant_pick"] == "Home Win"
    assert len(qc["sources"]) == 4

def test_quad_consensus_split_market():
    # 2 agree Home, 2 agree Away/Draw
    forebet_data = {"recommended_pick": "Away Win"}
    understat_data = {"verdict": "Draw"}
    whoscored_data = {"verdict": "Home Win"}

    qc = evaluate_quad_consensus(
        home_team="Team A",
        away_team="Team B",
        ml_prediction="Home Win",
        ml_confidence=45.0,
        forebet_data=forebet_data,
        understat_data=understat_data,
        whoscored_data=whoscored_data
    )

    assert qc["consensus_count"] == 2
    assert qc["tier_level"] == 3
    assert "SPLIT" in qc["consensus_tier"]


def test_football_predictor_metrics():
    from src.models.football_predictor import compute_football_predictor
    fp = compute_football_predictor("Arsenal", "Hull City", rank_h=1, pts_h=28, gd_h=18, rank_a=18, pts_a=9, gd_a=-9)
    assert fp["form_h"] > fp["form_a"]
    assert fp["home_prob"] > fp["away_prob"]
    assert fp["recommended_pick"] == "Home Win"
    assert "predicted_score" in fp


def test_common_ground_market_conflict_arbitrage():
    from src.models.consensus_engine import find_common_ground_market
    # User scenario: 2 say Home (2-0, 2-1) and 2 say Away/Draw (1-1, 1-2)
    sources = [{"score": "2 - 0"}, {"score": "2 - 1"}, {"score": "1 - 1"}, {"score": "1 - 2"}]
    cg = find_common_ground_market("Arsenal", "Chelsea", sources, 1.5, 1.2)
    
    # When multiple markets reach 100%, verify a top safe market is selected
    assert cg["common_ground_agreement"] == 100.0
    assert len(cg["all_predicted_scores"]) == 4
    assert any(m in cg["best_common_ground_market"] for m in ["Over 1.5", "Under 4.5", "Under 3.5"])


def test_common_ground_market_low_scoring_under():
    from src.models.consensus_engine import find_common_ground_market
    # Low-scoring scenario: 0-0, 1-0, 0-1, 1-1
    sources = [{"score": "0 - 0"}, {"score": "1 - 0"}, {"score": "0 - 1"}, {"score": "1 - 1"}]
    cg = find_common_ground_market("Everton", "Crystal Palace", sources, 0.8, 0.8)
    assert any(u in cg["best_common_ground_market"] for u in ["Under 2.5", "Under 3.5", "Under 4.5"])
    assert cg["common_ground_agreement"] == 100.0


def test_penta_consensus_royal_diamond():
    from src.models.consensus_engine import evaluate_penta_consensus
    fb = {"predicted_score": "2 - 0", "recommended_pick": "Home Win"}
    us = {"xg_h": 2.5, "xg_a": 0.5, "verdict": "Home Win"}
    ws = {"verdict": "Home Win", "rating_h": 7.2, "rating_a": 6.3}
    fp = {"predicted_score": "2 - 0", "recommended_pick": "Home Win", "form_h": 85, "form_a": 35}

    penta = evaluate_penta_consensus(
        home_team="Arsenal",
        away_team="Hull City",
        ml_prediction="Home Win",
        ml_confidence=80.0,
        ml_score="2 - 0",
        forebet_data=fb,
        understat_data=us,
        whoscored_data=ws,
        football_predictor_data=fp
    )

    # In upgraded 7-way Hepta consensus, unanimous agreement reaches tier 1 Diamond
    assert penta["consensus_count"] >= 5
    assert penta["tier_level"] == 1
    assert "DIAMOND" in penta["consensus_tier"]
    assert len(penta["sources"]) >= 5


def test_evaluate_bet_hit_all_markets():
    from src.evaluation.live_clv_tracker import evaluate_bet_hit

    # Double Chance 1X
    hit, mult = evaluate_bet_hit("Double Chance: Arsenal or Draw (1X)", "Arsenal", "Hull City", 2, 0)
    assert hit == 1 and mult == 1.0
    hit, mult = evaluate_bet_hit("Double Chance: Arsenal or Draw (1X)", "Arsenal", "Hull City", 1, 1)
    assert hit == 1 and mult == 1.0
    hit, mult = evaluate_bet_hit("Double Chance: Arsenal or Draw (1X)", "Arsenal", "Hull City", 0, 1)
    assert hit == 0 and mult == -1.0

    # Over 1.5 Goals
    hit, mult = evaluate_bet_hit("Over 1.5 Total Match Goals", "Arsenal", "Hull City", 2, 0)
    assert hit == 1 and mult == 1.0
    hit, mult = evaluate_bet_hit("Over 1.5 Total Match Goals", "Arsenal", "Hull City", 1, 0)
    assert hit == 0 and mult == -1.0

    # Under 2.5 Goals
    hit, mult = evaluate_bet_hit("Under 2.5 Total Match Goals", "Arsenal", "Hull City", 1, 1)
    assert hit == 1 and mult == 1.0
    hit, mult = evaluate_bet_hit("Under 2.5 Total Match Goals", "Arsenal", "Hull City", 3, 0)
    assert hit == 0 and mult == -1.0

    # BTTS
    hit, mult = evaluate_bet_hit("Both Teams To Score: YES", "Arsenal", "Hull City", 2, 1)
    assert hit == 1 and mult == 1.0
    hit, mult = evaluate_bet_hit("Both Teams To Score: YES", "Arsenal", "Hull City", 2, 0)
    assert hit == 0 and mult == -1.0

    # Draw No Bet (DNB)
    hit, mult = evaluate_bet_hit("Draw No Bet (Home DNB)", "Arsenal", "Hull City", 2, 0)
    assert hit == 1 and mult == 1.0
    hit, mult = evaluate_bet_hit("Draw No Bet (Home DNB)", "Arsenal", "Hull City", 1, 1)
    assert hit == 0 and mult == 0.0 # Push / Refund!


def test_record_and_auto_grade_ledger_flow(tmp_path):
    import sqlite3
    from src.evaluation.live_clv_tracker import (
        init_ledger_db,
        record_live_prediction,
        auto_grade_pending_predictions_from_live_feed,
        get_ledger_summary
    )
    test_db = str(tmp_path / "test_ledger.sqlite")
    init_ledger_db(test_db)

    # Record finished official match: Arsenal vs Coventry City 3 - 0
    pid = record_live_prediction(
        match_date="2026-08-21",
        league="E0",
        home_team="Arsenal",
        away_team="Coventry City",
        model_track="Gameweek Banker Multi",
        predicted_pick="Double Chance: Arsenal or Draw (1X)",
        calibrated_prob=0.90,
        opening_odds=1.15,
        stake_units=10.0,
        bet_category="Banker Parlay",
        db_path=test_db
    )
    assert pid > 0

    # Run auto-grader with official finished fixture feed
    mock_fixtures = [{
        "team_h": 1,
        "team_a": 2,
        "finished": True,
        "team_h_score": 3,
        "team_a_score": 0,
        "stats": [{"identifier": "saves", "h": [{"value": 2}], "a": [{"value": 5}]}]
    }]
    mock_teams = {1: "Arsenal", 2: "Coventry City"}

    res = auto_grade_pending_predictions_from_live_feed(
        db_path=test_db,
        fixtures_override=mock_fixtures,
        teams_map_override=mock_teams
    )
    assert res["graded_count"] == 1
    item = res["graded_items"][0]
    assert item["actual_score"] == "3 - 0"
    assert item["is_hit"] == 1
    assert item["actual_xg_h"] > 0
    assert item["actual_xg_a"] > 0
    assert item["pnl"] == 1.5

    # Check updated summary
    summ = get_ledger_summary(db_path=test_db)
    assert summ["settled_count"] == 1
    assert summ["win_rate_pct"] == 100.0
    assert summ["total_flat_pnl"] == 1.5

