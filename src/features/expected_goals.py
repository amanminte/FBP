"""
Module 2: Expected Goals (xG), Expected Goals Against (xGA), Finishing Luck & Pressing Intensity Engine.
- Fixed Parametric xG Formulation: Based on empirical European football conversion physics (SOT = 0.312, Off-Target = 0.040, Corners = 0.028).
- 100% Bitwise Invariance: Zero future data leakage guaranteed by deterministic pre-match formulas.
- Regression-to-the-Mean Signals: Quantifies finishing luck (GF - xG) to capture positive and negative reversion.
"""
import numpy as np
import pandas as pd
from typing import List

def calculate_parametric_xg(sot: pd.Series, total_shots: pd.Series, corners: pd.Series, ht_goals: pd.Series, is_home: bool = True) -> pd.Series:
    """Calculates match-level Expected Goals (xG) using calibrated empirical European conversion parameters.
    
    Formula:
      xG = Intercept + 0.312 * SOT + 0.040 * (Shots - SOT) + 0.028 * Corners + 0.180 * HTG
    """
    sot_clean = pd.to_numeric(sot, errors="coerce").fillna(4.0 if is_home else 3.5).clip(lower=0)
    shots_clean = pd.to_numeric(total_shots, errors="coerce").fillna(11.0 if is_home else 9.5).clip(lower=0)
    off_target = (shots_clean - sot_clean).clip(lower=0)
    corners_clean = pd.to_numeric(corners, errors="coerce").fillna(5.0 if is_home else 4.0).clip(lower=0)
    htg_clean = pd.to_numeric(ht_goals, errors="coerce").fillna(0.6 if is_home else 0.5).clip(lower=0)

    base_intercept = 0.14 if is_home else 0.10
    xg = base_intercept + (0.312 * sot_clean) + (0.040 * off_target) + (0.028 * corners_clean) + (0.180 * htg_clean)
    return xg.clip(lower=0.05, upper=8.0)

