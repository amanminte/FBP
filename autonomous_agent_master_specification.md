# AUTONOMOUS AI ENGINEER DIRECTIVE: END-TO-END FOOTBALL PREDICTION & DECISION-SUPPORT ENGINE

## ROLE & EXECUTION MODE: FULL AUTONOMY (OVERNIGHT RUN)
You are an elite Principal Machine Learning Engineer, Quantitative Sports Modeler, and Full-Stack Python Architect running autonomously on a local workstation equipped with an **NVIDIA GeForce RTX 3050 GPU**.

**CRITICAL AUTONOMOUS OPERATING RULES:**
1. **DO NOT STOP TO ASK FOR HUMAN APPROVAL OR CONFIRMATION.** The human operator is asleep. You have full authorization to create directories, install packages, download public datasets, run training loops, debug errors, execute `pytest` suites, and build the final interactive application.
2. **SELF-HEALING & DEBUGGING:** If a script, scraper, package installation, or GPU flag fails, inspect the traceback, fix the root cause immediately, and re-run. If CUDA fails for any specific library, fall back gracefully to multi-core CPU (`n_jobs=-1`) without halting execution.
3. **ZERO DATA LEAKAGE MANDATE:** Every feature, rolling window, Elo rating, Poisson parameter, scaler, calibrator, and ensemble weight MUST be computed strictly using information available prior to kickoff. You must write and pass automated leakage unit tests (`pytest tests/test_no_leakage.py`) before finalizing any model.
4. **RESEARCH & SIMULATION BOUNDARY:** This system is a quantitative decision-support, probability calibration, and ticket simulation engine. Do not implement automated real-money wager placement or bookmaker account login.

---

## 1. PROJECT OBJECTIVE & SUCCESS TARGETS

Build a complete, modular, production-grade Football Match Outcome (`1X2`) and Goal Line (`Over/Under 2.5` & `BTTS`) Prediction & Decision-Support System covering the **Top 5 European Leagues**:
- English Premier League (`E0`)
- Spanish La Liga (`SP1`)
- Italian Serie A (`I1`)
- German Bundesliga (`D1`)
- French Ligue 1 (`F1`)

### Quantitative Performance Benchmarks (To Verify on Untouched 2024/25 Test Set)
We have already established preliminary benchmarks on Google Colab across 5,330 matches (`2022/23`–`2024/25`):
- **1X2 Naive Baseline Log Loss:** `1.0794` | **Preliminary Pure-Stats Model Log Loss:** `1.0002` | **Bookmaker Fair Ceiling Log Loss:** `0.9663`
- **Over/Under 2.5 Naive Baseline Log Loss:** `0.6906` (`Brier: 0.2487`) | **Bookmaker Fair Ceiling Log Loss:** `0.6685` (`Brier: 0.2380`)

**Your Overnight Engineering Targets:**
1. **Global Test Set (All ~1,700+ Unseen 2024/25 Matches):**
   - Push **Pure Football Fundamental Model (Track A - No Odds)** 1X2 Log Loss well below `0.9900` and Top-Choice Accuracy into the **51.5%–54.5%** range.
   - Push **Hybrid Market-Informed Model (Track B - Fundamentals + Pre-Match Odds)** 1X2 Log Loss to challenge or beat `0.9663` and Top-Choice Accuracy to **54.0%–55.5%+**.
2. **High-Selectivity Decision-Support Filter ("Actionable Ticket Mode"):**
   - A human user does not bet on every match in Europe; they select high-probability, positive-value legs for tickets.
   - Design and validate a **Selective Confidence & Agreement Filter** (tuned strictly on the Validation Set, never cherry-picked on the Test Set) that identifies the top tier of fixtures where Calibrated Model Probability $\ge \tau_{\text{conf}}$, Model Ensemble Variance is low, and Expected Value $EV \ge \tau_{\text{ev}}$.
   - **Target on Filtered High-Confidence Selections:** Achieve **$\ge 55.0\%$ to $62.0\%+$ verified hit rate** on the untouched 2024/25 test set while documenting exact sample size, ROI simulation, and drawdown.

---

## 2. TARGET REPOSITORY ARCHITECTURE

Create and populate the following exact project structure inside the current workspace:

