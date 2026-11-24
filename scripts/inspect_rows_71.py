import sqlite3

conn = sqlite3.connect('data/live_ledger/paper_trading.sqlite')
c = conn.cursor()
c.execute("SELECT id, match_date, league, home_team, away_team, predicted_pick, actual_score, is_hit, pnl_flat, status FROM predictions WHERE id >= 71")
for r in c.fetchall():
    print(r)
conn.close()
