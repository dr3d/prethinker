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
