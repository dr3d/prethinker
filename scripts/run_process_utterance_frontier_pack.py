from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORGE_PATH = ROOT / "scripts" / "run_process_utterance_forge.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mcp_server import PrologMCPServer


def _load_forge_module():
    spec = importlib.util.spec_from_file_location("process_utterance_forge", FORGE_PATH)
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load forge module from {FORGE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _severity(verdict: str) -> int:
    lookup = {"pass": 0, "warn": 1, "fail": 2}
    return lookup.get(str(verdict).strip().lower(), 99)


def _delta_label(*, baseline: str, current: str) -> str:
    baseline_score = _severity(baseline)
    current_score = _severity(current)
    if current_score < baseline_score:
        return "improved"
    if current_score > baseline_score:
        return "regressed"
    return "unchanged"


def _build_server(args: argparse.Namespace) -> PrologMCPServer:
    return PrologMCPServer(
        compiler_mode=args.compiler_mode,
        compiler_backend=args.compiler_backend,
        compiler_base_url=args.compiler_base_url,
        compiler_model=args.compiler_model,
        compiler_context_length=args.compiler_context_length,
        compiler_timeout=args.compiler_timeout,
        compiler_prompt_file=args.compiler_prompt_file,
        freethinker_resolution_policy=args.freethinker_resolution_policy,
        freethinker_backend=args.freethinker_backend,
        freethinker_base_url=args.freethinker_base_url,
        freethinker_model=args.freethinker_model,
        freethinker_context_length=args.freethinker_context_length,
        freethinker_timeout=args.freethinker_timeout,
        freethinker_prompt_file=args.freethinker_prompt_file,
    )


def _run_turn(
    *,
    server: PrologMCPServer,
    utterance: str,
    clarification_answer: str = "",
    prethink_id: str = "",
) -> dict[str, Any]:
    payload = {"utterance": utterance}
    if clarification_answer:
        payload["clarification_answer"] = clarification_answer
    if prethink_id:
        payload["prethink_id"] = prethink_id
    return server.process_utterance(payload)


def _write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Process Utterance Frontier Pack",
        "",
        f"- pack_id: `{summary.get('pack_id', '')}`",
        f"- generated_at_utc: `{summary.get('generated_at_utc', '')}`",
        f"- cases: `{summary.get('cases_total', 0)}`",
        f"- verdict_counts: `{summary.get('verdict_counts', {})}`",
        f"- delta_counts: `{summary.get('delta_counts', {})}`",
        f"- status_counts: `{summary.get('status_counts', {})}`",
        "",
        "## Case Results",
        "",
    ]
    for row in summary.get("cases", []):
        baseline = row.get("baseline", {})
        current = row.get("current", {})
        lines.append(
            f"- `{row.get('case_id', '')}`: baseline=`{baseline.get('verdict', '')}/{baseline.get('status', '')}` "
            f"current=`{current.get('verdict', '')}/{current.get('status', '')}` delta=`{row.get('delta', '')}` "
            f"target=`{row.get('utterance', '')}`"
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay a tracked process_utterance frontier pack.")
    parser.add_argument("--pack", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out-dir", default="tmp/runs/process_utterance_frontier_packs")
    parser.add_argument("--summary-out", default="")
    parser.add_argument("--summary-md", default="")

    parser.add_argument("--compiler-mode", choices=["strict", "auto", "heuristic"], default="strict")
    parser.add_argument("--compiler-backend", default="ollama")
    parser.add_argument("--compiler-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--compiler-model", default="qwen3.5:9b")
    parser.add_argument("--compiler-context-length", type=int, default=8192)
    parser.add_argument("--compiler-timeout", type=int, default=60)
    parser.add_argument(
        "--compiler-prompt-file",
        default=str(ROOT / "modelfiles" / "semantic_parser_system_prompt.md"),
    )

    parser.add_argument("--freethinker-resolution-policy", default="off")
    parser.add_argument("--freethinker-backend", default="ollama")
    parser.add_argument("--freethinker-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--freethinker-model", default="qwen3.5:9b")
    parser.add_argument("--freethinker-context-length", type=int, default=16384)
    parser.add_argument("--freethinker-timeout", type=int, default=60)
    parser.add_argument(
        "--freethinker-prompt-file",
        default=str(ROOT / "modelfiles" / "freethinker_system_prompt.md"),
    )

    parser.add_argument("--judge-backend", default="ollama")
    parser.add_argument("--judge-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--judge-model", default="qwen3.5:9b")
    parser.add_argument("--judge-context-length", type=int, default=8192)
    parser.add_argument("--judge-timeout", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    forge = _load_forge_module()
    judge_api_key = forge._get_api_key()

    pack_path = Path(args.pack)
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    cases = list(pack.get("cases", [])) if isinstance(pack.get("cases"), list) else []
    if int(args.limit) > 0:
        cases = cases[: int(args.limit)]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = ROOT / args.out_dir / f"{timestamp}_{pack.get('pack_id', 'frontier_pack')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    verdict_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    delta_counts: Counter[str] = Counter()

    for index, case in enumerate(cases, start=1):
        server = _build_server(args)
        server.empty_kb()

        setup_records: list[dict[str, Any]] = []
        setup_failed = False
        for setup_turn in case.get("setup_turns", []):
            utterance = str(setup_turn.get("utterance", "")).strip()
            if not utterance:
                continue
            result = _run_turn(
                server=server,
                utterance=utterance,
                clarification_answer=str(setup_turn.get("clarification_answer", "")).strip(),
                prethink_id=str(setup_turn.get("prethink_id", "")).strip(),
            )
            summary = forge._summarize_result(result)
            setup_records.append({"utterance": utterance, "result_summary": summary})
            if str(summary.get("status", "")).strip() == "error":
                setup_failed = True
                break

        target_utterance = str(case.get("utterance", "")).strip()
        target_result: dict[str, Any]
        clarification_answer = str(case.get("clarification_answer", "")).strip()
        if setup_failed:
            target_result = {
                "status": "error",
                "result_type": "setup_failed",
                "front_door": {
                    "route": "",
                    "compiler_intent": "",
                    "needs_clarification": False,
                    "clarification_question": "",
                    "ambiguity_score": 1.0,
                },
                "execution": {
                    "status": "error",
                    "writes_applied": 0,
                    "operations": [],
                    "query_result": None,
                    "parse": {},
                    "errors": ["setup_failed"],
                },
                "compiler_trace": {"summary": {"overall": "setup_failed", "parse_rescues": [], "freethinker_action": ""}},
            }
        else:
            target_result = _run_turn(server=server, utterance=target_utterance)
            if str(target_result.get("status", "")).strip() == "clarification_required" and clarification_answer:
                prethink_id = str(target_result.get("front_door", {}).get("prethink_id", "")).strip()
                target_result = _run_turn(
                    server=server,
                    utterance=target_utterance,
                    clarification_answer=clarification_answer,
                    prethink_id=prethink_id,
                )

        result_summary = forge._summarize_result(target_result)
        judgment = forge._judge_turn(
            spec=case.get("spec", {}),
            result_summary=result_summary,
            clarification_answer=clarification_answer,
            backend=args.judge_backend,
            base_url=args.judge_base_url,
            model=args.judge_model,
            context_length=args.judge_context_length,
            timeout=args.judge_timeout,
            api_key=judge_api_key,
        )
        baseline = case.get("baseline", {}) if isinstance(case.get("baseline"), dict) else {}
        delta = _delta_label(
            baseline=str(baseline.get("verdict", "")).strip(),
            current=str(judgment.get("verdict", "")).strip(),
        )

        record = {
            "case_id": str(case.get("case_id", "")).strip(),
            "utterance": target_utterance,
            "setup_turns": case.get("setup_turns", []),
            "setup_results": setup_records,
            "baseline": baseline,
            "current": {
                "verdict": str(judgment.get("verdict", "")).strip(),
                "status": str(result_summary.get("status", "")).strip(),
                "tags": list(judgment.get("tags", [])) if isinstance(judgment.get("tags"), list) else [],
                "rationale": str(judgment.get("rationale", "")).strip(),
                "logic_string": str(result_summary.get("logic_string", "")).strip(),
                "trace_overall": str(result_summary.get("trace_overall", "")).strip(),
            },
            "delta": delta,
            "raw_result_summary": result_summary,
        }
        rows.append(record)
        verdict_counts[str(judgment.get("verdict", "")).strip()] += 1
        status_counts[str(result_summary.get("status", "")).strip()] += 1
        delta_counts[delta] += 1

        case_path = run_dir / f"{index:02d}_{record['case_id']}.json"
        case_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(
            f"[{index:02d}/{len(cases):02d}] case={record['case_id']} "
            f"baseline={baseline.get('verdict', '')}/{baseline.get('status', '')} "
            f"current={record['current']['verdict']}/{record['current']['status']} delta={delta}"
        )

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "pack_id": str(pack.get("pack_id", "")).strip(),
        "family": str(pack.get("family", "")).strip(),
        "cases_total": len(rows),
        "verdict_counts": dict(verdict_counts),
        "status_counts": dict(status_counts),
        "delta_counts": dict(delta_counts),
        "run_dir": str(run_dir),
        "cases": rows,
    }
    summary_out = Path(args.summary_out) if args.summary_out else run_dir / "summary.json"
    summary_md = Path(args.summary_md) if args.summary_md else run_dir / "summary.md"
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_md.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    _write_summary_md(summary_md, summary)
    print(f"Summary JSON: {summary_out}")
    print(f"Summary MD: {summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
