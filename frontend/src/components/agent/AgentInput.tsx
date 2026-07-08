import type { KeyboardEvent } from 'react';
import { Play } from 'lucide-react';
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
    <div className="space-y-4">
      <div>
        <p className="console-label">Command input</p>
        <h3 className="mt-1 text-base font-bold text-foreground">
          Ask the vehicle agent
        </h3>
      </div>

      <textarea
        id="agent-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="예: 나 좀 추워 / 집으로 안내해줘 / 배터리 상태 확인해줘"
        disabled={loading || disabled}
        className="console-input h-[120px] resize-none leading-relaxed"
      />

      <div className="flex justify-end">
        <button
          type="button"
          onClick={onRun}
          disabled={loading || disabled || !value.trim()}
          className="console-btn-primary"
        >
          <Play className="h-3.5 w-3.5" fill="currentColor" />
          {loading ? 'Running…' : 'Run Agent'}
        </button>
      </div>

      <div>
        <p className="mb-2 text-[11px] font-medium text-muted">Quick phrases</p>
        <div className="flex flex-wrap gap-1.5">
          {EXAMPLE_PHRASES.map((phrase) => (
            <button
              key={phrase}
              type="button"
              onClick={() => onChange(phrase)}
              disabled={loading}
              className="chip-btn"
            >
              {phrase}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
