"""Run eval items through the real AgentService pipeline.

The agent runs end to end (NLU, Safety, Tool execution) against an in-memory
SQLite database so evaluation never touches the development log database.
"""

from __future__ import annotations

import platform
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registers tables on Base.metadata)
from app.config import Settings
from app.database import Base

# app.services must load before app.nlu: rule_based_nlu -> app.services -> agent_service -> app.nlu
# is a circular chain that only resolves in this order (see eval/README.md, known issues).
from app.services.agent_service import AgentService  # isort: skip
from app.nlu import HttpxOpenAIClient, HybridNLU, LLMFunctionCallingNLU, LLMParseError, LLMRequestError, RuleBasedNLU
from app.schemas import AgentRunRequest, NLUResult, VehicleState
from app.services.vehicle_service import vehicle_state_store
from app.tools import ToolRegistry

from eval.dataset import EvalItem
from eval.scoring import Verdict, score_item

NLU_MODES = ("rule", "llm", "hybrid")

# Neutral starting state. Every item overrides only what its scenario needs, so
# results never depend on the demo defaults in vehicle_service (rain, open window).
BASE_STATE: Dict[str, Any] = {
    "speed": 70,
    "speed_limit": 80,
    "road_name": "대전 유성대로",
    "road_type": "urban",
    "is_school_zone": False,
    "is_driving": True,
    "driver_status": "normal",
    "weather": "sunny",
    "window_status": "closed",
    "indoor_temperature": 22,
    "outdoor_temperature": 15,
    "battery_level": 68,
    "fuel_level": 42,
    "media_status": "off",
    "media_volume": 50,
    "air_conditioner_status": "off",
    "display_brightness": "medium",
    "navigation_active": False,
}


class RecordingNLU:
    """Wraps an NLU to remember the last parse error for reporting."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.last_error: Optional[str] = None

    def parse(self, user_input: str, vehicle_state: Optional[VehicleState] = None) -> NLUResult:
        self.last_error = None
        result = self.inner.parse(user_input, vehicle_state)
        self.last_error = result.parse_error
        return result


class PureLLMNLU:
    """LLM only. Parse or request errors become UNKNOWN instead of a rule fallback."""

    def __init__(self, llm: LLMFunctionCallingNLU) -> None:
        self.llm = llm

    def parse(self, user_input: str, vehicle_state: Optional[VehicleState] = None) -> NLUResult:
        try:
            return self.llm.parse(user_input, vehicle_state or VehicleState())
        except (LLMParseError, LLMRequestError) as exc:
            return NLUResult(intent="UNKNOWN", slots={}, confidence=0.0, source="llm", parse_error=str(exc))


def build_nlu(mode: str, registry: ToolRegistry, settings: Settings, model: Optional[str], base_url: Optional[str]) -> Tuple[Any, Dict[str, Any]]:
    if mode not in NLU_MODES:
        raise ValueError(f"nlu mode must be one of {NLU_MODES}")
    meta: Dict[str, Any] = {"nlu_mode": mode}
    rule = RuleBasedNLU()
    if mode == "rule":
        return HybridNLU(rule_based=rule, llm_nlu=None, llm_enabled=False), meta

    api_key = (settings.openai_api_key or "").strip()
    resolved_base = (base_url or settings.openai_base_url).rstrip("/")
    is_local = urlparse(resolved_base).hostname in ("localhost", "127.0.0.1", "::1")
    if not api_key and not is_local:
        raise SystemExit("LLM 모드에는 OPENAI_API_KEY가 필요합니다 (backend/.env 또는 환경 변수).")
    resolved_model = model or settings.openai_model
    client = HttpxOpenAIClient(api_key=api_key or "local", base_url=resolved_base)
    llm = LLMFunctionCallingNLU(tool_registry=registry, client=client, model=resolved_model)
    meta.update({"model": resolved_model, "base_url_host": urlparse(resolved_base).hostname})
    if mode == "llm":
        return PureLLMNLU(llm), meta
    return HybridNLU(rule_based=rule, llm_nlu=llm, llm_enabled=True), meta


def run_items(
    items: List[EvalItem],
    mode: str = "rule",
    *,
    settings: Optional[Settings] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    progress: bool = False,
) -> Tuple[List[Verdict], Dict[str, Any]]:
    settings = settings or Settings()
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    registry = ToolRegistry()
    nlu, meta = build_nlu(mode, registry, settings, model, base_url)
    recorder = RecordingNLU(nlu)
    agent = AgentService(session, nlu=recorder, tool_registry=registry)

    verdicts: List[Verdict] = []
    started = time.perf_counter()
    try:
        for idx, item in enumerate(items, start=1):
            vehicle_state_store.reset()
            state = {**BASE_STATE, **item.state}
            response = agent.run(AgentRunRequest(user_input=item.user_input, vehicle_state=state))
            verdict = score_item(item, response)
            verdict.nlu_error = recorder.last_error
            verdicts.append(verdict)
            if progress:
                mark = "PASS" if verdict.passed else "FAIL"
                print(f"[{idx:3d}/{len(items)}] {mark} {item.id}  {item.user_input}")
    finally:
        session.close()
        vehicle_state_store.reset()

    meta.update(
        {
            "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "wall_seconds": round(time.perf_counter() - started, 2),
            "python": platform.python_version(),
        }
    )
    return verdicts, meta
