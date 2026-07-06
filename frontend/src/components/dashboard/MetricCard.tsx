import type { ReactNode } from 'react';

type MetricCardProps = {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  variant?: 'default' | 'success' | 'danger' | 'warning' | 'primary';
};

const accentBar: Record<string, string> = {
  default: 'bg-border',
  success: 'bg-success',
  danger: 'bg-danger',
  warning: 'bg-warning',
  primary: 'bg-primary',
};

const valueStyles = {
  default: 'text-foreground',
  success: 'text-success',
  danger: 'text-danger',
  warning: 'text-warning',
  primary: 'text-primary',
};

export function MetricCard({
  title,
  value,
  subtitle,
  icon,
  variant = 'default',
}: MetricCardProps) {
  return (
    <div className="mobility-card relative overflow-hidden p-5">
      <div className={`absolute left-0 top-0 h-1 w-full ${accentBar[variant]}`} />
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted">
          {title}
        </p>
        {icon && <span className="text-lg opacity-60">{icon}</span>}
      </div>
      <p
        className={`mt-3 text-3xl font-bold tabular-nums tracking-tight ${valueStyles[variant]}`}
      >
        {value}
      </p>
      {subtitle && (
        <p className="mt-1.5 text-xs text-secondary">{subtitle}</p>
      )}
    </div>
  );
}
