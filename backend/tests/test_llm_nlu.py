import json

import pytest

from app.config import Settings
from app.nlu import HybridNLU, LLMFunctionCallingNLU, RuleBasedNLU
from app.schemas import VehicleState
from app.tools import ToolRegistry


class MockLLMClient:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.last_request = None

    def chat_completions(self, *, model, messages, tools):
        self.last_request = {"model": model, "messages": messages, "tools": tools}
        return self.payload


def _climate_tool_payload():
    return {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "setClimate",
                                "arguments": json.dumps({"temperature": 26, "mode": "heating"}),
                            }
                        }
                    ]
                }
            }
        ]
    }


def test_tool_registry_exports_openai_schemas():
    registry = ToolRegistry()
    tools = registry.to_openai_tools()
    names = {item["function"]["name"] for item in tools}
    assert names == {
        "setClimate",
        "setNavigation",
        "playMedia",
        "makeCall",
        "checkVehicleStatus",
        "checkRoadContext",
        "findNearbyPlace",
        "changeVehicleSetting",
        "readSchedule",
    }
    for item in tools:
        assert "simulation only" in item["function"]["description"]
        assert item["function"]["parameters"]["type"] == "object"


def test_llm_nlu_parses_tool_call():
    registry = ToolRegistry()
    client = MockLLMClient(_climate_tool_payload())
    nlu = LLMFunctionCallingNLU(registry, client, model="gpt-4o-mini")

    result = nlu.parse("실내 온도 좀 올려줘", VehicleState(is_driving=True, speed=60))

    assert result.source == "llm"
    assert result.intent == "CONTROL_CLIMATE"
    assert result.tool_call is not None
    assert result.tool_call.name == "setClimate"
    assert result.tool_call.arguments["temperature"] == 26
    assert len(client.last_request["tools"]) == 9


def test_llm_nlu_parse_failure_raises():
    registry = ToolRegistry()
    client = MockLLMClient({"choices": [{"message": {"tool_calls": [{"function": {"name": "setClimate", "arguments": "not-json"}}]}}]})
    nlu = LLMFunctionCallingNLU(registry, client, model="gpt-4o-mini")

    with pytest.raises(Exception):
        nlu._parse_completion(client.payload)


def test_hybrid_nlu_uses_rule_based_when_disabled():
    registry = ToolRegistry()
    client = MockLLMClient(_climate_tool_payload())
    llm_nlu = LLMFunctionCallingNLU(registry, client, model="gpt-4o-mini")
    hybrid = HybridNLU(RuleBasedNLU(), llm_nlu, llm_enabled=False)

    result = hybrid.parse("나 좀 추워", VehicleState())
    assert result.source == "rule_based"
    assert result.intent == "CONTROL_CLIMATE"


def test_hybrid_nlu_falls_back_on_parse_error():
    registry = ToolRegistry()
    client = MockLLMClient(
        {"choices": [{"message": {"tool_calls": [{"function": {"name": "setClimate", "arguments": "{"}}]}}]}
    )
    llm_nlu = LLMFunctionCallingNLU(registry, client, model="gpt-4o-mini")
    hybrid = HybridNLU(RuleBasedNLU(), llm_nlu, llm_enabled=True)

    result = hybrid.parse("나 좀 추워", VehicleState())
    assert result.source == "rule_based"
    assert result.intent == "CONTROL_CLIMATE"
    assert result.parse_error is not None


def test_hybrid_nlu_uses_llm_when_enabled():
    registry = ToolRegistry()
    client = MockLLMClient(_climate_tool_payload())
    llm_nlu = LLMFunctionCallingNLU(registry, client, model="gpt-4o-mini")
    hybrid = HybridNLU(RuleBasedNLU(), llm_nlu, llm_enabled=True)

    result = hybrid.parse("실내 온도 좀 올려줘", VehicleState())
    assert result.source == "llm"
    assert result.tool_call is not None


def test_registry_missing_clarification_fields():
    registry = ToolRegistry()
    from app.schemas import ToolCall

    missing = registry.missing_clarification_fields(
        ToolCall(name="makeCall", arguments={"contact": "unknown", "hands_free": True})
    )
    assert missing == ["contact"]


def test_settings_llm_available_requires_key():
    disabled = Settings(llm_enabled=False, openai_api_key="sk-test")
    assert disabled.llm_available is False

    enabled = Settings(llm_enabled=True, openai_api_key="sk-test")
    assert enabled.llm_available is True

    empty_key = Settings(llm_enabled=True, openai_api_key="")
    assert empty_key.llm_available is False
