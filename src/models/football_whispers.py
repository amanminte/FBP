"""
Football Whispers (footballwhispers.com/us/) Quantitative Intelligence Engine.
Models the signature methodologies of Football Whispers:
- Form & Tactical Matchup Angles
- Smart Bet Advice (e.g. Double Chance, Team To Score, Total Goals)
- Exact Scoreline Generation
- Both Teams To Score (BTTS) & Goal Expectancies
- Whispers Confidence Index
"""
import math
import numpy as np
from typing import Dict, Any

def _poisson_pmf(k: int, lamb: float) -> float:
    if lamb <= 0:
        return 1.0 if k == 0 else 0.0
    return (lamb ** k) * math.exp(-lamb) / math.factorial(k)

def compute_football_whispers(
    home_team: str,
    away_team: str,
    rank_h: int = 10,
    pts_h: int = 15,
    gd_h: int = 0,
    rank_a: int = 10,
    pts_a: int = 15,
    gd_a: int = 0,
    lambda_h: float = 1.55,
    lambda_a: float = 1.15,
    max_goals: int = 6
) -> Dict[str, Any]:
    """
    Simulates Football Whispers' betting preview analysis, smart tips, and scoreline model.
    """
    # Whispers Tactical Momentum Index (30.0 to 95.0)
    home_momentum = round(min(95.0, max(30.0, 52.0 + (pts_h - 14) * 2.5 + gd_h * 1.3)), 1)
    away_momentum = round(min(90.0, max(25.0, 48.0 + (pts_a - 14) * 2.5 + gd_a * 1.3)), 1)

    # Whispers Goal Expectancies with Tactical Adjustments
    whispers_exp_h = max(0.50, lambda_h + (home_momentum - away_momentum) * 0.010)
    whispers_exp_a = max(0.40, lambda_a - (home_momentum - away_momentum) * 0.008)

    # Matrix generation
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h in range(max_goals + 1):
        ph = _poisson_pmf(h, whispers_exp_h)
        for a in range(max_goals + 1):
            pa = _poisson_pmf(a, whispers_exp_a)
            matrix[h, a] = ph * pa

    tot = matrix.sum()
    if tot > 0:
        matrix /= tot

    p_home = float(sum(matrix[h, a] for h in range(max_goals + 1) for a in range(max_goals + 1) if h > a))
    p_draw = float(sum(matrix[i, i] for i in range(max_goals + 1)))
    p_away = float(sum(matrix[h, a] for h in range(max_goals + 1) for a in range(max_goals + 1) if h < a))

    # Scoreline with highest probability
    max_idx = np.unravel_index(np.argmax(matrix, axis=None), matrix.shape)
    pred_h, pred_a = int(max_idx[0]), int(max_idx[1])
    predicted_score = f"{pred_h} - {pred_a}"

    # Over / Under and BTTS
    p_over15 = float(sum(matrix[h, a] for h in range(max_goals + 1) for a in range(max_goals + 1) if (h + a) >= 2))
    p_btts = float(sum(matrix[h, a] for h in range(1, max_goals + 1) for a in range(1, max_goals + 1)))

    # Recommended Outcome
    if p_home >= p_away and p_home >= p_draw:
        rec_pick = "Home Win"
        confidence = round(p_home * 100.0, 1)
    elif p_away >= p_home and p_away >= p_draw:
        rec_pick = "Away Win"
        confidence = round(p_away * 100.0, 1)
    else:
        rec_pick = "Draw"
        confidence = round(p_draw * 100.0, 1)

    # Whispers "Smart Bet Advice" (derived for maximum safety)
    if p_home >= 0.50:
        smart_bet = f"Double Chance: {home_team} or Draw (1X)"
        smart_odds = 1.14
    elif p_away >= 0.50:
        smart_bet = f"Double Chance: {away_team} or Draw (X2)"
        smart_odds = 1.15
    elif p_over15 >= 0.75:
        smart_bet = "Over 1.5 Total Goals"
        smart_odds = 1.20
    elif p_btts >= 0.55:
        smart_bet = "Both Teams to Score (BTTS)"
        smart_odds = 1.65
    else:
        smart_bet = "Under 3.5 Total Goals"
        smart_odds = 1.25

    return {
        "source": "Football Whispers",
        "url": "https://footballwhispers.com/us/",
        "recommended_pick": rec_pick,
        "confidence": confidence,
        "predicted_score": predicted_score,
        "smart_bet": smart_bet,
        "smart_odds": smart_odds,
        "home_momentum": home_momentum,
        "away_momentum": away_momentum,
        "exp_goals": f"{whispers_exp_h:.2f} vs {whispers_exp_a:.2f}",
        "probabilities": {
            "home": round(p_home * 100.0, 1),
            "draw": round(p_draw * 100.0, 1),
            "away": round(p_away * 100.0, 1),
            "over_1_5": round(p_over15 * 100.0, 1),
            "btts": round(p_btts * 100.0, 1)
        }
    }
