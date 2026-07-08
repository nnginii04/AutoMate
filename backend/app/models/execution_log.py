from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database import Base


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_input: Mapped[str] = mapped_column(Text, nullable=False)
    vehicle_state_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    intent: Mapped[str] = mapped_column(String(64), nullable=False)
    slots: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    tool_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    tool_arguments: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tool_result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    final_response: Mapped[str] = mapped_column(Text, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    safety_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fallback: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_clarification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
