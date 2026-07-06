import { useEffect, useState } from 'react';
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
  { key: 'speed', label: 'Speed (km/h)', type: 'number', min: 0, max: 200 },
  {
    key: 'indoor_temperature',
    label: 'Indoor Temp (°C)',
    type: 'number',
    min: -10,
    max: 40,
  },
  {
    key: 'outdoor_temperature',
    label: 'Outdoor Temp (°C)',
    type: 'number',
    min: -30,
    max: 50,
  },
  {
    key: 'battery_level',
    label: 'Battery (%)',
    type: 'number',
    min: 0,
    max: 100,
  },
  { key: 'fuel_level', label: 'Fuel (%)', type: 'number', min: 0, max: 100 },
  { key: 'driver_status', label: 'Driver Status', type: 'text' },
  {
    key: 'driving_mode',
    label: 'Driving Mode',
    type: 'select',
    options: ['city', 'highway', 'comfort', 'sport', 'eco'],
  },
  { key: 'is_driving', label: 'Is Driving', type: 'boolean' },
  {
    key: 'weather',
    label: 'Weather',
    type: 'select',
    options: ['sunny', 'cloudy', 'rainy', 'snowy', 'foggy'],
  },
  {
    key: 'window_status',
    label: 'Window Status',
    type: 'select',
    options: ['open', 'closed', 'partial'],
  },
  {
    key: 'air_conditioner_status',
    label: 'A/C Status',
    type: 'select',
    options: ['on', 'off', 'heating', 'cooling', 'auto'],
  },
  {
    key: 'media_status',
    label: 'Media Status',
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

  const handleApply = () => {
    void onApply(draft);
  };

  return (
    <div className="mobility-card overflow-hidden">
      <details className="group" open>
        <summary className="cursor-pointer list-none px-6 py-5 [&::-webkit-details-marker]:hidden">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-foreground">
                Scenario Control Panel
              </h3>
              <p className="mt-1 text-sm text-secondary">
                Adjust vehicle context values to test agent behavior.
              </p>
            </div>
            <span className="text-muted transition-transform group-open:rotate-180">
              ▾
            </span>
          </div>
        </summary>

        <div className="border-t border-border px-6 pb-6 pt-2">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {FIELDS.map((field) => (
              <div key={field.key}>
                <label
                  htmlFor={`vehicle-${field.key}`}
                  className="mb-1.5 block text-xs font-medium text-secondary"
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
                    className="mobility-input"
                  >
                    <option value="true">true</option>
                    <option value="false">false</option>
                  </select>
                ) : field.type === 'select' && field.options ? (
                  <select
                    id={`vehicle-${field.key}`}
                    value={String(draft[field.key])}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    className="mobility-input"
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
                    className="mobility-input"
                  />
                )}
              </div>
            ))}
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={handleApply}
              disabled={loading}
              className="mobility-btn-secondary"
            >
              {loading ? 'Applying…' : 'Apply Changes'}
            </button>
            {error && (
              <span className="inline-flex items-center rounded-full border border-warning/25 bg-warning-soft px-3 py-1 text-xs text-warning">
                {error.message}
              </span>
            )}
          </div>
        </div>
      </details>
    </div>
  );
}
