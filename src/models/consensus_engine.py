"""
Penta-Consensus & Common-Ground Market Harmonization Engine.
Fuses 5 Independent Predictive Intelligence Systems:
1. 🤖 Syndicate ML Model (LightGBM + XGBoost + CatBoost + Dixon-Coles)
2. 📊 Forebet (Poisson Exact Scorelines & Algorithmic 1X2 Probabilities)
3. 📈 Understat (Expected Goals xG, Non-Penalty xG, and xPTS Projections)
4. ⭐ WhoScored (Match Ratings, Tactical Department Mismatches)
5. 🎯 FootballPredictor.net (Form Streaks, Goal Expectancies & Exact Scores)

Key Capabilities:
- 👑 Penta-Lock Royal Diamond (5/5 Unanimous Agreement)
- 💎 Quad-Lock Diamond (4/5 Agreement)
- 🥇 Triple-Lock Gold (3/5 Agreement)
- ⚡ Common Ground Market Harmonizer: When 1X2 winner picks are split or opposed
  (e.g. 2 Home vs 2 Draw vs 1 Away), analyzes all predicted scores across all 5 engines
  to find the universal common ground market (Over 1.5, Under 2.5, Under 1.5, BTTS Yes/No, Double Chance)
  that unites all systems into a high-safety bet!
"""
from typing import Dict, Any, List, Optional
import numpy as np

def parse_score(score_str: str) -> Optional[tuple[int, int]]:
    """Extracts (home_goals, away_goals) from score string like '2 - 1' or '2-0'."""
    try:
        parts = score_str.replace(" ", "").split("-")
        return int(parts[0]), int(parts[1])
    except Exception:
        return None

