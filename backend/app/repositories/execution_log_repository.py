from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.execution_log import ExecutionLog
from app.schemas import AgentRunResponse, DistributionItem, EvaluationSummary, ExecutionLogResponse


class ExecutionLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_from_agent_run(
        self,
        user_input: str,
        vehicle_snapshot: dict,
        response: AgentRunResponse,
    ) -> ExecutionLog:
        tool_call = response.tool_call
        tool_result = response.tool_result
        log = ExecutionLog(
            user_input=user_input,
            vehicle_state_snapshot=vehicle_snapshot,
            intent=response.intent,
            slots=response.slots,
            tool_name=tool_call.name if tool_call else None,
            tool_arguments=tool_call.arguments if tool_call else None,
            tool_result=tool_result.model_dump() if tool_result else None,
            final_response=response.final_response,
            success=response.success,
            failure_reason=response.failure_reason,
            latency_ms=response.latency_ms,
            safety_blocked=response.safety_blocked,
            fallback=response.fallback,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_all(self, limit: int = 200) -> list[ExecutionLog]:
        stmt = select(ExecutionLog).order_by(desc(ExecutionLog.created_at)).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, log_id: int) -> ExecutionLog | None:
        return self.db.get(ExecutionLog, log_id)

    def to_response(self, log: ExecutionLog) -> ExecutionLogResponse:
        return ExecutionLogResponse(
            id=log.id,
            user_input=log.user_input,
            vehicle_state_snapshot=log.vehicle_state_snapshot,
            intent=log.intent,
            slots=log.slots or {},
            tool_name=log.tool_name,
            tool_arguments=log.tool_arguments,
            tool_result=log.tool_result,
            final_response=log.final_response,
            success=log.success,
            failure_reason=log.failure_reason,
            latency_ms=log.latency_ms,
            created_at=log.created_at.isoformat(),
        )

    def get_evaluation_summary(self) -> EvaluationSummary:
        total = self.db.scalar(select(func.count()).select_from(ExecutionLog)) or 0
        if total == 0:
            return EvaluationSummary(
                total_requests=0,
                success_requests=0,
                failed_requests=0,
                tool_call_success_rate=0.0,
                average_latency_ms=0.0,
                safety_block_count=0,
                fallback_count=0,
            )

        success = self.db.scalar(
            select(func.count()).select_from(ExecutionLog).where(ExecutionLog.success.is_(True))
        ) or 0
        failed = total - success
        avg_latency = self.db.scalar(select(func.avg(ExecutionLog.latency_ms))) or 0.0
        safety_blocks = self.db.scalar(
            select(func.count()).select_from(ExecutionLog).where(ExecutionLog.safety_blocked.is_(True))
        ) or 0
        fallbacks = self.db.scalar(
            select(func.count()).select_from(ExecutionLog).where(ExecutionLog.fallback.is_(True))
        ) or 0

        tool_calls = self.db.scalar(
            select(func.count()).select_from(ExecutionLog).where(ExecutionLog.tool_name.is_not(None))
        ) or 0
        tool_success = self.db.scalar(
            select(func.count())
            .select_from(ExecutionLog)
            .where(
                ExecutionLog.tool_name.is_not(None),
                ExecutionLog.success.is_(True),
            )
        ) or 0
        tool_rate = (tool_success / tool_calls) if tool_calls else 0.0

        return EvaluationSummary(
            total_requests=total,
            success_requests=success,
            failed_requests=failed,
            tool_call_success_rate=round(tool_rate, 4),
            average_latency_ms=round(float(avg_latency), 2),
            safety_block_count=safety_blocks,
            fallback_count=fallbacks,
        )

    def get_intent_distribution(self) -> list[DistributionItem]:
        rows = self.db.execute(
            select(ExecutionLog.intent, func.count())
            .group_by(ExecutionLog.intent)
            .order_by(desc(func.count()))
        ).all()
        return [DistributionItem(name=row[0], count=row[1]) for row in rows]

    def get_tool_usage(self) -> list[DistributionItem]:
        rows = self.db.execute(
            select(ExecutionLog.tool_name, func.count())
            .where(ExecutionLog.tool_name.is_not(None))
            .group_by(ExecutionLog.tool_name)
            .order_by(desc(func.count()))
        ).all()
        return [DistributionItem(name=row[0], count=row[1]) for row in rows]
