"""AutoMate evaluation CLI.

Examples (run from backend/):
    python -m eval run --nlu rule
    python -m eval run --nlu llm --model gpt-4o-mini
    python -m eval run --nlu llm --model qwen2.5:3b --base-url http://localhost:11434/v1
    python -m eval report eval/results/rule.json eval/results/llm-gpt-4o-mini.json --out eval/reports/compare.md
    python -m eval stats
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from eval.dataset import DATA_DIR, file_sha256, load_manifest, load_split, split_path
from eval.metrics import summarize
from eval.report import write_report
from eval.runner import NLU_MODES, run_items

HERE = Path(__file__).resolve().parent


def _default_out(mode: str, model: str | None) -> Path:
    name = mode if not model else f"{mode}-{re.sub(r'[^A-Za-z0-9._-]+', '_', model)}"
    return HERE / "results" / f"{name}.json"


def cmd_run(args: argparse.Namespace) -> None:
    manifest = load_manifest()
    test_hash = file_sha256(split_path("test"))
    matches = test_hash == manifest["files"]["test.jsonl"]["sha256"]
    if not matches:
        print("경고: test.jsonl이 MANIFEST의 고정 해시와 다릅니다. 보고용 수치로 쓰지 마세요.")

    payload = {"meta": {}, "splits": {}}
    for split in args.split:
        items = load_split(split)
        if args.limit:
            items = items[: args.limit]
        verdicts, meta = run_items(items, args.nlu, model=args.model, base_url=args.base_url, progress=args.progress)
        payload["meta"] = meta
        payload["splits"][split] = {"summary": summarize(verdicts), "verdicts": [v.to_dict() for v in verdicts]}
        s = payload["splits"][split]["summary"]
        print(f"[{split}] pass {s['pass'][0]}/{s['pass'][1]}  unsafe {s['unsafe_execution'][0]}/{s['unsafe_execution'][1]}")

    payload["meta"].update(
        {
            "dataset_version": manifest["version"],
            "test_sha256": test_hash,
            "test_hash_matches_manifest": matches,
            "limit": args.limit,
        }
    )
    out = Path(args.out) if args.out else _default_out(args.nlu, args.model)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"saved {out}")


def cmd_report(args: argparse.Namespace) -> None:
    out = write_report([Path(p) for p in args.results], Path(args.out))
    print(f"saved {out}")


def cmd_stats(_: argparse.Namespace) -> None:
    for path in sorted(DATA_DIR.glob("*.jsonl")):
        items = load_split(path.stem)
        print(f"{path.name}: {len(items)} items")
        for variant, count in sorted(Counter(i.variant for i in items).items()):
            print(f"  {variant:12s} {count}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m eval")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="평가셋 실행")
    run.add_argument("--nlu", choices=NLU_MODES, default="rule")
    run.add_argument("--split", nargs="+", default=["dev", "test"])
    run.add_argument("--model", default=None, help="LLM 모델명 (기본: .env의 OPENAI_MODEL)")
    run.add_argument("--base-url", default=None, help="OpenAI 호환 엔드포인트 (예: Ollama http://localhost:11434/v1)")
    run.add_argument("--limit", type=int, default=None, help="앞에서 N개만 실행 (점검용)")
    run.add_argument("--out", default=None)
    run.add_argument("--progress", action="store_true")
    run.set_defaults(func=cmd_run)

    report = sub.add_parser("report", help="결과 파일들로 Markdown 리포트 생성")
    report.add_argument("results", nargs="+")
    report.add_argument("--out", default=str(HERE / "reports" / "report.md"))
    report.set_defaults(func=cmd_report)

    stats = sub.add_parser("stats", help="데이터셋 구성 확인")
    stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
