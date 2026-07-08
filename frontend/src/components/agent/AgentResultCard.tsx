import { useState } from 'react';
import { Bot, ChevronDown, Loader2 } from 'lucide-react';
import { Badge, IntentBadge, SuccessBadge } from '../common/Badge';
import { JsonViewer } from '../common/JsonViewer';
import { formatPercent } from '../../utils/format';
import type { AgentRunResponse } from '../../types/agent';
import type { ApiError } from '../../api/client';

type AgentResultCardProps = {
  result: AgentRunResponse | null;
  loading: boolean;
  error: ApiError | null;
};

function accentClass(result: AgentRunResponse): string {
  if (result.safety_blocked) return 'border-t-warning';
  if (!result.success) return 'border-t-danger';
  return 'border-t-success';
}

function StatusBadges({ result }: { result: AgentRunResponse }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      <IntentBadge intent={result.intent} />
      <Badge variant="primary">{formatPercent(result.confidence)}</Badge>
      <SuccessBadge success={result.success} />
      {result.safety_blocked && <Badge variant="warning">Safety Block</Badge>}
      {result.fallback && <Badge variant="warning">Fallback</Badge>}
    </div>
  );
}

export function AgentResultCard({
  result,
  loading,
  error,
}: AgentResultCardProps) {
  const [slotsOpen, setSlotsOpen] = useState(false);

  if (loading) {
    return (
      <div className="console-card flex h-full min-h-[160px] items-center justify-center p-6">
        <Loader2 className="h-5 w-5 animate-spin text-primary" />
        <span className="ml-2 text-sm text-secondary">Processing…</span>
      </div>
    );
  }

  if (error && !result) {
    return (
      <div className="console-card border-t-2 border-t-danger p-4">
        <p className="text-sm font-semibold text-danger">Agent error</p>
        <p className="mt-1 text-sm text-secondary">{error.message}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="console-card flex h-full min-h-[120px] items-center gap-3 p-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface-soft">
          <Bot className="h-4 w-4 text-muted" strokeWidth={2} />
        </div>
        <div>
          <p className="text-sm font-semibold text-foreground">Agent Response</p>
          <p className="text-xs text-muted">
            Run a command to view the agent&apos;s response and classification.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`console-card border-t-[3px] p-4 ${accentClass(result)}`}>
      <p className="console-label">Agent Response</p>

      <p className="mt-2 text-[15px] font-semibold leading-relaxed text-foreground">
        {result.final_response}
      </p>

      <div className="mt-3">
        <StatusBadges result={result} />
        {result.failure_reason && (
          <p className="mt-2 text-xs text-danger">{result.failure_reason}</p>
        )}
      </div>

      <button
        type="button"
        onClick={() => setSlotsOpen((v) => !v)}
        className="mt-3 flex items-center gap-1 text-[11px] font-medium text-secondary hover:text-foreground"
      >
        <ChevronDown
          className={`h-3.5 w-3.5 transition-transform ${slotsOpen ? 'rotate-180' : ''}`}
        />
        Slots JSON
      </button>
      {slotsOpen && (
        <div className="mt-2">
          <JsonViewer data={result.slots} maxHeight="8rem" />
        </div>
      )}
    </div>
  );
}
