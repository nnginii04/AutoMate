def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_agent_run_climate(client):
    response = client.post(
        "/api/agent/run",
        json={
            "user_input": "나 좀 추워",
            "vehicle_state": {"is_driving": True, "speed": 72},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "CONTROL_CLIMATE"
    assert data["success"] is True
    assert data["tool_call"]["name"] == "setClimate"


def test_agent_run_safety_block(client):
    response = client.post(
        "/api/agent/run",
        json={
            "user_input": "운전 중인데 화면 설정 좀 복잡하게 바꿔줘",
            "vehicle_state": {"is_driving": True, "speed": 72},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["safety_blocked"] is True
    assert data["success"] is False


def test_agent_run_fallback(client):
    response = client.post(
        "/api/agent/run",
        json={"user_input": "아무 농담 해줘", "vehicle_state": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "UNKNOWN"
    assert data["fallback"] is True
    assert data["safety_decision"]["allowed"] is False
    assert data["safety_decision"]["fallback_response"] is not None


def test_agent_run_navigation_clarification(client):
    response = client.post(
        "/api/agent/run",
        json={"user_input": "안내해줘", "vehicle_state": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["requires_clarification"] is True
    assert data["success"] is False
    assert data["nlu_source"] == "rule_based"
    assert "목적지" in data["final_response"] or "어디" in data["final_response"]


def test_vehicle_state_endpoints(client):
    get_resp = client.get("/api/vehicle/state")
    assert get_resp.status_code == 200

    patch_resp = client.patch(
        "/api/vehicle/state",
        json={"speed": 80, "location": "Seoul"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["speed"] == 80


def test_logs_created_after_agent_run(client):
    client.post(
        "/api/agent/run",
        json={"user_input": "배터리 상태 확인해줘", "vehicle_state": {}},
    )
    logs = client.get("/api/logs").json()
    assert len(logs) >= 1


def test_evaluation_summary(client):
    client.post(
        "/api/agent/run",
        json={"user_input": "집으로 안내해줘", "vehicle_state": {}},
    )
    summary = client.get("/api/evaluation/summary").json()
    assert summary["total_requests"] >= 1


def test_scenarios_list(client):
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    assert len(response.json()) >= 20


def test_scenario_run(client):
    response = client.post("/api/scenarios/climate-cold/run", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "climate-cold"
    assert data["agent_response"]["intent"] == "CONTROL_CLIMATE"
    assert "passed" in data


def test_scenario_run_by_path(client):
    response = client.post("/api/scenarios/run/climate-cold", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["passed"] is True


def test_scenario_run_all(client):
    response = client.post("/api/scenarios/run-all")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total"] >= 20
    assert len(data["results"]) >= 20
    assert "intent_accuracy" in data["summary"]
