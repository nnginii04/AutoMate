import { useCallback, useEffect, useState } from 'react';
import { evaluationApi } from '../api/evaluationApi';
import { safeApiCall } from '../api/client';
import type { ApiError } from '../api/client';
import type { DistributionItem, EvaluationSummary } from '../types/evaluation';
import {
  mockEvaluationSummary,
  mockIntentDistribution,
  mockToolUsage,
} from '../utils/mockData';

type UseEvaluationReturn = {
  summary: EvaluationSummary | null;
  intentDistribution: DistributionItem[];
  toolUsage: DistributionItem[];
  loading: boolean;
  error: ApiError | null;
  refresh: () => Promise<void>;
};

export function useEvaluation(): UseEvaluationReturn {
  const [summary, setSummary] = useState<EvaluationSummary | null>(null);
  const [intentDistribution, setIntentDistribution] = useState<
    DistributionItem[]
  >([]);
  const [toolUsage, setToolUsage] = useState<DistributionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);

    const [summaryResult, intentResult, toolResult] = await Promise.all([
      safeApiCall(() => evaluationApi.getSummary(), mockEvaluationSummary),
      safeApiCall(
        () => evaluationApi.getIntentDistribution(),
        mockIntentDistribution,
      ),
      safeApiCall(() => evaluationApi.getToolUsage(), mockToolUsage),
    ]);

    setSummary(summaryResult.data);
    setIntentDistribution(intentResult.data ?? []);
    setToolUsage(toolResult.data ?? []);

    const firstError =
      summaryResult.error ?? intentResult.error ?? toolResult.error ?? null;
    setError(firstError);
    setLoading(false);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    summary,
    intentDistribution,
    toolUsage,
    loading,
    error,
    refresh,
  };
}
