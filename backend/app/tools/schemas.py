from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SetClimateArgs(BaseModel):
    temperature: float = Field(default=24, ge=16, le=32)
    mode: Literal["auto", "heating", "cooling", "on", "off"] = "auto"


class SetNavigationArgs(BaseModel):
    destination: str = "home"
    route_type: Literal["fastest", "shortest", "eco"] = "fastest"


class PlayMediaArgs(BaseModel):
    genre: str = "default"
    volume: int = Field(default=50, ge=0, le=100)


class MakeCallArgs(BaseModel):
    contact: str = "unknown"
    hands_free: bool = True


class CheckVehicleStatusArgs(BaseModel):
    fields: List[str] = Field(default_factory=lambda: ["battery_level", "fuel_level"])


class FindNearbyPlaceArgs(BaseModel):
    place_type: str = "rest_area"
    radius_km: float = Field(default=10, gt=0, le=50)


class ChangeVehicleSettingArgs(BaseModel):
    setting: Literal["window", "wiper", "display", "general"] = "window"
    action: Optional[str] = None
    status: Optional[Literal["open", "closed", "partial"]] = None
    value: Optional[str] = None


class ReadScheduleArgs(BaseModel):
    range: Literal["today", "week"] = "today"
