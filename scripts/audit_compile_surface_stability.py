#!/usr/bin/env python3
"""Compare compile draws for direct-surface stability.

This audit is intentionally post-hoc. It does not merge facts or repair a
compile. It asks whether multiple draws of the same source preserve the same
direct predicate palette and direct fact rows.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
SURFACE_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("assignment_binding_surface", ("assigned", "assignment")),
    ("task_scope_surface", ("task", "review", "inspection", "testing", "verification")),
    ("status_phase_surface", ("status", "phase", "pending", "closed", "complete")),
    ("identity_role_surface", ("person", "role", "name", "actor")),
    ("object_record_surface", ("record", "ticket", "docket", "file", "packet", "equipment", "sample")),
    ("completion_transition_surface", ("completed", "closed", "finished", "moved", "transition")),
)


def audit_paths(paths: list[Path]) -> dict[str, Any]:
    expanded = _expand_compile_paths(paths)
    draws_by_fixture: dict[str, list[dict[str, Any]]] = {}
    for path in expanded:
        draw = _load_draw(path)
        draws_by_fixture.setdefault(draw["fixture"], []).append(draw)

    fixtures = []
    for fixture, draws in sorted(draws_by_fixture.items()):
        fixtures.append(_audit_fixture(fixture, draws))

    return {
        "schema_version": "compile_surface_stability_audit_v1",
        "compile_count": len(expanded),
        "fixture_count": len(fixtures),
        "summary": _summarize(fixtures),
        "fixtures": fixtures,
    }


def _expand_compile_paths(inputs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for item in inputs:
        if item.is_file():
            out.append(item)
            continue
        if not item.is_dir():
            continue
        direct = sorted(item.glob("domain_bootstrap_file_*.json"))
        if direct:
            out.append(direct[-1])
            continue
        out.extend(sorted(item.glob("*/domain_bootstrap_file_*.json")))
    return sorted(dict.fromkeys(path.resolve() for path in out))


def _load_draw(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    facts = _facts_from_compile(payload)
    direct_facts = sorted(fact for fact in facts if not _predicate_name(fact).startswith("source_record"))
    source_facts = sorted(fact for fact in facts if _predicate_name(fact).startswith("source_record"))
    direct_rows = _fact_rows(direct_facts)
    source_texts = _source_text_atoms(source_facts)
    predicate_counts: dict[str, int] = {}
    for fact in direct_facts:
        predicate = _predicate_name(fact)
        if predicate:
            predicate_counts[predicate] = predicate_counts.get(predicate, 0) + 1
    return {
        "compile_json": str(path),
        "fixture": path.parent.name,
        "run": path.parent.parent.name,
        "parsed_ok": bool(payload.get("parsed_ok")),
        "direct_fact_count": len(direct_facts),
        "direct_predicate_count": len(predicate_counts),
        "direct_facts": direct_facts,
        "predicate_counts": dict(sorted(predicate_counts.items())),
        "surface_counts": _surface_counts(direct_facts),
        "contracts": _contract_reports(source_texts=source_texts, direct_rows=direct_rows),
    }


def _facts_from_compile(payload: dict[str, Any]) -> list[str]:
    source_compile = payload.get("source_compile") if isinstance(payload.get("source_compile"), dict) else {}
    facts = source_compile.get("facts")
    if isinstance(facts, list):
        return [str(fact).strip() for fact in facts if str(fact).strip()]
    parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
    parsed_facts = parsed.get("facts")
    if isinstance(parsed_facts, list):
        return [str(fact).strip() for fact in parsed_facts if str(fact).strip()]
    return []


def _audit_fixture(fixture: str, draws: list[dict[str, Any]]) -> dict[str, Any]:
    fact_sets = [set(draw["direct_facts"]) for draw in draws]
    union_facts = set().union(*fact_sets) if fact_sets else set()
    common_facts = set.intersection(*fact_sets) if fact_sets else set()
    unstable_facts = sorted(union_facts - common_facts)
    predicate_names = sorted({name for draw in draws for name in draw["predicate_counts"]})
    predicate_drift = []
    for predicate in predicate_names:
        counts = [int(draw["predicate_counts"].get(predicate, 0)) for draw in draws]
        if len(set(counts)) <= 1:
            continue
        predicate_drift.append(
            {
                "predicate": predicate,
                "counts": counts,
                "min": min(counts),
                "max": max(counts),
                "delta": max(counts) - min(counts),
            }
        )
    surface_names = sorted({name for draw in draws for name in draw["surface_counts"]})
    surface_drift = []
    for surface in surface_names:
        counts = [int(draw["surface_counts"].get(surface, 0)) for draw in draws]
        if len(set(counts)) <= 1:
            continue
        surface_drift.append(
            {
                "surface": surface,
                "counts": counts,
                "min": min(counts),
                "max": max(counts),
                "delta": max(counts) - min(counts),
            }
        )
    missing_by_draw = []
    for draw, fact_set in zip(draws, fact_sets):
        missing = sorted(union_facts - fact_set)
        missing_by_draw.append(
            {
                "compile_json": draw["compile_json"],
                "run": draw["run"],
                "missing_union_fact_count": len(missing),
                "missing_union_facts": missing[:25],
            }
        )
    return {
        "fixture": fixture,
        "draw_count": len(draws),
        "stable": not unstable_facts,
        "union_fact_count": len(union_facts),
        "common_fact_count": len(common_facts),
        "unstable_fact_count": len(unstable_facts),
        "predicate_drift": predicate_drift,
        "surface_drift": surface_drift,
        "draws": [
            {
                "compile_json": draw["compile_json"],
                "run": draw["run"],
                "parsed_ok": draw["parsed_ok"],
                "direct_fact_count": draw["direct_fact_count"],
                "direct_predicate_count": draw["direct_predicate_count"],
                "surface_counts": draw["surface_counts"],
                "contracts": draw["contracts"],
            }
            for draw in draws
        ],
        "missing_by_draw": missing_by_draw,
    }


def _summarize(fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    unstable = [fixture for fixture in fixtures if not fixture["stable"]]
    return {
        "stable_fixture_count": len(fixtures) - len(unstable),
        "unstable_fixture_count": len(unstable),
        "unstable_fact_count": sum(int(fixture["unstable_fact_count"]) for fixture in fixtures),
        "predicate_drift_count": sum(len(fixture["predicate_drift"]) for fixture in fixtures),
        "surface_drift_count": sum(len(fixture["surface_drift"]) for fixture in fixtures),
    }


def _predicate_name(fact: str) -> str:
    match = FACT_RE.match(str(fact))
    return match.group(1) if match else ""


def _fact_rows(facts: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact in facts:
        match = FACT_RE.match(fact)
        if not match:
            continue
        rows.append({"predicate": match.group(1), "args": _split_fact_args(match.group(2))})
    return rows


def _split_fact_args(raw_args: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    depth = 0
    for char in raw_args:
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        if char in "([":
            depth += 1
        elif char in ")]" and depth > 0:
            depth -= 1
        current.append(char)
    if current:
        args.append("".join(current).strip())
    return args


def _source_text_atoms(source_facts: list[str]) -> list[str]:
    texts: list[str] = []
    for row in _fact_rows(source_facts):
        if row["predicate"] != "source_record_text_atom" or len(row["args"]) < 2:
            continue
        texts.append(str(row["args"][1]).strip().lower())
    return texts


def _contract_reports(*, source_texts: list[str], direct_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _parallel_assignment_contract(source_texts=source_texts, direct_rows=direct_rows),
        _source_authority_pair_contract(source_texts=source_texts, direct_rows=direct_rows),
    ]


def _parallel_assignment_contract(*, source_texts: list[str], direct_rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_mentions = [
        text
        for text in source_texts
        if ("assigned_to" in text or "was_assigned" in text or "assigned_" in text)
        and any(marker in text for marker in ("task", "review", "inspection", "testing", "verification", "scope"))
    ]
    direct_rows_found = [
        row
        for row in direct_rows
        if row["predicate"]
        in {
            "assigned_to",
            "record_assigned_to",
            "task_assigned",
            "task_assigned_to",
            "assignment_event",
            "assignment_scope",
        }
    ]
    return _contract_status(
        contract="parallel_assignment_event_preservation",
        source_signal_count=len(source_mentions),
        direct_surface_count=len(direct_rows_found),
        required_when_source_count_at_least=2,
    )


def _source_authority_pair_contract(*, source_texts: list[str], direct_rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_mentions = [
        text
        for text in source_texts
        if any(marker in text for marker in ("authority", "authorized", "court_order", "policy", "source", "governing"))
        and any(marker in text for marker in ("access", "finding", "status", "action", "subject", "item"))
    ]
    direct_rows_found = [
        row
        for row in direct_rows
        if row["predicate"]
        in {
            "access_authority_source",
            "access_source",
            "source_authority",
            "authority_source",
            "authorized_by",
            "governing_source",
            "court_order",
        }
    ]
    return _contract_status(
        contract="source_authority_pair_preservation",
        source_signal_count=len(source_mentions),
        direct_surface_count=len(direct_rows_found),
        required_when_source_count_at_least=1,
    )


def _contract_status(
    *,
    contract: str,
    source_signal_count: int,
    direct_surface_count: int,
    required_when_source_count_at_least: int,
) -> dict[str, Any]:
    if source_signal_count < required_when_source_count_at_least:
        status = "not_applicable"
    elif direct_surface_count >= source_signal_count:
        status = "pass"
    elif direct_surface_count > 0:
        status = "partial"
    else:
        status = "ledger_only"
    return {
        "contract": contract,
        "status": status,
        "source_signal_count": source_signal_count,
        "direct_surface_count": direct_surface_count,
    }


def _surface_counts(facts: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for fact in facts:
        predicate = _predicate_name(fact)
        text = f"{predicate} {fact}".lower()
        for surface, markers in SURFACE_GROUPS:
            if any(marker in text for marker in markers):
                counts[surface] = counts.get(surface, 0) + 1
    return dict(sorted(counts.items()))


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Compile Surface Stability Audit",
        "",
        f"- Compiles: `{report['compile_count']}`",
        f"- Fixtures: `{report['fixture_count']}`",
        f"- Stable fixtures: `{report['summary']['stable_fixture_count']}`",
        f"- Unstable fixtures: `{report['summary']['unstable_fixture_count']}`",
        f"- Unstable direct facts: `{report['summary']['unstable_fact_count']}`",
        f"- Predicate drift rows: `{report['summary']['predicate_drift_count']}`",
        f"- Surface drift rows: `{report['summary']['surface_drift_count']}`",
        "",
    ]
    for fixture in report["fixtures"]:
        lines.extend(
            [
                f"## `{fixture['fixture']}`",
                "",
                f"- Draws: `{fixture['draw_count']}`",
                f"- Stable: `{fixture['stable']}`",
                f"- Common / union direct facts: `{fixture['common_fact_count']} / {fixture['union_fact_count']}`",
                f"- Unstable direct facts: `{fixture['unstable_fact_count']}`",
                "",
            ]
        )
        if fixture["predicate_drift"]:
            lines.extend(["| Predicate | Counts | Delta |", "| --- | --- | ---: |"])
            for row in fixture["predicate_drift"]:
                lines.append(f"| `{row['predicate']}` | `{row['counts']}` | {row['delta']} |")
            lines.append("")
        if fixture["surface_drift"]:
            lines.extend(["| Surface | Counts | Delta |", "| --- | --- | ---: |"])
            for row in fixture["surface_drift"]:
                lines.append(f"| `{row['surface']}` | `{row['counts']}` | {row['delta']} |")
            lines.append("")
        lines.extend(["| Draw | Contract | Status | Source signals | Direct surfaces |", "| --- | --- | --- | ---: | ---: |"])
        for draw in fixture["draws"]:
            draw_name = Path(draw["compile_json"]).parent.parent.name
            for contract in draw["contracts"]:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            f"`{draw_name}`",
                            f"`{contract['contract']}`",
                            f"`{contract['status']}`",
                            str(contract["source_signal_count"]),
                            str(contract["direct_surface_count"]),
                        ]
                    )
                    + " |"
                )
        lines.append("")
        for draw in fixture["missing_by_draw"]:
            if not draw["missing_union_fact_count"]:
                continue
            lines.append(f"### Missing From `{Path(draw['compile_json']).parent.parent.name}`")
            lines.append("")
            lines.append(f"- Missing union facts: `{draw['missing_union_fact_count']}`")
            for fact in draw["missing_union_facts"]:
                lines.append(f"- `{fact}`")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-json", action="append", type=Path, default=[])
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()
    report = audit_paths(args.compile_json)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
