from __future__ import annotations

from typing import Any, Dict, List

from app.schemas import ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.schemas import CheckVehicleStatusArgs

_TARGET_FIELDS: Dict[str, List[str]] = {
    "battery_level": ["battery_level"],
    "battery": ["battery_level"],
    "fuel_level": ["fuel_level"],
    "fuel": ["fuel_level"],
    "weather": ["weather"],
    "indoor_temperature": ["indoor_temperature"],
    "overall": ["battery_level", "fuel_level", "weather", "indoor_temperature"],
    "general": ["battery_level", "fuel_level"],
}


class CheckVehicleStatusTool(VehicleTool[CheckVehicleStatusArgs]):
    name = "checkVehicleStatus"
    description = "Read vehicle status metrics such as battery, fuel, and weather"
    argument_schema = CheckVehicleStatusArgs
    supported_intents = ("CHECK_VEHICLE_STATUS",)

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        target = slots.get("target", "overall")
        if target in ("battery",):
            target = "battery_level"
        if target in ("fuel",):
            target = "fuel_level"
        fields = _TARGET_FIELDS.get(target, _TARGET_FIELDS["overall"])
        return {"target": target, "fields": fields}

    def execute(self, arguments: CheckVehicleStatusArgs, vehicle_state: VehicleState) -> ToolResult:
        target = arguments.target
        if target == "battery_level":
            message = f"현재 배터리 잔량은 {int(vehicle_state.battery_level)}%입니다."
        elif target == "fuel_level":
            message = f"현재 연료 잔량은 {int(vehicle_state.fuel_level)}%입니다."
        elif target == "weather":
            weather_label = "비" if vehicle_state.weather.lower() in ("rainy", "rain") else vehicle_state.weather
            message = f"현재 날씨는 {weather_label}입니다."
            if vehicle_state.weather.lower() in ("rainy", "rain") and vehicle_state.window_status == "open":
                message += " 창문이 열려 있으니 닫는 것을 추천드려요."
        elif target == "indoor_temperature":
            message = f"현재 실내 온도는 {int(vehicle_state.indoor_temperature)}도입니다."
        else:
            message = (
                f"배터리 {int(vehicle_state.battery_level)}%, 연료 {int(vehicle_state.fuel_level)}%, "
                f"실내 {int(vehicle_state.indoor_temperature)}도, 날씨 {vehicle_state.weather}입니다."
            )

        return ToolResult(
            success=True,
            tool_name=self.name,
            message=message,
        )
