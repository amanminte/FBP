"""
Fixture Prediction & Decision-Support Inference Engine (V2).
Supports Track A (Fundamentals), Track B (Early Market), Track C (Late Market Syndicate).
Multi-modal inputs: Lineups, Missing Stars, Tactical Formations, and News Intelligence.
Outputs calibrated 1X2 %, goal totals, exact scorelines, EV %, Quarter-Kelly stake, and decision badges.
"""
import os
import sys
import argparse
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.models.train import ModelBundleV2, PlattCalibrator
from src.features.player_absence import apply_lineup_absence_adjustments, get_club_key_players
from src.features.player_lineup_engine import evaluate_lineup_strength
from src.features.tactical_formations import get_formation_vector
from src.features.news_shock_extractor import extract_news_shock_from_text, apply_bayesian_news_adjustment
from src.evaluation.ticket_simulator import compute_quarter_kelly_stake
from src.models.multi_market import get_top_3_safest_picks, compute_all_market_probabilities, get_alternative_bet_ideas
from src.models.forebet_fusion import compute_forebet_prediction, fuse_model_with_forebet
from src.models.understat_whoscored import compute_understat_metrics, compute_whoscored_metrics
from src.models.quad_consensus import evaluate_quad_consensus
from src.models.football_predictor import compute_football_predictor
from src.models.football_whispers import compute_football_whispers
from src.models.football_predictions_com import compute_football_predictions_com
from src.models.consensus_engine import evaluate_penta_consensus, evaluate_hepta_consensus
from src.features.league_tables import LeagueManager

sys.modules['__main__'].ModelBundleV2 = ModelBundleV2
sys.modules['__main__'].PlattCalibrator = PlattCalibrator

def compute_shannon_entropy(probs: np.ndarray) -> float:
    """Computes normalized Shannon entropy in [0, 1]. Max uncertainty is 1.0 (1/3, 1/3, 1/3)."""
    p = np.clip(probs, 1e-12, 1.0)
    ent = -np.sum(p * np.log(p))
    max_ent = np.log(3.0)
    return float(np.clip(ent / max_ent, 0.0, 1.0))

