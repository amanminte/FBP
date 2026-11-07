"""
Unit Tests for Yellow Cards Prediction Engine and Betting Markets.
Audits:
- Historical training on 12,900+ matches
- Mathematical validity of Poisson card distributions
- League and team discipline differential (La Liga vs EPL, Getafe vs Man City)
- Referee strictness adjustments
- Multi-market integration and alternative bet idea generation
- Live ledger settlement logic for Yellow Cards Over/Under bets
"""
import pytest
from src.models.cards_model import YellowCardsEngine, poisson_pmf
from src.models.multi_market import compute_all_market_probabilities, get_top_3_safest_picks, get_alternative_bet_ideas
from src.evaluation.live_clv_tracker import evaluate_bet_hit

@pytest.fixture
def cards_engine():
    return YellowCardsEngine.get_instance()

def test_cards_engine_training(cards_engine):
    assert cards_engine.is_trained is True
    assert len(cards_engine.team_stats) >= 50
    assert "E0" in cards_engine.league_means
    assert "SP1" in cards_engine.league_means
    # La Liga historically has significantly more cards than Premier League
    assert cards_engine.league_means["SP1"] > cards_engine.league_means["E0"]

def test_cards_probability_distributions(cards_engine):
    pred = cards_engine.predict_yellow_cards("Arsenal", "Chelsea", league="E0")
    assert "probabilities" in pred
    assert "fair_odds" in pred
    assert "best_card_bet" in pred

    probs = pred["probabilities"]
    # Probabilities must be bounded
    for k, v in probs.items():
        assert 0.0 <= v <= 100.0

    # Over + Under must sum to 100% within rounding tolerance
    assert abs((probs["over_2_5"] + probs["under_2_5"]) - 100.0) < 0.2
    assert abs((probs["over_3_5"] + probs["under_3_5"]) - 100.0) < 0.2
    assert abs((probs["over_4_5"] + probs["under_4_5"]) - 100.0) < 0.2
    assert abs((probs["over_5_5"] + probs["under_5_5"]) - 100.0) < 0.2

    # Expected cards must be positive and physically realistic (between 1.5 and 8.0)
    assert 1.5 <= pred["expected_total_cards"] <= 8.0

def test_cards_high_vs_low_teams(cards_engine):
    # La Liga clash with disciplined/physical history
    pred_sp1 = cards_engine.predict_yellow_cards("Getafe", "Ath Madrid", league="SP1")
    # Low-fouling Premier League clash
    pred_e0 = cards_engine.predict_yellow_cards("Manchester City", "Liverpool", league="E0")

    assert pred_sp1["expected_total_cards"] > pred_e0["expected_total_cards"]
    assert pred_sp1["probabilities"]["over_3_5"] > pred_e0["probabilities"]["over_3_5"]

def test_cards_referee_adjustment(cards_engine):
    # Find two referees if available
    ref_keys = list(cards_engine.referee_stats.keys())
    if len(ref_keys) >= 2:
        sorted_refs = sorted(ref_keys, key=lambda r: cards_engine.referee_stats[r]["cards_mean"] if isinstance(cards_engine.referee_stats[r], dict) else cards_engine.referee_stats[r])
        lenient_ref = sorted_refs[0]
        strict_ref = sorted_refs[-1]

        pred_lenient = cards_engine.predict_yellow_cards("Everton", "Liverpool", league="E0", referee=lenient_ref)
        pred_strict = cards_engine.predict_yellow_cards("Everton", "Liverpool", league="E0", referee=strict_ref)

        assert pred_strict["expected_total_cards"] >= pred_lenient["expected_total_cards"]

def test_multi_market_cards_integration():
    markets = compute_all_market_probabilities(
        home_team="Arsenal",
        away_team="Tottenham",
        p_home=0.55,
        p_draw=0.25,
        p_away=0.20,
        lambda_h=2.1,
        lambda_a=1.2,
        league="E0"
    )
    assert "yellow_cards" in markets
    assert markets["yellow_cards"]["expected_total_cards"] > 0

    alt_ideas = get_alternative_bet_ideas(
        home_team="Getafe",
        away_team="Sevilla",
        p_home=40.0,
        p_draw=30.0,
        p_away=30.0,
        lambda_h=1.1,
        lambda_a=1.0,
        league="SP1"
    )
    card_ideas = [i for i in alt_ideas if "Card" in i.get("category", "") or "card" in i.get("title", "").lower()]
    assert len(card_ideas) >= 1

