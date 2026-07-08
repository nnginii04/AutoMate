import { CheckCircle2, Play, XCircle, FlaskConical } from 'lucide-react';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { MockModeBanner } from '../components/common/MockModeBanner';
import { MetricCard } from '../components/dashboard/MetricCard';
import { useScenarioRunner } from '../hooks/useScenarioRunner';
import { formatPercent } from '../utils/format';
import type { TestScenario, TestScenarioRunResponse } from '../types/scenario';

function resultForScenario(
  results: TestScenarioRunResponse[],
  scenarioId: string,
): TestScenarioRunResponse | undefined {
  return results.find((item) => item.scenario_id === scenarioId);
}

function ScenarioRow({
  scenario,
  result,
  onRun,
  running,
}: {
  scenario: TestScenario;
  result?: TestScenarioRunResponse;
  onRun: (id: string) => void;
  running: boolean;
}) {
  const passed = result?.passed;
  const hasResult = Boolean(result);

  return (
    <div className="flex items-start justify-between gap-4 border-b border-border px-4 py-3 last:border-b-0">
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-sm font-semibold text-foreground">{scenario.name}</p>
          {hasResult &&
            (passed ? (
              <Badge variant="success">PASS</Badge>
            ) : (
              <Badge variant="danger">FAIL</Badge>
            ))}
          {scenario.tags.map((tag) => (
            <Badge key={tag} variant="muted">
              {tag}
            </Badge>
          ))}
        </div>
        <p className="mt-1 text-xs text-secondary">{scenario.description}</p>
        <p className="mt-1 font-mono text-xs text-muted">"{scenario.user_input}"</p>
        {result && (
          <div className="mt-2 flex flex-wrap gap-3 text-[11px] text-secondary">
            <span>Intent: {result.agent_response.intent}</span>
            {result.agent_response.tool_call?.name && (
              <span>Tool: {result.agent_response.tool_call.name}</span>
            )}
            <span>{result.agent_response.latency_ms}ms</span>
          </div>
        )}
      </div>
      <button
        type="button"
        disabled={running}
        onClick={() => onRun(scenario.id)}
        className="shrink-0 rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-semibold text-secondary transition-colors hover:border-primary hover:text-primary disabled:opacity-50"
      >
        Run
      </button>
    </div>
  );
}

export function ScenarioRunnerPage() {
  const {
    scenarios,
    results,
    summary,
    batchId,
    loading,
    running,
    error,
    runAll,
    runOne,
  } = useScenarioRunner();

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <LoadingSpinner label="Loading test scenarios…" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FlaskConical className="h-6 w-6 text-primary" />
            <h2 className="text-2xl font-bold tracking-tight text-foreground">
              Scenario Runner
            </h2>
          </div>
          <p className="mt-1 text-sm text-secondary">
            Run integration scenarios against intent, tool, and safety expectations.
          </p>
        </div>
        <button
          type="button"
          disabled={running}
          onClick={() => void runAll()}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {running ? (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
          ) : (
            <Play className="h-4 w-4" />
          )}
          Run All Tests
        </button>
      </div>

      {error && <MockModeBanner />}

      {summary && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            <MetricCard
              title="Total"
              value={summary.total}
              variant="default"
            />
            <MetricCard
              title="Passed"
              value={summary.passed}
              variant="success"
              icon={<CheckCircle2 className="h-4 w-4" />}
            />
            <MetricCard
              title="Failed"
              value={summary.failed}
              variant="danger"
              icon={<XCircle className="h-4 w-4" />}
            />
            <MetricCard
              title="Intent Accuracy"
              value={formatPercent(summary.intent_accuracy)}
              variant="primary"
            />
            <MetricCard
              title="Tool Accuracy"
              value={formatPercent(summary.tool_accuracy)}
              variant="primary"
            />
            <MetricCard
              title="Safety Accuracy"
              value={formatPercent(summary.safety_accuracy)}
              variant="warning"
            />
          </div>
          {batchId && (
            <p className="text-xs text-muted">
              Batch ID: <span className="font-mono">{batchId}</span>
            </p>
          )}
        </>
      )}

      <div className="mobility-card overflow-hidden">
        <div className="border-b border-border px-4 py-3">
          <h3 className="text-base font-semibold text-foreground">
            Scenarios ({scenarios.length})
          </h3>
          <p className="text-xs text-secondary">
            Click Run on a single scenario or use Run All Tests above.
          </p>
        </div>
        <div>
          {scenarios.map((scenario) => (
            <ScenarioRow
              key={scenario.id}
              scenario={scenario}
              result={resultForScenario(results, scenario.id)}
              onRun={(id) => void runOne(id)}
              running={running}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
