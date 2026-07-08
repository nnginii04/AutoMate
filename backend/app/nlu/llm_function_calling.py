"""OpenAI function-calling based NLU for in-vehicle agent commands."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Protocol

import httpx

from app.schemas import NLUResult, ToolCall, VehicleState
from app.tools import ToolRegistry

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are AutoMate, an in-vehicle AI assistant.
Analyze the driver's utterance together with the current vehicle_state snapshot.
Select at most one simulation tool via function calling when the request maps to a vehicle action.
All tools are simulation-only and must never claim to control real vehicle hardware.

Guidelines:
- Prefer a tool call when the user clearly wants climate, navigation, media, calls, status, nearby places, settings, or schedule.
- Populate tool arguments with concrete values inferred from the utterance and context.
- Leave required fields empty (do not guess) when the user did not specify destination, contact, etc.
- If the request is unrelated to in-vehicle assistance, do not call any tool.
"""


class LLMClient(Protocol):
    def chat_completions(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        ...


class LLMParseError(Exception):
    """Raised when the LLM response cannot be parsed into NLU output."""


class LLMRequestError(Exception):
    """Raised when the LLM HTTP request fails."""


class HttpxOpenAIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def chat_completions(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                    "temperature": 0.1,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise LLMRequestError(str(exc)) from exc


class LLMFunctionCallingNLU:
    """Uses OpenAI function calling to infer intent, slots, and tool_call candidates."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        client: LLMClient,
        model: str,
    ) -> None:
        self.tool_registry = tool_registry
        self.client = client
        self.model = model

    def parse(self, user_input: str, vehicle_state: VehicleState) -> NLUResult:
        text = user_input.strip()
        if not text:
            return NLUResult(intent="UNKNOWN", slots={}, confidence=0.0, source="llm")

        tools = self.tool_registry.to_openai_tools()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "user_input": text,
                        "vehicle_state": vehicle_state.to_snapshot(),
                    },
                    ensure_ascii=False,
                ),
            },
        ]

        payload = self.client.chat_completions(model=self.model, messages=messages, tools=tools)
        return self._parse_completion(payload)

    def _parse_completion(self, payload: Dict[str, Any]) -> NLUResult:
        try:
            choices = payload.get("choices") or []
            if not choices:
                raise LLMParseError("LLM response missing choices")

            message = choices[0].get("message") or {}
            tool_calls = message.get("tool_calls") or []

            if not tool_calls and message.get("function_call"):
                tool_calls = [{"function": message["function_call"]}]

            if not tool_calls:
                return NLUResult(intent="UNKNOWN", slots={}, confidence=0.45, source="llm")

            function = tool_calls[0].get("function") or {}
            tool_name = function.get("name")
            if not tool_name:
                raise LLMParseError("LLM tool call missing function name")

            raw_arguments = function.get("arguments", "{}")
            if isinstance(raw_arguments, str):
                arguments = json.loads(raw_arguments or "{}")
            elif isinstance(raw_arguments, dict):
                arguments = raw_arguments
            else:
                raise LLMParseError("LLM tool arguments must be JSON object")

            if not isinstance(arguments, dict):
                raise LLMParseError("LLM tool arguments must be a JSON object")

            intent = self.tool_registry.intent_from_tool_name(tool_name)
            if intent is None:
                raise LLMParseError(f"Unknown tool from LLM: {tool_name}")

            tool_call = self.tool_registry.build_tool_call_from_llm(tool_name, arguments)
            if tool_call is None:
                raise LLMParseError(f"Failed to build tool call for: {tool_name}")

            return NLUResult(
                intent=intent,
                slots=dict(tool_call.arguments),
                confidence=0.9,
                tool_call=tool_call,
                source="llm",
            )
        except json.JSONDecodeError as exc:
            raise LLMParseError(f"Invalid JSON in LLM tool arguments: {exc}") from exc
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMParseError(f"Malformed LLM response: {exc}") from exc
