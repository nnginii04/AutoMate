import { useCallback, useEffect, useState } from 'react';
import { logApi } from '../api/logApi';
import { safeApiCall } from '../api/client';
import type { ApiError } from '../api/client';
import type { ExecutionLog } from '../types/log';
import { findMockLogById, mockExecutionLogs } from '../utils/mockData';

type UseLogsReturn = {
  logs: ExecutionLog[];
  loading: boolean;
  error: ApiError | null;
  refresh: () => Promise<void>;
  fetchLogById: (logId: number) => Promise<ExecutionLog | null>;
};

export function useLogs(): UseLogsReturn {
  const [logs, setLogs] = useState<ExecutionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    const { data, error: apiError } = await safeApiCall(
      () => logApi.getAll(),
      mockExecutionLogs,
    );
    setLogs(data ?? []);
    setError(apiError);
    setLoading(false);
  }, []);

  const fetchLogById = useCallback(
    async (logId: number): Promise<ExecutionLog | null> => {
      const local = logs.find((log) => log.id === logId) ?? findMockLogById(logId);
      const { data, error: apiError } = await safeApiCall(
        () => logApi.getById(logId),
        local ?? undefined,
      );
      if (apiError) setError(apiError);
      return data;
    },
    [logs],
  );

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { logs, loading, error, refresh, fetchLogById };
}
