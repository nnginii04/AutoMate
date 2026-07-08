from __future__ import annotations

from typing import Any, Dict

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import MakeCallArgs


class MakeCallTool(VehicleTool[MakeCallArgs]):
    name = "makeCall"
    description = "Initiate a hands-free phone call"
    argument_schema = MakeCallArgs
    supported_intents = ("MAKE_CALL",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        return {
            "contact": slots.get("contact", "unknown"),
            "hands_free": True,
        }

    def missing_clarification_fields(self, arguments: Dict[str, Any]) -> list[str]:
        contact = str(arguments.get("contact", "")).strip().lower()
        if not contact or contact in ("unknown", "custom", "unspecified"):
            return ["contact"]
        return []

    def execute(self, arguments: MakeCallArgs, vehicle_state: VehicleState) -> ToolResult:
        mode = "hands-free" if arguments.hands_free else "standard"
        return ToolResult(
            success=True,
            tool_name=self.name,
            message=f"Calling {arguments.contact} ({mode})",
            updated_vehicle_state={"media_status": "paused"},
        )
