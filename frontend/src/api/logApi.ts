import { apiClient } from './client';
import type { ExecutionLog } from '../types/log';

export const logApi = {
  getAll: async (): Promise<ExecutionLog[]> => {
    const { data } = await apiClient.get<ExecutionLog[]>('/api/logs');
    return data;
  },

  getById: async (logId: number): Promise<ExecutionLog> => {
    const { data } = await apiClient.get<ExecutionLog>(
      `/api/logs/${logId}`,
    );
    return data;
  },
};
