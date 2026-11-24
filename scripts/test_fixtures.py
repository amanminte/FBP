import sys
sys.path.insert(0, '.')
from src.models.predict import FootballPredictorV2

p = FootballPredictorV2()
for h, a in [('Man City', 'Fulham'), ('Aston Villa', 'Sunderland'), ('Bournemouth', 'Forest')]:
    res = p.predict_fixture(h, a, league='E0')
    print(f"=== {h} vs {a} ===")
    print("expected_goals:", res.get('expected_goals'))
    print("top_3_scorelines:", res.get('top_3_scorelines'))
    print("calibrated_probs:", res.get('calibrated_probabilities'))
    print("top_3_safe_picks:", [x.get('pick_type') for x in res.get('top_3_safe_picks', [])])
