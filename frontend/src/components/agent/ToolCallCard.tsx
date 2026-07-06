import { JsonViewer } from '../common/JsonViewer';
import { SuccessBadge, ToolBadge } from '../common/Badge';
import type { ToolCall, ToolResult } from '../../types/agent';

type ToolCallCardProps = {
  toolCall?: ToolCall | null;
  toolResult?: ToolResult | null;
};

export function ToolCallCard({ toolCall, toolResult }: ToolCallCardProps) {
  if (!toolCall && !toolResult) {
    return (
      <div className="rounded-xl border border-border bg-surface-soft px-6 py-10 text-center">
        <p className="text-sm font-medium text-secondary">No Tool Called</p>
        <p className="mt-1 text-xs text-muted">
          The agent responded without invoking a vehicle API tool.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {toolCall && (
        <div className="rounded-xl border border-primary/20 bg-primary-soft/40 p-5">
          <div className="mb-3 flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-primary">
              Tool Call
            </span>
            <ToolBadge name={toolCall.name} />
          </div>
          <p className="mb-2 text-xs text-secondary">Arguments</p>
          <JsonViewer data={toolCall.arguments} maxHeight="12rem" />
        </div>
      )}

      {toolResult && (
        <div
          className={`rounded-xl border p-5 ${
            toolResult.success
              ? 'border-success/25 bg-success-soft/40'
              : 'border-danger/25 bg-danger-soft/40'
          }`}
        >
          <div className="mb-3 flex items-center justify-between gap-2">
            <span
              className={`text-xs font-bold uppercase tracking-wider ${
                toolResult.success ? 'text-success' : 'text-danger'
              }`}
            >
              Tool Result
            </span>
            <SuccessBadge success={toolResult.success} />
          </div>
          <p className="mb-3 text-sm text-foreground">{toolResult.message}</p>
          {toolResult.updated_vehicle_state && (
            <div>
              <p className="mb-2 text-xs text-secondary">
                Updated Vehicle State
              </p>
              <JsonViewer
                data={toolResult.updated_vehicle_state}
                maxHeight="8rem"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
