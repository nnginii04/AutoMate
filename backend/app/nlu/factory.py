"""Factory helpers for NLU provider selection."""

from __future__ import annotations

from app.config import Settings, get_settings
from app.nlu.hybrid_nlu import HybridNLU
from app.nlu.llm_function_calling import HttpxOpenAIClient, LLMFunctionCallingNLU
from app.nlu.rule_based_nlu import RuleBasedNLU
from app.tools import ToolRegistry


def create_nlu(
    tool_registry: ToolRegistry | None = None,
    settings: Settings | None = None,
) -> HybridNLU:
    registry = tool_registry or ToolRegistry()
    config = settings or get_settings()

    llm_nlu = None
    if config.llm_available:
        client = HttpxOpenAIClient(
            api_key=config.openai_api_key or "",
            base_url=config.openai_base_url,
        )
        llm_nlu = LLMFunctionCallingNLU(
            tool_registry=registry,
            client=client,
            model=config.openai_model,
        )

    return HybridNLU(
        rule_based=RuleBasedNLU(),
        llm_nlu=llm_nlu,
        llm_enabled=config.llm_enabled,
    )
