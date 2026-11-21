export interface LeagueInfo {
  id: string;
  name: string;
  country: string;
  flag: string;
  teams: string[];
}

export interface FixtureMatch {
  home: string;
  away: string;
  kickoff?: string;
  finished?: boolean;
  score_h?: number | null;
  score_a?: number | null;
  gameweek?: number;
}

export interface SafePick {
  title: string;
  market_key?: string;
  bet: string;
  probability: number;
  fair_odds: number;
  reasoning: string;
  risk_level: string;
  badge?: string;
}

export interface ConsensusSource {
  name: string;
  icon: string;
  url?: string;
  pick: string;
  pick_readable?: string;
  score: string;
  metric_label: string;
  metric_value: string;
  secondary: string;
  agrees: boolean;
}

export interface PentaConsensus {
  primary_pick: string;
  consensus_tier: string;
  agreement_count: number;
  total_sources?: number;
  consensus_score: number;
  safest_recommended_market?: string;
  common_ground_market?: {
    market: string;
    fair_odds: number;
    agreement_count: number;
    scorelines: string[];
  };
  sources?: ConsensusSource[];
  individual_predictions?: Record<string, any>;
}

export interface YellowCardsData {
  expected_total_cards: number;
  expected_home_cards: number;
  expected_away_cards: number;
  is_derby?: boolean;
  derby_name?: string;
  derby_note?: string;
  referee_note?: string;
  best_card_bet?: {
    market: string;
    fair_odds: number;
    probability_pct: number;
    confidence: string;
  };
}

export interface MatchPrediction {
  fixture: string;
  competition: string;
  model_track: string;
  prediction: string;
  tier_badge: string;
  top_3_safe_picks: SafePick[];
  calibrated_probabilities: {
    home_win: number;
    draw: number;
    away_win: number;
  };
  expected_goals: {
    home_xg: number;
    away_xg: number;
    total_xg: number;
  };
  top_3_scorelines: Array<{
    score: string;
    probability_pct: number;
  }>;
  penta_consensus: PentaConsensus;
  yellow_cards: YellowCardsData;
  alternative_bet_ideas?: SafePick[];
  timestamp: string;
}

export interface BetSlipItem {
  id: string;
  fixture: string;
  home_team: string;
  away_team: string;
  league: string;
  pick: string;
  odds: number;
  prob: number;
  category: string;
}

export interface LedgerBet {
  id: number;
  created_at: string;
  match_date: string;
  league: string;
  fixture: string;
  home_team: string;
  away_team: string;
  model_track: string;
  predicted_pick: string;
  calibrated_prob: number;
  opening_odds: number;
  is_hit: number | null;
  status: string;
  result_label: string;
  result_color: string;
  actual_score: string;
  actual_outcome: string;
  stake_units: number;
  pnl: number;
}

export interface LedgerSummary {
  total_predictions: number;
  settled_count: number;
  win_rate_pct: number;
  avg_clv_pct: number;
  beat_clv_rate_pct: number;
  total_flat_pnl: number;
  flat_roi_pct: number;
}

export interface ContinuousLearningSummary {
  total_matches_learned: number;
  average_brier_score: number;
  temperature_adjustment: number;
  last_updated: string | null;
  top_positive_elo_drifts: Array<[string, number]>;
  top_negative_elo_drifts: Array<[string, number]>;
  recent_log: Array<{
    fixture: string;
    score: string;
    actual: string;
    elo_delta: string;
  }>;
}