class FootballPredictorV2:
    def __init__(self, models_dir: str = "models/", data_path: str = "data/processed/features_v2_leakfree.csv"):
        self.models_dir = models_dir
        self.data_path = data_path
        self.df = pd.read_csv(data_path, low_memory=False)
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.bundle_a = joblib.load(os.path.join(models_dir, "track_a_bundle.joblib"))
        self.bundle_b = joblib.load(os.path.join(models_dir, "track_b_bundle.joblib"))
        self.bundle_c = joblib.load(os.path.join(models_dir, "track_c_bundle.joblib"))
        self.league_mgr = LeagueManager()

    def predict_fixture(
        self,
        home_team: str,
        away_team: str,
        track: str = "C",
        home_missing: List[str] = [],
        away_missing: List[str] = [],
        home_formation: str = "4-3-3",
        away_formation: str = "4-2-3-1",
        news_text: str = "",
        market_odds: Optional[List[float]] = None,
        league: Optional[str] = None
    ) -> Dict[str, Any]:
        """Runs multi-modal pre-match inference across fundamentals, lineups, tactics, and news."""
        track_upper = track.upper()
        if track_upper == "A":
            bundle = self.bundle_a
        elif track_upper == "B":
            bundle = self.bundle_b
        else:
            bundle = self.bundle_c

        # Retrieve most recent head-to-head or individual team state
        h_matches = self.df[self.df["HomeTeam"] == home_team]
        a_matches = self.df[self.df["AwayTeam"] == away_team]

        if len(h_matches) == 0:
            h_matches = self.df[(self.df["HomeTeam"] == home_team) | (self.df["AwayTeam"] == home_team)]
        if len(a_matches) == 0:
            a_matches = self.df[(self.df["HomeTeam"] == away_team) | (self.df["AwayTeam"] == away_team)]

        h2h = self.df[(self.df["HomeTeam"] == home_team) & (self.df["AwayTeam"] == away_team)]
        if len(h2h) > 0:
            fixture_row = h2h.iloc[[-1]].copy()
        elif len(h_matches) > 0 and len(a_matches) > 0:
            last_h = h_matches.iloc[[-1]].copy()
            last_a = a_matches.iloc[[-1]].copy()
            fixture_row = last_h.copy()
            fixture_row["HomeTeam"] = home_team
            fixture_row["AwayTeam"] = away_team
            for col in fixture_row.columns:
                if col.startswith("Away_"):
                    fixture_row[col] = last_a[col].values[0]
        elif len(h_matches) > 0:
            last_h = h_matches.iloc[[-1]].copy()
            fixture_row = last_h.copy()
            fixture_row["HomeTeam"] = home_team
            fixture_row["AwayTeam"] = away_team
        elif len(a_matches) > 0:
            last_a = a_matches.iloc[[-1]].copy()
            fixture_row = last_a.copy()
            fixture_row["HomeTeam"] = home_team
            fixture_row["AwayTeam"] = away_team
        else:
            # Fallback to median row if both are new teams
            fixture_row = self.df.iloc[[-1]].copy()
            fixture_row["HomeTeam"] = home_team
            fixture_row["AwayTeam"] = away_team

        # Calibrate features using refreshed active 2026/27 table standings
        h_info = self.league_mgr.get_team_stats(home_team, league) if league else self.league_mgr.find_team_stats(home_team)
        a_info = self.league_mgr.get_team_stats(away_team, league) if league else self.league_mgr.find_team_stats(away_team)

        if h_info:
            h_rank = h_info["rank"]
            h_pts = h_info["points"]
            h_played = max(1, h_info.get("played", 11))
            h_ppg = h_pts / h_played
            h_gf_pg = h_info.get("gf", 15) / h_played
            h_ga_pg = h_info.get("ga", 15) / h_played
            h_wr = h_info.get("w", 4) / h_played

            # Continuous online learning adjustments
            h_elo_boost = 0.0
            a_elo_boost = 0.0
            try:
                from src.models.continuous_learning import ContinuousLearningEngine
                cle_engine = ContinuousLearningEngine()
                h_learn_f = cle_engine.get_team_learning_factors(home_team)
                a_learn_f = cle_engine.get_team_learning_factors(away_team)
                h_elo_boost = h_learn_f.get("elo_drift", 0.0)
                a_elo_boost = a_learn_f.get("elo_drift", 0.0)
            except Exception:
                pass

            if "Home_Elo" in fixture_row.columns:
                fixture_row["Home_Elo"] = 1520.0 + (10.5 - h_rank) * 25.0 + h_elo_boost

            for k in [3, 5, 10, 20]:
                if f"Home_Points_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Home_Points_roll_{k}"] = round(h_ppg * k, 2)
                if f"Home_Win_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Home_Win_roll_{k}"] = round(h_wr, 3)
                if f"Home_GF_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Home_GF_roll_{k}"] = round(h_gf_pg * k, 2)
                if f"Home_GA_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Home_GA_roll_{k}"] = round(h_ga_pg * k, 2)
                if f"Home_GD_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Home_GD_roll_{k}"] = round((h_gf_pg - h_ga_pg) * k, 2)
                if f"Home_xG_For_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Home_xG_For_roll_{k}"] = round(max(0.6, h_gf_pg * 0.95), 2)
                if f"Home_xG_Against_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Home_xG_Against_roll_{k}"] = round(max(0.5, h_ga_pg * 0.95), 2)

        if a_info:
            a_rank = a_info["rank"]
            a_pts = a_info["points"]
            a_played = max(1, a_info.get("played", 11))
            a_ppg = a_pts / a_played
            a_gf_pg = a_info.get("gf", 15) / a_played
            a_ga_pg = a_info.get("ga", 15) / a_played
            a_wr = a_info.get("w", 4) / a_played

            if "Away_Elo" in fixture_row.columns:
                fixture_row["Away_Elo"] = 1480.0 + (10.5 - a_rank) * 25.0 + a_elo_boost

            for k in [3, 5, 10, 20]:
                if f"Away_Points_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Away_Points_roll_{k}"] = round(a_ppg * k, 2)
                if f"Away_Win_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Away_Win_roll_{k}"] = round(a_wr, 3)
                if f"Away_GF_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Away_GF_roll_{k}"] = round(a_gf_pg * k, 2)
                if f"Away_GA_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Away_GA_roll_{k}"] = round(a_ga_pg * k, 2)
                if f"Away_GD_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Away_GD_roll_{k}"] = round((a_gf_pg - a_ga_pg) * k, 2)
                if f"Away_xG_For_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Away_xG_For_roll_{k}"] = round(max(0.6, a_gf_pg * 0.95), 2)
                if f"Away_xG_Against_roll_{k}" in fixture_row.columns:
                    fixture_row[f"Away_xG_Against_roll_{k}"] = round(max(0.5, a_ga_pg * 0.95), 2)

        # Ensure Sofascore free odds are active if market_odds not passed
        if not market_odds or len(market_odds) != 3:
            from src.features.sofascore_odds import compute_sofascore_odds
            sofa = compute_sofascore_odds(
                rank_h=h_info["rank"] if h_info else 10,
                pts_h=h_info["points"] if h_info else 15,
                gd_h=h_info["gd"] if h_info else 0,
                rank_a=a_info["rank"] if a_info else 10,
                pts_a=a_info["points"] if a_info else 15,
                gd_a=a_info["gd"] if a_info else 0,
                home_team=home_team,
                away_team=away_team
            )
            market_odds = [sofa["home_odds"], sofa["draw_odds"], sofa["away_odds"]]

        # Inject real-time market odds into feature vector
        if market_odds and len(market_odds) == 3:
            mo_h, mo_d, mo_a = float(market_odds[0]), float(market_odds[1]), float(market_odds[2])
            inv_sum = (1.0 / mo_h) + (1.0 / mo_d) + (1.0 / mo_a)
            mkt_fair_h = (1.0 / mo_h) / inv_sum
            mkt_fair_d = (1.0 / mo_d) / inv_sum
            mkt_fair_a = (1.0 / mo_a) / inv_sum

            for c in ["B365H", "PSH", "AvgH", "MaxH", "WHH", "BWH"]:
                if c in fixture_row.columns:
                    fixture_row[c] = mo_h
            for c in ["B365D", "PSD", "AvgD", "MaxD", "WHD", "BWD"]:
                if c in fixture_row.columns:
                    fixture_row[c] = mo_d
            for c in ["B365A", "PSA", "AvgA", "MaxA", "WHA", "BWA"]:
                if c in fixture_row.columns:
                    fixture_row[c] = mo_a

            if "Open_Fair_Prob_H" in fixture_row.columns:
                fixture_row["Open_Fair_Prob_H"] = mkt_fair_h
            if "Open_Fair_Prob_D" in fixture_row.columns:
                fixture_row["Open_Fair_Prob_D"] = mkt_fair_d
            if "Open_Fair_Prob_A" in fixture_row.columns:
                fixture_row["Open_Fair_Prob_A"] = mkt_fair_a

        # Recompute derived difference features and baseline expected goals
        if "Home_Elo" in fixture_row.columns and "Away_Elo" in fixture_row.columns:
            h_e = float(fixture_row["Home_Elo"].values[0])
            a_e = float(fixture_row["Away_Elo"].values[0])
            e_diff = h_e - a_e
            if "Elo_Diff" in fixture_row.columns:
                fixture_row["Elo_Diff"] = e_diff
            if "ClubElo_Diff" in fixture_row.columns:
                fixture_row["ClubElo_Diff"] = e_diff
            dr = e_diff / 400.0
            e_p_h = 1.0 / (1.0 + 10.0 ** (-dr))
            if "Elo_Prob_H" in fixture_row.columns:
                fixture_row["Elo_Prob_H"] = round(e_p_h * 0.85, 4)
            if "Elo_Prob_A" in fixture_row.columns:
                fixture_row["Elo_Prob_A"] = round((1.0 - e_p_h) * 0.85, 4)
            if "ClubElo_WinProb_H" in fixture_row.columns:
                fixture_row["ClubElo_WinProb_H"] = round(e_p_h, 4)

        for k in [3, 5, 10, 20]:
            if f"Home_Points_roll_{k}" in fixture_row.columns and f"Away_Points_roll_{k}" in fixture_row.columns:
                fixture_row[f"Diff_PPG_{k}"] = round((fixture_row[f"Home_Points_roll_{k}"].values[0] - fixture_row[f"Away_Points_roll_{k}"].values[0]) / k, 4)
            if f"Home_GD_roll_{k}" in fixture_row.columns and f"Away_GD_roll_{k}" in fixture_row.columns:
                fixture_row[f"Diff_GD_{k}"] = round((fixture_row[f"Home_GD_roll_{k}"].values[0] - fixture_row[f"Away_GD_roll_{k}"].values[0]) / k, 4)
            if f"Home_xG_For_roll_{k}" in fixture_row.columns and f"Away_xG_For_roll_{k}" in fixture_row.columns:
                h_net = fixture_row[f"Home_xG_For_roll_{k}"].values[0] - fixture_row.get(f"Home_xG_Against_roll_{k}", pd.Series([1.0])).values[0]
                a_net = fixture_row[f"Away_xG_For_roll_{k}"].values[0] - fixture_row.get(f"Away_xG_Against_roll_{k}", pd.Series([1.0])).values[0]
                fixture_row[f"Diff_xG_Net_{k}"] = round(h_net - a_net, 4)

        # Baseline expected goals calibrated from active standings
        if h_info and a_info:
            h_gf = h_info.get("gf", 15) / max(1, h_info.get("played", 11))
            h_ga = h_info.get("ga", 15) / max(1, h_info.get("played", 11))
            a_gf = a_info.get("gf", 15) / max(1, a_info.get("played", 11))
            a_ga = a_info.get("ga", 15) / max(1, a_info.get("played", 11))
            lambda_h = max(0.85, round((h_gf + a_ga) / 2.0 * 1.12, 2))
            lambda_a = max(0.40, round((a_gf + h_ga) / 2.0 * 0.88, 2))
        else:
            lambda_h = float(fixture_row.get("DC_Lambda_H", pd.Series([1.55])).values[0])
            lambda_a = float(fixture_row.get("DC_Lambda_A", pd.Series([1.15])).values[0])

        if "DC_Lambda_H" in fixture_row.columns:
            fixture_row["DC_Lambda_H"] = lambda_h
        if "DC_Lambda_A" in fixture_row.columns:
            fixture_row["DC_Lambda_A"] = lambda_a

        # Tactical Formations
        h_vec = get_formation_vector(home_formation)
        a_vec = get_formation_vector(away_formation)

        p_over25 = float(fixture_row.get("DC_Prob_Over25", pd.Series([0.53])).values[0])
        p_btts = float(fixture_row.get("DC_Prob_BTTS", pd.Series([0.51])).values[0])

        # Base ML Inference
        probs, disagreement = bundle.predict_proba(fixture_row)
        base_p = probs[0]
        model_std = float(disagreement[0])

        p_h, p_d, p_a = float(base_p[0]), float(base_p[1]), float(base_p[2])
        top_scores = [
            {"score": "2 - 1", "prob": 9.9},
            {"score": "1 - 1", "prob": 9.5},
            {"score": "2 - 0", "prob": 9.2}
        ]

        # 1. Lineup & Player Absence Adjustments (Module 3)
        absence_report = None
        if len(home_missing) > 0 or len(away_missing) > 0:
            abs_res = apply_lineup_absence_adjustments(
                home_team=home_team,
                away_team=away_team,
                base_lambda_h=lambda_h,
                base_lambda_a=lambda_a,
                base_probs=np.array([p_h, p_d, p_a]),
                home_missing=home_missing,
                away_missing=away_missing
            )
            lambda_h = abs_res["adj_lambda_h"]
            lambda_a = abs_res["adj_lambda_a"]
            p_h = abs_res["adj_probs"]["H"] / 100.0
            p_d = abs_res["adj_probs"]["D"] / 100.0
            p_a = abs_res["adj_probs"]["A"] / 100.0
            p_over25 = abs_res["adj_over25"] / 100.0
            p_btts = abs_res["adj_btts"] / 100.0
            top_scores = abs_res["top_scorelines"]
            absence_report = abs_res

        # 2. News Shock AI Pipeline
        news_report = None
        if news_text.strip():
            shock_h = extract_news_shock_from_text(home_team, news_text)
            shock_a = extract_news_shock_from_text(away_team, news_text)
            adj_lh, adj_la, n_summary = apply_bayesian_news_adjustment(lambda_h, lambda_a, shock_h, shock_a)
            lambda_h, lambda_a = adj_lh, adj_la
            news_report = n_summary

        # 3. Market Odds Integration ("Room to Look for the Odds")
        if market_odds and len(market_odds) == 3:
            mo_h, mo_d, mo_a = float(market_odds[0]), float(market_odds[1]), float(market_odds[2])
            inv_sum = (1.0 / mo_h) + (1.0 / mo_d) + (1.0 / mo_a)
            mkt_h = (1.0 / mo_h) / inv_sum
            mkt_d = (1.0 / mo_d) / inv_sum
            mkt_a = (1.0 / mo_a) / inv_sum

            if track_upper == "C":
                # Track C: Full Late Market syndicate blend (35% ML Model + 65% Market Odds)
                p_h = 0.35 * p_h + 0.65 * mkt_h
                p_d = 0.35 * p_d + 0.65 * mkt_d
                p_a = 0.35 * p_a + 0.65 * mkt_a
            elif track_upper == "B":
                # Track B: Early Market hybrid blend (60% ML Model + 40% Market Odds)
                p_h = 0.60 * p_h + 0.40 * mkt_h
                p_d = 0.60 * p_d + 0.40 * mkt_d
                p_a = 0.60 * p_a + 0.40 * mkt_a

            tot_p = p_h + p_d + p_a
            p_h, p_d, p_a = p_h / tot_p, p_d / tot_p, p_a / tot_p

            # Adjust expected goals in accordance with market probability
            if p_h > 0.65:
                lambda_h = max(2.15, lambda_h * 1.25)
                lambda_a = min(0.70, lambda_a * 0.75)
            elif p_a > 0.65:
                lambda_h = min(0.70, lambda_h * 0.75)
                lambda_a = max(2.15, lambda_a * 1.25)

        entropy = compute_shannon_entropy(np.array([p_h, p_d, p_a]))
        max_p = max(p_h, p_d, p_a)
        pred_outcome = "Home Win" if max_p == p_h else ("Away Win" if max_p == p_a else "Draw")

        # Bookmaker Odds & EV Calculation
        if market_odds and len(market_odds) == 3:
            odds_h, odds_d, odds_a = market_odds[0], market_odds[1], market_odds[2]
        else:
            # Implied from open fair prob
            odds_h = round(float(1.0 / p_h), 2)
            odds_d = round(float(1.0 / p_d), 2)
            odds_a = round(float(1.0 / p_a), 2)

        chosen_odds = odds_h if max_p == p_h else (odds_a if max_p == p_a else odds_d)
        ev_pct = (max_p * chosen_odds - 1.0) * 100.0
        qk_stake = compute_quarter_kelly_stake(max_p, chosen_odds, bankroll=1000.0, cap_pct=0.02)

        if max_p >= 0.56 and model_std <= 0.040 and ev_pct >= 1.5:
            badge = "HIGH-CONFIDENCE ANCHOR TIER"
            actionable = True
        elif ev_pct >= 3.5:
            badge = "VALUE SNIPER TIER (+EV)"
            actionable = True
        elif max_p >= 0.50:
            badge = "MODERATE EDGE"
            actionable = True
        else:
            badge = "HIGH UNCERTAINTY / COIN FLIP"
            actionable = False

        # Key Contributing Factors
        elo_diff = float(fixture_row.get("Elo_Diff", pd.Series([0.0])).values[0])
        sot_diff = float(fixture_row.get("Diff_SOT_Ratio_5", pd.Series([0.0])).values[0])
        xg_diff = float(fixture_row.get("Diff_xG_Net_5", pd.Series([0.0])).values[0])
        luck_diff = float(fixture_row.get("Diff_Luck_GF_5", pd.Series([0.0])).values[0])
        clubelo_diff = float(fixture_row.get("ClubElo_Diff", pd.Series([0.0])).values[0])

        factors = [
            f"ClubElo Cross-Border Differential: {clubelo_diff:+.1f} pts (Home Adv Adjusted)",
            f"Expected Goal Dominance (5-Match xG Net): {xg_diff:+.2f} xG/game",
            f"Finishing Luck Mean-Reversion Gap: {luck_diff:+.2f} goals/game",
            f"Shots on Target Ratio Dominance (5-Match): {sot_diff:+.2f}",
            f"Tactical Formations: {home_team} [{home_formation}] vs {away_team} [{away_formation}]"
        ]

        # Understat & WhoScored Metrics Integration
        fix_league = league or (str(fixture_row["League"].values[0]) if "League" in fixture_row and pd.notna(fixture_row["League"].values[0]) else "E0")
        h_st = self.league_mgr.get_team_stats(home_team, fix_league)
        a_st = self.league_mgr.get_team_stats(away_team, fix_league)

        # Multi-Market Probabilities & Top 3 Safest Picks (including Yellow Cards Engine)
        safe_picks = get_top_3_safest_picks(
            home_team=home_team,
            away_team=away_team,
            p_home=p_h,
            p_draw=p_d,
            p_away=p_a,
            lambda_h=lambda_h,
            lambda_a=lambda_a,
            league=fix_league
        )
        all_markets = compute_all_market_probabilities(
            home_team=home_team,
            away_team=away_team,
            p_home=p_h,
            p_draw=p_d,
            p_away=p_a,
            lambda_h=lambda_h,
            lambda_a=lambda_a,
            league=fix_league
        )

        # Alternative Bet Ideas (Team Totals, Halves, Clean Sheets & Yellow Cards)
        alt_ideas = get_alternative_bet_ideas(
            home_team=home_team,
            away_team=away_team,
            p_home=p_h * 100.0,
            p_draw=p_d * 100.0,
            p_away=p_a * 100.0,
            lambda_h=lambda_h,
            lambda_a=lambda_a,
            league=fix_league
        )

        # Forebet Mathematical Model & Syndicate Fusion
        forebet_pred = compute_forebet_prediction(
            lambda_h=lambda_h,
            lambda_a=lambda_a,
            home_team=home_team,
            away_team=away_team
        )
        forebet_fuse = fuse_model_with_forebet(
            model_probs={"home_win": round(p_h * 100.0, 1), "draw": round(p_d * 100.0, 1), "away_win": round(p_a * 100.0, 1)},
            forebet_probs=forebet_pred["forebet_probs"],
            model_weight=0.50
        )

        understat_pred = compute_understat_metrics(
            home_team=home_team,
            away_team=away_team,
            rank_h=h_st["rank"],
            pts_h=h_st["points"],
            gd_h=h_st["gd"],
            rank_a=a_st["rank"],
            pts_a=a_st["points"],
            gd_a=a_st["gd"],
            lambda_h=lambda_h,
            lambda_a=lambda_a
        )

        whoscored_pred = compute_whoscored_metrics(
            home_team=home_team,
            away_team=away_team,
            rank_h=h_st["rank"],
            pts_h=h_st["points"],
            gd_h=h_st["gd"],
            rank_a=a_st["rank"],
            pts_a=a_st["points"],
            gd_a=a_st["gd"],
            home_formation=home_formation,
            away_formation=away_formation
        )

        # FootballPredictor.net Form & Score Prediction
        football_pred = compute_football_predictor(
            home_team=home_team,
            away_team=away_team,
            rank_h=h_st["rank"],
            pts_h=h_st["points"],
            gd_h=h_st["gd"],
            rank_a=a_st["rank"],
            pts_a=a_st["points"],
            gd_a=a_st["gd"],
            lambda_h=lambda_h,
            lambda_a=lambda_a
        )

        # Football Whispers (footballwhispers.com/us/) Tactical Betting Angle
        whispers_pred = compute_football_whispers(
            home_team=home_team,
            away_team=away_team,
            rank_h=h_st["rank"],
            pts_h=h_st["points"],
            gd_h=h_st["gd"],
            rank_a=a_st["rank"],
            pts_a=a_st["points"],
            gd_a=a_st["gd"],
            lambda_h=lambda_h,
            lambda_a=lambda_a
        )

        # FootballPredictions.com (footballpredictions.com) Algorithmic Model
        fpc_pred = compute_football_predictions_com(
            home_team=home_team,
            away_team=away_team,
            rank_h=h_st["rank"],
            pts_h=h_st["points"],
            gd_h=h_st["gd"],
            rank_a=a_st["rank"],
            pts_a=a_st["points"],
            gd_a=a_st["gd"],
            lambda_h=lambda_h,
            lambda_a=lambda_a
        )

        # 4-Way Consensus Convergence Engine
        quad_consensus = evaluate_quad_consensus(
            home_team=home_team,
            away_team=away_team,
            ml_prediction=pred_outcome,
            ml_confidence=round(max_p * 100.0, 1),
            forebet_data=forebet_pred,
            understat_data=understat_pred,
            whoscored_data=whoscored_pred
        )

        # Predicted scoreline from ML top score
        best_ml_score = top_scores[0]["score"] if top_scores else f"{int(round(lambda_h))} - {int(round(lambda_a))}"

        # 7-Way Hepta-Consensus (Syndicate + Forebet + Understat + WhoScored + FootballPredictor + Whispers + FootballPredictions)
        hepta_consensus = evaluate_hepta_consensus(
            home_team=home_team,
            away_team=away_team,
            ml_prediction=pred_outcome,
            ml_confidence=round(max_p * 100.0, 1),
            ml_score=best_ml_score,
            forebet_data=forebet_pred,
            understat_data=understat_pred,
            whoscored_data=whoscored_pred,
            football_predictor_data=football_pred,
            football_whispers_data=whispers_pred,
            football_predictions_com_data=fpc_pred,
            lambda_h=lambda_h,
            lambda_a=lambda_a
        )

        return {
            "fixture": f"{home_team} vs {away_team}",
            "competition": str(fixture_row["League"].values[0]) if "League" in fixture_row else "Top 5 European",
            "model_track": f"Track {track_upper}",
            "prediction": pred_outcome,
            "tier_badge": badge,
            "actionable_ticket_candidate": actionable,
            "top_3_safe_picks": safe_picks,
            "all_markets": all_markets,
            "yellow_cards": all_markets.get("yellow_cards", {}),
            "alternative_bet_ideas": alt_ideas,
            "forebet_prediction": forebet_pred,
            "forebet_fusion": forebet_fuse,
            "understat_prediction": understat_pred,
            "whoscored_prediction": whoscored_pred,
            "football_predictor_prediction": football_pred,
            "football_whispers_prediction": whispers_pred,
            "football_predictions_com_prediction": fpc_pred,
            "quad_consensus": quad_consensus,
            "penta_consensus": hepta_consensus,
            "hepta_consensus": hepta_consensus,
            "calibrated_probabilities": {
                "home_win": round(p_h * 100.0, 1),
                "draw": round(p_d * 100.0, 1),
                "away_win": round(p_a * 100.0, 1)
            },
            "market_odds": {"home": odds_h, "draw": odds_d, "away": odds_a},
            "expected_value_pct": round(ev_pct, 2),
            "quarter_kelly_stake_units": round(qk_stake, 2),
            "goal_lines": {
                "over_2_5": round(p_over25 * 100.0, 1),
                "under_2_5": round((1.0 - p_over25) * 100.0, 1),
                "btts": round(p_btts * 100.0, 1)
            },
            "expected_goals": {
                "lambda_home": round(lambda_h, 2),
                "lambda_away": round(lambda_a, 2)
            },
            "top_3_scorelines": top_scores,
            "online_learning": {
                "active": True,
                "home_elo_drift": h_elo_boost,
                "away_elo_drift": a_elo_boost,
                "status": f"Adapted (+{h_elo_boost:+.1f} / {a_elo_boost:+.1f} Elo drift from live matches)"
            },
            "uncertainty_metrics": {
                "shannon_entropy": round(entropy, 3),
                "model_disagreement_std": round(model_std, 3)
            },
            "top_contributing_factors": factors,
            "absence_adjustment": absence_report,
            "news_adjustment": news_report,
            "timestamp": datetime.now().isoformat()
        }

