import { useCallback, useMemo, useState } from 'react';
import { ExecutionLogTable } from '../components/logs/ExecutionLogTable';
import { ExecutionLogDetail } from '../components/logs/ExecutionLogDetail';
import { MetricCard } from '../components/dashboard/MetricCard';
import { MockModeBanner } from '../components/common/MockModeBanner';
import { useLogs } from '../hooks/useLogs';
import { formatLatency } from '../utils/format';
import type { ExecutionLog } from '../types/log';

export function LogsPage() {
  const { logs, loading, error, fetchLogById } = useLogs();
  const [selectedLog, setSelectedLog] = useState<ExecutionLog | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const stats = useMemo(() => {
    const success = logs.filter((l) => l.success).length;
    const failed = logs.length - success;
    const avgLatency =
      logs.length > 0
        ? logs.reduce((sum, l) => sum + l.latency_ms, 0) / logs.length
        : 0;
    return { total: logs.length, success, failed, avgLatency };
  }, [logs]);

  const handleSelect = useCallback(
    async (log: ExecutionLog) => {
      setSelectedLog(log);
      setDetailLoading(true);
      const detail = await fetchLogById(log.id);
      if (detail) setSelectedLog(detail);
      setDetailLoading(false);
    },
    [fetchLogById],
  );

  const handleClose = () => setSelectedLog(null);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">
          Execution Logs
        </h2>
        <p className="mt-1 text-sm text-secondary">
          Browse agent execution history, tool invocations, and response
          outcomes.
        </p>
      </div>

      {error && <MockModeBanner />}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Total Logs" value={stats.total} icon="📋" />
        <MetricCard
          title="Success"
          value={stats.success}
          variant="success"
          icon="✓"
        />
        <MetricCard
          title="Failed"
          value={stats.failed}
          variant="danger"
          icon="✗"
        />
        <MetricCard
          title="Avg Latency"
          value={formatLatency(stats.avgLatency)}
          variant="primary"
          icon="⏱"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-5">
        <div className="xl:col-span-3">
          <ExecutionLogTable
            logs={logs}
            loading={loading}
            selectedId={selectedLog?.id ?? null}
            onSelect={(log) => void handleSelect(log)}
          />
        </div>

        {selectedLog && (
          <button
            type="button"
            aria-label="Close detail panel"
            className="fixed inset-0 z-40 bg-graphite/20 backdrop-blur-sm xl:hidden"
            onClick={handleClose}
          />
        )}

        <div
          className={
            selectedLog
              ? 'fixed inset-x-0 bottom-0 z-50 p-4 xl:static xl:col-span-2 xl:p-0'
              : 'hidden xl:block xl:col-span-2'
          }
        >
          <ExecutionLogDetail
            log={selectedLog}
            loading={detailLoading}
            onClose={handleClose}
          />
        </div>
      </div>
    </div>
  );
}
