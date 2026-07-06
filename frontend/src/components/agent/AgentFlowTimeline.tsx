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
  shortLabel: string;
  getValue: () => string | null;
  getStatus: () => StepStatus;
};

const statusStyles: Record<StepStatus, string> = {
  idle: 'border-border bg-surface-soft text-muted',
  active: 'border-primary/30 bg-primary-soft text-primary',
  success: 'border-success/30 bg-success-soft text-success',
  warning: 'border-warning/30 bg-warning-soft text-warning',
  danger: 'border-danger/30 bg-danger-soft text-danger',
  cyan: 'border-cyan/30 bg-cyan-soft text-cyan',
};

const connectorStyles: Record<StepStatus, string> = {
  idle: 'bg-border',
  active: 'bg-primary/40',
  success: 'bg-success/40',
  warning: 'bg-warning/40',
  danger: 'bg-danger/40',
  cyan: 'bg-cyan/40',
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
      label: 'User Input',
      shortLabel: 'Input',
      getValue: () => (active && userInput.trim() ? truncateText(userInput, 28) : null),
      getStatus: () => (active && userInput.trim() ? 'active' : 'idle'),
    },
    {
      key: 'context',
      label: 'Context',
      shortLabel: 'Ctx',
      getValue: () =>
        active
          ? `${vehicleState.speed}km/h · ${vehicleState.weather}`
          : null,
      getStatus: () => (active ? 'cyan' : 'idle'),
    },
    {
      key: 'intent',
      label: 'Intent',
      shortLabel: 'Intent',
      getValue: () =>
        result
          ? `${result.intent} (${formatPercent(result.confidence, 0)})`
          : null,
      getStatus: () => (result ? 'active' : active ? 'idle' : 'idle'),
    },
    {
      key: 'safety',
      label: 'Safety',
      shortLabel: 'Safe',
      getValue: () => {
        if (!result) return null;
        return result.safety_blocked ? 'Blocked' : 'Passed';
      },
      getStatus: () => {
        if (!result) return active ? 'idle' : 'idle';
        return result.safety_blocked ? 'warning' : 'success';
      },
    },
    {
      key: 'tool',
      label: 'Tool',
      shortLabel: 'Tool',
      getValue: () => {
        if (!result) return null;
        return result.tool_call?.name ?? 'No Tool Called';
      },
      getStatus: () => {
        if (!result) return 'idle';
        return result.tool_call ? 'cyan' : 'idle';
      },
    },
    {
      key: 'execution',
      label: 'Execution',
      shortLabel: 'Exec',
      getValue: () => {
        if (!result) return null;
        if (!result.tool_result) return 'Skipped';
        return result.tool_result.success ? 'Success' : 'Failed';
      },
      getStatus: () => {
        if (!result?.tool_result) return 'idle';
        return result.tool_result.success ? 'success' : 'danger';
      },
    },
    {
      key: 'response',
      label: 'Response',
      shortLabel: 'Resp',
      getValue: () =>
        result ? truncateText(result.final_response, 32) : null,
      getStatus: () => (result ? 'success' : 'idle'),
    },
  ];

  return (
    <div className="mobility-card p-6">
      <h3 className="mb-1 text-base font-semibold text-foreground">
        Agent Decision Flow
      </h3>
      <p className="mb-6 text-sm text-secondary">
        Step-by-step pipeline from user command to final vehicle action.
      </p>

      <div className="overflow-x-auto pb-2">
        <div className="flex min-w-[720px] items-stretch">
          {steps.map((step, index) => {
            const value = step.getValue();
            const status = value ? step.getStatus() : 'idle';
            const isLast = index === steps.length - 1;

            return (
              <div key={step.key} className="flex flex-1 items-center">
                <div
                  className={`flex min-w-[88px] flex-1 flex-col rounded-xl border px-3 py-3 ${statusStyles[status]}`}
                >
                  <span className="text-[10px] font-bold uppercase tracking-wider opacity-70">
                    {step.shortLabel}
                  </span>
                  <span className="mt-1 text-[11px] font-semibold leading-tight">
                    {step.label}
                  </span>
                  <span className="mt-2 text-xs leading-snug opacity-90">
                    {value ?? '—'}
                  </span>
                </div>
                {!isLast && (
                  <div
                    className={`mx-1 h-0.5 w-4 shrink-0 ${connectorStyles[status]}`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
