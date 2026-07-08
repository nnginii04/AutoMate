"""Vehicle Capability Catalog service.

The :class:`CapabilityService` loads ``vehicle-capabilities.json`` and turns a
raw Korean utterance into a matched capability plus extracted slots. It is the
single source of truth that drives Intent classification, Slot extraction, Tool
selection, and Safety decisions across the agent pipeline.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.schemas import IntentType, VehicleState

CAPABILITIES_FILE = Path(__file__).resolve().parent.parent / "data" / "vehicle-capabilities.json"

_MISSING_SENTINELS = frozenset({"", "unknown", "custom", "unspecified"})


def normalize_text(text: str) -> tuple[str, str]:
    """Return (normalized, compact) forms of a Korean utterance.

    - normalized: trimmed, lower-cased, single-spaced
    - compact: normalized with all whitespace removed (spacing-tolerant match)
    """
    normalized = " ".join(text.strip().lower().split())
    compact = normalized.replace(" ", "")
    return normalized, compact


# Known destinations mapped to canonical names. Anything else is passed through.
_KNOWN_DESTINATIONS: dict[str, str] = {
    "집": "home",
    "회사": "company",
    "서울역": "Seoul Station",
    "대전역": "Daejeon Station",
    "부산역": "Busan Station",
}

_DESTINATION_STOPWORDS = frozenset(
    {"목적지", "여기", "거기", "길", "내비", "네비", "경로", "그곳", ""}
)

_DESTINATION_PATTERNS: tuple[str, ...] = (
    r"([가-힣a-z0-9]+?)(?:으로|로)가고싶",
    r"([가-힣a-z0-9]+?)까지",
    r"([가-힣a-z0-9]+?)(?:으로|로)가",
    r"([가-힣a-z0-9]+?)(?:으로|로)안내",
    r"([가-힣a-z0-9]+?)가자",
    r"([가-힣a-z0-9]+?)가줘",
    r"([가-힣a-z0-9]+?)안내",
)


def extract_destination(compact: str) -> Optional[str]:
    """Extract a destination from the compact text, or None if unclear."""
    for pattern in _DESTINATION_PATTERNS:
        match = re.search(pattern, compact)
        if match:
            token = match.group(1).strip()
            if token in _DESTINATION_STOPWORDS:
                continue
            return _KNOWN_DESTINATIONS.get(token, token)

    for keyword, canonical in _KNOWN_DESTINATIONS.items():
        if keyword in compact:
            return canonical

    return None


def extract_contact(compact: str) -> Optional[str]:
    """Extract a contact name from the compact text, or None if unclear."""
    if "엄마" in compact:
        return "mother"
    if "아빠" in compact:
        return "father"
    for suffix in ("한테", "에게", "한대"):
        match = re.search(rf"([가-힣]{{2,6}}){suffix}", compact)
        if match:
            return match.group(1)
    return None


def extract_temperature(compact: str) -> Optional[int]:
    match = re.search(r"(\d{1,2})\s*도", compact)
    if match:
        return int(match.group(1))
    return None


@dataclass(frozen=True)
class Capability:
    capability_id: str
    category: str
    intent: IntentType
    tool_name: str
    display_name: str
    description: str
    example_utterances: List[str]
    match_keywords: List[str]
    priority: int
    confidence: float
    required_slots: List[str]
    optional_slots: List[str]
    default_arguments: Dict[str, Any]
    allowed_while_driving: bool
    risk_level: str
    state_updates: Dict[str, Any]
    success_response_template: Optional[str]
    clarification_question: Optional[str]
    blocked_response: Optional[str]


@dataclass
class CapabilityMatch:
    capability: Capability
    slots: Dict[str, Any] = field(default_factory=dict)
    missing_required: List[str] = field(default_factory=list)

    @property
    def intent(self) -> IntentType:
        return self.capability.intent

    @property
    def tool_name(self) -> str:
        return self.capability.tool_name

    @property
    def confidence(self) -> float:
        return self.capability.confidence

    @property
    def capability_id(self) -> str:
        return self.capability.capability_id


@lru_cache
def _load_capabilities() -> tuple[Capability, ...]:
    with CAPABILITIES_FILE.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    capabilities: List[Capability] = []
    for item in payload.get("capabilities", []):
        capabilities.append(
            Capability(
                capability_id=item["capability_id"],
                category=item["category"],
                intent=item["intent"],
                tool_name=item["tool_name"],
                display_name=item.get("display_name", item["capability_id"]),
                description=item.get("description", ""),
                example_utterances=list(item.get("example_utterances", [])),
                match_keywords=list(item.get("match_keywords", [])),
                priority=int(item.get("priority", 0)),
                confidence=float(item.get("confidence", 0.9)),
                required_slots=list(item.get("required_slots", [])),
                optional_slots=list(item.get("optional_slots", [])),
                default_arguments=dict(item.get("default_arguments", {})),
                allowed_while_driving=bool(item.get("allowed_while_driving", True)),
                risk_level=item.get("risk_level", "none"),
                state_updates=dict(item.get("state_updates", {})),
                success_response_template=item.get("success_response_template"),
                clarification_question=item.get("clarification_question"),
                blocked_response=item.get("blocked_response"),
            )
        )
    return tuple(capabilities)


class CapabilityService:
    """Loads the capability catalog and matches utterances to capabilities."""

    def __init__(self, capabilities: Optional[tuple[Capability, ...]] = None) -> None:
        self._capabilities = capabilities or _load_capabilities()
        self._by_id = {cap.capability_id: cap for cap in self._capabilities}

    def all(self) -> tuple[Capability, ...]:
        return self._capabilities

    def get(self, capability_id: Optional[str]) -> Optional[Capability]:
        if not capability_id:
            return None
        return self._by_id.get(capability_id)

    def match(
        self, user_input: str, vehicle_state: Optional[VehicleState] = None
    ) -> Optional[CapabilityMatch]:
        _, compact = normalize_text(user_input)
        if not compact:
            return None

        best: Optional[tuple[int, int, float, Capability]] = None
        for cap in self._capabilities:
            matched = [kw for kw in cap.match_keywords if kw and kw in compact]
            if not matched:
                continue
            score = (cap.priority, max(len(kw) for kw in matched), cap.confidence, cap)
            if best is None or score[:3] > best[:3]:
                best = score

        if best is None:
            return None

        capability = best[3]
        slots = self._resolve_slots(capability, compact, vehicle_state)
        missing = self.missing_required(capability, slots)
        return CapabilityMatch(capability=capability, slots=slots, missing_required=missing)

    def _resolve_slots(
        self,
        capability: Capability,
        compact: str,
        vehicle_state: Optional[VehicleState],
    ) -> Dict[str, Any]:
        slots: Dict[str, Any] = dict(capability.default_arguments)

        if capability.intent == "SET_NAVIGATION":
            destination = extract_destination(compact)
            if destination:
                slots["destination"] = destination

        elif capability.intent == "MAKE_CALL":
            contact = extract_contact(compact)
            if contact:
                slots["contact"] = contact

        elif capability.intent == "CONTROL_CLIMATE":
            temperature = extract_temperature(compact)
            if temperature is not None:
                slots["temperature"] = temperature
                slots["target_temperature"] = temperature
            if (
                slots.get("mode") == "recirculation"
                and vehicle_state is not None
                and vehicle_state.window_status == "open"
            ):
                slots["close_window"] = True

        return slots

    @staticmethod
    def missing_required(capability: Capability, slots: Dict[str, Any]) -> List[str]:
        missing: List[str] = []
        for slot in capability.required_slots:
            value = slots.get(slot)
            if value is None:
                missing.append(slot)
                continue
            if isinstance(value, str) and value.strip().lower() in _MISSING_SENTINELS:
                missing.append(slot)
        return missing

    @staticmethod
    def render_success(
        capability: Capability,
        slots: Dict[str, Any],
        tool_result,
        vehicle_state: VehicleState,
    ) -> str:
        message = tool_result.message if tool_result and tool_result.message else ""
        template = capability.success_response_template
        if not template:
            return message or "요청을 처리했습니다."

        context: Dict[str, Any] = {"message": message}
        context.update(vehicle_state.model_dump())
        context.update(slots)
        try:
            return template.format(**context)
        except (KeyError, IndexError, ValueError):
            return message or template


@lru_cache
def get_capability_service() -> CapabilityService:
    return CapabilityService()
