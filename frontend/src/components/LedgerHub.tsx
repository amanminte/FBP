import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  Percent,
  RefreshCw,
  Search,
  ChevronDown,
  MinusCircle,
  Zap,
  X
} from 'lucide-react';
import type { LedgerBet, LedgerSummary } from '../types';
import { fetchLedger, triggerAutoGrade, settleMatchScore } from '../api';

export const LedgerHub: React.FC = () => {
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [ledgerData, setLedgerData] = useState<{ summary: LedgerSummary; bets: LedgerBet[] } | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isGrading, setIsGrading] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedId, setExpandedId] = useState<number | null>(null);

  // Settle modal state
  const [settleModalBet, setSettleModalBet] = useState<LedgerBet | null>(null);
  const [modalScoreH, setModalScoreH] = useState<number>(0);
  const [modalScoreA, setModalScoreA] = useState<number>(0);
  const [modalCardsH, setModalCardsH] = useState<number>(2);
  const [modalCardsA, setModalCardsA] = useState<number>(2);
  const [isSubmittingScore, setIsSubmittingScore] = useState<boolean>(false);

  const loadLedger = (filter: string = filterStatus) => {
    setLoading(true);
    fetchLedger(filter)
      .then((data) => setLedgerData(data))
      .catch((err) => console.error('Ledger error:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadLedger(filterStatus);
  }, [filterStatus]);

  const handleAutoGrade = async () => {
    setIsGrading(true);
    try {
      const res = await triggerAutoGrade();
      let msg = res.message || 'Auto-grading complete!';
      if (res.graded_items && res.graded_items.length > 0) {
        msg += '\n\nSettled Predictions:\n' + res.graded_items.map((it: any) => 
          `• ${it.fixture} (${it.actual_score}) -> ${it.is_hit === 1 ? 'HIT (+'+it.pnl+'u)' : it.is_hit === 2 ? 'PUSH (Refunded)' : 'MISSED ('+it.pnl+'u)'}`
        ).join('\n');
      }
      alert(msg);
      loadLedger();
    } catch (err: any) {
      alert(`Auto-grade error: ${err.message}`);
    } finally {
      setIsGrading(false);
    }
  };

  const openSettleModal = (bet: LedgerBet) => {
    setSettleModalBet(bet);
    setModalScoreH(0);
    setModalScoreA(0);
    setModalCardsH(2);
    setModalCardsA(2);
  };

  const handleManualSettle = async () => {
    if (!settleModalBet) return;
    setIsSubmittingScore(true);
    try {
      const parts = settleModalBet.fixture.split(' vs ');
      const homeTeam = parts[0]?.trim() || '';
      const awayTeam = parts[1]?.trim() || '';

      const res = await settleMatchScore({
        league: settleModalBet.league,
        home_team: homeTeam,
        away_team: awayTeam,
        score_h: Number(modalScoreH),
        score_a: Number(modalScoreA),
        cards_h: Number(modalCardsH),
        cards_a: Number(modalCardsA)
      });

      alert(res.message || `Successfully settled ${homeTeam} ${modalScoreH} - ${modalScoreA} ${awayTeam}!`);
      setSettleModalBet(null);
      loadLedger();
    } catch (err: any) {
      alert(`Settlement failed: ${err.message}`);
    } finally {
      setIsSubmittingScore(false);
    }
  };

  const bets = ledgerData?.bets || [];
  const summary = ledgerData?.summary;

  const filteredBets = bets.filter((b) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      b.fixture.toLowerCase().includes(q) ||
      b.predicted_pick.toLowerCase().includes(q) ||
      b.league.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6 pb-20">
      {/* 1. Header & Summary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Win Rate */}
        <div className="glass-panel p-5 rounded-2xl border border-border-subtle">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>STRIKE RATE</span>
            <Percent className="w-4 h-4 text-brand-emerald" />
          </div>
          <div className="text-2xl md:text-3xl font-black text-brand-emerald font-mono">
            {summary?.win_rate_pct?.toFixed(1) || '0.0'}%
          </div>
          <span className="text-[11px] text-slate-500 font-mono mt-1 block">
            {summary?.settled_count || 0} Settled Bets
          </span>
        </div>

        {/* Total Bets */}
        <div className="glass-panel p-5 rounded-2xl border border-border-subtle">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>TOTAL LOGGED</span>
            <BookOpen className="w-4 h-4 text-brand-cyan" />
          </div>
          <div className="text-2xl md:text-3xl font-black text-white font-mono">
            {summary?.total_predictions || bets.length}
          </div>
          <span className="text-[11px] text-slate-500 font-mono mt-1 block">
            Immutable SQLite Ledger
          </span>
        </div>

        {/* Beat CLV Rate */}
        <div className="glass-panel p-5 rounded-2xl border border-border-subtle">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>BEAT CLV RATE</span>
            <TrendingUp className="w-4 h-4 text-brand-violet" />
          </div>
          <div className="text-2xl md:text-3xl font-black text-brand-violet font-mono">
            {summary?.beat_clv_rate_pct?.toFixed(1) || '0.0'}%
          </div>
          <span className="text-[11px] text-slate-500 font-mono mt-1 block">
            Avg CLV: +{summary?.avg_clv_pct?.toFixed(2) || '0.00'}%
          </span>
        </div>

        {/* Net PnL */}
        <div className="glass-panel p-5 rounded-2xl border border-border-subtle">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>NET FLAT P/L</span>
            <span className="text-xs font-mono font-bold text-slate-400">UNITS</span>
          </div>
          <div
            className={`text-2xl md:text-3xl font-black font-mono ${
              (summary?.total_flat_pnl || 0) >= 0 ? 'text-brand-emerald' : 'text-slate-300'
            }`}
          >
            {(summary?.total_flat_pnl || 0) >= 0 ? '+' : ''}
            {summary?.total_flat_pnl?.toFixed(2) || '0.00'}u
          </div>
          <span className="text-[11px] text-slate-500 font-mono mt-1 block">
            ROI: {summary?.flat_roi_pct?.toFixed(2) || '0.00'}%
          </span>
        </div>
      </div>

      {/* 2. Controls & Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Quick Filter Tabs */}
        <div className="flex items-center gap-1 bg-surface-card p-1 rounded-xl border border-border-subtle">
          {['ALL', 'SETTLED', 'PENDING'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                filterStatus === st
                  ? 'bg-white/10 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {st === 'ALL' ? 'All Bets' : st === 'SETTLED' ? 'Settled Hits/Misses' : 'Pending Only'}
            </button>
          ))}
        </div>

        {/* Search & Auto-Grade Action */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-60">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by fixture or pick..."
              className="w-full bg-surface-card border border-border-subtle rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 outline-none focus:border-brand-emerald transition-colors"
            />
          </div>

          <button
            onClick={handleAutoGrade}
            disabled={isGrading}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-card hover:bg-surface-elevated border border-border-medium text-xs font-bold text-white transition-all disabled:opacity-50"
            title="Auto-grade pending predictions from verified fixtures"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-brand-emerald ${isGrading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Auto-Grade</span>
          </button>
        </div>
      </div>

      {/* 3. Clean Performance Table */}
      <div className="glass-panel rounded-3xl overflow-hidden border border-border-subtle">
        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center gap-3">
            <div className="w-7 h-7 rounded-full border-2 border-brand-emerald border-t-transparent animate-spin" />
            <p className="text-xs font-mono text-slate-400">Loading ledger records from SQLite...</p>
          </div>
        ) : filteredBets.length === 0 ? (
          <div className="py-16 text-center text-slate-400 text-xs font-mono">
            No matching predictions found in this view.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border-subtle bg-surface-card/60 text-slate-400 font-mono text-[11px] uppercase tracking-wider">
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-3">League</th>
                  <th className="py-3 px-4">Fixture</th>
                  <th className="py-3 px-4">Predicted Pick</th>
                  <th className="py-3 px-3">Odds (Prob)</th>
                  <th className="py-3 px-3">Actual Score</th>
                  <th className="py-3 px-4 text-right">Profit / Loss</th>
                  <th className="py-3 px-2"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle font-sans">
                {filteredBets.map((b) => {
                  const isExpanded = expandedId === b.id;
                  return (
                    <React.Fragment key={b.id}>
                      <tr
                        onClick={() => setExpandedId(isExpanded ? null : b.id)}
                        className="hover:bg-white/[0.02] cursor-pointer transition-colors"
                      >
                        {/* Status Badge */}
                        <td className="py-3 px-4">
                          {b.is_hit === 1 ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold text-[11px]">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>HIT</span>
                            </span>
                          ) : b.is_hit === 2 ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-bold text-[11px]" title="Stake Refunded (Push)">
                              <MinusCircle className="w-3.5 h-3.5" />
                              <span>PUSH</span>
                            </span>
                          ) : b.is_hit === 0 ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 font-bold text-[11px]">
                              <XCircle className="w-3.5 h-3.5" />
                              <span>MISSED</span>
                            </span>
                          ) : (
                            <div className="flex items-center gap-2">
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold text-[11px]">
                                <Clock className="w-3.5 h-3.5" />
                                <span>PENDING</span>
                              </span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  openSettleModal(b);
                                }}
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-brand-emerald/10 hover:bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/30 text-[11px] font-bold transition-all shadow-sm"
                                title="Enter verified final score to settle immediately"
                              >
                                <Zap className="w-3 h-3" />
                                <span>Settle</span>
                              </button>
                            </div>
                          )}
                        </td>

                        {/* League */}
                        <td className="py-3 px-3 font-mono text-[11px] text-slate-400">
                          {b.league}
                        </td>

                        {/* Fixture */}
                        <td className="py-3 px-4 font-bold text-white">
                          {b.fixture}
                        </td>

                        {/* Pick */}
                        <td className="py-3 px-4 text-slate-200 font-medium">
                          {b.predicted_pick}
                        </td>

                        {/* Odds & Win Prob */}
                        <td className="py-3 px-3 font-mono">
                          <span className="text-white font-bold">{Number(b.opening_odds || 1.0).toFixed(2)}</span>{' '}
                          <span className="text-slate-500 text-[11px]">({b.calibrated_prob}%)</span>
                        </td>

                        {/* Actual Score */}
                        <td className="py-3 px-3 font-mono text-slate-300 font-semibold">
                          {b.actual_score || '—'}
                        </td>

                        {/* PnL */}
                        <td className="py-3 px-4 text-right font-mono font-bold">
                          {b.is_hit === 1 ? (
                            <span className="text-emerald-400">+{Number(b.pnl || 0).toFixed(2)}u</span>
                          ) : b.is_hit === 2 ? (
                            <span className="text-cyan-400">0.00u</span>
                          ) : b.is_hit === 0 ? (
                            <span className="text-rose-400">{Number(b.pnl || 0).toFixed(2)}u</span>
                          ) : (
                            <span className="text-slate-500">—</span>
                          )}
                        </td>

                        {/* Expand Icon */}
                        <td className="py-3 px-2 text-slate-500 text-right pr-4">
                          <ChevronDown
                            className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                          />
                        </td>
                      </tr>

                      {/* Expandable Quant Drill-down */}
                      {isExpanded && (
                        <tr className="bg-surface-elevated/40 border-b border-border-subtle">
                          <td colSpan={8} className="p-4">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono bg-surface-card p-4 rounded-xl border border-border-subtle">
                              <div>
                                <span className="text-slate-500 block">RECORD ID & DATE:</span>
                                <span className="text-white font-bold">
                                  #{b.id} &bull; {b.match_date} ({b.created_at?.split('.')[0]})
                                </span>
                              </div>
                              <div>
                                <span className="text-slate-500 block">MODEL TRACK:</span>
                                <span className="text-brand-cyan font-bold">{b.model_track}</span>
                              </div>
                              <div>
                                <span className="text-slate-500 block">ACTUAL OUTCOME STRING:</span>
                                <span className="text-white font-bold">{b.actual_outcome || 'Pending Kickoff'}</span>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Manual Settlement Modal */}
      {settleModalBet && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-surface-card border border-border-medium rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-border-subtle pb-3">
              <div>
                <span className="text-[10px] font-mono text-brand-emerald uppercase tracking-wider font-bold">
                  Instant Match Settlement
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">
                  {settleModalBet.fixture}
                </h3>
              </div>
              <button
                onClick={() => setSettleModalBet(null)}
                className="p-1 rounded-lg hover:bg-surface-elevated text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-3 bg-surface-elevated/50 rounded-xl border border-border-subtle text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Locked Pick:</span>
                <span className="text-brand-cyan font-semibold">{settleModalBet.predicted_pick}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Odds / Stake:</span>
                <span className="text-white font-mono">{Number(settleModalBet.opening_odds).toFixed(2)} @ {settleModalBet.stake_units}u</span>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-mono text-slate-300 mb-2">
                  FINAL MATCH SCORE (Home - Away)
                </label>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <span className="text-[11px] text-slate-400 block mb-1 truncate">
                      {settleModalBet.fixture.split(' vs ')[0]}
                    </span>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={modalScoreH}
                      onChange={(e) => setModalScoreH(parseInt(e.target.value) || 0)}
                      className="w-full bg-surface-elevated border border-border-subtle rounded-xl px-3 py-2 text-center text-lg font-bold text-white focus:border-brand-emerald outline-none font-mono"
                    />
                  </div>
                  <span className="text-slate-500 font-bold text-xl pt-4">:</span>
                  <div className="flex-1">
                    <span className="text-[11px] text-slate-400 block mb-1 truncate">
                      {settleModalBet.fixture.split(' vs ')[1]}
                    </span>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={modalScoreA}
                      onChange={(e) => setModalScoreA(parseInt(e.target.value) || 0)}
                      className="w-full bg-surface-elevated border border-border-subtle rounded-xl px-3 py-2 text-center text-lg font-bold text-white focus:border-brand-emerald outline-none font-mono"
                    />
                  </div>
                </div>
              </div>

              {settleModalBet.predicted_pick.toLowerCase().includes('card') && (
                <div>
                  <label className="block text-xs font-mono text-slate-300 mb-2">
                    TOTAL YELLOW CARDS (Derby Market)
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <span className="text-[11px] text-slate-400 block mb-1">Home Cards</span>
                      <input
                        type="number"
                        min="0"
                        value={modalCardsH}
                        onChange={(e) => setModalCardsH(parseInt(e.target.value) || 0)}
                        className="w-full bg-surface-elevated border border-border-subtle rounded-xl px-3 py-2 text-center font-mono text-sm text-white focus:border-brand-emerald outline-none"
                      />
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-400 block mb-1">Away Cards</span>
                      <input
                        type="number"
                        min="0"
                        value={modalCardsA}
                        onChange={(e) => setModalCardsA(parseInt(e.target.value) || 0)}
                        className="w-full bg-surface-elevated border border-border-subtle rounded-xl px-3 py-2 text-center font-mono text-sm text-white focus:border-brand-emerald outline-none"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-border-subtle">
              <button
                type="button"
                onClick={() => setSettleModalBet(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleManualSettle}
                disabled={isSubmittingScore}
                className="px-5 py-2 rounded-xl bg-brand-emerald text-brand-dark font-bold text-xs hover:bg-emerald-400 transition-all flex items-center gap-2 disabled:opacity-50"
              >
                {isSubmittingScore ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Grading...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Grade & Calibrate</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
