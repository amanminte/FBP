"""
Downloads and saves 100% authentic, real-world official fixture schedules for all Big 5 leagues:
- English Premier League (E0: 38 Gameweeks, 380 matches, 10 per week)
- Spanish La Liga (SP1: 38 Gameweeks, 380 matches, 10 per week)
- Italian Serie A (I1: 38 Gameweeks, 380 matches, 10 per week)
- German Bundesliga (D1: 34 Gameweeks, 306 matches, 9 per week)
- French Ligue 1 (F1: 34 Gameweeks, 306 matches, 9 per week)

Stored permanently in local directory: data/fixtures/official_fixtures_{league}.json
"""
import os
import sys
import json
import urllib.request
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.makedirs('data/fixtures', exist_ok=True)

# Standard Name Mapping for openfootball team names
CLEAN_NAME_MAP = {
    # English Premier League
    'Arsenal FC': 'Arsenal',
    'Aston Villa FC': 'Aston Villa',
    'AFC Bournemouth': 'Bournemouth',
    'Brentford FC': 'Brentford',
    'Brighton & Hove Albion FC': 'Brighton',
    'Chelsea FC': 'Chelsea',
    'Crystal Palace FC': 'Crystal Palace',
    'Everton FC': 'Everton',
    'Fulham FC': 'Fulham',
    'Ipswich Town FC': 'Ipswich Town',
    'Leicester City FC': 'Leicester',
    'Liverpool FC': 'Liverpool',
    'Manchester City FC': 'Manchester City',
    'Manchester United FC': 'Manchester United',
    'Newcastle United FC': 'Newcastle',
    'Nottingham Forest FC': 'Nottingham Forest',
    'Southampton FC': 'Southampton',
    'Tottenham Hotspur FC': 'Tottenham',
    'West Ham United FC': 'West Ham',
    'Wolverhampton Wanderers FC': 'Wolves',

    # Spanish La Liga
    'Athletic Club': 'Ath Bilbao',
    'Club Atlético de Madrid': 'Ath Madrid',
    'Club Atletico de Madrid': 'Ath Madrid',
    'FC Barcelona': 'Barcelona',
    'Real Madrid CF': 'Real Madrid',
    'Girona FC': 'Girona',
    'Real Sociedad de Fútbol': 'Sociedad',
    'Real Sociedad': 'Sociedad',
    'Real Betis Balompié': 'Betis',
    'Real Betis': 'Betis',
    'Villarreal CF': 'Villarreal',
    'Valencia CF': 'Valencia',
    'CA Osasuna': 'Osasuna',
    'RC Celta de Vigo': 'Celta',
    'Sevilla FC': 'Sevilla',
    'RCD Mallorca': 'Mallorca',
    'Getafe CF': 'Getafe',
    'Deportivo Alavés': 'Alaves',
    'Deportivo Alaves': 'Alaves',
    'UD Las Palmas': 'Las Palmas',
    'Rayo Vallecano de Madrid': 'Vallecano',
    'RCD Espanyol de Barcelona': 'Espanyol',
    'CD Leganés': 'Leganes',
    'CD Leganes': 'Leganes',
    'Real Valladolid CF': 'Valladolid',

    # Italian Serie A
    'FC Internazionale Milano': 'Inter',
    'Juventus FC': 'Juventus',
    'AC Milan': 'Milan',
    'Atalanta BC': 'Atalanta',
    'SSC Napoli': 'Napoli',
    'AS Roma': 'Roma',
    'SS Lazio': 'Lazio',
    'ACF Fiorentina': 'Fiorentina',
    'Bologna FC 1909': 'Bologna',
    'Torino FC': 'Torino',
    'Genoa CFC': 'Genoa',
    'AC Monza': 'Monza',
    'Udinese Calcio': 'Udinese',
    'Hellas Verona FC': 'Verona',
    'US Lecce': 'Lecce',
    'Cagliari Calcio': 'Cagliari',
    'Parma Calcio 1913': 'Parma',
    'Como 1907': 'Como',
    'Empoli FC': 'Empoli',
    'Venezia FC': 'Venezia',

    # German Bundesliga
    'FC Bayern München': 'Bayern Munich',
    'FC Bayern Munchen': 'Bayern Munich',
    'Bayer 04 Leverkusen': 'Leverkusen',
    'Borussia Dortmund': 'Dortmund',
    'RB Leipzig': 'RB Leipzig',
    'VfB Stuttgart': 'Stuttgart',
    'Eintracht Frankfurt': 'Ein Frankfurt',
    'SC Freiburg': 'Freiburg',
    'TSG 1899 Hoffenheim': 'Hoffenheim',
    'SV Werder Bremen': 'Werder Bremen',
    'FC Augsburg': 'Augsburg',
    '1. FC Heidenheim 1846': 'Heidenheim',
    'VfL Wolfsburg': 'Wolfsburg',
    '1. FSV Mainz 05': 'Mainz',
    'Borussia Mönchengladbach': "M'gladbach",
    'Borussia Monchengladbach': "M'gladbach",
    '1. FC Union Berlin': 'Union Berlin',
    'FC St. Pauli 1910': 'St. Pauli',
    'Holstein Kiel': 'Holstein Kiel',
    'VfL Bochum 1848': 'Bochum',

    # French Ligue 1
    'Paris Saint-Germain FC': 'Paris SG',
    'AS Monaco FC': 'Monaco',
    'Olympique de Marseille': 'Marseille',
    'Lille OSC': 'Lille',
    'Olympique Lyonnais': 'Lyon',
    'Racing Club de Lens': 'Lens',
    'OGC Nice': 'Nice',
    'Stade Brestois 29': 'Brest',
    'Stade Rennais FC 1901': 'Rennes',
    'Stade de Reims': 'Reims',
    'Toulouse FC': 'Toulouse',
    'RC Strasbourg Alsace': 'Strasbourg',
    'FC Nantes': 'Nantes',
    'Le Havre AC': 'Le Havre',
    'Montpellier HSC': 'Montpellier',
    'AJ Auxerre': 'Auxerre',
    'Angers SCO': 'Angers',
    'AS Saint-Étienne': 'Saint-Etienne',
    'AS Saint-Etienne': 'Saint-Etienne'
}

