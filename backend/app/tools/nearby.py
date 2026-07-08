from __future__ import annotations

from typing import Any, Dict

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import FindNearbyPlaceArgs


class FindNearbyPlaceTool(VehicleTool[FindNearbyPlaceArgs]):
    name = "findNearbyPlace"
    description = "Find nearby points of interest such as rest areas"
    argument_schema = FindNearbyPlaceArgs
    supported_intents = ("FIND_NEARBY_PLACE",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        return {
            "place_type": slots.get("place_type", "rest_area"),
            "radius_km": slots.get("radius_km", 10),
        }

    def execute(self, arguments: FindNearbyPlaceArgs, vehicle_state: VehicleState) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            message=(
                f"Found nearby {arguments.place_type} "
                f"within {arguments.radius_km}km"
            ),
        )
