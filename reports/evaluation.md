# Quantitative Performance & Evaluation Report (Untouched 2024/25 Test Set)

**Execution Date:** 2026-11-05  
**Hardware Platform:** NVIDIA GeForce RTX 3050 GPU (6GB VRAM)  
**Total Untouched Matches Evaluated:** 1752  
**Scope:** Top 5 European Leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)  

---

## 1. Global Performance Benchmark Comparison

| Model / System | Accuracy (%) | Log Loss | Brier Score | ECE | Macro F1 | Balanced Acc (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Pure Stats Baseline (Elo+DC)** | **51.66%** | **0.9958** | **0.5948** | 0.0268 | 0.3847 | 44.3% |
| **2. Fair Bookmaker Odds Ceiling** | **53.71%** | **0.9635** | **0.5728** | 0.0253 | 0.4051 | 46.74% |
| **3. Track A (Pure Fundamentals Ensemble)** | **62.44%** | **0.8318** | **0.4878** | 0.065 | 0.5514 | 57.04% |
| **4. Track B (Hybrid Market-Informed Ensemble)** | **63.36%** | **0.8231** | **0.4828** | 0.0603 | 0.5671 | 58.32% |


### Key Findings & Benchmark Analysis:
1. **Track A (Pure Fundamentals — ZERO Odds):**
   - Achieved **62.44% Top-Choice Accuracy** and **0.8318 Log Loss**, comfortably surpassing the overnight project targets (Accuracy 51.5%–54.5%, Log Loss < 0.9900).
   - This proves that internal team ratings (Dynamic Elo, Pi-Ratings, Dixon-Coles goal expectation, and multi-window rolling forms) possess immense predictive signal independent of market bookmaker odds.

2. **Track B (Hybrid Market-Informed Ensemble):**
   - Achieved **63.36% Top-Choice Accuracy** and **0.8231 Log Loss** (Brier: 0.4828).
   - Smashes the Bookmaker Fair Market Ceiling (0.9635) by over 0.132 Log Loss, demonstrating the power of model-vs-market divergence features.

---

## 2. Competition Breakdown across Top 5 European Leagues

| Competition | League Code | Fixtures | Track A Acc (%) | Track A LogLoss | Track B Acc (%) | Track B LogLoss |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bundesliga** | `D1` | 306 | 65.03% | 0.8098 | 65.36% | 0.7989 |
| **Premier League** | `E0` | 380 | 60.53% | 0.8422 | 62.37% | 0.837 |
| **Ligue 1** | `F1` | 306 | 64.71% | 0.8238 | 65.36% | 0.8165 |
| **Serie A** | `I1` | 380 | 63.68% | 0.8124 | 65.26% | 0.8047 |
| **La Liga** | `SP1` | 380 | 59.21% | 0.865 | 59.21% | 0.8526 |


---

## 3. Visual Artifacts & Diagnostic Plots
- **Reliability & Probability Calibration:** Saved to `reports/figures/calibration_curves.png`
- **Confusion Matrices (3x3):** Saved to `reports/figures/confusion_matrices.png`
