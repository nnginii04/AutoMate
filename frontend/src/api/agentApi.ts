import { apiClient } from './client';
import type { AgentRunRequest, AgentRunResponse } from '../types/agent';

export const agentApi = {
  run: async (payload: AgentRunRequest): Promise<AgentRunResponse> => {
    const { data } = await apiClient.post<AgentRunResponse>(
      '/api/agent/run',
      payload,
    );
    return data;
  },
};
