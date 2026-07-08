import { AlertCircle } from 'lucide-react';

type MockModeBannerProps = {
  className?: string;
};

export function MockModeBanner({ className = '' }: MockModeBannerProps) {
  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border border-warning/25 bg-warning-soft px-3 py-1.5 ${className}`}
    >
      <AlertCircle className="h-3.5 w-3.5 shrink-0 text-warning" strokeWidth={2} />
      <p className="text-[11px] font-medium text-warning">
        Mock Mode · Backend API unavailable, using sample data
      </p>
    </div>
  );
}
