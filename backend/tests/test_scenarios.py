from app.scenarios.loader import load_test_scenarios
from app.services.scenario_service import ScenarioService


def test_load_scenarios_count():
    scenarios = load_test_scenarios()
    assert len(scenarios) >= 20


def test_scenario_has_expected_fields():
    scenarios = load_test_scenarios()
    climate = next(s for s in scenarios if s.id == "climate-cold")
    assert climate.expected_intent == "CONTROL_CLIMATE"
    assert climate.expected_tool == "setClimate"
    assert climate.expected_result is not None
    assert climate.expected_result.success is True


def test_run_all_scenarios(db_session):
    service = ScenarioService(db_session)
    response = service.run_all()
    assert response.summary.total >= 20
    assert len(response.results) == response.summary.total
    assert 0.0 <= response.summary.intent_accuracy <= 1.0
    assert 0.0 <= response.summary.tool_accuracy <= 1.0
    assert 0.0 <= response.summary.safety_accuracy <= 1.0
    assert response.summary.passed + response.summary.failed == response.summary.total


def test_run_single_scenario(db_session):
    service = ScenarioService(db_session)
    result = service.run_scenario("climate-cold")
    assert result is not None
    assert result.scenario_id == "climate-cold"
    assert result.passed_intent is True
    assert result.run_log_id is not None


def test_safety_scenario_blocked(db_session):
    service = ScenarioService(db_session)
    result = service.run_scenario("display-block")
    assert result is not None
    assert result.agent_response.safety_blocked is True
    assert result.passed_safety is True
