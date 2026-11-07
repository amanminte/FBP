"""
Shin's Method & Power Method for Exact Fair Market Probabilities.
Removes bookmaker overround (vig) while accounting for insider trading / favorite-longshot bias.
"""
import numpy as np
from typing import Tuple, List, Union
from scipy.optimize import brentq

def proportional_probabilities(odds: Union[List[float], np.ndarray]) -> np.ndarray:
    """Standard proportional margin removal (baseline de-vig)."""
    inv = 1.0 / np.asarray(odds, dtype=float)
    margin = np.sum(inv)
    if margin <= 0 or np.isnan(margin):
        return np.ones_like(inv) / len(inv)
    return inv / margin

def power_probabilities(odds: Union[List[float], np.ndarray]) -> np.ndarray:
    """Power method: solves for k such that sum((1/odds_i)^k) = 1.
    Corrects for favorite-longshot bias by exponentiating implied probabilities.
    """
    inv = 1.0 / np.asarray(odds, dtype=float)
    if np.any(inv <= 0) or len(inv) < 2:
        return proportional_probabilities(odds)
    
    def obj(k):
        return np.sum(inv ** k) - 1.0

    try:
        # k typically between 0.8 and 1.5
        k_star = brentq(obj, 0.5, 3.0)
        fair_probs = inv ** k_star
        return fair_probs / np.sum(fair_probs)
    except Exception:
        return proportional_probabilities(odds)

def shin_probabilities(odds: Union[List[float], np.ndarray]) -> Tuple[np.ndarray, float]:
    """Shin's method (1991, 1992, 1993): Solves for insider trading parameter z.
    
    Model:
      pi_i = (sqrt(z^2 + 4 * (1 - z) * (beta_i^2 / sum(beta))) - z) / (2 * (1 - z))
      where beta_i = 1 / odds_i
    
    Returns:
      (fair_probabilities, z_parameter)
    """
    odds_arr = np.asarray(odds, dtype=float)
    if np.any(odds_arr <= 1.0) or len(odds_arr) < 2:
        return proportional_probabilities(odds_arr), 0.0

    beta = 1.0 / odds_arr
    sum_beta = np.sum(beta)

    if sum_beta <= 1.0:
        # No margin or negative margin
        return beta / sum_beta, 0.0

    def f_z(z):
        if z >= 1.0:
            return 1.0
        # Shin's formula for implied probability given z
        terms = np.sqrt(z**2 + 4.0 * (1.0 - z) * (beta**2 / sum_beta))
        return np.sum(terms) - (2.0 - z)

    try:
        # z represents proportion of insider trading, typically in [0.0, 0.35]
        z_star = brentq(f_z, 0.0, 0.5)
        terms = np.sqrt(z_star**2 + 4.0 * (1.0 - z_star) * (beta**2 / sum_beta))
        p = (terms - z_star) / (2.0 * (1.0 - z_star))
        p = np.clip(p, 0.001, 0.999)
        p = p / np.sum(p)
        return p, float(z_star)
    except Exception:
        # Fallback to power method or proportional
        return power_probabilities(odds_arr), 0.0
