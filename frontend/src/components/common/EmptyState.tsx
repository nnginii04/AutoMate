import type { ReactNode } from 'react';

type EmptyStateProps = {
  title?: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
  className?: string;
};

export function EmptyState({
  title = 'No data',
  description = 'There is nothing to display yet.',
  icon,
  action,
  className = '',
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center rounded-2xl border border-border bg-surface-soft px-6 py-14 text-center ${className}`}
    >
      {icon && <div className="mb-4 text-2xl text-muted">{icon}</div>}
      <h3 className="text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-2 max-w-sm text-sm text-secondary">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
