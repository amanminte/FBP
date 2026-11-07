"""
Module 1: Market Odds Flow & Sharp Steam Movement + Referee Profiling Engine.
- Zero Data Leakage: Strictly pre-match opening vs closing market odds and shifted rolling referee metrics.
- Market Steam Tracking: De-vigged opening vs closing Pinnacle / Bet365 odds drift, syndicate flow signals.
- Referee Profiling: Rolling foul averages, card strictness index, and home-bias ratios.
"""
import numpy as np
import pandas as pd

def get_series(df: pd.DataFrame, col: str, default=np.nan) -> pd.Series:
    """Safely retrieves a numeric Series from DataFrame, returning Series of defaults if missing."""
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(default, index=df.index, dtype=float)

def compute_market_drift_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes de-vigged opening vs closing market odds flow and sharp steam signals."""
    df_out = df.copy()

    # 1. Resolve Opening 1X2 Odds (Priority: Pinnacle -> Bet365 -> Avg -> Odds_H)
    open_h = get_series(df_out, "PSH").combine_first(
        get_series(df_out, "B365H")
    ).combine_first(get_series(df_out, "AvgH")).combine_first(
        get_series(df_out, "Odds_H", 2.50)
    ).fillna(2.50)

    open_d = get_series(df_out, "PSD").combine_first(
        get_series(df_out, "B365D")
    ).combine_first(get_series(df_out, "AvgD")).combine_first(
        get_series(df_out, "Odds_D", 3.25)
    ).fillna(3.25)

    open_a = get_series(df_out, "PSA").combine_first(
        get_series(df_out, "B365A")
    ).combine_first(get_series(df_out, "AvgA")).combine_first(
        get_series(df_out, "Odds_A", 2.90)
    ).fillna(2.90)

    # 2. Resolve Closing 1X2 Odds (Priority: Pinnacle Close -> Bet365 Close -> Avg Close -> Opening)
    close_h = get_series(df_out, "PSCH").combine_first(
        get_series(df_out, "B365CH")
    ).combine_first(get_series(df_out, "AvgCH")).combine_first(open_h).fillna(open_h)

    close_d = get_series(df_out, "PSCD").combine_first(
        get_series(df_out, "B365CD")
    ).combine_first(get_series(df_out, "AvgCD")).combine_first(open_d).fillna(open_d)

    close_a = get_series(df_out, "PSCA").combine_first(
        get_series(df_out, "B365CA")
    ).combine_first(get_series(df_out, "AvgCA")).combine_first(open_a).fillna(open_a)

    # 3. De-vig Opening Probabilities
    sum_open = (1.0 / open_h) + (1.0 / open_d) + (1.0 / open_a)
    p_open_h = (1.0 / open_h) / sum_open
    p_open_d = (1.0 / open_d) / sum_open
    p_open_a = (1.0 / open_a) / sum_open

    # 4. De-vig Closing Probabilities
    sum_close = (1.0 / close_h) + (1.0 / close_d) + (1.0 / close_a)
    p_close_h = (1.0 / close_h) / sum_close
    p_close_d = (1.0 / close_d) / sum_close
    p_close_a = (1.0 / close_a) / sum_close

    # Fill any remaining NaNs with neutral baseline
    p_open_h = p_open_h.fillna(0.40)
    p_open_d = p_open_d.fillna(0.28)
    p_open_a = p_open_a.fillna(0.32)

    p_close_h = p_close_h.fillna(p_open_h)
    p_close_d = p_close_d.fillna(p_open_d)
    p_close_a = p_close_a.fillna(p_open_a)

    # 5. Probability Drifts (Sharp Syndicate Flow)
    drift_h = p_close_h - p_open_h
    drift_d = p_close_d - p_open_d
    drift_a = p_close_a - p_open_a

    # 6. Relative Odds Ratio Drift
    odds_ratio_drift_h = (close_h - open_h) / open_h
    odds_ratio_drift_a = (close_a - open_a) / open_a

    df_out["Market_P_Open_H"] = p_open_h
    df_out["Market_P_Open_D"] = p_open_d
    df_out["Market_P_Open_A"] = p_open_a

    df_out["Market_P_Close_H"] = p_close_h
    df_out["Market_P_Close_D"] = p_close_d
    df_out["Market_P_Close_A"] = p_close_a

    df_out["Market_Drift_H"] = drift_h
    df_out["Market_Drift_D"] = drift_d
    df_out["Market_Drift_A"] = drift_a

    df_out["Market_Odds_Ratio_Drift_H"] = odds_ratio_drift_h.fillna(0.0)
    df_out["Market_Odds_Ratio_Drift_A"] = odds_ratio_drift_a.fillna(0.0)

    # Binary Steam Moves (>= +2% probability shift)
    df_out["Market_Steam_H"] = (drift_h >= 0.02).astype(float)
    df_out["Market_Steam_A"] = (drift_a >= 0.02).astype(float)
    df_out["Market_Drift_Magnitude"] = np.abs(drift_h) + np.abs(drift_d) + np.abs(drift_a)

    # 7. Total Goals Over 2.5 Market Drift
    ou_open = get_series(df_out, "Avg>2.5").combine_first(get_series(df_out, "B365>2.5")).fillna(1.90)
    ou_close = get_series(df_out, "AvgC>2.5").combine_first(get_series(df_out, "B365C>2.5")).combine_first(ou_open).fillna(ou_open)

    ou_open_u = get_series(df_out, "Avg<2.5").combine_first(get_series(df_out, "B365<2.5")).fillna(1.90)
    ou_close_u = get_series(df_out, "AvgC<2.5").combine_first(get_series(df_out, "B365C<2.5")).combine_first(ou_open_u).fillna(ou_open_u)

    sum_ou_open = (1.0 / ou_open) + (1.0 / ou_open_u)
    sum_ou_close = (1.0 / ou_close) + (1.0 / ou_close_u)

    p_open_ou = ((1.0 / ou_open) / sum_ou_open).fillna(0.50)
    p_close_ou = ((1.0 / ou_close) / sum_ou_close).fillna(p_open_ou)

    df_out["Market_Drift_Over25"] = p_close_ou - p_open_ou
    df_out["Market_Steam_Over25"] = (df_out["Market_Drift_Over25"] >= 0.02).astype(float)

    return df_out

def compute_referee_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes zero-leakage shifted rolling referee metrics and strictness index."""
    df_out = df.copy()

    # Check if referee column exists
    if "Referee" not in df_out.columns:
        df_out["Ref_Known"] = 0.0
        df_out["Ref_Prior_Matches"] = 0.0
        df_out["Ref_Fouls_Avg_15"] = 23.5
        df_out["Ref_Yellows_Avg_15"] = 3.6
        df_out["Ref_Reds_Avg_15"] = 0.12
        df_out["Ref_Strictness_Ratio"] = 1.0
        df_out["Ref_Home_Foul_Bias"] = 0.50
        return df_out

    # Global league averages for baseline imputation
    hf = get_series(df_out, "HF", 11.5)
    af = get_series(df_out, "AF", 11.5)
    hy = get_series(df_out, "HY", 1.8)
    ay = get_series(df_out, "AY", 1.8)
    hr = get_series(df_out, "HR", 0.06)
    ar = get_series(df_out, "AR", 0.06)

    total_fouls = hf + af
    total_yellows = hy + ay
    total_reds = hr + ar

    league_fouls_mean = total_fouls.mean()
    if np.isnan(league_fouls_mean) or league_fouls_mean == 0:
        league_fouls_mean = 23.5

    league_yellows_mean = total_yellows.mean()
    if np.isnan(league_yellows_mean) or league_yellows_mean == 0:
        league_yellows_mean = 3.6

    league_reds_mean = total_reds.mean()
    if np.isnan(league_reds_mean) or league_reds_mean == 0:
        league_reds_mean = 0.12

    # Filter to matches with known referee and sort chronologically
    df_out["Total_Fouls"] = total_fouls
    df_out["Total_Yellows"] = total_yellows
    df_out["Total_Reds"] = total_reds

    ref_mask = df_out["Referee"].notna() & (df_out["Referee"] != "") & (df_out["Referee"] != "nan")
    
    # Initialize output columns with neutral league priors
    df_out["Ref_Known"] = 0.0
    df_out["Ref_Prior_Matches"] = 0.0
    df_out["Ref_Fouls_Avg_15"] = league_fouls_mean
    df_out["Ref_Yellows_Avg_15"] = league_yellows_mean
    df_out["Ref_Reds_Avg_15"] = league_reds_mean
    df_out["Ref_Strictness_Ratio"] = 1.0
    df_out["Ref_Home_Foul_Bias"] = 0.50

    if ref_mask.sum() > 0:
        ref_df = df_out[ref_mask].sort_values("Date").copy()
        grouped = ref_df.groupby("Referee")

        # Shifted rolling metrics (Zero Data Leakage: strictly match history before today)
        prior_matches = grouped.cumcount()
        rolling_fouls = grouped["Total_Fouls"].transform(lambda s: s.shift(1).rolling(15, min_periods=3).mean())
        rolling_yellows = grouped["Total_Yellows"].transform(lambda s: s.shift(1).rolling(15, min_periods=3).mean())
        rolling_reds = grouped["Total_Reds"].transform(lambda s: s.shift(1).rolling(15, min_periods=3).mean())
        
        rolling_hf = grouped["HF"].transform(lambda s: s.shift(1).rolling(15, min_periods=3).sum())
        rolling_af = grouped["AF"].transform(lambda s: s.shift(1).rolling(15, min_periods=3).sum())
        home_foul_bias = rolling_hf / (rolling_hf + rolling_af + 1e-5)

        # Merge back using index
        df_out.loc[ref_df.index, "Ref_Known"] = (prior_matches >= 3).astype(float)
        df_out.loc[ref_df.index, "Ref_Prior_Matches"] = prior_matches.astype(float)
        df_out.loc[ref_df.index, "Ref_Fouls_Avg_15"] = rolling_fouls.fillna(league_fouls_mean)
        df_out.loc[ref_df.index, "Ref_Yellows_Avg_15"] = rolling_yellows.fillna(league_yellows_mean)
        df_out.loc[ref_df.index, "Ref_Reds_Avg_15"] = rolling_reds.fillna(league_reds_mean)
        df_out.loc[ref_df.index, "Ref_Strictness_Ratio"] = df_out.loc[ref_df.index, "Ref_Fouls_Avg_15"] / league_fouls_mean
        df_out.loc[ref_df.index, "Ref_Home_Foul_Bias"] = home_foul_bias.fillna(0.50)

    # Drop temporary calculation columns
    df_out = df_out.drop(columns=["Total_Fouls", "Total_Yellows", "Total_Reds"])
    return df_out

def compute_module1_features(df: pd.DataFrame) -> pd.DataFrame:
    """Entry point for Module 1: Market Odds Flow + Referee Profiling."""
    print("[MODULE 1] Computing Market Odds Drift & Sharp Steam Signals...")
    df = compute_market_drift_features(df)
    print("[MODULE 1] Computing Shifted Referee Profiling & Strictness Index...")
    df = compute_referee_features(df)
    return df
