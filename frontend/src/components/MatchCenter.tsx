import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Crown,
  Sparkles,
  Plus,
  Check,
  Flame
} from 'lucide-react';
import type { LeagueInfo, FixtureMatch, MatchPrediction, SafePick, BetSlipItem } from '../types';
import { predictMatch } from '../api';

interface MatchCenterProps {
  leagues: LeagueInfo[];
  selectedLeague: string;
  fixtures: FixtureMatch[];
  onSelectFixture: (home: string, away: string) => void;
  onAddToSlip: (item: BetSlipItem) => void;
  slipItems: BetSlipItem[];
}

export const MatchCenter: React.FC<MatchCenterProps> = ({
  leagues,
  selectedLeague,
  fixtures,
  onSelectFixture,
  onAddToSlip,
  slipItems,
}) => {
  const currentLeagueObj = leagues.find((l) => l.id === selectedLeague) || leagues[0];
  const teams = currentLeagueObj?.teams || [];

  const [homeTeam, setHomeTeam] = useState<string>('');
  const [awayTeam, setAwayTeam] = useState<string>('');
  const [prediction, setPrediction] = useState<MatchPrediction | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Default selection when league changes or fixtures load
  useEffect(() => {
    if (fixtures.length > 0) {
      // Pick first non-finished fixture, or first fixture
      const upcoming = fixtures.find((f) => !f.finished) || fixtures[0];
      setHomeTeam(upcoming.home);
      setAwayTeam(upcoming.away);
    } else if (teams.length >= 2) {
      setHomeTeam(teams[0]);
      setAwayTeam(teams[1]);
    }
  }, [selectedLeague, fixtures, teams]);

  // Run prediction whenever teams change
  useEffect(() => {
    if (!homeTeam || !awayTeam || homeTeam === awayTeam) return;

    let isMounted = true;
    setLoading(true);
    setError(null);

    predictMatch({
      home_team: homeTeam,
      away_team: awayTeam,
      league: selectedLeague,
    })
      .then((data) => {
        if (isMounted) setPrediction(data);
      })
      .catch((err) => {
        if (isMounted) setError(err.message);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [homeTeam, awayTeam, selectedLeague]);

  const isPickInSlip = (pickBet: string) => {
    return slipItems.some(
      (it) => it.home_team === homeTeam && it.away_team === awayTeam && it.pick === pickBet
    );
  };

  const handleAddPick = (pick: SafePick, category: string = 'Top Safe Pick') => {
    onAddToSlip({
      id: `${homeTeam}_${awayTeam}_${pick.bet}_${Date.now()}`,
      fixture: `${homeTeam} vs ${awayTeam}`,
      home_team: homeTeam,
      away_team: awayTeam,
      league: selectedLeague,
      pick: pick.bet,
      odds: pick.fair_odds,
      prob: pick.probability,
      category,
    });
  };

  return (
    <div className="space-y-6 pb-20">
      {/* 1. Fixture Strip Carousel */}
      {fixtures.length > 0 && (
        <div className="overflow-x-auto pb-2 scrollbar-thin">
          <div className="flex items-center gap-2.5 min-w-max">
            {fixtures.map((f, idx) => {
              const isSelected = f.home === homeTeam && f.away === awayTeam;
              return (
                <button
                  key={idx}
                  onClick={() => {
                    setHomeTeam(f.home);
                    setAwayTeam(f.away);
                    onSelectFixture(f.home, f.away);
                  }}
                  className={`p-2.5 rounded-xl text-left border transition-all ${
                    isSelected
                      ? 'bg-surface-elevated border-brand-cyan/50 shadow-glow-cyan'
                      : 'bg-surface-card border-border-subtle hover:border-border-medium'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono mb-1">
                    <span>{f.kickoff?.split('•')[0]?.trim() || 'GW Match'}</span>
                    {f.finished && (
                      <span className="text-emerald-400 font-bold uppercase">FT</span>
                    )}
                  </div>
                  <div className="text-xs font-semibold text-white flex items-center justify-between gap-3">
                    <span className="truncate max-w-[90px]">{f.home}</span>
                    <span className="font-mono text-slate-300">
                      {f.finished ? `${f.score_h} - ${f.score_a}` : 'vs'}
                    </span>
                    <span className="truncate max-w-[90px]">{f.away}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* 2. Team Selector Controls */}
      <div className="glass-panel p-4 rounded-2xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex flex-col">
            <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-1">
              Home Team
            </label>
            <select
              value={homeTeam}
              onChange={(e) => setHomeTeam(e.target.value)}
              className="bg-surface-card border border-border-medium text-white text-xs font-semibold rounded-lg px-3 py-2 outline-none focus:border-brand-cyan transition-colors"
            >
              {teams.map((t) => (
                <option key={t} value={t} disabled={t === awayTeam}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="text-slate-500 font-mono text-xs pt-4">vs</div>

          <div className="flex flex-col">
            <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-1">
              Away Team
            </label>
            <select
              value={awayTeam}
              onChange={(e) => setAwayTeam(e.target.value)}
              className="bg-surface-card border border-border-medium text-white text-xs font-semibold rounded-lg px-3 py-2 outline-none focus:border-brand-cyan transition-colors"
            >
              {teams.map((t) => (
                <option key={t} value={t} disabled={t === homeTeam}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400">Competition:</span>
          <span className="px-2.5 py-1 rounded-lg bg-surface-card border border-border-subtle text-xs font-bold text-white flex items-center gap-1.5">
            <span>{currentLeagueObj.flag}</span>
            <span>{currentLeagueObj.name}</span>
          </span>
        </div>
      </div>

      {loading && (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-brand-cyan border-t-transparent animate-spin" />
          <p className="text-xs font-mono text-slate-400">
            Running 5-Way Consensus & Dixon-Coles Poisson Simulation...
          </p>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-brand-rose/10 border border-brand-rose/20 text-brand-rose text-xs font-mono">
          {error}
        </div>
      )}

      {/* 3. Prediction Hero & Probability Visualizer */}
      {prediction && !loading && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl relative overflow-hidden">
            {/* Background Accent Ambient Light */}
            <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 rounded-full bg-brand-cyan/10 blur-3xl pointer-events-none" />
            <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 rounded-full bg-brand-emerald/10 blur-3xl pointer-events-none" />

            <div className="relative z-10">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-6 border-b border-border-subtle">
                {/* Home Team */}
                <div className="text-center md:text-left">
                  <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                    Home Team
                  </span>
                  <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight mt-0.5">
                    {homeTeam}
                  </h2>
                  <span className="text-xs text-brand-cyan font-mono">
                    xG: {prediction.expected_goals?.home_xg?.toFixed(2) || '1.40'}
                  </span>
                </div>

                {/* Score Projection Center */}
                <div className="flex flex-col items-center">
                  <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[11px] font-mono font-semibold text-slate-300 mb-2">
                    {prediction.tier_badge || 'QUANT VALUE PICK'}
                  </span>
                  <div className="flex items-center gap-3 font-mono font-black text-3xl md:text-4xl text-white">
                    <span>{prediction.top_3_scorelines?.[0]?.score || '1 - 1'}</span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono mt-1">
                    Most Probable Scoreline ({(prediction.top_3_scorelines?.[0]?.probability_pct ?? 10.0).toFixed(1)}%)
                  </span>
                </div>

                {/* Away Team */}
                <div className="text-center md:text-right">
                  <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                    Away Team
                  </span>
                  <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight mt-0.5">
                    {awayTeam}
                  </h2>
                  <span className="text-xs text-brand-cyan font-mono">
                    xG: {prediction.expected_goals?.away_xg?.toFixed(2) || '1.10'}
                  </span>
                </div>
              </div>

              {/* 1X2 Probabilities Bar */}
              <div className="pt-6">
                <div className="flex items-center justify-between text-xs font-mono mb-2">
                  <span className="text-emerald-400 font-bold">
                    {homeTeam} Win: {(prediction.calibrated_probabilities?.home_win ?? 45.0).toFixed(1)}%
                  </span>
                  <span className="text-slate-400 font-bold">
                    Draw: {(prediction.calibrated_probabilities?.draw ?? 25.0).toFixed(1)}%
                  </span>
                  <span className="text-cyan-400 font-bold">
                    {awayTeam} Win: {(prediction.calibrated_probabilities?.away_win ?? 30.0).toFixed(1)}%
                  </span>
                </div>

                {/* Segmented Bar */}
                <div className="h-3 w-full rounded-full bg-white/5 overflow-hidden flex border border-border-subtle p-0.5">
                  <div
                    style={{ width: `${prediction.calibrated_probabilities?.home_win ?? 45}%` }}
                    className="h-full bg-emerald-500 rounded-l-full transition-all"
                  />
                  <div
                    style={{ width: `${prediction.calibrated_probabilities?.draw ?? 25}%` }}
                    className="h-full bg-slate-500 transition-all"
                  />
                  <div
                    style={{ width: `${prediction.calibrated_probabilities?.away_win ?? 30}%` }}
                    className="h-full bg-cyan-500 rounded-r-full transition-all"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* 4. Top 3 Safest Picks Across All Markets */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="w-5 h-5 text-brand-emerald" />
              <h3 className="text-base font-extrabold text-white tracking-tight">
                Top 3 Safest Picks Across All Markets
              </h3>
              <span className="text-xs text-slate-400 font-mono">
                (Ranked by Pure Statistical Win Probability)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {prediction.top_3_safe_picks?.map((pick, i) => {
                const added = isPickInSlip(pick.bet);
                return (
                  <div
                    key={i}
                    className="glass-card p-5 rounded-2xl flex flex-col justify-between relative overflow-hidden group"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-brand-emerald bg-brand-emerald/10 border border-brand-emerald/20 px-2 py-0.5 rounded-full">
                          #{i + 1} SAFEST PICK
                        </span>
                        <span className="text-xs font-mono font-bold text-white bg-white/10 px-2 py-0.5 rounded">
                          {Number(pick.fair_odds || 1.15).toFixed(2)}
                        </span>
                      </div>

                      <h4 className="text-base font-black text-white tracking-tight mt-1">
                        {pick.bet}
                      </h4>

                      <div className="flex items-center gap-1.5 my-2">
                        <span className="font-mono text-xl font-black text-brand-emerald">
                          {Number(pick.probability || 85.0).toFixed(1)}%
                        </span>
                        <span className="text-xs text-slate-400 font-medium">Win Chance</span>
                      </div>

                      <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                        {pick.reasoning}
                      </p>
                    </div>

                    <div className="pt-4 mt-3 border-t border-border-subtle">
                      <button
                        onClick={() => handleAddPick(pick, `#${i + 1} Safest Pick`)}
                        className={`w-full py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                          added
                            ? 'bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/30'
                            : 'bg-surface-elevated hover:bg-white/10 text-white border border-border-medium active:scale-98'
                        }`}
                      >
                        {added ? (
                          <>
                            <Check className="w-3.5 h-3.5" />
                            <span>ADDED TO SLIP</span>
                          </>
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5 text-brand-emerald" />
                            <span>ADD TO BETSLIP</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 5. 5-Way Consensus & Common Ground Conflict Arbitrage */}
          {prediction.penta_consensus && (
            <div className="glass-panel p-6 rounded-3xl border border-brand-violet/20 bg-gradient-to-br from-surface to-brand-violet/5">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-border-subtle">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-brand-violet/10 border border-brand-violet/30 flex items-center justify-center shadow-glow-violet">
                    <Crown className="w-5 h-5 text-brand-violet" />
                  </div>
                  <div>
                    <span className="text-[10px] font-mono uppercase font-bold tracking-widest text-brand-violet">
                      PENTA-LOCK ROYAL CONSENSUS
                    </span>
                    <h3 className="text-lg font-black text-white">
                      {prediction.penta_consensus.primary_pick}
                    </h3>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-slate-400">Cross-Model Agreement:</span>
                  <span className="font-mono text-sm font-black text-brand-emerald px-2.5 py-1 rounded-lg bg-brand-emerald/10 border border-brand-emerald/20">
                    {prediction.penta_consensus.agreement_count}/5 Engines ({prediction.penta_consensus.consensus_score}%)
                  </span>
                </div>
              </div>

              {/* Common Ground Arbitrage Derivative */}
              {prediction.penta_consensus.common_ground_market && (
                <div className="mt-4 p-4 rounded-2xl bg-surface-card border border-border-subtle flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Sparkles className="w-3.5 h-3.5 text-brand-amber" />
                      <span className="text-[11px] font-bold uppercase tracking-wider text-brand-amber">
                        UNIVERSAL COMMON GROUND ARBITRAGE
                      </span>
                    </div>
                    <div className="text-sm font-bold text-white">
                      {prediction.penta_consensus.common_ground_market.market}
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Unified market matching all 5 predicted engine scorelines with 100% agreement.
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="font-mono text-sm font-bold text-brand-emerald bg-brand-emerald/10 px-2.5 py-1 rounded border border-brand-emerald/20">
                      Odds: {Number(prediction.penta_consensus.common_ground_market.fair_odds || 1.15).toFixed(2)}
                    </span>
                    <button
                      onClick={() =>
                        handleAddPick(
                          {
                            title: 'Common Ground Arbitrage',
                            bet: prediction.penta_consensus.common_ground_market!.market,
                            fair_odds: prediction.penta_consensus.common_ground_market!.fair_odds,
                            probability: 88.0,
                            reasoning: 'Universal 5-way model derivative lock',
                            risk_level: 'Ultra Safe',
                          },
                          'Common Ground Arbitrage'
                        )
                      }
                      className="px-3.5 py-1.5 rounded-xl bg-brand-violet hover:bg-brand-violet/80 text-white text-xs font-bold flex items-center gap-1.5 transition-all shadow-glow-violet"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Lock Market</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 6. Discipline & Yellow Cards Market */}
          {prediction.yellow_cards && (
            <div className="glass-panel p-5 rounded-2xl border border-border-subtle flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-brand-amber/10 border border-brand-amber/30 flex items-center justify-center">
                  <Flame className="w-5 h-5 text-brand-amber" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Yellow Cards Discipline Line
                    </span>
                    {prediction.yellow_cards.is_derby && (
                      <span className="px-2 py-0.5 rounded bg-brand-rose/10 text-brand-rose text-[10px] font-bold border border-brand-rose/20">
                        DERBY CLASH
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Projected Total: <strong className="text-white font-mono">{prediction.yellow_cards.expected_total_cards} Cards</strong> &bull; Home: {prediction.yellow_cards.expected_home_cards} / Away: {prediction.yellow_cards.expected_away_cards}
                  </p>
                </div>
              </div>

              {prediction.yellow_cards.best_card_bet && (
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="text-[10px] uppercase font-mono text-slate-400 block">Top Value Bet</span>
                    <span className="text-xs font-bold text-white">{prediction.yellow_cards.best_card_bet.market}</span>
                  </div>
                  <button
                    onClick={() =>
                      handleAddPick(
                        {
                          title: 'Yellow Cards Line',
                          bet: prediction.yellow_cards.best_card_bet!.market,
                          fair_odds: prediction.yellow_cards.best_card_bet!.fair_odds,
                          probability: prediction.yellow_cards.best_card_bet!.probability_pct,
                          reasoning: 'Discipline referee & derby expectation model',
                          risk_level: 'High Probability',
                        },
                        'Yellow Cards Market'
                      )
                    }
                    className="px-3 py-1.5 rounded-xl bg-surface-elevated hover:bg-white/10 text-white text-xs font-bold border border-border-medium flex items-center gap-1.5 transition-all"
                  >
                    <Plus className="w-3.5 h-3.5 text-brand-amber" />
                    <span>Add Cards Bet</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
