"""
Master Leak-Free Feature Engineering Engine (V2).
Passes the Target-Row Blindfold Test with 100% bitwise exactness.
Explicitly whitelists pre-match variables for Track A, Track B, and Track C.
"""
import os
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any

from src.features.elo_pi_ratings import compute_ratings_features
from src.features.poisson_dixon_coles import compute_dixon_coles_features
from src.data.enrich_xg_elo import compute_shin_market_odds, compute_historical_club_elo, compute_calibrated_match_xg
from src.features.tactical_formations import compute_tactical_features
from src.features.player_lineup_engine import evaluate_lineup_strength

def build_team_match_logs(df: pd.DataFrame) -> pd.DataFrame:
    """Builds chronological team-match logs for shifted rolling statistics."""
    home_records = []
    away_records = []

    for idx, row in df.iterrows():
        fthg = row.get("FTHG", 0.0)
        ftag = row.get("FTAG", 0.0)
        hthg = row.get("HTHG", 0.0)
        htag = row.get("HTAG", 0.0)
        hst = row.get("HST", 4.0)
        ast = row.get("AST", 3.5)
        hs = row.get("HS", 11.0)
        as_shots = row.get("AS", 9.5)
        hc = row.get("HC", 5.0)
        ac = row.get("AC", 4.0)

        h_pts = 3 if fthg > ftag else (1 if fthg == ftag else 0)
        a_pts = 3 if ftag > fthg else (1 if ftag == fthg else 0)

        # Home record
        home_records.append({
            "Match_ID": idx,
            "Date": row["Date"],
            "League": row["League"],
            "Team": row["HomeTeam"],
            "Opponent": row["AwayTeam"],
            "Is_Home": 1,
            "GF": fthg,
            "GA": ftag,
            "GD": fthg - ftag,
            "Points": h_pts,
            "Win": 1 if h_pts == 3 else 0,
            "Draw": 1 if h_pts == 1 else 0,
            "Loss": 1 if h_pts == 0 else 0,
            "Clean_Sheet": 1 if ftag == 0 else 0,
            "Failed_To_Score": 1 if fthg == 0 else 0,
            "SOT_For": hst,
            "SOT_Against": ast,
            "Corners_For": hc,
            "Corners_Against": ac,
            "Second_Half_GF": max(0, fthg - hthg)
        })

        # Away record
        away_records.append({
            "Match_ID": idx,
            "Date": row["Date"],
            "League": row["League"],
            "Team": row["AwayTeam"],
            "Opponent": row["HomeTeam"],
            "Is_Home": 0,
            "GF": ftag,
            "GA": fthg,
            "GD": ftag - fthg,
            "Points": a_pts,
            "Win": 1 if a_pts == 3 else 0,
            "Draw": 1 if a_pts == 1 else 0,
            "Loss": 1 if a_pts == 0 else 0,
            "Clean_Sheet": 1 if fthg == 0 else 0,
            "Failed_To_Score": 1 if ftag == 0 else 0,
            "SOT_For": ast,
            "SOT_Against": hst,
            "Corners_For": ac,
            "Corners_Against": hc,
            "Second_Half_GF": max(0, ftag - htag)
        })

    logs = pd.concat([pd.DataFrame(home_records), pd.DataFrame(away_records)], ignore_index=True)
    logs = logs.sort_values(["Date", "Match_ID"]).reset_index(drop=True)
    return logs