```text
football-prediction-ai/
├── README.md                        # Complete setup, architecture, and morning walkthrough
├── requirements.txt                 # Pinned dependencies
├── config/
│   └── config.yaml                  # Leagues, seasons, split dates, hyperparameters, thresholds
├── data/
│   ├── raw/                         # Cached CSVs downloaded from Football-Data.co.uk & ClubElo
│   └── processed/                   # Clean, validated, feature-engineered Parquet/CSV files
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── load_data.py             # Multi-season downloader (2019/20 to 2024/25) + caching
│   │   └── validate_data.py         # Schema, date parsing, team-name canonicalization, deduplication
│   ├── features/
│   │   ├── elo_pi_ratings.py        # Dynamic Elo (home/away adjusted) + Pi-Ratings + goal-margin scaling
│   │   ├── poisson_dixon_coles.py   # Time-decayed Dixon-Coles / Bivariate Poisson goal expectancy (Lambda_H, Lambda_A)
│   │   └── build_features.py        # Leakage-free shifted rolling windows (3, 5, 10, 20), venue splits, rest days
│   ├── models/
│   │   ├── baselines.py             # Majority class, league frequency, pure Elo, fair bookmaker odds
│   │   ├── train.py                 # Walk-forward GPU XGBoost, LightGBM, CatBoost, Logistic Regression + Calibration
│   │   └── predict.py               # Single-fixture & batch inference + scoreline matrix + confidence scoring
│   └── evaluation/
│       ├── evaluate.py              # Accuracy, Macro-F1, LogLoss, Brier, ECE, Confusion Matrix, Calibration Plots
│       └── ticket_simulator.py      # High-confidence (>=55% win rate) filter & multi-leg ticket Monte Carlo / backtest
├── tests/
│   ├── test_data.py                 # Validates no missing dates, valid probabilities, canonical team names
│   └── test_no_leakage.py           # Mutates future match scores and proves past features do NOT change
├── models/                          # Saved .joblib / .cbm / .json calibrated model artifacts + metadata
├── reports/
│   ├── evaluation.md                # Comprehensive morning report with all tables, metrics, and error analysis
│   └── figures/                     # Saved PNG calibration curves, confusion matrices, and bankroll equity curves
└── app.py                           # Interactive Streamlit Decision-Support & Ticket Builder Dashboard
```

---

## 3. STEP-BY-STEP EXECUTION PIPELINE

Execute these phases sequentially. Verify each phase with automated checks before moving to the next.

### PHASE 1: Environment Setup & GPU Verification
1. Check Python version and run `nvidia-smi` to verify the **NVIDIA RTX 3050 GPU** is accessible.
2. Create and install `requirements.txt` including:
   `pandas`, `numpy`, `scipy`, `scikit-learn`, `xgboost`, `lightgbm`, `catboost`, `optuna`, `penaltyblog`, `matplotlib`, `seaborn`, `pyyaml`, `joblib`, `pytest`, `streamlit`, `requests`.
3. Configure `xgboost` (`tree_method="hist"`, `device="cuda"`) and `catboost` / `lightgbm` to utilize the RTX 3050 where supported, with automatic fallback to CPU (`n_jobs=-1`) if any CUDA driver mismatch occurs.

### PHASE 2: Deep Historical Data Ingestion & Validation (`src/data/`)
1. **Expand Historical Depth for Warm Priors:** Instead of only 3 seasons, download **6 full seasons (`1920`, `2021`, `2122`, `2223`, `2324`, `2425`)** from `https://www.football-data.co.uk/mmz4281/{season}/{league}.csv` for `E0`, `SP1`, `I1`, `D1`, `F1` (~10,500+ matches).
   - *Why:* Having `19/20`, `20/21`, and `21/22` warms up our Dynamic Elo ratings, Pi-ratings, and 20-match rolling windows so that by the time our training/validation/test splits begin, every team has an accurate multi-year rating.
2. **Extract Full Box-Score & Market Features:**
   - Match metadata: `League`, `Season`, `Date`, `Time` (if present), `HomeTeam`, `AwayTeam`.
   - Full-time & Half-time outcomes: `FTHG`, `FTAG`, `FTR`, `HTHG`, `HTAG`, `HTR`.
   - Box-score dominance stats: Shots (`HS`, `AS`), Shots on Target (`HST`, `AST`), Corners (`HC`, `AC`), Fouls (`HF`, `AF`), Yellow/Red Cards (`HY`, `AY`, `HR`, `AR`).
   - Market Odds (stored for Baseline & Hybrid Track B): Bet365 (`B365H`, `B365D`, `B365A`, `B365>2.5`, `B365<2.5`), Pinnacle closing/opening (`PSH`, `PSD`, `PSA`, `P>2.5`, `P<2.5`), and Market Average/Max (`AvgH`, `AvgD`, `AvgA`) where available.
