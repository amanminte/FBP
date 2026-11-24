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
    category?: string;
    fair_odds: number;
    agreement_count: number;
    scorelines: string[];
    reason?: string;
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

export interface CornersData {
  expected_total_corners: number;
  expected_home_corners: number;
  expected_away_corners: number;
  wing_play_factor_home?: number;
  wing_play_factor_away?: number;
  tactical_rationale?: string;
  wing_profiles_note?: string;
  probabilities?: Record<string, number>;
  fair_odds?: Record<string, number>;
  best_corner_bet?: {
    market: string;
    category: string;
    probability: number;
    odds: number;
    confidence_tier: string;
    rationale: string;
  };
}

export interface TeamAtmosphere {
  team: string;
  manager: string;
  manager_status: string;
  manager_reliability_pct: number;
  manager_badge: string;
  manager_note: string;
  atmosphere_label: string;
  atmosphere_sentiment: string;
  atmosphere_color: string;
  morale_index_pct: number;
  xg_attack_shift: number;
  xg_defense_concede_shift: number;
  verified_news: Array<{
    title: string;
    source: string;
    link: string;
    published?: string;
  }>;
  form: {
    team: string;
    form_sequence?: string[];
    form_string?: string;
    points_last_5?: number;
    points_per_game: number;
    goals_for_last_5?: number;
    goals_against_last_5?: number;
    goal_diff_last_5?: number;
    momentum_trend?: string;
    sequence?: string[];
    record?: { wins: number; draws: number; losses: number };
    goal_diff?: number;
    summary?: string;
  };
}

export interface TacticalIntelligence {
  fixture: string;
  league_code: string;
  timestamp: string;
  home: TeamAtmosphere;
  away: TeamAtmosphere;
  atmosphere_differential: {
    home_momentum_score: number;
    away_momentum_score: number;
    net_edge: string;
    verdict: string;
    xg_net_home_bias: number;
    xg_net_away_bias: number;
  };
}

export interface TacticalRecommendation {
  bet: string;
  market: string;
  outcome_code?: string;
  probability: number;
  fair_odds: number;
  badge: string;
  reasoning: string;
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
    lambda_home?: number;
    lambda_away?: number;
  };
  top_3_scorelines: Array<{
    score: string;
    probability_pct: number;
    prob?: number;
  }>;
  penta_consensus: PentaConsensus;
  yellow_cards: YellowCardsData;
  corners?: CornersData;
  alternative_bet_ideas?: SafePick[];
  tactical_intelligence?: TacticalIntelligence;
  tactical_1x2_recommendation?: TacticalRecommendation;
  tactical_dc_recommendation?: TacticalRecommendation;
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
