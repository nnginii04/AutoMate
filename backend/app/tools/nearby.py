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

    _PLACE_LABELS = {
        "rest_area": "휴게소",
        "gas_station": "주유소",
        "charging_station": "충전소",
        "cafe": "카페",
    }

    def execute(self, arguments: FindNearbyPlaceArgs, vehicle_state: VehicleState) -> ToolResult:
        label = self._PLACE_LABELS.get(arguments.place_type, arguments.place_type)
        return ToolResult(
            success=True,
            tool_name=self.name,
            message=f"{int(arguments.radius_km)}km 이내 가까운 {label}를 찾았습니다. 안내를 시작할까요?",
        )
