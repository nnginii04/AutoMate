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


class SafetyGuard:
    """Evaluates driving context, intent, and slots before tool execution."""

    COMPLEX_UI_KEYWORDS = ("복잡", "화면 설정", "디스플레이", "설정 바꿔", "설정 변경", "자세히")
    DANGEROUS_SETTING_TARGETS = frozenset(
        {"display", "seat", "mirror", "steering", "infotainment", "hud"}
    )
    IMMEDIATE_SAFETY_INTENTS = frozenset({"CONTROL_CLIMATE", "CHECK_VEHICLE_STATUS"})
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
    ) -> SafetyDecision:
        if intent == "UNKNOWN":
            return self._unknown_fallback()

        risk_level = self._assess_context_risk(vehicle_state)
        context_reason = self._context_risk_reason(vehicle_state)

        drowsy_decision = self._check_drowsy_priority(intent, vehicle_state, slots, risk_level)
        if drowsy_decision:
            return drowsy_decision

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

        allowed = SafetyDecision(
            allowed=True,
            blocked=False,
            requires_clarification=False,
            risk_level=risk_level,
            reason=context_reason,
        )
        if context_reason and risk_level in ("medium", "high", "critical"):
            allowed.fallback_response = context_reason
        return allowed

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

        if intent == "CHANGE_VEHICLE_SETTING" and self._is_safe_window_action(slots):
            return SafetyDecision(
                allowed=True,
                blocked=False,
                requires_clarification=False,
                reason="Drowsy driver detected; allowing immediate safety action",
                risk_level=self._max_risk(risk_level, "high"),
            )

        if intent in self.IMMEDIATE_SAFETY_INTENTS:
            return SafetyDecision(
                allowed=True,
                blocked=False,
                requires_clarification=False,
                reason="Drowsy driver detected; allowing comfort/safety check with rest area reminder",
                fallback_response="졸음이 감지되었습니다. 처리 후 휴게소 안내를 권장합니다.",
                risk_level=self._max_risk(risk_level, "high"),
            )

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

        if intent == "CHANGE_VEHICLE_SETTING":
            target = slots.get("target") or slots.get("setting", "")
            action = slots.get("action", "")
            complexity = slots.get("complexity", "")

            if target == "display" or complexity == "high":
                return self._blocked_complex_ui()

            if any(kw in text for kw in self.COMPLEX_UI_KEYWORDS):
                return self._blocked_complex_ui()

            if target in self.DANGEROUS_SETTING_TARGETS:
                return self._blocked_dangerous_control(target)

            if target == "window" and action == "open":
                return self._blocked_dangerous_control("window_open")

            if vehicle_state.speed > 100 and target == "display":
                return self._blocked_complex_ui("Safety block: display changes not allowed at high speed")

        return None

    @staticmethod
    def _is_safe_window_action(slots: dict) -> bool:
        target = slots.get("target") or slots.get("setting", "")
        action = slots.get("action", "")
        return target == "window" and action == "close"

    @staticmethod
    def _is_window_open_request(intent: IntentType, slots: dict) -> bool:
        if intent != "CHANGE_VEHICLE_SETTING":
            return False
        target = slots.get("target") or slots.get("setting", "")
        return target == "window" and slots.get("action") == "open"

    def _blocked_complex_ui(self, reason: str | None = None) -> SafetyDecision:
        message = reason or "Safety block: complex UI changes not allowed while driving"
        return SafetyDecision(
            allowed=False,
            blocked=True,
            requires_clarification=False,
            reason=message,
            fallback_response="운전 중에는 복잡한 화면 설정 변경을 할 수 없습니다. 안전을 위해 요청을 차단했습니다.",
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
