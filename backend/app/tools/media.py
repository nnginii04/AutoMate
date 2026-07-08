from __future__ import annotations

from typing import Any, Dict

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import PlayMediaArgs


class PlayMediaTool(VehicleTool[PlayMediaArgs]):
    name = "playMedia"
    description = "Play in-vehicle media content"
    argument_schema = PlayMediaArgs
    supported_intents = ("PLAY_MEDIA",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        volume = 30 if slots.get("volume") == "low" else 50
        return {"genre": slots.get("genre", "default"), "volume": volume}

    def execute(self, arguments: PlayMediaArgs, vehicle_state: VehicleState) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            message=f"Playing {arguments.genre} playlist at volume {arguments.volume}",
            updated_vehicle_state={"media_status": "playing"},
        )
