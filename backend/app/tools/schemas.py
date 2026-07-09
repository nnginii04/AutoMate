from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SetClimateArgs(BaseModel):
    temperature: float = Field(default=24, ge=16, le=32)
    mode: Literal[
        "auto",
        "heating",
        "cooling",
        "fresh_air",
        "recirculation",
        "defrost",
        "on",
        "off",
    ] = "auto"
    close_window: bool = False


class SetNavigationArgs(BaseModel):
    destination: str = "home"
    route_type: Literal["fastest", "shortest", "eco"] = "fastest"


class PlayMediaArgs(BaseModel):
    genre: str = "default"
    mood: Optional[str] = None
    action: Literal["play", "stop"] = "play"
    volume: int = Field(default=50, ge=0, le=100)


class MakeCallArgs(BaseModel):
    contact: str = "unknown"
    hands_free: bool = True


class CheckVehicleStatusArgs(BaseModel):
    target: Literal[
        "battery_level",
        "fuel_level",
        "weather",
        "indoor_temperature",
        "overall",
        "general",
    ] = "overall"
    fields: List[str] = Field(default_factory=lambda: ["battery_level", "fuel_level"])


class FindNearbyPlaceArgs(BaseModel):
    place_type: str = "rest_area"
    radius_km: float = Field(default=10, gt=0, le=50)


class ChangeVehicleSettingArgs(BaseModel):
    setting: Literal[
        "window_status",
        "wiper_mode",
        "wiper_status",
        "display_brightness",
        "volume",
        "door_lock",
        "media_status",
        "display",
        "wiper",
        "window",
        "general",
    ] = "window_status"
    action: Optional[str] = None
    status: Optional[Literal["open", "closed", "partial"]] = None
    value: Optional[str] = None


class ReadScheduleArgs(BaseModel):
    range: Literal["today", "week"] = "today"


class CheckRoadContextArgs(BaseModel):
    target: Literal[
        "speed_limit",
        "speeding_status",
        "road_name",
        "road_type",
        "school_zone",
        "overall",
    ] = "speed_limit"
