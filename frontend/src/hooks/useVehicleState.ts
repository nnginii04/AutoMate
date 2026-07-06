import { useCallback, useEffect, useState } from 'react';
import { vehicleApi } from '../api/vehicleApi';
import { safeApiCall } from '../api/client';
import type { ApiError } from '../api/client';
import type { VehicleState } from '../types/vehicle';
import { defaultVehicleState } from '../utils/mockData';

type UseVehicleStateReturn = {
  vehicleState: VehicleState;
  loading: boolean;
  error: ApiError | null;
  refresh: () => Promise<void>;
  updateState: (partial: Partial<VehicleState>) => Promise<void>;
  mergeState: (partial: Partial<VehicleState>) => void;
};

export function useVehicleState(): UseVehicleStateReturn {
  const [vehicleState, setVehicleState] =
    useState<VehicleState>(defaultVehicleState);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const mergeState = useCallback((partial: Partial<VehicleState>) => {
    setVehicleState((prev) => ({ ...prev, ...partial }));
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    const { data, error: apiError } = await safeApiCall(
      () => vehicleApi.getState(),
      defaultVehicleState,
    );
    if (data) setVehicleState(data);
    setError(apiError);
    setLoading(false);
  }, []);

  const updateState = useCallback(async (partial: Partial<VehicleState>) => {
    setVehicleState((prev) => ({ ...prev, ...partial }));
    setLoading(true);

    const { data, error: apiError } = await safeApiCall(() =>
      vehicleApi.updateState(partial),
    );
    if (data) setVehicleState(data);
    setError(apiError);
    setLoading(false);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { vehicleState, loading, error, refresh, updateState, mergeState };
}
