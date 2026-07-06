import { useCallback, useState } from 'react';
import { agentApi } from '../api/agentApi';
import { safeApiCall } from '../api/client';
import type { ApiError } from '../api/client';
import type { AgentRunRequest, AgentRunResponse } from '../types/agent';

type UseAgentRunReturn = {
  result: AgentRunResponse | null;
  loading: boolean;
  error: ApiError | null;
  runAgent: (request: AgentRunRequest) => Promise<AgentRunResponse | null>;
  reset: () => void;
};

export function useAgentRun(): UseAgentRunReturn {
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const runAgent = useCallback(async (request: AgentRunRequest) => {
    setLoading(true);
    setError(null);

    const { data, error: apiError } = await safeApiCall(() =>
      agentApi.run(request),
    );

    setResult(data);
    setError(apiError);
    setLoading(false);
    return data;
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setLoading(false);
  }, []);

  return { result, loading, error, runAgent, reset };
}
