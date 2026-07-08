from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database import Base


class ScenarioRunLog(Base):
    __tablename__ = "scenario_run_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    scenario_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    scenario_name: Mapped[str] = mapped_column(String(256), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    passed_intent: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    passed_tool: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    passed_result: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    passed_safety: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    expected_intent: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    expected_tool: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    expected_result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    actual_intent: Mapped[str] = mapped_column(String(64), nullable=False)
    actual_tool: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    checks: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    agent_response: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
