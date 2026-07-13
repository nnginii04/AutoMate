from __future__ import annotations

import copy
import threading
from collections import OrderedDict
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
    road_name="대전 유성대로",
    road_type="urban",
    speed_limit=60,
    is_school_zone=False,
    navigation_active=True,
)

# Fallback key used when a request does not carry a session identifier. This
# preserves the original single-state behaviour for callers (and tests) that do
# not pass a session id.
DEFAULT_SESSION_ID = "default"

# Upper bound on concurrently tracked sessions. Oldest (least-recently-used)
# sessions are evicted beyond this to keep the in-memory store bounded.
MAX_SESSIONS = 500


class VehicleStateStore:
    """Thread-safe, per-session in-memory vehicle state store.

    Each session (keyed by an ``X-Session-Id`` supplied by the caller) owns an
    isolated :class:`VehicleState`, so concurrent users no longer share or clobber
    a single global state. All access is guarded by a lock because FastAPI runs
    sync endpoints in a worker threadpool. The session map is an LRU bounded to
    :data:`MAX_SESSIONS` entries.
    """

    def __init__(self) -> None:
        self._states: "OrderedDict[str, VehicleState]" = OrderedDict()
        self._lock = threading.Lock()

    def _resolve(self, session_id: str | None) -> str:
        return session_id or DEFAULT_SESSION_ID

    def _touch(self, key: str, state: VehicleState) -> None:
        """Insert/refresh a session as most-recently-used, evicting the oldest."""
        self._states[key] = state
        self._states.move_to_end(key)
        while len(self._states) > MAX_SESSIONS:
            self._states.popitem(last=False)

    def get(self, session_id: str | None = None) -> VehicleState:
        key = self._resolve(session_id)
        with self._lock:
            state = self._states.get(key)
            if state is None:
                state = DEFAULT_VEHICLE_STATE
                self._touch(key, state)
            else:
                self._states.move_to_end(key)
            return copy.deepcopy(state)

    def update(self, partial: dict[str, Any], session_id: str | None = None) -> VehicleState:
        key = self._resolve(session_id)
        with self._lock:
            base = self._states.get(key, DEFAULT_VEHICLE_STATE)
            merged = base.merge(partial)
            self._touch(key, merged)
            return copy.deepcopy(merged)

    def apply_tool_updates(
        self, updates: dict[str, Any] | None, session_id: str | None = None
    ) -> VehicleState:
        key = self._resolve(session_id)
        with self._lock:
            base = self._states.get(key, DEFAULT_VEHICLE_STATE)
            if updates:
                base = base.merge(updates)
            self._touch(key, base)
            return copy.deepcopy(base)

    def reset(self, session_id: str | None = None) -> VehicleState:
        key = self._resolve(session_id)
        with self._lock:
            self._touch(key, DEFAULT_VEHICLE_STATE)
            return copy.deepcopy(DEFAULT_VEHICLE_STATE)

    def reset_all(self) -> None:
        """Clear every tracked session (test / development helper)."""
        with self._lock:
            self._states.clear()


vehicle_state_store = VehicleStateStore()
