"""
FastAPI High-Speed Asynchronous Quantitative Terminal Backend.
Serves match predictions, 5-way consensus, gameweek scans, live ledger,
and continuous learning telemetry for the React Obsidian Terminal.
"""
import os
import sys
import json
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure models can deserialize joblib models
from src.models.train import ModelBundleV2, PlattCalibrator
from src.models.predict import FootballPredictorV2
from src.features.squad_database import get_squad_player_names, EXPANDED_SQUAD_DATABASE
from src.features.official_fixtures import fetch_official_league_fixtures
from src.models.gameweek_scanner import scan_weekly_gameweek, scan_all_european_leagues
from src.models.continuous_learning import ContinuousLearningEngine
from src.evaluation.live_clv_tracker import (
    record_live_prediction,
    get_ledger_summary,
    auto_grade_pending_predictions_from_live_feed,
    LEDGER_DB_PATH
)

sys.modules['__main__'].ModelBundleV2 = ModelBundleV2
sys.modules['__main__'].PlattCalibrator = PlattCalibrator

# Initialize FastAPI App
app = FastAPI(
    title="Syndicate Terminal Quantitative API",
    version="2.0.0",
    description="High-frequency predictive football betting & consensus engine"
)

# Enable CORS for frontend Vite dev server & production builds
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-load singleton models for zero-latency in-memory predictions (<10ms)
print("[INFO] Pre-loading FootballPredictorV2 and ContinuousLearningEngine...")
predictor = FootballPredictorV2()
learning_engine = ContinuousLearningEngine()
print("[SUCCESS] Models and engines primed successfully!")

# Supported Leagues definition
LEAGUES = [
    {"id": "E0", "name": "Premier League", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    {"id": "SP1", "name": "La Liga", "country": "Spain", "flag": "🇪🇸"},
    {"id": "I1", "name": "Serie A", "country": "Italy", "flag": "🇮🇹"},
    {"id": "D1", "name": "Bundesliga", "country": "Germany", "flag": "🇩🇪"},
    {"id": "F1", "name": "Ligue 1", "country": "France", "flag": "🇫🇷"},
]

# Request / Response Schemas
class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    league: str = "E0"
    model_track: str = "C"
    home_missing: List[str] = Field(default_factory=list)
    away_missing: List[str] = Field(default_factory=list)
    home_formation: str = "4-3-3"
    away_formation: str = "4-2-3-1"
    market_odds: Optional[List[float]] = None

class LockBetRequest(BaseModel):
    match_date: str
    league: str
    home_team: str
    away_team: str
    model_track: str
    predicted_pick: str
    calibrated_prob: float
    opening_odds: float
    stake_units: float = 1.0

# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "predictor_loaded": True,
        "models_version": "v2.0-online-consensus"
    }

