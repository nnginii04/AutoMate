from __future__ import annotations

from typing import Any, Dict

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import ChangeVehicleSettingArgs


class ChangeVehicleSettingTool(VehicleTool[ChangeVehicleSettingArgs]):
    name = "changeVehicleSetting"
    description = "Change vehicle settings such as windows, wipers, and display"
    argument_schema = ChangeVehicleSettingArgs
    supported_intents = ("CHANGE_VEHICLE_SETTING",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        target = slots.get("target", slots.get("setting", "window"))
        if target == "wiper":
            return {"setting": "wiper", "action": slots.get("action", "auto")}
        if slots.get("setting") == "display":
            return {
                "setting": "display",
                "value": slots.get("complexity", "normal"),
            }
        action = slots.get("action", "close")
        status = "closed" if action == "close" else "open" if action == "open" else "partial"
        return {"setting": "window", "status": status, "action": action}

    def execute(
        self,
        arguments: ChangeVehicleSettingArgs,
        vehicle_state: VehicleState,
    ) -> ToolResult:
        if arguments.setting == "wiper":
            return ToolResult(
                success=True,
                tool_name=self.name,
                message="Wiper set to automatic mode",
            )

        if arguments.setting == "display":
            return ToolResult(
                success=True,
                tool_name=self.name,
                message=f"Display setting updated to {arguments.value or 'default'}",
            )

        status = arguments.status or "closed"
        return ToolResult(
            success=True,
            tool_name=self.name,
            message=f"Window status set to {status}",
            updated_vehicle_state={"window_status": status},
        )
