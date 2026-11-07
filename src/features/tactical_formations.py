"""
Tactical Formations, Archetypes & Style Interaction Engine.
Models tactical dimensions: Width Bias, Line Height / Pressing, Transition Speed,
and computes tactical mismatch interaction terms strictly shifted by 1 (.shift(1)).
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

# Formation Archetype Mappings for live inference / classification
FORMATION_ARCHETYPES = {
    "4-3-3": {"width_bias": 0.65, "line_height": 0.70, "transition_speed": 0.45},
    "4-2-3-1": {"width_bias": 0.35, "line_height": 0.50, "transition_speed": 0.40},
    "3-5-2": {"width_bias": 0.75, "line_height": 0.30, "transition_speed": 0.75},
    "3-4-2-1": {"width_bias": 0.60, "line_height": 0.55, "transition_speed": 0.60},
    "4-4-2": {"width_bias": 0.40, "line_height": -0.20, "transition_speed": 0.80},
    "5-3-2": {"width_bias": 0.20, "line_height": -0.70, "transition_speed": 0.85},
    "4-1-4-1": {"width_bias": 0.30, "line_height": 0.40, "transition_speed": 0.30}
}

def get_formation_vector(formation_str: str) -> Dict[str, float]:
    """Returns tactical dimensions for a given formation string."""
    clean = formation_str.strip()
    return FORMATION_ARCHETYPES.get(clean, {"width_bias": 0.40, "line_height": 0.30, "transition_speed": 0.50})

def compute_tactical_features(df: pd.DataFrame, windows: List[int] = [5, 15]) -> pd.DataFrame:
    """Computes strictly pre-match rolling tactical style features for each club.
    
    Metrics:
      - Directness_Index: (Shots + Corners) / (Fouls + 1)
      - Shot_Accuracy_Discipline: SOT / (Total_Shots + 1)
      - Defensive_Block_Compactness: Opponent_SOT / (Opponent_Total_Shots + 1)
      - Second_Half_Adaptability: GD_2H - GD_1H
      - Game_State_Resilience: Comeback recovery from HT deficit
    """
    df_sorted = df.sort_values(["Date", "HomeTeam"]).reset_index(drop=True)

    # Build chronological match logs for tactical metrics
    records = []
    for idx, row in df_sorted.iterrows():
        # Home
        fthg = row.get("FTHG", 0.0)
        ftag = row.get("FTAG", 0.0)
        hthg = row.get("HTHG", 0.0)
        htag = row.get("HTAG", 0.0)
        hs = row.get("HS", 11.0)
        hst = row.get("HST", 4.0)
        as_shots = row.get("AS", 10.0)
        ast = row.get("AST", 3.5)
        hc = row.get("HC", 5.0)
        ac = row.get("AC", 4.0)
        hf = row.get("HF", 11.0)
        af = row.get("AF", 11.0)

        gd_1h_h = hthg - htag
        gd_2h_h = (fthg - hthg) - (ftag - htag)
        ht_deficit_h = 1.0 if gd_1h_h < 0 else 0.0
        recovered_pts_h = (3.0 if fthg > ftag else (1.0 if fthg == ftag else 0.0)) if ht_deficit_h == 1.0 else 0.0

        records.append({
            "Match_ID": idx,
            "Date": row["Date"],
            "Team": row["HomeTeam"],
            "Is_Home": 1,
            "Shots": hs,
            "SOT": hst,
            "Corners": hc,
            "Fouls": hf,
            "Opp_Shots": as_shots,
            "Opp_SOT": ast,
            "Opp_Corners": ac,
            "Opp_Fouls": af,
            "GD_2H_Diff": gd_2h_h - gd_1h_h,
            "HT_Deficit": ht_deficit_h,
            "Recovered_Pts": recovered_pts_h
        })

        # Away
        gd_1h_a = htag - hthg
        gd_2h_a = (ftag - htag) - (fthg - hthg)
        ht_deficit_a = 1.0 if gd_1h_a < 0 else 0.0
        recovered_pts_a = (3.0 if ftag > fthg else (1.0 if ftag == fthg else 0.0)) if ht_deficit_a == 1.0 else 0.0

        records.append({
            "Match_ID": idx,
            "Date": row["Date"],
            "Team": row["AwayTeam"],
            "Is_Home": 0,
            "Shots": as_shots,
            "SOT": ast,
            "Corners": ac,
            "Fouls": af,
            "Opp_Shots": hs,
            "Opp_SOT": hst,
            "Opp_Corners": hc,
            "Opp_Fouls": hf,
            "GD_2H_Diff": gd_2h_a - gd_1h_a,
            "HT_Deficit": ht_deficit_a,
            "Recovered_Pts": recovered_pts_a
        })

    logs = pd.DataFrame(records)
    logs = logs.sort_values(["Team", "Date", "Match_ID"]).reset_index(drop=True)

    grouped = logs.groupby("Team")

    # Shifted rolling tactical styles
    for w in windows:
        # Directness = (Shots + Corners) / (Fouls + 1)
        shots_roll = grouped["Shots"].apply(lambda g: g.shift(1).rolling(w, min_periods=1).mean()).reset_index(level=0, drop=True)
        corners_roll = grouped["Corners"].apply(lambda g: g.shift(1).rolling(w, min_periods=1).mean()).reset_index(level=0, drop=True)
        fouls_roll = grouped["Fouls"].apply(lambda g: g.shift(1).rolling(w, min_periods=1).mean()).reset_index(level=0, drop=True)
        logs[f"Directness_roll_{w}"] = ((shots_roll + corners_roll) / (fouls_roll + 1.0)).fillna(1.2)

        # Shot Accuracy Discipline = SOT / (Shots + 1)
        sot_roll = grouped["SOT"].apply(lambda g: g.shift(1).rolling(w, min_periods=1).mean()).reset_index(level=0, drop=True)
        logs[f"Shot_Accuracy_roll_{w}"] = (sot_roll / (shots_roll + 1.0)).clip(0.1, 0.9).fillna(0.35)

        # Defensive Compactness = Opp_SOT / (Opp_Shots + 1)
        opp_sot_roll = grouped["Opp_SOT"].apply(lambda g: g.shift(1).rolling(w, min_periods=1).mean()).reset_index(level=0, drop=True)
        opp_shots_roll = grouped["Opp_Shots"].apply(lambda g: g.shift(1).rolling(w, min_periods=1).mean()).reset_index(level=0, drop=True)
        logs[f"Def_Compactness_roll_{w}"] = (opp_sot_roll / (opp_shots_roll + 1.0)).clip(0.1, 0.9).fillna(0.35)

        # 2nd Half Tactical Adaptability
        logs[f"Adaptability_2H_roll_{w}"] = grouped["GD_2H_Diff"].apply(lambda g: g.shift(1).rolling(w, min_periods=1).mean()).reset_index(level=0, drop=True).fillna(0.0)

        # Game State Resilience
        rec_pts_roll = grouped["Recovered_Pts"].apply(lambda g: g.shift(1).rolling(w, min_periods=1).sum()).reset_index(level=0, drop=True)
        deficit_roll = grouped["HT_Deficit"].apply(lambda g: g.shift(1).rolling(w, min_periods=1).sum()).reset_index(level=0, drop=True)
        logs[f"Resilience_roll_{w}"] = (rec_pts_roll / (deficit_roll + 1e-4)).clip(0.0, 3.0).fillna(0.5)

    # Separate Home and Away
    home_tac = logs[logs["Is_Home"] == 1].copy()
    away_tac = logs[logs["Is_Home"] == 0].copy()

    tac_cols_to_keep = ["Match_ID"] + [c for c in home_tac.columns if "roll_" in c]
    home_tac = home_tac[tac_cols_to_keep].rename(columns={c: f"Home_Tac_{c}" for c in tac_cols_to_keep if c != "Match_ID"})
    away_tac = away_tac[tac_cols_to_keep].rename(columns={c: f"Away_Tac_{c}" for c in tac_cols_to_keep if c != "Match_ID"})

    df_out = df_sorted.copy()
    df_out["Match_ID"] = df_out.index
    df_out = df_out.merge(home_tac, on="Match_ID", how="left")
    df_out = df_out.merge(away_tac, on="Match_ID", how="left")
    df_out = df_out.drop(columns=["Match_ID"])

    # Tactical Mismatch Features (5-game and 15-game)
    for w in windows:
        # Counter Attack Vulnerability: High directness away vs low defensive compactness home
        h_comp = df_out[f"Home_Tac_Def_Compactness_roll_{w}"]
        a_dir = df_out[f"Away_Tac_Directness_roll_{w}"]
        df_out[f"Counter_Vulnerability_H_roll_{w}"] = (h_comp * a_dir).fillna(0.5)

        # Tactical Adaptability Differential
        h_ad = df_out[f"Home_Tac_Adaptability_2H_roll_{w}"]
        a_ad = df_out[f"Away_Tac_Adaptability_2H_roll_{w}"]
        df_out[f"Diff_Adaptability_2H_roll_{w}"] = h_ad - a_ad

        # Shot Discipline Differential
        h_disc = df_out[f"Home_Tac_Shot_Accuracy_roll_{w}"]
        a_disc = df_out[f"Away_Tac_Shot_Accuracy_roll_{w}"]
        df_out[f"Diff_Shot_Discipline_roll_{w}"] = h_disc - a_disc

    return df_out
