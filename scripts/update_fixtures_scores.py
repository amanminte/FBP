import json

# Update E0
with open('data/fixtures/official_fixtures_E0.json', 'r', encoding='utf-8') as f:
    e0 = json.load(f)

scores_e0 = {
    ('Man City', 'Fulham'): (1, 1),
    ('Aston Villa', 'Sunderland'): (0, 0),
    ('Bournemouth', 'Forest'): (2, 0),
    ('Chelsea', 'Leeds'): (1, 4),
    ('Coventry', 'Crystal Palace'): (3, 2),
    ('Tottenham', 'Ipswich'): (2, 0)
}

for m in e0.get('11', []):
    pair = (m.get('home'), m.get('away'))
    if pair in scores_e0:
        sh, sa = scores_e0[pair]
        m['finished'] = True
        m['score_h'] = sh
        m['score_a'] = sa
        print('Updated E0:', pair, sh, sa)

with open('data/fixtures/official_fixtures_E0.json', 'w', encoding='utf-8') as f:
    json.dump(e0, f, indent=2)

# Update D1
with open('data/fixtures/official_fixtures_D1.json', 'r', encoding='utf-8') as f:
    d1 = json.load(f)

scores_d1 = {
    ('Bayern', 'Köln'): (1, 1),
    ("M'gladbach", 'Dortmund'): (0, 1),
    ('Leverkusen', 'Paderborn'): (4, 0),
    ('Union Berlin', 'Leipzig'): (1, 5)
}

for m in d1.get('10', []):
    pair = (m.get('home'), m.get('away'))
    if pair in scores_d1:
        sh, sa = scores_d1[pair]
        m['finished'] = True
        m['score_h'] = sh
        m['score_a'] = sa
        print('Updated D1:', pair, sh, sa)

with open('data/fixtures/official_fixtures_D1.json', 'w', encoding='utf-8') as f:
    json.dump(d1, f, indent=2)

# Update I1
with open('data/fixtures/official_fixtures_I1.json', 'r', encoding='utf-8') as f:
    i1 = json.load(f)

scores_i1 = {
    ('Lazio', 'Lecce'): (3, 0)
}

for m in i1.get('12', []):
    pair = (m.get('home'), m.get('away'))
    if pair in scores_i1:
        sh, sa = scores_i1[pair]
        m['finished'] = True
        m['score_h'] = sh
        m['score_a'] = sa
        print('Updated I1:', pair, sh, sa)

with open('data/fixtures/official_fixtures_I1.json', 'w', encoding='utf-8') as f:
    json.dump(i1, f, indent=2)

print("Done updating fixture scores!")
