import { AlertTriangle, Thermometer, Battery, Fuel } from 'lucide-react';
import type { VehicleState } from '../../types/vehicle';

type VehicleContextPanelProps = {
  vehicleState: VehicleState;
  loading?: boolean;
};

function MiniBar({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string;
  value: number;
  icon: typeof Battery;
  color: string;
}) {
  return (
    <div className="flex-1">
      <div className="mb-1 flex items-center justify-between">
        <span className="flex items-center gap-1 text-[11px] font-medium text-secondary">
          <Icon className="h-3 w-3" strokeWidth={2} />
          {label}
        </span>
        <span className="text-xs font-bold tabular-nums text-foreground">
          {value}%
        </span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-border">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  );
}

function hasRainWindowWarning(state: VehicleState): boolean {
  return state.weather === 'rainy' && state.window_status === 'open';
}

export function VehicleContextPanel({
  vehicleState,
  loading = false,
}: VehicleContextPanelProps) {
  const showWarning = hasRainWindowWarning(vehicleState);

  const specs: { label: string; value: string }[] = [
    { label: 'Location', value: vehicleState.location },
    { label: 'Road', value: vehicleState.road_name ?? '—' },
    { label: 'Road Type', value: vehicleState.road_type ?? '—' },
    { label: 'School Zone', value: vehicleState.is_school_zone ? 'yes' : 'no' },
    { label: 'Driver', value: vehicleState.driver_status },
    { label: 'Window', value: vehicleState.window_status },
    { label: 'A/C', value: vehicleState.air_conditioner_status },
    { label: 'Media', value: vehicleState.media_status },
    {
      label: 'Passenger',
      value: `${vehicleState.passenger_count}`,
    },
  ];

  return (
    <div className="console-card flex h-full flex-col p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-bold text-foreground">Vehicle Cockpit</h3>
        {loading && (
          <span className="text-[10px] text-muted">syncing</span>
        )}
      </div>

      {showWarning && (
        <div className="mb-3 flex items-center gap-2 rounded-lg border border-warning/30 bg-warning-soft px-3 py-2">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-warning" />
          <span className="text-[11px] font-medium text-warning">
            Rain detected · Window is open
          </span>
        </div>
      )}

      <div className="flex gap-4">
        {/* Speed cluster */}
        <div className="flex min-w-[100px] flex-col justify-center rounded-xl border border-border bg-graphite px-4 py-3 text-white">
          <span className="text-[10px] font-medium text-white/60">Speed</span>
          <span className="text-4xl font-bold tabular-nums leading-none">
            {vehicleState.speed}
          </span>
          <span className="mt-0.5 text-xs text-white/70">km/h</span>
          {vehicleState.speed_limit != null && (
            <span className="mt-1 text-[10px] text-white/60">
              Limit {vehicleState.speed_limit} km/h
            </span>
          )}
          <span className="mt-2 text-[10px] capitalize text-white/50">
            {vehicleState.driving_mode} mode
          </span>
        </div>

        {/* Secondary gauges */}
        <div className="flex flex-1 flex-col justify-between gap-2">
          <div className="flex items-center gap-3 rounded-xl border border-border bg-surface-soft px-3 py-2.5">
            <Thermometer className="h-4 w-4 text-cyan" strokeWidth={2} />
            <div>
              <p className="text-[10px] text-muted">Indoor</p>
              <p className="text-lg font-bold tabular-nums leading-tight">
                {vehicleState.indoor_temperature}
                <span className="text-xs font-medium text-secondary">°C</span>
              </p>
            </div>
            <div className="ml-auto text-right">
              <p className="text-[10px] text-muted">Outdoor</p>
              <p className="text-sm font-semibold tabular-nums text-secondary">
                {vehicleState.outdoor_temperature}°C
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <MiniBar
              label="Battery"
              value={vehicleState.battery_level}
              icon={Battery}
              color="bg-primary"
            />
            <MiniBar
              label="Fuel"
              value={vehicleState.fuel_level}
              icon={Fuel}
              color="bg-cyan"
            />
          </div>

          <div className="flex items-center gap-1.5">
            <span
              className={`h-2 w-2 rounded-full ${
                vehicleState.is_driving ? 'bg-success' : 'bg-muted'
              }`}
            />
            <span className="text-xs font-medium text-secondary">
              {vehicleState.is_driving ? 'Driving' : 'Parked'}
            </span>
            <span className="ml-auto text-[11px] capitalize text-muted">
              {vehicleState.weather}
            </span>
          </div>
        </div>
      </div>

      {/* Spec list */}
      <div className="mt-3 grid grid-cols-3 gap-x-4 gap-y-1.5 border-t border-border pt-3">
        {specs.map((spec) => (
          <div key={spec.label} className="flex justify-between gap-2 text-[11px]">
            <span className="text-muted">{spec.label}</span>
            <span className="truncate font-medium capitalize text-foreground">
              {spec.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
