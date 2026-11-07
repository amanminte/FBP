# AUTONOMOUS AI ENGINEER DIRECTIVE (V2): SYNDICATE-GRADE AUDIT, MULTI-MODAL DATA FUSION (xG, LINEUPS, TACTICS, NEWS AI) & LIVE CLV TRADING ENGINE

## ROLE & EXECUTION MODE: FULL AUTONOMY (ZERO HUMAN INTERVENTION)
You are a Principal Quantitative Sports Modeler (with live syndicate trading experience), Senior ML Systems Architect, and Full-Stack Python Engineer operating on a local workstation with an **NVIDIA GeForce RTX 3050 GPU (6GB VRAM)**.

**CRITICAL OPERATING MANDATES:**
1. **DO NOT STOP TO ASK FOR PERMISSION.** Execute every phase from forensic debugging to data integration, model training, unit testing, and Streamlit UI deployment autonomously.
2. **SELF-HEALING EXECUTION:** If a scraper, external API, or package fails, implement fallback sources, retry logic, or local synthetic/historical proxies automatically so the pipeline never halts.
3. **RUTHLESS SCIENTIFIC HONESTY:** Never fabricate metrics. An honest `54.5%` accuracy with `+3.8%` real-world ROI and positive Closing Line Value (CLV) is infinitely more valuable than a leaked `62.3%` model that loses real money.

---

## PART 1: FORENSIC POST-MORTEM OF V1 (KILLING THE `0.8369` LOG LOSS LEAKAGE BUG)

### Why V1's Results Are Mathematically Impossible Without Leakage
In V1 (`EXECUTION_DIARY.md`), Entry 4 reported a realistic **Bookmaker Fair Market Ceiling** of **53.71% Accuracy** and **0.9635 Log Loss** on the 1,752 untouched `2024/25` test matches. Then, Entry 5 reported that Track A (using zero odds) achieved **62.33% Accuracy** and **0.8369 Log Loss**, and Entry 6 claimed a **78.45% hit rate (+41.69% Flat ROI)** across 789 bets.

In top-flight European football, **no leak-free model achieves `0.8369` Log Loss or `+41.69%` ROI over 789 matches**. Even though `tests/test_no_leakage.py` passed, it only tested whether mutating *future rows* changed *past rows*. It did **NOT** test **Intra-Row Post-Kickoff Leakage** or **Global Target Encoding Leakage**.

### Mandatory Forensic Audit & Fix Protocol (Execute First)
1. **Inspect `models/track_a_bundle.joblib` and `src/features/build_features.py`:**
   - Extract and print the top 25 features ranked by permutation importance / tree split gain.
   - Check for and immediately purge the following classic leakage culprits:
     - **Culprit A (Intra-Row Match Stats):** In-play/post-match columns from `Football-Data.co.uk` accidentally left in `feature_cols`: Half-Time Goals/Result (`HTHG`, `HTAG`, `HTR`), Full-Time Shots/Corners/Fouls/Cards (`HS`, `AS`, `HST`, `AST`, `HC`, `AC`, `HF`, `AF`, `HY`, `AY`, `HR`, `AR`), or closing odds leakage into Track A.
     - **Culprit B (Unshifted Rolling/EWM Aggregations):** Any `.rolling()`, `.ewm()`, or `.expanding()` call on goals, points, or shots that is missing `.shift(1)` prior to aggregation, or where `.groupby('Team')` was applied *after* merging or without strict chronological sorting.
     - **Culprit C (Global Dixon-Coles / Pi-Rating Lookahead):** Fitting Dixon-Coles attack/defense parameters ($\alpha, \beta$) once on the entire dataset rather than fitting strictly on matches with $\text{Date} < t_{\text{kickoff}}$.
