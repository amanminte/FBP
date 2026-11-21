import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { MatchCenter } from './components/MatchCenter';
import { MegaScanner } from './components/MegaScanner';
import { LedgerHub } from './components/LedgerHub';
import { BrainTelemetry } from './components/BrainTelemetry';
import { BetslipDrawer } from './components/BetslipDrawer';
import type { LeagueInfo, FixtureMatch, BetSlipItem } from './types';
import { fetchLeagues, fetchFixtures } from './api';
import { CheckCircle2 } from 'lucide-react';

export function App() {
  const [currentSpace, setCurrentSpace] = useState<'matches' | 'scanner' | 'ledger' | 'brain'>('matches');
  const [leagues, setLeagues] = useState<LeagueInfo[]>([]);
  const [selectedLeague, setSelectedLeague] = useState<string>('E0');
  const [fixtures, setFixtures] = useState<FixtureMatch[]>([]);
  const [slipItems, setSlipItems] = useState<BetSlipItem[]>([]);
  const [isSlipOpen, setIsSlipOpen] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Load leagues on initial mount
  useEffect(() => {
    fetchLeagues()
      .then((data) => {
        setLeagues(data);
        if (data.length > 0 && !selectedLeague) {
          setSelectedLeague(data[0].id);
        }
      })
      .catch((err) => console.error('Failed to load leagues:', err));
  }, []);

  // Load fixtures whenever selected league changes
  useEffect(() => {
    if (!selectedLeague) return;
    fetchFixtures(selectedLeague)
      .then((data: any) => {
        const curGw = String(data.current_gameweek || 11);
        const activeGwObj = data.gameweeks?.find((gw: any) => String(gw.gameweek) === curGw);
        const matches = activeGwObj ? activeGwObj.matches : (data.gameweeks?.flatMap((gw: any) => gw.matches) || []);
        setFixtures(matches);
      })
      .catch((err) => console.error('Failed to load fixtures:', err));
  }, [selectedLeague]);

  // Handle adding a pick to the slip
  const handleAddToSlip = (item: BetSlipItem) => {
    setSlipItems((prev) => {
      // Check if already in slip
      const exists = prev.some((it) => it.fixture === item.fixture && it.pick === item.pick);
      if (exists) {
        return prev.filter((it) => !(it.fixture === item.fixture && it.pick === item.pick));
      }
      return [...prev, item];
    });
    // Open the slip automatically on addition for instant feedback
    setIsSlipOpen(true);
  };

  const handleRemoveItem = (id: string) => {
    setSlipItems((prev) => prev.filter((it) => it.id !== id));
  };

  const handleClearSlip = () => {
    setSlipItems([]);
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  return (
    <div className="min-h-screen bg-canvas text-slate-100 flex flex-col font-sans selection:bg-brand-emerald/30 selection:text-white">
      {/* 1. Global Navigation Bar */}
      <Navbar
        currentSpace={currentSpace}
        onSelectSpace={setCurrentSpace}
        leagues={leagues}
        selectedLeague={selectedLeague}
        onSelectLeague={setSelectedLeague}
        slipCount={slipItems.length}
        onToggleSlip={() => setIsSlipOpen(!isSlipOpen)}
      />

      {/* 2. Main Content Canvas */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 pt-6">
        {currentSpace === 'matches' && (
          <MatchCenter
            leagues={leagues}
            selectedLeague={selectedLeague}
            fixtures={fixtures}
            onSelectFixture={() => {}}
            onAddToSlip={handleAddToSlip}
            slipItems={slipItems}
          />
        )}

        {currentSpace === 'scanner' && (
          <MegaScanner onAddToSlip={handleAddToSlip} slipItems={slipItems} />
        )}

        {currentSpace === 'ledger' && <LedgerHub />}

        {currentSpace === 'brain' && <BrainTelemetry />}
      </main>

      {/* 3. Universal Persistent Betslip Drawer */}
      <BetslipDrawer
        isOpen={isSlipOpen}
        onClose={() => setIsSlipOpen(false)}
        items={slipItems}
        onRemoveItem={handleRemoveItem}
        onClearSlip={handleClearSlip}
        onBetLockedSuccess={showToast}
      />

      {/* 4. Celebratory Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 glass-panel px-5 py-3 rounded-2xl border border-brand-emerald/40 bg-surface/90 text-white text-xs font-bold flex items-center gap-2.5 shadow-glow-emerald animate-in fade-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-brand-emerald" />
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
}

export default App;
