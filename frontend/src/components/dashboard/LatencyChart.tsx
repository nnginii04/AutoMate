import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { EmptyState } from '../common/EmptyState';
import type { ExecutionLog } from '../../types/log';
import { formatDateTime } from '../../utils/format';

const tooltipStyle = {
  backgroundColor: '#FFFFFF',
  border: '1px solid #E5E7EB',
  borderRadius: '12px',
  color: '#111827',
  fontSize: '12px',
  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.07)',
};

type LatencyChartProps = {
  logs: ExecutionLog[];
};

type LatencyPoint = {
  label: string;
  latency_ms: number;
  id: number;
};

function buildLatencyData(logs: ExecutionLog[]): LatencyPoint[] {
  return [...logs]
    .sort(
      (a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    )
    .slice(-12)
    .map((log) => ({
      id: log.id,
      label: formatDateTime(log.created_at).slice(11),
      latency_ms: log.latency_ms,
    }));
}

export function LatencyChart({ logs }: LatencyChartProps) {
  const data = buildLatencyData(logs);

  if (data.length === 0) {
    return (
      <EmptyState
        title="No latency data"
        description="Latency trends will appear once execution logs are available."
      />
    );
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: '#6B7280', fontSize: 11 }}
            axisLine={{ stroke: '#E5E7EB' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#6B7280', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            unit="ms"
          />
          <Tooltip
            contentStyle={tooltipStyle}
            formatter={(value: number) => [`${value}ms`, 'Latency']}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="latency_ms"
            stroke="#0891B2"
            strokeWidth={2.5}
            dot={{ fill: '#0891B2', r: 4, strokeWidth: 2, stroke: '#FFFFFF' }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
