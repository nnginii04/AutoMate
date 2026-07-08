from __future__ import annotations

from typing import Any, Dict

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import ChangeVehicleSettingArgs


class ChangeVehicleSettingTool(VehicleTool[ChangeVehicleSettingArgs]):
    name = "changeVehicleSetting"
    description = "Change vehicle settings such as windows, wipers, display, and volume"
    argument_schema = ChangeVehicleSettingArgs
    supported_intents = ("CHANGE_VEHICLE_SETTING",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        if slots.get("setting"):
            return {
                "setting": slots["setting"],
                "value": slots.get("value"),
                "action": slots.get("action"),
                "status": slots.get("status"),
            }

        target = slots.get("target", "window")
        if target == "wiper":
            return {"setting": "wiper_mode", "value": slots.get("action", "auto")}
        if slots.get("setting") == "display" or target == "display":
            return {
                "setting": "display",
                "value": slots.get("complexity", slots.get("value", "normal")),
            }

        action = slots.get("action", "close")
        status = "closed" if action == "close" else "open" if action == "open" else "partial"
        return {"setting": "window_status", "value": status, "action": action, "status": status}

    def execute(
        self,
        arguments: ChangeVehicleSettingArgs,
        vehicle_state: VehicleState,
    ) -> ToolResult:
        setting = arguments.setting
        value = arguments.value or arguments.status

        if setting in ("window", "window_status"):
            status = value or arguments.status or "closed"
            return ToolResult(
                success=True,
                tool_name=self.name,
                message="모든 창문을 닫았습니다." if status == "closed" else "창문을 열었습니다.",
                updated_vehicle_state={"window_status": status},
            )

        if setting in ("wiper", "wiper_mode"):
            return ToolResult(
                success=True,
                tool_name=self.name,
                message="와이퍼를 자동 모드로 설정했습니다.",
            )

        if setting == "wiper_status":
            return ToolResult(
                success=True,
                tool_name=self.name,
                message="와이퍼를 작동했습니다.",
            )

        if setting == "display_brightness":
            return ToolResult(
                success=True,
                tool_name=self.name,
                message="화면 밝기를 낮춰 눈부심을 줄였습니다.",
                updated_vehicle_state={"display_brightness": value or "low"},
            )

        if setting == "volume":
            current = vehicle_state.media_volume
            if value == "down":
                new_volume = max(0, current - 15)
                message = "미디어 볼륨을 낮출게요."
            else:
                new_volume = min(100, current + 15)
                message = "미디어 볼륨을 높일게요."
            return ToolResult(
                success=True,
                tool_name=self.name,
                message=message,
                updated_vehicle_state={"media_volume": new_volume},
            )

        if setting == "door_lock":
            return ToolResult(
                success=True,
                tool_name=self.name,
                message="차량 문을 잠갔습니다.",
            )

        if setting == "media_status":
            return ToolResult(
                success=True,
                tool_name=self.name,
                message="음악 재생을 중지했습니다.",
                updated_vehicle_state={"media_status": "off"},
            )

        if setting == "display":
            return ToolResult(
                success=True,
                tool_name=self.name,
                message=f"디스플레이 설정을 {value or '기본'}으로 변경했습니다.",
            )

        return ToolResult(
            success=True,
            tool_name=self.name,
            message="차량 설정을 변경했습니다.",
        )
