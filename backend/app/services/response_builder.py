"""Response templates for agent final messages."""

from __future__ import annotations

from app.schemas import IntentType, ToolResult, VehicleState


def build_final_response(
    intent: IntentType,
    user_input: str,
    tool_result: ToolResult | None,
    vehicle_state: VehicleState,
) -> str:
    if tool_result and tool_result.message:
        return tool_result.message

    if intent == "CONTROL_CLIMATE":
        return "실내 공조를 조절했습니다."

    if intent == "SET_NAVIGATION":
        return "안내를 시작합니다."

    if intent == "PLAY_MEDIA":
        return "음악을 재생합니다."

    if intent == "MAKE_CALL":
        return "통화를 연결합니다. 핸즈프리 모드로 진행할게요."

    if intent == "FIND_NEARBY_PLACE":
        return "가까운 장소를 찾았습니다. 안내를 시작할까요?"

    if intent == "CHECK_VEHICLE_STATUS":
        if vehicle_state.weather.lower() in ("rainy", "rain") and vehicle_state.window_status == "open":
            return "현재 비가 오고 있어요. 창문이 열려 있으니 닫는 것을 추천드려요."
        return "차량 상태를 확인했습니다."

    if intent == "CHECK_ROAD_CONTEXT":
        return "도로 주행 정보를 확인했습니다."

    if intent == "CHANGE_VEHICLE_SETTING":
        return "차량 설정을 변경했습니다."

    if intent == "READ_SCHEDULE":
        return "오늘 예정된 일정이 없습니다."

    return "요청을 처리했습니다."


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
    return "안전을 위해 요청을 차단했습니다."
