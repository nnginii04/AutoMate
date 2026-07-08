"""Korean utterance variation coverage for the rule-based NLU and agent API."""

from __future__ import annotations

import pytest

from app.nlu.rule_based_nlu import RuleBasedNLU, normalize_text


def test_normalize_text_compact():
    normalized, compact = normalize_text("  손 시려워  ")
    assert normalized == "손 시려워"
    assert compact == "손시려워"


@pytest.mark.parametrize(
    "user_input, expected_intent, expected_tool",
    [
        ("손시려워", "CONTROL_CLIMATE", "setClimate"),
        ("손 시려워", "CONTROL_CLIMATE", "setClimate"),
        ("손시려", "CONTROL_CLIMATE", "setClimate"),
        ("발 시려워", "CONTROL_CLIMATE", "setClimate"),
        ("몸이 추워", "CONTROL_CLIMATE", "setClimate"),
        ("따뜻하게 해줘", "CONTROL_CLIMATE", "setClimate"),
        ("너무 더워", "CONTROL_CLIMATE", "setClimate"),
        ("시원하게 해줘", "CONTROL_CLIMATE", "setClimate"),
        ("서울역으로 가고싶어", "SET_NAVIGATION", "setNavigation"),
        ("서울역으로 가고 싶어", "SET_NAVIGATION", "setNavigation"),
        ("서울역까지 얼마나 걸려", "SET_NAVIGATION", "setNavigation"),
        ("서울역까지 안내해줘", "SET_NAVIGATION", "setNavigation"),
        ("서울역 가자", "SET_NAVIGATION", "setNavigation"),
        ("대전역으로 가줘", "SET_NAVIGATION", "setNavigation"),
        ("회사로 가자", "SET_NAVIGATION", "setNavigation"),
        ("소리 줄여줘", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("볼륨 낮춰줘", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("소리 키워줘", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("눈부셔", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("화면이 너무 밝아", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("창문 닫아줘", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("비 오니까 와이퍼 자동으로 해줘", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("와이퍼 켜줘", "CHANGE_VEHICLE_SETTING", "changeVehicleSetting"),
        ("밖에 비가 와", "CHECK_VEHICLE_STATUS", "checkVehicleStatus"),
        ("지금 날씨 어때?", "CHECK_VEHICLE_STATUS", "checkVehicleStatus"),
        ("배터리 얼마나 남았어?", "CHECK_VEHICLE_STATUS", "checkVehicleStatus"),
        ("실내 온도 몇 도야?", "CHECK_VEHICLE_STATUS", "checkVehicleStatus"),
        ("밖에서 소똥냄새나", "CONTROL_CLIMATE", "setClimate"),
        ("근처 카페 찾아줘", "FIND_NEARBY_PLACE", "findNearbyPlace"),
        ("가까운 주유소 찾아줘", "FIND_NEARBY_PLACE", "findNearbyPlace"),
    ],
)
def test_korean_nlu_variations(client, user_input, expected_intent, expected_tool):
    response = client.post(
        "/api/agent/run",
        json={"user_input": user_input, "vehicle_state": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == expected_intent, f"{user_input} -> {data['intent']}"
    assert data["tool_call"] is not None, f"{user_input} produced no tool_call"
    assert data["tool_call"]["name"] == expected_tool
    assert data["success"] is True
    assert data["fallback"] is False


@pytest.mark.parametrize(
    "user_input, expected_destination",
    [
        ("서울역으로 가고싶어", "Seoul Station"),
        ("대전역까지 얼마나 걸려", "Daejeon Station"),
        ("부산역 가자", "Busan Station"),
        ("집으로 안내해줘", "home"),
        ("회사로 가자", "company"),
        ("성심당으로 가고싶어", "성심당"),
    ],
)
def test_navigation_destination_extraction(user_input, expected_destination):
    nlu = RuleBasedNLU()
    result = nlu.parse(user_input)
    assert result.intent == "SET_NAVIGATION"
    assert result.slots.get("destination") == expected_destination


def test_navigation_requires_destination(client):
    response = client.post(
        "/api/agent/run",
        json={"user_input": "길 안내해줘", "vehicle_state": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "SET_NAVIGATION"
    assert data["requires_clarification"] is True
    assert data["success"] is False
    assert data["tool_call"] is None


def test_call_requires_contact(client):
    response = client.post(
        "/api/agent/run",
        json={"user_input": "전화해줘", "vehicle_state": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "MAKE_CALL"
    assert data["requires_clarification"] is True
    assert data["success"] is False


def test_call_contact_extraction(client):
    response = client.post(
        "/api/agent/run",
        json={"user_input": "정예진한테 전화해줘", "vehicle_state": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "MAKE_CALL"
    assert data["slots"]["contact"] == "정예진"
    assert data["success"] is True


def test_clear_logs_endpoint(client):
    client.post("/api/agent/run", json={"user_input": "나 좀 추워", "vehicle_state": {}})
    delete_resp = client.request("DELETE", "/api/logs")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["deleted"] >= 1
    logs = client.get("/api/logs").json()
    assert logs == []
