import { useState } from 'react';
import { TopNavBar } from './components/TopNavBar';
import { Sidebar } from './components/Sidebar';
import { InputSection } from './components/InputSection';
import { InvestigationTimeline } from './components/InvestigationTimeline';
import { VerdictPanel } from './components/VerdictPanel';
import { EvidenceSidebar } from './components/EvidenceSidebar';
import { MobileBottomNav } from './components/MobileBottomNav';
import { ScanResults } from './components/ScanResults';
import { useInvestigation } from './hooks/useInvestigation';
import { useEventScan } from './hooks/useEventScan';

type InputMode = 'investigate' | 'scan';

export default function App() {
  const [mode, setMode] = useState<InputMode>('investigate');
  const investigation = useInvestigation();
  const scan = useEventScan();

  const isRunning =
    mode === 'investigate'
      ? investigation.state === 'running'
      : scan.state === 'scanning';

  function handleModeChange(newMode: InputMode) {
    if (investigation.state === 'running') investigation.cancel();
    if (scan.state === 'scanning') scan.cancel();
    setMode(newMode);
  }

  function handleCancel() {
    if (mode === 'investigate') investigation.cancel();
    else scan.cancel();
  }

  return (
    <div className="min-h-screen bg-background text-on-surface">
      <TopNavBar />
      <Sidebar />
      <main className="lg:ml-64 mt-16 p-4 md:p-6 lg:p-8 mb-16 md:mb-0">
        <InputSection
          onSubmit={investigation.start}
          onScan={scan.start}
          isRunning={isRunning}
          onCancel={handleCancel}
          activeMode={mode}
          onModeChange={handleModeChange}
        />

        {/* Investigate mode */}
        {mode === 'investigate' && investigation.state !== 'idle' && (
          <div className="mt-8 grid grid-cols-1 xl:grid-cols-12 gap-8 max-w-7xl mx-auto">
            <div className="xl:col-span-8">
              <InvestigationTimeline steps={investigation.steps} />
              {investigation.verdict && <VerdictPanel verdict={investigation.verdict} />}
            </div>
            <div className="xl:col-span-4">
              <EvidenceSidebar steps={investigation.steps} verdict={investigation.verdict} />
            </div>
          </div>
        )}

        {/* Scan mode - active scan */}
        {mode === 'scan' && scan.state !== 'idle' && (
          <div className="mt-8 max-w-7xl mx-auto">
            <ScanResults
              listings={scan.listings}
              stats={scan.stats}
              isScanning={scan.state === 'scanning'}
            />
          </div>
        )}

        {/* Scan mode - idle empty state */}
        {mode === 'scan' && scan.state === 'idle' && (
          <div className="mt-8 max-w-7xl mx-auto">
            <ScanResults
              listings={[]}
              stats={scan.stats}
              isScanning={false}
            />
          </div>
        )}

        {/* Error display */}
        {mode === 'investigate' && investigation.error && (
          <p className="mt-4 text-center text-error text-sm font-body">{investigation.error}</p>
        )}
        {mode === 'scan' && scan.error && (
          <p className="mt-4 text-center text-error text-sm font-body">{scan.error}</p>
        )}
      </main>
      <MobileBottomNav />
    </div>
  );
}
