import { apiClient } from './client';
import type { DistributionItem, EvaluationSummary } from '../types/evaluation';

export const evaluationApi = {
  getSummary: async (): Promise<EvaluationSummary> => {
    const { data } = await apiClient.get<EvaluationSummary>(
      '/api/evaluation/summary',
    );
    return data;
  },

  getIntentDistribution: async (): Promise<DistributionItem[]> => {
    const { data } = await apiClient.get<DistributionItem[]>(
      '/api/evaluation/intent-distribution',
    );
    return data;
  },

  getToolUsage: async (): Promise<DistributionItem[]> => {
    const { data } = await apiClient.get<DistributionItem[]>(
      '/api/evaluation/tool-usage',
    );
    return data;
  },
};