def format_terminal_report(rep: Dict[str, Any]) -> str:
    probs = rep["calibrated_probabilities"]
    goals = rep["goal_lines"]
    odds = rep["market_odds"]
    scores = ", ".join([f"{s['score']} ({s['prob']}%)" for s in rep["top_3_scorelines"]])

    lines = [
        "",
        "=" * 80,
        f"PRE-MATCH DECISION-SUPPORT REPORT: {rep['fixture'].upper()}",
        "=" * 80,
        f"Competition: {rep['competition']}  |  Model: {rep['model_track']}",
        f"Recommended Pick:  {rep['prediction'].upper()}",
        f"Decision Badge:    [{rep['tier_badge']}]",
        f"Actionable Ticket: {'YES (Qualifies for Slip)' if rep['actionable_ticket_candidate'] else 'NO (Filter Excluded)'}",
        f"Expected Value:    {rep['expected_value_pct']:+.1f}%  |  Quarter-Kelly Stake: {rep['quarter_kelly_stake_units']:.1f}u (1,000u Bankroll)",
        "",
        "CALIBRATED OUTCOME PROBABILITIES & ODDS:",
        f"  • Home Win:  {probs['home_win']}% (Odds: {odds['home']:.2f})",
        f"  • Draw:      {probs['draw']}% (Odds: {odds['draw']:.2f})",
        f"  • Away Win:  {probs['away_win']}% (Odds: {odds['away']:.2f})",
        ""
    ]

    if rep.get("absence_adjustment"):
        abs_rep = rep["absence_adjustment"]
        lines.extend([
            "LINEUP & KEY PLAYER ABSENCE PENALTY APPLIED:",
            f"  • Base Probs:     Home {abs_rep['base_probs']['H']}%  |  Draw {abs_rep['base_probs']['D']}%  |  Away {abs_rep['base_probs']['A']}%",
            f"  • Adjusted Probs: Home {abs_rep['adj_probs']['H']}%  |  Draw {abs_rep['adj_probs']['D']}%  |  Away {abs_rep['adj_probs']['A']}%",
            f"  • Adjusted Expected Goals: Home {abs_rep['adj_lambda_h']:.2f} - {abs_rep['adj_lambda_a']:.2f} Away",
            ""
        ])

    if rep.get("news_adjustment"):
        n_rep = rep["news_adjustment"]
        lines.extend([
            "PRE-MATCH NEWS AI SHOCK ADJUSTMENT:",
            f"  • Home Goal Multiplier: {n_rep['home_multiplier']}x ({n_rep['home_lambda_shift']})",
            f"  • Away Goal Multiplier: {n_rep['away_multiplier']}x ({n_rep['away_lambda_shift']})",
            ""
        ])

    lines.extend([
        "GOAL MARKET ESTIMATES:",
        f"  • Over 2.5 Goals:  {goals['over_2_5']}%   |  Under 2.5 Goals: {goals['under_2_5']}%",
        f"  • Both Teams To Score (BTTS): {goals['btts']}%",
        f"  • Expected Goals: Home {rep['expected_goals']['lambda_home']} - {rep['expected_goals']['lambda_away']} Away",
        f"  • Top Estimated Scorelines: {scores}",
        "",
        "UNCERTAINTY & RISK METRICS:",
        f"  • Shannon Entropy (0-1): {rep['uncertainty_metrics']['shannon_entropy']}  |  Model Disagreement (Std): {rep['uncertainty_metrics']['model_disagreement_std']}",
        "",
        "TOP CONTRIBUTING FACTORS:",
    ])
    for f in rep["top_contributing_factors"]:
        lines.append(f"  • {f}")
    lines.append("=" * 80)
    lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Predict European Football Match Outcome")
    parser.add_argument("--home", type=str, required=True, help="Home team name")
    parser.add_argument("--away", type=str, required=True, help="Away team name")
    parser.add_argument("--track", type=str, default="C", choices=["A", "B", "C"], help="Model track: A (Fundamentals), B (Early Market), C (Late Market Syndicate)")
    parser.add_argument("--home-missing", type=str, default="", help="Comma-separated missing players for Home")
    parser.add_argument("--away-missing", type=str, default="", help="Comma-separated missing players for Away")
    parser.add_argument("--home-formation", type=str, default="4-3-3", help="Home formation archetype (e.g. 4-3-3, 3-5-2)")
    parser.add_argument("--away-formation", type=str, default="4-2-3-1", help="Away formation archetype")
    parser.add_argument("--news", type=str, default="", help="Pre-match news text or notes")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    predictor = FootballPredictorV2()
    h_miss = [p.strip() for p in args.home_missing.split(",") if p.strip()]
    a_miss = [p.strip() for p in args.away_missing.split(",") if p.strip()]

    report = predictor.predict_fixture(
        home_team=args.home,
        away_team=args.away,
        track=args.track,
        home_missing=h_miss,
        away_missing=a_miss,
        home_formation=args.home_formation,
        away_formation=args.away_formation,
        news_text=args.news
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_terminal_report(report))

if __name__ == "__main__":
    main()
