export type VehicleState = {
  vehicle_id?: string;
  speed: number;
  indoor_temperature: number;
  outdoor_temperature: number;
  battery_level: number;
  fuel_level: number;
  driver_status: string;
  driving_mode: string;
  time: string;
  location: string;
  passenger_count: number;
  is_driving: boolean;
  weather: string;
  window_status: string;
  air_conditioner_status: string;
  media_status: string;
};

export type Intent =
  | 'CONTROL_CLIMATE'
  | 'SET_NAVIGATION'
  | 'PLAY_MEDIA'
  | 'MAKE_CALL'
  | 'READ_SCHEDULE'
  | 'CHANGE_VEHICLE_SETTING'
  | 'CHECK_VEHICLE_STATUS'
  | 'FIND_NEARBY_PLACE'
  | 'UNKNOWN';

export type ToolCall = {
  name: string;
  arguments: Record<string, unknown>;
};

export type ToolResult = {
  success: boolean;
  tool_name?: string;
  message: string;
  updated_vehicle_state?: Partial<VehicleState>;
};

export type AgentRunRequest = {
  user_input: string;
  vehicle_state: Partial<VehicleState>;
};

export type AgentRunResponse = {
  intent: Intent;
  slots: Record<string, unknown>;
  confidence: number;
  tool_call?: ToolCall | null;
  tool_result?: ToolResult | null;
  final_response: string;
  latency_ms: number;
  success: boolean;
  failure_reason?: string | null;
  safety_blocked?: boolean;
  fallback?: boolean;
  requires_clarification?: boolean;
  nlu_source?: 'llm' | 'rule_based';
};
