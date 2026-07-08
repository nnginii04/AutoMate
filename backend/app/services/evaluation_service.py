from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories import ExecutionLogRepository
from app.schemas import DistributionItem, EvaluationSummary, ExecutionLogResponse


class LogService:
    def __init__(self, db: Session) -> None:
        self.repo = ExecutionLogRepository(db)

    def list_logs(self) -> list[ExecutionLogResponse]:
        return [self.repo.to_response(log) for log in self.repo.get_all()]

    def get_log(self, log_id: int) -> ExecutionLogResponse | None:
        log = self.repo.get_by_id(log_id)
        if not log:
            return None
        return self.repo.to_response(log)


class EvaluationService:
    def __init__(self, db: Session) -> None:
        self.repo = ExecutionLogRepository(db)

    def get_summary(self) -> EvaluationSummary:
        return self.repo.get_evaluation_summary()

    def get_intent_distribution(self) -> list[DistributionItem]:
        return self.repo.get_intent_distribution()

    def get_tool_usage(self) -> list[DistributionItem]:
        return self.repo.get_tool_usage()
