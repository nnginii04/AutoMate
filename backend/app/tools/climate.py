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
        return {
            "temperature": slots.get("target_temperature", 24),
            "mode": slots.get("mode", "auto"),
        }

    def execute(self, arguments: SetClimateArgs, vehicle_state: VehicleState) -> ToolResult:
        ac_status = (
            "heating"
            if arguments.mode == "heating"
            else "cooling"
            if arguments.mode == "cooling"
            else arguments.mode
        )
        return ToolResult(
            success=True,
            tool_name=self.name,
            message=f"Indoor temperature set to {arguments.temperature}°C",
            updated_vehicle_state={
                "indoor_temperature": arguments.temperature,
                "air_conditioner_status": ac_status,
            },
        )
