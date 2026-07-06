import type { ReactNode } from 'react';

type BadgeVariant =
  | 'success'
  | 'danger'
  | 'warning'
  | 'primary'
  | 'muted'
  | 'cyan';

type BadgeProps = {
  children: ReactNode;
  variant?: BadgeVariant;
  className?: string;
};

const variantStyles: Record<BadgeVariant, string> = {
  success: 'bg-success-soft text-success border-success/20',
  danger: 'bg-danger-soft text-danger border-danger/20',
  warning: 'bg-warning-soft text-warning border-warning/20',
  primary: 'bg-primary-soft text-primary border-primary/20',
  cyan: 'bg-cyan-soft text-cyan border-cyan/20',
  muted: 'bg-surface-soft text-secondary border-border',
};

export function Badge({
  children,
  variant = 'muted',
  className = '',
}: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}

export function IntentBadge({ intent }: { intent: string }) {
  const variant: BadgeVariant =
    intent === 'UNKNOWN' ? 'warning' : 'primary';
  return <Badge variant={variant}>{intent}</Badge>;
}

export function ToolBadge({ name }: { name: string }) {
  return <Badge variant="cyan">{name}</Badge>;
}

export function SuccessBadge({ success }: { success: boolean }) {
  return (
    <Badge variant={success ? 'success' : 'danger'}>
      {success ? 'Success' : 'Failed'}
    </Badge>
  );
}
