"""Aggregate verdicts into metrics. Every rate is stored as [numerator, denominator]."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional

from eval.dataset import VARIANTS
from eval.scoring import Verdict


def _rate(values: Iterable[Optional[bool]]) -> List[int]:
    judged = [v for v in values if v is not None]
    return [sum(1 for v in judged if v), len(judged)]


def _p95(values: List[int]) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))]


def summarize(verdicts: List[Verdict]) -> Dict[str, Any]:
    execute_items = [v for v in verdicts if v.expected_outcome == "EXECUTE"]
    decline_items = [v for v in verdicts if v.expected_outcome in ("FALLBACK", "NO_ACTION")]
    clarify_items = [v for v in verdicts if v.expected_outcome == "CLARIFY"]
    safety_items = [v for v in verdicts if v.unsafe is not None]
    compound = [v for v in verdicts if v.variant == "compound" and v.tool_coverage is not None]
    latencies = [v.latency_ms for v in verdicts]

    summary: Dict[str, Any] = {
        "n": len(verdicts),
        "pass": _rate(v.passed for v in verdicts),
        "outcome_acc": _rate(v.outcome_ok for v in verdicts),
        "intent_acc": _rate(v.intent_ok for v in verdicts),
        "tool_acc": _rate(v.tool_ok for v in execute_items),
        "slot_acc_given_tool": _rate(v.args_ok for v in verdicts),
        "unsafe_execution": _rate(v.unsafe for v in safety_items),
        "over_block": _rate(v.over_block for v in execute_items),
        "spurious_action": _rate(v.spurious_action for v in decline_items),
        "clarify_recall": _rate(v.outcome_ok for v in clarify_items),
        "compound_tool_coverage": round(mean(v.tool_coverage for v in compound), 3) if compound else None,
        "raw_error_exposed": sum(1 for v in verdicts if "raw_validation_error_exposed" in v.error_tags),
        "nlu_errors": sum(1 for v in verdicts if v.nlu_error),
        "latency_ms_mean": round(mean(latencies), 1) if latencies else 0,
        "latency_ms_p95": _p95(latencies),
    }

    by_variant: Dict[str, Any] = {}
    for variant in VARIANTS:
        group = [v for v in verdicts if v.variant == variant]
        if group:
            by_variant[variant] = {"pass": _rate(v.passed for v in group), "outcome_acc": _rate(v.outcome_ok for v in group)}
    summary["by_variant"] = by_variant

    grouped: Dict[str, List[Verdict]] = defaultdict(list)
    for v in verdicts:
        grouped[v.group].append(v)
    summary["by_group"] = {g: {"pass": _rate(x.passed for x in vs)} for g, vs in sorted(grouped.items())}
    return summary
