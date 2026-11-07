"""
Multi-Market Probabilistic Engine & Safest Picks Ranker.
Computes calibrated win probabilities across:
- Double Chance (1X, X2, 12)
- Over / Under Goal Totals (Over 1.5, Under 3.5, Over 2.5, Under 2.5)
- Both Teams to Score (BTTS Yes, BTTS No)
- Total Corners Over / Under (Over 8.5, Over 9.5)
- Draw No Bet (Home DNB, Away DNB)
- Team Total Goals (Over 1.5 Team Goals)
- First Half Goals (1st Half Over 0.5 Goals)
- Win to Nil / Clean Sheets
- Win Either Half

Ranks and extracts the Top 3 Safest Picks and Alternative Smart Bet Ideas with exact percentages.
"""
import math
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from src.models.cards_model import YellowCardsEngine

def poisson_pmf(k: int, lamb: float) -> float:
    """Computes Poisson probability P(X = k; lambda)."""
    if lamb <= 0:
        return 1.0 if k == 0 else 0.0
    return (lamb ** k) * math.exp(-lamb) / math.factorial(k)

def compute_scoreline_matrix(lambda_h: float, lambda_a: float, max_goals: int = 8, rho: float = -0.11) -> np.ndarray:
    """
    Computes bivariate Dixon-Coles scoreline probability matrix.
    Applies the tau(rho) low-score correlation adjustment for (0,0), (0,1), (1,0), (1,1)
    to eliminate naive Poisson independence distortions on low scorelines.
    """
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h in range(max_goals + 1):
        p_h = poisson_pmf(h, lambda_h)
        for a in range(max_goals + 1):
            p_a = poisson_pmf(a, lambda_a)
            matrix[h, a] = p_h * p_a

    # Dixon-Coles tau adjustment for low scores
    # tau(0,0) = 1 - lambda_h * lambda_a * rho
    # tau(0,1) = 1 + lambda_h * rho
    # tau(1,0) = 1 + lambda_a * rho
    # tau(1,1) = 1 - rho
    matrix[0, 0] = max(0.0, matrix[0, 0] * (1.0 - lambda_h * lambda_a * rho))
    matrix[0, 1] = max(0.0, matrix[0, 1] * (1.0 + lambda_h * rho))
    matrix[1, 0] = max(0.0, matrix[1, 0] * (1.0 + lambda_a * rho))
    matrix[1, 1] = max(0.0, matrix[1, 1] * (1.0 - rho))

    s = matrix.sum()
    if s > 0:
        matrix /= s
    return matrix

def calculate_corner_probabilities(lambda_h: float, lambda_a: float, total_corners_base: float = 9.8) -> Dict[str, float]:
    """Estimates match corner count using attacking intensity from expected goals."""
    intensity = (lambda_h + lambda_a) / 2.7
    lambda_corners = total_corners_base * np.clip(0.85 + 0.15 * intensity, 0.85, 1.25)
    
    p_cum = sum(poisson_pmf(k, lambda_corners) for k in range(9))
    p_over_85 = float(np.clip(1.0 - p_cum, 0.05, 0.95))
    
    p_cum_9 = p_cum + poisson_pmf(9, lambda_corners)
    p_over_95 = float(np.clip(1.0 - p_cum_9, 0.05, 0.95))
    
    return {
        "lambda_corners": round(float(lambda_corners), 2),
        "over_8_5": round(p_over_85 * 100.0, 1),
        "under_8_5": round((1.0 - p_over_85) * 100.0, 1),
        "over_9_5": round(p_over_95 * 100.0, 1),
        "under_9_5": round((1.0 - p_over_95) * 100.0, 1)
    }

