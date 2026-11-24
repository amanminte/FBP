import json

with open('data/fixtures/official_fixtures_E0.json', 'r', encoding='utf-8') as f:
    e0 = json.load(f)

for gw, matches in e0.items():
    for m in matches:
        if 'Man City' in m.get('home', '') and 'Fulham' in m.get('away', ''):
            print(f"GW {gw}: finished={m.get('finished')}, score_h={m.get('score_h')}, score_a={m.get('score_a')}")
