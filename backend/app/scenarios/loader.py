from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.schemas import ExpectedScenarioResult, TestScenario

SCENARIOS_FILE = Path(__file__).resolve().parent.parent / "data" / "test-scenarios.json"


@lru_cache
def load_test_scenarios() -> list[TestScenario]:
    with SCENARIOS_FILE.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    scenarios: list[TestScenario] = []
    for item in payload.get("scenarios", []):
        expected_result = item.get("expected_result")
        scenarios.append(
            TestScenario(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                user_input=item["user_input"],
                vehicle_state_overrides=item.get("vehicle_state_overrides", {}),
                expected_intent=item.get("expected_intent"),
                expected_tool=item.get("expected_tool"),
                expected_result=ExpectedScenarioResult(**expected_result)
                if expected_result
                else None,
                tags=item.get("tags", []),
            )
        )
    return scenarios
