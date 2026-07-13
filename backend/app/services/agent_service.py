from __future__ import annotations

import time

from sqlalchemy.orm import Session

from app.config import get_settings
from app.nlu import HybridNLU, create_nlu
from app.repositories import ExecutionLogRepository
from app.safety import SafetyGuard
from app.schemas import AgentRunRequest, AgentRunResponse, SafetyDecision, VehicleState
from app.services.capability_service import CapabilityService, get_capability_service
from app.services.response_builder import (
    build_clarification_response,
    build_fallback_response,
    build_final_response,
    build_safety_block_response,
    build_slot_clarification_response,
)
from app.services.vehicle_service import vehicle_state_store
from app.tools import ToolRegistry


class AgentService:
    """Orchestrates NLU → safety → tool execution → response → persistence."""

    def __init__(
        self,
        db: Session,
        nlu: HybridNLU | None = None,
        safety_guard: SafetyGuard | None = None,
        tool_registry: ToolRegistry | None = None,
        capability_service: CapabilityService | None = None,
    ) -> None:
        self.db = db
        self.tool_registry = tool_registry or ToolRegistry()
        self.nlu = nlu or create_nlu(tool_registry=self.tool_registry, settings=get_settings())
        self.safety_guard = safety_guard or SafetyGuard()
        self.capability_service = capability_service or get_capability_service()
        self.log_repo = ExecutionLogRepository(db)

    def run(self, request: AgentRunRequest, session_id: str | None = None) -> AgentRunResponse:
        started = time.perf_counter()
        user_input = request.user_input.strip()

        stored = vehicle_state_store.get(session_id)
        vehicle_state = stored.merge(request.vehicle_state)
        snapshot = vehicle_state.to_snapshot()

        nlu_result = self.nlu.parse(user_input, vehicle_state)
        capability = self.capability_service.get(nlu_result.capability_id)

        if nlu_result.intent != "UNKNOWN":
            slot_clarification = self._check_slot_clarification(nlu_result, capability)
            if slot_clarification:
                response = self._build_response(
                    intent=nlu_result.intent,
                    slots=nlu_result.slots,
                    confidence=nlu_result.confidence,
                    final_response=slot_clarification,
                    success=False,
                    failure_reason="Clarification required: missing required tool arguments",
                    requires_clarification=True,
                    nlu_source=nlu_result.source,
                    started=started,
                )
                self._persist(user_input, snapshot, response)
                return response

        safety = self.safety_guard.evaluate(
            user_input, nlu_result.intent, vehicle_state, nlu_result.slots, capability=capability
        )

        if safety.blocked:
            response = self._build_response(
                intent=nlu_result.intent,
                slots=nlu_result.slots,
                confidence=nlu_result.confidence,
                final_response=build_safety_block_response(safety),
                success=False,
                failure_reason=safety.reason,
                safety_blocked=True,
                safety_decision=safety,
                nlu_source=nlu_result.source,
                started=started,
            )
            self._persist(user_input, snapshot, response)
            return response

        if safety.requires_clarification:
            response = self._build_response(
                intent=nlu_result.intent,
                slots=nlu_result.slots,
                confidence=nlu_result.confidence,
                final_response=build_clarification_response(safety),
                success=False,
                failure_reason=safety.reason,
                requires_clarification=True,
                safety_decision=safety,
                nlu_source=nlu_result.source,
                started=started,
            )
            self._persist(user_input, snapshot, response)
            return response

        if not safety.allowed:
            response = self._build_response(
                intent="UNKNOWN" if nlu_result.intent == "UNKNOWN" else nlu_result.intent,
                slots=nlu_result.slots,
                confidence=nlu_result.confidence,
                final_response=safety.fallback_response or build_fallback_response(),
                success=False,
                failure_reason=safety.reason,
                fallback=True,
                safety_decision=safety,
                nlu_source=nlu_result.source,
                started=started,
            )
            self._persist(user_input, snapshot, response)
            return response

        tool_call = nlu_result.tool_call
        if tool_call is None and capability is not None:
            tool_call = self.tool_registry.build_tool_call_by_name(
                capability.tool_name, nlu_result.slots, user_input
            )
        if tool_call is None:
            tool_call = self.tool_registry.build_tool_call(
                nlu_result.intent, nlu_result.slots, user_input
            )

        tool_result = None
        if tool_call:
            tool_result = self.tool_registry.execute(tool_call, vehicle_state)
            if tool_result.updated_vehicle_state:
                vehicle_state_store.apply_tool_updates(
                    tool_result.updated_vehicle_state, session_id
                )

        if capability is not None:
            final_response = self.capability_service.render_success(
                capability, nlu_result.slots, tool_result, vehicle_state
            )
        else:
            final_response = build_final_response(
                nlu_result.intent, user_input, tool_result, vehicle_state
            )

        response = self._build_response(
            intent=nlu_result.intent,
            slots=nlu_result.slots,
            confidence=nlu_result.confidence,
            tool_call=tool_call,
            tool_result=tool_result,
            final_response=final_response,
            success=True if tool_result is None or tool_result.success else False,
            failure_reason=None if (tool_result is None or tool_result.success) else tool_result.message,
            safety_decision=safety,
            nlu_source=nlu_result.source,
            started=started,
        )
        self._persist(user_input, snapshot, response)
        return response

    def _check_slot_clarification(self, nlu_result, capability=None) -> str | None:
        if capability is not None:
            missing = self.capability_service.missing_required(capability, nlu_result.slots)
            if not missing:
                return None
            if capability.clarification_question:
                return capability.clarification_question
            return build_slot_clarification_response(capability.tool_name, missing)

        tool_call = nlu_result.tool_call
        if tool_call is None:
            tool_call = self.tool_registry.build_tool_call(
                nlu_result.intent, nlu_result.slots, ""
            )
        if tool_call is None:
            return None

        missing = self.tool_registry.missing_clarification_fields(tool_call)
        if not missing:
            return None
        return build_slot_clarification_response(tool_call.name, missing)

    def _build_response(
        self,
        *,
        intent,
        slots,
        confidence,
        final_response: str,
        success: bool,
        started: float,
        tool_call=None,
        tool_result=None,
        failure_reason: str | None = None,
        safety_blocked: bool = False,
        fallback: bool = False,
        requires_clarification: bool = False,
        safety_decision: SafetyDecision | None = None,
        nlu_source: str = "rule_based",
    ) -> AgentRunResponse:
        latency_ms = max(1, int((time.perf_counter() - started) * 1000))
        if safety_blocked or fallback or requires_clarification:
            tool_call = None
            tool_result = None

        return AgentRunResponse(
            intent=intent,
            slots=slots,
            confidence=confidence,
            tool_call=tool_call,
            tool_result=tool_result,
            final_response=final_response,
            latency_ms=latency_ms,
            success=success,
            failure_reason=failure_reason,
            safety_blocked=safety_blocked,
            fallback=fallback,
            requires_clarification=requires_clarification,
            safety_decision=safety_decision,
            nlu_source=nlu_source,
        )

    def _persist(self, user_input: str, snapshot: dict, response: AgentRunResponse) -> None:
        self.log_repo.create_from_agent_run(user_input, snapshot, response)
