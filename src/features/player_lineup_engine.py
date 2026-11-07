"""
Player Lineup Engine & Player Value-Added (PVA_90) Architecture.
Computes Starting XI Strength Ratios, Attack Threat Retention, GK Absence Flags,
and Squad Fatigue Load for both historical training rows and live pre-match lineups.
"""
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd

# Comprehensive Roster Database with Position, PVA_90, and Impact Scores (PIS in [0.0, 10.0])
SQUAD_DATABASE: Dict[str, Dict[str, Dict[str, Any]]] = {
    "Manchester City": {
        "Erling Haaland": {"pos": "FWD", "pis": 9.8, "npxg90": 0.88, "xa90": 0.12, "is_gk": False, "is_starter": True},
        "Rodri": {"pos": "MID", "pis": 9.6, "npxg90": 0.15, "xa90": 0.22, "is_gk": False, "is_starter": True},
        "Kevin De Bruyne": {"pos": "MID", "pis": 9.4, "npxg90": 0.25, "xa90": 0.52, "is_gk": False, "is_starter": True},
        "Phil Foden": {"pos": "FWD", "pis": 8.9, "npxg90": 0.42, "xa90": 0.30, "is_gk": False, "is_starter": True},
        "Ruben Dias": {"pos": "DEF", "pis": 8.8, "npxg90": 0.04, "xa90": 0.03, "is_gk": False, "is_starter": True},
        "Josko Gvardiol": {"pos": "DEF", "pis": 8.5, "npxg90": 0.12, "xa90": 0.10, "is_gk": False, "is_starter": True},
        "Ederson": {"pos": "GK", "pis": 8.7, "npxg90": 0.00, "xa90": 0.02, "is_gk": True, "is_starter": True},
        "Bernardo Silva": {"pos": "MID", "pis": 8.7, "npxg90": 0.22, "xa90": 0.28, "is_gk": False, "is_starter": True},
        "Manuel Akanji": {"pos": "DEF", "pis": 8.1, "npxg90": 0.05, "xa90": 0.04, "is_gk": False, "is_starter": True},
        "Mateo Kovacic": {"pos": "MID", "pis": 8.0, "npxg90": 0.10, "xa90": 0.15, "is_gk": False, "is_starter": True},
        "Jeremy Doku": {"pos": "FWD", "pis": 8.2, "npxg90": 0.25, "xa90": 0.35, "is_gk": False, "is_starter": True}
    },
    "Arsenal": {
        "Bukayo Saka": {"pos": "FWD", "pis": 9.5, "npxg90": 0.48, "xa90": 0.45, "is_gk": False, "is_starter": True},
        "Martin Odegaard": {"pos": "MID", "pis": 9.3, "npxg90": 0.32, "xa90": 0.42, "is_gk": False, "is_starter": True},
        "William Saliba": {"pos": "DEF", "pis": 9.2, "npxg90": 0.05, "xa90": 0.02, "is_gk": False, "is_starter": True},
        "Gabriel Magalhaes": {"pos": "DEF", "pis": 8.9, "npxg90": 0.12, "xa90": 0.02, "is_gk": False, "is_starter": True},
        "Kai Havertz": {"pos": "FWD", "pis": 8.6, "npxg90": 0.44, "xa90": 0.20, "is_gk": False, "is_starter": True},
        "Declan Rice": {"pos": "MID", "pis": 9.1, "npxg90": 0.18, "xa90": 0.24, "is_gk": False, "is_starter": True},
        "David Raya": {"pos": "GK", "pis": 8.8, "npxg90": 0.00, "xa90": 0.01, "is_gk": True, "is_starter": True},
        "Jurrien Timber": {"pos": "DEF", "pis": 8.2, "npxg90": 0.08, "xa90": 0.12, "is_gk": False, "is_starter": True},
        "Gabriel Martinelli": {"pos": "FWD", "pis": 8.4, "npxg90": 0.35, "xa90": 0.25, "is_gk": False, "is_starter": True},
        "Thomas Partey": {"pos": "MID", "pis": 8.0, "npxg90": 0.08, "xa90": 0.10, "is_gk": False, "is_starter": True},
        "Ben White": {"pos": "DEF", "pis": 8.3, "npxg90": 0.06, "xa90": 0.18, "is_gk": False, "is_starter": True}
    },
    "Liverpool": {
        "Mohamed Salah": {"pos": "FWD", "pis": 9.7, "npxg90": 0.65, "xa90": 0.42, "is_gk": False, "is_starter": True},
        "Virgil van Dijk": {"pos": "DEF", "pis": 9.4, "npxg90": 0.10, "xa90": 0.04, "is_gk": False, "is_starter": True},
        "Alisson": {"pos": "GK", "pis": 9.1, "npxg90": 0.00, "xa90": 0.01, "is_gk": True, "is_starter": True},
        "Trent Alexander-Arnold": {"pos": "DEF", "pis": 9.2, "npxg90": 0.12, "xa90": 0.45, "is_gk": False, "is_starter": True},
        "Alexis Mac Allister": {"pos": "MID", "pis": 8.7, "npxg90": 0.18, "xa90": 0.22, "is_gk": False, "is_starter": True},
        "Ryan Gravenberch": {"pos": "MID", "pis": 8.5, "npxg90": 0.10, "xa90": 0.18, "is_gk": False, "is_starter": True},
        "Luis Diaz": {"pos": "FWD", "pis": 8.8, "npxg90": 0.45, "xa90": 0.22, "is_gk": False, "is_starter": True},
        "Ibrahima Konate": {"pos": "DEF", "pis": 8.5, "npxg90": 0.06, "xa90": 0.02, "is_gk": False, "is_starter": True},
        "Dominik Szoboszlai": {"pos": "MID", "pis": 8.4, "npxg90": 0.22, "xa90": 0.25, "is_gk": False, "is_starter": True},
        "Andrew Robertson": {"pos": "DEF", "pis": 8.3, "npxg90": 0.05, "xa90": 0.20, "is_gk": False, "is_starter": True},
        "Darwin Nunez": {"pos": "FWD", "pis": 8.2, "npxg90": 0.55, "xa90": 0.18, "is_gk": False, "is_starter": True}
    },
    "Real Madrid": {
        "Kylian Mbappe": {"pos": "FWD", "pis": 9.8, "npxg90": 0.75, "xa90": 0.28, "is_gk": False, "is_starter": True},
        "Vinicius Junior": {"pos": "FWD", "pis": 9.7, "npxg90": 0.60, "xa90": 0.45, "is_gk": False, "is_starter": True},
        "Jude Bellingham": {"pos": "MID", "pis": 9.5, "npxg90": 0.45, "xa90": 0.35, "is_gk": False, "is_starter": True},
        "Federico Valverde": {"pos": "MID", "pis": 9.0, "npxg90": 0.20, "xa90": 0.25, "is_gk": False, "is_starter": True},
        "Antonio Rudiger": {"pos": "DEF", "pis": 8.9, "npxg90": 0.08, "xa90": 0.02, "is_gk": False, "is_starter": True},
        "Thibaut Courtois": {"pos": "GK", "pis": 9.2, "npxg90": 0.00, "xa90": 0.00, "is_gk": True, "is_starter": True},
        "Eduardo Camavinga": {"pos": "MID", "pis": 8.5, "npxg90": 0.08, "xa90": 0.15, "is_gk": False, "is_starter": True},
        "Aurelien Tchouameni": {"pos": "MID", "pis": 8.6, "npxg90": 0.08, "xa90": 0.12, "is_gk": False, "is_starter": True},
        "Rodrygo": {"pos": "FWD", "pis": 8.7, "npxg90": 0.40, "xa90": 0.30, "is_gk": False, "is_starter": True},
        "Ferland Mendy": {"pos": "DEF", "pis": 8.1, "npxg90": 0.03, "xa90": 0.08, "is_gk": False, "is_starter": True},
        "Dani Carvajal": {"pos": "DEF", "pis": 8.5, "npxg90": 0.08, "xa90": 0.20, "is_gk": False, "is_starter": True}
    },
    "Bayern Munich": {
        "Harry Kane": {"pos": "FWD", "pis": 9.8, "npxg90": 0.82, "xa90": 0.35, "is_gk": False, "is_starter": True},
        "Jamal Musiala": {"pos": "MID", "pis": 9.4, "npxg90": 0.45, "xa90": 0.38, "is_gk": False, "is_starter": True},
        "Michael Olise": {"pos": "FWD", "pis": 8.9, "npxg90": 0.35, "xa90": 0.40, "is_gk": False, "is_starter": True},
        "Joshua Kimmich": {"pos": "MID", "pis": 9.1, "npxg90": 0.12, "xa90": 0.38, "is_gk": False, "is_starter": True},
        "Dayot Upamecano": {"pos": "DEF", "pis": 8.5, "npxg90": 0.05, "xa90": 0.03, "is_gk": False, "is_starter": True},
        "Manuel Neuer": {"pos": "GK", "pis": 8.7, "npxg90": 0.00, "xa90": 0.01, "is_gk": True, "is_starter": True},
        "Alphonso Davies": {"pos": "DEF", "pis": 8.6, "npxg90": 0.10, "xa90": 0.25, "is_gk": False, "is_starter": True},
        "Kim Min-jae": {"pos": "DEF", "pis": 8.4, "npxg90": 0.04, "xa90": 0.02, "is_gk": False, "is_starter": True},
        "Serge Gnabry": {"pos": "FWD", "pis": 8.3, "npxg90": 0.38, "xa90": 0.22, "is_gk": False, "is_starter": True},
        "Aleksandar Pavlovic": {"pos": "MID", "pis": 8.1, "npxg90": 0.08, "xa90": 0.15, "is_gk": False, "is_starter": True},
        "Konrad Laimer": {"pos": "MID", "pis": 8.0, "npxg90": 0.08, "xa90": 0.12, "is_gk": False, "is_starter": True}
    }
}

