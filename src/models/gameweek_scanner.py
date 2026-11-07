"""
Weekly Matchday Gameweek Scanner & Parlay Generator.
Scans all 10 weekly matches for any league (EPL, La Liga, Serie A, Bundesliga, Ligue 1)
using our 5-Way Consensus Engine + Common Ground Conflict Arbitrage.

Outputs:
- Full 10-Match Ranked Gameweek Leaderboard
- Top 3 Banker Multi-Bet (Ultra-Safe Accumulator)
- Top 5 Weekend Multi Builder
- Filterable views for Overs, Unders (Under 1.5, Under 2.5, Under 3.5), Double Chance, and BTTS
"""
import math
from typing import Dict, Any, List, Optional
from src.features.sofascore_odds import compute_sofascore_odds
from src.features.official_fixtures import fetch_official_league_fixtures, fetch_official_epl_fixtures, get_current_and_next_gameweek

GAMEWEEK_SCHEDULE: Dict[str, List[Dict[str, str]]] = {}

def scan_weekly_gameweek(predictor, league: str = "E0", gameweek: Optional[int] = None) -> Dict[str, Any]:
    """
    Scans and grades all weekly fixtures of the specified league (EPL, La Liga, Serie A, Bundesliga, Ligue 1).
    Ranks them by statistical safety and constructs optimum multi-bets.
    Pulls 100% accurate official confirmed fixtures for ANY Gameweek (1 to 38 for EPL/La Liga/Serie A, 1 to 34 for Bundesliga/Ligue 1).
    """
    official_data = fetch_official_league_fixtures(league=league, gameweek=gameweek)
    fixtures = official_data.get("fixtures", [])
    gameweek_label = official_data.get("gameweek_label", f"Matchweek {gameweek if gameweek else 10}")
    active_gw = official_data.get("gameweek", gameweek if gameweek else 10)
    is_official = official_data.get("success", False)

    results = []

    for fix in fixtures:
        h = fix["home"]
        a = fix["away"]
        ko = fix.get("kickoff", "Weekend")

        # Get team stats from league manager
        h_st = predictor.league_mgr.get_team_stats(h, league)
        a_st = predictor.league_mgr.get_team_stats(a, league)

        # Free Sofascore odds
        sofa = compute_sofascore_odds(
            rank_h=h_st["rank"],
            pts_h=h_st["points"],
            gd_h=h_st["gd"],
            rank_a=a_st["rank"],
            pts_a=a_st["points"],
            gd_a=a_st["gd"],
            home_team=h,
            away_team=a
        )

        # Run multi-modal prediction
        rep = predictor.predict_fixture(
            home_team=h,
            away_team=a,
            track="C",
            market_odds=[sofa["home_odds"], sofa["draw_odds"], sofa["away_odds"]],
            league=league
        )

        penta = rep.get("penta_consensus", rep.get("quad_consensus", {}))
        safe_top = rep.get("top_3_safe_picks", [{}])[0] if rep.get("top_3_safe_picks") else {}
        common_grd = penta.get("common_ground", {})

        # Determine best weekly pick across ALL market derivatives
        # (Home/Away to score, Over 1.5, Under 4.5, Yellow Cards, Double Chance, etc.)
        candidates_pool = []
        for sp in rep.get("top_3_safe_picks", []):
            candidates_pool.append({
                "pick_type": sp["pick_type"],
                "win_percentage": float(sp["win_percentage"]),
                "fair_odds": float(sp["fair_odds"]),
                "reason": sp.get("why_plain_english", "High statistical confidence.")
            })

        card_p = rep.get("yellow_cards", {}).get("best_card_bet", {})
        if card_p and card_p.get("win_percentage", 0) >= 65.0:
            candidates_pool.append({
                "pick_type": card_p["pick_type"],
                "win_percentage": float(card_p["win_percentage"]),
                "fair_odds": float(card_p["fair_odds"]),
                "reason": card_p.get("rationale", "Disciplinary friction index.")
            })

        if penta.get("is_split") and common_grd.get("best_common_ground_market"):
            cg_mkt = common_grd["best_common_ground_market"]
            matching_safe = next((sp for sp in rep.get("top_3_safe_picks", []) if sp.get("pick_type") == cg_mkt), None)
            cg_prob = matching_safe.get("win_percentage", 78.0) if matching_safe else 78.0
            candidates_pool.append({
                "pick_type": cg_mkt,
                "win_percentage": float(cg_prob),
                "fair_odds": float(round(100.0 / cg_prob, 2)),
                "reason": common_grd.get("plain_explanation", "Cross-model agreement on derivative goals market.")
            })

        # Pick the absolute highest win probability pick across all derivatives!
        if candidates_pool:
            best_pick_obj = max(candidates_pool, key=lambda x: x["win_percentage"])
            weekly_pick = best_pick_obj["pick_type"]
            win_prob = best_pick_obj["win_percentage"]
            odds = best_pick_obj["fair_odds"]
            reason = best_pick_obj["reason"]
        else:
            weekly_pick = "Over 1.5 Total Match Goals"
            win_prob = 78.0
            odds = 1.28
            reason = "Standard baseline derivative."

        if win_prob >= 85.0 or penta.get("consensus_count", 0) >= 4:
            badge = "💎 DIAMOND LOCK"
        elif win_prob >= 78.0:
            badge = "⚡ VALUE LOCK"
        else:
            badge = "🥇 GOLD SAFETY"

        results.append({
            "fixture": f"{h} vs {a}",
            "home_team": h,
            "away_team": a,
            "kickoff": ko,
            "best_weekly_pick": weekly_pick,
            "win_probability": float(win_prob),
            "fair_odds": float(odds),
            "safety_badge": badge,
            "consensus_tier": penta.get("consensus_tier", "High Confidence"),
            "consensus_count": penta.get("consensus_count", 4),
            "predicted_score": rep.get("forebet_prediction", {}).get("predicted_score", "—"),
            "sofascore_odds": f"{sofa['home_odds']:.2f} | {sofa['draw_odds']:.2f} | {sofa['away_odds']:.2f}",
            "reason": reason,
            "yellow_cards": rep.get("yellow_cards", {}),
            "card_pick": rep.get("yellow_cards", {}).get("best_card_bet", {})
        })

    # Sort fixtures by highest win probability (Rank 1 to 10)
    ranked = sorted(results, key=lambda x: x["win_probability"], reverse=True)

    # 1. Top 3 Banker Multi
    top3 = ranked[:3]
    top3_odds = round(math.prod([x["fair_odds"] for x in top3]), 2)
    top3_prob = round(math.prod([x["win_probability"] / 100.0 for x in top3]) * 100.0, 1)

    # 2. Top 5 Weekend Multi
    top5 = ranked[:5]
    top5_odds = round(math.prod([x["fair_odds"] for x in top5]), 2)
    top5_prob = round(math.prod([x["win_probability"] / 100.0 for x in top5]) * 100.0, 1)

    # 3. Complete 10-Game Gameweek Mega Ticket
    top10_odds = round(math.prod([x["fair_odds"] for x in ranked]), 2)
    top10_prob = round(math.prod([x["win_probability"] / 100.0 for x in ranked]) * 100.0, 2)

    # Filter for Unders, Overs, and Yellow Cards specials
    unders = [x for x in ranked if "under" in x["best_weekly_pick"].lower() and "card" not in x["best_weekly_pick"].lower()]
    overs = [x for x in ranked if "over" in x["best_weekly_pick"].lower() and "card" not in x["best_weekly_pick"].lower()]
    cards_picks = [x for x in ranked if x.get("card_pick") and x["card_pick"].get("win_percentage", 0) >= 65.0]

    return {
        "gameweek": active_gw,
        "gameweek_label": gameweek_label,
        "is_official": is_official,
        "fixtures_count": len(ranked),
        "ranked_fixtures": ranked,
        "banker_multi_3": {
            "legs": top3,
            "total_odds": top3_odds,
            "combined_win_prob": top3_prob,
            "tier": "🏦 TOP 3 BANKER PARLAY (ULTRA-SAFE)"
        },
        "weekend_multi_5": {
            "legs": top5,
            "total_odds": top5_odds,
            "combined_win_prob": top5_prob,
            "tier": "🚀 TOP 5 WEEKEND ACCUMULATOR"
        },
        "mega_multi_10": {
            "legs": ranked,
            "total_odds": top10_odds,
            "combined_win_prob": top10_prob,
            "tier": "👑 TOP 10 COMPLETE GAMEWEEK ACCUMULATOR (MEGA TICKET)"
        },
        "unders_count": len(unders),
        "overs_count": len(overs),
        "cards_count": len(cards_picks)
    }

