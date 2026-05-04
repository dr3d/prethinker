from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.kb_pipeline_clean import (  # noqa: E402
    canonical_process_result,
    compare_signatures,
    instrument_manifest,
    normalizer_inventory_audit,
    render_instrument_markdown,
    trace_plan,
)
from src.mcp_server import PrologMCPServer  # noqa: E402


RunTurn = Callable[[str, list[str], str, str], dict[str, Any]]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _case_id(case: dict[str, Any], index: int) -> str:
    candidate = str(case.get("case_id", "")).strip()
    if not candidate:
        candidate = str(case.get("id", "")).strip()
    return candidate or f"case_{index:03d}"


def _case_context(case: dict[str, Any]) -> list[str]:
    context = case.get("context", [])
    if not isinstance(context, list):
        return []
    return [str(item).strip() for item in context if str(item).strip()]


def _build_server(args: argparse.Namespace) -> PrologMCPServer:
    return PrologMCPServer(
        compiler_mode=args.compiler_mode,
        compiler_backend=args.compiler_backend,
        compiler_base_url=args.compiler_base_url,
        compiler_model=args.compiler_model,
        compiler_context_length=args.compiler_context_length,
        compiler_timeout=args.compiler_timeout,
        compiler_prompt_file=args.compiler_prompt_file,
        compiler_prompt_enabled=args.compiler_prompt_enabled,
        active_profile=args.active_profile,
        semantic_ir_enabled=args.semantic_ir_enabled,
        semantic_ir_model=args.semantic_ir_model or args.compiler_model,
        semantic_ir_context_length=args.semantic_ir_context_length,
        semantic_ir_timeout=args.semantic_ir_timeout,
        semantic_ir_temperature=args.semantic_ir_temperature,
        semantic_ir_top_p=args.semantic_ir_top_p,
        semantic_ir_top_k=args.semantic_ir_top_k,
        semantic_ir_thinking=args.semantic_ir_thinking,
    )


def _server_turn_runner(server: PrologMCPServer) -> RunTurn:
    def run_turn(
        utterance: str,
        context: list[str] | None = None,
        clarification_answer: str = "",
        prethink_id: str = "",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"utterance": utterance}
        if context:
            payload["context"] = context
        if clarification_answer:
            payload["clarification_answer"] = clarification_answer
        if prethink_id:
            payload["prethink_id"] = prethink_id
        return server.process_utterance(payload)

    return run_turn


def _baseline_signature(
    *,
    case: dict[str, Any],
    case_id: str,
    baseline_dir: Path | None,
) -> dict[str, Any] | None:
    inline = case.get("canonical_signature")
    if isinstance(inline, dict):
        return inline
    inline = case.get("baseline_signature")
    if isinstance(inline, dict):
        return inline
    if baseline_dir is None:
        return None
    path = baseline_dir / f"{case_id}.json"
    if not path.exists():
        return None
    payload = _load_json(path)
    if isinstance(payload, dict) and isinstance(payload.get("canonical_signature"), dict):
        return payload["canonical_signature"]
    return payload if isinstance(payload, dict) else None


def replay_process_case(
    *,
    case: dict[str, Any],
    index: int,
    run_turn: RunTurn,
    baseline_dir: Path | None = None,
) -> dict[str, Any]:
    """Replay one process_utterance case through live behavior and canonicalize it."""

    case_id = _case_id(case, index)
    case_context = _case_context(case)
    setup_records: list[dict[str, Any]] = []
    setup_failed = False
    for setup_turn in case.get("setup_turns", []):
        if not isinstance(setup_turn, dict):
            continue
        utterance = str(setup_turn.get("utterance", "")).strip()
        if not utterance:
            continue
        result = run_turn(
            utterance,
            _case_context(setup_turn),
            str(setup_turn.get("clarification_answer", "")).strip(),
            str(setup_turn.get("prethink_id", "")).strip(),
        )
        signature = canonical_process_result(result)
        setup_records.append(
            {
                "utterance": utterance,
                "status": signature.get("status", ""),
                "result_type": signature.get("result_type", ""),
                "canonical_signature": signature,
            }
        )
        if str(signature.get("status", "")).strip() == "error":
            setup_failed = True
            break

    target_utterance = str(case.get("utterance", "")).strip()
    clarification_answer = str(case.get("clarification_answer", "")).strip()
    if setup_failed:
        raw_result: dict[str, Any] = {
            "status": "error",
            "result_type": "setup_failed",
            "execution": {"status": "error", "writes_applied": 0, "operations": [], "errors": ["setup_failed"]},
        }
    else:
        raw_result = run_turn(target_utterance, case_context)
        if str(raw_result.get("status", "")).strip() == "clarification_required" and clarification_answer:
            prethink_id = str(raw_result.get("front_door", {}).get("prethink_id", "")).strip()
            raw_result = run_turn(target_utterance, case_context, clarification_answer, prethink_id)

    signature = canonical_process_result(raw_result)
    baseline = _baseline_signature(case=case, case_id=case_id, baseline_dir=baseline_dir)
    comparison = compare_signatures(baseline, signature) if baseline is not None else {"status": "no_baseline"}
    return {
        "case_id": case_id,
        "utterance": target_utterance,
        "context": case_context,
        "source_metadata": {
            "domain": str(case.get("domain", "")).strip(),
            "hazard": str(case.get("hazard", case.get("failure_mode", ""))).strip(),
            "allowed_predicates": [str(item).strip() for item in case.get("allowed_predicates", []) if str(item).strip()]
            if isinstance(case.get("allowed_predicates"), list)
            else [],
            "expect": case.get("expect", {}) if isinstance(case.get("expect"), dict) else {},
        },
        "setup_results": setup_records,
        "status": signature.get("status", ""),
        "result_type": signature.get("result_type", ""),
        "canonical_signature": signature,
        "comparison": comparison,
        "raw_result": raw_result,
    }


