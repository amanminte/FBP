"""
Unit Tests for Quantitative Corner Kicks Prediction Engine & Betting Markets.
Audits:
- Historical training on 12,900+ matches (Empirical Bayes shrinkage)
- Negative Binomial and Bivariate probability distribution bounds
- Wing-play and crossing exploitation differentials (Man City/Bayern vs Getafe/Forest)
- Multi-market integration into Match Center & Alternative Picks
- Live ledger settlement logic for Total, Team, and Most Corners bets
- 5-League coverage across European top tier
"""
import pytest
from src.models.corners_model import CornersEngine, get_wing_profile
from src.models.multi_market import compute_all_market_probabilities, get_top_3_safest_picks, get_alternative_bet_ideas
from src.evaluation.live_clv_tracker import evaluate_bet_hit


@pytest.fixture
def corners_engine():
    return CornersEngine.get_instance()


def test_corners_engine_training(corners_engine):
    assert corners_engine.is_trained is True
    assert corners_engine.total_matches_trained >= 12000
    assert len(corners_engine.team_stats) >= 100
    assert "E0" in corners_engine.league_means
    assert "SP1" in corners_engine.league_means
    # Premier League historically has significantly more corners than Spanish La Liga
    assert corners_engine.league_means["E0"]["Total"] > corners_engine.league_means["SP1"]["Total"]


def test_corners_probability_distributions(corners_engine):
    pred = corners_engine.predict_corners("Arsenal", "Chelsea", league="E0")
    assert "probabilities" in pred
    assert "fair_odds" in pred
    assert "best_corner_bet" in pred
    assert "expected_total_corners" in pred

    probs = pred["probabilities"]
    # All probabilities must be mathematically bounded between 0 and 100%
    for k, v in probs.items():
        assert 0.0 <= v <= 100.0

    # Over + Under must sum to 100% within rounding tolerance
    assert abs((probs["over_8_5"] + probs["under_8_5"]) - 100.0) < 0.2
    assert abs((probs["over_9_5"] + probs["under_9_5"]) - 100.0) < 0.2
    assert abs((probs["over_10_5"] + probs["under_10_5"]) - 100.0) < 0.2
    assert abs((probs["over_12_5"] + probs["under_12_5"]) - 100.0) < 0.2

    # Expected corners must be physically realistic (between 6.0 and 15.0)
    assert 6.0 <= pred["expected_total_corners"] <= 15.0
    assert 2.0 <= pred["expected_home_corners"] <= 11.0
    assert 1.0 <= pred["expected_away_corners"] <= 9.0


def test_wing_play_differential(corners_engine):
    # Manchester City & Bayern Munich utilize elite wingers and high cross volume
    prof_mcfc = get_wing_profile("Manchester City")
    prof_bayern = get_wing_profile("Bayern Munich")
    prof_getafe = get_wing_profile("Getafe")
    prof_forest = get_wing_profile("Nottingham Forest")

    assert prof_mcfc["wing_mult"] > 1.15
    assert prof_bayern["wing_mult"] > 1.15
    assert prof_getafe["wing_mult"] < 0.90
    assert prof_forest["wing_mult"] < 0.90

    # Model projection for high-wing Man City at home vs compact low-block
    pred_mcfc = corners_engine.predict_corners("Manchester City", "Fulham", league="E0")
    pred_low = corners_engine.predict_corners("Getafe", "Alavés", league="SP1")

    assert pred_mcfc["expected_home_corners"] > pred_low["expected_home_corners"]
    assert pred_mcfc["expected_total_corners"] > pred_low["expected_total_corners"]


def test_multi_market_corners_integration():
    markets = compute_all_market_probabilities(
        home_team="Manchester City",
        away_team="Fulham",
        p_home=75.0,
        p_draw=15.0,
        p_away=10.0,
        lambda_h=2.5,
        lambda_a=0.8,
        league="E0"
    )

    assert "corners" in markets
    c_data = markets["corners"]
    assert "lambda_corners" in c_data
    assert "expected_home_corners" in c_data
    assert "under_12_5" in c_data
    assert c_data["under_12_5"] >= 50.0

    # Top safest picks include diverse markets
    safest = get_top_3_safest_picks(
        home_team="Manchester City",
        away_team="Fulham",
        p_home=75.0,
        p_draw=15.0,
        p_away=10.0,
        lambda_h=2.5,
        lambda_a=0.8,
        league="E0"
    )
    assert len(safest) == 3

    # Alternative smart bet ideas include corners
    alt_ideas = get_alternative_bet_ideas(
        home_team="Manchester City",
        away_team="Fulham",
        p_home=75.0,
        p_draw=15.0,
        p_away=10.0,
        lambda_h=2.5,
        lambda_a=0.8,
        league="E0"
    )
    assert any("Corners" in i["category"] for i in alt_ideas)


def test_evaluate_corners_bet_settlement():
    # 1. Total Corners Under 12.5 (10 corners -> Won, 14 corners -> Lost)
    hit, mult = evaluate_bet_hit("Under 12.5 Total Match Corners", "Arsenal", "Chelsea", 2, 1, corners_h=6, corners_a=4)
    assert hit == 1 and mult == 1.0

    hit, mult = evaluate_bet_hit("Under 12.5 Total Match Corners", "Arsenal", "Chelsea", 2, 1, corners_h=8, corners_a=6)
    assert hit == 0 and mult == -1.0

    # 2. Total Corners Over 8.5 (9 corners -> Won, 7 corners -> Lost)
    hit, mult = evaluate_bet_hit("Over 8.5 Total Match Corners", "Man City", "Liverpool", 1, 1, corners_h=6, corners_a=3)
    assert hit == 1 and mult == 1.0

    hit, mult = evaluate_bet_hit("Over 8.5 Total Match Corners", "Man City", "Liverpool", 1, 1, corners_h=4, corners_a=3)
    assert hit == 0 and mult == -1.0

    # 3. Most Corners Match Bet (Man City or Tie)
    hit, mult = evaluate_bet_hit("Most Corners: Manchester City or Tie", "Manchester City", "Fulham", 2, 0, corners_h=8, corners_a=2)
    assert hit == 1 and mult == 1.0

    hit, mult = evaluate_bet_hit("Most Corners: Manchester City or Tie", "Manchester City", "Fulham", 2, 0, corners_h=3, corners_a=5)
    assert hit == 0 and mult == -1.0

    # 4. Team Corners Over 4.5
    hit, mult = evaluate_bet_hit("Manchester City Over 4.5 Team Corners", "Manchester City", "Fulham", 2, 0, corners_h=7, corners_a=2)
    assert hit == 1 and mult == 1.0

    hit, mult = evaluate_bet_hit("Manchester City Over 4.5 Team Corners", "Manchester City", "Fulham", 2, 0, corners_h=3, corners_a=2)
    assert hit == 0 and mult == -1.0


def test_all_five_leagues_support(corners_engine):
    leagues = [
        ("Arsenal", "Chelsea", "E0"),
        ("Real Madrid", "Barcelona", "SP1"),
        ("Inter", "Juventus", "I1"),
        ("Bayern Munich", "Borussia Dortmund", "D1"),
        ("Paris SG", "Marseille", "F1")
    ]
    for h, a, div in leagues:
        pred = corners_engine.predict_corners(h, a, league=div)
        assert pred["expected_total_corners"] >= 7.0
        assert "under_12_5" in pred["probabilities"]
        assert "most_corners_home" in pred["probabilities"]
