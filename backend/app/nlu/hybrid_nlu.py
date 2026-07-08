"""Hybrid NLU that prefers LLM function calling with rule-based fallback."""

from __future__ import annotations

import logging
from typing import Optional

from app.nlu.llm_function_calling import LLMFunctionCallingNLU, LLMParseError, LLMRequestError
from app.nlu.rule_based_nlu import RuleBasedNLU
from app.schemas import NLUResult, VehicleState

logger = logging.getLogger(__name__)


class HybridNLU:
    def __init__(
        self,
        rule_based: RuleBasedNLU,
        llm_nlu: Optional[LLMFunctionCallingNLU] = None,
        *,
        llm_enabled: bool = False,
    ) -> None:
        self.rule_based = rule_based
        self.llm_nlu = llm_nlu
        self.llm_enabled = llm_enabled

    @property
    def llm_available(self) -> bool:
        return self.llm_enabled and self.llm_nlu is not None

    def parse(self, user_input: str, vehicle_state: Optional[VehicleState] = None) -> NLUResult:
        state = vehicle_state or VehicleState()

        if self.llm_available:
            try:
                return self.llm_nlu.parse(user_input, state)
            except (LLMParseError, LLMRequestError) as exc:
                logger.warning("LLM NLU failed, falling back to rule-based NLU: %s", exc)
                fallback = self.rule_based.parse(user_input, state)
                fallback.parse_error = str(exc)
                return fallback

        return self.rule_based.parse(user_input, state)
