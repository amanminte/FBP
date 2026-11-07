"""
Dixon-Coles & Poisson Goal Expectancy Engine.
Zero Data Leakage: strictly pre-match estimation of attack, defense, expected goals (Lambda_H, Lambda_A),
scoreline probability matrices, Over/Under 2.5, and BTTS.
"""
import numpy as np
import pandas as pd
from scipy.stats import poisson
from typing import Dict, Tuple

class DixonColesEngine:
    def __init__(self, time_decay_xi: float = 0.003, rho: float = -0.11, max_goals: int = 7):
        self.time_decay_xi = time_decay_xi
        self.rho = rho
        self.max_goals = max_goals
        # Track team rolling stats: (scored, conceded, matches)
        self.team_stats: Dict[str, Dict[str, float]] = {}
        self.league_avg_goals = 1.35
        self.home_adv_factor = 1.20

    def get_attack_defense(self, team: str) -> Tuple[float, float]:
        if team not in self.team_stats:
            return 1.0, 1.0
        st = self.team_stats[team]
        n = max(1.0, st["n"])
        # Smoothed with prior
        prior_weight = 5.0
        avg_scored = (st["scored"] + prior_weight * self.league_avg_goals) / (n + prior_weight)
        avg_conceded = (st["conceded"] + prior_weight * self.league_avg_goals) / (n + prior_weight)

        attack = max(0.5, avg_scored / self.league_avg_goals)
        defense = max(0.5, avg_conceded / self.league_avg_goals)
        return attack, defense

    def calculate_lambdas(self, home_team: str, away_team: str) -> Tuple[float, float]:
        att_h, def_h = self.get_attack_defense(home_team)
        att_a, def_a = self.get_attack_defense(away_team)

        lambda_h = self.league_avg_goals * att_h * def_a * self.home_adv_factor
        lambda_a = (self.league_avg_goals / self.home_adv_factor) * att_a * def_h

        # Bound to realistic ranges
        lambda_h = max(0.25, min(4.5, lambda_h))
        lambda_a = max(0.20, min(4.0, lambda_a))
        return lambda_h, lambda_a

    def scoreline_matrix(self, lambda_h: float, lambda_a: float) -> np.ndarray:
        goals = np.arange(self.max_goals + 1)
        p_h = poisson.pmf(goals, lambda_h)
        p_a = poisson.pmf(goals, lambda_a)
        matrix = np.outer(p_h, p_a)

        # Dixon-Coles tau adjustment for low scores
        # tau(0,0) = 1 - lambda_h * lambda_a * rho
        # tau(0,1) = 1 + lambda_h * rho
        # tau(1,0) = 1 + lambda_a * rho
        # tau(1,1) = 1 - rho
        matrix[0, 0] = max(0.0, matrix[0, 0] * (1.0 - lambda_h * lambda_a * self.rho))
        matrix[0, 1] = max(0.0, matrix[0, 1] * (1.0 + lambda_h * self.rho))
        matrix[1, 0] = max(0.0, matrix[1, 0] * (1.0 + lambda_a * self.rho))
        matrix[1, 1] = max(0.0, matrix[1, 1] * (1.0 - self.rho))

        # Re-normalize
        total = matrix.sum()
        if total > 0:
            matrix = matrix / total
        return matrix

    def extract_probabilities(self, matrix: np.ndarray) -> Dict[str, float]:
        prob_h = float(np.sum(np.tril(matrix, -1)))
        prob_d = float(np.sum(np.diag(matrix)))
        prob_a = float(np.sum(np.triu(matrix, 1)))

        # Over / Under 2.5
        under25 = 0.0
        for i in range(min(3, matrix.shape[0])):
            for j in range(min(3, matrix.shape[1])):
                if i + j <= 2:
                    under25 += matrix[i, j]
        prob_over25 = float(max(0.0, min(1.0, 1.0 - under25)))

        # BTTS (Both Teams To Score)
        prob_btts = float(np.sum(matrix[1:, 1:]))

        # Most likely score
        idx = np.unravel_index(np.argmax(matrix, axis=None), matrix.shape)
        most_likely_score = f"{idx[0]}-{idx[1]}"
        most_likely_prob = float(matrix[idx])

        return {
            "DC_Prob_H": prob_h,
            "DC_Prob_D": prob_d,
            "DC_Prob_A": prob_a,
            "DC_Prob_Over25": prob_over25,
            "DC_Prob_BTTS": prob_btts,
            "Most_Likely_Score": most_likely_score,
            "Most_Likely_Score_Prob": most_likely_prob
        }

    def update(self, home_team: str, away_team: str, fthg: int, ftag: int):
        for team, scored, conceded in [(home_team, fthg, ftag), (away_team, ftag, fthg)]:
            if team not in self.team_stats:
                self.team_stats[team] = {"scored": 0.0, "conceded": 0.0, "n": 0.0}
            st = self.team_stats[team]
            decay = np.exp(-self.time_decay_xi * 7.0) # decay ~1 match week
            st["scored"] = st["scored"] * decay + scored
            st["conceded"] = st["conceded"] * decay + conceded
            st["n"] = st["n"] * decay + 1.0

def compute_dixon_coles_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes Dixon-Coles goal expectancy strictly prior to match kickoff."""
    df = df.sort_values(["Date", "League", "HomeTeam"]).reset_index(drop=True)

    dc = DixonColesEngine()

    lambda_h_list = []
    lambda_a_list = []
    total_lambda_list = []
    dc_p_h = []
    dc_p_d = []
    dc_p_a = []
    dc_p_over = []
    dc_p_btts = []
    most_likely_score = []
    most_likely_prob = []

    for idx, row in df.iterrows():
        ht = row["HomeTeam"]
        at = row["AwayTeam"]

        # Pre-match lambdas
        lh, la = dc.calculate_lambdas(ht, at)
        mat = dc.scoreline_matrix(lh, la)
        probs = dc.extract_probabilities(mat)

        lambda_h_list.append(lh)
        lambda_a_list.append(la)
        total_lambda_list.append(lh + la)
        dc_p_h.append(probs["DC_Prob_H"])
        dc_p_d.append(probs["DC_Prob_D"])
        dc_p_a.append(probs["DC_Prob_A"])
        dc_p_over.append(probs["DC_Prob_Over25"])
        dc_p_btts.append(probs["DC_Prob_BTTS"])
        most_likely_score.append(probs["Most_Likely_Score"])
        most_likely_prob.append(probs["Most_Likely_Score_Prob"])

        # Post-match update
        if pd.notnull(row.get("FTHG")) and pd.notnull(row.get("FTAG")):
            dc.update(ht, at, int(row["FTHG"]), int(row["FTAG"]))

    df["DC_Lambda_H"] = lambda_h_list
    df["DC_Lambda_A"] = lambda_a_list
    df["DC_Total_Lambda"] = total_lambda_list
    df["DC_Prob_H"] = dc_p_h
    df["DC_Prob_D"] = dc_p_d
    df["DC_Prob_A"] = dc_p_a
    df["DC_Prob_Over25"] = dc_p_over
    df["DC_Prob_BTTS"] = dc_p_btts
    df["Most_Likely_Score"] = most_likely_score
    df["Most_Likely_Score_Prob"] = most_likely_prob

    return df
