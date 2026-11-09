import type {
  LeagueInfo,
  FixtureMatch,
  MatchPrediction,
  LedgerBet,
  LedgerSummary,
  ContinuousLearningSummary
} from './types';

const BASE_URL = '/api';

export async function fetchLeagues(): Promise<LeagueInfo[]> {
  const res = await fetch(`${BASE_URL}/leagues`);
  if (!res.ok) throw new Error('Failed to fetch leagues');
  return res.json();
}

export async function fetchFixtures(league: string): Promise<{ league: string; gameweeks: Array<{ gameweek: string; matches: FixtureMatch[] }> }> {
  const res = await fetch(`${BASE_URL}/fixtures/${league}`);
  if (!res.ok) throw new Error(`Failed to fetch fixtures for ${league}`);
  return res.json();
}

export async function predictMatch(params: {
  home_team: string;
  away_team: string;
  league: string;
  model_track?: string;
  home_missing?: string[];
  away_missing?: string[];
}): Promise<MatchPrediction> {
  const res = await fetch(`${BASE_URL}/predict/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate match prediction');
  }
  return res.json();
}

export async function fetchLedger(filterStatus: string = 'ALL'): Promise<{ summary: LedgerSummary; bets: LedgerBet[] }> {
  const res = await fetch(`${BASE_URL}/ledger?filter_status=${filterStatus}`);
  if (!res.ok) throw new Error('Failed to fetch ledger');
  return res.json();
}

export async function lockBetToLedger(bet: {
  match_date: string;
  league: string;
  home_team: string;
  away_team: string;
  model_track: string;
  predicted_pick: string;
  calibrated_prob: number;
  opening_odds: number;
  stake_units?: number;
}): Promise<{ success: boolean; ledger_id: number; message: string }> {
  const res = await fetch(`${BASE_URL}/ledger/lock`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bet),
  });
  if (!res.ok) throw new Error('Failed to lock bet to ledger');
  return res.json();
}

export async function triggerAutoGrade(): Promise<{ graded_count: number; message: string }> {
  const res = await fetch(`${BASE_URL}/ledger/auto-grade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error('Failed to auto-grade ledger');
  return res.json();
}

export async function fetchLearningSummary(): Promise<ContinuousLearningSummary> {
  const res = await fetch(`${BASE_URL}/continuous-learning/summary`);
  if (!res.ok) throw new Error('Failed to fetch learning summary');
  return res.json();
}

export async function fetchGameweekScan(league: string = 'E0'): Promise<any> {
  const res = await fetch(`${BASE_URL}/scanner/${league}`);
  if (!res.ok) throw new Error(`Failed to scan gameweek for ${league}`);
  return res.json();
}
