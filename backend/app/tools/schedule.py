from __future__ import annotations

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import ReadScheduleArgs


class ReadScheduleTool(VehicleTool[ReadScheduleArgs]):
    name = "readSchedule"
    description = "Read driver calendar and schedule events"
    argument_schema = ReadScheduleArgs
    supported_intents = ("READ_SCHEDULE",)

    def execute(self, arguments: ReadScheduleArgs, vehicle_state: VehicleState) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            message=f"No upcoming events for {arguments.range}",
        )