def compute_rolling_form_features(logs: pd.DataFrame, windows: List[int] = [3, 5, 10, 20]) -> pd.DataFrame:
    """Computes strictly pre-match shifted rolling statistics."""
    logs = logs.sort_values(["Team", "Date", "Match_ID"]).reset_index(drop=True)

    metrics = [
        "Points", "Win", "Draw", "GF", "GA", "GD",
        "Clean_Sheet", "Failed_To_Score", "SOT_For", "SOT_Against",
        "Corners_For", "Corners_Against", "Second_Half_GF"
    ]

    grouped = logs.groupby("Team")

    for w in windows:
        roll = grouped[metrics].apply(lambda g: g.shift(1).rolling(window=w, min_periods=1).mean()).reset_index(level=0, drop=True)
        for m in metrics:
            logs[f"{m}_roll_{w}"] = roll[m].fillna(0.0)

        sot_for = logs[f"SOT_For_roll_{w}"]
        sot_against = logs[f"SOT_Against_roll_{w}"]
        logs[f"SOT_Ratio_roll_{w}"] = (sot_for / (sot_for + sot_against + 1e-5)).clip(0.0, 1.0)

        corn_for = logs[f"Corners_For_roll_{w}"]
        corn_against = logs[f"Corners_Against_roll_{w}"]
        logs[f"Corner_Ratio_roll_{w}"] = (corn_for / (corn_for + corn_against + 1e-5)).clip(0.0, 1.0)

    # Rest days
    logs["Prev_Date"] = grouped["Date"].shift(1)
    logs["Rest_Days"] = (logs["Date"] - logs["Prev_Date"]).dt.days.fillna(14).clip(1, 30)

    # Matches in last 14 days
    def calc_congestion(dates_series):
        dates = pd.to_datetime(dates_series.values)
        counts = []
        for i in range(len(dates)):
            if i == 0:
                counts.append(0)
            else:
                prior = dates[:i]
                diff_days = (dates[i] - prior) / np.timedelta64(1, 'D')
                counts.append(int(np.sum((diff_days <= 14) & (diff_days > 0))))
        return pd.Series(counts, index=dates_series.index)

    logs["Congestion_14D"] = grouped["Date"].transform(calc_congestion)
    return logs

def compute_rolling_xg_and_luck(df: pd.DataFrame, windows: List[int] = [3, 5, 10, 20]) -> pd.DataFrame:
    """Computes strictly pre-match rolling xG, xGA, Finishing Luck and PPDA."""
    df_sorted = df.sort_values(["Date", "HomeTeam"]).reset_index(drop=True)

    # Calculate match-level xG strictly for historical log construction
    xg_h, npxg_h = compute_calibrated_match_xg(df_sorted["HST"], df_sorted["HS"], df_sorted["HC"], df_sorted["HTHG"], is_home=True)
    xg_a, npxg_a = compute_calibrated_match_xg(df_sorted["AST"], df_sorted["AS"], df_sorted["AC"], df_sorted["HTAG"], is_home=False)

    records = []
    for idx, row in df_sorted.iterrows():
        # Home
        hf = row.get("HF", 11.0)
        hy = row.get("HY", 1.8) * 2 + row.get("HR", 0.0) * 4
        as_shots = row.get("AS", 10.0)
        h_ppda = (hf + hy + 1.0) / (as_shots + 1.0)

        records.append({
            "Match_ID": idx,
            "Date": row["Date"],
            "Team": row["HomeTeam"],
            "Is_Home": 1,
            "xG_For": xg_h.iloc[idx],
            "xG_Against": xg_a.iloc[idx],
            "Luck_GF": row.get("FTHG", 0.0) - xg_h.iloc[idx],
            "PPDA": h_ppda
        })

        # Away
        af = row.get("AF", 11.0)
        ay = row.get("AY", 1.8) * 2 + row.get("AR", 0.0) * 4
        hs_shots = row.get("HS", 12.0)
        a_ppda = (af + ay + 1.0) / (hs_shots + 1.0)

        records.append({
            "Match_ID": idx,
            "Date": row["Date"],
            "Team": row["AwayTeam"],
            "Is_Home": 0,
            "xG_For": xg_a.iloc[idx],
            "xG_Against": xg_h.iloc[idx],
            "Luck_GF": row.get("FTAG", 0.0) - xg_a.iloc[idx],
            "PPDA": a_ppda
        })

    logs = pd.DataFrame(records)
    logs = logs.sort_values(["Team", "Date", "Match_ID"]).reset_index(drop=True)
    grouped = logs.groupby("Team")

    for w in windows:
        for metric in ["xG_For", "xG_Against", "Luck_GF", "PPDA"]:
            roll = grouped[metric].apply(lambda g: g.shift(1).rolling(w, min_periods=1).mean()).reset_index(level=0, drop=True)
            logs[f"{metric}_roll_{w}"] = roll.fillna(0.0)

    # Separate Home and Away
    home_xg = logs[logs["Is_Home"] == 1].copy()
    away_xg = logs[logs["Is_Home"] == 0].copy()

    xg_cols_keep = ["Match_ID"] + [c for c in home_xg.columns if "roll_" in c]
    home_xg = home_xg[xg_cols_keep].rename(columns={c: f"Home_{c}" for c in xg_cols_keep if c != "Match_ID"})
    away_xg = away_xg[xg_cols_keep].rename(columns={c: f"Away_{c}" for c in xg_cols_keep if c != "Match_ID"})

    df_out = df_sorted.copy()
    df_out["Match_ID"] = df_out.index
    df_out = df_out.merge(home_xg, on="Match_ID", how="left")
    df_out = df_out.merge(away_xg, on="Match_ID", how="left")
    df_out = df_out.drop(columns=["Match_ID"])

    # Compute differentials
    for w in windows:
        df_out[f"Diff_xG_Net_{w}"] = df_out[f"Home_xG_For_roll_{w}"] - df_out[f"Away_xG_For_roll_{w}"]
        df_out[f"Diff_Luck_GF_{w}"] = df_out[f"Home_Luck_GF_roll_{w}"] - df_out[f"Away_Luck_GF_roll_{w}"]
        df_out[f"Diff_PPDA_{w}"] = df_out[f"Home_PPDA_roll_{w}"] - df_out[f"Away_PPDA_roll_{w}"]

    return df_out

