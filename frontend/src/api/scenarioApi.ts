import { apiClient } from './client';
import type {
  RunAllScenariosResponse,
  TestScenario,
  TestScenarioRunResponse,
} from '../types/scenario';

export const scenarioApi = {
  list(): Promise<TestScenario[]> {
    return apiClient.get<TestScenario[]>('/api/scenarios').then((r) => r.data);
  },

  run(scenarioId: string): Promise<TestScenarioRunResponse> {
    return apiClient
      .post<TestScenarioRunResponse>(`/api/scenarios/run/${scenarioId}`, {})
      .then((r) => r.data);
  },

  runAll(): Promise<RunAllScenariosResponse> {
    return apiClient
      .post<RunAllScenariosResponse>('/api/scenarios/run-all')
      .then((r) => r.data);
  },
};
