import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Crown,
  Sparkles,
  Plus,
  Check,
  Flame,
  Newspaper,
  Activity,
  UserCheck,
  ExternalLink,
  Flag
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
  const currentLeagueObj = leagues.find((l) => l.id === selectedLeague) || leagues[0] || {
    id: selectedLeague || 'E0',
    name: 'Premier League',
    country: 'England',
    flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    teams: ['Arsenal', 'Chelsea', 'Liverpool', 'Manchester City']
  };
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
            <span>{currentLeagueObj?.flag || '🏴󠁧󠁢󠁥󠁮󠁧󠁿'}</span>
            <span>{currentLeagueObj?.name || 'Premier League'}</span>
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
                    xG: {(prediction.expected_goals?.home_xg ?? (prediction.expected_goals as any)?.lambda_home ?? 1.85).toFixed(2)}
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
                    Most Probable Scoreline ({((prediction.top_3_scorelines?.[0]?.probability_pct ?? (prediction.top_3_scorelines?.[0] as any)?.prob ?? 11.5)).toFixed(1)}%)
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
                    xG: {(prediction.expected_goals?.away_xg ?? (prediction.expected_goals as any)?.lambda_away ?? 1.05).toFixed(2)}
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

              {/* Tactical 1X2 & Double Chance High-Conviction Suggestion Cards */}
              <div className="pt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 1X2 Tactical Bet */}
                {prediction.tactical_1x2_recommendation && (
                  <div className="p-4 rounded-2xl bg-surface-card border border-emerald-500/20 flex flex-col justify-between gap-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-brand-emerald/10 text-brand-emerald border border-brand-emerald/20 flex items-center gap-1">
                        <Crown className="w-3 h-3" />
                        <span>SUGGESTED 1X2 OUTRIGHT</span>
                      </span>
                      <span className="font-mono text-xs font-bold text-brand-emerald">
                        Odds: {prediction.tactical_1x2_recommendation.fair_odds.toFixed(2)}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-sm font-black text-white">
                        {prediction.tactical_1x2_recommendation.bet}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1">
                        {prediction.tactical_1x2_recommendation.reasoning}
                      </p>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-white/5">
                      <span className="text-xs font-mono text-slate-300">
                        Confidence: <strong className="text-brand-emerald">{prediction.tactical_1x2_recommendation.probability.toFixed(1)}%</strong>
                      </span>
                      <button
                        onClick={() =>
                          handleAddPick(
                            {
                              title: '1X2 Outright Winner',
                              bet: prediction.tactical_1x2_recommendation!.bet,
                              fair_odds: prediction.tactical_1x2_recommendation!.fair_odds,
                              probability: prediction.tactical_1x2_recommendation!.probability,
                              reasoning: prediction.tactical_1x2_recommendation!.reasoning,
                              risk_level: 'High Value 1X2',
                            },
                            '1X2 Outright Winner'
                          )
                        }
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all ${
                          isPickInSlip(prediction.tactical_1x2_recommendation.bet)
                            ? 'bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/30'
                            : 'bg-brand-emerald hover:bg-brand-emerald/90 text-white shadow-glow-emerald active:scale-98'
                        }`}
                      >
                        {isPickInSlip(prediction.tactical_1x2_recommendation.bet) ? (
                          <>
                            <Check className="w-3.5 h-3.5" />
                            <span>In Slip</span>
                          </>
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5" />
                            <span>Add 1X2 Bet</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {/* Double Chance Tactical Bet */}
                {prediction.tactical_dc_recommendation && (
                  <div className="p-4 rounded-2xl bg-surface-card border border-brand-cyan/20 flex flex-col justify-between gap-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/20 flex items-center gap-1">
                        <ShieldCheck className="w-3 h-3" />
                        <span>SUGGESTED DOUBLE CHANCE LOCK</span>
                      </span>
                      <span className="font-mono text-xs font-bold text-brand-cyan">
                        Odds: {prediction.tactical_dc_recommendation.fair_odds.toFixed(2)}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-sm font-black text-white">
                        {prediction.tactical_dc_recommendation.bet}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1">
                        {prediction.tactical_dc_recommendation.reasoning}
                      </p>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-white/5">
                      <span className="text-xs font-mono text-slate-300">
                        Safety: <strong className="text-brand-cyan">{prediction.tactical_dc_recommendation.probability.toFixed(1)}%</strong>
                      </span>
                      <button
                        onClick={() =>
                          handleAddPick(
                            {
                              title: 'Double Chance Lock',
                              bet: prediction.tactical_dc_recommendation!.bet,
                              fair_odds: prediction.tactical_dc_recommendation!.fair_odds,
                              probability: prediction.tactical_dc_recommendation!.probability,
                              reasoning: prediction.tactical_dc_recommendation!.reasoning,
                              risk_level: 'Ultra Safe Lock',
                            },
                            'Double Chance Lock'
                          )
                        }
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all ${
                          isPickInSlip(prediction.tactical_dc_recommendation.bet)
                            ? 'bg-brand-cyan/20 text-brand-cyan border border-brand-cyan/30'
                            : 'bg-brand-cyan hover:bg-brand-cyan/90 text-white shadow-glow-cyan active:scale-98'
                        }`}
                      >
                        {isPickInSlip(prediction.tactical_dc_recommendation.bet) ? (
                          <>
                            <Check className="w-3.5 h-3.5" />
                            <span>In Slip</span>
                          </>
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5" />
                            <span>Add Double Chance</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                )}
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

          {/* 5. 7-Way Hepta-Consensus & Common Ground Conflict Arbitrage */}
          {prediction.penta_consensus && (
            <div className="glass-panel p-6 rounded-3xl border border-blue-500/30 bg-gradient-to-br from-surface via-blue-950/20 to-blue-900/10 space-y-5 shadow-glow-blue">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-blue-500/15">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-blue-500/15 border border-blue-400/40 flex items-center justify-center shadow-lg shadow-blue-500/25">
                    <Crown className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <span className="text-[10px] font-mono uppercase font-bold tracking-widest text-blue-400">
                      {prediction.penta_consensus.consensus_tier || 'HEPTA-LOCK IMPERIAL DIAMOND'}
                    </span>
                    <h3 className="text-lg font-black text-white">
                      {prediction.penta_consensus.primary_pick}
                    </h3>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-slate-400">7-Platform Convergence:</span>
                  <span className="font-mono text-sm font-black text-blue-300 px-2.5 py-1 rounded-lg bg-blue-500/15 border border-blue-400/30">
                    {prediction.penta_consensus.agreement_count}/{prediction.penta_consensus.total_sources || 7} Engines ({prediction.penta_consensus.consensus_score}%)
                  </span>
                </div>
              </div>

              {/* Common Ground Arbitrage Derivative */}
              {prediction.penta_consensus.common_ground_market && (
                <div className="p-4 rounded-2xl bg-blue-950/30 border border-blue-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 backdrop-blur-sm">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                      <span className="text-[11px] font-bold uppercase tracking-wider text-blue-400">
                        7-WAY UNANIMOUS HEPTA-LOCK ARBITRAGE (MAX CONVICTION)
                      </span>
                    </div>
                    <div className="text-base font-black text-white">
                      {prediction.penta_consensus.common_ground_market.market}
                    </div>
                    <p className="text-xs text-blue-100/70 mt-0.5 max-w-2xl">
                      {prediction.penta_consensus.common_ground_market.reason ||
                        `Harmonizes all 7 predicted scorelines (${prediction.penta_consensus.common_ground_market.scorelines?.slice(0, 7).join(', ') || 'all scorelines'}) into an ultra-high conviction derivative lock.`}
                    </p>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span className="font-mono text-sm font-bold text-blue-300 bg-blue-500/20 px-3 py-1.5 rounded-xl border border-blue-400/40 shadow-sm">
                      Odds: {Number(prediction.penta_consensus.common_ground_market.fair_odds || 1.15).toFixed(2)}
                    </span>
                    <button
                      onClick={() =>
                        handleAddPick(
                          {
                            title: 'Hepta-Lock Arbitrage',
                            bet: prediction.penta_consensus.common_ground_market!.market,
                            fair_odds: prediction.penta_consensus.common_ground_market!.fair_odds,
                            probability: 95.0,
                            reasoning: prediction.penta_consensus.common_ground_market!.reason || '7-Way multi-model derivative arbitrage lock',
                            risk_level: 'Ultra Safe',
                          },
                          'Hepta-Lock Arbitrage'
                        )
                      }
                      className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all shadow-lg shadow-blue-500/30 active:scale-98 border border-blue-400/30"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Lock Hepta Bet</span>
                    </button>
                  </div>
                </div>
              )}

              {/* 7 Predictive Platforms Grid */}
              {prediction.penta_consensus.sources && prediction.penta_consensus.sources.length > 0 && (
                <div>
                  <div className="text-[11px] uppercase font-bold tracking-wider text-slate-400 mb-2.5 flex items-center justify-between">
                    <span>7 Independent Intelligence Engines:</span>
                    <span className="text-slate-500 font-mono">Football Whispers &bull; FootballPredictions &bull; Understat &bull; WhoScored &bull; Forebet</span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
                    {prediction.penta_consensus.sources.map((src, idx) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-xl border text-xs flex flex-col justify-between transition-all ${
                          src.agrees
                            ? 'bg-surface-card border-brand-emerald/20'
                            : 'bg-surface-card/60 border-border-subtle opacity-85'
                        }`}
                      >
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-bold text-white flex items-center gap-1 truncate max-w-[120px]">
                              <span>{src.icon}</span>
                              <span className="truncate">{src.name}</span>
                            </span>
                            <span
                              className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${
                                src.agrees
                                  ? 'bg-brand-emerald/10 text-brand-emerald border border-brand-emerald/20'
                                  : 'bg-white/5 text-slate-400'
                              }`}
                            >
                              {src.agrees ? 'AGREE' : 'ALT'}
                            </span>
                          </div>

                          <div className="font-bold text-slate-200 mt-1">
                            {src.pick_readable || src.pick}
                          </div>

                          <div className="text-[11px] font-mono text-slate-400 mt-0.5">
                            Score: <strong className="text-white">{src.score}</strong>
                          </div>
                        </div>

                        <div className="text-[10px] text-slate-500 font-mono mt-2 pt-1 border-t border-white/5 truncate">
                          {src.metric_value}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 6. Live Tactical Atmosphere, Manager Reliability & 5-Game Form Radar */}
          {prediction.tactical_intelligence && (
            <div className="glass-panel p-6 rounded-2xl border border-border-subtle flex flex-col gap-5">
              {/* Radar Header */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-brand-cyan/10 border border-brand-cyan/30 flex items-center justify-center">
                    <Activity className="w-5 h-5 text-brand-cyan" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white uppercase tracking-wider">
                        Live Team Atmosphere, Manager Reliability & Form Radar
                      </span>
                      <span className="px-2 py-0.5 rounded bg-brand-emerald/10 text-brand-emerald text-[10px] font-mono font-bold border border-brand-emerald/20">
                        FREE MULTI-DESK INTELLIGENCE
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {prediction.tactical_intelligence.atmosphere_differential.verdict}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-brand-violet/10 text-brand-violet border border-brand-violet/20 font-bold">
                    {prediction.tactical_intelligence.atmosphere_differential.net_edge}
                  </span>
                </div>
              </div>

              {/* Two Team Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Home Team Card */}
                {(() => {
                  const h = prediction.tactical_intelligence.home;
                  return (
                    <div className="p-4 rounded-xl bg-surface-card border border-border-subtle flex flex-col justify-between gap-4">
                      <div>
                        {/* Header & Manager Badge */}
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-bold text-sm text-white">{h.team}</span>
                          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-white/5 text-slate-300 border border-white/10">
                            {h.manager_status}
                          </span>
                        </div>

                        {/* Manager Reliability */}
                        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                          <span className="flex items-center gap-1">
                            <UserCheck className="w-3.5 h-3.5 text-brand-cyan" />
                            Manager: <strong className="text-slate-200">{h.manager}</strong>
                          </span>
                          <span className="font-mono text-brand-cyan font-bold">{h.manager_reliability_pct}% Stability</span>
                        </div>
                        <p className="text-[11px] text-slate-400 italic mb-3">"{h.manager_note}"</p>

                        {/* Dressing Room Morale Bar */}
                        <div className="mb-3">
                          <div className="flex items-center justify-between text-[11px] mb-1">
                            <span className="text-slate-400 font-medium">Dressing Room Morale:</span>
                            <span className="font-mono font-bold text-slate-200">
                              {h.morale_index_pct}% ({h.atmosphere_sentiment})
                            </span>
                          </div>
                          <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all duration-500 ${
                                h.morale_index_pct >= 75
                                  ? 'bg-brand-emerald'
                                  : h.morale_index_pct >= 55
                                  ? 'bg-brand-amber'
                                  : 'bg-brand-rose'
                              }`}
                              style={{ width: `${h.morale_index_pct}%` }}
                            />
                          </div>
                        </div>

                        {/* 5-Game Recent Form Splits */}
                        <div className="mb-3 p-2.5 rounded-lg bg-surface-elevated border border-white/5">
                          <div className="flex items-center justify-between text-[11px] mb-1.5">
                            <span className="text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                              5-Game Form Splits
                            </span>
                            <span className="font-mono text-slate-300 text-[10px]">
                              {h.form.form_string || 'N/A'} &bull; {h.form.points_per_game} PPG
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            {(h.form.form_sequence || h.form.sequence || []).map((res, i) => (
                              <span
                                key={i}
                                className={`w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold font-mono ${
                                  res === 'W'
                                    ? 'bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/40'
                                    : res === 'D'
                                    ? 'bg-brand-amber/20 text-brand-amber border border-brand-amber/40'
                                    : 'bg-brand-rose/20 text-brand-rose border border-brand-rose/40'
                                }`}
                              >
                                {res}
                              </span>
                            ))}
                            <span className="ml-auto text-[10px] text-slate-400 font-mono">
                              GD: {(h.form.goal_diff_last_5 ?? h.form.goal_diff ?? 0) > 0 ? `+${h.form.goal_diff_last_5 ?? h.form.goal_diff ?? 0}` : (h.form.goal_diff_last_5 ?? h.form.goal_diff ?? 0)}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Verified News Headlines */}
                      {h.verified_news && h.verified_news.length > 0 && (
                        <div className="pt-2 border-t border-white/5">
                          <div className="flex items-center gap-1 text-[10px] uppercase font-bold text-slate-400 mb-1.5">
                            <Newspaper className="w-3 h-3 text-slate-400" />
                            <span>Live Pre-Match Intelligence:</span>
                          </div>
                          <div className="flex flex-col gap-1">
                            {h.verified_news.slice(0, 2).map((art, idx) => (
                              <a
                                key={idx}
                                href={art.link}
                                target="_blank"
                                rel="noreferrer"
                                className="text-[11px] text-slate-300 hover:text-brand-cyan truncate flex items-center gap-1.5 transition-colors"
                              >
                                <ExternalLink className="w-3 h-3 text-slate-500 shrink-0" />
                                <span className="truncate">{art.title}</span>
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })()}

                {/* Away Team Card */}
                {(() => {
                  const a = prediction.tactical_intelligence.away;
                  return (
                    <div className="p-4 rounded-xl bg-surface-card border border-border-subtle flex flex-col justify-between gap-4">
                      <div>
                        {/* Header & Manager Badge */}
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-bold text-sm text-white">{a.team}</span>
                          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-white/5 text-slate-300 border border-white/10">
                            {a.manager_status}
                          </span>
                        </div>

                        {/* Manager Reliability */}
                        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                          <span className="flex items-center gap-1">
                            <UserCheck className="w-3.5 h-3.5 text-brand-cyan" />
                            Manager: <strong className="text-slate-200">{a.manager}</strong>
                          </span>
                          <span className="font-mono text-brand-cyan font-bold">{a.manager_reliability_pct}% Stability</span>
                        </div>
                        <p className="text-[11px] text-slate-400 italic mb-3">"{a.manager_note}"</p>

                        {/* Dressing Room Morale Bar */}
                        <div className="mb-3">
                          <div className="flex items-center justify-between text-[11px] mb-1">
                            <span className="text-slate-400 font-medium">Dressing Room Morale:</span>
                            <span className="font-mono font-bold text-slate-200">
                              {a.morale_index_pct}% ({a.atmosphere_sentiment})
                            </span>
                          </div>
                          <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all duration-500 ${
                                a.morale_index_pct >= 75
                                  ? 'bg-brand-emerald'
                                  : a.morale_index_pct >= 55
                                  ? 'bg-brand-amber'
                                  : 'bg-brand-rose'
                              }`}
                              style={{ width: `${a.morale_index_pct}%` }}
                            />
                          </div>
                        </div>

                        {/* 5-Game Recent Form Splits */}
                        <div className="mb-3 p-2.5 rounded-lg bg-surface-elevated border border-white/5">
                          <div className="flex items-center justify-between text-[11px] mb-1.5">
                            <span className="text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                              5-Game Form Splits
                            </span>
                            <span className="font-mono text-slate-300 text-[10px]">
                              {a.form.form_string || 'N/A'} &bull; {a.form.points_per_game} PPG
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            {(a.form.form_sequence || a.form.sequence || []).map((res, i) => (
                              <span
                                key={i}
                                className={`w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold font-mono ${
                                  res === 'W'
                                    ? 'bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/40'
                                    : res === 'D'
                                    ? 'bg-brand-amber/20 text-brand-amber border border-brand-amber/40'
                                    : 'bg-brand-rose/20 text-brand-rose border border-brand-rose/40'
                                }`}
                              >
                                {res}
                              </span>
                            ))}
                            <span className="ml-auto text-[10px] text-slate-400 font-mono">
                              GD: {(a.form.goal_diff_last_5 ?? a.form.goal_diff ?? 0) > 0 ? `+${a.form.goal_diff_last_5 ?? a.form.goal_diff ?? 0}` : (a.form.goal_diff_last_5 ?? a.form.goal_diff ?? 0)}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Verified News Headlines */}
                      {a.verified_news && a.verified_news.length > 0 && (
                        <div className="pt-2 border-t border-white/5">
                          <div className="flex items-center gap-1 text-[10px] uppercase font-bold text-slate-400 mb-1.5">
                            <Newspaper className="w-3 h-3 text-slate-400" />
                            <span>Live Pre-Match Intelligence:</span>
                          </div>
                          <div className="flex flex-col gap-1">
                            {a.verified_news.slice(0, 2).map((art, idx) => (
                              <a
                                key={idx}
                                href={art.link}
                                target="_blank"
                                rel="noreferrer"
                                className="text-[11px] text-slate-300 hover:text-brand-cyan truncate flex items-center gap-1.5 transition-colors"
                              >
                                <ExternalLink className="w-3 h-3 text-slate-500 shrink-0" />
                                <span className="truncate">{art.title}</span>
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>
            </div>
          )}

          {/* 7. Discipline & Yellow Cards Market */}
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

          {/* 8. Quantitative Corners & Wing-Exploitation Line */}
          {prediction.corners && (
            <div className="glass-panel p-5 rounded-2xl border border-border-subtle flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center">
                  <Flag className="w-5 h-5 text-teal-400" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Corner Kicks Quantitative Model
                    </span>
                    <span className="px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 text-[10px] font-mono font-bold border border-teal-500/20">
                      WING EXPLOITATION ENGINE
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Projected Total: <strong className="text-white font-mono">{prediction.corners.expected_total_corners} Corners</strong> &bull; Home: {prediction.corners.expected_home_corners} / Away: {prediction.corners.expected_away_corners}
                  </p>
                  {prediction.corners.tactical_rationale && (
                    <p className="text-[11px] text-slate-400 italic mt-1 max-w-xl">
                      {prediction.corners.tactical_rationale}
                    </p>
                  )}
                </div>
              </div>

              {prediction.corners.best_corner_bet && (
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="text-[10px] uppercase font-mono text-slate-400 block">Top Corner Pick</span>
                    <span className="text-xs font-bold text-white">{prediction.corners.best_corner_bet.market}</span>
                    <span className="text-[10px] font-mono text-teal-400 block">
                      {(prediction.corners.best_corner_bet.probability > 1
                        ? prediction.corners.best_corner_bet.probability
                        : prediction.corners.best_corner_bet.probability * 100
                      ).toFixed(0)}% Conviction @ {prediction.corners.best_corner_bet.odds.toFixed(2)}
                    </span>
                  </div>
                  <button
                    onClick={() => {
                      const probVal = prediction.corners!.best_corner_bet!.probability > 1
                        ? prediction.corners!.best_corner_bet!.probability
                        : prediction.corners!.best_corner_bet!.probability * 100;
                      handleAddPick(
                        {
                          title: 'Corner Kicks Line',
                          bet: prediction.corners!.best_corner_bet!.market,
                          fair_odds: prediction.corners!.best_corner_bet!.odds,
                          probability: Math.round(probVal),
                          reasoning: prediction.corners!.best_corner_bet!.rationale || 'Negative Binomial wing-play corner projection',
                          risk_level: prediction.corners!.best_corner_bet!.confidence_tier || 'Anchor Lock',
                        },
                        'Corners'
                      );
                    }}
                    className="px-3 py-1.5 rounded-xl bg-surface-elevated hover:bg-white/10 text-white text-xs font-bold border border-teal-500/30 flex items-center gap-1.5 transition-all shadow-glow-cyan"
                  >
                    <Plus className="w-3.5 h-3.5 text-teal-400" />
                    <span>Add Corner Bet</span>
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
