"""Tests for Road Context / Driving Information feature."""

from __future__ import annotations

import pytest

from app.nlu import RuleBasedNLU
from app.schemas import AgentRunRequest, VehicleState
from app.services.agent_service import AgentService
from app.tools import ToolRegistry


@pytest.fixture
def agent(db_session):
    return AgentService(db_session)


@pytest.mark.parametrize(
    ("user_input", "expected_target"),
    [
        ("지금 제한속도 몇이야?", "speed_limit"),
        ("나 과속 중이야?", "speeding_status"),
        ("속도 괜찮아?", "speeding_status"),
        ("지금 도로 이름 뭐야?", "road_name"),
        ("여기 어린이 보호구역이야?", "school_zone"),
    ],
)
def test_road_context_nlu_intent(user_input, expected_target):
    nlu = RuleBasedNLU()
    result = nlu.parse(user_input, VehicleState(is_driving=True))
    assert result.intent == "CHECK_ROAD_CONTEXT"
    assert result.slots.get("target") == expected_target
    assert result.capability_id is not None


@pytest.mark.parametrize(
    "user_input",
    [
        "지금 제한속도 몇이야?",
        "나 과속 중이야?",
        "속도 괜찮아?",
        "여기 어린이 보호구역이야?",
        "지금 도로 이름 뭐야?",
    ],
)
def test_road_context_agent_run(client, user_input):
    response = client.post(
        "/api/agent/run",
        json={
            "user_input": user_input,
            "vehicle_state": {
                "speed": 72,
                "speed_limit": 60,
                "road_name": "대전 유성대로",
                "road_type": "urban",
                "is_driving": True,
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "CHECK_ROAD_CONTEXT"
    assert data["tool_call"]["name"] == "checkRoadContext"
    assert data["success"] is True
    assert data["fallback"] is False


def test_road_context_speeding_safety_message(agent):
    response = agent.run(
        AgentRunRequest(
            user_input="지금 제한속도 몇이야?",
            vehicle_state={
                "speed": 72,
                "speed_limit": 60,
                "road_name": "대전 유성대로",
                "is_driving": True,
            },
        )
    )
    assert response.intent == "CHECK_ROAD_CONTEXT"
    assert response.success is True
    assert "줄여" in response.final_response or "초과" in response.final_response


def test_road_context_within_limit_message(agent):
    response = agent.run(
        AgentRunRequest(
            user_input="속도 괜찮아?",
            vehicle_state={
                "speed": 55,
                "speed_limit": 60,
                "road_name": "대전 유성대로",
                "is_driving": True,
            },
        )
    )
    assert response.intent == "CHECK_ROAD_CONTEXT"
    assert response.success is True
    assert "이내" in response.final_response


def test_road_context_school_zone_speeding(agent):
    response = agent.run(
        AgentRunRequest(
            user_input="여기 어린이 보호구역이야?",
            vehicle_state={
                "speed": 35,
                "speed_limit": 30,
                "is_school_zone": True,
                "road_type": "school_zone",
                "is_driving": True,
            },
        )
    )
    assert response.intent == "CHECK_ROAD_CONTEXT"
    assert response.success is True
    assert "어린이 보호구역" in response.final_response
    assert "줄이" in response.final_response


def test_road_context_missing_speed_limit(agent):
    response = agent.run(
        AgentRunRequest(
            user_input="지금 제한속도 몇이야?",
            vehicle_state={
                "speed": 45,
                "speed_limit": None,
                "road_name": None,
                "is_driving": True,
            },
        )
    )
    assert response.intent == "CHECK_ROAD_CONTEXT"
    assert response.success is False
    assert "확인할 수 없" in response.final_response


def test_road_context_tool_data():
    registry = ToolRegistry()
    tool_call = registry.build_tool_call(
        "CHECK_ROAD_CONTEXT",
        {"target": "speed_limit"},
        "지금 제한속도 몇이야?",
    )
    assert tool_call is not None
    assert tool_call.name == "checkRoadContext"
    result = registry.execute(
        tool_call,
        VehicleState(speed=72, speed_limit=60, road_name="대전 유성대로"),
    )
    assert result.success is True
    assert result.data is not None
    assert result.data["is_speeding"] is True
    assert result.data["speed_over"] == 12


def test_battery_status_not_road_context():
    nlu = RuleBasedNLU()
    result = nlu.parse("배터리 상태 확인해줘", VehicleState())
    assert result.intent == "CHECK_VEHICLE_STATUS"


def test_navigation_eta_not_road_context():
    nlu = RuleBasedNLU()
    result = nlu.parse("서울역까지 얼마나 걸려", VehicleState())
    assert result.intent == "SET_NAVIGATION"
