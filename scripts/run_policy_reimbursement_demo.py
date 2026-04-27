#!/usr/bin/env python3
"""Run the reimbursement-policy demo as a cross-turn Semantic IR trace."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "policy_reimbursement_demo"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.policy_reimbursement_demo import (  # noqa: E402
    ALLOWED_PREDICATES,
    DEMO_TURNS,
    DOMAIN,
    DOMAIN_CONTEXT,
    PREDICATE_CONTRACTS,
    PolicyDemoState,
    apply_mapped_to_policy_runtime,
    build_policy_kb_context_pack,
    query_policy_runtime,
    summarize_policy_demo_rows,
    write_policy_demo_html,
    write_policy_demo_markdown,
)
from src.semantic_ir import (  # noqa: E402
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the policy reimbursement Semantic IR demo.")
    parser.add_argument("--backend", choices=["lmstudio", "ollama"], default="lmstudio")
    parser.add_argument("--model", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--include-model-input", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backend = str(args.backend or "lmstudio").strip().lower()
    model = str(args.model or "").strip()
    if not model:
        model = "qwen/qwen3.6-35b-a3b" if backend == "lmstudio" else "qwen3.6:35b"
    base_url = str(args.base_url or "").strip()
    if not base_url:
        base_url = "http://127.0.0.1:1234" if backend == "lmstudio" else "http://127.0.0.1:11434"

    config = SemanticIRCallConfig(
        backend=backend,
        base_url=base_url,
        model=model,
        context_length=int(args.num_ctx),
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        top_k=int(args.top_k),
        max_tokens=int(args.max_tokens),
        think_enabled=False,
        reasoning_effort="none",
    )

    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(model)}"
    jsonl_path = out_dir / f"policy_reimbursement_demo_{slug}.jsonl"
    json_path = out_dir / f"policy_reimbursement_demo_{slug}.json"
    md_path = out_dir / f"policy_reimbursement_demo_{slug}.md"
    html_path = out_dir / f"policy_reimbursement_demo_{slug}.html"
    latest_html_path = out_dir / "policy_reimbursement_demo_latest.html"

    state = PolicyDemoState()
    rows: list[dict[str, Any]] = []
    for index, turn in enumerate(DEMO_TURNS, start=1):
        print(f"[{index}/{len(DEMO_TURNS)}] {turn['id']}", flush=True)
        row = run_turn(
            index=index,
            turn=turn,
            state=state,
            config=config,
            include_model_input=bool(args.include_model_input),
        )
        rows.append(row)
        with jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    record = {
        "ts": _utc_now(),
        "backend": backend,
        "model": model,
        "base_url": base_url,
        "domain": DOMAIN,
        "allowed_predicates": ALLOWED_PREDICATES,
        "predicate_contracts": PREDICATE_CONTRACTS,
        "domain_context": DOMAIN_CONTEXT,
        "summary": summarize_policy_demo_rows(rows),
        "rows": rows,
    }
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    write_policy_demo_markdown(record, md_path)
    write_policy_demo_html(record, html_path)
    write_policy_demo_html(record, latest_html_path)
    print(f"Wrote {jsonl_path}")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    print(f"Wrote {latest_html_path}")
    print(json.dumps(record["summary"], ensure_ascii=False, sort_keys=True))
    return 0


def run_turn(
    *,
    index: int,
    turn: dict[str, Any],
    state: PolicyDemoState,
    config: SemanticIRCallConfig,
    include_model_input: bool,
) -> dict[str, Any]:
    utterance = str(turn.get("utterance") or "").strip()
    turn_id = str(turn.get("id") or f"turn_{index}").strip()
    expected_query = str(turn.get("expect", {}).get("query") or "").strip()
    expected_rows = [str(item).strip().casefold() for item in turn.get("expect", {}).get("expected_rows", [])]
    started = time.perf_counter()
    kb_context_pack = build_policy_kb_context_pack(state, utterance=utterance, turn_id=turn_id)
    row: dict[str, Any] = {
        "ts": _utc_now(),
        "index": index,
        "turn_id": turn_id,
        "utterance": utterance,
        "expected_query": expected_query,
        "expected_rows": expected_rows,
        "parsed_ok": False,
        "error": "",
    }
    try:
        response = call_semantic_ir(
            utterance=utterance,
            config=config,
            context=[
                "This is a cross-turn policy/reimbursement demo.",
                "Use prior committed KB context for rules, facts, and explicit corrections.",
                "Derived violations belong in query answers or truth_maintenance.derived_consequences, not durable fact writes.",
            ],
            domain_context=DOMAIN_CONTEXT,
            allowed_predicates=ALLOWED_PREDICATES,
            predicate_contracts=PREDICATE_CONTRACTS,
            kb_context_pack=kb_context_pack,
            domain=DOMAIN,
            include_model_input=include_model_input,
        )
        parsed = response.get("parsed")
    except Exception as exc:
        row["error"] = str(exc)
        row["latency_ms"] = int((time.perf_counter() - started) * 1000)
        return row
    row["latency_ms"] = int(response.get("latency_ms", 0) or ((time.perf_counter() - started) * 1000))
    if include_model_input:
        row["model_input"] = response.get("model_input", {})
    if not isinstance(parsed, dict):
        row["error"] = str(response.get("parse_error", "semantic_ir_parse_failed"))
        row["raw_content"] = str(response.get("content", ""))[:4000]
        return row

    mapped, warnings = semantic_ir_to_legacy_parse(
        parsed,
        allowed_predicates=ALLOWED_PREDICATES,
        predicate_contracts=PREDICATE_CONTRACTS,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    runtime_apply = apply_mapped_to_policy_runtime(mapped, state)
    runtime_query = query_policy_runtime(state, expected_query) if expected_query else {}
    actual_rows = [str(item).strip().casefold() for item in runtime_query.get("r_values", [])]
    derived_leak = _has_derived_violation_write(runtime_apply)
    row.update(
        {
            "parsed_ok": True,
            "model_decision": parsed.get("decision", ""),
            "projected_decision": diagnostics.get("projected_decision", ""),
            "admitted_count": int(diagnostics.get("admitted_count", 0) or 0),
            "skipped_count": int(diagnostics.get("skipped_count", 0) or 0),
            "warning_counts": diagnostics.get("warning_counts", {}),
            "mapper_warnings": warnings,
            "runtime_apply": runtime_apply,
            "runtime_query": runtime_query,
            "expected_match": sorted(actual_rows) == sorted(expected_rows),
            "derived_violation_write_leak": derived_leak,
            "parsed": parsed,
            "mapped": mapped,
            "admission_diagnostics": diagnostics,
            "kb_context_pack": kb_context_pack,
            "kb_after": {
                "facts": list(state.facts),
                "rules": list(state.rules),
                "recent_committed_logic": list(state.recent_committed_logic),
            },
        }
    )
    return row


def _has_derived_violation_write(runtime_apply: dict[str, Any]) -> bool:
    for clause in runtime_apply.get("asserted_facts", []):
        if str(clause).strip().casefold().startswith(("violation(", "self_approval(", "manager_conflict_approval(")):
            return True
    return False


def _slug(value: str) -> str:
    text = "".join(char.lower() if char.isalnum() else "-" for char in str(value or ""))
    text = "-".join(part for part in text.split("-") if part)
    return text[:80] or "run"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
