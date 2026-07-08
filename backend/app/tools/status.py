from __future__ import annotations

from typing import Any, Dict, List

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import CheckVehicleStatusArgs


class CheckVehicleStatusTool(VehicleTool[CheckVehicleStatusArgs]):
    name = "checkVehicleStatus"
    description = "Read vehicle status metrics such as battery and fuel"
    argument_schema = CheckVehicleStatusArgs
    supported_intents = ("CHECK_VEHICLE_STATUS",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        target = slots.get("target", "general")
        fields: List[str]
        if target == "battery":
            fields = ["battery_level"]
        elif target == "fuel":
            fields = ["fuel_level"]
        else:
            fields = ["battery_level", "fuel_level"]
        return {"fields": fields}

    def execute(self, arguments: CheckVehicleStatusArgs, vehicle_state: VehicleState) -> ToolResult:
        readings = {
            field: getattr(vehicle_state, field)
            for field in arguments.fields
            if hasattr(vehicle_state, field)
        }
        if not readings:
            return ToolResult(
                success=False,
                tool_name=self.name,
                message="No valid status fields requested",
            )
        return ToolResult(
            success=True,
            tool_name=self.name,
            message="Vehicle status retrieved",
        )
