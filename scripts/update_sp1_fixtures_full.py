import json

with open("data/fixtures/official_fixtures_SP1.json", "r", encoding="utf-8") as f:
    sp1 = json.load(f)

repl = {
    'Girona': 'Deportivo La Coruna',
    'Las Palmas': 'Racing Santander',
    'Leganes': 'Elche',
    'Valladolid': 'Levante',
    'Mallorca': 'Malaga',
    'Ath Madrid': 'Atletico Madrid',
    'Atlético Madrid': 'Atletico Madrid',
    'Ath Bilbao': 'Athletic Club',
    'Sociedad': 'Real Sociedad',
    'Betis': 'Real Betis',
    'Vallecano': 'Rayo Vallecano',
    'Celta': 'Celta Vigo',
}

# Update all gameweeks with canonical names
for gw, fixes in sp1.items():
    if gw == "12":
        continue
    for m in fixes:
        m['home'] = repl.get(m['home'], m['home'])
        m['away'] = repl.get(m['away'], m['away'])
        # If gameweek >= 10, mark upcoming matches as finished: False
        if int(gw) >= 10:
            m['finished'] = False
            m['score_h'] = None
            m['score_a'] = None

# Exact Gameweek 12 matches from user's official screenshots
gw12_exact = [
    {
        "home": "Sevilla",
        "away": "Alaves",
        "kickoff": "Fri Nov 06 • 11:00 PM",
        "raw_kickoff": "2026-11-06T21:00:00Z",
        "finished": True,
        "score_h": 0,
        "score_a": 0,
        "cards_h": 2,
        "cards_a": 2,
        "gameweek": 12
    },
    {
        "home": "Malaga",
        "away": "Racing Santander",
        "kickoff": "Sat Nov 07 • 04:00 PM",
        "raw_kickoff": "2026-11-07T16:00:00Z",
        "finished": False,
        "score_h": None,
        "score_a": None,
        "gameweek": 12
    },
    {
        "home": "Espanyol",
        "away": "Deportivo La Coruna",
        "kickoff": "Sat Nov 07 • 06:15 PM",
        "raw_kickoff": "2026-11-07T18:15:00Z",
        "finished": False,
        "score_h": None,
        "score_a": None,
        "gameweek": 12
    },
    {
        "home": "Osasuna",
        "away": "Athletic Club",
        "kickoff": "Sat Nov 07 • 08:30 PM",
        "raw_kickoff": "2026-11-07T20:30:00Z",
        "finished": False,
        "score_h": None,
        "score_a": None,
        "gameweek": 12
    },
    {
        "home": "Valencia",
        "away": "Real Madrid",
        "kickoff": "Sat Nov 07 • 11:00 PM",
        "raw_kickoff": "2026-11-07T23:00:00Z",
        "finished": False,
        "score_h": None,
        "score_a": None,
        "gameweek": 12
    },
    {
        "home": "Elche",
        "away": "Real Betis",
        "kickoff": "Sun Nov 08 • 04:00 PM",
        "raw_kickoff": "2026-11-08T16:00:00Z",
        "finished": False,
        "score_h": None,
        "score_a": None,
        "gameweek": 12
    },
    {
        "home": "Real Sociedad",
        "away": "Rayo Vallecano",
        "kickoff": "Sun Nov 08 • 06:15 PM",
        "raw_kickoff": "2026-11-08T18:15:00Z",
        "finished": False,
        "score_h": None,
        "score_a": None,
        "gameweek": 12
    },
    {
        "home": "Villarreal",
        "away": "Getafe",
        "kickoff": "Sun Nov 08 • 08:30 PM",
        "raw_kickoff": "2026-11-08T20:30:00Z",
        "finished": False,
        "score_h": None,
        "score_a": None,
        "gameweek": 12
    },
    {
        "home": "Celta Vigo",
        "away": "Levante",
        "kickoff": "Sun Nov 08 • 08:30 PM",
        "raw_kickoff": "2026-11-08T20:30:00Z",
        "finished": False,
        "score_h": None,
        "score_a": None,
        "gameweek": 12
    },
    {
        "home": "Atletico Madrid",
        "away": "Barcelona",
        "kickoff": "Sun Nov 08 • 11:00 PM",
        "raw_kickoff": "2026-11-08T23:00:00Z",
        "finished": False,
        "score_h": None,
        "score_a": None,
        "gameweek": 12
    }
]

sp1["12"] = gw12_exact

with open("data/fixtures/official_fixtures_SP1.json", "w", encoding="utf-8") as f:
    json.dump(sp1, f, indent=2, ensure_ascii=False)

print("Updated data/fixtures/official_fixtures_SP1.json across all 38 gameweeks!")
