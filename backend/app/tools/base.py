from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Generic, Type, TypeVar

from pydantic import BaseModel, ValidationError

from app.schemas import IntentType, ToolResult, VehicleState

TArgs = TypeVar("TArgs", bound=BaseModel)


class VehicleTool(ABC, Generic[TArgs]):
    """Common interface for all in-vehicle executable tools."""

    name: ClassVar[str]
    description: ClassVar[str]
    argument_schema: ClassVar[Type[BaseModel]]
    supported_intents: ClassVar[tuple[IntentType, ...]]

    @abstractmethod
    def execute(self, arguments: TArgs, vehicle_state: VehicleState) -> ToolResult:
        """Run tool logic with validated arguments."""

    def build_arguments(self, slots: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Map NLU slots to raw tool arguments before schema validation."""
        return dict(slots)

    def missing_clarification_fields(self, arguments: Dict[str, Any]) -> list[str]:
        """Return argument field names that need explicit user clarification."""
        return []

    def run(self, raw_arguments: Dict[str, Any], vehicle_state: VehicleState) -> ToolResult:
        """Validate arguments and execute, returning a standard ToolResult."""
        try:
            validated = self.argument_schema.model_validate(raw_arguments)
        except ValidationError as exc:
            return self._failure(f"Invalid tool arguments: {self._format_validation_error(exc)}")

        try:
            result = self.execute(validated, vehicle_state)
            if result.tool_name is None:
                result.tool_name = self.name
            return result
        except Exception as exc:  # noqa: BLE001 — tool boundary catches all execution errors
            return self._failure(f"Tool execution failed: {exc}")

    def _failure(self, message: str) -> ToolResult:
        return ToolResult(success=False, tool_name=self.name, message=message)

    @staticmethod
    def _format_validation_error(exc: ValidationError) -> str:
        parts = []
        for err in exc.errors():
            loc = ".".join(str(item) for item in err.get("loc", ()))
            parts.append(f"{loc}: {err.get('msg', 'invalid')}")
        return "; ".join(parts) if parts else str(exc)