def replay_process_pack(
    *,
    pack: dict[str, Any],
    run_case: Callable[[dict[str, Any], int], dict[str, Any]],
) -> dict[str, Any]:
    cases = [case for case in pack.get("cases", []) if isinstance(case, dict)]
    rows = [run_case(case, index) for index, case in enumerate(cases, start=1)]
    status_counts = Counter(str(row.get("status", "")).strip() for row in rows)
    result_type_counts = Counter(str(row.get("result_type", "")).strip() for row in rows)
    comparison_counts = Counter(str(row.get("comparison", {}).get("status", "")).strip() for row in rows)
    route_counts = Counter(
        str(row.get("canonical_signature", {}).get("front_door", {}).get("route", "")).strip()
        for row in rows
    )
    execution_status_counts = Counter(
        str(row.get("canonical_signature", {}).get("execution", {}).get("status", "")).strip()
        for row in rows
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "pack_id": str(pack.get("pack_id", "")).strip(),
        "family": str(pack.get("family", "")).strip(),
        "cases_total": len(rows),
        "status_counts": dict(status_counts),
        "result_type_counts": dict(result_type_counts),
        "comparison_counts": dict(comparison_counts),
        "front_door_route_counts": dict(route_counts),
        "execution_status_counts": dict(execution_status_counts),
        "cases": rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daily-driver clean harness for KB pipeline parity work.")
    parser.add_argument("--instrument-manifest", action="store_true", help="Print the harness instrument manifest JSON.")
    parser.add_argument("--instrument-md", action="store_true", help="Print the harness instrument manifest as Markdown.")
    parser.add_argument("--trace-plan", action="store_true", help="Print the clean normalizer trace plan.")
    parser.add_argument("--audit-normalizers", action="store_true", help="Audit clean normalizer mapping against kb_pipeline.")
    parser.add_argument("--pack", type=Path, default=None, help="Replay a process_utterance frontier-style pack.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "tmp" / "runs" / "kb_pipeline_clean_harness")
    parser.add_argument("--baseline-dir", type=Path, default=None)

    parser.add_argument("--compiler-mode", choices=["strict", "auto", "heuristic"], default="heuristic")
    parser.add_argument("--compiler-backend", default="ollama")
    parser.add_argument("--compiler-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--compiler-model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--compiler-context-length", type=int, default=8192)
    parser.add_argument("--compiler-timeout", type=int, default=60)
    parser.add_argument("--compiler-prompt-file", default=str(ROOT / "modelfiles" / "blank_prompt.md"))
    parser.add_argument("--compiler-prompt-enabled", action="store_true")
    parser.add_argument("--active-profile", default="general")
    parser.add_argument("--semantic-ir-enabled", action="store_true")
    parser.add_argument("--semantic-ir-model", default="")
    parser.add_argument("--semantic-ir-context-length", type=int, default=8192)
    parser.add_argument("--semantic-ir-timeout", type=int, default=60)
    parser.add_argument("--semantic-ir-temperature", type=float, default=0.0)
    parser.add_argument("--semantic-ir-top-p", type=float, default=0.82)
    parser.add_argument("--semantic-ir-top-k", type=int, default=20)
    parser.add_argument("--semantic-ir-thinking", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.instrument_manifest:
        print(json.dumps(instrument_manifest(), indent=2, sort_keys=True))
        return 0
    if args.instrument_md:
        print(render_instrument_markdown())
        return 0
    if args.trace_plan:
        print(json.dumps(trace_plan(), indent=2, sort_keys=True))
        return 0
    if args.audit_normalizers:
        print(json.dumps(normalizer_inventory_audit(), indent=2, sort_keys=True))
        return 0
    if args.pack is None:
        print("No run selected. Use --trace-plan, --audit-normalizers, or --pack.")
        return 2

    pack = _load_json(args.pack)
    cases = pack.get("cases", []) if isinstance(pack.get("cases"), list) else []
    if args.limit > 0:
        pack = dict(pack)
        pack["cases"] = cases[: args.limit]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = args.out_dir / f"{timestamp}_{str(pack.get('pack_id', 'process_pack')).strip() or 'process_pack'}"
    server = _build_server(args)

    def run_case(case: dict[str, Any], index: int) -> dict[str, Any]:
        server.empty_kb()
        record = replay_process_case(
            case=case,
            index=index,
            run_turn=_server_turn_runner(server),
            baseline_dir=args.baseline_dir,
        )
        _write_json(run_dir / "cases" / f"{record['case_id']}.json", record)
        print(
            f"[{index:03d}] {record['case_id']} status={record['status']} "
            f"comparison={record['comparison'].get('status', '')}"
        )
        return record

    summary = replay_process_pack(pack=pack, run_case=run_case)
    summary["run_dir"] = str(run_dir)
    _write_json(run_dir / "summary.json", summary)
    print(f"Summary JSON: {run_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
