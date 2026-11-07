"""
Module 3: Lineup & Key Player Absence Penalty Architecture (The "Replacement Problem").
Models individual player values (Goal Share, Assist Share, Defensive Value) across European clubs.
Applies Bayesian lambda adjustments to Dixon-Coles and machine learning probabilities when key players are missing.
"""
from typing import Dict, List, Tuple, Any
import numpy as np

from src.features.squad_database import get_club_squad, get_squad_player_names, EXPANDED_SQUAD_DATABASE

# Database of key players across Top 5 European Leagues
# Fields: position, goal_share, assist_share, defense_impact
KEY_PLAYERS_DB: Dict[str, Dict[str, Dict[str, Any]]] = {
    "Manchester City": {
        "Erling Haaland": {"pos": "FW", "goal_share": 0.35, "assist_share": 0.08, "def_impact": 0.00},
        "Rodri": {"pos": "DM", "goal_share": 0.08, "assist_share": 0.14, "def_impact": 0.28},
        "Kevin De Bruyne": {"pos": "AM", "goal_share": 0.12, "assist_share": 0.32, "def_impact": 0.02},
        "Ruben Dias": {"pos": "CB", "goal_share": 0.02, "assist_share": 0.02, "def_impact": 0.18},
        "Phil Foden": {"pos": "AM/W", "goal_share": 0.22, "assist_share": 0.18, "def_impact": 0.03}
    },
    "Arsenal": {
        "Bukayo Saka": {"pos": "W", "goal_share": 0.24, "assist_share": 0.28, "def_impact": 0.05},
        "Martin Odegaard": {"pos": "AM", "goal_share": 0.16, "assist_share": 0.26, "def_impact": 0.04},
        "William Saliba": {"pos": "CB", "goal_share": 0.02, "assist_share": 0.02, "def_impact": 0.22},
        "Gabriel Magalhaes": {"pos": "CB", "goal_share": 0.05, "assist_share": 0.02, "def_impact": 0.18},
        "Kai Havertz": {"pos": "FW", "goal_share": 0.20, "assist_share": 0.12, "def_impact": 0.05}
    },
    "Liverpool": {
        "Mohamed Salah": {"pos": "W/FW", "goal_share": 0.32, "assist_share": 0.28, "def_impact": 0.02},
        "Virgil van Dijk": {"pos": "CB", "goal_share": 0.04, "assist_share": 0.03, "def_impact": 0.24},
        "Alisson": {"pos": "GK", "goal_share": 0.00, "assist_share": 0.01, "def_impact": 0.18},
        "Trent Alexander-Arnold": {"pos": "RB/AM", "goal_share": 0.06, "assist_share": 0.26, "def_impact": 0.08},
        "Alexis Mac Allister": {"pos": "CM", "goal_share": 0.08, "assist_share": 0.14, "def_impact": 0.12}
    },
    "Chelsea": {
        "Cole Palmer": {"pos": "AM/W", "goal_share": 0.34, "assist_share": 0.28, "def_impact": 0.03},
        "Nicolas Jackson": {"pos": "FW", "goal_share": 0.22, "assist_share": 0.10, "def_impact": 0.02},
        "Moises Caicedo": {"pos": "DM", "goal_share": 0.03, "assist_share": 0.06, "def_impact": 0.20},
        "Levi Colwill": {"pos": "CB", "goal_share": 0.02, "assist_share": 0.02, "def_impact": 0.15}
    },
    "Real Madrid": {
        "Kylian Mbappe": {"pos": "FW", "goal_share": 0.32, "assist_share": 0.12, "def_impact": 0.01},
        "Vinicius Junior": {"pos": "W", "goal_share": 0.26, "assist_share": 0.28, "def_impact": 0.02},
        "Jude Bellingham": {"pos": "AM/CM", "goal_share": 0.20, "assist_share": 0.20, "def_impact": 0.12},
        "Antonio Rudiger": {"pos": "CB", "goal_share": 0.03, "assist_share": 0.02, "def_impact": 0.22},
        "Thibaut Courtois": {"pos": "GK", "goal_share": 0.00, "assist_share": 0.00, "def_impact": 0.18}
    },
    "Barcelona": {
        "Robert Lewandowski": {"pos": "FW", "goal_share": 0.34, "assist_share": 0.10, "def_impact": 0.01},
        "Lamine Yamal": {"pos": "W", "goal_share": 0.18, "assist_share": 0.32, "def_impact": 0.03},
        "Raphinha": {"pos": "W/AM", "goal_share": 0.24, "assist_share": 0.24, "def_impact": 0.04},
        "Pedri": {"pos": "CM", "goal_share": 0.08, "assist_share": 0.18, "def_impact": 0.10},
        "Pau Cubarsi": {"pos": "CB", "goal_share": 0.01, "assist_share": 0.02, "def_impact": 0.18}
    },
    "Bayern Munich": {
        "Harry Kane": {"pos": "FW", "goal_share": 0.38, "assist_share": 0.20, "def_impact": 0.02},
        "Jamal Musiala": {"pos": "AM", "goal_share": 0.20, "assist_share": 0.24, "def_impact": 0.04},
        "Michael Olise": {"pos": "W", "goal_share": 0.16, "assist_share": 0.22, "def_impact": 0.03},
        "Joshua Kimmich": {"pos": "CM/DM", "goal_share": 0.05, "assist_share": 0.22, "def_impact": 0.16},
        "Dayot Upamecano": {"pos": "CB", "goal_share": 0.02, "assist_share": 0.01, "def_impact": 0.16}
    },
    "Bayer Leverkusen": {
        "Florian Wirtz": {"pos": "AM", "goal_share": 0.25, "assist_share": 0.32, "def_impact": 0.04},
        "Granit Xhaka": {"pos": "CM/DM", "goal_share": 0.06, "assist_share": 0.12, "def_impact": 0.22},
        "Victor Boniface": {"pos": "FW", "goal_share": 0.28, "assist_share": 0.10, "def_impact": 0.02},
        "Alex Grimaldo": {"pos": "WB", "goal_share": 0.14, "assist_share": 0.24, "def_impact": 0.10},
        "Jonathan Tah": {"pos": "CB", "goal_share": 0.04, "assist_share": 0.02, "def_impact": 0.20}
    },
    "Inter": {
        "Lautaro Martinez": {"pos": "FW", "goal_share": 0.32, "assist_share": 0.12, "def_impact": 0.02},
        "Marcus Thuram": {"pos": "FW", "goal_share": 0.24, "assist_share": 0.18, "def_impact": 0.02},
        "Hakan Calhanoglu": {"pos": "CM/DM", "goal_share": 0.14, "assist_share": 0.18, "def_impact": 0.14},
        "Alessandro Bastoni": {"pos": "CB", "goal_share": 0.03, "assist_share": 0.10, "def_impact": 0.20},
        "Nicolo Barella": {"pos": "CM", "goal_share": 0.08, "assist_share": 0.18, "def_impact": 0.14}
    },
    "Paris SG": {
        "Ousmane Dembele": {"pos": "W", "goal_share": 0.18, "assist_share": 0.30, "def_impact": 0.02},
        "Bradley Barcola": {"pos": "W", "goal_share": 0.26, "assist_share": 0.18, "def_impact": 0.02},
        "Vitinha": {"pos": "CM", "goal_share": 0.10, "assist_share": 0.14, "def_impact": 0.14},
        "Marquinhos": {"pos": "CB", "goal_share": 0.03, "assist_share": 0.01, "def_impact": 0.22},
        "Gianluigi Donnarumma": {"pos": "GK", "goal_share": 0.00, "assist_share": 0.00, "def_impact": 0.16}
    }
}

