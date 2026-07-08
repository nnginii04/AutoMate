"""Safety validation layer for in-vehicle agent actions."""

from __future__ import annotations

from typing import Literal, Optional

from app.schemas import IntentType, SafetyDecision, VehicleState

RiskLevel = Literal["none", "low", "medium", "high", "critical"]

_RISK_ORDER: dict[RiskLevel, int] = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

_SAFE_DRIVING_SETTINGS = frozenset(
    {"volume", "display_brightness", "wiper_mode", "wiper_status", "window_status", "media_status"}
)


class SafetyGuard:
    """Evaluates driving context, intent, and slots before tool execution."""

    COMPLEX_UI_KEYWORDS = ("복잡", "화면 설정", "디스플레이", "설정 바꿔", "설정 변경", "자세히")
    DANGEROUS_SETTING_TARGETS = frozenset(
        {"seat", "mirror", "steering", "infotainment", "hud", "door_lock"}
    )
    IMMEDIATE_SAFETY_INTENTS = frozenset(
        {"CONTROL_CLIMATE", "CHECK_VEHICLE_STATUS", "MAKE_CALL", "CHANGE_VEHICLE_SETTING"}
    )
    UNKNOWN_FALLBACK_RESPONSE = (
        "죄송합니다. 차량 제어와 관련된 요청만 도와드릴 수 있어요. "
        "내비게이션이나 에어컨 설정을 도와드릴까요?"
    )

    def evaluate(
        self,
        user_input: str,
        intent: IntentType,
        vehicle_state: VehicleState,
        slots: dict,
        capability=None,
    ) -> SafetyDecision:
        if intent == "UNKNOWN":
            return self._unknown_fallback()

        risk_level = self._assess_context_risk(vehicle_state)
        context_reason = self._context_risk_reason(vehicle_state)

        drowsy_decision = self._check_drowsy_priority(intent, vehicle_state, slots, risk_level)
        if drowsy_decision:
            return drowsy_decision

        # Capability-driven path: use the catalog's allowed_while_driving/risk_level.
        # Slot-based clarification is handled upstream (AgentService) from the
        # capability's required_slots, so we do not re-run the legacy check here.
        if capability is not None:
            capability_block = self._check_capability_driving_block(vehicle_state, capability)
            if capability_block:
                return capability_block
        else:
            clarification = self._check_clarification_needed(intent, slots)
            if clarification:
                return clarification

            if vehicle_state.is_driving:
                block = self._check_driving_blocks(user_input, intent, vehicle_state, slots)
                if block:
                    return block

        if self._is_context_window_risk(vehicle_state) and self._is_window_open_request(intent, slots):
            return SafetyDecision(
                allowed=False,
                blocked=True,
                reason="Safety block: opening windows is unsafe in rainy weather while driving",
                fallback_response=(
                    "비가 오는 날 운전 중에는 창문을 여는 것이 위험합니다. "
                    "창문을 닫거나 에어컨으로 환기하는 것을 권장합니다."
                ),
                risk_level=self._max_risk(risk_level, "high"),
            )

        if capability is not None:
            risk_level = self._max_risk(risk_level, capability.risk_level or "none")

        allowed = SafetyDecision(
            allowed=True,
            blocked=False,
            requires_clarification=False,
            risk_level=risk_level,
            reason=context_reason,
        )
        return allowed

    def _check_capability_driving_block(
        self, vehicle_state: VehicleState, capability
    ) -> Optional[SafetyDecision]:
        if not vehicle_state.is_driving or capability.allowed_while_driving:
            return None
        return SafetyDecision(
            allowed=False,
            blocked=True,
            requires_clarification=False,
            reason=(
                f"Safety block: capability '{capability.capability_id}' "
                "is not allowed while driving"
            ),
            fallback_response=(
                capability.blocked_response
                or "안전을 위해 정차 후 다시 시도해 주세요."
            ),
            risk_level=capability.risk_level or "high",
        )

    def _unknown_fallback(self) -> SafetyDecision:
        return SafetyDecision(
            allowed=False,
            blocked=False,
            requires_clarification=False,
            reason="Fallback: intent not recognized, no matching tool",
            fallback_response=self.UNKNOWN_FALLBACK_RESPONSE,
            risk_level="none",
        )

    def _assess_context_risk(self, vehicle_state: VehicleState) -> RiskLevel:
        risk: RiskLevel = "none"

        if self._is_context_window_risk(vehicle_state):
            risk = self._max_risk(risk, "medium")

        if vehicle_state.driver_status == "drowsy":
            risk = self._max_risk(risk, "high")

        if vehicle_state.is_driving and vehicle_state.speed > 100:
            risk = self._max_risk(risk, "low")

        return risk

    @staticmethod
    def _is_context_window_risk(vehicle_state: VehicleState) -> bool:
        weather = vehicle_state.weather.lower()
        return weather in ("rainy", "rain", "storm") and vehicle_state.window_status == "open"

    @staticmethod
    def _context_risk_reason(vehicle_state: VehicleState) -> Optional[str]:
        if SafetyGuard._is_context_window_risk(vehicle_state):
            return (
                "Context risk: rainy weather with windows open. "
                "Consider closing windows for safety."
            )
        return None

    def _check_drowsy_priority(
        self,
        intent: IntentType,
        vehicle_state: VehicleState,
        slots: dict,
        risk_level: RiskLevel,
    ) -> Optional[SafetyDecision]:
        if vehicle_state.driver_status != "drowsy":
            return None

        if intent == "FIND_NEARBY_PLACE":
            return SafetyDecision(
                allowed=True,
                blocked=False,
                requires_clarification=False,
                reason="Drowsy driver detected; prioritizing rest area guidance",
                risk_level=self._max_risk(risk_level, "high"),
            )

        if intent == "CHANGE_VEHICLE_SETTING" and self._is_safe_driving_setting(slots):
            return SafetyDecision(
                allowed=True,
                blocked=False,
                requires_clarification=False,
                reason="Drowsy driver detected; allowing immediate safety action",
                risk_level=self._max_risk(risk_level, "high"),
            )

        if intent in {"CONTROL_CLIMATE", "CHECK_VEHICLE_STATUS", "MAKE_CALL"}:
            return SafetyDecision(
                allowed=True,
                blocked=False,
                requires_clarification=False,
                reason="Drowsy driver detected; allowing comfort/safety check with rest area reminder",
                fallback_response="졸음이 감지되었습니다. 처리 후 휴게소 안내를 권장합니다.",
                risk_level=self._max_risk(risk_level, "high"),
            )

        if intent in {"PLAY_MEDIA", "SET_NAVIGATION", "READ_SCHEDULE"}:
            return SafetyDecision(
                allowed=False,
                blocked=False,
                requires_clarification=True,
                reason="Drowsy driver detected; rest area guidance should be prioritized",
                fallback_response=(
                    "졸음 상태가 감지되었습니다. 안전을 위해 가까운 휴게소로 안내해 드릴까요? "
                    "휴식 후 다른 요청을 도와드리겠습니다."
                ),
                risk_level=self._max_risk(risk_level, "high"),
            )

        return None

    def _check_clarification_needed(self, intent: IntentType, slots: dict) -> Optional[SafetyDecision]:
        if intent == "SET_NAVIGATION":
            destination = slots.get("destination")
            if not destination or destination in ("custom", "unknown"):
                return SafetyDecision(
                    allowed=False,
                    blocked=False,
                    requires_clarification=True,
                    reason="Clarification required: navigation destination is unclear",
                    fallback_response="어디로 안내해 드릴까요? 집, 회사, 또는 목적지를 말씀해 주세요.",
                    risk_level="none",
                )

        if intent == "MAKE_CALL":
            contact = slots.get("contact")
            if not contact or contact in ("unknown", "custom"):
                return SafetyDecision(
                    allowed=False,
                    blocked=False,
                    requires_clarification=True,
                    reason="Clarification required: call contact is unclear",
                    fallback_response="누구에게 전화를 연결해 드릴까요? 연락처 이름을 말씀해 주세요.",
                    risk_level="none",
                )

        return None

    def _check_driving_blocks(
        self,
        user_input: str,
        intent: IntentType,
        vehicle_state: VehicleState,
        slots: dict,
    ) -> Optional[SafetyDecision]:
        text = user_input.lower()

        if intent == "MAKE_CALL":
            return None

        if intent == "CHANGE_VEHICLE_SETTING":
            setting = slots.get("setting", slots.get("target", ""))
            action = slots.get("action", "")
            value = slots.get("value", "")
            complexity = slots.get("complexity", "")

            if self._is_safe_driving_setting(slots):
                return None

            if setting == "display" and complexity == "high":
                return self._blocked_complex_ui()

            if any(kw in text for kw in self.COMPLEX_UI_KEYWORDS):
                return self._blocked_complex_ui()

            if setting in self.DANGEROUS_SETTING_TARGETS:
                return self._blocked_dangerous_control(setting)

            if setting in ("window", "window_status") and (action == "open" or value == "open"):
                return self._blocked_dangerous_control("window_open")

        return None

    @staticmethod
    def _is_safe_driving_setting(slots: dict) -> bool:
        setting = slots.get("setting", slots.get("target", ""))
        value = slots.get("value", "")
        action = slots.get("action", "")

        if setting in _SAFE_DRIVING_SETTINGS:
            if setting in ("window", "window_status"):
                return value == "closed" or action == "close"
            return True

        if setting in ("wiper", "wiper_mode", "wiper_status"):
            return True

        if setting == "display_brightness":
            return True

        return False

    @staticmethod
    def _is_safe_window_action(slots: dict) -> bool:
        return SafetyGuard._is_safe_driving_setting(slots) and slots.get("setting") in {
            "window",
            "window_status",
            None,
        }

    @staticmethod
    def _is_window_open_request(intent: IntentType, slots: dict) -> bool:
        if intent != "CHANGE_VEHICLE_SETTING":
            return False
        setting = slots.get("setting", slots.get("target", ""))
        return setting in ("window", "window_status") and (
            slots.get("action") == "open" or slots.get("value") == "open"
        )

    def _blocked_complex_ui(self, reason: str | None = None) -> SafetyDecision:
        message = reason or "Safety block: complex UI changes not allowed while driving"
        return SafetyDecision(
            allowed=False,
            blocked=True,
            requires_clarification=False,
            reason=message,
            fallback_response="안전을 위해 정차 후 설정 변경을 도와드릴게요.",
            risk_level="high",
        )

    def _blocked_dangerous_control(self, target: str) -> SafetyDecision:
        labels = {
            "window_open": "창문 열기",
            "display": "디스플레이 설정",
            "seat": "시트 설정",
            "mirror": "미러 설정",
            "steering": "스티어링 설정",
            "infotainment": "인포테인먼트 설정",
            "hud": "HUD 설정",
            "door_lock": "문 잠금",
        }
        label = labels.get(target, "차량 설정 변경")
        return SafetyDecision(
            allowed=False,
            blocked=True,
            requires_clarification=False,
            reason=f"Safety block: dangerous control '{target}' not allowed while driving",
            fallback_response=f"운전 중에는 {label}과 같은 위험한 제어를 수행할 수 없습니다. 정차 후 다시 요청해 주세요.",
            risk_level="critical",
        )

    @staticmethod
    def _max_risk(current: RiskLevel, candidate: RiskLevel) -> RiskLevel:
        if _RISK_ORDER[candidate] > _RISK_ORDER[current]:
            return candidate
        return current
