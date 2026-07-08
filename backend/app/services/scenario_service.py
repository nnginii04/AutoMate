from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.scenario_run_repository import ScenarioRunRepository
from app.scenarios import load_test_scenarios
from app.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    ExpectedScenarioResult,
    RunAllScenariosResponse,
    ScenarioAccuracySummary,
    TestScenario,
    TestScenarioRunRequest,
    TestScenarioRunResponse,
)
from app.services.agent_service import AgentService
from app.services.vehicle_service import vehicle_state_store


class ScenarioService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.agent_service = AgentService(db)
        self.run_repo = ScenarioRunRepository(db)

    def list_scenarios(self) -> list[TestScenario]:
        return load_test_scenarios()

    def get_scenario(self, scenario_id: str) -> TestScenario | None:
        return next((s for s in load_test_scenarios() if s.id == scenario_id), None)

    def run_scenario(
        self,
        scenario_id: str,
        request: TestScenarioRunRequest | None = None,
        *,
        batch_id: str | None = None,
        persist: bool = True,
    ) -> TestScenarioRunResponse | None:
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None

        vehicle_state_store.reset()
        overrides = {**scenario.vehicle_state_overrides}
        if request and request.vehicle_state_overrides:
            overrides.update(request.vehicle_state_overrides)

        agent_response = self.agent_service.run(
            AgentRunRequest(
                user_input=scenario.user_input,
                vehicle_state=overrides,
            )
        )

        result = self._evaluate_scenario(scenario, agent_response)
        if persist:
            log = self.run_repo.create(batch_id=batch_id, scenario=scenario, result=result)
            result.run_log_id = log.id
        return result

    def run_all(self) -> RunAllScenariosResponse:
        import uuid

        batch_id = str(uuid.uuid4())
        scenarios = self.list_scenarios()
        results: list[TestScenarioRunResponse] = []

        for scenario in scenarios:
            result = self.run_scenario(scenario.id, batch_id=batch_id, persist=True)
            if result:
                results.append(result)

        summary = self._build_accuracy_summary(results)
        return RunAllScenariosResponse(batch_id=batch_id, summary=summary, results=results)

    def _evaluate_scenario(
        self,
        scenario: TestScenario,
        agent_response: AgentRunResponse,
    ) -> TestScenarioRunResponse:
        checks: dict[str, bool] = {}

        passed_intent: bool | None = None
        if scenario.expected_intent is not None:
            passed_intent = agent_response.intent == scenario.expected_intent
            checks["intent"] = passed_intent

        passed_tool: bool | None = None
        if scenario.expected_tool is not None:
            actual_tool = agent_response.tool_call.name if agent_response.tool_call else None
            passed_tool = actual_tool == scenario.expected_tool
            checks["tool"] = passed_tool

        passed_result: bool | None = None
        if scenario.expected_result is not None:
            passed_result = self._match_expected_result(scenario.expected_result, agent_response)
            checks["result"] = passed_result

        passed_safety: bool | None = None
        if self._is_safety_scenario(scenario):
            passed_safety = self._match_safety_expectations(scenario, agent_response)
            checks["safety"] = passed_safety

        overall_checks = [value for value in checks.values()]
        passed = all(overall_checks) if overall_checks else True

        return TestScenarioRunResponse(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            agent_response=agent_response,
            passed=passed,
            passed_intent=passed_intent,
            passed_tool=passed_tool,
            passed_result=passed_result,
            passed_safety=passed_safety,
            checks=checks,
            passed_intent_check=passed_intent,
        )

    @staticmethod
    def _match_expected_result(
        expected: ExpectedScenarioResult,
        response: AgentRunResponse,
    ) -> bool:
        if expected.success is not None and response.success != expected.success:
            return False
        if expected.safety_blocked is not None and response.safety_blocked != expected.safety_blocked:
            return False
        if expected.fallback is not None and response.fallback != expected.fallback:
            return False
        if (
            expected.requires_clarification is not None
            and response.requires_clarification != expected.requires_clarification
        ):
            return False
        return True

    @staticmethod
    def _is_safety_scenario(scenario: TestScenario) -> bool:
        if "safety" in scenario.tags:
            return True
        if not scenario.expected_result:
            return False
        return (
            scenario.expected_result.safety_blocked is not None
            or scenario.expected_result.requires_clarification is not None
        )

    @staticmethod
    def _match_safety_expectations(scenario: TestScenario, response: AgentRunResponse) -> bool:
        expected = scenario.expected_result
        if not expected:
            return response.safety_blocked or response.requires_clarification

        checks: list[bool] = []
        if expected.safety_blocked is not None:
            checks.append(response.safety_blocked == expected.safety_blocked)
        if expected.requires_clarification is not None:
            checks.append(response.requires_clarification == expected.requires_clarification)
        if expected.success is not None and (
            expected.safety_blocked is not None or expected.requires_clarification is not None
        ):
            checks.append(response.success == expected.success)
        return all(checks) if checks else True

    @staticmethod
    def _build_accuracy_summary(results: list[TestScenarioRunResponse]) -> ScenarioAccuracySummary:
        total = len(results)
        passed = sum(1 for result in results if result.passed)
        failed = total - passed

        intent_results = [r.passed_intent for r in results if r.passed_intent is not None]
        tool_results = [r.passed_tool for r in results if r.passed_tool is not None]
        safety_results = [r.passed_safety for r in results if r.passed_safety is not None]

        intent_accuracy = (
            sum(1 for value in intent_results if value) / len(intent_results) if intent_results else 0.0
        )
        tool_accuracy = (
            sum(1 for value in tool_results if value) / len(tool_results) if tool_results else 0.0
        )
        safety_accuracy = (
            sum(1 for value in safety_results if value) / len(safety_results) if safety_results else 0.0
        )

        return ScenarioAccuracySummary(
            total=total,
            passed=passed,
            failed=failed,
            intent_accuracy=round(intent_accuracy, 4),
            tool_accuracy=round(tool_accuracy, 4),
            safety_accuracy=round(safety_accuracy, 4),
        )