def compute_all_market_probabilities(
    home_team: str,
    away_team: str,
    p_home: float,
    p_draw: float,
    p_away: float,
    lambda_h: float,
    lambda_a: float,
    league: str = "E0",
    referee: Optional[str] = None,
    rho: float = -0.11
) -> Dict[str, Any]:
    """Calculates all bet types across 1X2, Double Chance, Goals, BTTS, Corners, Team Totals, Halves & Yellow Cards."""
    # Defensive normalization if probabilities were passed as percentages (0-100)
    if p_home > 1.0: p_home /= 100.0
    if p_draw > 1.0: p_draw /= 100.0
    if p_away > 1.0: p_away /= 100.0

    matrix = compute_scoreline_matrix(lambda_h, lambda_a, rho=rho)
    
    # Double Chance
    p_1x = p_home + p_draw
    p_x2 = p_draw + p_away
    p_12 = p_home + p_away
    
    # Total Goals
    p_under_15 = float(matrix[0, 0] + matrix[1, 0] + matrix[0, 1])
    p_over_15 = 1.0 - p_under_15
    
    p_under_25 = float(sum(matrix[h, a] for h in range(3) for a in range(3) if h + a <= 2))
    p_over_25 = 1.0 - p_under_25
    
    p_under_35 = float(sum(matrix[h, a] for h in range(4) for a in range(4) if h + a <= 3))
    p_over_35 = 1.0 - p_under_35

    p_under_45 = float(sum(matrix[h, a] for h in range(5) for a in range(5) if h + a <= 4))
    p_over_45 = 1.0 - p_under_45
    
    # BTTS
    p_btts_yes = float(sum(matrix[h, a] for h in range(1, 9) for a in range(1, 9)))
    p_btts_no = 1.0 - p_btts_yes
    
    # Corners
    corner_probs = calculate_corner_probabilities(lambda_h, lambda_a)
    
    # Draw No Bet
    sum_ha = p_home + p_away
    p_dnb_h = (p_home / sum_ha) if sum_ha > 0 else 0.50
    p_dnb_a = (p_away / sum_ha) if sum_ha > 0 else 0.50

    # Team Totals (Over 1.5 & Over 0.5 individual team goals)
    p_h_o15 = 1.0 - (poisson_pmf(0, lambda_h) + poisson_pmf(1, lambda_h))
    p_a_o15 = 1.0 - (poisson_pmf(0, lambda_a) + poisson_pmf(1, lambda_a))
    p_h_o05 = 1.0 - poisson_pmf(0, lambda_h)
    p_a_o05 = 1.0 - poisson_pmf(0, lambda_a)

    # 1st Half Over 0.5 Goals (~45% of total xG happens in 1st half)
    fh_xg = 0.45 * (lambda_h + lambda_a)
    p_fh_o05 = 1.0 - math.exp(-fh_xg)

    # Clean Sheets & Win to Nil
    p_h_cs = math.exp(-lambda_a)
    p_a_cs = math.exp(-lambda_h)
    p_h_wtn = (1.0 - math.exp(-lambda_h)) * p_h_cs
    p_a_wtn = (1.0 - math.exp(-lambda_a)) * p_a_cs

    # Win Either Half
    p_h_weh = 1.0 - (1.0 - 0.70 * (p_home / 100.0)) ** 2
    p_a_weh = 1.0 - (1.0 - 0.70 * (p_away / 100.0)) ** 2

    return {
        "double_chance": {
            "1X": round(p_1x * 100.0, 1),
            "X2": round(p_x2 * 100.0, 1),
            "12": round(p_12 * 100.0, 1)
        },
        "totals": {
            "over_1_5": round(p_over_15 * 100.0, 1),
            "under_1_5": round(p_under_15 * 100.0, 1),
            "over_2_5": round(p_over_25 * 100.0, 1),
            "under_2_5": round(p_under_25 * 100.0, 1),
            "over_3_5": round(p_over_35 * 100.0, 1),
            "under_3_5": round(p_under_35 * 100.0, 1),
            "over_4_5": round(p_over_45 * 100.0, 1),
            "under_4_5": round(p_under_45 * 100.0, 1)
        },
        "team_totals": {
            "home_over_15": round(p_h_o15 * 100.0, 1),
            "away_over_15": round(p_a_o15 * 100.0, 1),
            "home_over_05": round(p_h_o05 * 100.0, 1),
            "away_over_05": round(p_a_o05 * 100.0, 1)
        },
        "first_half": {
            "over_05": round(p_fh_o05 * 100.0, 1),
            "under_05": round((1.0 - p_fh_o05) * 100.0, 1)
        },
        "clean_sheets": {
            "home_clean_sheet": round(p_h_cs * 100.0, 1),
            "away_clean_sheet": round(p_a_cs * 100.0, 1),
            "home_win_to_nil": round(p_h_wtn * 100.0, 1),
            "away_win_to_nil": round(p_a_wtn * 100.0, 1)
        },
        "win_either_half": {
            "home": round(p_h_weh * 100.0, 1),
            "away": round(p_a_weh * 100.0, 1)
        },
        "btts": {
            "yes": round(p_btts_yes * 100.0, 1),
            "no": round(p_btts_no * 100.0, 1)
        },
        "corners": corner_probs,
        "draw_no_bet": {
            "home_dnb": round(p_dnb_h * 100.0, 1),
            "away_dnb": round(p_dnb_a * 100.0, 1)
        },
        "yellow_cards": YellowCardsEngine.get_instance().predict_yellow_cards(home_team, away_team, league=league, referee=referee)
    }