def get_club_key_players(team_name: str) -> List[str]:
    """Returns list of tracked key players for a given club (active 2024/2025/2026)."""
    return get_squad_player_names(team_name)

def calculate_absence_penalty(team_name: str, missing_players: List[str]) -> Tuple[float, float, List[Dict[str, Any]]]:
    """Calculates attack and defense penalty modifiers for missing players.
    
    Returns:
      (attack_penalty, defense_penalty, breakdown_details)
    """
    squad = get_club_squad(team_name)
    att_pen = 0.0
    def_pen = 0.0
    details = []

    for p in missing_players:
        p_clean = p.strip()
        if " (" in p_clean:
            name_only = p_clean.split(" (")[0].strip()
        else:
            name_only = p_clean

        # Find matching player in roster
        matched = None
        for r_name in squad:
            if name_only.lower() in r_name.lower() or r_name.lower() in name_only.lower():
                matched = r_name
                break

        if matched:
            p_data = squad[matched]
            goal_s = p_data.get("goal_share", 0.15)
            ast_s = p_data.get("assist_share", 0.10)
            def_imp = p_data.get("def_impact", 0.10)
            p_att = (goal_s * 0.65) + (ast_s * 0.35)
            p_def = def_imp
            att_pen += p_att
            def_pen += p_def
            details.append({
                "player": matched,
                "position": p_data.get("pos", "MID/FWD"),
                "goal_share": f"{goal_s*100:.1f}%",
                "assist_share": f"{ast_s*100:.1f}%",
                "attack_penalty": round(p_att, 3),
                "defense_penalty": round(p_def, 3)
            })
        else:
            # Custom / User-entered or generic player absence
            details.append({
                "player": name_only,
                "position": "Unknown / Squad Player",
                "goal_share": "5.0%",
                "assist_share": "5.0%",
                "attack_penalty": 0.04,
                "defense_penalty": 0.04
            })
            att_pen += 0.04
            def_pen += 0.04

    # Cap penalties at realistic maximums (squad depth absorbs up to ~40%)
    att_pen = float(np.clip(att_pen, 0.0, 0.40))
    def_pen = float(np.clip(def_pen, 0.0, 0.35))

    return att_pen, def_pen, details

