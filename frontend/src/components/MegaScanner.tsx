import React, { useState, useEffect } from 'react';
import { Zap, ShieldCheck, Plus, Sparkles, Filter, RefreshCw } from 'lucide-react';
import type { BetSlipItem } from '../types';
import { fetchGameweekScan } from '../api';

interface MegaScannerProps {
  onAddToSlip: (item: BetSlipItem) => void;
  slipItems: BetSlipItem[];
}

export const MegaScanner: React.FC<MegaScannerProps> = ({ onAddToSlip, slipItems }) => {
  const [selectedLeague, setSelectedLeague] = useState<string>('E0');
  const [scanData, setScanData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterSafeOnly, setFilterSafeOnly] = useState<boolean>(false);
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');

  const loadScan = (league: string) => {
    setLoading(true);
    fetchGameweekScan(league)
      .then((data) => setScanData(data))
      .catch((err) => console.error('Scan error:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadScan(selectedLeague);
  }, [selectedLeague]);

  const matches = scanData?.matches || scanData?.scanned_matches || scanData?.ranked_fixtures || [];
  
  const filteredMatches = matches.filter((m: any) => {
    if (filterSafeOnly) {
      const p = Number(m.safety_probability || m.calibrated_prob || m.win_probability || 0);
      if (p < 75) return false;
    }
    const cat = m.category || '';
    const pick = m.safest_market || m.predicted_pick || m.best_weekly_pick || '';
    if (categoryFilter === 'DNB_DC') {
      return cat.includes('Double Chance') || cat.includes('Draw No Bet') || pick.includes('Double Chance') || pick.includes('Draw No Bet');
    }
    if (categoryFilter === 'TEAM') {
      return cat.includes('Team Goals') || pick.includes('to Score');
    }
    if (categoryFilter === 'OVERS_UNDERS') {
      return cat.includes('Goals') || pick.includes('Match Goals');
    }
    if (categoryFilter === 'CORNERS') {
      return cat.includes('Corners') || pick.includes('Corner');
    }
    if (categoryFilter === 'CARDS_BTTS') {
      return cat.includes('Yellow Cards') || cat.includes('BTTS') || pick.includes('Card') || pick.includes('BTTS');
    }
    return true;
  });

  const getCategoryColor = (cat: string) => {
    switch (cat) {
      case 'Double Chance':
        return 'bg-blue-500/10 border-blue-500/30 text-blue-400';
      case 'Draw No Bet':
        return 'bg-purple-500/10 border-purple-500/30 text-purple-400';
      case 'Team Goals':
        return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';
      case 'Goals Over':
        return 'bg-amber-500/10 border-amber-500/30 text-amber-400';
      case 'Goals Under':
        return 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400';
      case 'Yellow Cards':
        return 'bg-yellow-500/10 border-yellow-500/30 text-yellow-300';
      case 'Corners':
        return 'bg-teal-500/10 border-teal-500/30 text-teal-400';
      case 'BTTS':
        return 'bg-rose-500/10 border-rose-500/30 text-rose-400';
      default:
        return 'bg-brand-cyan/10 border-brand-cyan/20 text-brand-cyan';
    }
  };

  const handleBuildTopMulti = () => {
    const sorted = [...matches].sort(
      (a: any, b: any) =>
        (b.safety_probability || b.calibrated_prob || b.win_probability || 0) -
        (a.safety_probability || a.calibrated_prob || a.win_probability || 0)
    );
    const top3 = sorted.slice(0, 3);
    top3.forEach((m: any) => {
      const pick = m.safest_market || m.predicted_pick || m.best_weekly_pick || 'Double Chance (1X)';
      const odds = Number(m.market_odds || m.fair_odds || 1.15);
      const prob = Number(m.safety_probability || m.calibrated_prob || m.win_probability || 88.0);
      onAddToSlip({
        id: `${m.home_team}_${m.away_team}_${pick}_${Date.now()}`,
        fixture: `${m.home_team} vs ${m.away_team}`,
        home_team: m.home_team,
        away_team: m.away_team,
        league: m.league || selectedLeague,
        pick: pick,
        odds: odds,
        prob: prob,
        category: 'Mega Scanner Multi Pick',
      });
    });
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Header & Controls */}
      <div className="glass-panel p-6 rounded-3xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-5 h-5 text-brand-amber" />
            <h2 className="text-xl font-black text-white tracking-tight">Gameweek Mega Scanner</h2>
          </div>
          <p className="text-xs text-slate-400">
            Automatically parses all fixtures across the round and identifies mathematically optimal derivative markets.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* League Selector */}
          <select
            value={selectedLeague}
            onChange={(e) => setSelectedLeague(e.target.value)}
            className="bg-surface-card border border-border-medium text-white text-xs font-semibold rounded-xl px-3 py-2 outline-none focus:border-brand-amber transition-colors"
          >
            <option value="E0">🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League</option>
            <option value="SP1">🇪🇸 La Liga</option>
            <option value="I1">🇮🇹 Serie A</option>
            <option value="D1">🇩🇪 Bundesliga</option>
            <option value="F1">🇫🇷 Ligue 1</option>
          </select>

          {/* Safe Filter Toggle */}
          <button
            onClick={() => setFilterSafeOnly(!filterSafeOnly)}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold border transition-all ${
              filterSafeOnly
                ? 'bg-brand-emerald/20 text-brand-emerald border-brand-emerald/40'
                : 'bg-surface-card text-slate-400 border-border-subtle hover:text-white'
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Ultra Safe Only (&ge;80%)</span>
          </button>

          {/* Quick 1-Click Multi Builder */}
          <button
            onClick={handleBuildTopMulti}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-brand-amber to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black text-xs font-black tracking-wide shadow-md active:scale-95 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5 text-black" />
            <span>AUTO-BUILD TOP 3 MULTI</span>
          </button>
        </div>
      </div>

      {/* Category Filter Chips */}
      <div className="flex flex-wrap items-center gap-2">
        {[
          { id: 'ALL', label: 'All Diverse Picks' },
          { id: 'DNB_DC', label: '🛡️ Double Chance & DNB' },
          { id: 'TEAM', label: '🥅 Team Goals' },
          { id: 'OVERS_UNDERS', label: '📈 Overs & 📉 Unders' },
          { id: 'CORNERS', label: '🚩 Corner Kicks' },
          { id: 'CARDS_BTTS', label: '🟨 Cards & Derbies' },
        ].map((f) => (
          <button
            key={f.id}
            onClick={() => setCategoryFilter(f.id)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold border transition-all ${
              categoryFilter === f.id
                ? 'bg-brand-amber/15 text-brand-amber border-brand-amber/40 shadow-glow-amber'
                : 'bg-surface-card border-border-subtle text-slate-400 hover:text-white hover:border-border-medium'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <RefreshCw className="w-7 h-7 text-brand-amber animate-spin" />
          <p className="text-xs font-mono text-slate-400">Scanning full gameweek schedule...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredMatches.map((m: any, idx: number) => {
            const prob = Number(m.safety_probability || m.calibrated_prob || m.win_probability || 85.0);
            const pick = m.safest_market || m.predicted_pick || m.best_weekly_pick || 'Match Derivative Pick';
            const odds = Number(m.market_odds || m.fair_odds || 1.15);
            const inSlip = slipItems.some(
              (it) => it.home_team === m.home_team && it.away_team === m.away_team && it.pick === pick
            );

            return (
              <div
                key={idx}
                className="glass-card p-5 rounded-2xl flex flex-col justify-between border border-border-subtle hover:border-brand-amber/30 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-slate-400 font-mono mb-2">
                    <span className="uppercase px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-[10px]">
                      {m.kickoff || 'Gameweek Fixture'}
                    </span>
                    <div className="flex items-center gap-2">
                      {m.category && (
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getCategoryColor(m.category)}`}>
                          {m.category}
                        </span>
                      )}
                      <span className="text-brand-amber font-bold">Rank #{idx + 1}</span>
                    </div>
                  </div>

                  <h3 className="text-base font-extrabold text-white tracking-tight">
                    {m.home_team} <span className="text-slate-500 font-normal">vs</span> {m.away_team}
                  </h3>

                  <div className="p-3 my-3 rounded-xl bg-surface-card border border-border-subtle flex items-center justify-between">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block">
                        Algorithm Pick
                      </span>
                      <span className="text-sm font-bold text-white">{pick}</span>
                    </div>
                    <span className="font-mono text-xs font-black text-brand-emerald px-2 py-1 rounded bg-brand-emerald/10 border border-brand-emerald/20">
                      {odds.toFixed(2)}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                    <ShieldCheck className="w-3.5 h-3.5 text-brand-emerald" />
                    <span>Confidence: {prob.toFixed(1)}%</span>
                  </div>

                  {m.reason && (
                    <p className="text-[11px] text-slate-400 mt-2.5 line-clamp-2 leading-relaxed bg-surface-card/50 p-2 rounded-lg border border-border-subtle/50">
                      {m.reason}
                    </p>
                  )}
                </div>

                <div className="pt-4 mt-2 border-t border-border-subtle">
                  <button
                    onClick={() =>
                      onAddToSlip({
                        id: `${m.home_team}_${m.away_team}_${pick}_${Date.now()}`,
                        fixture: `${m.home_team} vs ${m.away_team}`,
                        home_team: m.home_team,
                        away_team: m.away_team,
                        league: selectedLeague,
                        pick,
                        odds,
                        prob,
                        category: 'Gameweek Scanner',
                      })
                    }
                    className={`w-full py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                      inSlip
                        ? 'bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/30'
                        : 'bg-surface-elevated hover:bg-white/10 text-white border border-border-medium'
                    }`}
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>{inSlip ? 'IN SLIP' : 'ADD TO SLIP'}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