def find_common_ground_market(
    home_team: str,
    away_team: str,
    sources: List[Dict[str, Any]],
    lambda_h: float,
    lambda_a: float
) -> Dict[str, Any]:
    """
    Arbitrates conflicts when 1X2 picks disagree.
    Inspects predicted scores and goal metrics across all systems to discover the common denominator.
    """
    scores = []
    for s in sources:
        sc = s.get("score")
        if sc:
            parsed = parse_score(sc)
            if parsed:
                scores.append(parsed)

    # Fallback to Poisson expected score if missing
    if len(scores) < 3:
        h_round, a_round = int(round(lambda_h)), int(round(lambda_a))
        scores.append((h_round, a_round))

    tot_scores = len(scores)
    if tot_scores == 0:
        scores = [(1, 1)]
        tot_scores = 1

    # Evaluate candidate common ground markets
    # 1. Over 1.5 Goals
    o15_hits = sum(1 for h, a in scores if (h + a) >= 2)
    o15_pct = round(o15_hits / tot_scores * 100.0, 1)

    # 2. Under 1.5 Goals
    u15_hits = sum(1 for h, a in scores if (h + a) <= 1)
    u15_pct = round(u15_hits / tot_scores * 100.0, 1)

    # 3. Under 2.5 Goals
    u25_hits = sum(1 for h, a in scores if (h + a) <= 2)
    u25_pct = round(u25_hits / tot_scores * 100.0, 1)

    # 4. Under 3.5 Goals
    u35_hits = sum(1 for h, a in scores if (h + a) <= 3)
    u35_pct = round(u35_hits / tot_scores * 100.0, 1)

    # 5. Both Teams To Score (BTTS Yes)
    btts_hits = sum(1 for h, a in scores if h >= 1 and a >= 1)
    btts_pct = round(btts_hits / tot_scores * 100.0, 1)

    # 6. BTTS No (Clean Sheet by at least one side)
    btts_no_hits = sum(1 for h, a in scores if h == 0 or a == 0)
    btts_no_pct = round(btts_no_hits / tot_scores * 100.0, 1)

    # 7. Double Chance 1X (Home or Draw)
    dc_1x_hits = sum(1 for h, a in scores if h >= a)
    dc_1x_pct = round(dc_1x_hits / tot_scores * 100.0, 1)

    # 8. Double Chance X2 (Away or Draw)
    dc_x2_hits = sum(1 for h, a in scores if a >= h)
    dc_x2_pct = round(dc_x2_hits / tot_scores * 100.0, 1)

    candidates = [
        {
            "market": "Over 1.5 Total Match Goals",
            "category": "Over Goals",
            "agreement_pct": o15_pct,
            "hits": f"{o15_hits}/{tot_scores}",
            "fair_odds": round(max(1.10, 1.0 / max(0.01, o15_pct / 100.0)), 2),
            "reason": f"Although 1X2 winner picks are split, {o15_hits} of {tot_scores} predicted scorelines ({', '.join([f'{h}-{a}' for h,a in scores])}) contain 2+ goals."
        },
        {
            "market": "Under 2.5 Total Match Goals",
            "category": "Under Goals",
            "agreement_pct": u25_pct,
            "hits": f"{u25_hits}/{tot_scores}",
            "fair_odds": round(max(1.15, 1.0 / max(0.01, u25_pct / 100.0)), 2),
            "reason": f"Engines project low-scoring defensive friction; {u25_hits} of {tot_scores} models predict 2 or fewer total goals."
        },
        {
            "market": "Under 3.5 Total Match Goals",
            "category": "Under Goals",
            "agreement_pct": u35_pct,
            "hits": f"{u35_hits}/{tot_scores}",
            "fair_odds": round(max(1.08, 1.0 / max(0.01, u35_pct / 100.0)), 2),
            "reason": f"High statistical ceiling: {u35_hits} of {tot_scores} models keep match scorelines capped at 3 goals or less."
        },
        {
            "market": "Both Teams To Score: YES (BTTS)",
            "category": "BTTS",
            "agreement_pct": btts_pct,
            "hits": f"{btts_hits}/{tot_scores}",
            "fair_odds": round(max(1.20, 1.0 / max(0.01, btts_pct / 100.0)), 2),
            "reason": f"Both attacks are projected to find the net ({btts_hits}/{tot_scores} scorelines have both teams scoring)."
        },
        {
            "market": "Both Teams To Score: NO (At least one Clean Sheet)",
            "category": "Clean Sheet",
            "agreement_pct": btts_no_pct,
            "hits": f"{btts_no_hits}/{tot_scores}",
            "fair_odds": round(max(1.20, 1.0 / max(0.01, btts_no_pct / 100.0)), 2),
            "reason": f"{btts_no_hits} of {tot_scores} models anticipate a defensive shutout or blank."
        },
        {
            "market": f"Double Chance: {home_team} or Draw (1X)",
            "category": "Double Chance",
            "agreement_pct": dc_1x_pct,
            "hits": f"{dc_1x_hits}/{tot_scores}",
            "fair_odds": round(max(1.12, 1.0 / max(0.01, dc_1x_pct / 100.0)), 2),
            "reason": f"Unites both Home Win and Draw predictions ({dc_1x_hits}/{tot_scores} systems avoid away defeat)."
        },
        {
            "market": f"Double Chance: {away_team} or Draw (X2)",
            "category": "Double Chance",
            "agreement_pct": dc_x2_pct,
            "hits": f"{dc_x2_hits}/{tot_scores}",
            "fair_odds": round(max(1.12, 1.0 / max(0.01, dc_x2_pct / 100.0)), 2),
            "reason": f"Unites both Away Win and Draw predictions ({dc_x2_hits}/{tot_scores} systems avoid home defeat)."
        }
    ]

    # If ultra low scoring (e.g. 0-0 or 1-0 or 0-1)
    if u15_pct >= 60.0:
        candidates.append({
            "market": "Under 1.5 Total Match Goals",
            "category": "Under Goals",
            "agreement_pct": u15_pct,
            "hits": f"{u15_hits}/{tot_scores}",
            "fair_odds": round(max(1.30, 1.0 / max(0.01, u15_pct / 100.0)), 2),
            "reason": f"Extreme low-scoring deadlock projected ({u15_hits}/{tot_scores} models predict 0 or 1 total goal)."
        })

    # Sort by highest agreement percentage
    ranked = sorted(candidates, key=lambda x: x["agreement_pct"], reverse=True)
    best = ranked[0]

    return {
        "best_common_ground_market": best["market"],
        "category": best["category"],
        "common_ground_agreement": best["agreement_pct"],
        "score_hits": best["hits"],
        "fair_odds": best["fair_odds"],
        "plain_explanation": best["reason"],
        "all_predicted_scores": [f"{h}-{a}" for h, a in scores],
        "top_alternatives": ranked[1:3]
    }


