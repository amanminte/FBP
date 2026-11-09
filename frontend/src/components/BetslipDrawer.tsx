import React, { useState } from 'react';
import { X, Trash2, ShieldCheck, CheckCircle2, ChevronRight, Lock } from 'lucide-react';
import type { BetSlipItem } from '../types';
import { lockBetToLedger } from '../api';

interface BetslipDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  items: BetSlipItem[];
  onRemoveItem: (id: string) => void;
  onClearSlip: () => void;
  onBetLockedSuccess: (msg: string) => void;
}

export const BetslipDrawer: React.FC<BetslipDrawerProps> = ({
  isOpen,
  onClose,
  items,
  onRemoveItem,
  onClearSlip,
  onBetLockedSuccess,
}) => {
  const [stakeMode, setStakeMode] = useState<'flat' | 'kelly' | 'custom'>('flat');
  const [customStake] = useState<number>(1.0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  // Compute Combined Multi Odds
  const combinedOdds = items.reduce((acc, it) => acc * it.odds, 1.0);
  const combinedProb = items.reduce((acc, it) => acc * (it.prob / 100.0), 1.0) * 100.0;

  // Stake calculation
  const currentStake =
    stakeMode === 'flat' ? 1.0 : stakeMode === 'kelly' ? Math.max(0.5, Math.min(2.5, 1.25)) : customStake;

  const potentialPayout = currentStake * (items.length > 1 ? combinedOdds : items[0]?.odds || 1.0);

  const handleLockBets = async () => {
    if (items.length === 0) return;
    setIsSubmitting(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      for (const item of items) {
        await lockBetToLedger({
          match_date: today,
          league: item.league,
          home_team: item.home_team,
          away_team: item.away_team,
          model_track: item.category || 'Top Safe Pick',
          predicted_pick: item.pick,
          calibrated_prob: item.prob,
          opening_odds: item.odds,
          stake_units: currentStake,
        });
      }
      onBetLockedSuccess(`Successfully locked ${items.length} pick(s) into Live Ledger!`);
      onClearSlip();
      onClose();
    } catch (err: any) {
      alert(`Error locking bets: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[420px] glass-panel border-l border-border-medium bg-surface/95 backdrop-blur-2xl shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-subtle">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-brand-emerald animate-pulse" />
          <h3 className="font-extrabold text-white text-sm tracking-wide">ACTIVE SYNDICATE SLIP</h3>
          <span className="px-2 py-0.5 rounded-full bg-brand-emerald/10 text-brand-emerald text-xs font-mono font-bold">
            {items.length} {items.length === 1 ? 'Pick' : 'Picks'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {items.length > 0 && (
            <button
              onClick={onClearSlip}
              className="p-1.5 text-slate-400 hover:text-brand-rose transition-colors"
              title="Clear Slip"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Slip Items List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {items.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
            <div className="w-12 h-12 rounded-2xl bg-surface-card border border-border-subtle flex items-center justify-center mb-3 text-slate-500">
              <Lock className="w-6 h-6" />
            </div>
            <p className="text-sm font-medium text-slate-300">Your betslip is currently empty</p>
            <p className="text-xs text-slate-500 mt-1 max-w-[240px]">
              Click "+ Add to Slip" on any Safest Pick, Penta Consensus, or Alternative Bet to begin building your ticket.
            </p>
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              className="p-3.5 rounded-xl bg-surface-card border border-border-subtle hover:border-border-bright transition-all relative group"
            >
              <button
                onClick={() => onRemoveItem(item.id)}
                className="absolute top-2.5 right-2.5 text-slate-500 hover:text-brand-rose transition-colors opacity-0 group-hover:opacity-100"
              >
                <X className="w-4 h-4" />
              </button>

              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/5 text-slate-400 border border-white/10">
                  {item.league}
                </span>
                <span className="text-xs text-slate-400 font-medium truncate max-w-[200px]">
                  {item.fixture}
                </span>
              </div>

              <div className="text-sm font-bold text-white tracking-tight mt-1 flex items-center justify-between">
                <span>{item.pick}</span>
                <span className="font-mono text-brand-emerald text-sm bg-brand-emerald/10 px-2 py-0.5 rounded border border-brand-emerald/20">
                  {item.odds.toFixed(2)}
                </span>
              </div>

              <div className="flex items-center gap-2 mt-2 text-[11px] text-slate-400 font-mono">
                <ShieldCheck className="w-3.5 h-3.5 text-brand-cyan" />
                <span>Win Prob: {item.prob.toFixed(1)}%</span>
                <span className="text-slate-600">&bull;</span>
                <span className="text-slate-500">{item.category}</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Slip Footer / Multi Calculations */}
      {items.length > 0 && (
        <div className="p-4 border-t border-border-subtle bg-surface-elevated/70 space-y-3">
          {/* Multi / Accumulator Stats */}
          {items.length > 1 && (
            <div className="p-3 rounded-xl bg-brand-violet/10 border border-brand-violet/20 flex items-center justify-between">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-brand-violet block">
                  COMBINED PARLAY ODDS
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Est. Joint Safety: {combinedProb.toFixed(1)}%
                </span>
              </div>
              <span className="font-mono text-lg font-black text-white">
                {combinedOdds.toFixed(2)}x
              </span>
            </div>
          )}

          {/* Staking Sizer Controls */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-300">Staking Model:</span>
              <div className="flex items-center gap-1 bg-surface-card p-0.5 rounded-lg border border-border-subtle">
                <button
                  onClick={() => setStakeMode('flat')}
                  className={`px-2 py-0.5 rounded text-[11px] font-mono transition-all ${
                    stakeMode === 'flat' ? 'bg-white/10 text-white font-bold' : 'text-slate-400'
                  }`}
                >
                  Flat 1.0u
                </button>
                <button
                  onClick={() => setStakeMode('kelly')}
                  className={`px-2 py-0.5 rounded text-[11px] font-mono transition-all ${
                    stakeMode === 'kelly' ? 'bg-white/10 text-white font-bold' : 'text-slate-400'
                  }`}
                >
                  Kelly
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400 font-mono py-1">
              <span>Allocated Stake:</span>
              <span className="text-white font-bold">{currentStake.toFixed(2)} units</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono py-1">
              <span>Potential Return:</span>
              <span className="text-brand-emerald font-black text-sm">
                +{potentialPayout.toFixed(2)} units
              </span>
            </div>
          </div>

          {/* Lock Action Button */}
          <button
            onClick={handleLockBets}
            disabled={isSubmitting}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-brand-emerald to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-black font-extrabold text-sm tracking-wide shadow-glow-emerald flex items-center justify-center gap-2 active:scale-98 transition-all disabled:opacity-50"
          >
            {isSubmitting ? (
              <span>Locking Bets to Ledger...</span>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4 text-black" />
                <span>LOCK {items.length} {items.length === 1 ? 'BET' : 'BETS'} TO LIVE LEDGER</span>
                <ChevronRight className="w-4 h-4 text-black" />
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};
