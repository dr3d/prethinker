#!/usr/bin/env python3
"""Run natural-language QA probes against a bootstrapped source KB.

This is deliberately post-ingestion. The QA markdown is not used to design the
profile or compile the source document. It probes the resultant KB after a
source compile run has produced admitted facts/rules.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_qa"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_pipeline import CorePrologRuntime  # noqa: E402
from src.profile_bootstrap import (  # noqa: E402
    profile_bootstrap_allowed_predicates,
    profile_bootstrap_domain_context,
    profile_bootstrap_predicate_contracts,
)
from src.semantic_ir import (  # noqa: E402
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run QA probes against a domain bootstrap source-compile run.")
    parser.add_argument("--run-json", type=Path, required=True, help="domain_bootstrap_file_*.json with source_compile.")
    parser.add_argument("--qa-file", type=Path, required=True, help="Markdown file containing numbered QA prompts.")
    parser.add_argument("--oracle-jsonl", type=Path, default=None, help="Optional answer key for scoring.")
    parser.add_argument("--backend", choices=["lmstudio"], default="lmstudio")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=32768)
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--include-model-input", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_path = args.run_json if args.run_json.is_absolute() else (REPO_ROOT / args.run_json).resolve()
    qa_path = args.qa_file if args.qa_file.is_absolute() else (REPO_ROOT / args.qa_file).resolve()
    run_record = json.loads(run_path.read_text(encoding="utf-8-sig"))
    qa_text = qa_path.read_text(encoding="utf-8-sig")
    questions = parse_numbered_markdown_questions(qa_text)
    if int(args.limit or 0) > 0:
        questions = questions[: int(args.limit)]
    oracle = load_oracle(args.oracle_jsonl)
    for qid, answer in parse_markdown_answer_key(qa_text).items():
        oracle.setdefault(qid, {})["reference_answer"] = answer

    parsed_profile = run_record.get("parsed") if isinstance(run_record.get("parsed"), dict) else {}
    compile_record = run_record.get("source_compile") if isinstance(run_record.get("source_compile"), dict) else {}
    facts = [str(item).strip() for item in compile_record.get("facts", []) if str(item).strip()]
    rules = [str(item).strip() for item in compile_record.get("rules", []) if str(item).strip()]
    runtime, load_errors = load_runtime(facts=facts, rules=rules)

    allowed_predicates = profile_bootstrap_allowed_predicates(parsed_profile)
    predicate_contracts = profile_bootstrap_predicate_contracts(parsed_profile)
    kb_inventory = compiled_kb_inventory(facts=facts, rules=rules)
    actual_signatures = list(kb_inventory["signatures"])
    if actual_signatures:
        allowed_predicates = actual_signatures
        predicate_contracts = compiled_kb_contracts(actual_signatures)
    domain_context = [
        *profile_bootstrap_domain_context(parsed_profile),
        "Post-ingestion QA mode: the source document has already been compiled into the KB.",
        "Treat the current utterance as a probe against existing KB state unless it explicitly states a correction or new assertion.",
        "For ordinary questions, emit query candidate_operations, not writes.",
        "Use the actual compiled KB predicate inventory exactly. Do not invent a new query predicate when the KB already has a predicate with the needed meaning.",
        "When the answer position is unknown, use Prolog variables X, Y, or Z exactly. Lowercase terms such as rule, time, condition, item, person, location, who, what, where, and answer are constants, not variables.",
        "Never put lowercase generic placeholder words into query arguments when you want the KB to return a value.",
        "For multi-hop questions, emit multiple safe query operations over the actual KB predicates instead of inventing a composite predicate.",
        "For unsafe inference traps, preserve the difference between direct KB support, source claim, inference, and unknown.",
    ]
    config = SemanticIRCallConfig(
        backend=str(args.backend),
        base_url=str(args.base_url),
        model=str(args.model),
        context_length=int(args.num_ctx),
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        top_k=int(args.top_k),
        max_tokens=int(args.max_tokens),
        think_enabled=False,
        reasoning_effort="none",
    )

    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for item in questions:
        row = run_one_question(
            item=item,
            config=config,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
            domain_context=domain_context,
            kb_inventory=kb_inventory,
            facts=facts,
            rules=rules,
            runtime=runtime,
            oracle=oracle.get(item["id"], {}),
            include_model_input=bool(args.include_model_input),
        )
        rows.append(row)

    summary = summarize(rows=rows, load_errors=load_errors, elapsed_ms=int((time.perf_counter() - started) * 1000))
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_json": str(run_path),
        "qa_file": str(qa_path),
        "model": str(args.model),
        "source_fact_count": len(facts),
        "source_rule_count": len(rules),
        "runtime_load_errors": load_errors,
        "oracle_present": bool(oracle),
        "summary": summary,
        "rows": rows,
    }
    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(qa_path.stem)}_{_slug(str(args.model))}"
    json_path = out_dir / f"domain_bootstrap_qa_{slug}.json"
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    write_summary(record, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def parse_numbered_markdown_questions(text: str) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    phase = ""
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if re.match(r"^#+\s*answers\b", line, flags=re.IGNORECASE):
            break
        if line.startswith("#"):
            phase = line.lstrip("#").strip()
            continue
        match = re.match(r"^(\d+)\.\s+(.*\S)\s*$", line)
        if not match:
            continue
        questions.append({"id": f"q{int(match.group(1)):03d}", "number": int(match.group(1)), "phase": phase, "utterance": match.group(2)})
    return questions


def parse_markdown_answer_key(text: str) -> dict[str, str]:
    answers: dict[str, str] = {}
    in_answers = False
    current_id = ""
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_lines
        if current_id and current_lines:
            answers[current_id] = " ".join(part.strip() for part in current_lines if part.strip()).strip()
        current_id = ""
        current_lines = []

    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not in_answers:
            if re.match(r"^#+\s*answers\b", line, flags=re.IGNORECASE):
                in_answers = True
            continue
        match = re.match(r"^(\d+)\.\s+(.*\S)\s*$", line)
        if match:
            flush()
            current_id = f"q{int(match.group(1)):03d}"
            current_lines = [match.group(2)]
            continue
        if current_id and line and not line.startswith("#"):
            current_lines.append(line)
    flush()
    return answers


def compiled_kb_inventory(*, facts: list[str], rules: list[str]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    examples: dict[str, list[str]] = {}
    for clause in [*facts, *rules]:
        signature = clause_signature(clause)
        if not signature:
            continue
        counts[signature] = counts.get(signature, 0) + 1
        bucket = examples.setdefault(signature, [])
        if len(bucket) < 3:
            bucket.append(str(clause).strip())
    signatures = sorted(counts, key=lambda item: (-counts[item], item))
    return {
        "signatures": signatures,
        "counts": counts,
        "examples": {signature: examples.get(signature, []) for signature in signatures[:80]},
    }


def compiled_kb_contracts(signatures: list[str]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for signature in signatures:
        try:
            arity = int(signature.rsplit("/", 1)[1])
        except Exception:
            continue
        contracts.append({"signature": signature, "args": [f"arg{i}" for i in range(1, arity + 1)]})
    return contracts


def clause_signature(clause: str) -> str:
    text = str(clause or "").strip()
    if not text:
        return ""
    if ":-" in text:
        text = text.split(":-", 1)[0].strip()
    match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*\.?$", text)
    if not match:
        return ""
    args = split_top_level_args(match.group(2).strip())
    return f"{match.group(1)}/{len(args)}"


def split_top_level_args(text: str) -> list[str]:
    if not str(text or "").strip():
        return []
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in str(text):
        if char in "([":
            depth += 1
        elif char in ")]" and depth > 0:
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def load_oracle(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    resolved = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    out: dict[str, dict[str, Any]] = {}
    for raw_line in resolved.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        item = json.loads(line)
        if isinstance(item, dict) and str(item.get("id", "")).strip():
            out[str(item["id"]).strip()] = item
    return out


def load_runtime(*, facts: list[str], rules: list[str]) -> tuple[CorePrologRuntime, list[str]]:
    runtime = CorePrologRuntime(max_depth=500)
    errors: list[str] = []
    for fact in facts:
        result = runtime.assert_fact(fact)
        if str(result.get("status", "")) != "success":
            errors.append(f"fact {fact}: {result.get('message', result)}")
    for rule in rules:
        result = runtime.assert_rule(rule)
        if str(result.get("status", "")) != "success":
            errors.append(f"rule {rule}: {result.get('message', result)}")
    return runtime, errors


def run_one_question(
    *,
    item: dict[str, Any],
    config: SemanticIRCallConfig,
    allowed_predicates: list[str],
    predicate_contracts: list[dict[str, Any]],
    domain_context: list[str],
    kb_inventory: dict[str, Any],
    facts: list[str],
    rules: list[str],
    runtime: CorePrologRuntime,
    oracle: dict[str, Any],
    include_model_input: bool,
) -> dict[str, Any]:
    utterance = str(item.get("utterance", ""))
    kb_context_pack = {
        "version": "semantic_ir_context_pack_v1",
        "mode": "post_ingestion_qa",
        "compiled_predicate_inventory": {
            "signatures": kb_inventory.get("signatures", [])[:120],
            "counts": kb_inventory.get("counts", {}),
            "examples": kb_inventory.get("examples", {}),
        },
        "relevant_clauses": [*facts[:260], *rules[:80]],
        "source_fact_count": len(facts),
        "source_rule_count": len(rules),
    }
    started = time.perf_counter()
    try:
        result = call_semantic_ir(
            utterance=utterance,
            config=config,
            context=[],
            domain_context=domain_context,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
            kb_context_pack=kb_context_pack,
            domain="post_ingestion_qa",
            include_model_input=include_model_input,
        )
    except Exception as exc:
        return {**item, "ok": False, "error": str(exc), "latency_ms": int((time.perf_counter() - started) * 1000)}
    ir = result.get("parsed") if isinstance(result, dict) else None
    row: dict[str, Any] = {
        **item,
        "ok": isinstance(ir, dict),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parse_error": str(result.get("parse_error", "")) if isinstance(result, dict) else "",
        "model_decision": ir.get("decision", "") if isinstance(ir, dict) else "",
    }
    if include_model_input and isinstance(result, dict):
        row["model_input"] = result.get("model_input", {})
    if not isinstance(ir, dict):
        row["raw_content"] = str(result.get("content", ""))[:4000] if isinstance(result, dict) else ""
        return row
    mapped, warnings = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    clauses = diagnostics.get("clauses", {}) if isinstance(diagnostics.get("clauses"), dict) else {}
    queries = [str(q).strip() for q in clauses.get("queries", []) if str(q).strip()]
    facts_out = [str(q).strip() for q in clauses.get("facts", []) if str(q).strip()]
    rules_out = [str(q).strip() for q in clauses.get("rules", []) if str(q).strip()]
    query_results = [{"query": query, "result": runtime.query_rows(query)} for query in queries]
    row.update(
        {
            "projected_decision": diagnostics.get("projected_decision", ""),
            "warnings": warnings,
            "queries": queries,
            "proposed_facts": facts_out,
            "proposed_rules": rules_out,
            "query_results": query_results,
            "oracle": oracle,
            "reference_answer": str(oracle.get("reference_answer", "")),
            "self_check": ir.get("self_check", {}),
        }
    )
    row["oracle_match"] = score_oracle(row=row, oracle=oracle)
    return row


def score_oracle(*, row: dict[str, Any], oracle: dict[str, Any]) -> bool | None:
    if not oracle:
        return None
    has_structured_expectation = any(
        key in oracle for key in ("expected_decision", "expected_query_predicates", "expected_answer_contains")
    )
    if not has_structured_expectation:
        return None
    expected_decision = str(oracle.get("expected_decision", "")).strip()
    if expected_decision and str(row.get("projected_decision") or row.get("model_decision", "")).strip() != expected_decision:
        return False
    expected_predicates = [str(item).strip() for item in oracle.get("expected_query_predicates", []) if str(item).strip()]
    if expected_predicates:
        actual = {query.split("(", 1)[0].strip() for query in row.get("queries", [])}
        if not set(expected_predicates).issubset(actual):
            return False
    contains = [str(item).strip() for item in oracle.get("expected_answer_contains", []) if str(item).strip()]
    if contains:
        haystack = json.dumps(row.get("query_results", []), ensure_ascii=False)
        if not all(item in haystack for item in contains):
            return False
    return True


def summarize(*, rows: list[dict[str, Any]], load_errors: list[str], elapsed_ms: int) -> dict[str, Any]:
    oracle_rows = [row for row in rows if isinstance(row.get("oracle_match"), bool)]
    return {
        "question_count": len(rows),
        "reference_answer_rows": sum(1 for row in rows if row.get("reference_answer")),
        "parsed_ok": sum(1 for row in rows if row.get("ok")),
        "query_rows": sum(1 for row in rows if row.get("queries")),
        "write_proposal_rows": sum(1 for row in rows if row.get("proposed_facts") or row.get("proposed_rules")),
        "oracle_rows": len(oracle_rows),
        "oracle_match": sum(1 for row in oracle_rows if row.get("oracle_match") is True),
        "runtime_load_error_count": len(load_errors),
        "elapsed_ms": elapsed_ms,
    }


def write_summary(record: dict[str, Any], path: Path) -> None:
    summary = record.get("summary", {})
    lines = [
        "# Domain Bootstrap QA Run",
        "",
        f"- Run JSON: `{record.get('run_json', '')}`",
        f"- QA file: `{record.get('qa_file', '')}`",
        f"- Model: `{record.get('model', '')}`",
        f"- Source facts/rules: `{record.get('source_fact_count', 0)}` / `{record.get('source_rule_count', 0)}`",
        f"- Questions: `{summary.get('question_count', 0)}`",
        f"- Parsed OK: `{summary.get('parsed_ok', 0)}`",
        f"- Rows with queries: `{summary.get('query_rows', 0)}`",
        f"- Rows with proposed writes: `{summary.get('write_proposal_rows', 0)}`",
        f"- Oracle rows/matches: `{summary.get('oracle_rows', 0)}` / `{summary.get('oracle_match', 0)}`",
        "",
        "## Rows",
        "",
    ]
    for row in record.get("rows", []):
        lines.extend(
            [
                f"### {row.get('id', '')} - {row.get('utterance', '')}",
                "",
                f"- Phase: `{row.get('phase', '')}`",
                f"- Decision: model=`{row.get('model_decision', '')}` projected=`{row.get('projected_decision', '')}`",
                f"- Queries: `{row.get('queries', [])}`",
                f"- Proposed writes: facts=`{len(row.get('proposed_facts', []) or [])}` rules=`{len(row.get('proposed_rules', []) or [])}`",
                f"- Oracle match: `{row.get('oracle_match', None)}`",
                f"- Reference answer: {row.get('reference_answer', '') or '-'}",
                "",
                "```json",
                json.dumps(row.get("query_results", []), ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip()).strip("-").lower()
    return text[:60] or "run"


if __name__ == "__main__":
    raise SystemExit(main())
