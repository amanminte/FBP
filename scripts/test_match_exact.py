import sys
sys.path.insert(0, '.')
import json
from src.features.official_fixtures import standardize_team_name

pending = [
    (71, 'E0', 'Man City', 'Fulham'),
    (72, 'E0', 'Aston Villa', 'Sunderland'),
    (73, 'E0', 'Bournemouth', 'Forest'),
    (74, 'E0', 'Chelsea', 'Leeds'),
    (75, 'E0', 'Coventry', 'Crystal Palace'),
    (76, 'E0', 'Tottenham', 'Ipswich'),
    (77, 'E0', 'Newcastle', 'Arsenal'),
    (78, 'E0', 'Man City', 'Fulham'),
    (79, 'E0', 'Newcastle', 'Arsenal'),
    (80, 'E0', 'Hull', 'Brighton'),
    (81, 'SP1', 'Getafe', 'Atlético Madrid'),
    (82, 'SP1', 'Racing Club', 'Real Sociedad'),
    (83, 'SP1', 'Sevilla', 'Real Betis'),
    (84, 'I1', 'Parma', 'Roma'),
    (85, 'I1', 'Lazio', 'Lecce'),
    (86, 'I1', 'Atalanta', 'Inter'),
    (87, 'D1', "M'gladbach", 'Dortmund'),
    (88, 'D1', 'Bayern', 'Köln'),
    (89, 'D1', 'Union Berlin', 'Leipzig'),
    (90, 'F1', 'Monaco', 'Auxerre'),
    (92, 'F1', 'Nice', 'PSG')
]

for p_id, lg, h, a in pending:
    with open(f'data/fixtures/official_fixtures_{lg}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Active gameweeks for Nov 21: E0: 11, D1: 10, I1: 12, SP1: 13, F1: 10
    active_gws = {
        'E0': ['11', '12'],
        'D1': ['10', '11'],
        'I1': ['12', '13'],
        'SP1': ['13', '14'],
        'F1': ['10', '11']
    }
    
    found = None
    for gw in active_gws.get(lg, []):
        for m in data.get(gw, []):
            mf_h = standardize_team_name(m.get('home', '')).lower().strip()
            mf_a = standardize_team_name(m.get('away', '')).lower().strip()
            h_std = standardize_team_name(h).lower().strip()
            a_std = standardize_team_name(a).lower().strip()
            
            # Exact or standard substring
            h_ok = (h_std == mf_h or h_std in mf_h or mf_h in h_std)
            a_ok = (a_std == mf_a or a_std in mf_a or mf_a in a_std)
            if h_ok and a_ok:
                found = (gw, m.get('home'), m.get('away'), m.get('finished'), m.get('score_h'), m.get('score_a'))
                break
        if found:
            break
    print(f"[{p_id}] {h} vs {a} ({lg}) -> {found}")
