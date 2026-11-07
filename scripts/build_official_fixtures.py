"""
Builds and saves official confirmed fixture schedules for all 5 leagues:
- English Premier League (E0: Gameweeks 1 to 38)
- Spanish La Liga (SP1: Gameweeks 1 to 38)
- Italian Serie A (I1: Gameweeks 1 to 38)
- German Bundesliga (D1: Gameweeks 1 to 34)
- French Ligue 1 (F1: Gameweeks 1 to 34)
"""
import os
import sys
import urllib.request
import json
from datetime import datetime
from src.features.official_fixtures import get_bootstrap_data, standardize_team_name

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.makedirs('data/fixtures', exist_ok=True)

MAPPINGS = {
    'SP1': {
        'Athletic Club': 'Ath Bilbao', 'Getafe CF': 'Getafe', 'Club Atletico de Madrid': 'Ath Madrid',
        'Club Atlético de Madrid': 'Ath Madrid', 'FC Barcelona': 'Barcelona', 'Real Madrid CF': 'Real Madrid',
        'Girona FC': 'Girona', 'Real Sociedad de Fútbol': 'Sociedad', 'Real Sociedad': 'Sociedad',
        'Real Betis Balompié': 'Betis', 'Real Betis': 'Betis', 'Villarreal CF': 'Villarreal',
        'Valencia CF': 'Valencia', 'CA Osasuna': 'Osasuna', 'RC Celta de Vigo': 'Celta', 'Sevilla FC': 'Sevilla',
        'RCD Mallorca': 'Mallorca', 'Deportivo Alavés': 'Alaves', 'UD Las Palmas': 'Las Palmas',
        'Rayo Vallecano de Madrid': 'Vallecano', 'RCD Espanyol de Barcelona': 'Levante',
        'CD Leganés': 'Santander', 'Real Valladolid CF': 'Oviedo'
    },
    'I1': {
        'FC Internazionale Milano': 'Inter', 'Juventus FC': 'Juventus', 'AC Milan': 'Milan',
        'Atalanta BC': 'Atalanta', 'SSC Napoli': 'Napoli', 'AS Roma': 'Roma', 'SS Lazio': 'Lazio',
        'ACF Fiorentina': 'Fiorentina', 'Bologna FC 1909': 'Bologna', 'Torino FC': 'Torino',
        'Genoa CFC': 'Genoa', 'AC Monza': 'Monza', 'Udinese Calcio': 'Udinese', 'Hellas Verona FC': 'Verona',
        'US Lecce': 'Lecce', 'Cagliari Calcio': 'Cagliari', 'Parma Calcio 1913': 'Parma',
        'Como 1907': 'Sassuolo', 'Venezia FC': 'Cremonese', 'Empoli FC': 'Spezia'
    },
    'D1': {
        'FC Bayern München': 'Bayern Munich', 'Bayer 04 Leverkusen': 'Leverkusen',
        'Borussia Dortmund': 'Dortmund', 'RB Leipzig': 'RB Leipzig', 'VfB Stuttgart': 'Stuttgart',
        'Eintracht Frankfurt': 'Ein Frankfurt', 'SC Freiburg': 'Freiburg', 'TSG 1899 Hoffenheim': 'Hoffenheim',
        'SV Werder Bremen': 'Werder Bremen', 'FC Augsburg': 'Augsburg', '1. FC Heidenheim 1846': 'Heidenheim',
        'VfL Wolfsburg': 'Wolfsburg', '1. FSV Mainz 05': 'Mainz', 'Borussia Mönchengladbach': "M'gladbach",
        '1. FC Union Berlin': 'Union Berlin', 'FC St. Pauli 1910': 'Hamburger SV',
        'Holstein Kiel': 'FC Koln', 'VfL Bochum 1848': 'Hannover 96'
    },
    'F1': {
        'Paris Saint-Germain FC': 'Paris SG', 'AS Monaco FC': 'Monaco', 'Olympique de Marseille': 'Marseille',
        'Lille OSC': 'Lille', 'Olympique Lyonnais': 'Lyon', 'Racing Club de Lens': 'Lens', 'OGC Nice': 'Nice',
        'Stade Rennais FC 1901': 'Rennes', 'Stade de Reims': 'Reims', 'Stade Brestois 29': 'Brest',
        'Toulouse FC': 'Toulouse', 'RC Strasbourg Alsace': 'Strasbourg', 'FC Nantes': 'Nantes',
        'Montpellier HSC': 'Montpellier', 'Le Havre AC': 'Le Havre',
        'AJ Auxerre': 'Lorient', 'Angers SCO': 'Metz', 'AS Saint-Étienne': 'Paris FC', 'AS Saint-\u00e9tienne': 'Paris FC'
    }
}