2. **Write the Ultimate Anti-Leakage Test (`tests/test_intra_row_and_temporal_leakage.py`):**
   - **Test 1 (Future-Row Mutation):** Mutate `FTHG`, `FTAG`, `FTR`, `HTHG`, `HTAG`, `HS`, `AS`, `HST`, `AST` for the last 50 rows of a 200-row slice and assert that all features for the first 150 rows are bitwise identical.
   - **Test 2 (Target-Row Blindfold Test — CRITICAL):** Take match $i$. Before computing features for match $i$, overwrite match $i$'s own post-kickoff columns (`FTHG = np.nan`, `FTAG = np.nan`, `FTR = None`, `HTHG = np.nan`, `HTAG = np.nan`, `HTR = None`, `HS = np.nan`, `AS = np.nan`, `HST = np.nan`, `AST = np.nan`, `HC = np.nan`, `AC = np.nan`, `HF = np.nan`, `AF = np.nan`, `HY = np.nan`, `AY = np.nan`, `HR = np.nan`, `AR = np.nan`). Assert that the generated pre-match feature vector $X_i$ is **100% identical** whether match $i$'s post-kickoff stats are present or wiped to `NaN`!
   - **Test 3 (Sanity Ceiling Assertion):** Assert that on the untouched `2024/25` test set (all 1,752 matches), Track A 1X2 Log Loss lies in the realistic physical range $[0.940, 1.050]$. If Log Loss is $< 0.900$, automatically trigger a feature-by-feature ablation audit and drop any leaking column until Test 2 and Test 3 both pass.

---

## PART 2: THE PRO BETTOR & ML ARCHITECT'S BLUEPRINT FOR REAL-WORLD PROFIT

To make actual money in football markets, you must understand how sharp betting syndicates operate:
1. **You Are Betting Against the Market Price, Not Predicting Winner Labels:** A team with a $70\%$ win probability priced at `1.30` odds ($76.9\%$ implied probability) is a **losing bet**. A team with a $42\%$ win probability priced at `2.65` odds ($37.7\%$ implied probability) is a **highly profitable bet** ($EV = 0.42 \times 2.65 - 1 = +11.3\%$).
2. **Why Raw Formations, News, and Player Profiles Fail When Fed Naively—And How to Engineer Them Properly:**
   - **Formations:** Feeding strings like `"4-3-3"` vs `"4-2-3-1"` into XGBoost creates noise because formations morph in-game. Instead, we engineer **Structural Tactical Archetypes** (Back-3 Wingback vs. Back-4 Wide vs. Low-Block Counter) and **Style Interaction Differentials** (Pressing Intensity vs. Build-Up Resistance, Shot Quality per Possession).
   - **Player Profiles & Lineups:** Feeding 22 player IDs causes severe overfitting. Instead, we compute a unified **Player Value-Added per 90 ($\text{PVA}_{90}$)** metric for every squad member and compress the confirmed/projected Starting XI into **Lineup Strength Delta Features** (Active XI Rating vs. Optimal 10-Match XI Rating, Primary Goalkeeper Absence Flag, Top Goal-Threat Absence Flag, Defensive Unit Continuity).
   - **News & Injury Intelligence:** LLMs are terrible at guessing match probabilities directly, and historical news scraping suffers from post-match editing bias. The syndicate solution is a **Two-Stage Hybrid Architecture**:
     1. **In Historical Training:** Use **Opening-to-Closing Pinnacle Line Steam ($\Delta P_{\text{steam}}$)** and **Match-to-Match Lineup Turnover** to teach the ML model how pre-match information shocks shift probabilities.
     2. **In Live Pre-Match Inference:** Use an automated **Structured News & Injury Extractor** (RSS/API-Football/Web Scraper -> Local LLM on RTX 3050 or NLP Rule Engine) that outputs a strict **Pre-Match Shock JSON** (late key injury, Champions League rotation risk, manager sacking, squad crisis) which applies a mathematically bounded **Bayesian Expected Goals Adjustment ($\Delta \lambda_H, \Delta \lambda_A$)** to the model's baseline forecast.

---

## PART 3: UPGRADED REPOSITORY ARCHITECTURE (V2)

Upgrade the existing repository to include these new modules:

