"""Tests for the Vehicle Capability Catalog and CapabilityService."""

from __future__ import annotations

import pytest

from app.safety import SafetyGuard
from app.schemas import VehicleState
from app.services.capability_service import (
    CapabilityService,
    extract_contact,
    extract_destination,
    get_capability_service,
    normalize_text,
)


@pytest.fixture
def service() -> CapabilityService:
    return get_capability_service()


def test_catalog_loads_with_all_categories(service):
    categories = {cap.category for cap in service.all()}
    assert {
        "climate",
        "navigation",
        "media",
        "phone",
        "vehicle_setting",
        "vehicle_status",
        "road_context",
        "nearby_place",
    } <= categories
    assert len(service.all()) >= 20


@pytest.mark.parametrize(
    ("user_input", "expected_intent", "expected_tool"),
    [
        ("나 좀 추워", "CONTROL_CLIMATE", "setClimate"),
        ("차 안이 답답해", "CONTROL_CLIMATE", "setClimate"),
        ("밖에서 소똥냄새나", "CONTROL_CLIMATE", "setClimate"),
        ("집으로 안내해줘", "SET_NAVIGATION", "setNavigation"),
        ("서울역으로 가고싶어", "SET_NAVIGATION", "setNavigation"),
        ("소리 줄여줘", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("눈부셔", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("엄마한테 전화해줘", "MAKE_CALL", "makeCall"),
        ("배터리 상태 확인해줘", "CHECK_VEHICLE_STATUS", "checkVehicleStatus"),
        ("가까운 주유소 찾아줘", "FIND_NEARBY_PLACE", "findNearbyPlace"),
        ("졸려", "FIND_NEARBY_PLACE", "findNearbyPlace"),
    ],
)
def test_capability_match(service, user_input, expected_intent, expected_tool):
    match = service.match(user_input, VehicleState())
    assert match is not None, user_input
    assert match.intent == expected_intent
    assert match.tool_name == expected_tool


def test_capability_no_match_for_off_domain(service):
    assert service.match("아무 농담 해줘", VehicleState()) is None


def test_normalize_text_compact():
    normalized, compact = normalize_text("  손 시려워  ")
    assert normalized == "손 시려워"
    assert compact == "손시려워"


@pytest.mark.parametrize(
    ("user_input", "expected"),
    [
        ("서울역으로가고싶어", "Seoul Station"),
        ("대전역까지", "Daejeon Station"),
        ("집으로안내", "home"),
        ("회사로가자", "company"),
        ("성심당으로가줘", "성심당"),
    ],
)
def test_extract_destination(user_input, expected):
    assert extract_destination(user_input) == expected


@pytest.mark.parametrize(
    ("user_input", "expected"),
    [
        ("엄마한테전화해줘", "mother"),
        ("아빠한테전화해줘", "father"),
        ("정예진한테전화해줘", "정예진"),
        ("전화해줘", None),
    ],
)
def test_extract_contact(user_input, expected):
    assert extract_contact(user_input) == expected


def test_navigation_requires_destination(service):
    match = service.match("길 안내해줘", VehicleState())
    assert match is not None
    assert match.intent == "SET_NAVIGATION"
    assert "destination" in match.missing_required


def test_call_requires_contact(service):
    match = service.match("전화해줘", VehicleState())
    assert match is not None
    assert match.intent == "MAKE_CALL"
    assert "contact" in match.missing_required


def test_smell_closes_window_when_open(service):
    match = service.match("밖에서 소똥냄새나", VehicleState(window_status="open"))
    assert match is not None
    assert match.slots.get("mode") == "recirculation"
    assert match.slots.get("close_window") is True


def test_safety_allows_capability_while_driving(service):
    guard = SafetyGuard()
    capability = service.get("setting.window_close")
    decision = guard.evaluate(
        "창문 닫아줘",
        "CHANGE_VEHICLE_SETTING",
        VehicleState(is_driving=True, speed=60),
        {"setting": "window_status", "value": "closed"},
        capability=capability,
    )
    assert decision.allowed is True
    assert decision.blocked is False


def test_safety_blocks_capability_while_driving(service):
    guard = SafetyGuard()
    capability = service.get("setting.window_open")
    decision = guard.evaluate(
        "창문 열어줘",
        "CHANGE_VEHICLE_SETTING",
        VehicleState(is_driving=True, speed=60),
        {"setting": "window_status", "value": "open"},
        capability=capability,
    )
    assert decision.blocked is True
    assert decision.risk_level == "critical"


def test_safety_blocks_complex_display_capability(service):
    guard = SafetyGuard()
    capability = service.get("setting.display_complex_block")
    decision = guard.evaluate(
        "운전 중인데 화면 설정 좀 복잡하게 바꿔줘",
        "CHANGE_VEHICLE_SETTING",
        VehicleState(is_driving=True, speed=72),
        capability.default_arguments,
        capability=capability,
    )
    assert decision.blocked is True
    assert "정차 후" in (decision.fallback_response or "")
