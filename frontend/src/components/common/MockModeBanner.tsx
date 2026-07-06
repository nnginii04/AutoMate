type MockModeBannerProps = {
  className?: string;
};

export function MockModeBanner({ className = '' }: MockModeBannerProps) {
  return (
    <div
      className={`inline-flex items-start gap-3 rounded-xl border border-warning/20 bg-warning-soft px-4 py-3 ${className}`}
    >
      <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-warning/15 text-[10px] font-bold text-warning">
        M
      </span>
      <div>
        <p className="text-xs font-semibold text-warning">Mock Mode</p>
        <p className="mt-0.5 text-xs text-secondary">
          Backend API unavailable. Showing sample execution data.
        </p>
      </div>
    </div>
  );
}