```text
football-prediction-ai/
├── config/
│   └── config.yaml                          # Updated with xG, lineup, tactical, news & Kelly parameters
├── data/
│   ├── raw/
│   │   ├── football_data/                   # 6 seasons of match stats + Bet365 & Pinnacle Opening/Closing odds
│   │   ├── understat_xg/                    # Match & team shot-quality xG / npxG / PPDA / Deep completions
│   │   ├── club_elo/                        # Daily historical ClubElo ratings (cross-league European strength)
│   │   └── player_lineups/                  # Squad player ratings & historical/live starting XI caches
│   ├── processed/
│   │   └── features_v2_leakfree.parquet     # Audited, 100% leak-free feature matrix
│   └── live_ledger/
│       └── paper_trading.sqlite             # Immutable SQLite database for live pre-kickoff predictions & CLV
├── src/
│   ├── data/
│   │   ├── load_data.py                     # Football-Data.co.uk + Opening & Closing Pinnacle/B365 odds
│   │   ├── enrich_xg_elo.py                 # NEW: Fetches Understat xG/PPDA & ClubElo via soccerdata / HTTP
│   │   └── validate_data.py                 # Canonical team names across Football-Data, Understat, and ClubElo
│   ├── features/
│   │   ├── elo_pi_ratings.py                # Audited strictly pre-match Dynamic Elo + Pi-Ratings
│   │   ├── poisson_dixon_coles.py           # Time-decayed Dixon-Coles fitted strictly on Date < kickoff
│   │   ├── tactical_formations.py           # NEW: Formation archetypes, pressing/tempo vectors & style matchups
│   │   ├── player_lineup_engine.py          # NEW: Player PVA_90 ratings & Starting XI vs. Optimal XI deltas
│   │   ├── news_shock_extractor.py          # NEW: Live RSS/Injury scraper -> Structured JSON Shock -> Bayesian Lambda adj
│   │   └── build_features.py                # Master leak-free feature builder passing Target-Row Blindfold Test
│   ├── models/
│   │   ├── shin_margin.py                   # NEW: Shin's method & Power method for exact fair market probabilities
│   │   ├── baselines.py                     # 4 mandatory baselines + Pinnacle Opening & Closing benchmarks
│   │   ├── train.py                         # GPU XGBoost, LightGBM, CatBoost, Logistic + Out-of-Fold Calibration
│   │   └── predict.py                       # Unified inference engine accepting (Fixture + Lineup + News + Live Odds)
│   └── evaluation/
│       ├── audit_leakage.py                 # NEW: Automated feature ablation & permutation importance auditor
│       ├── evaluate.py                      # Honest metrics, ECE, Calibration curves, League breakdowns
│       ├── ticket_simulator.py              # Quarter-Kelly sizing, correlation-aware tickets, Monte Carlo drawdown
│       └── live_clv_tracker.py              # NEW: Real-world forward-testing ledger & Closing Line Value (CLV) grader
├── tests/
│   ├── test_data.py
│   ├── test_no_leakage.py
│   └── test_intra_row_and_temporal_leakage.py # NEW: Blindfold target-row test + realistic Log Loss bounds test
├── reports/
│   ├── v1_leakage_postmortem.md             # NEW: Explains exactly what leaked in V1 and how V2 fixed it
│   ├── evaluation_v2.md                     # Complete V2 evaluation report
│   └── figures/
└── app.py                                   # Upgraded 5-Tab Streamlit Syndicate Terminal
```

---

## PART 4: DETAILED IMPLEMENTATION STEPS FOR NEW CAPABILITIES

### STEP 1: Deep Data Enrichment (`src/data/enrich_xg_elo.py`)
1. **Pinnacle Opening vs. Closing Odds Extraction (`Football-Data.co.uk`):**
   - Extract both **Opening Odds** (`B365H`, `B365D`, `B365A`, `PSH`, `PSD`, `PSA`, `B365>2.5`, `P>2.5`) and **Closing Odds** (`B365CH`, `B365CD`, `B365CA`, `PSCH`, `PSCD`, `PSCA`, `B365C>2.5`, `PC>2.5`).
   - Implement **Shin's Margin Removal (`src/models/shin_margin.py`)** to convert both Opening and Closing odds into true fair probabilities:
     - `Open_Fair_Prob_H/D/A` (Available 48–72 hours before kickoff — **allowed in Track B features**).
     - `Close_Fair_Prob_H/D/A` (Final market price at kickoff — **used to measure Closing Line Value (CLV) and Market Steam**).
2. **Understat Expected Goals ($xG$) & ClubElo Integration:**
   - Install/use `soccerdata` or direct async HTTP fetchers to pull Understat match-level `xG`, `npxG` (non-penalty xG), `deep` (completions within 20 yards of goal), and `ppda` (pressing intensity) for the Top 5 leagues across `2019/20`–`2024/25`.
   - Fetch historical team ratings from `http://api.clubelo.com/{Team}` (which accounts for Champions League / Europa League cross-border matches).
   - *Resilience Fallback:* If any external endpoint rate-limits or fails for a subset of rows, build a calibrated **Shot-Quality Expected Goals Estimator** trained on `(HST, HS - HST, Corners, Big_Chance_Proxy, Home/Away, Elo_Diff)` so `100%` of the 10,707 matches have non-null pre-match `xG` and `npxG` rolling features.

