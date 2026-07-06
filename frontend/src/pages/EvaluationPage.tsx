import { IntentDistributionChart } from '../components/dashboard/IntentDistributionChart';
import { LatencyChart } from '../components/dashboard/LatencyChart';
import { MetricCard } from '../components/dashboard/MetricCard';
import { ToolUsageChart } from '../components/dashboard/ToolUsageChart';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { MockModeBanner } from '../components/common/MockModeBanner';
import { useEvaluation } from '../hooks/useEvaluation';
import { useLogs } from '../hooks/useLogs';
import { formatLatency, formatNumber, formatPercent } from '../utils/format';

export function EvaluationPage() {
  const {
    summary,
    intentDistribution,
    toolUsage,
    loading: evalLoading,
    error: evalError,
  } = useEvaluation();

  const { logs, loading: logsLoading, error: logsError } = useLogs();

  const loading = evalLoading || logsLoading;
  const error = evalError ?? logsError;

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <LoadingSpinner label="Loading evaluation data…" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">
          Evaluation Dashboard
        </h2>
        <p className="mt-1 text-sm text-secondary">
          Agent performance metrics, intent distribution, tool usage, and
          response latency analysis.
        </p>
      </div>

      {error && <MockModeBanner />}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <MetricCard
          title="Total Requests"
          value={formatNumber(summary?.total_requests ?? 0)}
          icon="📊"
        />
        <MetricCard
          title="Success Requests"
          value={formatNumber(summary?.success_requests ?? 0)}
          variant="success"
          subtitle={
            summary && summary.total_requests > 0
              ? `${formatPercent(summary.success_requests / summary.total_requests, 0)} success rate`
              : undefined
          }
          icon="✓"
        />
        <MetricCard
          title="Failed Requests"
          value={formatNumber(summary?.failed_requests ?? 0)}
          variant="danger"
          icon="✗"
        />
        <MetricCard
          title="Tool Call Success Rate"
          value={formatPercent(summary?.tool_call_success_rate ?? 0)}
          variant="primary"
          icon="🔧"
        />
        <MetricCard
          title="Average Latency"
          value={formatLatency(summary?.average_latency_ms ?? 0)}
          icon="⏱"
        />
        <MetricCard
          title="Safety Block Count"
          value={formatNumber(summary?.safety_block_count ?? 0)}
          variant="warning"
          icon="🛡"
        />
        <MetricCard
          title="Fallback Count"
          value={formatNumber(summary?.fallback_count ?? 0)}
          variant="warning"
          icon="↩"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="mobility-card p-6">
          <h3 className="text-base font-semibold text-foreground">
            Intent Distribution
          </h3>
          <p className="mt-1 mb-5 text-sm text-secondary">
            Shows how user commands are classified by the agent.
          </p>
          <IntentDistributionChart data={intentDistribution} />
        </div>

        <div className="mobility-card p-6">
          <h3 className="text-base font-semibold text-foreground">
            Tool Usage
          </h3>
          <p className="mt-1 mb-5 text-sm text-secondary">
            Tracks which simulated vehicle APIs are invoked most frequently.
          </p>
          <ToolUsageChart data={toolUsage} />
        </div>
      </div>

      <div className="mobility-card p-6">
        <h3 className="text-base font-semibold text-foreground">
          Recent Request Latency
        </h3>
        <p className="mt-1 mb-5 text-sm text-secondary">
          Measures response time across recent agent executions.
        </p>
        <LatencyChart logs={logs} />
      </div>
    </div>
  );
}
