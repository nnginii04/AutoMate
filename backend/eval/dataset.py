"""Evaluation dataset schema and loading.

Each line in ``eval/data/<split>.jsonl`` is one :class:`EvalItem`.
Labels describe the *desired* behavior under the Safety policy in README.md,
not whatever the current implementation happens to do.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

DATA_DIR = Path(__file__).resolve().parent / "data"
MANIFEST_PATH = DATA_DIR / "MANIFEST.json"

Outcome = Literal["EXECUTE", "BLOCK", "CLARIFY", "FALLBACK", "NO_ACTION", "TOOL_FAIL"]

VARIANTS = (
    "direct",        # 표준 명령형
    "colloquial",    # 구어체, 축약, 조사 생략, 방언
    "situational",   # 상황 발화 (명령 없이 상태만 말함)
    "off_command",   # 끄기, 중지 명령
    "negation",      # 금지, 부정, 정정
    "compound",      # 한 발화에 여러 기능
    "clarify",       # 필수 정보 누락
    "safety",        # 주행 중 위험 요청
    "context",       # 차량 상태에 따라 정답이 달라지는 요청
    "unsupported",   # Tool 범위 밖 기능
    "off_domain",    # 차량과 무관한 발화
)


class ToolSpec(BaseModel):
    """Expected or forbidden tool call.

    ``name`` may be ``"*"`` (any tool). ``args`` maps a key to allowed values;
    a key like ``"value|status"`` passes if any of those keys holds an allowed value.
    """

    name: str
    args: Dict[str, List[Any]] = Field(default_factory=dict)


class Expected(BaseModel):
    outcome: Outcome
    intent: Optional[str] = None
    tools: List[ToolSpec] = Field(default_factory=list)
    accept: List[Outcome] = Field(default_factory=list)


class EvalItem(BaseModel):
    id: str
    split: str
    group: str
    variant: str
    family: str
    user_input: str
    state: Dict[str, Any] = Field(default_factory=dict)
    expected: Expected
    safety_critical: bool = False
    forbid: List[ToolSpec] = Field(default_factory=list)
    note: Optional[str] = None

    @model_validator(mode="after")
    def _check(self) -> "EvalItem":
        if self.variant not in VARIANTS:
            raise ValueError(f"{self.id}: unknown variant {self.variant}")
        if self.expected.outcome == "EXECUTE" and not self.expected.tools:
            raise ValueError(f"{self.id}: EXECUTE needs expected tools")
        if self.safety_critical and not self.forbid:
            raise ValueError(f"{self.id}: safety_critical item needs forbid specs")
        return self


def split_path(split: str) -> Path:
    return DATA_DIR / f"{split}.jsonl"


def load_split(split: str) -> List[EvalItem]:
    path = split_path(split)
    if not path.exists():
        raise FileNotFoundError(f"No eval split at {path}")
    items: List[EvalItem] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(EvalItem.model_validate(json.loads(line)))
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"{path.name}:{line_no}: {exc}") from exc
    return items


def file_sha256(path: Path) -> str:
    """SHA-256 over LF-normalized bytes, so a CRLF checkout on Windows does not break the freeze."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_manifest() -> Dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
