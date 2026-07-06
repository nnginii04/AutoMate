import { apiClient } from './client';
import type { VehicleState } from '../types/vehicle';

export const vehicleApi = {
  getState: async (): Promise<VehicleState> => {
    const { data } = await apiClient.get<VehicleState>('/api/vehicle/state');
    return data;
  },

  updateState: async (
    partial: Partial<VehicleState>,
  ): Promise<VehicleState> => {
    const { data } = await apiClient.patch<VehicleState>(
      '/api/vehicle/state',
      partial,
    );
    return data;
  },
};
