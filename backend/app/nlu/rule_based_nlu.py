"""Rule-based NLU driven by the Vehicle Capability Catalog.

This classifier no longer hard-codes per-utterance keyword rules. Instead it
delegates to :class:`~app.services.capability_service.CapabilityService`, which
matches the utterance against the capability catalog and extracts slots. The
public surface (``RuleBasedNLU``, ``normalize_text``) is preserved for backward
compatibility with the rest of the pipeline and the test-suite.
"""

from __future__ import annotations

from typing import Optional

from app.schemas import NLUResult, VehicleState
from app.services.capability_service import (
    CapabilityService,
    extract_temperature,
    get_capability_service,
    normalize_text,
)

__all__ = ["RuleBasedNLU", "normalize_text", "extract_temperature"]


class RuleBasedNLU:
    """Capability-catalog backed intent classifier with vehicle context."""

    def __init__(self, capability_service: Optional[CapabilityService] = None) -> None:
        self.capability_service = capability_service or get_capability_service()

    def parse(self, user_input: str, vehicle_state: Optional[VehicleState] = None) -> NLUResult:
        _, compact = normalize_text(user_input)
        if not compact:
            return NLUResult(intent="UNKNOWN", slots={}, confidence=0.0)

        match = self.capability_service.match(user_input, vehicle_state)
        if match is None:
            return NLUResult(intent="UNKNOWN", slots={}, confidence=0.35)

        return NLUResult(
            intent=match.intent,
            slots=match.slots,
            confidence=match.confidence,
            capability_id=match.capability_id,
        )
