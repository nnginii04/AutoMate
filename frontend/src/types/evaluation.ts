export type EvaluationSummary = {
  total_requests: number;
  success_requests: number;
  failed_requests: number;
  tool_call_success_rate: number;
  average_latency_ms: number;
  safety_block_count: number;
  fallback_count: number;
};

export type DistributionItem = {
  name: string;
  count: number;
};
