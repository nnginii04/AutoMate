"""Tests for per-session isolation and thread-safety of the vehicle state store."""

from __future__ import annotations

import threading

import pytest

from app.services.vehicle_service import (
    DEFAULT_SESSION_ID,
    MAX_SESSIONS,
    VehicleStateStore,
)


@pytest.fixture
def store() -> VehicleStateStore:
    return VehicleStateStore()


def test_sessions_are_isolated(store: VehicleStateStore) -> None:
    store.update({"speed": 10}, session_id="alice")
    store.update({"speed": 99}, session_id="bob")

    assert store.get("alice").speed == 10
    assert store.get("bob").speed == 99


def test_no_session_id_uses_default_key(store: VehicleStateStore) -> None:
    store.update({"speed": 42})  # no session id -> default
    assert store.get(DEFAULT_SESSION_ID).speed == 42
    assert store.get().speed == 42


def test_reset_only_affects_target_session(store: VehicleStateStore) -> None:
    store.update({"speed": 10}, session_id="alice")
    store.update({"speed": 20}, session_id="bob")

    store.reset(session_id="alice")

    assert store.get("alice").speed == 72  # back to default
    assert store.get("bob").speed == 20  # untouched


def test_apply_tool_updates_is_scoped(store: VehicleStateStore) -> None:
    store.update({"window_status": "open"}, session_id="alice")
    store.apply_tool_updates({"window_status": "closed"}, session_id="alice")

    assert store.get("alice").window_status == "closed"
    # A fresh session still sees the default state
    assert store.get("bob").window_status == "open"


def test_get_returns_a_copy(store: VehicleStateStore) -> None:
    first = store.get("alice")
    first.speed = 123
    # Mutating the returned copy must not leak back into the store
    assert store.get("alice").speed != 123


def test_lru_eviction_bounds_session_count(store: VehicleStateStore) -> None:
    for i in range(MAX_SESSIONS + 25):
        store.update({"speed": i}, session_id=f"session-{i}")
    assert len(store._states) == MAX_SESSIONS  # noqa: SLF001
    # The very first sessions should have been evicted
    assert "session-0" not in store._states  # noqa: SLF001


def test_concurrent_updates_do_not_corrupt_state(store: VehicleStateStore) -> None:
    def writer(session: str, value: int) -> None:
        for _ in range(50):
            store.update({"speed": value}, session_id=session)

    threads = [
        threading.Thread(target=writer, args=(f"s{i}", i * 5)) for i in range(8)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for i in range(8):
        assert store.get(f"s{i}").speed == i * 5


def test_agent_run_respects_session_header(client) -> None:
    # Drive session A's state via a tool call, then confirm session B is unaffected.
    client.post(
        "/api/agent/run",
        json={"user_input": "창문 닫아줘", "vehicle_state": {"is_driving": False}},
        headers={"X-Session-Id": "sessionA"},
    )
    state_b = client.get("/api/vehicle/state", headers={"X-Session-Id": "sessionB"})
    assert state_b.status_code == 200
    # Session B never ran anything, so it still holds the default open window.
    assert state_b.json()["window_status"] == "open"
