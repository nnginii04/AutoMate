import type { AgentRunResponse } from '../../types/agent';
import type { VehicleState } from '../../types/vehicle';
import { formatPercent, truncateText } from '../../utils/format';

type AgentFlowTimelineProps = {
  userInput: string;
  vehicleState: VehicleState;
  result: AgentRunResponse | null;
  active: boolean;
};

type StepStatus = 'idle' | 'active' | 'success' | 'warning' | 'danger' | 'cyan';

type PipelineStep = {
  key: string;
  label: string;
  getValue: () => string | null;
  getStatus: () => StepStatus;
};

const nodeStyles: Record<StepStatus, string> = {
  idle: 'border-border bg-surface-soft text-muted',
  active: 'border-primary/40 bg-primary-soft text-primary',
  success: 'border-success/40 bg-success-soft text-success',
  warning: 'border-warning/40 bg-warning-soft text-warning',
  danger: 'border-danger/40 bg-danger-soft text-danger',
  cyan: 'border-cyan/40 bg-cyan-soft text-cyan',
};

const lineStyles: Record<StepStatus, string> = {
  idle: 'bg-border',
  active: 'bg-primary/50',
  success: 'bg-success/50',
  warning: 'bg-warning/50',
  danger: 'bg-danger/50',
  cyan: 'bg-cyan/50',
};

export function AgentFlowTimeline({
  userInput,
  vehicleState,
  result,
  active,
}: AgentFlowTimelineProps) {
  const steps: PipelineStep[] = [
    {
      key: 'input',
      label: 'Input',
      getValue: () =>
        active && userInput.trim() ? truncateText(userInput, 22) : null,
      getStatus: () => (active && userInput.trim() ? 'active' : 'idle'),
    },
    {
      key: 'context',
      label: 'Context',
      getValue: () =>
        active ? `${vehicleState.speed} km/h · ${vehicleState.weather}` : null,
      getStatus: () => (active ? 'cyan' : 'idle'),
    },
    {
      key: 'intent',
      label: 'Intent',
      getValue: () =>
        result
          ? truncateText(
              `${result.intent} ${formatPercent(result.confidence, 0)}`,
              24,
            )
          : null,
      getStatus: () => (result ? 'active' : 'idle'),
    },
    {
      key: 'safety',
      label: 'Safety',
      getValue: () => {
        if (!result) return null;
        return result.safety_blocked ? 'Blocked' : 'Passed';
      },
      getStatus: () => {
        if (!result) return 'idle';
        return result.safety_blocked ? 'warning' : 'success';
      },
    },
    {
      key: 'tool',
      label: 'Tool',
      getValue: () => {
        if (!result) return null;
        return result.tool_call?.name ?? 'No tool';
      },
      getStatus: () => {
        if (!result) return 'idle';
        return result.tool_call ? 'cyan' : 'idle';
      },
    },
    {
      key: 'result',
      label: 'Result',
      getValue: () => {
        if (!result) return null;
        return result.success ? 'Success' : 'Failed';
      },
      getStatus: () => {
        if (!result) return 'idle';
        return result.success ? 'success' : 'danger';
      },
    },
  ];

  return (
    <div className="console-card p-4">
      <h3 className="text-sm font-bold text-foreground">
        Agent Decision Pipeline
      </h3>

      <div className="mt-3 overflow-x-auto">
        <div className="flex min-w-[560px] items-center">
          {steps.map((step, index) => {
            const value = step.getValue();
            const status = active && value ? step.getStatus() : 'idle';
            const isLast = index === steps.length - 1;

            return (
              <div key={step.key} className="flex flex-1 items-center">
                <div
                  className={`flex h-[72px] min-w-0 flex-1 flex-col justify-center rounded-xl border px-2.5 py-2 ${nodeStyles[status]}`}
                >
                  <span className="text-[10px] font-semibold">{step.label}</span>
                  <span className="mt-1 truncate text-[11px] leading-snug">
                    {value ?? '—'}
                  </span>
                </div>
                {!isLast && (
                  <div className={`mx-1 h-px w-3 shrink-0 ${lineStyles[status]}`} />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