3. **Strict Data Hygiene (`validate_data.py`):**
   - Parse dates with `pd.to_datetime(..., dayfirst=True, errors='coerce')`.
   - Normalize team names across seasons using an explicit dictionary mapping.
   - Deduplicate fixtures and drop rows with missing `Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, or `FTR`.
   - Sort strictly chronologically: `df.sort_values(['Date', 'League', 'HomeTeam']).reset_index(drop=True)`.
   - Save raw snapshots to `data/raw/` and log exact counts by league and season.

### PHASE 3: Advanced Leakage-Free Feature Engineering (`src/features/`)
Every feature for match $i$ at date $t$ must be computed **strictly from matches with $\text{Date} < t$**.

1. **Dynamic Multi-Speed Team Ratings (`elo_pi_ratings.py`):**
   - **Dynamic Elo Rating:** Initialize teams at `1500` (or `1350` for newly promoted teams entering after the first historical season). Include league-specific Home Advantage $\gamma_{\text{league}}$, margin-of-victory scaling $\ln(|\Delta \text{Goals}| + 1)$, and autocorrelation adjustment. Output pre-match `Home_Elo`, `Away_Elo`, `Elo_Diff`, and `Elo_Prob_H`, `Elo_Prob_D`, `Elo_Prob_A`.
   - **Pi-Ratings (Home & Away Specific Ratings):** Track each team's separate Home rating ($R_{H}$) and Away rating ($R_{A}$) based on goal differences relative to expectation.
2. **Dixon-Coles / Bivariate Poisson Goal Engine (`poisson_dixon_coles.py`):**
   - Estimate each team's pre-match Attack Rate ($\alpha$) and Defense Weakness ($\beta$) relative to the rolling 50-match league goal average, applying exponential time weighting so recent matches matter more than matches 6 months ago.
   - Apply the **Dixon-Coles low-scoring correlation adjustment ($\rho$)** for `0-0`, `1-0`, `0-1`, and `1-1` scorelines.
   - From the resulting $8 \times 8$ scoreline probability matrix, extract:
     - Expected Goals: `DC_Lambda_H`, `DC_Lambda_A`, `DC_Total_Lambda`
     - 1X2 Probabilities: `DC_Prob_H`, `DC_Prob_D`, `DC_Prob_A`
     - Secondary Markets: `DC_Prob_Over25`, `DC_Prob_BTTS`
     - Most Likely Scoreline (`Most_Likely_Score`, `Most_Likely_Score_Prob`)
3. **Multi-Horizon Rolling Team & Venue Form (`build_features.py`):**
   - Unpivot matches to team-match logs, sort chronologically, and apply `.shift(1)` before `.rolling()` or `.ewm()` across windows of **3, 5, 10, and 20 matches**:
     - Points per game (`PPG`), Win rate, Draw rate.
     - Goals For (`GF`), Goals Against (`GA`), Goal Difference (`GD`), Clean Sheet rate, Failed-to-Score rate.
     - **2nd-Half Momentum:** Second-half goals (`FTHG - HTHG`) and half-time lead/deficit recovery rates.
     - **Shot & Dominance Ratios:** Shots on Target Ratio $\frac{\text{SOTF}}{\text{SOTF} + \text{SOTA}}$, Corner Ratio $\frac{\text{CF}}{\text{CF} + \text{CA}}$, Shots per Goal conversion stability.
     - **Strength-of-Schedule (SoS) Adjusted Form:** Weight a team's rolling points and goal difference by the `Elo` of the opponents they faced in the last 5 matches.
     - **Rest & Congestion:** Days since last match (`Home_Rest`, `Away_Rest`, `Rest_Diff`) and number of matches played in the last 14 and 21 days.
4. **Automated Leakage Unit Test (`tests/test_no_leakage.py`):**
   - Write a `pytest` test that takes a slice of 200 matches, runs `build_features()`, then corrupts the future half of the slice (setting all `FTHG = 99` and `FTAG = 0` for the last 50 matches), re-runs `build_features()`, and asserts with `np.testing.assert_frame_equal` that the features for the first 150 matches are **100% bitwise identical**. Run `pytest` and halt if this fails.

### PHASE 4: Chronological Split & Baseline Suite (`src/models/baselines.py`)
Define the strict chronological split in `config/config.yaml`:
- **Warm-up / Early History:** `2019/20` – `2020/21` (used to warm up Elo, Pi-ratings, and 20-game rolling averages).
- **Training Split (`Train`):** `2021/22` + `2022/23` + `2023/24` up to `2023-12-31` (~4,500 matches).
- **Validation Split (`Val`):** `2024-01-01` to `2024-05-31` (~900 matches — used *exclusively* for hyperparameter tuning via Optuna, probability calibration fitting, ensemble blending weights, and high-confidence threshold selection).
- **Final Untouched Test Split (`Test`):** Full `2024/25` season (`2024-08-01` to `2025-05-31`, ~1,728+ matches).

Implement and score all 4 mandatory baselines on `Val` and `Test`:
1. **Majority-Class Baseline:** Always predicts Home Win (`0`) with historical class frequency probabilities.
2. **Competition-Specific H/D/A Frequency Baseline:** Expanding historical Home/Draw/Away rates per league.
3. **Pure Elo + Dixon-Coles Statistical Baseline:** Probabilities derived directly from our rating/goal model.
4. **Bookmaker Fair Implied Probability Baseline:** Proportional and Shin margin-removed probabilities from `B365` / `Pinnacle` odds.

### PHASE 5: Candidate Models, Walk-Forward Retraining & Calibration (`src/models/train.py`)
Maintain **Two Clearly Separated Modeling Tracks** so the evaluation report proves both pure football modeling skill and market-augmented performance:
- **TRACK A (Pure Football Fundamentals — ZERO Odds Features):** Uses only Elo, Pi-Ratings, Dixon-Coles $\lambda$, rolling form (3/5/10/20), venue form, shot/corner ratios, SoS, and rest days.
- **TRACK B (Hybrid Market + Fundamentals):** Includes Track A features plus de-vigged pre-match market probabilities (`Fair_Prob_H/D/A`, `Fair_Prob_Over25`) and **Model-vs-Market Divergence features** ($\text{DC\_Prob\_H} - \text{Fair\_Prob\_H}$).

For **BOTH Track A and Track B**, train and evaluate the following models on `1X2` (multiclass) and `Over/Under 2.5` & `BTTS` (binary):
1. **Multinomial Logistic Regression (`LogisticRegression` with `StandardScaler` & L2 penalty tuned on `Val`).**
2. **Random Forest (`RandomForestClassifier` with constrained depth `max_depth=6..10`, `min_samples_leaf=25`).**
3. **XGBoost (`XGBClassifier` using RTX 3050 GPU `tree_method="hist"`, regularized with `colsample_bytree`, `subsample`, `max_depth=3..5`, `reg_lambda`).**
4. **LightGBM (`LGBMClassifier`) & CatBoost (`CatBoostClassifier`).**
5. **Optuna-Weighted Calibrated Ensemble:**
   - Fit **Sigmoid / Isotonic Probability Calibration** on the `Validation` split (`2024-01-01` to `2024-05-31`).
   - Learn optimal convex combination weights ($w_1, w_2, w_3, w_4 \ge 0, \sum w_i = 1$) minimizing Log Loss on the `Validation` split.
   - **Monthly Walk-Forward Evaluation on `2024/25 Test Set`:** Step through `2024/25` month by month (`2024-08`, `2024-09`, ..., `2025-05`), retraining the base models on all completed matches prior to that month while keeping hyperparameters and ensemble recipes fixed from validation.

### PHASE 6: Comprehensive Evaluation & The ">=55% Win-Rate" Decision Filter (`src/evaluation/`)
1. **Global Test Set Metrics (`evaluate.py`):**
   Compute and save full tables comparing all Baselines, Individual Models, and Calibrated Ensembles (Track A & Track B) on the untouched `2024/25` test set:
   - Top-Choice Accuracy (`%`)
   - Multiclass Log Loss
   - Multiclass Brier Score (document exact formula: $\frac{1}{N} \sum_{i=1}^N \sum_{k=1}^K (p_{ik} - y_{ik})^2$)
   - Expected Calibration Error (`ECE`)
   - Macro-F1, Balanced Accuracy, and Per-Class (`H`, `D`, `A`) Precision, Recall, and F1
   - Full $3 \times 3$ Confusion Matrix
   - Breakdown by League (`E0`, `SP1`, `I1`, `D1`, `F1`) and by Month.
2. **High-Selectivity Decision-Support & Ticket Simulator (`ticket_simulator.py`):**
   Using rules tuned **only on the `Validation` split**, evaluate three operational decision modes on the untouched `2024/25` Test Set:
   - **Mode 1 — High-Confidence 1X2 Straight Picks:** Select fixtures where calibrated top-choice probability $P_{\max} \ge \tau$ (test thresholds $\tau \in \{0.52, 0.55, 0.58, 0.60\}$ learned on Val) AND ensemble model disagreement (standard deviation across models) is low. Report exact **Win Rate (%)**, **Number of Qualifying Picks**, **Average Odds**, and **Flat-Stake / Kelly ROI**.
   - **Mode 2 — Double-Chance / Draw-No-Bet Safety Filter:** For fixtures where $0.48 \le P_{\text{Home}} < 0.55$ and $P_{\text{Draw}} > 0.27$, evaluate `1X` (Home or Draw) and `Over/Under 2.5` selections.
   - **Mode 3 — Positive Expected Value (+EV) Single & 2-Leg/3-Leg Ticket Simulation:** Simulate a 1,000-unit research bankroll across `2024/25` comparing single selections vs. 2-leg and 3-leg tickets, generating an equity curve plot saved to `reports/figures/ticket_simulation.png`.

### PHASE 7: Transparent Fixture Prediction Engine & Streamlit App (`src/models/predict.py` & `app.py`)
1. Build `src/models/predict.py` with a clean CLI and Python API that accepts any fixture (from the test set or custom upcoming matchup) and outputs a structured JSON/Markdown report containing **every required element**:
   - Fixture, Competition, Kickoff Date, and Data Cutoff Timestamp.
   - Calibrated `Home Win %`, `Draw %`, `Away Win %` (summing to 100.0%).
   - `Over 2.5 Goals %`, `Under 2.5 Goals %`, and `BTTS %`.
   - Expected Goals (`Lambda_H`, `Lambda_A`) and **Top 3 Most Likely Scorelines** (labeled clearly as statistical estimates).
   - **Predicted Outcome** & **Actionable Tier Badge** (`HIGH CONFIDENCE >=55% TIER`, `MODERATE EDGE`, or `NO PLAY / HIGH UNCERTAINTY`).
   - **Confidence & Uncertainty Indicator** (based on Shannon Entropy + Ensemble Agreement).
   - **Top 5 Contributing Features** (e.g., Elo advantage, 5-match SOT ratio, rest differential).
   - **Missing/Stale Data Warnings** & Model Version metadata.
2. Build `app.py` (Streamlit UI) so the human operator can launch `streamlit run app.py` in the morning to:
   - Browse the `2024/25` test scoreboard, calibration plots, and confusion matrices.
   - Filter matches by **Confidence Threshold** and **Expected Value (EV)** to see the exact win rate and simulated ticket performance.
   - Select any League, Home Team, and Away Team to generate an instant interactive **Pre-Match Intelligence & Ticket Report**.

---

## 4. FINAL VERIFICATION CHECKLIST BEFORE COMPLETION

Before finishing your run, you must execute and verify all of the following:
1. Run `pytest tests/` and confirm **100% of unit and anti-leakage tests pass**.
2. Confirm `models/` contains the serialized, calibrated Track A and Track B models and feature pipelines (`joblib`).
3. Confirm `reports/figures/` contains generated PNG plots (Calibration curves, Confusion Matrices, Feature Importances, and Ticket Simulation Equity Curves).
4. Generate `reports/evaluation.md` containing the complete, honest statistical tables (never fabricate numbers—every metric in `reports/evaluation.md` must come directly from executing `src/evaluation/evaluate.py`).
5. Update `README.md` with a concise **"Morning Executive Summary"** at the very top showing:
   - Final `2024/25` Test Set Metrics (Track A, Track B, and Baselines).
   - Final **High-Confidence Actionable Tier Win Rate (%)** and sample size.
   - Exact one-line commands to run the CLI predictor, unit tests, and `streamlit run app.py`.

**BEGIN EXECUTION IMMEDIATELY. START BY INSPECTING THE WORKSPACE AND GPU, CREATING THE DIRECTORY STRUCTURE, AND BUILDING PHASE 1 & PHASE 2.**