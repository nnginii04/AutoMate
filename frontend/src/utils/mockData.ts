import type { VehicleState } from '../types/vehicle';
import type { AgentRunResponse } from '../types/agent';
import type { ExecutionLog } from '../types/log';
import type { EvaluationSummary, DistributionItem } from '../types/evaluation';

export const defaultVehicleState: VehicleState = {
  vehicle_id: 'VH-001',
  speed: 72,
  indoor_temperature: 18,
  outdoor_temperature: 3,
  battery_level: 68,
  fuel_level: 42,
  driver_status: 'normal',
  driving_mode: 'highway',
  time: '22:30',
  location: 'Daejeon',
  passenger_count: 2,
  is_driving: true,
  weather: 'rainy',
  window_status: 'open',
  air_conditioner_status: 'off',
  media_status: 'off',
};

export const mockVehicleState: VehicleState = defaultVehicleState;

const snapshot = (): Record<string, unknown> =>
  ({ ...defaultVehicleState }) as unknown as Record<string, unknown>;

export const mockAgentResponse: AgentRunResponse = {
  intent: 'CONTROL_CLIMATE',
  slots: { target_temperature: 24 },
  confidence: 0.92,
  tool_call: {
    name: 'setClimate',
    arguments: { temperature: 24, mode: 'heating' },
  },
  tool_result: {
    success: true,
    tool_name: 'setClimate',
    message: 'Indoor temperature set to 24°C',
    updated_vehicle_state: {
      indoor_temperature: 24,
      air_conditioner_status: 'heating',
    },
  },
  final_response: '추우시군요. 실내 온도를 24도로 올려둘게요.',
  latency_ms: 842,
  success: true,
  safety_blocked: false,
  fallback: false,
};

export const mockExecutionLogs: ExecutionLog[] = [
  {
    id: 1,
    user_input: '나 좀 추워',
    vehicle_state_snapshot: snapshot(),
    intent: 'CONTROL_CLIMATE',
    slots: { target_temperature: 24, action: 'increase' },
    tool_name: 'setClimate',
    tool_arguments: { temperature: 24, mode: 'heating' },
    tool_result: {
      success: true,
      message: 'Indoor temperature set to 24°C',
      updated_vehicle_state: { indoor_temperature: 24 },
    },
    final_response: '추우시군요. 실내 온도를 24도로 올려둘게요.',
    success: true,
    latency_ms: 842,
    created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
  },
  {
    id: 2,
    user_input: '집으로 안내해줘',
    vehicle_state_snapshot: snapshot(),
    intent: 'SET_NAVIGATION',
    slots: { destination: 'home' },
    tool_name: 'setNavigation',
    tool_arguments: { destination: 'home', route_type: 'fastest' },
    tool_result: { success: true, message: 'Navigation to home started' },
    final_response: '집으로 안내를 시작합니다. 예상 소요 시간은 35분입니다.',
    success: true,
    latency_ms: 1024,
    created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
  },
  {
    id: 3,
    user_input: '졸려',
    vehicle_state_snapshot: snapshot(),
    intent: 'FIND_NEARBY_PLACE',
    slots: { place_type: 'rest_area', urgency: 'high' },
    tool_name: 'findNearbyPlace',
    tool_arguments: { type: 'rest_area', radius_km: 10 },
    tool_result: {
      success: true,
      message: 'Found 2 rest areas within 10km',
      places: ['대전휴게소', '청주휴게소'],
    },
    final_response:
      '가까운 휴게소를 찾았습니다. 8km 앞 대전휴게소로 안내할까요?',
    success: true,
    latency_ms: 1180,
    created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
  },
  {
    id: 4,
    user_input: '운전 중인데 화면 설정 좀 복잡하게 바꿔줘',
    vehicle_state_snapshot: snapshot(),
    intent: 'CHANGE_VEHICLE_SETTING',
    slots: { setting: 'display', complexity: 'high' },
    tool_name: null,
    tool_arguments: null,
    tool_result: null,
    final_response:
      '운전 중에는 복잡한 화면 설정 변경을 할 수 없습니다. 안전을 위해 요청을 차단했습니다.',
    success: false,
    failure_reason: 'Safety block: complex UI changes not allowed while driving',
    latency_ms: 312,
    created_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
  },
  {
    id: 5,
    user_input: '아무 농담 해줘',
    vehicle_state_snapshot: snapshot(),
    intent: 'UNKNOWN',
    slots: {},
    tool_name: null,
    tool_arguments: null,
    tool_result: null,
    final_response:
      '죄송합니다. 차량 제어와 관련된 요청만 도와드릴 수 있어요. 내비게이션이나 에어컨 설정을 도와드릴까요?',
    success: false,
    failure_reason: 'Fallback: intent not recognized, no matching tool',
    latency_ms: 456,
    created_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
  },
  {
    id: 6,
    user_input: '배터리 상태 확인해줘',
    vehicle_state_snapshot: snapshot(),
    intent: 'CHECK_VEHICLE_STATUS',
    slots: { target: 'battery' },
    tool_name: 'getVehicleStatus',
    tool_arguments: { fields: ['battery_level'] },
    tool_result: { success: true, battery_level: 68 },
    final_response: '현재 배터리 잔량은 68%입니다.',
    success: true,
    latency_ms: 623,
    created_at: new Date(Date.now() - 90 * 60 * 1000).toISOString(),
  },
  {
    id: 7,
    user_input: '조용한 노래 틀어줘',
    vehicle_state_snapshot: snapshot(),
    intent: 'PLAY_MEDIA',
    slots: { genre: 'calm', volume: 'low' },
    tool_name: 'playMedia',
    tool_arguments: { genre: 'calm', volume: 30 },
    tool_result: { success: true, message: 'Playing calm playlist' },
    final_response: '조용한 음악을 재생합니다.',
    success: true,
    latency_ms: 789,
    created_at: new Date(Date.now() - 120 * 60 * 1000).toISOString(),
  },
  {
    id: 8,
    user_input: '창문 닫아줘',
    vehicle_state_snapshot: snapshot(),
    intent: 'CHANGE_VEHICLE_SETTING',
    slots: { target: 'window', action: 'close' },
    tool_name: 'setWindow',
    tool_arguments: { status: 'closed' },
    tool_result: {
      success: true,
      message: 'All windows closed',
      updated_vehicle_state: { window_status: 'closed' },
    },
    final_response: '모든 창문을 닫았습니다.',
    success: true,
    latency_ms: 534,
    created_at: new Date(Date.now() - 150 * 60 * 1000).toISOString(),
  },
];

