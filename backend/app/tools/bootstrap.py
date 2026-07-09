from __future__ import annotations

from app.tools.base import VehicleTool
from app.tools.call import MakeCallTool
from app.tools.climate import SetClimateTool
from app.tools.media import PlayMediaTool
from app.tools.navigation import SetNavigationTool
from app.tools.nearby import FindNearbyPlaceTool
from app.tools.road_context import CheckRoadContextTool
from app.tools.schedule import ReadScheduleTool
from app.tools.status import CheckVehicleStatusTool
from app.tools.vehicle_setting import ChangeVehicleSettingTool


def build_default_tools() -> list[VehicleTool]:
    """Instantiate all built-in vehicle tools in registration order."""
    return [
        SetClimateTool(),
        SetNavigationTool(),
        PlayMediaTool(),
        MakeCallTool(),
        CheckVehicleStatusTool(),
        CheckRoadContextTool(),
        FindNearbyPlaceTool(),
        ChangeVehicleSettingTool(),
        ReadScheduleTool(),
    ]
