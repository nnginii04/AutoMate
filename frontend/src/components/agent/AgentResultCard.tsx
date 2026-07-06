import { Badge, IntentBadge, SuccessBadge } from '../common/Badge';
import { JsonViewer } from '../common/JsonViewer';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { formatPercent } from '../../utils/format';
import type { AgentRunResponse } from '../../types/agent';
import type { ApiError } from '../../api/client';

type AgentResultCardProps = {
  result: AgentRunResponse | null;
  loading: boolean;
  error: ApiError | null;
};

function getResponseBorderClass(result: AgentRunResponse): string {
  if (result.safety_blocked) return 'border-warning/40 bg-warning-soft/30';
  if (!result.success) return 'border-danger/30 bg-danger-soft/20';
  return 'border-success/30 bg-success-soft/20';
}

function StatusBadges({ result }: { result: AgentRunResponse }) {
  return (
    <div className="flex flex-wrap gap-2">
      <IntentBadge intent={result.intent} />
      <Badge variant="primary">
        Confidence {formatPercent(result.confidence)}
      </Badge>
      <SuccessBadge success={result.success} />
      {result.safety_blocked && (
        <Badge variant="warning">Safety Block</Badge>
      )}
      {result.fallback && <Badge variant="warning">Fallback</Badge>}
    </div>
  );
}

export function AgentResultCard({
  result,
  loading,
  error,
}: AgentResultCardProps) {
  if (loading) {
    return (
      <div className="mobility-card p-10">
        <LoadingSpinner label="Running agent…" />
      </div>
    );
  }

  if (error && !result) {
    return (
      <div className="mobility-card border-danger/30 p-6">
        <h3 className="mb-2 text-sm font-semibold text-danger">Agent Error</h3>
        <p className="text-sm text-secondary">{error.message}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="mobility-card p-10 text-center">
        <p className="text-sm text-secondary">
          Run the agent to see the response, intent classification, and tool
          mapping here.
        </p>
      </div>
    );
  }

  return (
    <div className="mobility-card p-6">
      <h3 className="mb-5 text-base font-semibold text-foreground">
        Agent Response
      </h3>

      {/* 1. Final Response */}
      <div
        className={`mb-5 rounded-xl border-2 p-5 ${getResponseBorderClass(result)}`}
      >
        <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-secondary">
          Final Response
        </p>
        <p className="text-base font-medium leading-relaxed text-foreground">
          {result.final_response}
        </p>
      </div>

      {/* 2. Badges */}
      <div className="mb-5">
        <StatusBadges result={result} />
        {result.failure_reason && (
          <p className="mt-3 text-sm text-danger">{result.failure_reason}</p>
        )}
      </div>

      {/* 3 & 4. Tool Call / Tool Result handled in ToolCallCard separately */}

      {/* 5. Slots */}
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted">
          Slots
        </p>
        <JsonViewer data={result.slots} maxHeight="10rem" />
      </div>
    </div>
  );
}
