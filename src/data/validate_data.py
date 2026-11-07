"""
Data Validation, Date Parsing, Team-Name Canonicalization & Schema Standardization.
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, Tuple

# Canonical team names mapping across historical seasons
TEAM_NAME_MAP = {
    "Man United": "Manchester United",
    "Man City": "Manchester City",
    "Nott'm Forest": "Nottingham Forest",
    "Sheffield United": "Sheffield United",
    "Spurs": "Tottenham",
    "Tottenham Hotspur": "Tottenham",
    "Wolves": "Wolverhampton",
    "Wolverhampton Wanderers": "Wolverhampton",
    "West Ham United": "West Ham",
    "Newcastle United": "Newcastle",
    "Brighton and Hove Albion": "Brighton",
    "Athletic Bilbao": "Ath Bilbao",
    "Athletic Club": "Ath Bilbao",
    "Atletico Madrid": "Ath Madrid",
    "Atlético Madrid": "Ath Madrid",
    "Paris Saint Germain": "Paris SG",
    "Paris SG": "Paris SG",
    "Marseille": "Marseille",
    "Bayern Munich": "Bayern Munich",
    "Leverkusen": "Leverkusen",
    "Bayer Leverkusen": "Leverkusen",
    "Borussia Dortmund": "Dortmund",
    "Monchengladbach": "M'gladbach",
    "Moenchengladbach": "M'gladbach",
    "Borussia Monchengladbach": "M'gladbach",
    "Internazionale": "Inter",
    "AC Milan": "Milan",
    "Hellas Verona": "Verona",
}

def canonicalize_team(team: str) -> str:
    if not isinstance(team, str):
        return str(team)
    cleaned = team.strip()
    return TEAM_NAME_MAP.get(cleaned, cleaned)

def clean_and_validate_matches(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes, validates, and cleans the raw match dataframe."""
    required_cols = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "League", "Season"]
    df = df.dropna(subset=[col for col in required_cols if col in df.columns]).copy()

    # Parse Dates cleanly
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).copy()

    # Canonicalize Team Names
    df["HomeTeam"] = df["HomeTeam"].apply(canonicalize_team)
    df["AwayTeam"] = df["AwayTeam"].apply(canonicalize_team)

    # Filter out invalid scorelines
    df["FTHG"] = pd.to_numeric(df["FTHG"], errors="coerce")
    df["FTAG"] = pd.to_numeric(df["FTAG"], errors="coerce")
    df = df.dropna(subset=["FTHG", "FTAG"]).copy()
    df["FTHG"] = df["FTHG"].astype(int)
    df["FTAG"] = df["FTAG"].astype(int)

    # Standardize FTR to 'H', 'D', 'A'
    valid_ftr = df["FTR"].isin(["H", "D", "A"])
    df = df[valid_ftr].copy()

    # Numeric outcomes: 0 = H, 1 = D, 2 = A
    outcome_map = {"H": 0, "D": 1, "A": 2}
    df["Outcome"] = df["FTR"].map(outcome_map)
    df["Total_Goals"] = df["FTHG"] + df["FTAG"]
    df["Over25"] = (df["Total_Goals"] > 2.5).astype(int)
    df["BTTS"] = ((df["FTHG"] > 0) & (df["FTAG"] > 0)).astype(int)

    # Numerical box score stats (fill missing with 0 or reasonable medians)
    box_cols = ["HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR", "HTHG", "HTAG"]
    for col in box_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0

    # Bookmaker Odds handling (B365 or Pinnacle or Avg)
    # 1X2 Odds
    for h, d, a in [("B365H", "B365D", "B365A"), ("PSH", "PSD", "PSA"), ("AvgH", "AvgD", "AvgA")]:
        if h in df.columns and d in df.columns and a in df.columns:
            df[h] = pd.to_numeric(df[h], errors="coerce")
            df[d] = pd.to_numeric(df[d], errors="coerce")
            df[a] = pd.to_numeric(df[a], errors="coerce")

    # Primary odds selection (Priority: Pinnacle -> Bet365 -> Avg)
    df["Odds_H"] = df.get("PSH", np.nan).combine_first(df.get("B365H", np.nan)).combine_first(df.get("AvgH", np.nan))
    df["Odds_D"] = df.get("PSD", np.nan).combine_first(df.get("B365D", np.nan)).combine_first(df.get("AvgD", np.nan))
    df["Odds_A"] = df.get("PSA", np.nan).combine_first(df.get("B365A", np.nan)).combine_first(df.get("AvgA", np.nan))

    # Over/Under Odds
    ou_h = df.get("P>2.5", np.nan).combine_first(df.get("B365>2.5", np.nan)).combine_first(df.get("Avg>2.5", np.nan))
    ou_u = df.get("P<2.5", np.nan).combine_first(df.get("B365<2.5", np.nan)).combine_first(df.get("Avg<2.5", np.nan))
    df["Odds_Over25"] = pd.to_numeric(ou_h, errors="coerce")
    df["Odds_Under25"] = pd.to_numeric(ou_u, errors="coerce")

    # De-vig / Proportional Fair Probabilities
    sum_inv = (1.0 / df["Odds_H"]) + (1.0 / df["Odds_D"]) + (1.0 / df["Odds_A"])
    df["Fair_Prob_H"] = (1.0 / df["Odds_H"]) / sum_inv
    df["Fair_Prob_D"] = (1.0 / df["Odds_D"]) / sum_inv
    df["Fair_Prob_A"] = (1.0 / df["Odds_A"]) / sum_inv

    sum_ou = (1.0 / df["Odds_Over25"]) + (1.0 / df["Odds_Under25"])
    df["Fair_Prob_Over25"] = (1.0 / df["Odds_Over25"]) / sum_ou
    df["Fair_Prob_Under25"] = (1.0 / df["Odds_Under25"]) / sum_ou

    # Remove duplicates and sort strictly chronologically
    df = df.drop_duplicates(subset=["Date", "League", "HomeTeam", "AwayTeam"]).copy()
    df = df.sort_values(["Date", "League", "HomeTeam"]).reset_index(drop=True)

    print(f"[VALIDATION COMPLETE] Valid matches: {len(df)} across {df['League'].nunique()} leagues.")
    return df

def process_and_save(raw_dir: str = "data/raw", processed_dir: str = "data/processed") -> pd.DataFrame:
    from src.data.load_data import load_raw_dataset
    raw_df = load_raw_dataset(raw_dir)
    clean_df = clean_and_validate_matches(raw_df)
    os.makedirs(processed_dir, exist_ok=True)
    csv_path = os.path.join(processed_dir, "matches_clean.csv")
    clean_df.to_csv(csv_path, index=False)
    try:
        parquet_path = os.path.join(processed_dir, "matches_clean.parquet")
        clean_df.to_parquet(parquet_path, index=False)
    except Exception:
        pass
    print(f"[SAVED] Saved clean dataset to {csv_path}")
    return clean_df

if __name__ == "__main__":
    process_and_save()
