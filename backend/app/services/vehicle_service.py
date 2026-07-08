from __future__ import annotations

import copy
from typing import Any

from app.schemas import VehicleState

DEFAULT_VEHICLE_STATE = VehicleState(
    vehicle_id="VH-001",
    speed=72,
    indoor_temperature=18,
    outdoor_temperature=3,
    battery_level=68,
    fuel_level=42,
    driver_status="normal",
    driving_mode="highway",
    time="22:30",
    location="Daejeon",
    passenger_count=2,
    is_driving=True,
    weather="rainy",
    window_status="open",
    air_conditioner_status="off",
    media_status="off",
)


class VehicleStateStore:
    """In-memory vehicle state store for demo and integration testing."""

    def __init__(self) -> None:
        self._state = DEFAULT_VEHICLE_STATE

    def get(self) -> VehicleState:
        return copy.deepcopy(self._state)

    def update(self, partial: dict[str, Any]) -> VehicleState:
        self._state = self._state.merge(partial)
        return copy.deepcopy(self._state)

    def apply_tool_updates(self, updates: dict[str, Any] | None) -> VehicleState:
        if updates:
            self._state = self._state.merge(updates)
        return copy.deepcopy(self._state)

    def reset(self) -> VehicleState:
        self._state = DEFAULT_VEHICLE_STATE
        return copy.deepcopy(self._state)


vehicle_state_store = VehicleStateStore()
