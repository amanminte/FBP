import json

# 1. Update CURRENT_2627_STANDINGS["SP1"] in src/features/league_tables.py
with open("src/features/league_tables.py", "r", encoding="utf-8") as f:
    text = f.read()

sp1_start_marker = '    "SP1": ['
sp1_end_marker = '    "I1": ['

p1 = text.find(sp1_start_marker)
p2 = text.find(sp1_end_marker)
assert p1 != -1 and p2 != -1

new_sp1_standings = """    "SP1": [
        {"Team": "Barcelona", "Rank": 1, "Pts": 30, "W": 10, "D": 0, "L": 1, "GF": 33, "GA": 10, "GD": 23, "Status": "🏆 League Leader (1st)"},
        {"Team": "Atletico Madrid", "Rank": 2, "Pts": 28, "W": 9, "D": 1, "L": 1, "GF": 26, "GA": 8, "GD": 18, "Status": "🌟 Champions League (2nd)"},
        {"Team": "Real Madrid", "Rank": 3, "Pts": 27, "W": 9, "D": 0, "L": 2, "GF": 25, "GA": 9, "GD": 16, "Status": "🌟 Champions League (3rd)"},
        {"Team": "Real Betis", "Rank": 4, "Pts": 23, "W": 7, "D": 2, "L": 2, "GF": 20, "GA": 11, "GD": 9, "Status": "🌟 Champions League (4th)"},
        {"Team": "Real Sociedad", "Rank": 5, "Pts": 19, "W": 6, "D": 1, "L": 4, "GF": 18, "GA": 13, "GD": 5, "Status": "🇪🇺 Europa League (5th)"},
        {"Team": "Sevilla", "Rank": 6, "Pts": 18, "W": 5, "D": 3, "L": 4, "GF": 16, "GA": 14, "GD": 2, "Status": "🇪🇺 Europa League (6th)"},
        {"Team": "Athletic Club", "Rank": 7, "Pts": 15, "W": 4, "D": 3, "L": 3, "GF": 14, "GA": 11, "GD": 3, "Status": "Top Half (7th)"},
        {"Team": "Deportivo La Coruna", "Rank": 8, "Pts": 14, "W": 3, "D": 5, "L": 3, "GF": 13, "GA": 13, "GD": 0, "Status": "Top Half (8th)"},
        {"Team": "Alaves", "Rank": 9, "Pts": 13, "W": 3, "D": 4, "L": 5, "GF": 12, "GA": 15, "GD": -3, "Status": "Top Half (9th)"},
        {"Team": "Villarreal", "Rank": 10, "Pts": 12, "W": 3, "D": 3, "L": 5, "GF": 14, "GA": 16, "GD": -2, "Status": "Mid-Table (10th)"},
        {"Team": "Celta Vigo", "Rank": 11, "Pts": 12, "W": 2, "D": 6, "L": 3, "GF": 11, "GA": 13, "GD": -2, "Status": "Mid-Table (11th)"},
        {"Team": "Rayo Vallecano", "Rank": 12, "Pts": 12, "W": 3, "D": 3, "L": 4, "GF": 10, "GA": 13, "GD": -3, "Status": "Mid-Table (12th)"},
        {"Team": "Getafe", "Rank": 13, "Pts": 12, "W": 3, "D": 3, "L": 5, "GF": 9, "GA": 13, "GD": -4, "Status": "Mid-Table (13th)"},
        {"Team": "Espanyol", "Rank": 14, "Pts": 11, "W": 3, "D": 2, "L": 6, "GF": 11, "GA": 17, "GD": -6, "Status": "Lower Half (14th)"},
        {"Team": "Osasuna", "Rank": 15, "Pts": 11, "W": 3, "D": 2, "L": 6, "GF": 10, "GA": 16, "GD": -6, "Status": "Lower Half (15th)"},
        {"Team": "Racing Santander", "Rank": 16, "Pts": 11, "W": 3, "D": 2, "L": 6, "GF": 9, "GA": 16, "GD": -7, "Status": "Lower Half (16th)"},
        {"Team": "Elche", "Rank": 17, "Pts": 10, "W": 2, "D": 4, "L": 5, "GF": 9, "GA": 15, "GD": -6, "Status": "Lower Half (17th)"},
        {"Team": "Levante", "Rank": 18, "Pts": 10, "W": 2, "D": 4, "L": 5, "GF": 8, "GA": 15, "GD": -7, "Status": "⚠️ Relegation Zone (18th)"},
        {"Team": "Valencia", "Rank": 19, "Pts": 9, "W": 2, "D": 3, "L": 6, "GF": 8, "GA": 17, "GD": -9, "Status": "⚠️ Relegation Zone (19th)"},
        {"Team": "Malaga", "Rank": 20, "Pts": 5, "W": 0, "D": 5, "L": 6, "GF": 6, "GA": 19, "GD": -13, "Status": "⚠️ Relegation Zone (20th)"}
    ],
"""

new_text = text[:p1] + new_sp1_standings + text[p2:]
with open("src/features/league_tables.py", "w", encoding="utf-8") as f:
    f.write(new_text)

print("Updated CURRENT_2627_STANDINGS['SP1'] successfully!")
