import sys
sys.path.insert(0, '.')
from src.evaluation.live_clv_tracker import auto_grade_pending_predictions_from_live_feed

res = auto_grade_pending_predictions_from_live_feed()
print(f"Graded count: {res.get('graded_count')}")
print("Graded items:")
for item in res.get('graded_items', []):
    print(f"  [ID {item['id']}] {item['fixture']} | Pick: {item['predicted_pick']} | Actual: {item['actual_score']} | Hit: {item['is_hit']} | PnL: {item['pnl']}")
