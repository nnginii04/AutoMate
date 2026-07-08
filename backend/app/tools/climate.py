from __future__ import annotations

from typing import Any, Dict

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import SetClimateArgs


class SetClimateTool(VehicleTool[SetClimateArgs]):
    name = "setClimate"
    description = "Adjust cabin climate and indoor temperature"
    argument_schema = SetClimateArgs
    supported_intents = ("CONTROL_CLIMATE",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        mode = slots.get("mode", "auto")
        temperature = slots.get("temperature", slots.get("target_temperature", 24))
        return {
            "temperature": temperature,
            "mode": mode,
            "close_window": slots.get("close_window", False),
        }

    def execute(self, arguments: SetClimateArgs, vehicle_state: VehicleState) -> ToolResult:
        updates: Dict[str, Any] = {}
        mode = arguments.mode

        if mode == "heating":
            updates["air_conditioner_status"] = "heating"
            updates["indoor_temperature"] = arguments.temperature
            message = f"실내 온도를 {int(arguments.temperature)}도로 올리고 난방을 켰습니다."
        elif mode == "cooling":
            updates["air_conditioner_status"] = "cooling"
            updates["indoor_temperature"] = arguments.temperature
            message = f"실내 온도를 {int(arguments.temperature)}도로 낮추고 냉방을 켰습니다."
        elif mode == "fresh_air":
            updates["air_conditioner_status"] = "fresh_air"
            message = "환기 모드로 전환해 실내 공기를 바꿉니다."
        elif mode == "recirculation":
            updates["air_conditioner_status"] = "recirculation"
            message = "외부 냄새 유입을 줄이기 위해 내기 순환 모드로 전환합니다."
        elif mode == "defrost":
            updates["air_conditioner_status"] = "defrost"
            message = "앞유리 성에 제거를 시작합니다."
        else:
            updates["air_conditioner_status"] = mode
            updates["indoor_temperature"] = arguments.temperature
            message = f"실내 온도를 {int(arguments.temperature)}도로 설정했습니다."

        if arguments.close_window or (
            mode == "recirculation" and vehicle_state.window_status == "open"
        ):
            updates["window_status"] = "closed"
            message += " 창문도 닫았습니다."

        return ToolResult(
            success=True,
            tool_name=self.name,
            message=message,
            updated_vehicle_state=updates,
        )
