import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { EmptyState } from '../common/EmptyState';
import type { DistributionItem } from '../../types/evaluation';

const CHART_COLORS = [
  '#2563EB',
  '#0891B2',
  '#16A34A',
  '#D97706',
  '#DC2626',
  '#6366F1',
  '#9CA3AF',
];

const tooltipStyle = {
  backgroundColor: '#FFFFFF',
  border: '1px solid #E5E7EB',
  borderRadius: '12px',
  color: '#111827',
  fontSize: '12px',
  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.07)',
};

type IntentDistributionChartProps = {
  data: DistributionItem[];
};

export function IntentDistributionChart({ data }: IntentDistributionChartProps) {
  if (data.length === 0) {
    return (
      <EmptyState
        title="No intent data"
        description="Intent distribution will appear once requests are logged."
      />
    );
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="count"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={88}
            paddingAngle={3}
            stroke="#FFFFFF"
            strokeWidth={2}
          >
            {data.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={CHART_COLORS[index % CHART_COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: '11px', color: '#6B7280' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