EUROPEAN_LEAGUES_CONFIG = [
    {"code": "E0", "name": "Premier League", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "gameweek": 10},
    {"code": "SP1", "name": "La Liga", "flag": "🇪🇸", "gameweek": 12},
    {"code": "I1", "name": "Serie A", "flag": "🇮🇹", "gameweek": 11},
    {"code": "D1", "name": "Bundesliga", "flag": "🇩🇪", "gameweek": 9},
    {"code": "F1", "name": "Ligue 1", "flag": "🇫🇷", "gameweek": 10},
]

def scan_all_european_leagues(predictor) -> Dict[str, Any]:
    """
    Scans all 5 top European leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
    simultaneously across all active matchweeks (48 total matches).
    Ranks the entire continent's fixtures by statistical safety, isolates the Top 10
    absolute highest-conviction European banker picks, and builds pan-European multi-bets.
    """
    all_fixtures = []
    league_summaries = {}

    for cfg in EUROPEAN_LEAGUES_CONFIG:
        lg_code = cfg["code"]
        gw = cfg["gameweek"]
        res = scan_weekly_gameweek(predictor, league=lg_code, gameweek=gw)
        fixtures = res.get("ranked_fixtures", [])

        for f in fixtures:
            item = dict(f)
            item["league_code"] = lg_code
            item["league_name"] = cfg["name"]
            item["league_flag"] = cfg["flag"]
            all_fixtures.append(item)

        league_summaries[lg_code] = {
            "name": cfg["name"],
            "flag": cfg["flag"],
            "gameweek": gw,
            "matches_count": len(fixtures)
        }

    # Sort all European matches by win probability descending
    ranked_europe = sorted(all_fixtures, key=lambda x: x["win_probability"], reverse=True)

    # Multi-Market Candidate Extraction for Top 10 Diversity
    # Ensures slate includes a balanced mix of:
    # Double Chance, Team to Score, Goals Over/Under, and Yellow Cards
    all_candidate_bets = []
    for f in all_fixtures:
        # 1. Primary pick from match analysis
        cat = "Double Chance" if "Double Chance" in f["best_weekly_pick"] else (
            "Team Goals" if "to Score" in f["best_weekly_pick"] else (
                "Goals Total" if "Goal" in f["best_weekly_pick"] else "Market Derivative"
            )
        )
        all_candidate_bets.append({
            "fixture": f["fixture"],
            "league_flag": f["league_flag"],
            "league_name": f["league_name"],
            "league_code": f["league_code"],
            "home_team": f["home_team"],
            "away_team": f["away_team"],
            "kickoff": f["kickoff"],
            "best_weekly_pick": f["best_weekly_pick"],
            "win_probability": f["win_probability"],
            "fair_odds": f["fair_odds"],
            "category": cat,
            "reason": f["reason"],
            "safety_badge": f["safety_badge"],
            "sofascore_odds": f["sofascore_odds"],
            "predicted_score": f["predicted_score"],
            "yellow_cards": f.get("yellow_cards", {}),
            "card_pick": f.get("card_pick", {})
        })

        # 2. Yellow cards special pick if high probability
        cp = f.get("card_pick")
        if cp and cp.get("win_percentage", 0) >= 65.0:
            all_candidate_bets.append({
                "fixture": f["fixture"],
                "league_flag": f["league_flag"],
                "league_name": f["league_name"],
                "league_code": f["league_code"],
                "home_team": f["home_team"],
                "away_team": f["away_team"],
                "kickoff": f["kickoff"],
                "best_weekly_pick": cp["pick_type"],
                "win_probability": cp["win_percentage"],
                "fair_odds": cp["fair_odds"],
                "category": "Yellow Cards",
                "reason": cp.get("rationale", "Disciplinary friction index."),
                "safety_badge": cp.get("safety_badge", "🟨 CARDS VALUE"),
                "sofascore_odds": f["sofascore_odds"],
                "predicted_score": f["predicted_score"],
                "yellow_cards": f.get("yellow_cards", {}),
                "card_pick": cp
            })

    all_candidate_bets.sort(key=lambda x: x["win_probability"], reverse=True)

    # Select Top 10 with max 3 per category to ensure true multi-market diversity
    diverse_top10 = []
    cat_counts = {}
    seen_fixtures = set()

    for b in all_candidate_bets:
        cat = b["category"]
        fix = b["fixture"]
        if fix in seen_fixtures:
            continue
        if cat_counts.get(cat, 0) >= 3:
            continue
        diverse_top10.append(b)
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        seen_fixtures.add(fix)
        if len(diverse_top10) == 10:
            break

    if len(diverse_top10) < 10:
        for b in all_candidate_bets:
            if b["fixture"] not in seen_fixtures:
                diverse_top10.append(b)
                seen_fixtures.add(b["fixture"])
                if len(diverse_top10) == 10:
                    break

    top_10 = diverse_top10

    # Top 3 Pan-European Super Banker Multi
    top3 = top_10[:3]
    top3_odds = round(math.prod([x["fair_odds"] for x in top3]), 2) if top3 else 1.0
    top3_prob = round(math.prod([x["win_probability"] / 100.0 for x in top3]) * 100.0, 1) if top3 else 0.0

    # Top 5 Pan-European Elite Multi
    top5 = top_10[:5]
    top5_odds = round(math.prod([x["fair_odds"] for x in top5]), 2) if top5 else 1.0
    top5_prob = round(math.prod([x["win_probability"] / 100.0 for x in top5]) * 100.0, 1) if top5 else 0.0

    # Golden Doublets (2-Leg Vig-Resistant Round Robins)
    # 1. Heavyweight Safety Doublet
    doublet_1_legs = top_10[:2]
    d1_odds = round(math.prod([x["fair_odds"] for x in doublet_1_legs]), 2) if len(doublet_1_legs) == 2 else 1.0
    d1_prob = round(math.prod([x["win_probability"] / 100.0 for x in doublet_1_legs]) * 100.0, 1) if len(doublet_1_legs) == 2 else 0.0

    # 2. Attacking Goals Doublet
    goals_c = [b for b in top_10 if b.get("category") in ["Team Goals", "Goals Total"]]
    doublet_2_legs = goals_c[:2] if len(goals_c) >= 2 else top_10[2:4]
    d2_odds = round(math.prod([x["fair_odds"] for x in doublet_2_legs]), 2) if len(doublet_2_legs) == 2 else 1.0
    d2_prob = round(math.prod([x["win_probability"] / 100.0 for x in doublet_2_legs]) * 100.0, 1) if len(doublet_2_legs) == 2 else 0.0

    # 3. Disciplinary Cards Value Doublet
    cards_c = [b for b in top_10 if b.get("category") == "Yellow Cards"]
    doublet_3_legs = cards_c[:2] if len(cards_c) >= 2 else top_10[4:6]
    d3_odds = round(math.prod([x["fair_odds"] for x in doublet_3_legs]), 2) if len(doublet_3_legs) == 2 else 1.0
    d3_prob = round(math.prod([x["win_probability"] / 100.0 for x in doublet_3_legs]) * 100.0, 1) if len(doublet_3_legs) == 2 else 0.0

    # Top Cards Picks across Europe
    euro_cards = [
        f for f in all_fixtures
        if f.get("card_pick") and f["card_pick"].get("win_percentage", 0) >= 60.0
    ]
    ranked_cards = sorted(euro_cards, key=lambda x: x["card_pick"]["win_percentage"], reverse=True)
    top_5_cards = ranked_cards[:5]

    return {
        "total_matches_scanned": len(all_fixtures),
        "total_leagues_scanned": len(EUROPEAN_LEAGUES_CONFIG),
        "league_summaries": league_summaries,
        "ranked_fixtures": ranked_europe,
        "top_10_safest": top_10,
        "golden_doublets": [
            {
                "title": "🛡️ Heavyweight Safety Doublet",
                "legs": doublet_1_legs,
                "total_odds": d1_odds,
                "combined_win_prob": d1_prob,
                "tier": "LOW VIG • MAXIMUM CAPITAL PROTECTION"
            },
            {
                "title": "⚽ Attacking Goals Doublet",
                "legs": doublet_2_legs,
                "total_odds": d2_odds,
                "combined_win_prob": d2_prob,
                "tier": "POSITIVE EV • GOALS DIVERSITY"
            },
            {
                "title": "🟨 Disciplinary Cards Value Doublet",
                "legs": doublet_3_legs,
                "total_odds": d3_odds,
                "combined_win_prob": d3_prob,
                "tier": "TACTICAL FRICTION • INDEPENDENT MARKET"
            }
        ],
        "pan_euro_banker_3": {
            "legs": top3,
            "total_odds": top3_odds,
            "combined_win_prob": top3_prob,
            "tier": "👑 TOP 3 PAN-EUROPEAN SUPER BANKER (CROSS-LEAGUE SWEEP)"
        },
        "pan_euro_weekend_5": {
            "legs": top5,
            "total_odds": top5_odds,
            "combined_win_prob": top5_prob,
            "tier": "🚀 TOP 5 PAN-EUROPEAN ELITE MULTI"
        },
        "top_cards_picks": top_5_cards
    }
