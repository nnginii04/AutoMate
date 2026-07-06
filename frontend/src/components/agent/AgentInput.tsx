import type { KeyboardEvent } from 'react';
import { EXAMPLE_PHRASES } from '../../utils/constants';

type AgentInputProps = {
  value: string;
  onChange: (value: string) => void;
  onRun: () => void;
  loading?: boolean;
  disabled?: boolean;
};

export function AgentInput({
  value,
  onChange,
  onRun,
  loading = false,
  disabled = false,
}: AgentInputProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!loading && !disabled && value.trim()) onRun();
    }
  };

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-lg font-semibold text-foreground">
          AI Command Console
        </h3>
        <p className="mt-1 text-sm text-secondary">
          Enter an in-vehicle command and inspect how the agent maps it to intent
          and tool calls.
        </p>
      </div>

      <textarea
        id="agent-input"
        rows={4}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="e.g. Turn up the heat, navigate home, play calm music…"
        disabled={loading || disabled}
        className="mobility-input resize-none"
      />

      <button
        type="button"
        onClick={onRun}
        disabled={loading || disabled || !value.trim()}
        className="mobility-btn-primary w-full bg-gradient-to-r from-primary to-cyan"
      >
        {loading ? 'Running Agent…' : 'Run Agent'}
      </button>

      <div>
        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted">
          Example Phrases
        </p>
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_PHRASES.map((phrase) => (
            <button
              key={phrase}
              type="button"
              onClick={() => onChange(phrase)}
              disabled={loading}
              className="rounded-full border border-border bg-surface px-3 py-1.5 text-xs text-secondary shadow-sm transition-all hover:border-primary hover:bg-primary-soft hover:text-primary disabled:opacity-50"
            >
              {phrase}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
