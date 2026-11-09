import React from 'react';
import { Target, Zap, BookOpen, Cpu, Ticket, Activity } from 'lucide-react';
import type { LeagueInfo } from '../types';

interface NavbarProps {
  currentSpace: 'matches' | 'scanner' | 'ledger' | 'brain';
  onSelectSpace: (space: 'matches' | 'scanner' | 'ledger' | 'brain') => void;
  leagues: LeagueInfo[];
  selectedLeague: string;
  onSelectLeague: (leagueId: string) => void;
  slipCount: number;
  onToggleSlip: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentSpace,
  onSelectSpace,
  leagues,
  selectedLeague,
  onSelectLeague,
  slipCount,
  onToggleSlip,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-border-subtle px-4 lg:px-8 py-3 transition-all">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand & Terminal Identity */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-emerald/20 via-brand-cyan/20 to-brand-violet/20 border border-brand-cyan/30 flex items-center justify-center shadow-glow-cyan">
            <Activity className="w-5 h-5 text-brand-cyan" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-tight text-white text-base">SYNDICATE</span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded bg-brand-emerald/10 text-brand-emerald border border-brand-emerald/20">
                PRO QUANT V2
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">Dixon-Coles &bull; 5-Way Consensus &bull; Zero Leakage</p>
          </div>
        </div>

        {/* Global Space Navigation */}
        <nav className="flex items-center bg-surface-card p-1 rounded-xl border border-border-subtle shadow-inner">
          <button
            onClick={() => onSelectSpace('matches')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              currentSpace === 'matches'
                ? 'bg-surface-elevated text-white shadow-sm border border-border-medium'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Target className="w-3.5 h-3.5 text-brand-cyan" />
            <span>Match Center</span>
          </button>

          <button
            onClick={() => onSelectSpace('scanner')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              currentSpace === 'scanner'
                ? 'bg-surface-elevated text-white shadow-sm border border-border-medium'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-brand-amber" />
            <span>Mega Scanner</span>
          </button>

          <button
            onClick={() => onSelectSpace('ledger')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              currentSpace === 'ledger'
                ? 'bg-surface-elevated text-white shadow-sm border border-border-medium'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-brand-emerald" />
            <span>Live Ledger</span>
          </button>

          <button
            onClick={() => onSelectSpace('brain')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              currentSpace === 'brain'
                ? 'bg-surface-elevated text-white shadow-sm border border-border-medium'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Cpu className="w-3.5 h-3.5 text-brand-violet" />
            <span>Continuous Brain</span>
          </button>
        </nav>

        {/* League Selector & Floating Betslip Action Button */}
        <div className="flex items-center gap-3">
          {/* League Selector Pills */}
          <div className="hidden sm:flex items-center bg-surface-card p-1 rounded-lg border border-border-subtle">
            {leagues.map((lg) => (
              <button
                key={lg.id}
                onClick={() => onSelectLeague(lg.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs transition-all ${
                  selectedLeague === lg.id
                    ? 'bg-white/10 text-white font-semibold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title={lg.name}
              >
                <span>{lg.flag}</span>
                <span className="hidden md:inline font-mono text-[11px]">{lg.id}</span>
              </button>
            ))}
          </div>

          {/* Active Betslip Pill Trigger */}
          <button
            onClick={onToggleSlip}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-brand-emerald/15 to-brand-cyan/15 hover:from-brand-emerald/25 hover:to-brand-cyan/25 border border-brand-emerald/30 text-white text-xs font-semibold shadow-glow-emerald transition-all active:scale-95"
          >
            <Ticket className="w-4 h-4 text-brand-emerald" />
            <span>Betslip</span>
            {slipCount > 0 && (
              <span className="w-5 h-5 rounded-full bg-brand-emerald text-black text-[11px] font-black flex items-center justify-center">
                {slipCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
