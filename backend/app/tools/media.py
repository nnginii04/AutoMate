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
        mood = slots.get("mood", slots.get("genre", "default"))
        volume_label = slots.get("volume", "medium")
        volume = 30 if volume_label == "low" else 60 if volume_label == "high" else 50
        return {
            "genre": slots.get("genre", mood),
            "mood": mood,
            "action": slots.get("action", "play"),
            "volume": volume,
        }

    def execute(self, arguments: PlayMediaArgs, vehicle_state: VehicleState) -> ToolResult:
        if arguments.action == "stop":
            return ToolResult(
                success=True,
                tool_name=self.name,
                message="음악 재생을 중지했습니다.",
                updated_vehicle_state={"media_status": "off"},
            )

        mood_label = {
            "calm": "잔잔한",
            "energetic": "신나는",
        }.get(arguments.mood or arguments.genre, "")
        prefix = f"{mood_label} " if mood_label else ""
        return ToolResult(
            success=True,
            tool_name=self.name,
            message=f"{prefix}음악을 재생합니다.",
            updated_vehicle_state={
                "media_status": "playing",
                "media_volume": arguments.volume,
            },
        )