@app.get("/api/leagues")
def get_leagues():
    """Returns supported European leagues and teams."""
    result = []
    for lg in LEAGUES:
        lg_id = lg["id"]
        # Extract known teams for this league from squads or fixture files
        fixture_path = f"data/fixtures/official_fixtures_{lg_id}.json"
        teams = set()
        if os.path.exists(fixture_path):
            try:
                with open(fixture_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for gw, matches in data.items():
                        for m in matches:
                            if m.get("home"): teams.add(m["home"])
                            if m.get("away"): teams.add(m["away"])
            except Exception:
                pass
        
        # Add any remaining from CLUB_SQUADS
        for club in EXPANDED_SQUAD_DATABASE.keys():
            if lg_id == "E0" and club in ["Arsenal", "Chelsea", "Liverpool", "Manchester City", "Manchester United", "Newcastle", "Tottenham", "Aston Villa"]:
                teams.add(club)

        result.append({
            **lg,
            "teams": sorted(list(teams)) if teams else []
        })
    return result

@app.get("/api/squad/{team_name}")
def get_squad(team_name: str):
    """Returns squad roster for injury/absence selection."""
    players = get_squad_player_names(team_name)
    return {
        "team": team_name,
        "players": players
    }

@app.get("/api/fixtures/{league}")
def get_fixtures(league: str):
    """Returns current schedule, finished scores, and kickoff times."""
    fixture_path = f"data/fixtures/official_fixtures_{league}.json"
    if not os.path.exists(fixture_path):
        raise HTTPException(status_code=404, detail=f"No fixture data found for league {league}")
    
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert dictionary of gameweeks into structured list
    gameweeks = []
    for gw, matches in data.items():
        gameweeks.append({
            "gameweek": gw,
            "matches": matches
        })
    return {
        "league": league,
        "gameweeks": gameweeks
    }

@app.post("/api/predict/match")
def predict_match(req: PredictRequest):
    """Runs complete 5-way consensus & safe picks simulation."""
    try:
        prediction_result = predictor.predict_fixture(
            home_team=req.home_team,
            away_team=req.away_team,
            track=req.model_track,
            home_missing=req.home_missing,
            away_missing=req.away_missing,
            home_formation=req.home_formation,
            away_formation=req.away_formation,
            market_odds=req.market_odds,
            league=req.league
        )
        return prediction_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scanner/{league}")
def run_scanner(league: str, gameweek: Optional[int] = None):
    """Scans gameweek fixtures across selected league or all European leagues."""
    try:
        if league.upper() == "ALL":
            return scan_all_european_leagues()
        else:
            return scan_weekly_gameweek(league=league, target_gw=gameweek)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ledger")
def get_ledger(filter_status: str = "ALL"):
    """Returns clean ledger rows and high-level summary KPIs."""
    summary = get_ledger_summary()
    
    conn = sqlite3.connect(LEDGER_DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT id, created_at, match_date, league, home_team, away_team, 
               model_track, predicted_pick, calibrated_prob, opening_odds, 
               closing_odds, is_hit, stake_units, pnl_flat, status, actual_score, actual_outcome
        FROM predictions
    """
    params = []
    if filter_status.upper() == "SETTLED":
        query += " WHERE is_hit IS NOT NULL"
    elif filter_status.upper() == "PENDING":
        query += " WHERE is_hit IS NULL OR status = 'PENDING'"
        
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    formatted_bets = []
    for r in rows:
        (b_id, created_at, match_date, lg, h_team, a_team, track, 
         pick, prob, open_odds, close_odds, is_hit, stake, pnl, status, actual_score, outcome) = r
        
        # Result status
        if is_hit == 1:
            res_label = "HIT"
            res_color = "emerald"
        elif is_hit == 0:
            res_label = "MISSED"
            res_color = "rose"
        else:
            res_label = "PENDING"
            res_color = "amber"

        formatted_bets.append({
            "id": b_id,
            "created_at": created_at,
            "match_date": match_date,
            "league": lg,
            "fixture": f"{h_team} vs {a_team}",
            "home_team": h_team,
            "away_team": a_team,
            "model_track": track,
            "predicted_pick": pick,
            "calibrated_prob": round(prob * 100, 1) if prob <= 1.0 else round(prob, 1),
            "opening_odds": open_odds,
            "is_hit": is_hit,
            "status": status,
            "result_label": res_label,
            "result_color": res_color,
            "actual_score": actual_score or "—",
            "actual_outcome": outcome or "—",
            "stake_units": stake,
            "pnl": pnl or 0.0
        })

    return {
        "summary": summary,
        "bets": formatted_bets
    }

@app.post("/api/ledger/lock")
def lock_bet_to_ledger(req: LockBetRequest):
    """Records a single or parlay pick directly into the SQLite ledger."""
    try:
        new_id = record_live_prediction(
            match_date=req.match_date,
            league=req.league,
            home_team=req.home_team,
            away_team=req.away_team,
            model_track=req.model_track,
            predicted_pick=req.predicted_pick,
            calibrated_prob=req.calibrated_prob,
            opening_odds=req.opening_odds,
            stake_units=req.stake_units
        )
        return {
            "success": True,
            "ledger_id": new_id,
            "message": f"Successfully locked '{req.predicted_pick}' into Syndicate Ledger!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ledger/auto-grade")
def trigger_auto_grade():
    """Auto-grades pending bets against official fixture results."""
    try:
        result = auto_grade_pending_predictions_from_live_feed()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/continuous-learning/summary")
def get_continuous_learning_summary():
    """Returns online continuous learning stats and Elo momentum drifts."""
    return learning_engine.get_learning_summary()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