### STEP 2: Tactical Formations & Style Interaction Engine (`src/features/tactical_formations.py`)
Instead of treating formations as arbitrary text labels, build a quantitative tactical profiler for every team prior to kickoff using only past matches:
1. **Tactical Style Vectors (Rolling 5 & 15 Match Windows, Shifted by 1):**
   - `Directness_Index`: Ratio of shots and corners generated per foul/possession proxy.
   - `Shot_Accuracy_Discipline`: $\frac{\text{SOTF}}{\text{SF}}$ (measures whether a team takes high-probability box shots or wasteful long shots).
   - `Defensive_Block_Compactness`: Opponent shots on target allowed per total opponent shots ($\frac{\text{SOTA}}{\text{SA}}$).
   - `Second_Half_Tactical_Adaptability`: Rolling difference between 2nd-half goal difference and 1st-half goal difference ($\Delta \text{GD}_{2H - 1H}$).
   - `Game_State_Resilience`: Points recovered from losing at half-time (`HTR == 'A'` for Home or `'H'` for Away) and lead protection rate when leading at half-time.
2. **Formation & Tactical Archetype Matchup Features:**
   - Classify each team's prevailing tactical profile (or explicit formation input `[4-3-3, 4-2-3-1, 3-5-2, 3-4-2-1, 4-4-2, 5-3-2]` when provided in live mode) into three tactical dimensions:
     - `Width_Bias` $\in [-1, 1]$ (Wing/Crossing heavy vs. Central progression)
     - `Line_Height_Press` $\in [-1, 1]$ (High press vs. Low block)
     - `Transition_Speed` $\in [-1, 1]$ (Fast counter-attack vs. Slow control)
   - Compute **Tactical Mismatch Interaction Terms**:
     - `Counter_Attack_Vulnerability`: $\text{Home\_Line\_Height} \times \text{Away\_Transition\_Speed}$ (High-line teams struggle against clinical counter-attacking away teams—a classic source of away upsets!).
     - `Set_Piece_Mismatch`: $\text{Home\_Corner\_Dominance} \times \text{Away\_Foul\_Concession\_Rate}$.

### STEP 3: Player Profiles & Starting XI Impact Engine (`src/features/player_lineup_engine.py`)
Build a module that evaluates squad availability and Starting XI strength both historically and for live pre-match lineups:
1. **Player Value-Added Rating ($\text{PVA}_{90}$):**
   - Define a standardized schema for squad players (`player_id`, `team`, `position` $\in \{\text{GK, DEF, MID, FWD}\}$, `minutes_played`, `npxg_per90`, `xa_per90`, `prog_actions_per90`, `def_impact_per90`, `is_starter_regular`).
   - Compute a single composite **Player Impact Score ($\text{PIS} \in [0.0, 10.0]$)** weighted by position.
2. **Pre-Match Lineup Delta Features:**
   - When a confirmed or projected 11-player lineup is passed (via live API/UI or squad availability data):
     - `Active_XI_Strength_Ratio`: $\frac{\sum_{p \in \text{Starting11}} \text{PIS}_p}{\sum_{p \in \text{Optimal11}} \text{PIS}_p}$
     - `Attack_Threat_Retention`: Fraction of the team's rolling 10-match $xG + xA$ currently on the pitch in the Starting XI.
     - `Primary_GK_Missing_Flag`: `1` if the team's primary goalkeeper is out, else `0`.
     - `Squad_Fatigue_Load`: Fixture congestion interaction ($\text{Matches in last 14 days} \times (1 - \text{Squad\_Depth\_Factor})$).

### STEP 4: Real-Time News, Injury & Press Conference AI Pipeline (`src/features/news_shock_extractor.py`)
Create a production pipeline that ingests pre-match text (RSS feeds from BBC Sport, SkySports, Guardian Football, official injury tables, or user-pasted match preview notes) and converts them into **structured numerical adjustments**:
1. **Automated Pre-Match Text Fetcher:**
   - Query public RSS feeds and football news headlines for `"{HomeTeam}"` and `"{AwayTeam}"` within the last 72 hours.
