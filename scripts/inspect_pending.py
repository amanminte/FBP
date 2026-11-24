import sqlite3

conn = sqlite3.connect('data/live_ledger/paper_trading.sqlite')
c = conn.cursor()
c.execute("SELECT id, match_date, league, home_team, away_team, predicted_pick, opening_odds, status FROM predictions WHERE status = 'PENDING'")
rows = c.fetchall()
print(f"Total PENDING: {len(rows)}")
for r in rows:
    print(r)
conn.close()
