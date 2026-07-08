"""Agent quality integration tests for Korean in-vehicle utterances."""

from __future__ import annotations

import pytest

from app.nlu import RuleBasedNLU
from app.safety import SafetyGuard
from app.schemas import VehicleState
from app.services.agent_service import AgentService
from app.schemas import AgentRunRequest


@pytest.fixture
def agent(db_session):
    return AgentService(db_session)


@pytest.mark.parametrize(
    ("user_input", "vehicle_overrides", "expected_intent", "expected_tool"),
    [
        ("밖에 비가 와", {"weather": "rainy", "window_status": "open", "is_driving": True}, "CHECK_VEHICLE_STATUS", "checkVehicleStatus"),
        ("밖에서 소똥냄새나", {"window_status": "open", "is_driving": True}, "CONTROL_CLIMATE", "setClimate"),
        ("소리 줄여줘", {"media_status": "on", "is_driving": True}, "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("눈부셔", {"is_driving": True}, "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("나 좀 추워", {"is_driving": True}, "CONTROL_CLIMATE", "setClimate"),
    ],
)
def test_agent_korean_utterances(agent, user_input, vehicle_overrides, expected_intent, expected_tool):
    response = agent.run(AgentRunRequest(user_input=user_input, vehicle_state=vehicle_overrides))
    assert response.intent == expected_intent
    assert response.tool_call is not None
    assert response.tool_call.name == expected_tool
    assert response.success is True
    assert response.fallback is False
    assert response.latency_ms >= 1


def test_agent_safety_block_display(agent):
    response = agent.run(
        AgentRunRequest(
            user_input="운전 중인데 화면 설정 좀 복잡하게 바꿔줘",
            vehicle_state={"is_driving": True, "speed": 72},
        )
    )
    assert response.safety_blocked is True
    assert response.success is False
    assert response.tool_call is None


def test_agent_call_clarification(agent):
    response = agent.run(
        AgentRunRequest(user_input="전화해줘", vehicle_state={"is_driving": True})
    )
    assert response.requires_clarification is True
    assert response.success is False


def test_agent_fallback_unknown(agent):
    response = agent.run(AgentRunRequest(user_input="아무 농담 해줘", vehicle_state={}))
    assert response.intent == "UNKNOWN"
    assert response.fallback is True
    assert response.success is False


def test_nlu_rain_weather_status():
    nlu = RuleBasedNLU()
    result = nlu.parse("밖에 비가 와", VehicleState(weather="rainy", window_status="open"))
    assert result.intent == "CHECK_VEHICLE_STATUS"
    assert result.slots.get("target") == "weather"


def test_nlu_smell_recirculation():
    nlu = RuleBasedNLU()
    result = nlu.parse("밖에서 소똥냄새나", VehicleState(window_status="open"))
    assert result.intent == "CONTROL_CLIMATE"
    assert result.slots.get("mode") == "recirculation"


def test_nlu_volume_down():
    nlu = RuleBasedNLU()
    result = nlu.parse("소리 줄여줘")
    assert result.intent == "CHANGE_VEHICLE_SETTING"
    assert result.slots.get("setting") == "volume"


def test_nlu_glare_brightness():
    nlu = RuleBasedNLU()
    result = nlu.parse("눈부셔")
    assert result.intent == "CHANGE_VEHICLE_SETTING"
    assert result.slots.get("setting") == "display_brightness"


def test_safety_allows_volume_while_driving():
    guard = SafetyGuard()
    result = guard.evaluate(
        "소리 줄여줘",
        "CHANGE_VEHICLE_SETTING",
        VehicleState(is_driving=True, speed=60),
        {"setting": "volume", "value": "down"},
    )
    assert result.allowed is True
    assert result.blocked is False


def test_agent_latency_logged(agent, db_session):
    response = agent.run(AgentRunRequest(user_input="나 좀 추워", vehicle_state={}))
    assert response.latency_ms >= 1
    logs = agent.log_repo.get_all(limit=1)
    assert logs[0].latency_ms >= 1
    assert logs[0].success is True
