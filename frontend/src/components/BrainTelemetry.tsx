import React, { useState, useEffect } from 'react';
import { Cpu, TrendingUp, TrendingDown, Activity, Award } from 'lucide-react';
import type { ContinuousLearningSummary } from '../types';
import { fetchLearningSummary } from '../api';

export const BrainTelemetry: React.FC = () => {
  const [data, setData] = useState<ContinuousLearningSummary | null>(null);

  useEffect(() => {
    fetchLearningSummary()
      .then((res) => setData(res))
      .catch((err) => console.error('Learning summary error:', err));
  }, []);

  return (
    <div className="space-y-6 pb-20">
      {/* 1. Header & KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total Learned */}
        <div className="glass-panel p-5 rounded-2xl border border-border-subtle">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>MATCHES ABSORBED</span>
            <Cpu className="w-4 h-4 text-brand-violet" />
          </div>
          <div className="text-2xl md:text-3xl font-black text-brand-violet font-mono">
            {data?.total_matches_learned || 0}
          </div>
          <span className="text-[11px] text-slate-500 font-mono mt-1 block">
            Online Bayesian Updates
          </span>
        </div>

        {/* Avg Brier Score */}
        <div className="glass-panel p-5 rounded-2xl border border-border-subtle">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>RESIDUAL BRIER LOSS</span>
            <Activity className="w-4 h-4 text-brand-cyan" />
          </div>
          <div className="text-2xl md:text-3xl font-black text-brand-cyan font-mono">
            {data?.average_brier_score?.toFixed(4) || '0.0000'}
          </div>
          <span className="text-[11px] text-slate-500 font-mono mt-1 block">
            Multi-class Calibration Error
          </span>
        </div>

        {/* Temperature Scaling */}
        <div className="glass-panel p-5 rounded-2xl border border-border-subtle">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>TEMPERATURE (T)</span>
            <Award className="w-4 h-4 text-brand-amber" />
          </div>
          <div className="text-2xl md:text-3xl font-black text-brand-amber font-mono">
            {data?.temperature_adjustment?.toFixed(2) || '1.00'}
          </div>
          <span className="text-[11px] text-slate-500 font-mono mt-1 block">
            Adaptive Platt Sharpness
          </span>
        </div>

        {/* Status */}
        <div className="glass-panel p-5 rounded-2xl border border-border-subtle">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>ONLINE STATE</span>
            <div className="w-2.5 h-2.5 rounded-full bg-brand-emerald animate-pulse" />
          </div>
          <div className="text-xl md:text-2xl font-black text-brand-emerald font-mono">
            ACTIVE LEARNER
          </div>
          <span className="text-[11px] text-slate-500 font-mono mt-1 block">
            Zero-Leakage Invariance
          </span>
        </div>
      </div>

      {/* 2. Top Elo Momentum Drifts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Rising Teams */}
        <div className="glass-panel p-6 rounded-3xl border border-border-subtle">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-brand-emerald" />
            <h3 className="text-base font-extrabold text-white tracking-tight">
              Top Momentum Gainers (Elo Drift)
            </h3>
          </div>

          <div className="space-y-3">
            {data?.top_positive_elo_drifts?.slice(0, 5).map(([team, drift], idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-surface-card border border-border-subtle flex items-center justify-between"
              >
                <div className="flex items-center gap-2.5">
                  <span className="font-mono text-xs text-slate-500 w-4">#{idx + 1}</span>
                  <span className="text-sm font-bold text-white">{team}</span>
                </div>
                <span className="font-mono text-xs font-black text-brand-emerald bg-brand-emerald/10 px-2 py-0.5 rounded border border-brand-emerald/20">
                  +{drift.toFixed(1)} pts
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Dropping Teams */}
        <div className="glass-panel p-6 rounded-3xl border border-border-subtle">
          <div className="flex items-center gap-2 mb-4">
            <TrendingDown className="w-5 h-5 text-brand-rose" />
            <h3 className="text-base font-extrabold text-white tracking-tight">
              Teams Experiencing Negative Drift
            </h3>
          </div>

          <div className="space-y-3">
            {data?.top_negative_elo_drifts?.slice(0, 5).map(([team, drift], idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-surface-card border border-border-subtle flex items-center justify-between"
              >
                <div className="flex items-center gap-2.5">
                  <span className="font-mono text-xs text-slate-500 w-4">#{idx + 1}</span>
                  <span className="text-sm font-bold text-white">{team}</span>
                </div>
                <span className="font-mono text-xs font-black text-brand-rose bg-brand-rose/10 px-2 py-0.5 rounded border border-brand-rose/20">
                  {drift.toFixed(1)} pts
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 3. Recent Learning Log */}
      {data?.recent_log && data.recent_log.length > 0 && (
        <div className="glass-panel p-6 rounded-3xl border border-border-subtle">
          <h3 className="text-base font-extrabold text-white tracking-tight mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4 text-brand-violet" />
            <span>Recent Match Learning Stream</span>
          </h3>

          <div className="space-y-2">
            {data.recent_log.slice(0, 8).map((log, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-surface-card border border-border-subtle flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs font-mono"
              >
                <div className="flex items-center gap-3">
                  <span className="text-slate-500 font-bold">{log.actual}</span>
                  <span className="text-white font-bold">{log.fixture}</span>
                </div>

                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300 font-bold">
                    Score: {log.score}
                  </span>
                  <span className="text-brand-cyan">{log.elo_delta}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