LEAGUES = {
    'E0': ('en.1', 'English Premier League', 38, 10),
    'SP1': ('es.1', 'Spanish La Liga', 38, 10),
    'I1': ('it.1', 'Italian Serie A', 38, 10),
    'D1': ('de.1', 'German Bundesliga', 34, 9),
    'F1': ('fr.1', 'French Ligue 1', 34, 9)
}

def clean_team_name(raw: str) -> str:
    cleaned = raw.strip()
    if cleaned in CLEAN_NAME_MAP:
        return CLEAN_NAME_MAP[cleaned]
    # Fallback normalization
    for k, v in CLEAN_NAME_MAP.items():
        if k.lower() in cleaned.lower() or cleaned.lower() in k.lower():
            return v
    return cleaned

def build_all_official_fixtures():
    print("Downloading 100% authentic, real-world official schedules for Big 5 leagues...")
    for lg, (slug, name, total_gw, per_gw) in LEAGUES.items():
        url = f'https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/{slug}.json'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print(f"Error fetching {lg} from {url}: {e}")
            continue

        matches = data.get('matches', [])
        gw_dict = {str(i): [] for i in range(1, total_gw + 1)}

        for m in matches:
            r_str = str(m.get('round', ''))  # e.g. "Matchday 1" or "Round 1"
            digits = ''.join(c for c in r_str if c.isdigit())
            if not digits:
                continue
            gw_num = int(digits)
            if gw_num < 1 or gw_num > total_gw:
                continue

            h_raw = m.get('team1', '')
            a_raw = m.get('team2', '')
            h = clean_team_name(h_raw)
            a = clean_team_name(a_raw)

            date_str = m.get('date', '')
            time_str = m.get('time', '')
            formatted_ko = date_str
            if date_str:
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    day_name = dt.strftime("%a %b %d")
                    formatted_ko = f"{day_name} • {time_str} UTC" if time_str else day_name
                except Exception:
                    formatted_ko = f"{date_str} {time_str}".strip()

            ft_score = m.get('score', {}).get('ft')
            is_fin = (ft_score is not None and len(ft_score) == 2)
            score_h = ft_score[0] if is_fin else None
            score_a = ft_score[1] if is_fin else None

            gw_dict[str(gw_num)].append({
                'home': h,
                'away': a,
                'kickoff': formatted_ko,
                'raw_kickoff': f'{date_str}T{time_str}Z' if time_str else date_str,
                'finished': is_fin,
                'score_h': score_h,
                'score_a': score_a,
                'gameweek': gw_num
            })

        out_path = f'data/fixtures/official_fixtures_{lg}.json'
        with open(out_path, 'w', encoding='utf-8') as f_out:
            json.dump(gw_dict, f_out, indent=2, ensure_ascii=False)

        total_saved_matches = sum(len(v) for v in gw_dict.values())
        print(f"✅ {name} ({lg}): Saved {total_saved_matches} matches across {len(gw_dict)} Gameweeks to {out_path}")

if __name__ == '__main__':
    build_all_official_fixtures()
