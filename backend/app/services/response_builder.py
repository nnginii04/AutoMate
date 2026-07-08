"""Response templates for agent final messages."""

from __future__ import annotations

from app.schemas import AgentRunResponse, IntentType, ToolResult, VehicleState


def build_final_response(
    intent: IntentType,
    user_input: str,
    tool_result: ToolResult | None,
    vehicle_state: VehicleState,
) -> str:
    if intent == "CONTROL_CLIMATE":
        temp = (
            tool_result.updated_vehicle_state.get("indoor_temperature")
            if tool_result and tool_result.updated_vehicle_state
            else vehicle_state.indoor_temperature
        )
        return f"추우시군요. 실내 온도를 {temp}도로 올려둘게요." if "추" in user_input else f"실내 온도를 {temp}도로 설정했습니다."

    if intent == "SET_NAVIGATION":
        return "집으로 안내를 시작합니다. 예상 소요 시간은 35분입니다." if "집" in user_input else "안내를 시작합니다."

    if intent == "PLAY_MEDIA":
        return "조용한 음악을 재생합니다." if "조용" in user_input else "음악을 재생합니다."

    if intent == "MAKE_CALL":
        return "통화를 연결합니다. 핸즈프리 모드로 진행할게요."

    if intent == "FIND_NEARBY_PLACE":
        return "가까운 휴게소를 찾았습니다. 8km 앞 휴게소로 안내할까요?"

    if intent == "CHECK_VEHICLE_STATUS":
        if "배터리" in user_input:
            return f"현재 배터리 잔량은 {int(vehicle_state.battery_level)}%입니다."
        return "차량 상태를 확인했습니다."

    if intent == "CHANGE_VEHICLE_SETTING":
        if tool_result and tool_result.updated_vehicle_state:
            if "window_status" in tool_result.updated_vehicle_state:
                return "모든 창문을 닫았습니다." if tool_result.updated_vehicle_state["window_status"] == "closed" else "창문 상태를 변경했습니다."
        return "차량 설정을 변경했습니다."

    if intent == "READ_SCHEDULE":
        return "오늘 예정된 일정이 없습니다."

    return tool_result.message if tool_result else "요청을 처리했습니다."


def build_fallback_response() -> str:
    return (
        "죄송합니다. 차량 제어와 관련된 요청만 도와드릴 수 있어요. "
        "내비게이션이나 에어컨 설정을 도와드릴까요?"
    )


def build_clarification_response(decision) -> str:
    if decision.fallback_response:
        return decision.fallback_response
    return "요청을 이해하기 위해 추가 정보가 필요합니다."


def build_slot_clarification_response(tool_name: str, missing_fields: list[str]) -> str:
    if "destination" in missing_fields:
        return "어디로 안내해 드릴까요? 집, 회사, 또는 목적지를 말씀해 주세요."
    if "contact" in missing_fields:
        return "누구에게 전화를 연결해 드릴까요? 연락처 이름을 말씀해 주세요."
    return f"{tool_name} 실행에 필요한 정보가 부족합니다. ({', '.join(missing_fields)})"


def build_safety_block_response(decision) -> str:
    if decision.fallback_response:
        return decision.fallback_response
    reason = decision.reason or ""
    if "complex UI" in reason or "display" in reason.lower():
        return "운전 중에는 복잡한 화면 설정 변경을 할 수 없습니다. 안전을 위해 요청을 차단했습니다."
    return "안전을 위해 요청을 차단했습니다."
