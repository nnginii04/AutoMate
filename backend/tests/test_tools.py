from __future__ import annotations

from app.schemas import ToolCall, VehicleState
from app.tools import ToolRegistry


def test_tool_registry_lists_all_required_tools():
    registry = ToolRegistry()
    names = {tool.name for tool in registry.list_tools()}
    assert names == {
        "setClimate",
        "setNavigation",
        "playMedia",
        "makeCall",
        "checkVehicleStatus",
        "checkRoadContext",
        "findNearbyPlace",
        "changeVehicleSetting",
        "readSchedule",
    }


def test_tool_registry_climate_execution():
    registry = ToolRegistry()
    tool_call = registry.build_tool_call(
        "CONTROL_CLIMATE",
        {"target_temperature": 24, "mode": "heating"},
        "나 좀 추워",
    )
    assert tool_call is not None
    assert tool_call.name == "setClimate"
    result = registry.execute(tool_call, VehicleState())
    assert result.success is True
    assert result.updated_vehicle_state is not None


def test_tool_registry_validates_arguments():
    registry = ToolRegistry()
    tool_call = ToolCall(name="setClimate", arguments={"temperature": 99, "mode": "auto"})
    result = registry.execute(tool_call, VehicleState())
    assert result.success is False
    assert result.tool_name == "setClimate"
    assert "Invalid tool arguments" in result.message


def test_change_vehicle_setting_window():
    registry = ToolRegistry()
    tool_call = registry.build_tool_call(
        "CHANGE_VEHICLE_SETTING",
        {"target": "window", "action": "close"},
        "창문 닫아줘",
    )
    assert tool_call is not None
    assert tool_call.name == "changeVehicleSetting"
    result = registry.execute(tool_call, VehicleState())
    assert result.success is True
    assert result.updated_vehicle_state["window_status"] == "closed"
