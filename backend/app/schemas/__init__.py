from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

IntentType = Literal[
    "CONTROL_CLIMATE",
    "SET_NAVIGATION",
    "PLAY_MEDIA",
    "MAKE_CALL",
    "READ_SCHEDULE",
    "CHANGE_VEHICLE_SETTING",
    "CHECK_VEHICLE_STATUS",
    "CHECK_ROAD_CONTEXT",
    "FIND_NEARBY_PLACE",
    "UNKNOWN",
]


class VehicleState(BaseModel):
    vehicle_id: Optional[str] = "VH-001"
    speed: float = 0
    indoor_temperature: float = 22
    outdoor_temperature: float = 20
    battery_level: float = 100
    fuel_level: float = 100
    driver_status: str = "normal"
    driving_mode: str = "comfort"
    time: str = "12:00"
    location: str = "Unknown"
    passenger_count: int = 1
    is_driving: bool = False
    weather: str = "sunny"
    window_status: str = "closed"
    air_conditioner_status: str = "off"
    media_status: str = "off"
    media_volume: float = 50
    display_brightness: str = "medium"
    road_name: Optional[str] = "대전 유성대로"
    road_type: str = "urban"
    speed_limit: Optional[float] = 60
    is_school_zone: bool = False
    navigation_active: bool = True

    def merge(self, partial: Dict[str, Any]) -> VehicleState:
        nullable_keys = {"road_name", "speed_limit", "vehicle_id"}
        return self.model_copy(
            update={
                k: v
                for k, v in partial.items()
                if v is not None or k in nullable_keys
            }
        )

    def to_snapshot(self) -> Dict[str, Any]:
        return self.model_dump()


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    success: bool
    tool_name: Optional[str] = None
    message: str
    updated_vehicle_state: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None


class AgentRunRequest(BaseModel):
    user_input: str
    vehicle_state: Dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    intent: IntentType
    slots: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    tool_call: Optional[ToolCall] = None
    tool_result: Optional[ToolResult] = None
    final_response: str
    latency_ms: int
    success: bool
    failure_reason: Optional[str] = None
    safety_blocked: bool = False
    fallback: bool = False
    requires_clarification: bool = False
    safety_decision: Optional["SafetyDecision"] = None
    nlu_source: Literal["llm", "rule_based"] = "rule_based"


class ExecutionLogResponse(BaseModel):
    id: int
    user_input: str
    vehicle_state_snapshot: Dict[str, Any]
    intent: str
    slots: Dict[str, Any]
    tool_name: Optional[str] = None
    tool_arguments: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    final_response: str
    success: bool
    failure_reason: Optional[str] = None
    latency_ms: int
    created_at: str

    model_config = {"from_attributes": True}


class EvaluationSummary(BaseModel):
    total_requests: int
    success_requests: int
    failed_requests: int
    tool_call_success_rate: float
    average_latency_ms: float
    safety_block_count: int
    fallback_count: int


class DistributionItem(BaseModel):
    name: str
    count: int


class NLUResult(BaseModel):
    intent: IntentType
    slots: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    tool_call: Optional[ToolCall] = None
    source: Literal["llm", "rule_based"] = "rule_based"
    parse_error: Optional[str] = None
    capability_id: Optional[str] = None


class SafetyDecision(BaseModel):
    allowed: bool
    blocked: bool = False
    requires_clarification: bool = False
    reason: Optional[str] = None
    fallback_response: Optional[str] = None
    risk_level: Literal["none", "low", "medium", "high", "critical"] = "none"


# Backward-compatible alias
SafetyCheckResult = SafetyDecision


class ExpectedScenarioResult(BaseModel):
    success: Optional[bool] = None
    safety_blocked: Optional[bool] = None
    fallback: Optional[bool] = None
    requires_clarification: Optional[bool] = None


class TestScenario(BaseModel):
    id: str
    name: str
    description: str
    user_input: str
    vehicle_state_overrides: Dict[str, Any] = Field(default_factory=dict)
    expected_intent: Optional[IntentType] = None
    expected_tool: Optional[str] = None
    expected_result: Optional[ExpectedScenarioResult] = None
    tags: List[str] = Field(default_factory=list)


class TestScenarioRunRequest(BaseModel):
    vehicle_state_overrides: Dict[str, Any] = Field(default_factory=dict)


class TestScenarioRunResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    agent_response: AgentRunResponse
    passed: bool
    passed_intent: Optional[bool] = None
    passed_tool: Optional[bool] = None
    passed_result: Optional[bool] = None
    passed_safety: Optional[bool] = None
    checks: Dict[str, bool] = Field(default_factory=dict)
    run_log_id: Optional[int] = None
    passed_intent_check: Optional[bool] = None


class ScenarioAccuracySummary(BaseModel):
    total: int
    passed: int
    failed: int
    intent_accuracy: float
    tool_accuracy: float
    safety_accuracy: float


class RunAllScenariosResponse(BaseModel):
    batch_id: str
    summary: ScenarioAccuracySummary
    results: List[TestScenarioRunResponse]