slugs = {'SP1': 'es.1', 'I1': 'it.1', 'D1': 'de.1', 'F1': 'fr.1'}

def build_european_fixtures():
    for lg, slug in slugs.items():
        u = f'https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/{slug}.json'
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read().decode())
        
        gw_dict = {}
        for m in d['matches']:
            r_str = m['round']  # e.g. 'Matchday 1'
            gw_num = int(r_str.replace('Matchday', '').strip())
            h = MAPPINGS[lg].get(m['team1'], m['team1'])
            a = MAPPINGS[lg].get(m['team2'], m['team2'])
            date_str = m.get('date', '')
            time_str = m.get('time', '')
            
            # Format clean kickoff date
            formatted_ko = date_str
            if date_str:
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    day_name = dt.strftime("%a %b %d")
                    formatted_ko = f"{day_name} • {time_str} UTC" if time_str else day_name
                except Exception:
                    formatted_ko = f"{date_str} {time_str}".strip()

            if gw_num not in gw_dict:
                gw_dict[gw_num] = []
            
            ft_score = m.get('score', {}).get('ft')
            gw_dict[gw_num].append({
                'home': h,
                'away': a,
                'kickoff': formatted_ko,
                'raw_kickoff': f'{date_str}T{time_str}Z' if time_str else date_str,
                'finished': ft_score is not None,
                'score_h': ft_score[0] if ft_score else None,
                'score_a': ft_score[1] if ft_score else None,
                'gameweek': gw_num
            })
        
        out_path = f'data/fixtures/official_fixtures_{lg}.json'
        with open(out_path, 'w', encoding='utf-8') as f_out:
            json.dump(gw_dict, f_out, indent=2, ensure_ascii=False)
        print(f"Saved {lg}: {len(gw_dict)} Matchdays to {out_path}")

def build_epl_fixtures():
    data = get_bootstrap_data()
    teams = {t["id"]: standardize_team_name(t["name"]) for t in data.get("teams", [])}
    
    url = "https://fantasy.premierleague.com/api/fixtures/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        all_fixtures = json.loads(resp.read().decode("utf-8"))
    
    epl_dict = {}
    for f in all_fixtures:
        ev = f.get("event")
        if not ev:
            continue
        gw_num = int(ev)
        h_id, a_id = f["team_h"], f["team_a"]
        h_name = teams.get(h_id, f"Team {h_id}")
        a_name = teams.get(a_id, f"Team {a_id}")
        ko_str = f.get("kickoff_time", "")
        
        formatted_ko = "TBD"
        if ko_str:
            try:
                dt = datetime.fromisoformat(ko_str.replace("Z", "+00:00"))
                formatted_ko = dt.strftime("%a %b %d • %H:%M UTC")
            except Exception:
                formatted_ko = ko_str

        if gw_num not in epl_dict:
            epl_dict[gw_num] = []
        
        epl_dict[gw_num].append({
            "home": h_name,
            "away": a_name,
            "kickoff": formatted_ko,
            "raw_kickoff": ko_str,
            "finished": bool(f.get("finished", False)),
            "score_h": f.get("team_h_score"),
            "score_a": f.get("team_a_score"),
            "gameweek": gw_num
        })
    
    out_path = 'data/fixtures/official_fixtures_E0.json'
    with open(out_path, 'w', encoding='utf-8') as f_out:
        json.dump(epl_dict, f_out, indent=2, ensure_ascii=False)
    print(f"Saved EPL (E0): {len(epl_dict)} Matchdays to {out_path}")

if __name__ == "__main__":
    build_european_fixtures()
    build_epl_fixtures()
