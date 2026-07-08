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
    <div className="space-y-4">
      {/* Hero Header */}
      <header>
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-foreground">
              AutoMate Agent Console
            </h1>
            <p className="mt-0.5 max-w-xl text-sm leading-relaxed text-secondary">
              Context-aware vehicle AI agent for intent detection, safety
              validation, and tool calling.
            </p>
          </div>
          <div className="flex flex-wrap gap-1.5">
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
        <div className="mt-3 h-0.5 rounded-full bg-gradient-to-r from-graphite via-primary to-cyan" />
        {mockMode && <MockModeBanner className="mt-3" />}
      </header>

      {/* Row 1: Command 60% | Cockpit 40% */}
      <div className="grid gap-4 lg:grid-cols-[3fr_2fr]">
        <div className="console-card p-4">
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

      {/* Row 2: Pipeline */}
      <AgentFlowTimeline
        userInput={lastInput}
        vehicleState={vehicleState}
        result={result}
        active={hasRun}
      />

      {/* Row 3: Response 55% | Tool 45% */}
      <div className="grid gap-4 lg:grid-cols-[11fr_9fr]">
        <AgentResultCard
          result={result}
          loading={agentLoading}
          error={agentError}
        />
        <div className="console-card p-4">
          <p className="console-label">Tool execution</p>
          <h3 className="mt-0.5 text-sm font-bold text-foreground">
            Tool Execution Result
          </h3>
          <div className="mt-3">
            <ToolCallCard
              toolCall={result?.tool_call}
              toolResult={result?.tool_result}
            />
          </div>
        </div>
      </div>

      {/* Row 4: Scenario (collapsed) */}
      <VehicleStateEditor
        vehicleState={vehicleState}
        onApply={updateState}
        loading={vehicleLoading}
        error={vehicleError}
      />
    </div>
  );
}