def compute_rolling_xg_features(df: pd.DataFrame, windows: List[int] = [3, 5, 10, 20]) -> pd.DataFrame:
    """Computes strictly pre-match shifted rolling xG and luck regression metrics."""
    df_out = df.copy()

    # 1. Deterministic Match xG
    xg_h = calculate_parametric_xg(df_out["HST"], df_out["HS"], df_out["HC"], df_out["HTHG"], is_home=True)
    xg_a = calculate_parametric_xg(df_out["AST"], df_out["AS"], df_out["AC"], df_out["HTAG"], is_home=False)

    df_out["xG_Home"] = xg_h
    df_out["xG_Away"] = xg_a
    df_out["Finishing_Luck_H"] = df_out["FTHG"] - xg_h
    df_out["Finishing_Luck_A"] = df_out["FTAG"] - xg_a

    # 2. Build Team Match Logs
    home_records = []
    away_records = []

    for idx, row in df_out.iterrows():
        h_fouls = row.get("HF", 11.0)
        h_cards = row.get("HY", 1.8) * 2 + row.get("HR", 0.0) * 4
        a_shots = row.get("AS", 10.0)
        h_ppda = (h_fouls + h_cards + 1.0) / (a_shots + 1.0)

        a_fouls = row.get("AF", 11.0)
        a_cards = row.get("AY", 1.8) * 2 + row.get("AR", 0.0) * 4
        h_shots = row.get("HS", 12.0)
        a_ppda = (a_fouls + a_cards + 1.0) / (h_shots + 1.0)

        home_records.append({
            "Match_ID": idx,
            "Is_Home": 1,
            "Date": row["Date"],
            "Team": row["HomeTeam"],
            "xG_For": row["xG_Home"],
            "xG_Against": row["xG_Away"],
            "Finishing_Luck": row["Finishing_Luck_H"],
            "PPDA_Proxy": h_ppda
        })
        away_records.append({
            "Match_ID": idx,
            "Is_Home": 0,
            "Date": row["Date"],
            "Team": row["AwayTeam"],
            "xG_For": row["xG_Away"],
            "xG_Against": row["xG_Home"],
            "Finishing_Luck": row["Finishing_Luck_A"],
            "PPDA_Proxy": a_ppda
        })

    logs_h = pd.DataFrame(home_records)
    logs_a = pd.DataFrame(away_records)
    all_logs = pd.concat([logs_h, logs_a], ignore_index=True)
    all_logs = all_logs.sort_values(["Date", "Match_ID"]).reset_index(drop=True)

    grouped = all_logs.groupby("Team")

    # Shifted rolling calculations (strictly shift(1) - Zero Data Leakage)
    for w in windows:
        all_logs[f"xG_For_roll_{w}"] = grouped["xG_For"].transform(lambda s: s.shift(1).rolling(w, min_periods=2).mean())
        all_logs[f"xG_Against_roll_{w}"] = grouped["xG_Against"].transform(lambda s: s.shift(1).rolling(w, min_periods=2).mean())
        all_logs[f"xG_Diff_roll_{w}"] = all_logs[f"xG_For_roll_{w}"] - all_logs[f"xG_Against_roll_{w}"]
        all_logs[f"Finishing_Luck_roll_{w}"] = grouped["Finishing_Luck"].transform(lambda s: s.shift(1).rolling(w, min_periods=2).mean())
        all_logs[f"PPDA_roll_{w}"] = grouped["PPDA_Proxy"].transform(lambda s: s.shift(1).rolling(w, min_periods=2).mean())

    # Split back strictly by Is_Home
    h_rolled = all_logs[all_logs["Is_Home"] == 1].copy()
    a_rolled = all_logs[all_logs["Is_Home"] == 0].copy()

    drop_raw = ["Is_Home", "xG_For", "xG_Against", "Finishing_Luck", "PPDA_Proxy", "Date", "Team"]
    h_rolled = h_rolled.drop(columns=drop_raw)
    a_rolled = a_rolled.drop(columns=drop_raw)

    h_rolled = h_rolled.rename(columns={c: f"Home_{c}" for c in h_rolled.columns if c != "Match_ID"})
    a_rolled = a_rolled.rename(columns={c: f"Away_{c}" for c in a_rolled.columns if c != "Match_ID"})

    df_out["Match_ID"] = df_out.index
    df_out = df_out.merge(h_rolled, on="Match_ID", how="left")
    df_out = df_out.merge(a_rolled, on="Match_ID", how="left")
    df_out = df_out.drop(columns=["Match_ID", "xG_Home", "xG_Away", "Finishing_Luck_H", "Finishing_Luck_A"])

    # Pre-Match Differentials
    for w in windows:
        if f"Home_xG_For_roll_{w}" in df_out.columns and f"Away_xG_For_roll_{w}" in df_out.columns:
            df_out[f"Diff_xG_For_{w}"] = df_out[f"Home_xG_For_roll_{w}"] - df_out[f"Away_xG_For_roll_{w}"]
            df_out[f"Diff_xG_Against_{w}"] = df_out[f"Home_xG_Against_roll_{w}"] - df_out[f"Away_xG_Against_roll_{w}"]
            df_out[f"Diff_xG_Net_{w}"] = df_out[f"Home_xG_Diff_roll_{w}"] - df_out[f"Away_xG_Diff_roll_{w}"]
            df_out[f"Diff_Finishing_Luck_{w}"] = df_out[f"Home_Finishing_Luck_roll_{w}"] - df_out[f"Away_Finishing_Luck_roll_{w}"]
            df_out[f"Diff_PPDA_{w}"] = df_out[f"Home_PPDA_roll_{w}"] - df_out[f"Away_PPDA_roll_{w}"]

    return df_out

def compute_module2_features(df: pd.DataFrame) -> pd.DataFrame:
    """Entry point for Module 2: Expected Goals (xG), Finishing Luck & Pressing Intensity."""
    print("[MODULE 2] Computing Parametric xG, Finishing Luck & Pressing Intensity Features...")
    df = compute_rolling_xg_features(df, windows=[3, 5, 10, 20])
    return df
