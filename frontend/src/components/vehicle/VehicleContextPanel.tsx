import { Badge } from '../common/Badge';
import type { VehicleState } from '../../types/vehicle';

type VehicleContextPanelProps = {
  vehicleState: VehicleState;
  loading?: boolean;
};

function ProgressBar({
  label,
  value,
  colorClass,
}: {
  label: string;
  value: number;
  colorClass: string;
}) {
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <span className="text-xs font-medium text-secondary">{label}</span>
        <span className="text-xs font-semibold text-foreground">{value}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-surface-muted">
        <div
          className={`h-full rounded-full transition-all ${colorClass}`}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  );
}

function DrivingDot({ isDriving }: { isDriving: boolean }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span
        className={`h-2 w-2 rounded-full ${
          isDriving ? 'bg-success shadow-[0_0_6px_rgba(22,163,74,0.5)]' : 'bg-muted'
        }`}
      />
      <span className="text-sm font-semibold text-foreground">
        {isDriving ? 'Driving' : 'Parked'}
      </span>
    </span>
  );
}

function hasRiskContext(state: VehicleState): boolean {
  return (
    state.weather === 'rainy' &&
    state.window_status === 'open' &&
    state.is_driving
  );
}

export function VehicleContextPanel({
  vehicleState,
  loading = false,
}: VehicleContextPanelProps) {
  const risk = hasRiskContext(vehicleState);

  const compactItems = [
    { label: 'Weather', value: vehicleState.weather },
    { label: 'Window', value: vehicleState.window_status },
    { label: 'A/C', value: vehicleState.air_conditioner_status },
    { label: 'Media', value: vehicleState.media_status },
    { label: 'Location', value: vehicleState.location },
    { label: 'Mode', value: vehicleState.driving_mode },
    { label: 'Driver', value: vehicleState.driver_status },
    { label: 'Vehicle', value: vehicleState.vehicle_id ?? '—' },
  ];

  return (
    <div className="mobility-card p-6">
      <div className="mb-5 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-foreground">
            Live Vehicle Context
          </h3>
          <p className="mt-1 text-sm text-secondary">
            Real-time vehicle state used for agent decision making.
          </p>
        </div>
        {loading && (
          <span className="status-pill text-muted">Syncing…</span>
        )}
      </div>

      {risk && (
        <div className="mb-5">
          <Badge variant="warning">
            Risk: Rainy weather with window open while driving
          </Badge>
        </div>
      )}

      {/* Primary gauges */}
      <div className="mb-6 grid grid-cols-2 gap-4">
        <div className="rounded-xl border border-border bg-surface-soft p-4">
          <p className="text-xs font-medium uppercase tracking-wider text-muted">
            Speed
          </p>
          <p className="mt-1 text-3xl font-bold tabular-nums text-foreground">
            {vehicleState.speed}
            <span className="ml-1 text-base font-medium text-secondary">
              km/h
            </span>
          </p>
        </div>
        <div className="rounded-xl border border-border bg-surface-soft p-4">
          <p className="text-xs font-medium uppercase tracking-wider text-muted">
            Indoor Temp
          </p>
          <p className="mt-1 text-3xl font-bold tabular-nums text-foreground">
            {vehicleState.indoor_temperature}
            <span className="ml-0.5 text-base font-medium text-secondary">
              °C
            </span>
          </p>
        </div>
        <div className="rounded-xl border border-border bg-surface-soft p-4">
          <p className="text-xs font-medium uppercase tracking-wider text-muted">
            Battery
          </p>
          <p className="mt-1 text-3xl font-bold tabular-nums text-primary">
            {vehicleState.battery_level}%
          </p>
        </div>
        <div className="rounded-xl border border-border bg-surface-soft p-4">
          <p className="text-xs font-medium uppercase tracking-wider text-muted">
            Driving Status
          </p>
          <div className="mt-3">
            <DrivingDot isDriving={vehicleState.is_driving} />
          </div>
        </div>
      </div>

      {/* Progress bars */}
      <div className="mb-6 space-y-3">
        <ProgressBar
          label="Battery Level"
          value={vehicleState.battery_level}
          colorClass="bg-primary"
        />
        <ProgressBar
          label="Fuel Level"
          value={vehicleState.fuel_level}
          colorClass="bg-cyan"
        />
      </div>

      {/* Compact grid */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {compactItems.map((item) => (
          <div
            key={item.label}
            className="rounded-lg border border-border bg-surface px-3 py-2"
          >
            <p className="text-[10px] font-medium uppercase tracking-wide text-muted">
              {item.label}
            </p>
            <p className="mt-0.5 truncate text-xs font-semibold capitalize text-foreground">
              {item.value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
