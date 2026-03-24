import { TopNavBar } from './components/TopNavBar';
import { Sidebar } from './components/Sidebar';
import { InputSection } from './components/InputSection';
import { InvestigationTimeline } from './components/InvestigationTimeline';
import { VerdictPanel } from './components/VerdictPanel';
import { EvidenceSidebar } from './components/EvidenceSidebar';
import { MobileBottomNav } from './components/MobileBottomNav';
import { useInvestigation } from './hooks/useInvestigation';

export default function App() {
  const { state, steps, verdict, error, start, cancel } = useInvestigation();

  return (
    <div className="min-h-screen bg-background text-on-surface">
      <TopNavBar />
      <Sidebar />
      <main className="lg:ml-64 mt-16 p-4 md:p-6 lg:p-8 mb-16 md:mb-0">
        <InputSection
          onSubmit={start}
          isRunning={state === 'running'}
          onCancel={cancel}
        />
        {state !== 'idle' && (
          <div className="mt-8 grid grid-cols-1 xl:grid-cols-12 gap-8 max-w-7xl mx-auto">
            <div className="xl:col-span-8">
              <InvestigationTimeline steps={steps} />
              {verdict && <VerdictPanel verdict={verdict} />}
            </div>
            <div className="xl:col-span-4">
              <EvidenceSidebar steps={steps} verdict={verdict} />
            </div>
          </div>
        )}
        {error && (
          <p className="mt-4 text-center text-error text-sm font-body">{error}</p>
        )}
      </main>
      <MobileBottomNav />
    </div>
  );
}
