#!/usr/bin/env python3
"""Audit retrieval-constrained palette grounding without changing compile behavior.

This is a diagnostic bridge, not the final constrained compiler. It uses
existing compile candidate palettes as the registry and boundary-plan rows as
the observable pressure coordinates. Because current compile artifacts do not
attach every admitted fact to a source span, this audit measures coordinate-level
retrieval recall rather than true span-level retrieval.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TOKEN_RE = re.compile(r"[a-z0-9]+")
SIGNATURE_RE = re.compile(r"^([a-z][a-z0-9_]*)/([1-9][0-9]*)$")
NON_CANONICAL_HINT_PREFIXES = ("source_record_", "source_detail", "source_note", "memberchk")


@dataclass(frozen=True)
class RegistryEntry:
    signature: str
    predicate: str
    arity: int
    category: str
    tokens: frozenset[str]
    fixtures: frozenset[str]


def _tokens(value: Any) -> set[str]:
    text = str(value or "").casefold().replace("_", " ").replace("-", " ")
    return {token for token in TOKEN_RE.findall(text) if len(token) > 1}


def _signature(item: dict[str, Any]) -> str:
    raw = str(item.get("signature", "")).strip().casefold()
    if SIGNATURE_RE.fullmatch(raw):
        return raw
    name = str(item.get("name") or item.get("predicate") or "").strip().casefold()
    args = item.get("args", [])
    if name and re.fullmatch(r"[a-z][a-z0-9_]*", name) and isinstance(args, list):
        return f"{name}/{len(args)}"
    return ""


def _category(signature: str, metadata_tokens: set[str]) -> str:
    name = signature.split("/", 1)[0]
    tokens = set(name.split("_")) | metadata_tokens
    if tokens & {"authority", "authorized", "authorize", "approved", "approver", "issuer", "order", "rule"}:
        return "source_authority"
    if tokens & {"filed", "received", "withdrawn", "denied", "record", "register", "docket", "entry", "status", "phase"}:
        return "operational_record"
    if tokens & {"date", "time", "timestamp", "deadline", "interval", "duration", "current", "prior"}:
        return "temporal"
    if tokens & {"count", "total", "amount", "value", "rate", "threshold", "limit", "quantity"}:
        return "quantity"
    if tokens & {"custody", "holder", "owner", "possession", "access", "location"}:
        return "custody_location"
    if tokens & {"role", "person", "actor", "participant", "member", "group", "assignment"}:
        return "identity_role"
    if tokens & {"evidence", "claim", "finding", "statement", "reported", "source"}:
        return "evidence_provenance"
    return "other"


def _expand_compile_paths(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        path = raw if raw.is_absolute() else (REPO_ROOT / raw).resolve()
        if path.is_file():
            out.append(path)
        elif path.is_dir():
            direct = sorted(path.glob("domain_bootstrap_file_*.json"))
            if direct:
                out.append(direct[-1])
            else:
                for child in sorted(path.iterdir()):
                    if child.is_dir():
                        files = sorted(child.glob("domain_bootstrap_file_*.json"))
                        if files:
                            out.append(files[-1])
    return sorted(dict.fromkeys(out))


def _load_registry(paths: list[Path]) -> tuple[dict[str, RegistryEntry], dict[str, str]]:
    rows: dict[str, dict[str, Any]] = {}
    compile_by_fixture: dict[str, str] = {}
    for path in _expand_compile_paths(paths):
        fixture = path.parent.name
        compile_by_fixture[fixture] = str(path)
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
        for item in parsed.get("candidate_predicates", []) if isinstance(parsed.get("candidate_predicates"), list) else []:
            if not isinstance(item, dict):
                continue
            signature = _signature(item)
            if not signature:
                continue
            name, arity_text = signature.rsplit("/", 1)
            metadata = set(name.split("_"))
            for field in ("description", "why", "notes"):
                metadata |= _tokens(item.get(field))
            for arg in item.get("args", []) if isinstance(item.get("args"), list) else []:
                metadata |= _tokens(arg)
            for note in item.get("admission_notes", []) if isinstance(item.get("admission_notes"), list) else []:
                metadata |= _tokens(note)
            bucket = rows.setdefault(
                signature,
                {
                    "predicate": name,
                    "arity": int(arity_text),
                    "tokens": set(),
                    "fixtures": set(),
                },
            )
            bucket["tokens"].update(metadata)
            bucket["fixtures"].add(fixture)
    registry: dict[str, RegistryEntry] = {}
    for signature, row in rows.items():
        tokens = set(row["tokens"])
        registry[signature] = RegistryEntry(
            signature=signature,
            predicate=str(row["predicate"]),
            arity=int(row["arity"]),
            category=_category(signature, tokens),
            tokens=frozenset(tokens),
            fixtures=frozenset(row["fixtures"]),
        )
    return registry, compile_by_fixture


def _load_boundary_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = payload.get("coordinates")
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def _context_tokens(row: dict[str, Any]) -> set[str]:
    values = [
        row.get("question", ""),
        row.get("rationale", ""),
        row.get("failure_surface", ""),
        row.get("compile_surface_class", ""),
        row.get("hybrid_join_class", ""),
        row.get("status_timeline_density_class", ""),
        row.get("status_count_evidence_class", ""),
    ]
    tokens: set[str] = set()
    for value in values:
        tokens |= _tokens(value)
    return tokens


def _target_categories(context: set[str]) -> set[str]:
    categories: set[str] = set()
    if context & {"authority", "authorized", "approve", "approved", "issuer", "order", "rule", "policy"}:
        categories.add("source_authority")
    if context & {"record", "status", "filed", "received", "denied", "withdrawn", "register", "docket", "entry"}:
        categories.add("operational_record")
    if context & {"date", "deadline", "current", "prior", "superseded", "effective", "before", "after"}:
        categories.add("temporal")
    if context & {"count", "total", "how", "many", "amount", "value", "rate", "threshold"}:
        categories.add("quantity")
    if context & {"custody", "access", "holder", "owner", "location", "located", "possession"}:
        categories.add("custody_location")
    if context & {"role", "person", "member", "group", "assigned", "assignment"}:
        categories.add("identity_role")
    if context & {"evidence", "claim", "finding", "statement", "reported"}:
        categories.add("evidence_provenance")
    return categories


def _hint_signatures(row: dict[str, Any], registry: dict[str, RegistryEntry]) -> set[str]:
    hints = row.get("predicate_hints", [])
    out: set[str] = set()
    if not isinstance(hints, list):
        return out
    for hint in hints:
        name = str(hint or "").strip().casefold()
        if not name or name.startswith(NON_CANONICAL_HINT_PREFIXES):
            continue
        for signature, entry in registry.items():
            if entry.predicate == name:
                out.add(signature)
    return out


def _score(entry: RegistryEntry, context: set[str], target_categories: set[str]) -> float:
    if not context:
        return 0.0
    overlap = entry.tokens & context
    if not overlap:
        lexical = 0.0
    else:
        lexical = len(overlap) / math.sqrt(max(1, len(entry.tokens)))
    category_boost = 2.5 if entry.category in target_categories else 0.0
    exact_name_boost = 0.0
    name_tokens = set(entry.predicate.split("_"))
    if name_tokens and name_tokens <= context:
        exact_name_boost = 1.0
    return lexical + category_boost + exact_name_boost


def _classify(row: dict[str, Any], retrieved: list[str], hint_signatures: set[str], registry: dict[str, RegistryEntry]) -> str:
    if not hint_signatures:
        return "no_non_source_hint"
    in_registry = {signature for signature in hint_signatures if signature in registry}
    if not in_registry:
        return "true_palette_gap"
    if in_registry & set(retrieved):
        return "schema_recalled"
    hint_categories = {registry[signature].category for signature in in_registry if signature in registry}
    retrieved_categories = {registry[signature].category for signature in retrieved if signature in registry}
    if hint_categories & retrieved_categories:
        return "family_recalled_schema_missed"
    return "missed_schema"


def run_audit(
    *,
    compile_paths: list[Path],
    boundary_plan: Path,
    fixtures: set[str],
    failure_surfaces: set[str],
    k_values: list[int],
) -> dict[str, Any]:
    registry, compile_by_fixture = _load_registry(compile_paths)
    boundary_rows = _load_boundary_rows(boundary_plan)
    selected = []
    for row in boundary_rows:
        fixture = str(row.get("fixture", ""))
        surface = str(row.get("failure_surface", ""))
        if fixtures and fixture not in fixtures:
            continue
        if failure_surfaces and surface not in failure_surfaces:
            continue
        selected.append(row)

    audits: list[dict[str, Any]] = []
    by_k: dict[str, Counter[str]] = {str(k): Counter() for k in k_values}
    category_spread: dict[str, list[int]] = {str(k): [] for k in k_values}
    for row in selected:
        context = _context_tokens(row)
        targets = _target_categories(context)
        hint_signatures = _hint_signatures(row, registry)
        scored = sorted(
            (
                (_score(entry, context, targets), signature)
                for signature, entry in registry.items()
            ),
            key=lambda item: (-item[0], item[1]),
        )
        k_results = {}
        for k in k_values:
            retrieved = [signature for score, signature in scored[:k] if score > 0]
            verdict = _classify(row, retrieved, hint_signatures, registry)
            by_k[str(k)][verdict] += 1
            category_spread[str(k)].append(len({registry[sig].category for sig in retrieved if sig in registry}))
            k_results[str(k)] = {
                "verdict": verdict,
                "retrieved": retrieved,
                "retrieved_categories": sorted({registry[sig].category for sig in retrieved if sig in registry}),
                "hint_overlap": sorted(set(retrieved) & hint_signatures),
            }
        audits.append(
            {
                "fixture": row.get("fixture", ""),
                "question_id": row.get("id", ""),
                "failure_surface": row.get("failure_surface", ""),
                "compile_surface_class": row.get("compile_surface_class", ""),
                "hybrid_join_class": row.get("hybrid_join_class", ""),
                "context_categories": sorted(targets),
                "hint_signatures": sorted(hint_signatures),
                "k_results": k_results,
                "question": row.get("question", ""),
            }
        )
    summary_by_k = {}
    for k in k_values:
        key = str(k)
        count = sum(by_k[key].values())
        avg_category_spread = (
            round(sum(category_spread[key]) / len(category_spread[key]), 3)
            if category_spread[key]
            else 0.0
        )
        summary_by_k[key] = {
            "row_count": count,
            "verdict_counts": dict(sorted(by_k[key].items())),
            "schema_recall_rate": round(by_k[key].get("schema_recalled", 0) / count, 4) if count else 0.0,
            "avg_retrieved_category_spread": avg_category_spread,
        }
    return {
        "schema_version": "retrieval_constrained_palette_audit_v1",
        "scope_note": (
            "Audit-only coordinate-level proxy. Current compile artifacts do not yet attach every admitted row "
            "to source spans, so this measures boundary-coordinate retrieval against candidate palettes, not final "
            "span-level constrained decoding."
        ),
        "registry_signature_count": len(registry),
        "compile_fixture_count": len(compile_by_fixture),
        "selected_fixture_count": len(fixtures) if fixtures else len(set(row.get("fixture", "") for row in selected)),
        "selected_row_count": len(selected),
        "k_values": k_values,
        "summary_by_k": summary_by_k,
        "registry_category_counts": dict(sorted(Counter(entry.category for entry in registry.values()).items())),
        "fixtures": sorted(fixtures) if fixtures else sorted(set(row.get("fixture", "") for row in selected)),
        "failure_surfaces": sorted(failure_surfaces),
        "audits": audits,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Retrieval-Constrained Palette Audit",
        "",
        f"- Schema: `{report.get('schema_version')}`",
        f"- Registry signatures: `{report.get('registry_signature_count')}`",
        f"- Compile fixtures: `{report.get('compile_fixture_count')}`",
        f"- Selected fixtures: `{report.get('selected_fixture_count')}`",
        f"- Selected boundary rows: `{report.get('selected_row_count')}`",
        "",
        str(report.get("scope_note", "")),
        "",
        "## Summary By K",
        "",
        "| k | Rows | Schema recall | Verdicts | Avg category spread |",
        "| ---: | ---: | ---: | --- | ---: |",
    ]
    for key, summary in (report.get("summary_by_k") or {}).items():
        lines.append(
            f"| {key} | {summary.get('row_count', 0)} | {summary.get('schema_recall_rate', 0)} | "
            f"`{summary.get('verdict_counts', {})}` | {summary.get('avg_retrieved_category_spread', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Registry Categories",
            "",
        ]
    )
    for category, count in (report.get("registry_category_counts") or {}).items():
        lines.append(f"- `{category}`: `{count}`")
    lines.extend(
        [
            "",
            "## Missed Schema Samples",
            "",
        ]
    )
    sample_count = 0
    for row in report.get("audits", []):
        k_results = row.get("k_results", {})
        result = k_results.get(str(max(report.get("k_values", [0]))), {})
        if result.get("verdict") != "missed_schema":
            continue
        sample_count += 1
        lines.extend(
            [
                f"### {row.get('fixture')} / {row.get('question_id')}",
                "",
                f"- Surface: `{row.get('failure_surface')}`",
                f"- Class: `{row.get('compile_surface_class') or row.get('hybrid_join_class')}`",
                f"- Hint signatures: `{row.get('hint_signatures', [])}`",
                f"- Retrieved: `{result.get('retrieved', [])[:10]}`",
                f"- Question: {row.get('question')}",
                "",
            ]
        )
        if sample_count >= 12:
            break
    if sample_count == 0:
        lines.append("No missed-schema samples at the largest k.")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-json", action="append", type=Path, default=[])
    parser.add_argument("--boundary-plan-json", type=Path, required=True)
    parser.add_argument("--fixture", action="append", default=[])
    parser.add_argument(
        "--failure-surface",
        action="append",
        default=["compile_surface_gap", "hybrid_join_gap", "query_surface_gap"],
    )
    parser.add_argument("--k", action="append", type=int, default=[5, 10, 20])
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()

    boundary_plan = args.boundary_plan_json if args.boundary_plan_json.is_absolute() else (REPO_ROOT / args.boundary_plan_json).resolve()
    report = run_audit(
        compile_paths=args.compile_json,
        boundary_plan=boundary_plan,
        fixtures={str(item) for item in args.fixture if str(item).strip()},
        failure_surfaces={str(item) for item in args.failure_surface if str(item).strip()},
        k_values=sorted({int(k) for k in args.k if int(k) > 0}),
    )
    out_json = args.out_json if args.out_json.is_absolute() else (REPO_ROOT / args.out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        out_md = args.out_md if args.out_md.is_absolute() else (REPO_ROOT / args.out_md).resolve()
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "out_json": str(out_json),
                "registry_signature_count": report["registry_signature_count"],
                "selected_row_count": report["selected_row_count"],
                "summary_by_k": report["summary_by_k"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