2. **Structured AI / NLP Extraction (Local LLM via Ollama/Transformers on RTX 3050 OR Deterministic Keyword-Entity Parser Fallback):**
   - Extract a strict, validated `Pydantic` / JSON schema for each team:
     ```json
     {
       "team": "Arsenal",
       "key_starters_ruled_out_count": 1,
       "key_player_positions_out": ["FWD"],
       "primary_gk_out": false,
       "european_cup_rotation_risk": 0.25,
       "manager_change_within_14d": false,
       "squad_morale_or_disciplinary_crisis": false,
       "weather_pitch_severity": 0.0,
       "confidence_of_report": 0.85
     }
     ```
3. **Bayesian Expected Goals ($\lambda$) Adjustment Formula:**
   - Never let raw text override the statistical model wildly. Apply bounded, domain-calibrated multipliers to the Dixon-Coles expected goals ($\lambda_H, \lambda_A$):
     $$\lambda_{\text{adj}} = \lambda_{\text{base}} \times (1 - 0.06 \cdot N_{\text{key\_fwd\_out}}) \times (1 - 0.08 \cdot \text{RotationRisk})$$
     $$\lambda_{\text{opponent\_adj}} = \lambda_{\text{opponent\_base}} \times (1 + 0.05 \cdot N_{\text{key\_def\_out}}) \times (1 + 0.09 \cdot \mathbb{I}_{\text{GK\_out}})$$
   - Re-compute the $8 \times 8$ Dixon-Coles scoreline matrix from $(\lambda_{H,\text{adj}}, \lambda_{A,\text{adj}})$ and blend with the ML ensemble probabilities!

---

## PART 5: MODEL TRAINING, CALIBRATION & REAL-WORLD LIVE TESTING PROTOCOL

### 1. Strict Three-Track Modeling Architecture (`src/models/train.py`)
Train and evaluate three distinct tracks using **Monthly Walk-Forward Expanding Windows** across the `2024/25` test set (`1,752` matches):
- **Track A (Pure Football Fundamentals — No Odds):** Audited leak-free Elo, Pi-Ratings, pre-match Dixon-Coles $\lambda$, Understat $xG$/$npxG$ overperformance regression, tactical style matchups, rest/congestion, and multi-window rolling form (3/5/10/20).
- **Track B (Early-Market Hybrid — Opening Odds + Fundamentals):** Track A features + Shin-devigged **Opening Odds** (`Open_Fair_Prob_H/D/A`) + Model-vs-Opening Divergence ($\text{TrackA\_Prob} - \text{Open\_Fair\_Prob}$). *Simulates placing bets 24–48 hours before kickoff.*
- **Track C (Late-Market Syndicate Engine — Lineups + News Shock + Steam):** Track B + Lineup Deltas + Opening-to-Closing Steam Indicators. *Simulates placing bets 30–60 minutes before kickoff after lineups drop.*

### 2. Probability Calibration & Overfitting Prevention
- Constrain tree depth (`max_depth=3..5`, `min_child_weight=30`, `subsample=0.8`, `colsample_bytree=0.7`) on `XGBoost` (GPU), `LightGBM`, and `CatBoost`.
- Calibrate probabilities strictly on the chronological `Validation` split (`2024-01-01` to `2024-05-31`) using **Temperature Scaling / Dirichlet Calibration** and **Sigmoid Calibration**, selecting whichever achieves the lowest Validation Log Loss and Expected Calibration Error (`ECE`).

### 3. The Real-World Litmus Test: Closing Line Value (CLV) & Quarter-Kelly Backtester (`src/evaluation/`)
In `src/evaluation/ticket_simulator.py` and `live_clv_tracker.py`, implement the exact metrics professional syndicates use to verify if a bot can win real money:
1. **Closing Line Value (CLV %) Verification:**
   - When the model selects a bet against the **Opening Odds** ($O_{\text{open}}$), compare that price against the **Pinnacle Closing Fair Probability** ($P_{\text{close\_fair}}$):
     $$\text{CLV} = (O_{\text{open}} \times P_{\text{close\_fair}}) - 1$$
   - Report the **% of Bets That Beat the Closing Line** and **Average CLV %** across the `2024/25` test set.
