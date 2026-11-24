import json

def inspect_gw(league, gw_num):
    try:
        with open(f'data/fixtures/official_fixtures_{league}.json', 'r') as f:
            data = json.load(f)
            matches = data.get(str(gw_num), [])
            print(f"=== {league} GW {gw_num} ({len(matches)} matches) ===")
            for m in matches:
                print(f"  {m.get('date')} | {m.get('home')} vs {m.get('away')} | fin={m.get('finished')} | score={m.get('score_h')}-{m.get('score_a')}")
    except Exception as e:
        print(f"Error {league}: {e}")

inspect_gw('E0', 11)
inspect_gw('D1', 10)
inspect_gw('SP1', 13)
inspect_gw('I1', 12)
inspect_gw('F1', 10)
