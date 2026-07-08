from __future__ import annotations

import uuid

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.scenario_run_log import ScenarioRunLog
from app.schemas import AgentRunResponse, TestScenario, TestScenarioRunResponse


class ScenarioRunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        batch_id: str | None,
        scenario: TestScenario,
        result: TestScenarioRunResponse,
    ) -> ScenarioRunLog:
        agent_response = result.agent_response
        tool_name = agent_response.tool_call.name if agent_response.tool_call else None
        log = ScenarioRunLog(
            batch_id=batch_id,
            scenario_id=result.scenario_id,
            scenario_name=result.scenario_name,
            passed=result.passed,
            passed_intent=result.passed_intent,
            passed_tool=result.passed_tool,
            passed_result=result.passed_result,
            passed_safety=result.passed_safety,
            expected_intent=scenario.expected_intent,
            expected_tool=scenario.expected_tool,
            expected_result=scenario.expected_result.model_dump() if scenario.expected_result else None,
            actual_intent=agent_response.intent,
            actual_tool=tool_name,
            checks=result.checks,
            agent_response=agent_response.model_dump(),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_batch(self, batch_id: str) -> list[ScenarioRunLog]:
        stmt = (
            select(ScenarioRunLog)
            .where(ScenarioRunLog.batch_id == batch_id)
            .order_by(ScenarioRunLog.id)
        )
        return list(self.db.scalars(stmt).all())

    def get_recent(self, limit: int = 100) -> list[ScenarioRunLog]:
        stmt = select(ScenarioRunLog).order_by(desc(ScenarioRunLog.created_at)).limit(limit)
        return list(self.db.scalars(stmt).all())
