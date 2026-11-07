"""
Pre-Match News, Injury & Press Conference AI Pipeline.
Extracts structured news shocks from RSS feeds / match notes and applies bounded Bayesian lambda adjustments.
"""
import re
import json
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# Keyword dictionaries for robust NLP extraction
KEY_INJURY_KEYWORDS = ["ruled out", "injured", "sidelined", "torn", "hamstring", "knee", "surgery", "suspended", "red card ban", "doubtful"]
KEY_ROTATION_KEYWORDS = ["rested", "rotation", "champions league tie", "bench", "congestion", "fatigue", "prioritizing"]
KEY_MANAGER_KEYWORDS = ["sacked", "dismissed", "interim", "appointed", "new manager", "departure"]
KEY_MORALE_KEYWORDS = ["crisis", "strike", "dressing room row", "unrest", "disciplinary", "brawl", "protest"]

def extract_news_shock_from_text(team_name: str, text: str) -> Dict[str, Any]:
    """Parses raw match preview text or news feed into a strict Pre-Match Shock dictionary."""
    text_lower = text.lower()
    
    # 1. Starters ruled out
    ruled_out_count = 0
    positions_out = []
    
    for kw in KEY_INJURY_KEYWORDS:
        if kw in text_lower:
            ruled_out_count += text_lower.count(kw)
    ruled_out_count = min(3, ruled_out_count)

    # Position checks
    if any(p in text_lower for p in ["striker", "forward", "winger", "haaland", "saka", "mbappe", "kane"]):
        positions_out.append("FWD")
    if any(p in text_lower for p in ["defender", "centre-back", "fullback", "saliba", "dias", "van dijk"]):
        positions_out.append("DEF")
    if any(p in text_lower for p in ["midfielder", "anchor", "rodri", "de bruyne", "bellingham", "odegaard"]):
        positions_out.append("MID")

    # GK out
    primary_gk_out = any(gk in text_lower for gk in ["goalkeeper", "keeper", "alisson", "courtois", "ederson", "neuer", "raya"]) and any(kw in text_lower for kw in KEY_INJURY_KEYWORDS)

    # Rotation risk
    rotation_risk = 0.0
    if any(kw in text_lower for kw in KEY_ROTATION_KEYWORDS):
        rotation_risk = 0.35 if "champions league" in text_lower else 0.20

    # Manager change
    manager_change = any(kw in text_lower for kw in KEY_MANAGER_KEYWORDS)

    # Crisis / Morale
    crisis = any(kw in text_lower for kw in KEY_MORALE_KEYWORDS)

    return {
        "team": team_name,
        "key_starters_ruled_out_count": ruled_out_count,
        "key_player_positions_out": list(set(positions_out)),
        "primary_gk_out": bool(primary_gk_out),
        "european_cup_rotation_risk": float(rotation_risk),
        "manager_change_within_14d": bool(manager_change),
        "squad_morale_or_disciplinary_crisis": bool(crisis),
        "weather_pitch_severity": 0.0,
        "confidence_of_report": 0.85
    }

def apply_bayesian_news_adjustment(
    base_lambda_h: float,
    base_lambda_a: float,
    home_shock: Dict[str, Any],
    away_shock: Dict[str, Any]
) -> Tuple[float, float, Dict[str, Any]]:
    """Applies bounded domain-calibrated multipliers to Dixon-Coles expected goals (lambda_H, lambda_A).
    
    Formula:
      lambda_H_adj = lambda_H * (1 - 0.06 * n_fwd_out) * (1 - 0.08 * rot_risk) * (1 + 0.05 * n_opp_def_out) * (1 + 0.09 * opp_gk_out)
    """
    # Home adjustments
    n_fwd_h = 1 if "FWD" in home_shock.get("key_player_positions_out", []) else 0
    n_def_h = 1 if "DEF" in home_shock.get("key_player_positions_out", []) else 0
    rot_h = home_shock.get("european_cup_rotation_risk", 0.0)
    gk_h = 1.0 if home_shock.get("primary_gk_out", False) else 0.0

    # Away adjustments
    n_fwd_a = 1 if "FWD" in away_shock.get("key_player_positions_out", []) else 0
    n_def_a = 1 if "DEF" in away_shock.get("key_player_positions_out", []) else 0
    rot_a = away_shock.get("european_cup_rotation_risk", 0.0)
    gk_a = 1.0 if away_shock.get("primary_gk_out", False) else 0.0

    # Bound multipliers between 0.65 and 1.40
    mult_h = (1.0 - 0.06 * n_fwd_h) * (1.0 - 0.08 * rot_h) * (1.0 + 0.05 * n_def_a) * (1.0 + 0.09 * gk_a)
    mult_a = (1.0 - 0.06 * n_fwd_a) * (1.0 - 0.08 * rot_a) * (1.0 + 0.05 * n_def_h) * (1.0 + 0.09 * gk_h)

    mult_h = float(np.clip(mult_h, 0.65, 1.40))
    mult_a = float(np.clip(mult_a, 0.65, 1.40))

    adj_lambda_h = float(np.clip(base_lambda_h * mult_h, 0.20, 6.0))
    adj_lambda_a = float(np.clip(base_lambda_a * mult_a, 0.20, 6.0))

    shock_summary = {
        "home_multiplier": round(mult_h, 3),
        "away_multiplier": round(mult_a, 3),
        "home_lambda_shift": f"{base_lambda_h:.2f} -> {adj_lambda_h:.2f}",
        "away_lambda_shift": f"{base_lambda_a:.2f} -> {adj_lambda_a:.2f}",
        "home_shock_details": home_shock,
        "away_shock_details": away_shock
    }

    return adj_lambda_h, adj_lambda_a, shock_summary