def evaluate_lineup_strength(team_name: str, missing_players: List[str] = [], rest_days: float = 7.0, matches_14d: int = 2) -> Dict[str, float]:
    """Evaluates Starting XI strength delta against optimal XI.
    
    Returns:
      - active_xi_strength_ratio: [0.65, 1.0]
      - attack_threat_retention: [0.50, 1.0]
      - primary_gk_missing: 0.0 or 1.0
      - squad_fatigue_load: load factor
    """
    roster = SQUAD_DATABASE.get(team_name, {})
    if not roster:
        # Default baseline club
        n_missing = len(missing_players)
        att_loss = min(0.35, n_missing * 0.08)
        def_loss = min(0.30, n_missing * 0.06)
        fatigue = matches_14d * 0.15 * max(0.5, (14.0 - rest_days) / 7.0)
        return {
            "active_xi_strength_ratio": float(1.0 - (att_loss + def_loss) / 2.0),
            "attack_threat_retention": float(1.0 - att_loss),
            "primary_gk_missing": 0.0,
            "squad_fatigue_load": float(np.clip(fatigue, 0.0, 1.5))
        }

    optimal_pis = sum(p["pis"] for p in roster.values())
    optimal_threat = sum(p["npxg90"] + p["xa90"] for p in roster.values())

    active_pis = 0.0
    active_threat = 0.0
    gk_missing = 0.0

    for name, data in roster.items():
        is_missing = any(m.lower() in name.lower() for m in missing_players)
        if is_missing:
            if data["is_gk"]:
                gk_missing = 1.0
        else:
            active_pis += data["pis"]
            active_threat += (data["npxg90"] + data["xa90"])

    # Bench replacement points (replacement level player ~ 7.0 PIS)
    n_missing = len([m for m in missing_players if any(m.lower() in n.lower() for n in roster)])
    replacement_pis = n_missing * 7.0
    total_active_pis = min(optimal_pis, active_pis + replacement_pis)

    strength_ratio = total_active_pis / (optimal_pis + 1e-5)
    threat_retention = active_threat / (optimal_threat + 1e-5)
    fatigue = matches_14d * 0.12 * max(0.5, (14.0 - rest_days) / 7.0)

    return {
        "active_xi_strength_ratio": float(np.clip(strength_ratio, 0.65, 1.0)),
        "attack_threat_retention": float(np.clip(threat_retention, 0.50, 1.0)),
        "primary_gk_missing": float(gk_missing),
        "squad_fatigue_load": float(np.clip(fatigue, 0.0, 1.5))
    }
