import type { AgentRunResponse, Intent } from './agent';

export type ExpectedScenarioResult = {
  success?: boolean;
  safety_blocked?: boolean;
  fallback?: boolean;
  requires_clarification?: boolean;
};

export type TestScenario = {
  id: string;
  name: string;
  description: string;
  user_input: string;
  vehicle_state_overrides: Record<string, unknown>;
  expected_intent?: Intent;
  expected_tool?: string;
  expected_result?: ExpectedScenarioResult;
  tags: string[];
};

export type TestScenarioRunResponse = {
  scenario_id: string;
  scenario_name: string;
  agent_response: AgentRunResponse;
  passed: boolean;
  passed_intent?: boolean | null;
  passed_tool?: boolean | null;
  passed_result?: boolean | null;
  passed_safety?: boolean | null;
  checks: Record<string, boolean>;
  run_log_id?: number | null;
  passed_intent_check?: boolean | null;
};

export type ScenarioAccuracySummary = {
  total: number;
  passed: number;
  failed: number;
  intent_accuracy: number;
  tool_accuracy: number;
  safety_accuracy: number;
};

export type RunAllScenariosResponse = {
  batch_id: string;
  summary: ScenarioAccuracySummary;
  results: TestScenarioRunResponse[];
};
