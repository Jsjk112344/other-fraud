import { useState } from 'react';

interface InputSectionProps {
  onSubmit: (url: string) => void;
  isRunning: boolean;
  onCancel: () => void;
}

const SAMPLE_URL = 'https://www.carousell.sg/p/f1-singapore-gp-2026-pit-grandstand-1234567890';

function isValidUrl(input: string): boolean {
  try {
    const url = new URL(input);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

export function InputSection({ onSubmit, isRunning, onCancel }: InputSectionProps) {
  const [url, setUrl] = useState('');
  const [urlError, setUrlError] = useState<string | null>(null);

  function handleSubmit(inputUrl?: string) {
    const target = inputUrl ?? url;
    if (!isValidUrl(target)) {
      setUrlError('Could not detect listing. Please paste a valid Carousell, Viagogo, or marketplace URL.');
      return;
    }
    setUrlError(null);
    onSubmit(target);
  }

  function handleSample() {
    setUrl(SAMPLE_URL);
    setUrlError(null);
    handleSubmit(SAMPLE_URL);
  }

  return (
    <div className="max-w-4xl mx-auto text-center">
      {/* Headline */}
      <h1 className="text-4xl font-headline font-bold text-primary leading-tight">
        AI Fraud Detective for Ticket Scams
      </h1>
      <p className="mt-4 text-on-surface-variant font-body max-w-2xl mx-auto">
        Input a listing URL to start an autonomous investigation. Our AI agent will analyze the seller,
        verify the event, and deliver a fraud verdict with full evidence.
      </p>

      {/* Input Group */}
      <div className="mt-8 group relative">
        {/* Outer glow */}
        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-tertiary/20 rounded-lg blur-xl opacity-0 group-hover:opacity-50 transition duration-1000" />

        {/* Inner input container */}
        <div className="relative bg-surface-container-low rounded-lg p-2 flex items-center gap-2 border border-outline-variant/20 focus-within:border-primary/50 transition-colors">
          <span className="material-symbols-outlined text-outline ml-2">link</span>
          <input
            type="text"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              setUrlError(null);
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !isRunning) handleSubmit();
            }}
            placeholder="Paste a Carousell, Viagogo, or marketplace URL..."
            className="flex-1 bg-transparent outline-none text-on-surface placeholder:text-outline font-body text-sm"
          />
          {isRunning ? (
            <button
              onClick={onCancel}
              className="border border-error text-error px-6 py-2.5 rounded-lg font-headline font-bold text-sm hover:bg-error/10 transition-colors whitespace-nowrap"
            >
              Stop Investigation
            </button>
          ) : (
            <button
              onClick={() => handleSubmit()}
              className="bg-primary-container text-on-primary px-6 py-2.5 rounded-lg font-headline font-bold text-sm hover:brightness-110 transition whitespace-nowrap"
            >
              Investigate Listing
            </button>
          )}
        </div>
      </div>

      {/* Error message */}
      {urlError && (
        <p className="mt-2 text-error text-sm font-body">{urlError}</p>
      )}

      {/* Quick action chips */}
      <div className="mt-4 flex items-center justify-center gap-3">
        <button
          onClick={handleSample}
          disabled={isRunning}
          className="rounded-full bg-surface-container-highest border border-outline-variant/30 hover:border-primary/50 px-4 py-1.5 text-xs text-on-surface-variant font-body flex items-center gap-2 transition-colors disabled:opacity-50"
        >
          <span className="material-symbols-outlined text-sm">play_circle</span>
          Sample listing
        </button>
        <button
          disabled
          className="rounded-full bg-surface-container-highest border border-outline-variant/30 px-4 py-1.5 text-xs text-on-surface-variant font-body flex items-center gap-2 opacity-50 cursor-not-allowed"
        >
          <span className="material-symbols-outlined text-sm">search</span>
          Scan an event
        </button>
      </div>
    </div>
  );
}
