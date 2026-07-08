from __future__ import annotations

from typing import Any, Dict

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import SetNavigationArgs


class SetNavigationTool(VehicleTool[SetNavigationArgs]):
    name = "setNavigation"
    description = "Set navigation destination and start routing"
    argument_schema = SetNavigationArgs
    supported_intents = ("SET_NAVIGATION",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        destination = slots.get("destination", "custom")
        if destination == "work":
            destination = "company"
        return {
            "destination": destination,
            "route_type": slots.get("route_type", "fastest"),
        }

    def missing_clarification_fields(self, arguments: Dict[str, Any]) -> list[str]:
        destination = str(arguments.get("destination", "")).strip().lower()
        if not destination or destination in ("unknown", "custom", "unspecified"):
            return ["destination"]
        return []

    _DESTINATION_LABELS = {"home": "집", "company": "회사", "work": "회사"}

    def execute(self, arguments: SetNavigationArgs, vehicle_state: VehicleState) -> ToolResult:
        label = self._DESTINATION_LABELS.get(arguments.destination, arguments.destination)
        return ToolResult(
            success=True,
            tool_name=self.name,
            message=f"{label}까지 경로 안내를 시작합니다.",
        )