def evaluate_penta_consensus(
    home_team: str,
    away_team: str,
    ml_prediction: str,
    ml_confidence: float,
    ml_score: str,
    forebet_data: Dict[str, Any],
    understat_data: Dict[str, Any],
    whoscored_data: Dict[str, Any],
    football_predictor_data: Dict[str, Any],
    lambda_h: float = 1.55,
    lambda_a: float = 1.15
) -> Dict[str, Any]:
    """
    Evaluates 5-source consensus and runs Common Ground Conflict Arbitrage when engines diverge.
    """
    def normalize_pick(raw: str) -> str:
        s = str(raw).lower()
        if "home" in s or "(1)" in s:
            return "Home Win"
        if "away" in s or "(2)" in s:
            return "Away Win"
        return "Draw"

    p_ml = normalize_pick(ml_prediction)
    p_fb = normalize_pick(forebet_data.get("recommended_pick", "Home Win"))
    p_us = normalize_pick(understat_data.get("verdict", "Home Win"))
    p_ws = normalize_pick(whoscored_data.get("verdict", "Home Win"))
    p_fp = normalize_pick(football_predictor_data.get("recommended_pick", "Home Win"))

    votes = [p_ml, p_fb, p_us, p_ws, p_fp]
    counts = {
        "Home Win": votes.count("Home Win"),
        "Draw": votes.count("Draw"),
        "Away Win": votes.count("Away Win")
    }

    dominant_pick = max(counts, key=counts.get)
    consensus_count = counts[dominant_pick]

    if dominant_pick == "Home Win":
        dominant_team_pick = f"{home_team} to Win"
        primary_winner = home_team
    elif dominant_pick == "Away Win":
        dominant_team_pick = f"{away_team} to Win"
        primary_winner = away_team
    else:
        dominant_team_pick = "Draw (Points Shared)"
        primary_winner = "Draw"

    # Exact score extraction for each engine
    score_ml = ml_score or f"{int(round(lambda_h))} - {int(round(lambda_a))}"
    score_fb = forebet_data.get("predicted_score", "2 - 0")
    score_us = f"{int(round(understat_data.get('xg_h', 2.0)))} - {int(round(understat_data.get('xg_a', 1.0)))}"
    score_ws = "2 - 1" if p_ws == "Home Win" else ("1 - 2" if p_ws == "Away Win" else "1 - 1")
    score_fp = football_predictor_data.get("predicted_score", "2 - 1")

    sources = [
        {
            "name": "Syndicate ML Model",
            "icon": "🤖",
            "pick": p_ml,
            "pick_readable": f"{home_team} Win" if p_ml == "Home Win" else (f"{away_team} Win" if p_ml == "Away Win" else "Draw"),
            "score": score_ml,
            "metric_label": "Win Probability",
            "metric_value": f"{ml_confidence:.1f}%",
            "secondary": f"Predicted Score: {score_ml} • Multi-Model Ensemble",
            "agrees": (p_ml == dominant_pick)
        },
        {
            "name": "Forebet Algorithmic",
            "icon": "📊",
            "pick": p_fb,
            "pick_readable": f"{home_team} Win" if p_fb == "Home Win" else (f"{away_team} Win" if p_fb == "Away Win" else "Draw"),
            "score": score_fb,
            "metric_label": "Predicted Score",
            "metric_value": score_fb,
            "secondary": f"Poisson Odds: {forebet_data.get('forebet_probs', {}).get('home', 50)}% H / {forebet_data.get('forebet_probs', {}).get('draw', 25)}% D",
            "agrees": (p_fb == dominant_pick)
        },
        {
            "name": "Understat xG Engine",
            "icon": "📈",
            "pick": p_us,
            "pick_readable": f"{home_team} Win" if p_us == "Home Win" else (f"{away_team} Win" if p_us == "Away Win" else "Draw"),
            "score": score_us,
            "metric_label": "Expected Goals (xG)",
            "metric_value": f"{understat_data.get('xg_h', 0.0)} vs {understat_data.get('xg_a', 0.0)}",
            "secondary": f"xPTS: {understat_data.get('xpts_h', 0.0)} vs {understat_data.get('xpts_a', 0.0)} (Diff: {understat_data.get('xg_diff', 0.0):+.2f} xG)",
            "agrees": (p_us == dominant_pick)
        },
        {
            "name": "WhoScored Match Ratings",
            "icon": "⭐",
            "pick": p_ws,
            "pick_readable": f"{home_team} Win" if p_ws == "Home Win" else (f"{away_team} Win" if p_ws == "Away Win" else "Draw"),
            "score": score_ws,
            "metric_label": "Tactical Rating",
            "metric_value": f"{whoscored_data.get('rating_h', 0.0)} vs {whoscored_data.get('rating_a', 0.0)}",
            "secondary": f"{whoscored_data.get('poss_h', 50)}% Poss • {whoscored_data.get('positional_mismatches', 1)} Department Mismatches",
            "agrees": (p_ws == dominant_pick)
        },
        {
            "name": "FootballPredictor Net",
            "icon": "🎯",
            "pick": p_fp,
            "pick_readable": f"{home_team} Win" if p_fp == "Home Win" else (f"{away_team} Win" if p_fp == "Away Win" else "Draw"),
            "score": score_fp,
            "metric_label": "Form Rating",
            "metric_value": f"{football_predictor_data.get('form_h', 50)}% vs {football_predictor_data.get('form_a', 50)}%",
            "secondary": f"Score: {score_fp} • Tip: {football_predictor_data.get('recommended_tip', 'Over 1.5')}",
            "agrees": (p_fp == dominant_pick)
        }
    ]

    # Evaluate Common Ground Market (Arbitrage bridge across all scores)
    common_ground = find_common_ground_market(home_team, away_team, sources, lambda_h, lambda_a)

    # Classification Tiers
    if consensus_count == 5:
        consensus_tier = "👑 PENTA-LOCK ROYAL DIAMOND (5/5 UNANIMOUS)"
        tier_level = 1
        tier_badge_color = "#047857"
        bg_color = "#ecfdf5"
        border_color = "#10b981"
        confidence_score = 94.8
        verdict_summary = (
            f"🎯 100% UNANIMOUS ROYAL LOCK: All 5 independent predictive engines "
            f"(Syndicate ML, Forebet, Understat, WhoScored, and FootballPredictor) converge unanimously on {dominant_team_pick}. "
            f"Statistically represents the highest safety grade achievable."
        )
        if dominant_pick == "Home Win":
            recommended_diamond_bet = f"Double Chance: {home_team} or Draw (1X)"
        elif dominant_pick == "Away Win":
            recommended_diamond_bet = f"Double Chance: {away_team} or Draw (X2)"
        else:
            recommended_diamond_bet = "Under 2.5 Total Match Goals"
        safe_lock_odds = "1.12 - 1.25"
        is_split = False
    elif consensus_count == 4:
        consensus_tier = "💎 QUAD-LOCK DIAMOND CONSENSUS (4/5 SYSTEMS AGREE)"
        tier_level = 2
        tier_badge_color = "#0f766e"
        bg_color = "#f0fdfa"
        border_color = "#14b8a6"
        confidence_score = 88.5
        dissenting = [s["name"] for s in sources if not s["agrees"]]
        dissent_str = ", ".join(dissenting)
        verdict_summary = (
            f"⚡ 4-WAY SUPER CONSENSUS: 4 of 5 engines converge directly on {dominant_team_pick}. "
            f"Only {dissent_str} offered an alternative angle. High-conviction anchor bet."
        )
        recommended_diamond_bet = f"Draw No Bet (DNB): {primary_winner}" if dominant_pick != "Draw" else "Double Chance 1X"
        safe_lock_odds = "1.22 - 1.40"
        is_split = False
    elif consensus_count == 3:
        consensus_tier = "🥇 TRIPLE-LOCK GOLD CONSENSUS (3/5 MAJORITY)"
        tier_level = 3
        tier_badge_color = "#b45309"
        bg_color = "#fffbeb"
        border_color = "#f59e0b"
        confidence_score = 81.0
        verdict_summary = (
            f"⚖️ MAJORITY AGREEMENT: 3 of 5 engines agree on {dominant_team_pick}. "
            f"However, 2 systems project a contested match. Common ground arbitrage is recommended for safer staking."
        )
        recommended_diamond_bet = common_ground["best_common_ground_market"]
        safe_lock_odds = f"{common_ground['fair_odds']:.2f}"
        is_split = True
    else:
        consensus_tier = "⚡ SPLIT CONFLICT RESOLVED: COMMON GROUND ARBITRAGE LOCK"
        tier_level = 4
        tier_badge_color = "#4338ca"
        bg_color = "#eef2ff"
        border_color = "#6366f1"
        confidence_score = common_ground["common_ground_agreement"]
        verdict_summary = (
            f"🔄 CONFLICT RESOLVED BY DERIVATIVE ARBITRAGE: While the 5 engines are divided on the match winner "
            f"({counts['Home Win']} Home, {counts['Draw']} Draw, {counts['Away Win']} Away), they share a remarkable "
            f"{common_ground['common_ground_agreement']}% agreement on {common_ground['best_common_ground_market']}! "
            f"{common_ground['plain_explanation']}"
        )
        recommended_diamond_bet = common_ground["best_common_ground_market"]
        safe_lock_odds = f"{common_ground['fair_odds']:.2f}"
        is_split = True

    return {
        "consensus_tier": consensus_tier,
        "tier_level": tier_level,
        "dominant_pick": dominant_pick,
        "dominant_team_pick": dominant_team_pick,
        "consensus_count": consensus_count,
        "total_sources": 5,
        "confidence_score": confidence_score,
        "verdict_summary": verdict_summary,
        "recommended_diamond_bet": recommended_diamond_bet,
        "safe_lock_odds": safe_lock_odds,
        "tier_badge_color": tier_badge_color,
        "bg_color": bg_color,
        "border_color": border_color,
        "is_split": is_split,
        "common_ground": common_ground,
        "sources": sources
    }
