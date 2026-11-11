"""Render one or more eval result files into a Markdown report.

Discipline: dev failures are listed in full (they are what you tune against).
Test failures are shown only as counts per variant, so the test set stays a
fair measure of generalization.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from eval.dataset import VARIANTS

HEADLINE = [
    ("pass", "종합 통과율 (모든 검사 통과)", "up"),
    ("outcome_acc", "처리 결과 정확도 (실행, 차단, 되묻기, 거절)", "up"),
    ("intent_acc", "Intent 정확도", "up"),
    ("tool_acc", "Tool 정확도 (실행이 정답인 항목)", "up"),
    ("slot_acc_given_tool", "Slot 정확도 (맞는 Tool이 실행된 항목)", "up"),
    ("unsafe_execution", "위험 요청 실행률", "down"),
    ("over_block", "과잉 차단률 (실행이 정답인데 차단)", "down"),
    ("spurious_action", "오작동 실행률 (거절, 무동작이 정답인데 실행)", "down"),
    ("clarify_recall", "되묻기 재현율 (필수 정보 누락 시)", "up"),
    ("compound_tool_coverage", "복합 발화 Tool 커버리지", "up"),
    ("raw_error_exposed", "내부 검증 에러 노출 건수", "down"),
    ("nlu_errors", "NLU 파싱, 요청 실패 건수", "down"),
    ("latency_ms_mean", "평균 지연 (ms)", "down"),
    ("latency_ms_p95", "p95 지연 (ms)", "down"),
]

VARIANT_LABELS = {
    "direct": "직접 명령",
    "colloquial": "구어체, 축약",
    "situational": "상황 발화",
    "off_command": "끄기, 중지",
    "negation": "부정, 정정",
    "compound": "복합 명령",
    "clarify": "정보 누락",
    "safety": "주행 중 위험 요청",
    "context": "상태 의존",
    "unsupported": "미지원 기능",
    "off_domain": "차량 무관",
}


def wilson(num: int, den: int, z: float = 1.96) -> tuple[float, float]:
    if den == 0:
        return (0.0, 0.0)
    p = num / den
    centre = (p + z * z / (2 * den)) / (1 + z * z / den)
    half = z * ((p * (1 - p) / den + z * z / (4 * den * den)) ** 0.5) / (1 + z * z / den)
    return (max(0.0, centre - half), min(1.0, centre + half))


def fmt_ci(value: Any) -> str:
    if not (isinstance(value, list) and len(value) == 2 and value[1]):
        return fmt(value)
    lo, hi = wilson(*value)
    return f"{fmt(value)} [95% CI {100 * lo:.0f}~{100 * hi:.0f}%]"


def fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, list) and len(value) == 2:
        num, den = value
        if den == 0:
            return "-"
        return f"{num}/{den} ({100 * num / den:.1f}%)"
    if isinstance(value, float):
        return f"{value:.3f}" if value <= 1 else f"{value:.1f}"
    return str(value)


def run_label(result: Dict[str, Any]) -> str:
    meta = result["meta"]
    label = meta["nlu_mode"]
    if meta.get("model"):
        label += f" ({meta['model']})"
    return label


def _table(header: List[str], rows: List[List[str]]) -> List[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


def render(results: List[Dict[str, Any]]) -> str:
    labels = [run_label(r) for r in results]
    first = results[0]["meta"]
    lines: List[str] = ["# AutoMate 평가 리포트", ""]
    lines.append(f"- 데이터셋: `{first.get('dataset_version', '?')}`, test sha256 `{first.get('test_sha256', '?')[:12]}…`"
                 f" (MANIFEST 일치: {'예' if first.get('test_hash_matches_manifest') else '아니오'})")
    lines.append("- 정답 기준: README의 Safety 정책 표. 현재 구현의 동작이 아니라 의도된 동작을 정답으로 둠")
    lines.append("- 차량 상태: 항목마다 중립 기본 상태(주행 70km/h, 맑음, 창문 닫힘, 정상 운전자)에 필요한 값만 덮어씀")
    lines.append("")

    lines.append("## 실행 조건")
    lines.append("")
    rows = [[run_label(r), r["meta"].get("model", "-"), r["meta"].get("base_url_host", "-"), r["meta"]["ran_at"]] for r in results]
    lines += _table(["실행", "모델", "엔드포인트", "실행 시각 (UTC)"], rows)
    lines.append("")

    for split in ("test", "dev"):
        if not all(split in r["splits"] for r in results):
            continue
        n = results[0]["splits"][split]["summary"]["n"]
        title = "핵심 지표: test (보고용, 튜닝 금지)" if split == "test" else "핵심 지표: dev (튜닝용)"
        lines += [f"## {title}, {n}개 항목", ""]
        rows = []
        for key, label, direction in HEADLINE:
            arrow = "↑" if direction == "up" else "↓"
            render_cell = fmt_ci if key in ("pass", "unsafe_execution") else fmt
            rows.append([f"{label} {arrow}"] + [render_cell(r["splits"][split]["summary"].get(key)) for r in results])
        lines += _table(["지표"] + labels, rows)
        lines.append("")

        lines += [f"### 발화 유형별 종합 통과율: {split}", "", "유형별 항목 수가 3~21개로 작아서 유형별 수치는 경향으로만 해석할 것.", ""]
        rows = []
        for variant in VARIANTS:
            cells = [fmt(r["splits"][split]["summary"]["by_variant"].get(variant, {}).get("pass")) for r in results]
            if any(c != "-" for c in cells):
                rows.append([f"{VARIANT_LABELS[variant]} (`{variant}`)"] + cells)
        lines += _table(["유형"] + labels, rows)
        lines.append("")

    for result, label in zip(results, labels):
        if "test" in result["splits"]:
            fails = [v for v in result["splits"]["test"]["verdicts"] if not v["passed"]]
            counts = Counter(v["variant"] for v in fails)
            unsafe = sum(1 for v in fails if v.get("unsafe"))
            lines += [f"## test 실패 분포: {label}", ""]
            lines.append("test 실패는 개별 발화를 열람하지 않고 유형별 개수만 기록함 (test셋 오염 방지).")
            lines.append("")
            rows = [[VARIANT_LABELS[k], str(counts[k])] for k in VARIANTS if counts.get(k)]
            lines += _table(["유형", "실패 수"], rows)
            lines.append("")
            lines.append(f"위험 요청 실행 발생: {unsafe}건")
            lines.append("")

        if "dev" in result["splits"]:
            fails = [v for v in result["splits"]["dev"]["verdicts"] if not v["passed"]]
            lines += [f"## dev 실패 상세: {label} ({len(fails)}건)", "", "<details><summary>펼치기</summary>", ""]
            rows = []
            for v in fails:
                executed = ", ".join(e["name"] for e in v["executed"]) or "-"
                rows.append([
                    f"`{v['item_id']}`",
                    v["user_input"],
                    f"{v['expected_outcome']} / {v['expected_intent'] or '-'} / {', '.join(v['expected_tools']) or '-'}",
                    f"{v['actual_outcome']} / {v['actual_intent']} / {executed}",
                    ", ".join(v["error_tags"]),
                ])
            lines += _table(["id", "발화", "기대 (결과/Intent/Tool)", "실제 (결과/Intent/Tool)", "태그"], rows)
            lines += ["", "</details>", ""]

    return "\n".join(lines).rstrip() + "\n"


def write_report(result_paths: List[Path], out_path: Path) -> Path:
    results = [json.loads(p.read_text(encoding="utf-8")) for p in result_paths]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(results), encoding="utf-8")
    return out_path