def test_evaluate_yellow_cards_bet_settlement():
    # Over 3.5 Yellow Cards: 2 home cards + 2 away cards = 4 cards -> HIT
    hit, mult = evaluate_bet_hit("Over 3.5 Total Yellow Cards", "Arsenal", "Chelsea", 1, 0, cards_h=2, cards_a=2)
    assert hit == 1 and mult == 1.0

    # Over 3.5 Yellow Cards: 1 home card + 2 away cards = 3 cards -> MISS
    hit, mult = evaluate_bet_hit("Over 3.5 Total Yellow Cards", "Arsenal", "Chelsea", 1, 0, cards_h=1, cards_a=2)
    assert hit == 0 and mult == -1.0

    # Under 4.5 Yellow Cards: 2 home cards + 2 away cards = 4 cards -> HIT
    hit, mult = evaluate_bet_hit("Under 4.5 Total Yellow Cards", "Arsenal", "Chelsea", 2, 1, cards_h=2, cards_a=2)
    assert hit == 1 and mult == 1.0

    # Under 4.5 Yellow Cards: 3 home cards + 2 away cards = 5 cards -> MISS
    hit, mult = evaluate_bet_hit("Under 4.5 Total Yellow Cards", "Arsenal", "Chelsea", 2, 1, cards_h=3, cards_a=2)
    assert hit == 0 and mult == -1.0

    # Over 2.5 Yellow Cards: 1 home card + 2 away cards = 3 cards -> HIT
    hit, mult = evaluate_bet_hit("Over 2.5 Total Yellow Cards", "Everton", "Liverpool", 0, 0, cards_h=1, cards_a=2)
    assert hit == 1 and mult == 1.0


def test_derby_detection_and_inflation(cards_engine):
    # North London Derby (Arsenal vs Tottenham)
    pred_derby = cards_engine.predict_yellow_cards("Arsenal", "Tottenham", league="E0")
    pred_normal = cards_engine.predict_yellow_cards("Arsenal", "Fulham", league="E0")

    assert pred_derby["is_derby"] is True
    assert "North London Derby" in pred_derby["derby_name"]
    assert pred_derby["expected_total_cards"] > pred_normal["expected_total_cards"]

    # Rome Derby (Roma vs Lazio) in Serie A
    pred_roma = cards_engine.predict_yellow_cards("Roma", "Lazio", league="I1")
    assert pred_roma["is_derby"] is True
    assert "Derby della Capitale" in pred_roma["derby_name"]
    # Rome Derby historically has very high cards expectation
    assert pred_roma["expected_total_cards"] >= 5.0

    # El Clasico (Real Madrid vs Barcelona) in La Liga
    pred_clasico = cards_engine.predict_yellow_cards("Real Madrid", "Barcelona", league="SP1")
    assert pred_clasico["is_derby"] is True
    assert "El Clásico" in pred_clasico["derby_name"]

def test_all_five_leagues_support(cards_engine):
    leagues = ["E0", "SP1", "I1", "D1", "F1"]
    sample_fixtures = [
        ("E0", "Arsenal", "Liverpool"),
        ("SP1", "Real Madrid", "Barcelona"),
        ("I1", "Inter", "Juventus"),
        ("D1", "Bayern Munich", "Dortmund"),
        ("F1", "Paris SG", "Marseille")
    ]
    for lg, h, a in sample_fixtures:
        pred = cards_engine.predict_yellow_cards(h, a, league=lg)
        assert pred["league"] == lg
        assert pred["expected_total_cards"] > 0
        assert "over_3_5" in pred["probabilities"]
        assert "under_3_5" in pred["probabilities"]
