import { useCallback, useMemo, useState } from 'react';
import { AgentInput } from '../components/agent/AgentInput';
import { AgentResultCard } from '../components/agent/AgentResultCard';
import { AgentFlowTimeline } from '../components/agent/AgentFlowTimeline';
import { ToolCallCard } from '../components/agent/ToolCallCard';
import { VehicleContextPanel } from '../components/vehicle/VehicleContextPanel';
import { VehicleStateEditor } from '../components/vehicle/VehicleStateEditor';
import { MockModeBanner } from '../components/common/MockModeBanner';
import { useAgentRun } from '../hooks/useAgentRun';
import { useVehicleState } from '../hooks/useVehicleState';

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function AgentPage() {
  const [userInput, setUserInput] = useState('');
  const [lastInput, setLastInput] = useState('');

  const {
    vehicleState,
    loading: vehicleLoading,
    error: vehicleError,
    updateState,
    mergeState,
  } = useVehicleState();

  const { result, loading: agentLoading, error: agentError, runAgent } =
    useAgentRun();

  const mockMode = Boolean(vehicleError || agentError);

  const handleRunAgent = useCallback(async () => {
    const input = userInput.trim();
    if (!input) return;

    setLastInput(input);

    const response = await runAgent({
      user_input: input,
      vehicle_state: vehicleState,
    });

    if (response?.tool_result?.updated_vehicle_state) {
      mergeState(response.tool_result.updated_vehicle_state);
    }
  }, [userInput, vehicleState, runAgent, mergeState]);

  const hasRun = Boolean(result || agentLoading || (agentError && lastInput));

  const statusPills = useMemo(
    () => [
      {
        label: vehicleState.is_driving ? 'Driving' : 'Parked',
        dot: vehicleState.is_driving,
      },
      { label: `${vehicleState.speed} km/h` },
      { label: capitalize(vehicleState.weather) },
      { label: `Battery ${vehicleState.battery_level}%` },
    ],
    [vehicleState],
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">
            AutoMate Agent Console
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-secondary">
            Context-aware in-vehicle AI agent for safe tool calling.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {statusPills.map((pill) => (
            <span key={pill.label} className="status-pill">
              {'dot' in pill && (
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    pill.dot ? 'bg-success' : 'bg-muted'
                  }`}
                />
              )}
              {pill.label}
            </span>
          ))}
        </div>
      </div>

      {mockMode && <MockModeBanner />}

      {/* Main area */}
      <div className="grid gap-6 xl:grid-cols-2">
        <div className="mobility-card p-6">
          <AgentInput
            value={userInput}
            onChange={setUserInput}
            onRun={() => void handleRunAgent()}
            loading={agentLoading}
          />
        </div>
        <VehicleContextPanel
          vehicleState={vehicleState}
          loading={vehicleLoading}
        />
      </div>

      {/* Bottom area */}
      <AgentFlowTimeline
        userInput={lastInput}
        vehicleState={vehicleState}
        result={result}
        active={hasRun}
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <AgentResultCard
          result={result}
          loading={agentLoading}
          error={agentError}
        />
        <div className="mobility-card p-6">
          <h3 className="mb-1 text-base font-semibold text-foreground">
            Tool Execution Result
          </h3>
          <p className="mb-5 text-sm text-secondary">
            Vehicle API tool invocation and execution outcome.
          </p>
          <ToolCallCard
            toolCall={result?.tool_call}
            toolResult={result?.tool_result}
          />
        </div>
      </div>

      <VehicleStateEditor
        vehicleState={vehicleState}
        onApply={updateState}
        loading={vehicleLoading}
        error={vehicleError}
      />
    </div>
  );
}
