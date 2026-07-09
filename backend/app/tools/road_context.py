from __future__ import annotations

from typing import Any, Dict, Optional

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import CheckRoadContextArgs

_ROAD_TYPE_LABELS = {
    "highway": "고속도로",
    "urban": "시내 도로",
    "local": "지방 도로",
    "school_zone": "어린이 보호구역",
}


class CheckRoadContextTool(VehicleTool[CheckRoadContextArgs]):
    name = "checkRoadContext"
    description = "Check current road context such as speed limit, road name, and school zone"
    argument_schema = CheckRoadContextArgs
    supported_intents = ("CHECK_ROAD_CONTEXT",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        return {"target": slots.get("target", "speed_limit")}

    def execute(self, arguments: CheckRoadContextArgs, vehicle_state: VehicleState) -> ToolResult:
        target = arguments.target
        data = self._build_context_data(vehicle_state)

        if target in ("speed_limit", "speeding_status", "overall"):
            if vehicle_state.speed_limit is None:
                return ToolResult(
                    success=False,
                    tool_name=self.name,
                    message=(
                        "현재 도로의 제한속도 정보를 확인할 수 없어요. "
                        "도로 정보가 연결되면 제한속도와 과속 여부를 안내할 수 있습니다."
                    ),
                    data=data,
                )
            message = self._message_speed_context(vehicle_state, data, target)
            return ToolResult(success=True, tool_name=self.name, message=message, data=data)

        if target == "road_name":
            if not vehicle_state.road_name:
                return ToolResult(
                    success=False,
                    tool_name=self.name,
                    message="현재 주행 중인 도로 이름을 확인할 수 없습니다.",
                    data=data,
                )
            return ToolResult(
                success=True,
                tool_name=self.name,
                message=f"현재 주행 중인 도로는 {vehicle_state.road_name}입니다.",
                data=data,
            )

        if target == "road_type":
            label = _ROAD_TYPE_LABELS.get(vehicle_state.road_type, vehicle_state.road_type)
            return ToolResult(
                success=True,
                tool_name=self.name,
                message=f"현재 도로 유형은 {label}입니다.",
                data=data,
            )

        if target == "school_zone":
            return ToolResult(
                success=True,
                tool_name=self.name,
                message=self._message_school_zone(vehicle_state, data),
                data=data,
            )

        return ToolResult(
            success=False,
            tool_name=self.name,
            message="도로 정보를 확인할 수 없습니다.",
            data=data,
        )

    @staticmethod
    def _build_context_data(vehicle_state: VehicleState) -> Dict[str, Any]:
        speed = int(vehicle_state.speed)
        speed_limit = (
            int(vehicle_state.speed_limit) if vehicle_state.speed_limit is not None else None
        )
        is_speeding = (
            speed_limit is not None and speed > speed_limit
        )
        speed_over = max(0, speed - speed_limit) if speed_limit is not None and is_speeding else 0
        return {
            "road_name": vehicle_state.road_name,
            "road_type": vehicle_state.road_type,
            "speed": speed,
            "speed_limit": speed_limit,
            "is_speeding": is_speeding,
            "speed_over": speed_over,
            "is_school_zone": vehicle_state.is_school_zone,
            "navigation_active": vehicle_state.navigation_active,
        }

    @staticmethod
    def _road_prefix(road_name: Optional[str]) -> str:
        if road_name:
            return f"현재 {road_name}의 "
        return "현재 도로의 "

    def _message_speed_context(
        self,
        vehicle_state: VehicleState,
        data: Dict[str, Any],
        target: str,
    ) -> str:
        prefix = self._road_prefix(vehicle_state.road_name)
        speed = data["speed"]
        speed_limit = data["speed_limit"]
        is_speeding = data["is_speeding"]
        speed_over = data["speed_over"]

        if target == "speeding_status" or target == "overall":
            if is_speeding:
                return (
                    f"현재 제한속도보다 {speed_over}km/h 빠르게 주행 중입니다. "
                    "안전을 위해 속도를 줄여주세요."
                )
            return (
                f"현재 제한속도는 {speed_limit}km/h이고, 주행 속도는 {speed}km/h입니다. "
                "제한속도 이내로 주행 중입니다."
            )

        # speed_limit target
        if is_speeding:
            return (
                f"{prefix}제한속도는 {speed_limit}km/h예요. "
                f"지금은 {speed}km/h로 주행 중이라 제한속도를 {speed_over}km/h 초과하고 있어요. "
                "안전을 위해 속도를 조금 줄여주세요."
            )
        return (
            f"{prefix}제한속도는 {speed_limit}km/h입니다. "
            f"현재 주행 속도는 {speed}km/h입니다."
        )

    @staticmethod
    def _message_school_zone(vehicle_state: VehicleState, data: Dict[str, Any]) -> str:
        if vehicle_state.is_school_zone:
            speed = data["speed"]
            speed_limit = data.get("speed_limit")
            if speed_limit is not None and speed > speed_limit:
                return (
                    "현재 어린이 보호구역으로 설정되어 있어요. "
                    f"제한속도는 {speed_limit}km/h이고, 현재 속도는 {speed}km/h라 "
                    "속도를 줄이는 것이 좋습니다."
                )
            if speed_limit is not None:
                return (
                    "현재 어린이 보호구역으로 설정되어 있어요. "
                    f"제한속도는 {speed_limit}km/h이고, 현재 속도는 {speed}km/h입니다."
                )
            return "현재 어린이 보호구역으로 설정되어 있어요. 서행 운전에 유의해 주세요."
        return "현재 구간은 어린이 보호구역이 아닙니다."
