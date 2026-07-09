from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.schemas import IntentType, ToolCall, ToolResult, VehicleState
from app.tools.base import VehicleTool
from app.tools.bootstrap import build_default_tools

_SIMULATION_SUFFIX = " (simulation only — does not control real vehicle hardware)"


class ToolRegistry:
    """Central registry for vehicle tool discovery, validation, and execution."""

    def __init__(self) -> None:
        self._tools: Dict[str, VehicleTool] = {}
        self._intent_index: Dict[IntentType, List[str]] = {}
        for tool in build_default_tools():
            self.register(tool)

    def register(self, tool: VehicleTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool
        for intent in tool.supported_intents:
            self._intent_index.setdefault(intent, [])
            if tool.name not in self._intent_index[intent]:
                self._intent_index[intent].append(tool.name)

    def get(self, name: str) -> Optional[VehicleTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[VehicleTool]:
        return list(self._tools.values())

    def intent_from_tool_name(self, tool_name: str) -> Optional[IntentType]:
        tool = self._tools.get(tool_name)
        if not tool or not tool.supported_intents:
            return None
        return tool.supported_intents[0]

    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """Export registered tools as OpenAI function-calling schemas."""
        openai_tools: List[Dict[str, Any]] = []
        for tool in self.list_tools():
            parameters = tool.argument_schema.model_json_schema()
            parameters.pop("title", None)
            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": f"{tool.description}{_SIMULATION_SUFFIX}",
                        "parameters": parameters,
                    },
                }
            )
        return openai_tools

    def missing_clarification_fields(self, tool_call: ToolCall) -> List[str]:
        tool = self._tools.get(tool_call.name)
        if not tool:
            return []
        return tool.missing_clarification_fields(tool_call.arguments)

    def build_tool_call_from_llm(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[ToolCall]:
        tool = self._tools.get(tool_name)
        if not tool:
            return None

        try:
            validated = tool.argument_schema.model_validate(arguments)
            return ToolCall(name=tool_name, arguments=validated.model_dump())
        except ValidationError:
            return ToolCall(name=tool_name, arguments=arguments)

    def resolve_tool_name(self, intent: IntentType, slots: Dict[str, Any]) -> Optional[str]:
        if intent == "UNKNOWN":
            return None

        candidates = self._intent_index.get(intent, [])
        if not candidates:
            return None

        if intent == "CHANGE_VEHICLE_SETTING":
            return "changeVehicleSetting"

        if intent == "CHECK_VEHICLE_STATUS":
            return "checkVehicleStatus"

        if intent == "CHECK_ROAD_CONTEXT":
            return "checkRoadContext"

        return candidates[0]

    def build_tool_call(
        self,
        intent: IntentType,
        slots: Dict[str, Any],
        user_input: str,
    ) -> Optional[ToolCall]:
        tool_name = self.resolve_tool_name(intent, slots)
        if not tool_name:
            return None

        tool = self._tools.get(tool_name)
        if not tool:
            return None

        raw_arguments = tool.build_arguments(slots, user_input)

        try:
            validated = tool.argument_schema.model_validate(raw_arguments)
            arguments = validated.model_dump()
        except ValidationError:
            # Keep raw args; execute() will return standardized validation failure.
            arguments = raw_arguments

        return ToolCall(name=tool_name, arguments=arguments)

    def build_tool_call_by_name(
        self,
        tool_name: str,
        slots: Dict[str, Any],
        user_input: str,
    ) -> Optional[ToolCall]:
        """Build a validated tool call for an explicit tool name (capability path)."""
        tool = self._tools.get(tool_name)
        if not tool:
            return None

        raw_arguments = tool.build_arguments(slots, user_input)
        try:
            validated = tool.argument_schema.model_validate(raw_arguments)
            arguments = validated.model_dump()
        except ValidationError:
            arguments = raw_arguments

        return ToolCall(name=tool_name, arguments=arguments)

    def execute(self, tool_call: ToolCall, vehicle_state: VehicleState) -> ToolResult:
        tool = self._tools.get(tool_call.name)
        if not tool:
            return ToolResult(
                success=False,
                tool_name=tool_call.name,
                message=f"Unknown tool: {tool_call.name}",
            )
        return tool.run(tool_call.arguments, vehicle_state)
