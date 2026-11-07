# Forensic Post-Mortem of V1 Modeling Pipeline
**Author:** Quantitative Sports Modeler & Systems Architect  
**Date:** 2026-11-05  
**Audit Target:** `models/track_a_bundle.joblib`, `models/track_b_bundle.joblib`, `src/features/build_features.py`, and `src/models/train.py`

---

## 1. Executive Summary & Root Cause Confirmation
In V1, our models reported an apparently exceptional **62.33% Accuracy** and **0.8369 Log Loss** on Track A (purportedly using zero market odds), and **63.36% Accuracy / 0.8231 Log Loss** on Track B, with reported ticket win rates $>80\%$.

A rigorous forensic audit of the serialized model weights in `models/track_a_bundle.joblib` has **conclusively proven the existence of severe Intra-Row Post-Kickoff Data Leakage**. The 0.8369 Log Loss was mathematically artificial, driven by the accidental inclusion of in-play 90-minute box-score statistics and un-scrubbed bookmaker closing odds inside the feature matrix.

---

## 2. The Smoking Guns: Feature Importance Inspection

When extracting the top features ranked by model coefficient magnitude in `LogisticRegression` and feature importance in `RandomForestClassifier` from `models/track_a_bundle.joblib`, the following top predictors emerged:

### Logistic Regression Top Predictors (Track A):
1. **`HST` (Home Shots on Target in the match):** Coef = `+0.53265` (#1 Ranked Feature)
2. **`AST` (Away Shots on Target in the match):** Coef = `+0.52962` (#2 Ranked Feature)
3. **`HS` (Home Total Shots in the match):** Coef = `+0.23715` (#3 Ranked Feature)
4. **`IWCD` (Interwetten Closing Draw Odds):** Coef = `+0.22808` (#4 Ranked Feature)
5. **`PC<2.5` (Pinnacle Closing Under 2.5 Market Odds):** Coef = `+0.20946` (#5 Ranked Feature)
6. **`HC` (Home Corners in the match):** Coef = `+0.20401` (#6 Ranked Feature)
7. **`BWCA` (Betway Closing Away Odds):** Coef = `+0.18902` (#7 Ranked Feature)
8. **`AS` (Away Total Shots in the match):** Coef = `+0.16901` (#8 Ranked Feature)
11. **`AC` (Away Corners in the match):** Coef = `+0.15729`
12. **`HR` (Home Red Cards in the match):** Coef = `+0.14883`

### Random Forest Top Predictors (Track A):
1. **`AST` (Away Shots on Target):** Importance = `0.04861` (#1 Feature)
2. **`VCH` (BetVictor Home Odds):** Importance = `0.03578`
3. **`HST` (Home Shots on Target):** Importance = `0.03396`
4. **`IWH` (Interwetten Home Odds):** Importance = `0.03140`
5. **`WHCH` (William Hill Closing Home Odds):** Importance = `0.02891`

---

## 3. Forensic Anatomy of the Leakage Vectors

### Culprit A: Intra-Row In-Play Match Stats Leakage
In `src/models/train.py`, the `get_feature_columns()` function was implemented as:
```python
meta_cols = {
    "Date", "League", "Season", "HomeTeam", "AwayTeam", "FTHG", "FTAG",
    "HTHG", "HTAG", "FTR", "Outcome", "Total_Goals", "Over25", "BTTS",
    "Split", "Most_Likely_Score", "Odds_H", "Odds_D", "Odds_A", "Odds_Over25", "Odds_Under25"
}
all_num_cols = [c for c in df.columns if c not in meta_cols and pd.api.types.is_numeric_dtype(df[c])]
```
Because `meta_cols` only excluded target scorelines and primary odds, **the raw match box-score statistics were never excluded**:
- `HST` / `AST`: Shots on Target (the single most decisive in-play factor in football).
- `HS` / `AS`: Total Shots.
- `HC` / `AC`: Corner Kicks.
- `HF` / `AF`: Fouls committed.
- `HY` / `AY`: Yellow cards.
- `HR` / `AR`: Red cards (playing with 10 men).

The model was literally trained knowing whether a team received a red card or took 10 shots on target during the 90 minutes.

### Culprit B: Incomplete Market Column Scrubbing in Track A
In `train.py`, the filter `is_market_column()` only checked for a limited substring list:
`["Fair_Prob", "Divergence_", "Market_", "Steam_", "Odds_", "B365", "PSH", "PSD", "PSA", "PSCH", "PSCD", "PSCA", "AvgH", "AvgD", "AvgA", "AvgCH", "AvgCD", "AvgCA", "MaxH", "MaxCH"]`.
Columns from other bookmakers (`BW*`, `IW*`, `WH*`, `VC*`, `Max*`, `Avg*`, `AH*`, `P<*`, `P>*`) did not match the filter. Exactly **53 market odds columns** (including closing line odds) slipped into Track A, violating the "pure football fundamentals" rule.

### Culprit C: Why `tests/test_no_leakage.py` Passed
`tests/test_no_leakage.py` performed a *temporal future mutation test*: it took rows 150 to 199, changed their final scores to `99-0`, and verified that rows 0 to 149 did not change. This proved that rolling aggregations using `.shift(1)` correctly avoided future leakage across *different matches*. However, it never checked whether match $i$'s *own in-play statistics* leaked into match $i$'s pre-match feature row!

---

## 4. The V2 Architectural Remedy

To eliminate 100% of leakage, V2 implements:
1. **Strict Explicit Feature Whitelisting:**
   - Raw in-play match columns (`HST`, `AST`, `HS`, `AS`, `HC`, `AC`, `HF`, `AF`, `HY`, `AY`, `HR`, `AR`, `HTHG`, `HTAG`, `HTR`, `FTHG`, `FTAG`, `FTR`) and all bookmaker columns are strictly banned from feature matrices.
   - Only rolling, shifted (`.shift(1)`) historical variables and genuine pre-match ratings are permitted.
2. **The Target-Row Blindfold Test (`tests/test_intra_row_and_temporal_leakage.py`):**
   - Wipes all in-play and post-kickoff fields for target match $i$ to `NaN` prior to feature extraction.
   - Asserts that $X_i$ is 100% bitwise identical whether post-kickoff fields are present or `NaN`.
3. **Physical Bound Sanity Assertion:**
   - Real-world, leak-free 1X2 Log Loss on 1,752 untouched European fixtures must strictly reside between `0.940` and `1.050`. Any value $< 0.900$ triggers an automatic pipeline halt.
