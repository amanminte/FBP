"""
Dynamic Elo & Pi-Ratings Feature Engineering Engine.
Zero Data Leakage: Ratings are strictly computed prior to match kickoff and updated post-match.
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple

class EloEngine:
    def __init__(self, initial_rating: float = 1500.0, promoted_rating: float = 1350.0,
                 k_factor: float = 20.0, home_advantage: float = 65.0):
        self.initial_rating = initial_rating
        self.promoted_rating = promoted_rating
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.ratings: Dict[str, float] = {}

    def get_rating(self, team: str) -> float:
        if team not in self.ratings:
            self.ratings[team] = self.promoted_rating if len(self.ratings) > 20 else self.initial_rating
        return self.ratings[team]

    def expected_scores(self, r_home: float, r_away: float) -> Tuple[float, float, float]:
        """Calculates expected probabilities for Home Win, Draw, and Away Win."""
        diff = (r_home + self.home_advantage) - r_away
        prob_home = 1.0 / (1.0 + 10.0 ** (-diff / 400.0))
        # Draw probability estimated via normal distribution on rating difference
        # Peaks near 0.28 for evenly matched teams
        prob_draw = max(0.18, 0.28 * np.exp(-((diff / 350.0) ** 2)))
        # Rescale so H + D + A = 1
        rem = 1.0 - prob_draw
        p_h = rem * prob_home
        p_a = rem * (1.0 - prob_home)
        return p_h, prob_draw, p_a

    def update(self, home_team: str, away_team: str, fthg: int, ftag: int):
        r_h = self.get_rating(home_team)
        r_a = self.get_rating(away_team)

        # Pre-match expectation
        diff = (r_h + self.home_advantage) - r_a
        e_h = 1.0 / (1.0 + 10.0 ** (-diff / 400.0))
        e_a = 1.0 - e_h

        # Actual score
        if fthg > ftag:
            s_h, s_a = 1.0, 0.0
        elif fthg == ftag:
            s_h, s_a = 0.5, 0.5
        else:
            s_h, s_a = 0.0, 1.0

        # Margin multiplier
        goal_diff = abs(fthg - ftag)
        margin_mult = np.log(goal_diff + 1.0) * (1.75 / (2.0 + 0.001 * abs(diff)))
        margin_mult = max(1.0, margin_mult)

        # Update
        delta_h = self.k_factor * margin_mult * (s_h - e_h)
        delta_a = self.k_factor * margin_mult * (s_a - e_a)

        self.ratings[home_team] = r_h + delta_h
        self.ratings[away_team] = r_a + delta_a

class PiRatingsEngine:
    def __init__(self, lambda_factor: float = 0.06, gamma_factor: float = 0.7):
        self.lambda_factor = lambda_factor
        self.gamma_factor = gamma_factor
        # Each team has (home_rating, away_rating)
        self.ratings: Dict[str, Tuple[float, float]] = {}

    def get_ratings(self, team: str) -> Tuple[float, float]:
        if team not in self.ratings:
            self.ratings[team] = (0.0, 0.0)
        return self.ratings[team]

    def update(self, home_team: str, away_team: str, fthg: int, ftag: int):
        h_h, h_a = self.get_ratings(home_team)
        a_h, a_a = self.get_ratings(away_team)

        expected_gd = h_h - a_a
        actual_gd = fthg - ftag
        err = actual_gd - expected_gd

        # Damped update
        def psi(e):
            return 3.0 * np.log10(1.0 + abs(e)) if e >= 0 else -3.0 * np.log10(1.0 + abs(e))

        delta = psi(err) * self.lambda_factor
        new_h_h = h_h + delta
        new_h_a = h_a + delta * self.gamma_factor
        new_a_a = a_a - delta
        new_a_h = a_h - delta * self.gamma_factor

        self.ratings[home_team] = (new_h_h, new_h_a)
        self.ratings[away_team] = (new_a_h, new_a_a)

def compute_ratings_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes dynamic Elo & Pi-ratings in strict chronological order."""
    df = df.sort_values(["Date", "League", "HomeTeam"]).reset_index(drop=True)

    elo = EloEngine()
    pi = PiRatingsEngine()

    home_elo = []
    away_elo = []
    elo_diff = []
    elo_p_h = []
    elo_p_d = []
    elo_p_a = []

    home_pi = []
    away_pi = []
    pi_diff = []

    for idx, row in df.iterrows():
        ht = row["HomeTeam"]
        at = row["AwayTeam"]

        # Pre-match Elo
        rh = elo.get_rating(ht)
        ra = elo.get_rating(at)
        ph, pd_, pa = elo.expected_scores(rh, ra)

        home_elo.append(rh)
        away_away = ra
        away_elo.append(away_away)
        elo_diff.append(rh - ra)
        elo_p_h.append(ph)
        elo_p_d.append(pd_)
        elo_p_a.append(pa)

        # Pre-match Pi
        h_h, _ = pi.get_ratings(ht)
        _, a_a = pi.get_ratings(at)
        home_pi.append(h_h)
        away_pi.append(a_a)
        pi_diff.append(h_h - a_a)

        # Post-match update (using actual result after recording pre-match features)
        if pd.notnull(row.get("FTHG")) and pd.notnull(row.get("FTAG")):
            elo.update(ht, at, int(row["FTHG"]), int(row["FTAG"]))
            pi.update(ht, at, int(row["FTHG"]), int(row["FTAG"]))

    df["Home_Elo"] = home_elo
    df["Away_Elo"] = away_elo
    df["Elo_Diff"] = elo_diff
    df["Elo_Prob_H"] = elo_p_h
    df["Elo_Prob_D"] = elo_p_d
    df["Elo_Prob_A"] = elo_p_a

    df["Home_Pi"] = home_pi
    df["Away_Pi"] = away_pi
    df["Pi_Diff"] = pi_diff

    return df
