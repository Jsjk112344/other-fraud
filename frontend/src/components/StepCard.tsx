import type { StepWithState } from '../types/investigation';

interface StepCardProps {
  step: StepWithState;
}

export function StepCard({ step }: StepCardProps) {
  const isPending = step.status === 'pending';
  const isActive = step.status === 'active';
  const isComplete = step.status === 'complete';
  const isError = step.status === 'error';

  return (
    <div className="flex gap-6">
      {/* Circle */}
      <div
        className={`w-14 h-14 rounded-full flex-shrink-0 flex items-center justify-center border transition-all ${
          isActive
            ? 'bg-surface-container-highest border-primary/50 shadow-[0_0_15px_rgba(175,198,255,0.3)]'
            : isComplete
              ? 'bg-surface-container-highest border-green-400/50'
              : isError
                ? 'bg-surface-container-highest border-error/50'
                : 'bg-surface-container-highest border-outline-variant/50'
        }`}
      >
        {isComplete ? (
          <span
            className="material-symbols-outlined text-green-400 text-2xl"
            style={{ fontVariationSettings: "'FILL' 1" }}
            aria-label="Step complete"
          >
            check_circle
          </span>
        ) : isError ? (
          <span className="material-symbols-outlined text-error text-2xl">error</span>
        ) : (
          <span
            className={`material-symbols-outlined text-2xl ${
              isActive ? 'text-primary animate-pulse' : 'text-secondary'
            }`}
          >
            {step.icon}
          </span>
        )}
      </div>

      {/* Card */}
      <div
        className={`glass border rounded-xl p-5 flex-1 transition-colors ${
          isActive
            ? 'border-primary/20 hover:border-primary/30'
            : isError
              ? 'border-error/30'
              : isPending
                ? 'border-outline-variant/10'
                : 'border-outline-variant/20 hover:border-primary/30'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <span
            className={`font-headline font-bold text-sm ${
              isPending ? 'text-on-surface-variant/50' : 'text-on-surface'
            }`}
          >
            {step.label}
          </span>

          {/* Status indicator */}
          {isActive && (
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
              </span>
              <span className="text-primary text-xs uppercase tracking-wider font-body">
                Processing
              </span>
            </div>
          )}
          {isError && (
            <span className="text-error text-xs uppercase tracking-wider font-body">Error</span>
          )}
        </div>

        {/* Active: progress bar */}
        {isActive && (
          <div className="h-1 bg-surface-container rounded-full mt-3">
            <div className="bg-primary h-full rounded-full transition-all duration-1000 w-full" />
          </div>
        )}

        {/* Complete: data block */}
        {isComplete && step.data && (
          <div className="bg-black/20 rounded p-3 mt-3">
            <pre className="font-mono text-[11px] text-on-surface-variant leading-relaxed whitespace-pre-wrap">
              {JSON.stringify(step.data, null, 2).slice(0, 200)}
              {JSON.stringify(step.data, null, 2).length > 200 ? '...' : ''}
            </pre>
          </div>
        )}

        {/* Error: message */}
        {isError && step.data?.error && (
          <p className="mt-2 text-error text-xs font-body">
            {String(step.data.error)}
          </p>
        )}
      </div>
    </div>
  );
}
