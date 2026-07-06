export type ExecutionLog = {
  id: number;
  user_input: string;
  vehicle_state_snapshot: Record<string, unknown>;
  intent: string;
  slots: Record<string, unknown>;
  tool_name?: string | null;
  tool_arguments?: Record<string, unknown> | null;
  tool_result?: Record<string, unknown> | null;
  final_response: string;
  success: boolean;
  failure_reason?: string | null;
  latency_ms: number;
  created_at: string;
};
