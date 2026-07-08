import { Wrench } from 'lucide-react';
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
      <div className="flex items-center gap-2.5 rounded-lg border border-border bg-surface-soft px-3 py-3">
        <Wrench className="h-3.5 w-3.5 text-muted" strokeWidth={2} />
        <p className="text-xs text-muted">No tool called</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {toolCall && (
        <div>
          <div className="mb-1.5 flex items-center gap-2">
            <span className="text-[11px] font-semibold text-secondary">
              Tool name
            </span>
            <ToolBadge name={toolCall.name} />
          </div>
          <p className="mb-1 text-[11px] text-muted">Arguments</p>
          <JsonViewer data={toolCall.arguments} maxHeight="6rem" />
        </div>
      )}

      {toolResult && (
        <div className="rounded-lg border border-border bg-surface-soft p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-[11px] font-semibold text-secondary">
              Result message
            </span>
            <SuccessBadge success={toolResult.success} />
          </div>
          <p className="text-sm text-foreground">{toolResult.message}</p>
          {toolResult.updated_vehicle_state && (
            <div className="mt-2">
              <p className="mb-1 text-[11px] text-muted">Updated vehicle state</p>
              <JsonViewer
                data={toolResult.updated_vehicle_state}
                maxHeight="5rem"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
