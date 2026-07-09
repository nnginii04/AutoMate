import { useEffect, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import type { ApiError } from '../../api/client';
import type { VehicleState } from '../../types/vehicle';

type EditableFields = Pick<
  VehicleState,
  | 'speed'
  | 'indoor_temperature'
  | 'outdoor_temperature'
  | 'battery_level'
  | 'fuel_level'
  | 'driver_status'
  | 'driving_mode'
  | 'is_driving'
  | 'weather'
  | 'window_status'
  | 'air_conditioner_status'
  | 'media_status'
  | 'road_name'
  | 'road_type'
  | 'speed_limit'
  | 'is_school_zone'
  | 'navigation_active'
>;

type VehicleStateEditorProps = {
  vehicleState: VehicleState;
  onApply: (partial: Partial<VehicleState>) => Promise<void>;
  loading?: boolean;
  error?: ApiError | null;
};

type FieldConfig = {
  key: keyof EditableFields;
  label: string;
  type: 'number' | 'text' | 'boolean' | 'select';
  options?: string[];
  min?: number;
  max?: number;
};

const FIELDS: FieldConfig[] = [
  { key: 'speed', label: 'Speed', type: 'number', min: 0, max: 200 },
  { key: 'speed_limit', label: 'Speed Limit', type: 'number', min: 0, max: 200 },
  { key: 'road_name', label: 'Road Name', type: 'text' },
  {
    key: 'road_type',
    label: 'Road Type',
    type: 'select',
    options: ['highway', 'urban', 'local', 'school_zone'],
  },
  { key: 'is_school_zone', label: 'School Zone', type: 'boolean' },
  { key: 'navigation_active', label: 'Navigation', type: 'boolean' },
  { key: 'indoor_temperature', label: 'Indoor °C', type: 'number', min: -10, max: 40 },
  { key: 'outdoor_temperature', label: 'Outdoor °C', type: 'number', min: -30, max: 50 },
  { key: 'battery_level', label: 'Battery %', type: 'number', min: 0, max: 100 },
  { key: 'fuel_level', label: 'Fuel %', type: 'number', min: 0, max: 100 },
  { key: 'driver_status', label: 'Driver', type: 'text' },
  {
    key: 'driving_mode',
    label: 'Mode',
    type: 'select',
    options: ['city', 'highway', 'comfort', 'sport', 'eco'],
  },
  { key: 'is_driving', label: 'Driving', type: 'boolean' },
  {
    key: 'weather',
    label: 'Weather',
    type: 'select',
    options: ['sunny', 'cloudy', 'rainy', 'snowy', 'foggy'],
  },
  {
    key: 'window_status',
    label: 'Window',
    type: 'select',
    options: ['open', 'closed', 'partial'],
  },
  {
    key: 'air_conditioner_status',
    label: 'A/C',
    type: 'select',
    options: ['on', 'off', 'heating', 'cooling', 'auto'],
  },
  {
    key: 'media_status',
    label: 'Media',
    type: 'select',
    options: ['on', 'off', 'playing', 'paused'],
  },
];

function pickEditable(state: VehicleState): EditableFields {
  return {
    speed: state.speed,
    indoor_temperature: state.indoor_temperature,
    outdoor_temperature: state.outdoor_temperature,
    battery_level: state.battery_level,
    fuel_level: state.fuel_level,
    driver_status: state.driver_status,
    driving_mode: state.driving_mode,
    is_driving: state.is_driving,
    weather: state.weather,
    window_status: state.window_status,
    air_conditioner_status: state.air_conditioner_status,
    media_status: state.media_status,
    road_name: state.road_name ?? '',
    road_type: state.road_type ?? 'urban',
    speed_limit: state.speed_limit ?? 60,
    is_school_zone: state.is_school_zone ?? false,
    navigation_active: state.navigation_active ?? true,
  };
}

export function VehicleStateEditor({
  vehicleState,
  onApply,
  loading = false,
  error,
}: VehicleStateEditorProps) {
  const [draft, setDraft] = useState<EditableFields>(() =>
    pickEditable(vehicleState),
  );

  useEffect(() => {
    setDraft(pickEditable(vehicleState));
  }, [vehicleState]);

  const handleChange = (
    key: keyof EditableFields,
    value: string | number | boolean,
  ) => {
    setDraft((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="console-card overflow-hidden">
      <details className="group">
        <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-3 [&::-webkit-details-marker]:hidden">
          <div>
            <h3 className="text-sm font-bold text-foreground">
              Scenario Control Panel
            </h3>
            <p className="text-[11px] text-muted">
              Adjust vehicle context for testing
            </p>
          </div>
          <ChevronDown
            className="h-4 w-4 text-muted transition-transform group-open:rotate-180"
            strokeWidth={2}
          />
        </summary>

        <div className="border-t border-border px-4 pb-4 pt-3">
          <div className="grid grid-cols-3 gap-3">
            {FIELDS.map((field) => (
              <div key={field.key}>
                <label
                  htmlFor={`vehicle-${field.key}`}
                  className="mb-1 block text-[11px] font-medium text-secondary"
                >
                  {field.label}
                </label>

                {field.type === 'boolean' ? (
                  <select
                    id={`vehicle-${field.key}`}
                    value={String(draft[field.key])}
                    onChange={(e) =>
                      handleChange(field.key, e.target.value === 'true')
                    }
                    className="console-input py-1.5"
                  >
                    <option value="true">true</option>
                    <option value="false">false</option>
                  </select>
                ) : field.type === 'select' && field.options ? (
                  <select
                    id={`vehicle-${field.key}`}
                    value={String(draft[field.key])}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    className="console-input py-1.5"
                  >
                    {field.options.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    id={`vehicle-${field.key}`}
                    type={field.type}
                    value={draft[field.key] as number | string}
                    min={field.min}
                    max={field.max}
                    onChange={(e) =>
                      handleChange(
                        field.key,
                        field.type === 'number'
                          ? Number(e.target.value)
                          : e.target.value,
                      )
                    }
                    className="console-input py-1.5"
                  />
                )}
              </div>
            ))}
          </div>

          <div className="mt-4 flex items-center justify-end gap-2">
            {error && (
              <span className="text-[11px] text-warning">{error.message}</span>
            )}
            <button
              type="button"
              onClick={() => void onApply(draft)}
              disabled={loading}
              className="console-btn-secondary"
            >
              {loading ? 'Applying…' : 'Apply Changes'}
            </button>
          </div>
        </div>
      </details>
    </div>
  );
}