2. **Actionable High-Win-Rate Tier vs. Pure +EV Tier:**
   - **High-Probability Anchor Tier (Target $\ge 55\%–62\%$ Hit Rate):** Selections where calibrated $P_{\text{model}} \ge 0.56$, ensemble standard deviation $< 0.035$, and $EV = (P_{\text{model}} \times O_{\text{market}}) - 1 > +1.5\%$.
   - **Value Sniper Tier (+EV All Ranges):** Selections where $EV > +3.5\%$ and Model-vs-Market divergence is backed by $xG$ regression (e.g., fading a team that overperformed its $xG$ by $+3.0$ goals over the last 5 games).
3. **Bankroll Risk Management (Quarter-Kelly + Correlation Filter):**
   - Implement **0.25x Fractional Kelly Staking** capped at `2.0%` max stake per single match.
   - For **2-Leg and 3-Leg Tickets**, strictly forbid combining two markets from the same match (unless priced via the joint Dixon-Coles scoreline matrix) and cap ticket stakes at `0.5%–1.0%` of bankroll.
   - Run a **10,000-Path Monte Carlo Simulation** to report **95% Confidence Interval ROI**, **Max Drawdown (%)**, and **Risk of Ruin (%)**.

### 4. Upgraded 5-Tab Interactive Streamlit Syndicate Terminal (`app.py`)
Upgrade `app.py` into a full decision-support workstation with 5 tabs:
- **Tab 1 — Live Match & Lineup/News Simulator:** Select League, Home Team, Away Team, enter current bookmaker odds, toggle **Tactical Formations (`4-3-3`, `3-5-2`, etc.)**, mark **Key Players/GK Out**, or fetch/paste **Pre-Match News Headlines** to see real-time adjustments to `1X2`, `Over/Under 2.5`, `BTTS`, `Expected Goals`, `Top 3 Scorelines`, `EV %`, and `Quarter-Kelly Stake`.
- **Tab 2 — Weekend High-Confidence & +EV Ticket Builder:** Automatically scans upcoming or test fixtures, filters for the **$\ge 55\%$ High-Confidence Anchor Legs** and **+EV Value Legs**, and builds optimal single bets and 2-leg/3-leg tickets with compounded margin warnings.
- **Tab 3 — V1 vs. V2 Leakage Audit & Honest Model Scoreboard:** Shows the forensic post-mortem, permutation importances, calibration curves, confusion matrices, and league-by-league performance for Track A, Track B, and Track C.
- **Tab 4 — Bankroll & Monte Carlo Stress Tester:** Interactive equity curves, drawdown distributions, and threshold sliders ($\tau_{\text{prob}}, \tau_{\text{ev}}$).
- **Tab 5 — Live Forward-Testing & CLV Ledger:** Allows the user to click **"Lock Prediction into Live SQLite Ledger"** before kickoff and tracks real-world forward-tested Hit Rate, ROI, and Closing Line Value over time.

---

## PART 6: FINAL ACCEPTANCE CHECKLIST BEFORE COMPLETION

Do not finish until every item below is verified by execution:
1. `pytest tests/` passes **100% of tests**, including the new **`test_intra_row_and_temporal_leakage.py` (Target-Row Blindfold Test)**.
2. `reports/v1_leakage_postmortem.md` is generated, naming the exact column(s) or function(s) that caused the fake `0.8369` Log Loss in V1 and proving their removal.
3. `reports/evaluation_v2.md` is generated with **100% real, leak-free metrics** on the 1,752 untouched `2024/25` test matches across Track A, Track B, Track C, and all Baselines, plus **CLV %**, **High-Confidence Tier Hit Rate ($\ge 55\%$)**, and **Monte Carlo Drawdown stats**.
4. `src/features/tactical_formations.py`, `src/features/player_lineup_engine.py`, `src/features/news_shock_extractor.py`, and `src/evaluation/live_clv_tracker.py` are implemented, tested, and wired into `src/models/predict.py` and `app.py`.
5. `README.md` is updated with the V2 Executive Summary and exact commands to launch the Streamlit terminal and live paper-trading tracker.

**BEGIN EXECUTION IMMEDIATELY WITH PART 1: RUN THE FORENSIC FEATURE IMPORTANCE AUDIT ON `models/track_a_bundle.joblib` AND `src/features/build_features.py` TO EXPOSE AND FIX THE V1 LEAKAGE.**