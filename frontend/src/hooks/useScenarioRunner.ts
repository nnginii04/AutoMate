import { useCallback, useEffect, useState } from 'react';
import { scenarioApi } from '../api/scenarioApi';
import { safeApiCall, type ApiError } from '../api/client';
import type {
  RunAllScenariosResponse,
  ScenarioAccuracySummary,
  TestScenario,
  TestScenarioRunResponse,
} from '../types/scenario';
import { mockRunAllScenarios, mockScenarios } from '../utils/mockData';

type UseScenarioRunnerReturn = {
  scenarios: TestScenario[];
  results: TestScenarioRunResponse[];
  summary: ScenarioAccuracySummary | null;
  batchId: string | null;
  loading: boolean;
  running: boolean;
  error: ApiError | null;
  refreshScenarios: () => Promise<void>;
  runAll: () => Promise<void>;
  runOne: (scenarioId: string) => Promise<void>;
};

export function useScenarioRunner(): UseScenarioRunnerReturn {
  const [scenarios, setScenarios] = useState<TestScenario[]>([]);
  const [results, setResults] = useState<TestScenarioRunResponse[]>([]);
  const [summary, setSummary] = useState<ScenarioAccuracySummary | null>(null);
  const [batchId, setBatchId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const refreshScenarios = useCallback(async () => {
    setLoading(true);
    const { data, error: apiError } = await safeApiCall(
      () => scenarioApi.list(),
      mockScenarios,
    );
    setScenarios(data ?? []);
    setError(apiError);
    setLoading(false);
  }, []);

  const applyRunAll = useCallback((payload: RunAllScenariosResponse) => {
    setBatchId(payload.batch_id);
    setSummary(payload.summary);
    setResults(payload.results);
  }, []);

  const runAll = useCallback(async () => {
    setRunning(true);
    const { data, error: apiError } = await safeApiCall(
      () => scenarioApi.runAll(),
      mockRunAllScenarios,
    );
    if (data) {
      applyRunAll(data);
    }
    setError(apiError);
    setRunning(false);
  }, [applyRunAll]);

  const runOne = useCallback(async (scenarioId: string) => {
    setRunning(true);
    const { data, error: apiError } = await safeApiCall(() =>
      scenarioApi.run(scenarioId),
    );
    if (data) {
      setResults((prev) => {
        const filtered = prev.filter((item) => item.scenario_id !== scenarioId);
        return [...filtered, data];
      });
    }
    setError(apiError);
    setRunning(false);
  }, []);

  useEffect(() => {
    void refreshScenarios();
  }, [refreshScenarios]);

  return {
    scenarios,
    results,
    summary,
    batchId,
    loading,
    running,
    error,
    refreshScenarios,
    runAll,
    runOne,
  };
}
