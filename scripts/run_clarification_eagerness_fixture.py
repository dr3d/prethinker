#!/usr/bin/env python3
"""Run Clarification Eagerness fixture cases through Semantic IR.

This runner scores declared ask/no-ask behavior. It does not derive entities,
predicates, facts, rules, or answers from raw prose. The fixture authors provide
the cases and expected behavior; Python only calls the model, reads structured
Semantic IR, and compares the model's clarification posture with the declared
expectation.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = REPO_ROOT / "datasets" / "clarification_eagerness" / "clarification_eagerness_trap"
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "clarification_eagerness_runs"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.semantic_ir import SemanticIRCallConfig, call_semantic_ir  # noqa: E402


ASK_BEHAVIORS = {"clarify", "commit_partial_clarify_blocked"}
NO_ASK_BEHAVIORS = {
    "answer",
    "answer_broad",
    "answer_multiple",
    "commit_no_ask",
    "commit_claim_no_ask",
    "quarantine_no_ask",
    "reject_no_ask",
}


CE_DOMAIN_CONTEXT = [
    "clarification_eagerness_fixture_v1: This is a CE behavior test, not a final answer-quality test.",
    "Ask for clarification when durable truth, a correction target, rule scope, role identity, or query scope would otherwise require an unauthorized choice.",
    "Do not ask when the content can be safely represented as a source claim, safely quarantined, answered with multiple bindings, or answered broadly without guessing.",
    "For mixed clear/ambiguous ingestion, preserve safe candidate operations and mark only blocked operations as needs_clarification.",
    "For query turns, clarify only when the user's question cannot be scoped against the available source/KB context without guessing.",
    "A clarification question should target the blocked slot directly; do not ask the user to restate the whole case.",
    "If a question names the claim, actor, accusation, rule, date, or document clearly, answer from context rather than asking because nearby concepts also exist.",
    "If source context has a direct local phrase match such as a named notice before a named closure, use that source-local event instead of asking about every possible closure-like word.",
    "If an utterance says 'according to', 'memo says', 'letter states', or similar source-attribution language, represent the content as a source claim when possible; do not emit the claimed proposition itself as a safe fact.",
    "Do not treat a source_claim/claim row as committing the claim content as fact merely because the claim content is represented in arguments.",
    "Never propose a safe durable write from source='context'. Context may guide safety, conflict detection, or query answers, but context-sourced operations must be unsafe, skipped, or diagnostic unless the user directly restates them.",
    "If a role/title subject says 'she/he/they did X' and the pronoun could be the role-holder or another reported actor, ask who the pronoun refers to before committing the actor slot.",
    "That role/title pronoun rule is narrow: it applies to role/title subjects or competing actor slots, not to a named-person antecedent continuing their own action in the same sentence.",
    "Do not over-apply pronoun caution: if a named person is the only local antecedent in the same sentence and the pronoun continues that person's action, resolve it without asking.",
    "If an utterance conflicts with a clear source finding and does not explicitly say it is a correction, quarantine or mark unsafe rather than asking whether to override the source.",
    "For ordinary contradictions against source context, do not ask whether to override the source unless the user explicitly frames the utterance as a correction. Asking to override source truth is over-eager.",
    "For quarantine/no-ask contradictions, use safety='unsafe' or decision='quarantine'; do not use safety='needs_clarification' unless you truly need a user answer.",
    "If the utterance asserts an official finding but context says that official body adopted a different finding, do not ask whether to record it as a new finding; quarantine the conflicting official-finding assertion without a clarification question.",
    "If the user names the official body as the actor, as in 'the panel found X', treat the source as specified. If X conflicts with the body's adopted finding, quarantine no-ask rather than asking which source they meant.",
    "If a sentence combines a safe observation with a finding explicitly negated by source context, admit the safe observation and mark the negated finding unsafe rather than needs_clarification.",
    "If an utterance contains a safe event plus a conflicting status or finding, keep the event candidate safe and mark the conflicting status/finding needs_clarification or unsafe according to the expected conflict posture.",
    "Questions asking what a panel, court, committee, or document 'actually found' should answer with adopted findings when the context has them; do not ask whether the user wanted non-adopted claims unless the question names those claims.",
    "A user asking 'Can I record that X caused Y?' for a disputed or non-adopted responsibility claim is not giving permission to write the fact. Clarify whether to record a source claim, correction, or new finding; do not simply store the embedded causal claim.",
    "If a user says an unnamed report, minority report, draft, claim, or statement 'became a finding' without identifying the adopted statement, ask which source document and which finding were adopted instead of quarantining silently.",
    "Correction markers such as 'actually' require a clear correction target. If the target object or old fact is missing, ask for that target before proposing a durable replacement.",
    "A correction target is clear only when the old clause exists in the supplied KB context. A source document mentioning the old value is not enough by itself to authorize retraction.",
    "For explicit correction with old and new values, preserve safe clear details but mark the replacement/retraction path as needing clarification unless the matching old KB fact is supplied in context.",
]


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _string_list(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def _ops(ir: dict[str, Any]) -> list[dict[str, Any]]:
    raw = ir.get("candidate_operations", [])
    return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []


def _model_requested_clarification(ir: dict[str, Any]) -> bool:
    decision = str(ir.get("decision", "")).strip().lower()
    if decision == "clarify":
        return True
    if _string_list(ir.get("clarification_questions")):
        return True
    for op in _ops(ir):
        if str(op.get("safety", "")).strip().lower() == "needs_clarification":
            return True
    self_check = ir.get("self_check", {})
    if isinstance(self_check, dict) and _string_list(self_check.get("missing_slots")):
        return True
    return False


def _has_safe_partial(ir: dict[str, Any]) -> bool:
    for op in _ops(ir):
        if str(op.get("operation", "")).strip().lower() not in {"assert", "rule", "query", "retract"}:
            continue
        if str(op.get("safety", "")).strip().lower() == "safe":
            return True
    return False


def _blocked_row_count(ir: dict[str, Any]) -> int:
    count = 0
    for op in _ops(ir):
        safety = str(op.get("safety", "")).strip().lower()
        if safety in {"needs_clarification", "unsafe"}:
            count += 1
    return count


def _op_surface(op: dict[str, Any]) -> str:
    predicate = str(op.get("predicate", "")).strip()
    args = op.get("args", [])
    args_text = ",".join(str(arg).strip() for arg in args) if isinstance(args, list) else ""
    clause = str(op.get("clause", "")).strip()
    return " ".join(part for part in [predicate, args_text, clause] if part)


def _forbidden_hits(case: dict[str, Any], ir: dict[str, Any]) -> list[str]:
    forbidden = [str(item).strip("` ").lower() for item in case.get("must_not_commit", []) if str(item).strip()]
    if not forbidden:
        return []
    surfaces = []
    for op in _ops(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("operation", "")).strip().lower() == "query":
            continue
        predicate = str(op.get("predicate", "")).strip().lower()
        if predicate in {"source_claim", "claim", "witness_statement", "legal_position", "reported_event"}:
            continue
        surfaces.append(_op_surface(op).lower())
    hits: list[str] = []
    for pattern in forbidden:
        name = pattern.split("(", 1)[0].strip().lower()
        if not name or name == "none":
            continue
        for surface in surfaces:
            if name in surface:
                hits.append(pattern)
                break
    return sorted(set(hits))


def _context_write_hits(ir: dict[str, Any]) -> list[str]:
    hits: list[str] = []
    for op in _ops(ir):
        operation = str(op.get("operation", "")).strip().lower()
        if operation not in {"assert", "rule", "retract"}:
            continue
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("source", "")).strip().lower() != "context":
            continue
        hits.append(_op_surface(op))
    return hits


def _score_case(case: dict[str, Any], ir: dict[str, Any], *, parsed_ok: bool, error: str = "") -> dict[str, Any]:
    expected = str(case.get("expected_behavior", "")).strip().lower()
    expected_ask = expected in ASK_BEHAVIORS
    expected_no_ask = expected in NO_ASK_BEHAVIORS
    requested = _model_requested_clarification(ir) if parsed_ok else False
    safe_partial = _has_safe_partial(ir) if parsed_ok else False
    forbidden_hits = _forbidden_hits(case, ir) if parsed_ok else []
    context_write_hits = _context_write_hits(ir) if parsed_ok else []

    if not parsed_ok:
        verdict = "parse_error"
    elif expected_ask and requested:
        verdict = "correct"
    elif expected_no_ask and not requested:
        verdict = "correct"
    elif expected_ask and not requested:
        verdict = "undereager"
    elif expected_no_ask and requested:
        verdict = "overeager"
    else:
        verdict = "unknown_expected"

    if (forbidden_hits or context_write_hits) and verdict == "correct":
        verdict = "unsafe_candidate"

    return {
        "case_id": case.get("id", ""),
        "surface": case.get("surface", ""),
        "expected_behavior": expected,
        "expected_ask": expected_ask,
        "model_requested_clarification": requested,
        "verdict": verdict,
        "safe_partial_expected": bool(case.get("safe_partials_expected", False)),
        "safe_partial_seen": safe_partial,
        "blocked_row_count": _blocked_row_count(ir) if parsed_ok else 0,
        "forbidden_hits": forbidden_hits,
        "context_write_hits": context_write_hits,
        "decision": str(ir.get("decision", "")) if parsed_ok else "",
        "turn_type": str(ir.get("turn_type", "")) if parsed_ok else "",
        "clarification_questions": _string_list(ir.get("clarification_questions")) if parsed_ok else [],
        "missing_slots": _string_list(ir.get("self_check", {}).get("missing_slots")) if isinstance(ir.get("self_check"), dict) else [],
        "candidate_operation_surfaces": [
            {
                "operation": str(op.get("operation", "")),
                "predicate": str(op.get("predicate", "")),
                "args": op.get("args", []),
                "safety": str(op.get("safety", "")),
                "source": str(op.get("source", "")),
                "clause": str(op.get("clause", "")),
            }
            for op in _ops(ir)
        ] if parsed_ok else [],
        "parsed_ok": parsed_ok,
        "error": error,
    }


def _case_text(case: dict[str, Any]) -> str:
    return str(case.get("utterance") or case.get("question") or "").strip()


def _load_cases(fixture: Path, surface: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if surface in {"ingestion", "both"}:
        rows.extend(_jsonl(fixture / "ingestion_cases.jsonl"))
    if surface in {"query", "both"}:
        rows.extend(_jsonl(fixture / "query_cases.jsonl"))
    return rows


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    verdict_counts: dict[str, int] = {}
    for row in rows:
        verdict = str(row.get("verdict", "unknown"))
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
    requested = sum(1 for row in rows if row.get("model_requested_clarification"))
    expected_ask = sum(1 for row in rows if row.get("expected_ask"))
    ask_correct = sum(
        1
        for row in rows
        if row.get("expected_ask")
        and row.get("model_requested_clarification")
        and row.get("verdict") == "correct"
    )
    noask_correct = sum(
        1
        for row in rows
        if not row.get("expected_ask")
        and not row.get("model_requested_clarification")
        and row.get("verdict") == "correct"
    )
    correct = verdict_counts.get("correct", 0)
    overeager = verdict_counts.get("overeager", 0)
    undereager = verdict_counts.get("undereager", 0)
    parse_errors = verdict_counts.get("parse_error", 0)
    safe_partial_expected = sum(1 for row in rows if row.get("safe_partial_expected"))
    safe_partial_seen = sum(1 for row in rows if row.get("safe_partial_expected") and row.get("safe_partial_seen"))
    return {
        "case_count": len(rows),
        "expected_ask_count": expected_ask,
        "requested_clarification_count": requested,
        "correct_count": correct,
        "ask_correct_count": ask_correct,
        "noask_correct_count": noask_correct,
        "overeager_count": overeager,
        "undereager_count": undereager,
        "parse_error_count": parse_errors,
        "unsafe_candidate_count": verdict_counts.get("unsafe_candidate", 0),
        "context_write_violation_count": sum(1 for row in rows if row.get("context_write_hits")),
        "safe_partial_expected_count": safe_partial_expected,
        "safe_partial_seen_count": safe_partial_seen,
        "verdict_counts": verdict_counts,
        "clarification_precision": round(ask_correct / requested, 3) if requested else None,
        "clarification_recall": round(ask_correct / expected_ask, 3) if expected_ask else None,
        "noask_precision": round(noask_correct / (len(rows) - requested), 3) if len(rows) > requested else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--surface", choices=["ingestion", "query", "both"], default="both")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--backend", default="lmstudio")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--context-length", type=int, default=32768)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--include-source-context", action="store_true")
    args = parser.parse_args(argv)

    fixture = args.fixture.resolve()
    cases = _load_cases(fixture, args.surface)
    if args.limit > 0:
        cases = cases[: args.limit]

    source_context: list[str] = []
    if args.include_source_context:
        source_text = (fixture / "source.md").read_text(encoding="utf-8")
        source_context.append("Fixture source context:\n" + source_text)

    config = SemanticIRCallConfig(
        backend=str(args.backend),
        base_url=str(args.base_url),
        model=str(args.model),
        context_length=int(args.context_length),
        timeout=int(args.timeout_seconds),
        temperature=float(args.temperature),
        max_tokens=int(args.max_tokens),
    )

    run_started = datetime.now(timezone.utc)
    run_id = f"cet-{run_started.strftime('%Y%m%dT%H%M%SZ')}-{args.surface}-{len(cases)}"
    out_dir = args.out_dir.resolve() / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    details_path = out_dir / "case_results.jsonl"
    with details_path.open("w", encoding="utf-8") as handle:
        for index, case in enumerate(cases, start=1):
            text = _case_text(case)
            print(f"[{index}/{len(cases)}] {case.get('id')} {case.get('surface')} expected={case.get('expected_behavior')}")
            started = time.perf_counter()
            parsed: dict[str, Any] = {}
            parsed_ok = False
            error = ""
            try:
                result = call_semantic_ir(
                    utterance=text,
                    config=config,
                    context=source_context,
                    domain_context=CE_DOMAIN_CONTEXT,
                    domain="clarification_eagerness_trap",
                )
                parsed = result.get("parsed", {}) if isinstance(result.get("parsed"), dict) else {}
                parsed_ok = bool(parsed)
                if not parsed_ok:
                    error = "empty_or_unparseable_semantic_ir"
            except Exception as exc:  # pragma: no cover - external model path
                error = str(exc)
            scored = _score_case(case, parsed, parsed_ok=parsed_ok, error=error)
            scored["latency_ms"] = int((time.perf_counter() - started) * 1000)
            scored["utterance_or_question"] = text
            rows.append(scored)
            handle.write(json.dumps(scored, ensure_ascii=True) + "\n")
            handle.flush()

    summary = {
        "schema_version": "clarification_eagerness_run_v1",
        "run_id": run_id,
        "fixture": str(fixture),
        "surface": args.surface,
        "started_at": run_started.isoformat(),
        "backend": args.backend,
        "model": args.model,
        "include_source_context": bool(args.include_source_context),
        "summary": _summarize(rows),
        "details_path": str(details_path),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps(summary["summary"], indent=2, ensure_ascii=True))
    print(f"Wrote {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
