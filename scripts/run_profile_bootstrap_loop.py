#!/usr/bin/env python3
"""Run a bootstrapped profile draft through the normal Semantic IR path.

The profile bootstrap model proposes a vocabulary. This runner asks the next
question: if that proposed vocabulary is supplied as a draft profile, can the
ordinary Semantic IR compiler and deterministic mapper use it safely on the
starter frontier cases?

Artifacts stay under tmp/ because the profile remains review material.
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
DEFAULT_BOOTSTRAP_DIR = REPO_ROOT / "tmp" / "profile_bootstrap"
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "profile_bootstrap_loop"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.profile_bootstrap import (  # noqa: E402
    profile_bootstrap_allowed_predicates,
    profile_bootstrap_domain_context,
    profile_bootstrap_frontier_cases,
    profile_bootstrap_predicate_contracts,
    profile_bootstrap_score,
)
from src.semantic_ir import (  # noqa: E402
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Close the loop on a profile_bootstrap_v1 draft.")
    parser.add_argument(
        "--profile-run",
        type=Path,
        default=None,
        help="Path to a profile_bootstrap run JSON. Defaults to latest tmp/profile_bootstrap JSON.",
    )
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
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--include-model-input", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile_path = _resolve_profile_path(args.profile_run)
    record = json.loads(profile_path.read_text(encoding="utf-8"))
    parsed_profile = record.get("parsed") if isinstance(record.get("parsed"), dict) else record
    bootstrap_score = profile_bootstrap_score(parsed_profile)
    cases = profile_bootstrap_frontier_cases(parsed_profile)
    if int(args.limit or 0) > 0:
        cases = cases[: int(args.limit)]
    allowed_predicates = profile_bootstrap_allowed_predicates(parsed_profile)
    predicate_contracts = profile_bootstrap_predicate_contracts(parsed_profile)
    domain_context = profile_bootstrap_domain_context(parsed_profile)
    domain = f"profile_bootstrap:{parsed_profile.get('domain_guess', 'unknown')}"

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
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(str(parsed_profile.get('domain_guess', 'bootstrap')))}_{_slug(model)}"
    jsonl_path = out_dir / f"profile_bootstrap_loop_{slug}.jsonl"
    summary_path = jsonl_path.with_suffix(".md")

    rows: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] {case['id']}", flush=True)
        row = run_case(
            case=case,
            config=config,
            domain=domain,
            domain_context=domain_context,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
            include_model_input=bool(args.include_model_input),
        )
        rows.append(row)
        with jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = summarize_loop(rows, bootstrap_score=bootstrap_score)
    write_summary(
        {
            "profile_path": str(profile_path),
            "backend": backend,
            "model": model,
            "domain": domain,
            "bootstrap_score": bootstrap_score,
            "allowed_predicates": allowed_predicates,
            "predicate_contract_count": len(predicate_contracts),
            "domain_context_count": len(domain_context),
            "summary": summary,
            "rows": rows,
        },
        summary_path,
    )
    print(f"Wrote {jsonl_path}")
    print(f"Wrote {summary_path}")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def run_case(
    *,
    case: dict[str, Any],
    config: SemanticIRCallConfig,
    domain: str,
    domain_context: list[str],
    allowed_predicates: list[str],
    predicate_contracts: list[dict[str, Any]],
    include_model_input: bool,
) -> dict[str, Any]:
    started = time.perf_counter()
    utterance = str(case.get("utterance", "")).strip()
    expected_boundary = str(case.get("expected_boundary", "")).strip()
    must_not_write = [str(item).strip() for item in case.get("must_not_write", []) if str(item).strip()]
    row: dict[str, Any] = {
        "ts": _utc_now(),
        "case_id": str(case.get("id", "")),
        "utterance": utterance,
        "expected_boundary": expected_boundary,
        "must_not_write": must_not_write,
        "parsed_ok": False,
        "model_decision": "",
        "projected_decision": "",
        "admitted_count": 0,
        "skipped_count": 0,
        "expected_positive_refs": sorted(_predicate_refs(expected_boundary)),
        "must_not_refs": sorted(_predicate_refs(" ".join(must_not_write))),
        "must_not_write_keys": sorted(_clause_keys(" ".join(must_not_write))),
        "admitted_signatures": [],
        "admitted_write_keys": [],
        "expected_ref_hits": [],
        "must_not_write_violations": [],
        "out_of_palette_skip_count": 0,
        "error": "",
    }
    try:
        result = call_semantic_ir(
            utterance=utterance,
            config=config,
            context=[
                "This turn is a starter frontier case generated by profile_bootstrap_v1.",
                "Use the draft profile vocabulary and policies, but do not see evaluation labels.",
                "For direct source-grounded normative records, prefer operation='assert'. Use operation='rule' only with candidate_operations[].clause.",
            ],
            domain_context=domain_context,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
            kb_context_pack={},
            domain=domain,
            include_model_input=include_model_input,
        )
    except Exception as exc:
        row["error"] = str(exc)
        row["latency_ms"] = int((time.perf_counter() - started) * 1000)
        return row
    parsed = result.get("parsed") if isinstance(result, dict) else None
    row["latency_ms"] = int(result.get("latency_ms", 0) or ((time.perf_counter() - started) * 1000))
    row["content_channel"] = result.get("content_channel", "")
    if include_model_input:
        row["model_input"] = result.get("model_input", {})
    if not isinstance(parsed, dict):
        row["error"] = str(result.get("parse_error", "semantic_ir_parse_failed"))
        row["raw_content"] = str(result.get("content", ""))[:4000]
        return row
    mapped, warnings = semantic_ir_to_legacy_parse(
        parsed,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    clauses_by_effect = _diagnostic_clauses_by_effect(diagnostics)
    clauses = [clause for values in clauses_by_effect.values() for clause in values]
    admitted_write_signatures = sorted(_clause_refs(" ".join(clauses_by_effect["facts"] + clauses_by_effect["rules"])))
    admitted_write_keys = sorted(_clause_keys(" ".join(clauses_by_effect["facts"] + clauses_by_effect["rules"])))
    admitted_signatures = sorted(_clause_refs(" ".join(clauses)))
    expected_refs = set(row["expected_positive_refs"])
    must_not_keys = set(row["must_not_write_keys"])
    warning_counts = diagnostics.get("warning_counts", {}) if isinstance(diagnostics, dict) else {}
    row.update(
        {
            "parsed_ok": True,
            "model_decision": parsed.get("decision", ""),
            "projected_decision": diagnostics.get("projected_decision", ""),
            "admitted_count": int(diagnostics.get("admitted_count", 0) or 0),
            "skipped_count": int(diagnostics.get("skipped_count", 0) or 0),
            "warning_counts": warning_counts,
            "mapper_warnings": warnings,
            "admitted_clauses": clauses,
            "admitted_clauses_by_effect": clauses_by_effect,
            "admitted_signatures": admitted_signatures,
            "admitted_write_signatures": admitted_write_signatures,
            "admitted_write_keys": admitted_write_keys,
            "expected_ref_hits": sorted(expected_refs & set(admitted_write_signatures)),
            "must_not_write_violations": sorted(must_not_keys & set(admitted_write_keys)),
            "out_of_palette_skip_count": int(warning_counts.get("out_of_palette_predicate", 0) or 0),
            "parsed": parsed,
        }
    )
    return row


def summarize_loop(rows: list[dict[str, Any]], *, bootstrap_score: dict[str, Any]) -> dict[str, Any]:
    total = len(rows)
    parsed_ok = sum(1 for row in rows if row.get("parsed_ok"))
    zero_palette_skips = sum(1 for row in rows if not int(row.get("out_of_palette_skip_count", 0) or 0))
    zero_must_not = sum(1 for row in rows if not row.get("must_not_write_violations"))
    any_expected_hit = sum(
        1
        for row in rows
        if not row.get("expected_positive_refs") or bool(row.get("expected_ref_hits"))
    )
    admitted_total = sum(int(row.get("admitted_count", 0) or 0) for row in rows)
    rough_score = 0.0
    if total:
        rough_score = (
            parsed_ok / total
            + zero_palette_skips / total
            + zero_must_not / total
            + any_expected_hit / total
        ) / 4
    return {
        "cases": total,
        "parsed_ok": parsed_ok,
        "zero_out_of_palette_skip_cases": zero_palette_skips,
        "zero_must_not_violation_cases": zero_must_not,
        "expected_ref_hit_cases": any_expected_hit,
        "admitted_total": admitted_total,
        "rough_score": round(float(rough_score), 3),
        "bootstrap_rough_score": bootstrap_score.get("rough_score", 0.0),
    }


def write_summary(record: dict[str, Any], path: Path) -> None:
    summary = record.get("summary", {})
    lines = [
        "# Profile Bootstrap Closed Loop",
        "",
        f"Generated: {_utc_now()}",
        "",
        f"- Profile run: `{record.get('profile_path', '')}`",
        f"- Backend/model: `{record.get('backend', '')}` / `{record.get('model', '')}`",
        f"- Domain: `{record.get('domain', '')}`",
        f"- Bootstrap score: `{summary.get('bootstrap_rough_score', 0.0)}`",
        f"- Loop rough score: `{summary.get('rough_score', 0.0)}`",
        f"- Cases: `{summary.get('cases', 0)}`",
        f"- Parsed OK: `{summary.get('parsed_ok', 0)}`",
        f"- Zero out-of-palette skip cases: `{summary.get('zero_out_of_palette_skip_cases', 0)}`",
        f"- Zero must-not violation cases: `{summary.get('zero_must_not_violation_cases', 0)}`",
        f"- Expected-ref hit cases: `{summary.get('expected_ref_hit_cases', 0)}`",
        f"- Admitted total: `{summary.get('admitted_total', 0)}`",
        "",
        "## Draft Predicates",
        "",
    ]
    lines.extend([f"- `{item}`" for item in record.get("allowed_predicates", [])] or ["- none"])
    lines.extend(["", "## Case Results", ""])
    for row in record.get("rows", []):
        lines.extend(
            [
                f"### {row.get('case_id', '')}",
                "",
                f"- Parsed: `{row.get('parsed_ok', False)}`",
                f"- Decision: model `{row.get('model_decision', '')}`, projected `{row.get('projected_decision', '')}`",
                f"- Admission: `{row.get('admitted_count', 0)}` admitted, `{row.get('skipped_count', 0)}` skipped",
                f"- Expected refs: `{row.get('expected_positive_refs', [])}`",
                f"- Expected hits: `{row.get('expected_ref_hits', [])}`",
                f"- Must-not violations: `{row.get('must_not_write_violations', [])}`",
                f"- Out-of-palette skips: `{row.get('out_of_palette_skip_count', 0)}`",
                f"- Utterance: {row.get('utterance', '')}",
                "",
                "Admitted clauses by effect:",
                "",
            ]
        )
        clauses_by_effect = row.get("admitted_clauses_by_effect", {})
        wrote_any = False
        if isinstance(clauses_by_effect, dict):
            for effect in ("facts", "rules", "queries", "retracts"):
                clauses = clauses_by_effect.get(effect, [])
                if not isinstance(clauses, list) or not clauses:
                    continue
                wrote_any = True
                lines.append(f"- {effect}:")
                lines.extend([f"  - `{clause}`" for clause in clauses])
        if not wrote_any:
            lines.append("- none")
        if row.get("error"):
            lines.extend(["", f"Error: `{row.get('error')}`"])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _diagnostic_clauses_by_effect(diagnostics: dict[str, Any]) -> dict[str, list[str]]:
    clauses: dict[str, list[str]] = {
        "facts": [],
        "rules": [],
        "queries": [],
        "retracts": [],
    }
    source = diagnostics.get("clauses", {}) if isinstance(diagnostics, dict) else {}
    if not isinstance(source, dict):
        return clauses
    for key in ("facts", "rules", "queries", "retracts"):
        values = source.get(key, [])
        if isinstance(values, list):
            clauses[key].extend(str(item).strip() for item in values if str(item).strip())
    return clauses


def _resolve_profile_path(path: Path | None) -> Path:
    if isinstance(path, Path):
        return path if path.is_absolute() else (REPO_ROOT / path).resolve()
    candidates = sorted(DEFAULT_BOOTSTRAP_DIR.glob("profile_bootstrap_*.json"), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError("No profile_bootstrap_*.json files found under tmp/profile_bootstrap.")
    return candidates[-1]


def _predicate_refs(text: str) -> set[str]:
    refs: set[str] = set()
    raw = str(text or "")
    for match in re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)/(\d+)\b", raw):
        refs.add(f"{match.group(1).casefold()}/{match.group(2)}")
    refs.update(_clause_refs(raw))
    return refs


def _clause_refs(text: str) -> set[str]:
    refs: set[str] = set()
    raw = str(text or "")
    for match in re.finditer(r"\b([a-z][a-z0-9_]*)\s*\(", raw):
        name = match.group(1).casefold()
        close_index = _matching_paren(raw, match.end() - 1)
        if close_index is None:
            continue
        refs.add(f"{name}/{_arity(raw[match.end():close_index])}")
    return refs


def _clause_keys(text: str) -> set[str]:
    keys: set[str] = set()
    raw = str(text or "")
    for match in re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", raw):
        name = match.group(1).casefold()
        close_index = _matching_paren(raw, match.end() - 1)
        if close_index is None:
            continue
        args = [_normalize_atom(arg) for arg in _split_top_level_args(raw[match.end():close_index])]
        keys.add(f"{name}({','.join(args)})")
    return keys


def _split_top_level_args(args_text: str) -> list[str]:
    text = str(args_text or "").strip()
    if not text:
        return []
    args: list[str] = []
    depth = 0
    current: list[str] = []
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        args.append(tail)
    return args


def _normalize_atom(value: str) -> str:
    text = str(value or "").strip().strip(".")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").casefold()
    return text or "empty"


def _matching_paren(text: str, open_index: int) -> int | None:
    depth = 0
    for index in range(open_index, len(text)):
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def _arity(args_text: str) -> int:
    text = str(args_text or "").strip()
    if not text:
        return 0
    depth = 0
    count = 1
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            count += 1
    return count


def _slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip()).strip("-").lower()
    return text[:80] or "run"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