def compute_dixon_coles_matrix(lambda_h: float, lambda_a: float, rho: float = -0.11, max_goals: int = 8) -> np.ndarray:
    """Computes bivariate Dixon-Coles scoreline matrix with low-scoring correlation."""
    from scipy.stats import poisson
    matrix = np.zeros((max_goals, max_goals))
    for x in range(max_goals):
        for y in range(max_goals):
            p_x = poisson.pmf(x, lambda_h)
            p_y = poisson.pmf(y, lambda_a)
            # Tau factor
            if x == 0 and y == 0:
                tau = 1.0 - lambda_h * lambda_a * rho
            elif x == 0 and y == 1:
                tau = 1.0 + lambda_h * rho
            elif x == 1 and y == 0:
                tau = 1.0 + lambda_a * rho
            elif x == 1 and y == 1:
                tau = 1.0 - rho
            else:
                tau = 1.0
            matrix[x, y] = max(0.0, p_x * p_y * tau)
    total_p = np.sum(matrix)
    if total_p > 0:
        matrix /= total_p
    return matrix

def apply_lineup_absence_adjustments(
    home_team: str,
    away_team: str,
    base_lambda_h: float,
    base_lambda_a: float,
    base_probs: np.ndarray,
    home_missing: List[str] = [],
    away_missing: List[str] = []
) -> Dict[str, Any]:
    """Adjusts expected goals, scoreline matrix, and 1X2 win probabilities based on confirmed absences."""
    h_att_pen, h_def_pen, h_details = calculate_absence_penalty(home_team, home_missing)
    a_att_pen, a_def_pen, a_details = calculate_absence_penalty(away_team, away_missing)

    # Adjusted expected goals
    # Home lambda reduced by home attack loss, increased by away defensive loss
    adj_lambda_h = base_lambda_h * (1.0 - h_att_pen) * (1.0 + a_def_pen)
    adj_lambda_a = base_lambda_a * (1.0 - a_att_pen) * (1.0 + h_def_pen)

    # Base vs Adjusted Dixon-Coles
    base_dc = compute_dixon_coles_matrix(base_lambda_h, base_lambda_a)
    adj_dc = compute_dixon_coles_matrix(adj_lambda_h, adj_lambda_a)

    base_dc_h = float(np.sum(np.tril(base_dc, -1)))
    base_dc_d = float(np.sum(np.diag(base_dc)))
    base_dc_a = float(np.sum(np.triu(base_dc, 1)))

    adj_dc_h = float(np.sum(np.tril(adj_dc, -1)))
    adj_dc_d = float(np.sum(np.diag(adj_dc)))
    adj_dc_a = float(np.sum(np.triu(adj_dc, 1)))

    # Compute delta shift
    delta_h = adj_dc_h - base_dc_h
    delta_d = adj_dc_d - base_dc_d
    delta_a = adj_dc_a - base_dc_a

    # Apply Bayesian shift to ML ensemble probabilities
    adj_probs = np.array([
        max(0.05, base_probs[0] + delta_h),
        max(0.05, base_probs[1] + delta_d),
        max(0.05, base_probs[2] + delta_a)
    ])
    adj_probs /= np.sum(adj_probs)

    # Over/Under and BTTS
    total_goals_grid = np.fromfunction(lambda i, j: i + j, (8, 8))
    adj_over25 = float(np.sum(adj_dc[total_goals_grid >= 3]))
    adj_btts = float(np.sum(adj_dc[1:, 1:]))

    # Top 3 scorelines
    flat_indices = np.argsort(adj_dc.ravel())[::-1][:3]
    top_scorelines = []
    for idx in flat_indices:
        h_g = int(idx // 8)
        a_g = int(idx % 8)
        top_scorelines.append({
            "score": f"{h_g} - {a_g}",
            "prob": round(float(adj_dc[h_g, a_g]) * 100, 1)
        })

    return {
        "home_team": home_team,
        "away_team": away_team,
        "base_lambda_h": round(base_lambda_h, 2),
        "base_lambda_a": round(base_lambda_a, 2),
        "adj_lambda_h": round(adj_lambda_h, 2),
        "adj_lambda_a": round(adj_lambda_a, 2),
        "base_probs": {"H": round(base_probs[0] * 100, 1), "D": round(base_probs[1] * 100, 1), "A": round(base_probs[2] * 100, 1)},
        "adj_probs": {"H": round(adj_probs[0] * 100, 1), "D": round(adj_probs[1] * 100, 1), "A": round(adj_probs[2] * 100, 1)},
        "home_absence_details": h_details,
        "away_absence_details": a_details,
        "adj_over25": round(adj_over25 * 100, 1),
        "adj_btts": round(adj_btts * 100, 1),
        "top_scorelines": top_scorelines
    }