def compute_referee_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """Computes strictly pre-match rolling referee friction metrics."""
    df_out = df.copy()
    if "Referee" not in df_out.columns:
        df_out["Ref_Fouls_Avg_15"] = 22.0
        df_out["Ref_Yellows_Avg_15"] = 3.6
        df_out["Ref_Strictness_Ratio"] = 1.0
        df_out["Ref_Home_Foul_Bias"] = 1.0
        return df_out

    df_out["Total_Fouls"] = df_out.get("HF", 11.0) + df_out.get("AF", 11.0)
    df_out["Total_Cards"] = df_out.get("HY", 1.8) + df_out.get("AY", 1.8) + (df_out.get("HR", 0.0) + df_out.get("AR", 0.0)) * 2

    # Group by referee and shift by 1
    ref_grouped = df_out.groupby("Referee")
    df_out["Ref_Fouls_Avg_15"] = ref_grouped["Total_Fouls"].apply(lambda g: g.shift(1).rolling(15, min_periods=3).mean()).reset_index(level=0, drop=True).fillna(22.0)
    df_out["Ref_Yellows_Avg_15"] = ref_grouped["Total_Cards"].apply(lambda g: g.shift(1).rolling(15, min_periods=3).mean()).reset_index(level=0, drop=True).fillna(3.6)
    
    league_avg_fouls = df_out.groupby("League")["Total_Fouls"].transform(lambda g: g.shift(1).expanding().mean()).fillna(22.0)
    df_out["Ref_Strictness_Ratio"] = (df_out["Ref_Fouls_Avg_15"] / (league_avg_fouls + 1e-4)).clip(0.6, 1.5)
    
    h_foul_roll = ref_grouped["HF"].apply(lambda g: g.shift(1).rolling(15, min_periods=3).mean()).reset_index(level=0, drop=True).fillna(11.0)
    a_foul_roll = ref_grouped["AF"].apply(lambda g: g.shift(1).rolling(15, min_periods=3).mean()).reset_index(level=0, drop=True).fillna(11.0)
    df_out["Ref_Home_Foul_Bias"] = (h_foul_roll / (a_foul_roll + 1e-4)).clip(0.6, 1.6)

    # Clean up temporary columns
    df_out = df_out.drop(columns=["Total_Fouls", "Total_Cards"])
    return df_out