def get_alternative_bet_ideas(
    home_team: str,
    away_team: str,
    p_home: float,
    p_draw: float,
    p_away: float,
    lambda_h: float,
    lambda_a: float,
    league: str = "E0",
    referee: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Generates creative alternative betting ideas beyond basic 1X2 picks."""
    m = compute_all_market_probabilities(home_team, away_team, p_home, p_draw, p_away, lambda_h, lambda_a, league=league, referee=referee)
    ideas = []

    # 1. First Half Over 0.5 Goals (Banker)
    p_fh = m["first_half"]["over_05"]
    if p_fh >= 75.0:
        ideas.append({
            "title": "1st Half Over 0.5 Goals",
            "category": "⏱️ Half-Time Markets",
            "win_pct": p_fh,
            "fair_odds": round(100.0 / p_fh, 2),
            "badge": "🟢 High Liquidity / Banker",
            "reason": f"Combined first half expected goals is {0.45*(lambda_h+lambda_a):.2f}. High early tempo makes a goal before the break {p_fh}% probable."
        })

    # 2. Team Total Goals (Favorite Over 1.5 Team Goals)
    if lambda_h >= 1.70:
        p_to15 = m["team_totals"]["home_over_15"]
        ideas.append({
            "title": f"{home_team} Over 1.5 Team Goals",
            "category": "⚽ Team Totals",
            "win_pct": p_to15,
            "fair_odds": round(100.0 / p_to15, 2),
            "badge": "🔥 Offense Specialist",
            "reason": f"{home_team} carries an individual expected goals (xG) of {lambda_h:.2f}. Even if they draw 2-2, this bet wins."
        })
    elif lambda_a >= 1.70:
        p_to15 = m["team_totals"]["away_over_15"]
        ideas.append({
            "title": f"{away_team} Over 1.5 Team Goals",
            "category": "⚽ Team Totals",
            "win_pct": p_to15,
            "fair_odds": round(100.0 / p_to15, 2),
            "badge": "🔥 Offense Specialist",
            "reason": f"{away_team} carries an individual expected goals (xG) of {lambda_a:.2f}. High chance of netting 2 or more."
        })

    # 3. Win Either Half (Safer than full 90m)
    if p_home >= 60.0:
        p_weh = m["win_either_half"]["home"]
        ideas.append({
            "title": f"{home_team} to Win Either Half",
            "category": "🛡️ Half Coverage",
            "win_pct": p_weh,
            "fair_odds": round(100.0 / p_weh, 2),
            "badge": "💎 Smart Hedge",
            "reason": f"{home_team} only needs to outscore their opponent in either the 1st or 2nd 45 minutes."
        })
    elif p_away >= 60.0:
        p_weh = m["win_either_half"]["away"]
        ideas.append({
            "title": f"{away_team} to Win Either Half",
            "category": "🛡️ Half Coverage",
            "win_pct": p_weh,
            "fair_odds": round(100.0 / p_weh, 2),
            "badge": "💎 Smart Hedge",
            "reason": f"{away_team} only needs to outscore their opponent in either the 1st or 2nd 45 minutes."
        })

    # 4. Clean Sheet / Win to Nil
    if lambda_a <= 0.70 and p_home >= 65.0:
        p_wtn = m["clean_sheets"]["home_win_to_nil"]
        ideas.append({
            "title": f"{home_team} to Win to Nil (Clean Sheet Win)",
            "category": "🏰 Defensive Dominance",
            "win_pct": p_wtn,
            "fair_odds": round(100.0 / max(5.0, p_wtn), 2),
            "badge": "📈 High Payout Edge",
            "reason": f"{away_team}'s attacking expectation is suppressed to {lambda_a:.2f} xG against a rock-solid defense."
        })

    # 5. Asian Handicap
    if p_home >= 70.0:
        ideas.append({
            "title": f"{home_team} -1.5 Asian Handicap",
            "category": "🎯 Asian Handicap",
            "win_pct": round(m["team_totals"]["home_over_15"] * 0.82, 1),
            "fair_odds": round(100.0 / max(5.0, m["team_totals"]["home_over_15"] * 0.82), 2),
            "badge": "⚡ Multi-Goal Blowout",
            "reason": f"{home_team} is projected to win by 2 or more goals against a bottom-half opponent."
        })

    # 6. Discipline & Yellow Cards Special
    cards_info = m.get("yellow_cards", {})
    best_c = cards_info.get("best_card_bet")
    if best_c and best_c["win_percentage"] >= 65.0:
        ideas.append({
            "title": best_c["pick_type"],
            "category": "🟨 Yellow Cards Market",
            "win_pct": best_c["win_percentage"],
            "fair_odds": best_c["fair_odds"],
            "badge": best_c["safety_badge"],
            "reason": best_c["rationale"]
        })

    return ideas[:5]

def get_top_3_safest_picks(
    home_team: str,
    away_team: str,
    p_home: float,
    p_draw: float,
    p_away: float,
    lambda_h: float,
    lambda_a: float,
    league: str = "E0",
    referee: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Analyzes all available betting markets and returns the TOP 3 SAFEST PICKS."""
    all_markets = compute_all_market_probabilities(home_team, away_team, p_home, p_draw, p_away, lambda_h, lambda_a, league=league, referee=referee)
    candidates = []

    # 1. Double Chance Home or Draw (1X)
    p_1x = all_markets["double_chance"]["1X"]
    if p_1x >= 60.0:
        candidates.append({
            "pick_type": f"Double Chance: {home_team} or Draw (1X)",
            "market_category": "Double Chance",
            "win_percentage": p_1x,
            "fair_odds": round(100.0 / p_1x, 2),
            "safety_badge": "🟢 Ultra Safe" if p_1x >= 78.0 else "🟡 Very Safe",
            "why_plain_english": f"{home_team} only needs to avoid defeat on home ground. The model gives an {p_1x}% chance of a home win or draw based on defensive ratings and home advantage."
        })

    # 2. Double Chance Away or Draw (X2)
    p_x2 = all_markets["double_chance"]["X2"]
    if p_x2 >= 60.0:
        candidates.append({
            "pick_type": f"Double Chance: {away_team} or Draw (X2)",
            "market_category": "Double Chance",
            "win_percentage": p_x2,
            "fair_odds": round(100.0 / p_x2, 2),
            "safety_badge": "🟢 Ultra Safe" if p_x2 >= 78.0 else "🟡 Very Safe",
            "why_plain_english": f"{away_team} is projected to dominate possession and chances away from home. Model predicts {p_x2}% probability of getting at least a point."
        })

    # 3. 1st Half Over 0.5 Goals
    p_fh = all_markets["first_half"]["over_05"]
    if p_fh >= 76.0:
        candidates.append({
            "pick_type": "1st Half Over 0.5 Goals",
            "market_category": "Half Totals",
            "win_percentage": p_fh,
            "fair_odds": round(100.0 / p_fh, 2),
            "safety_badge": "🟢 Ultra Safe" if p_fh >= 80.0 else "🟡 Very Safe",
            "why_plain_english": f"Requires just a single goal before half-time. Fast-tempo offensive match with {0.45*(lambda_h+lambda_a):.2f} first-half expected goals."
        })

    # 4. Over 1.5 Total Goals
    p_o15 = all_markets["totals"]["over_1_5"]
    if p_o15 >= 65.0:
        candidates.append({
            "pick_type": "Over 1.5 Total Match Goals",
            "market_category": "Goals Total",
            "win_percentage": p_o15,
            "fair_odds": round(100.0 / p_o15, 2),
            "safety_badge": "🟢 Ultra Safe" if p_o15 >= 78.0 else "🟡 Very Safe",
            "why_plain_english": f"Requires just 2 total goals scored in 90 minutes. With combined expected goals (xG) of {(lambda_h + lambda_a):.2f}, there is an {p_o15}% likelihood of 2+ goals."
        })

    # 5. Under 3.5 Total Goals
    p_u35 = all_markets["totals"]["under_3_5"]
    if p_u35 >= 68.0:
        candidates.append({
            "pick_type": "Under 3.5 Total Match Goals",
            "market_category": "Goals Total",
            "win_percentage": p_u35,
            "fair_odds": round(100.0 / p_u35, 2),
            "safety_badge": "🟢 Ultra Safe" if p_u35 >= 78.0 else "🟡 Very Safe",
            "why_plain_english": f"Game is protected as long as there are 3 goals or fewer. Total expected goals is {(lambda_h + lambda_a):.2f}."
        })

    # 5b. Under 4.5 Total Goals (Maximum Goals Ceiling)
    p_u45 = all_markets["totals"]["under_4_5"]
    if p_u45 >= 75.0:
        candidates.append({
            "pick_type": "Under 4.5 Total Match Goals",
            "market_category": "Goals Total",
            "win_percentage": p_u45,
            "fair_odds": round(100.0 / p_u45, 2),
            "safety_badge": "🟢 Ultra Safe" if p_u45 >= 82.0 else "🟡 Very Safe",
            "why_plain_english": f"Combined xG of {(lambda_h + lambda_a):.2f} keeps the total score under 5 goals with an {p_u45}% probability ceiling."
        })

    # 5c. Home Team to Score (Over 0.5 Team Goals)
    p_h_o05 = all_markets["team_totals"]["home_over_05"]
    if p_h_o05 >= 72.0:
        candidates.append({
            "pick_type": f"{home_team} to Score (Over 0.5 Team Goals)",
            "market_category": "Team Goals",
            "win_percentage": p_h_o05,
            "fair_odds": round(100.0 / p_h_o05, 2),
            "safety_badge": "🟢 Ultra Safe" if p_h_o05 >= 80.0 else "🟡 Very Safe",
            "why_plain_english": f"{home_team} has an expected goals rate of {lambda_h:.2f} xG, giving them an {p_h_o05}% likelihood of scoring at least 1 goal."
        })

    # 5d. Away Team to Score (Over 0.5 Team Goals)
    p_a_o05 = all_markets["team_totals"]["away_over_05"]
    if p_a_o05 >= 72.0:
        candidates.append({
            "pick_type": f"{away_team} to Score (Over 0.5 Team Goals)",
            "market_category": "Team Goals",
            "win_percentage": p_a_o05,
            "fair_odds": round(100.0 / p_a_o05, 2),
            "safety_badge": "🟢 Ultra Safe" if p_a_o05 >= 80.0 else "🟡 Very Safe",
            "why_plain_english": f"{away_team} has an expected goals rate of {lambda_a:.2f} xG, giving them an {p_a_o05}% likelihood of scoring at least 1 goal."
        })

    # 6. Over 8.5 Total Corners
    p_c85 = all_markets["corners"]["over_8_5"]
    if p_c85 >= 64.0:
        candidates.append({
            "pick_type": "Over 8.5 Total Corners",
            "market_category": "Corners",
            "win_percentage": p_c85,
            "fair_odds": round(100.0 / p_c85, 2),
            "safety_badge": "🟢 Ultra Safe" if p_c85 >= 75.0 else "🟡 Very Safe",
            "why_plain_english": f"Attacking intensity projects {all_markets['corners']['lambda_corners']} corners ({p_c85}% chance of 9+)."
        })

    # 7. Draw No Bet (Home DNB or Away DNB)
    p_dnb_h = all_markets["draw_no_bet"]["home_dnb"]
    if p_dnb_h >= 68.0:
        candidates.append({
            "pick_type": f"Draw No Bet: {home_team} (Home DNB)",
            "market_category": "Draw No Bet",
            "win_percentage": p_dnb_h,
            "fair_odds": round(100.0 / p_dnb_h, 2),
            "safety_badge": "🟢 Ultra Safe" if p_dnb_h >= 78.0 else "🟡 Very Safe",
            "why_plain_english": f"Stake is 100% refunded if the match ends in a draw! {home_team} wins in {p_dnb_h}% of non-draw outcomes."
        })
    p_dnb_a = all_markets["draw_no_bet"]["away_dnb"]
    if p_dnb_a >= 68.0:
        candidates.append({
            "pick_type": f"Draw No Bet: {away_team} (Away DNB)",
            "market_category": "Draw No Bet",
            "win_percentage": p_dnb_a,
            "fair_odds": round(100.0 / p_dnb_a, 2),
            "safety_badge": "🟢 Ultra Safe" if p_dnb_a >= 78.0 else "🟡 Very Safe",
            "why_plain_english": f"Stake is 100% refunded if the match ends in a draw! {away_team} wins in {p_dnb_a}% of non-draw outcomes."
        })

    # 8. Yellow Cards Market
    cards_info = all_markets.get("yellow_cards", {})
    best_c = cards_info.get("best_card_bet")
    if best_c and best_c.get("win_percentage", 0) >= 62.0:
        candidates.append({
            "pick_type": best_c["pick_type"],
            "market_category": "Yellow Cards",
            "win_percentage": best_c["win_percentage"],
            "fair_odds": best_c["fair_odds"],
            "safety_badge": "🟢 Ultra Safe" if best_c["win_percentage"] >= 78.0 else "🟡 Very Safe",
            "why_plain_english": best_c["rationale"]
        })
    c_probs = cards_info.get("probabilities", {})
    if c_probs.get("under_4_5", 0) >= 68.0:
        candidates.append({
            "pick_type": "Under 4.5 Total Yellow Cards",
            "market_category": "Yellow Cards",
            "win_percentage": c_probs["under_4_5"],
            "fair_odds": cards_info.get("fair_odds", {}).get("under_4_5", 1.45),
            "safety_badge": "🟢 Ultra Safe" if c_probs["under_4_5"] >= 78.0 else "🟡 Very Safe",
            "why_plain_english": f"Expected booking count is {cards_info.get('expected_total_cards', 3.8):.2f} cards. Low-friction disciplinary profile."
        })
    elif c_probs.get("over_3_5", 0) >= 68.0:
        candidates.append({
            "pick_type": "Over 3.5 Total Yellow Cards",
            "market_category": "Yellow Cards",
            "win_percentage": c_probs["over_3_5"],
            "fair_odds": cards_info.get("fair_odds", {}).get("over_3_5", 1.45),
            "safety_badge": "🟢 Ultra Safe" if c_probs["over_3_5"] >= 78.0 else "🟡 Very Safe",
            "why_plain_english": f"High tactical friction projects {cards_info.get('expected_total_cards', 4.5):.2f} total bookings ({c_probs['over_3_5']}% chance of 4+)."
        })

    # Sort descending by win percentage
    candidates = sorted(candidates, key=lambda x: x["win_percentage"], reverse=True)
    
    top_3 = []
    seen_categories = set()
    for c in candidates:
        if c["market_category"] not in seen_categories:
            top_3.append(c)
            seen_categories.add(c["market_category"])
            if len(top_3) == 3:
                break
                
    if len(top_3) < 3:
        for c in candidates:
            if c not in top_3:
                top_3.append(c)
                if len(top_3) == 3:
                    break
                    
    return top_3