export const mockEvaluationSummary: EvaluationSummary = {
  total_requests: 128,
  success_requests: 112,
  failed_requests: 16,
  tool_call_success_rate: 0.91,
  average_latency_ms: 876,
  safety_block_count: 3,
  fallback_count: 5,
};

export const mockIntentDistribution: DistributionItem[] = [
  { name: 'CONTROL_CLIMATE', count: 34 },
  { name: 'SET_NAVIGATION', count: 28 },
  { name: 'PLAY_MEDIA', count: 18 },
  { name: 'FIND_NEARBY_PLACE', count: 14 },
  { name: 'CHECK_VEHICLE_STATUS', count: 12 },
  { name: 'CHANGE_VEHICLE_SETTING', count: 10 },
  { name: 'UNKNOWN', count: 6 },
];

export const mockToolUsage: DistributionItem[] = [
  { name: 'setClimate', count: 34 },
  { name: 'setNavigation', count: 28 },
  { name: 'playMedia', count: 18 },
  { name: 'findNearbyPlace', count: 14 },
  { name: 'getVehicleStatus', count: 12 },
  { name: 'setWindow', count: 8 },
];

export function findMockLogById(id: number): ExecutionLog | undefined {
  return mockExecutionLogs.find((log) => log.id === id);
}

export const mockScenarios = [
  {
    id: 'climate-cold',
    name: 'Cold cabin comfort',
    description: 'User feels cold; agent controls climate.',
    user_input: '나 좀 추워',
    vehicle_state_overrides: { is_driving: true, speed: 72 },
    expected_intent: 'CONTROL_CLIMATE' as const,
    expected_tool: 'setClimate',
    expected_result: { success: true },
    tags: ['climate', 'success'],
  },
  {
    id: 'display-block',
    name: 'Block complex display change',
    description: 'Complex UI changes blocked while driving.',
    user_input: '운전 중인데 화면 설정 좀 복잡하게 바꿔줘',
    vehicle_state_overrides: { is_driving: true, speed: 72 },
    expected_intent: 'CHANGE_VEHICLE_SETTING' as const,
    expected_result: { safety_blocked: true, success: false },
    tags: ['safety', 'blocked'],
  },
  {
    id: 'fallback-unknown',
    name: 'Unknown intent fallback',
    description: 'Off-domain request triggers fallback.',
    user_input: '아무 농담 해줘',
    vehicle_state_overrides: {},
    expected_intent: 'UNKNOWN' as const,
    expected_result: { fallback: true, success: false },
    tags: ['fallback'],
  },
];

export const mockRunAllScenarios = {
  batch_id: 'mock-batch-001',
  summary: {
    total: 3,
    passed: 3,
    failed: 0,
    intent_accuracy: 1,
    tool_accuracy: 1,
    safety_accuracy: 1,
  },
  results: mockScenarios.map((scenario, index) => ({
    scenario_id: scenario.id,
    scenario_name: scenario.name,
    passed: true,
    passed_intent: true,
    passed_tool: scenario.expected_tool ? true : null,
    passed_result: true,
    passed_safety: scenario.tags.includes('safety') ? true : null,
    checks: { intent: true, result: true },
    agent_response: {
      ...mockAgentResponse,
      intent: scenario.expected_intent ?? 'UNKNOWN',
      success: scenario.expected_result?.success ?? false,
      safety_blocked: scenario.expected_result?.safety_blocked ?? false,
      fallback: scenario.expected_result?.fallback ?? false,
      requires_clarification:
        (scenario.expected_result as { requires_clarification?: boolean } | undefined)
          ?.requires_clarification ?? false,
      final_response: `Mock response for ${scenario.name}`,
      latency_ms: 120 + index * 15,
    },
  })),
};