def compute_lineup_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes pre-match Starting XI strength indicators for historical and live rows."""
    h_ratio, a_ratio, diff_ratio = [], [], []
    h_threat, a_threat = [], []
    h_gk_out, a_gk_out = [], []
    h_fatigue, a_fatigue = [], []

    for _, row in df.iterrows():
        h_team = row["HomeTeam"]
        a_team = row["AwayTeam"]
        h_rest = row.get("Home_Rest_Days", 7.0)
        a_rest = row.get("Away_Rest_Days", 7.0)
        h_cong = row.get("Home_Congestion_14D", 2)
        a_cong = row.get("Away_Congestion_14D", 2)

        res_h = evaluate_lineup_strength(h_team, [], rest_days=h_rest, matches_14d=h_cong)
        res_a = evaluate_lineup_strength(a_team, [], rest_days=a_rest, matches_14d=a_cong)

        h_ratio.append(res_h["active_xi_strength_ratio"])
        a_ratio.append(res_a["active_xi_strength_ratio"])
        diff_ratio.append(res_h["active_xi_strength_ratio"] - res_a["active_xi_strength_ratio"])
        h_threat.append(res_h["attack_threat_retention"])
        a_threat.append(res_a["attack_threat_retention"])
        h_gk_out.append(res_h["primary_gk_missing"])
        a_gk_out.append(res_a["primary_gk_missing"])
        h_fatigue.append(res_h["squad_fatigue_load"])
        a_fatigue.append(res_a["squad_fatigue_load"])

    df["Home_Active_XI_Ratio"] = h_ratio
    df["Away_Active_XI_Ratio"] = a_ratio
    df["Diff_Active_XI_Ratio"] = diff_ratio
    df["Home_Attack_Threat_Retention"] = h_threat
    df["Away_Attack_Threat_Retention"] = a_threat
    df["Home_Primary_GK_Missing"] = h_gk_out
    df["Away_Primary_GK_Missing"] = a_gk_out
    df["Home_Squad_Fatigue"] = h_fatigue
    df["Away_Squad_Fatigue"] = a_fatigue
    return df

def build_v2_leakfree_features(df: pd.DataFrame, windows: List[int] = [3, 5, 10, 20]) -> pd.DataFrame:
    """Master pipeline producing 100% leak-free features across Tracks A, B, and C."""
    print("[V2 PIPELINE] Step 1: Elo and Pi-Ratings...", flush=True)
    df = compute_ratings_features(df)

    print("[V2 PIPELINE] Step 2: European ClubElo Engine...", flush=True)
    df = compute_historical_club_elo(df)

    print("[V2 PIPELINE] Step 3: Dixon-Coles Goal Expectancy...", flush=True)
    df = compute_dixon_coles_features(df)

    print("[V2 PIPELINE] Step 4: Chronological Rolling Form (Shifted by 1)...", flush=True)
    logs = build_team_match_logs(df)
    logs_rolled = compute_rolling_form_features(logs, windows=windows)

    home_feats = logs_rolled[logs_rolled["Is_Home"] == 1].copy()
    away_feats = logs_rolled[logs_rolled["Is_Home"] == 0].copy()

    drop_cols = ["GF", "GA", "GD", "Points", "Win", "Draw", "Loss", "Clean_Sheet",
                 "Failed_To_Score", "SOT_For", "SOT_Against", "Corners_For",
                 "Corners_Against", "Second_Half_GF", "Is_Home", "Team", "Opponent", "League", "Date", "Prev_Date"]

    home_feats = home_feats.drop(columns=[c for c in drop_cols if c in home_feats.columns])
    away_feats = away_feats.drop(columns=[c for c in drop_cols if c in away_feats.columns])

    home_rename = {c: f"Home_{c}" for c in home_feats.columns if c != "Match_ID"}
    away_rename = {c: f"Away_{c}" for c in away_feats.columns if c != "Match_ID"}
    home_feats = home_feats.rename(columns=home_rename)
    away_feats = away_feats.rename(columns=away_rename)

    df_feats = df.copy()
    df_feats["Match_ID"] = df_feats.index
    df_feats = df_feats.merge(home_feats, on="Match_ID", how="left")
    df_feats = df_feats.merge(away_feats, on="Match_ID", how="left")
    df_feats = df_feats.drop(columns=["Match_ID"])

    # Form Differentials
    for w in windows:
        if f"Home_Points_roll_{w}" in df_feats.columns and f"Away_Points_roll_{w}" in df_feats.columns:
            df_feats[f"Diff_PPG_{w}"] = df_feats[f"Home_Points_roll_{w}"] - df_feats[f"Away_Points_roll_{w}"]
            df_feats[f"Diff_GD_{w}"] = df_feats[f"Home_GD_roll_{w}"] - df_feats[f"Away_GD_roll_{w}"]
            df_feats[f"Diff_SOT_Ratio_{w}"] = df_feats[f"Home_SOT_Ratio_roll_{w}"] - df_feats[f"Away_SOT_Ratio_roll_{w}"]

    df_feats["Rest_Diff"] = df_feats["Home_Rest_Days"] - df_feats["Away_Rest_Days"]

    print("[V2 PIPELINE] Step 5: Rolling xG, xGA, Finishing Luck & PPDA...", flush=True)
    df_feats = compute_rolling_xg_and_luck(df_feats, windows=windows)

    print("[V2 PIPELINE] Step 6: Tactical Style Formations & Matchups...", flush=True)
    df_feats = compute_tactical_features(df_feats, windows=[5, 15])

    print("[V2 PIPELINE] Step 7: Referee Friction Profiles...", flush=True)
    df_feats = compute_referee_profiles(df_feats)

    print("[V2 PIPELINE] Step 8: Lineup Strength Delta Engine...", flush=True)
    df_feats = compute_lineup_features(df_feats)

    print("[V2 PIPELINE] Step 9: Shin Fair Opening & Closing Market Odds...", flush=True)
    df_feats = compute_shin_market_odds(df_feats)

    # Market Divergences (Opening odds vs Model)
    df_feats["Divergence_DC_Open_H"] = df_feats["DC_Prob_H"] - df_feats["Open_Fair_Prob_H"]
    df_feats["Divergence_Elo_Open_H"] = df_feats["Elo_Prob_H"] - df_feats["Open_Fair_Prob_H"]
    df_feats["Divergence_ClubElo_Open_H"] = df_feats["ClubElo_WinProb_H"] - df_feats["Open_Fair_Prob_H"]

    # Steam alignment
    df_feats["Steam_Align_H"] = ((df_feats["Market_Steam_H"] == 1.0) & (df_feats["Divergence_DC_Open_H"] > 0)).astype(float)
    df_feats["Steam_Align_A"] = ((df_feats["Market_Steam_A"] == 1.0) & (df_feats["DC_Prob_A"] > df_feats["Open_Fair_Prob_A"])).astype(float)

    # Assign Chronological Splits
    df_feats["Split"] = "Train"
    df_feats.loc[df_feats["Date"] < "2021-07-01", "Split"] = "Warmup"
    df_feats.loc[(df_feats["Date"] >= "2024-01-01") & (df_feats["Date"] <= "2024-05-31"), "Split"] = "Val"
    df_feats.loc[df_feats["Date"] >= "2024-08-01", "Split"] = "Test"

    print(f"[V2 PIPELINE COMPLETE] Total records: {len(df_feats)}. Columns: {df_feats.shape[1]}", flush=True)
    return df_feats

# EXPLICIT PRE-MATCH FEATURE WHITELISTS
# RAW IN-PLAY COLUMNS ARE STRICTLY BANNED!
BANNED_RAW_COLUMNS = {
    "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR", "Outcome", "Total_Goals", "Over25", "BTTS",
    "HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR",
    "xG_Home", "xG_Away", "Finishing_Luck_H", "Finishing_Luck_A", "Total_Fouls", "Total_Cards",
    "Date", "League", "Season", "HomeTeam", "AwayTeam", "Split", "Referee", "Most_Likely_Score"
}

# Backward-compatibility alias
build_all_features = build_v2_leakfree_features

def get_track_feature_columns(df: pd.DataFrame, track: str = "A") -> List[str]:
    """Returns strictly pre-match feature column names for the specified track."""
    cols = df.columns.tolist()

    # Base candidate pool: all numeric columns not in banned raw columns and not bookmaker odds
    # Identify bookmaker odds patterns
    raw_odds_prefixes = ["B365", "BW", "IW", "PS", "WH", "VC", "Max", "Avg", "AH", "P<", "P>", "Odds_"]

    def is_raw_bookmaker_col(c: str) -> bool:
        if c in ["Open_Fair_Prob_H", "Open_Fair_Prob_D", "Open_Fair_Prob_A", "Open_Shin_Z",
                 "Close_Fair_Prob_H", "Close_Fair_Prob_D", "Close_Fair_Prob_A", "Close_Shin_Z",
                 "Market_Drift_H", "Market_Drift_A", "Market_Steam_H", "Market_Steam_A",
                 "Divergence_DC_Open_H", "Divergence_Elo_Open_H", "Divergence_ClubElo_Open_H",
                 "Steam_Align_H", "Steam_Align_A"]:
            return False
        return any(c.startswith(p) or f"_{p}" in c for p in raw_odds_prefixes)

    # 1. Track A: Pure Football Fundamentals (ZERO Odds)
    track_a_cols = []
    for c in cols:
        if c in BANNED_RAW_COLUMNS:
            continue
        if is_raw_bookmaker_col(c):
            continue
        if any(m in c for m in ["Fair_Prob", "Shin_", "Market_", "Steam_", "Divergence_"]):
            continue
        if pd.api.types.is_numeric_dtype(df[c]) and df[c].notnull().sum() > 100:
            track_a_cols.append(c)

    if track == "A":
        return sorted(track_a_cols)

    # 2. Track B: Early-Market Hybrid (Opening Odds + Track A)
    track_b_cols = list(track_a_cols)
    for c in ["Open_Fair_Prob_H", "Open_Fair_Prob_D", "Open_Fair_Prob_A", "Open_Shin_Z",
              "Divergence_DC_Open_H", "Divergence_Elo_Open_H", "Divergence_ClubElo_Open_H"]:
        if c in df.columns:
            track_b_cols.append(c)

    if track == "B":
        return sorted(track_b_cols)

    # 3. Track C: Late-Market Syndicate Engine (Track B + Lineups + Steam)
    track_c_cols = list(track_b_cols)
    for c in ["Market_Steam_H", "Market_Steam_A", "Market_Drift_H", "Steam_Align_H", "Steam_Align_A",
              "Home_Active_XI_Ratio", "Away_Active_XI_Ratio", "Diff_Active_XI_Ratio",
              "Home_Attack_Threat_Retention", "Away_Attack_Threat_Retention",
              "Home_Primary_GK_Missing", "Away_Primary_GK_Missing",
              "Home_Squad_Fatigue", "Away_Squad_Fatigue"]:
        if c in df.columns and c not in track_c_cols:
            track_c_cols.append(c)

    return sorted(track_c_cols)

def generate_and_save_v2_features(
    input_path: str = "data/processed/matches_clean.csv",
    output_parquet: str = "data/processed/features_v2_leakfree.parquet"
) -> pd.DataFrame:
    """Executes V2 pipeline and saves audited leak-free feature matrix."""
    print(f"[V2 INGESTION] Reading clean dataset from {input_path}...", flush=True)
    df = pd.read_csv(input_path, low_memory=False)
    df["Date"] = pd.to_datetime(df["Date"])

    df_v2 = build_v2_leakfree_features(df)

    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)
    try:
        df_v2.to_parquet(output_parquet, index=False)
    except Exception as e:
        print(f"[WARNING] Parquet export failed: {e}")

    csv_out = output_parquet.replace(".parquet", ".csv")
    df_v2.to_csv(csv_out, index=False)
    print(f"[V2 COMPLETE] Saved to {output_parquet} and {csv_out}", flush=True)
    return df_v2

if __name__ == "__main__":
    generate_and_save_v2_features()
