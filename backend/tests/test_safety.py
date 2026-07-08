from app.safety import SafetyGuard
from app.schemas import VehicleState


def test_safety_blocks_complex_display_while_driving():
    guard = SafetyGuard()
    state = VehicleState(is_driving=True, speed=72)
    result = guard.evaluate(
        "운전 중인데 화면 설정 좀 복잡하게 바꿔줘",
        "CHANGE_VEHICLE_SETTING",
        state,
        {"setting": "display", "complexity": "high"},
    )
    assert result.allowed is False
    assert result.blocked is True
    assert "정차 후" in (result.fallback_response or "")


def test_safety_allows_window_close():
    guard = SafetyGuard()
    state = VehicleState(is_driving=True, speed=60)
    result = guard.evaluate(
        "창문 닫아줘",
        "CHANGE_VEHICLE_SETTING",
        state,
        {"target": "window", "action": "close"},
    )
    assert result.allowed is True
    assert result.blocked is False


def test_safety_blocks_window_open_while_driving():
    guard = SafetyGuard()
    state = VehicleState(is_driving=True, speed=60)
    result = guard.evaluate(
        "창문 열어줘",
        "CHANGE_VEHICLE_SETTING",
        state,
        {"target": "window", "action": "open"},
    )
    assert result.blocked is True
    assert result.risk_level == "critical"


def test_safety_requires_navigation_clarification():
    guard = SafetyGuard()
    result = guard.evaluate(
        "안내해줘",
        "SET_NAVIGATION",
        VehicleState(),
        {"destination": "custom"},
    )
    assert result.requires_clarification is True
    assert result.allowed is False
    assert "destination" in (result.reason or "").lower()


def test_safety_requires_call_clarification():
    guard = SafetyGuard()
    result = guard.evaluate(
        "전화해줘",
        "MAKE_CALL",
        VehicleState(),
        {"contact": "unknown", "action": "call"},
    )
    assert result.requires_clarification is True
    assert "contact" in (result.reason or "").lower()


def test_safety_detects_rainy_window_context_risk():
    guard = SafetyGuard()
    state = VehicleState(weather="rainy", window_status="open", is_driving=True, speed=50)
    result = guard.evaluate(
        "나 좀 추워",
        "CONTROL_CLIMATE",
        state,
        {"action": "increase", "target_temperature": 24, "mode": "heating"},
    )
    assert result.allowed is True
    assert result.risk_level in ("medium", "high")
    assert result.reason is not None
    assert "Context risk" in result.reason


def test_safety_blocks_window_open_in_rain():
    guard = SafetyGuard()
    state = VehicleState(weather="rainy", window_status="open", is_driving=True, speed=50)
    result = guard.evaluate(
        "창문 열어줘",
        "CHANGE_VEHICLE_SETTING",
        state,
        {"target": "window", "action": "open"},
    )
    assert result.blocked is True
    assert result.risk_level in ("high", "critical")


def test_safety_prioritizes_rest_area_for_drowsy_driver():
    guard = SafetyGuard()
    state = VehicleState(driver_status="drowsy", is_driving=True, speed=80)
    result = guard.evaluate(
        "음악 틀어줘",
        "PLAY_MEDIA",
        state,
        {"genre": "default", "volume": "medium"},
    )
    assert result.requires_clarification is True
    assert "rest area" in (result.reason or "").lower() or "Drowsy" in (result.reason or "")
    assert "휴게소" in (result.fallback_response or "")


def test_safety_allows_rest_area_when_drowsy():
    guard = SafetyGuard()
    state = VehicleState(driver_status="drowsy", is_driving=True)
    result = guard.evaluate(
        "졸려",
        "FIND_NEARBY_PLACE",
        state,
        {"place_type": "rest_area", "urgency": "high"},
    )
    assert result.allowed is True
    assert result.risk_level == "high"


def test_safety_unknown_intent_fallback():
    guard = SafetyGuard()
    result = guard.evaluate("아무 농담 해줘", "UNKNOWN", VehicleState(), {})
    assert result.allowed is False
    assert result.blocked is False
    assert result.fallback_response is not None
    assert "차량 제어" in result.fallback_response
