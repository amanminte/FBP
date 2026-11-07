"""
Forebet Mathematical Prediction & Ensemble Fusion Engine.
Emulates Forebet's proprietary mathematical Poisson modeling and provides seamless
fusion with our syndicate ML models (LightGBM + XGBoost + CatBoost + Dixon-Coles).

Outputs:
- Forebet 1X2 Mathematical Probabilities
- Forebet Predicted Exact Scoreline (e.g. 2 - 0)
- Forebet Over/Under 2.5 Goals % & BTTS %
- Fused Consensus Ensemble (Weighted blend between Our Model and Forebet)
"""
import math
import numpy as np
from typing import Dict, Any, Tuple

def poisson_pmf(k: int, lamb: float) -> float:
    """Computes Poisson probability P(X = k; lambda)."""
    if lamb <= 0:
        return 1.0 if k == 0 else 0.0
    return (lamb ** k) * math.exp(-lamb) / math.factorial(k)

def compute_forebet_prediction(
    lambda_h: float,
    lambda_a: float,
    home_team: str,
    away_team: str,
    max_goals: int = 6
) -> Dict[str, Any]:
    """
    Computes Forebet mathematical model distribution:
    - 1X2 Probabilities
    - Most probable exact scoreline
    - Over 2.5 and BTTS expectations
    """
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h in range(max_goals + 1):
        p_h = poisson_pmf(h, lambda_h)
        for a in range(max_goals + 1):
            p_a = poisson_pmf(a, lambda_a)
            matrix[h, a] = p_h * p_a
    
    total = matrix.sum()
    if total > 0:
        matrix /= total

    # 1X2 Probabilities
    p_home = float(sum(matrix[h, a] for h in range(max_goals + 1) for a in range(max_goals + 1) if h > a))
    p_draw = float(sum(matrix[i, i] for i in range(max_goals + 1)))
    p_away = float(sum(matrix[h, a] for h in range(max_goals + 1) for a in range(max_goals + 1) if h < a))

    # Highest probability exact scoreline (Forebet trademark)
    max_idx = np.unravel_index(np.argmax(matrix, axis=None), matrix.shape)
    pred_score = f"{max_idx[0]} - {max_idx[1]}"
    pred_score_prob = round(float(matrix[max_idx]) * 100.0, 1)

    # Over 2.5 goals and BTTS
    p_o25 = float(sum(matrix[h, a] for h in range(max_goals + 1) for a in range(max_goals + 1) if h + a > 2))
    p_btts = float(sum(matrix[h, a] for h in range(1, max_goals + 1) for a in range(1, max_goals + 1)))

    return {
        "forebet_probs": {
            "home": round(p_home * 100.0, 1),
            "draw": round(p_draw * 100.0, 1),
            "away": round(p_away * 100.0, 1)
        },
        "predicted_score": pred_score,
        "score_probability": pred_score_prob,
        "over_2_5_pct": round(p_o25 * 100.0, 1),
        "btts_pct": round(p_btts * 100.0, 1),
        "avg_goals": round(float(lambda_h + lambda_a), 2),
        "recommended_pick": "Home Win (1)" if p_home > max(p_draw, p_away) else ("Away Win (2)" if p_away > p_draw else "Draw (X)")
    }

def fuse_model_with_forebet(
    model_probs: Dict[str, float],
    forebet_probs: Dict[str, float],
    model_weight: float = 0.50
) -> Dict[str, Any]:
    """
    Fuses our syndicate model probabilities with Forebet's mathematical predictions.
    Computes ensemble consensus and detects whether both models agree or diverge.
    """
    fb_weight = 1.0 - model_weight
    
    m_h, m_d, m_a = model_probs.get("home_win", 50.0), model_probs.get("draw", 25.0), model_probs.get("away_win", 25.0)
    fb_h, fb_d, fb_a = forebet_probs.get("home", 50.0), forebet_probs.get("draw", 25.0), forebet_probs.get("away", 25.0)

    fused_h = round(model_weight * m_h + fb_weight * fb_h, 1)
    fused_d = round(model_weight * m_d + fb_weight * fb_d, 1)
    fused_a = round(model_weight * m_a + fb_weight * fb_a, 1)

    # Re-normalize
    tot = fused_h + fused_d + fused_a
    if tot > 0:
        fused_h = round(fused_h / tot * 100.0, 1)
        fused_d = round(fused_d / tot * 100.0, 1)
        fused_a = round(100.0 - fused_h - fused_d, 1)

    m_pick = "Home Win" if m_h > max(m_d, m_a) else ("Away Win" if m_a > m_d else "Draw")
    fb_pick = "Home Win" if fb_h > max(fb_d, fb_a) else ("Away Win" if fb_a > fb_d else "Draw")

    if m_pick == fb_pick:
        consensus_status = f"🔒 Strong Consensus Lock (Both Models Pick {m_pick})"
        is_consensus = True
    else:
        consensus_status = f"⚠️ Model Divergence (Our Model: {m_pick} vs Forebet: {fb_pick})"
        is_consensus = False

    return {
        "fused_probabilities": {
            "home_win": fused_h,
            "draw": fused_d,
            "away_win": fused_a
        },
        "model_pick": m_pick,
        "forebet_pick": fb_pick,
        "fused_pick": "Home Win" if fused_h > max(fused_d, fused_a) else ("Away Win" if fused_a > fused_d else "Draw"),
        "consensus_status": consensus_status,
        "is_consensus": is_consensus,
        "model_weight": round(model_weight * 100.0),
        "forebet_weight": round(fb_weight * 100.0)
    }
