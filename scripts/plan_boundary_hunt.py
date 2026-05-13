#!/usr/bin/env python3
"""Plan boundary-hunt work from judged domain-bootstrap QA artifacts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "boundary_hunt_plan.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "boundary_hunt_plan.md"
PREDICATE_RE = re.compile(r"\b([a-z][A-Za-z0-9_]*)\s*\(")


COMPILE_CLASS_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "wrong_authority_envelope",
        (
            "authority",
            "authorized",
            "approver",
            "approved",
            "issuer",
            "issued",
            "solicitor",
            "warden",
            "owner",
            "applicant",
            "committee",
            "board",
            "director",
            "signatory",
            "memo",
            "reporter",
            "recorded by",
            "prepared by",
        ),
    ),
    (
        "wrong_temporal_envelope",
        (
            "current",
            "currently",
            "date",
            "deadline",
            "before",
            "after",
            "on what date",
            "effective",
            "expired",
            "expiration",
            "superseded",
            "amended",
            "amendment",
            "prior",
            "final",
        ),
    ),
    (
        "wrong_epistemic_envelope",
        (
            "pending",
            "proposed",
            "reported",
            "claim",
            "claimed",
            "statement",
            "objection",
            "alleged",
            "suspected",
            "unresolved",
            "finding",
            "non-finding",
        ),
    ),
    (
        "wrong_granularity",
        (
            "how many",
            "count",
            "total",
            "percentage",
            "percent",
            "amount",
            "maximum",
            "minimum",
            "area",
            "feet",
            "measurement",
            "ratio",
        ),
    ),
)

HYBRID_JOIN_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "temporal_rule_join",
        (
            "deadline",
            "expiration",
            "expired",
            "window",
            "elapsed",
            "business day",
            "calendar day",
            "tolling",
            "extension",
            "timely",
            "date",
        ),
    ),
    (
        "authority_custody_join",
        (
            "custody",
            "authorize",
            "authorized",
            "consent",
            "access",
            "held",
            "physical",
            "location",
            "located",
            "placement",
        ),
    ),
    (
        "status_timeline_join",
        (
            "status",
            "current",
            "resolved",
            "unresolved",
            "remains",
            "end of",
            "on january",
            "on february",
            "on march",
            "on april",
            "on september",
        ),
    ),
    (
        "count_aggregation_join",
        (
            "how many",
            "total",
            "count",
            "all items",
            "list all",
            "identified",
            "increase",
        ),
    ),
    (
        "policy_measure_join",
        (
            "rate",
            "revenue",
            "average",
            "score",
            "percentage",
            "bylaw",
            "rule",
            "require",
            "required",
        ),
    ),
)

STATUS_TIMELINE_DENSITY_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "final_assembly",
        (
            "final",
            "score",
            "match",
            "result",
            "assembly",
        ),
    ),
    (
        "superseded_record_of_authority",
        (
            "supersedes",
            "superseded",
            "layer of record",
            "current evacuation order",
            "record of authority",
        ),
    ),
    (
        "status_count_aggregation",
        (
            "how many",
            "count",
            "total",
            "number of",
            "violations",
            "conflicts",
            "trades",
            "trees",
        ),
    ),
    (
        "current_authoritative_attribute",
        (
            "current authoritative",
            "current",
            "as of",
            "of record",
            "status on",
            "status at",
            "per the amendment",
        ),
    ),
    (
        "post_change_set_membership",
        (
            "list all",
            "unaffected",
            "protected",
            "subject to",
            "after the amendment",
        ),
    ),
)

STATUS_COUNT_EVIDENCE_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "explicit_source_count",
        (
            "explicit",
            "source text",
            "text atom",
            "total_",
            "source_record_text",
            "stated count",
        ),
    ),
    (
        "multi_predicate_union_count",
        (
            "multiple predicates",
            "multi-predicate",
            "union",
            "penalty",
            "violation",
            "event_status",
            "penalty_applied",
        ),
    ),
    (
        "scoped_semantic_filter_count",
        (
            "filter",
            "excluding",
            "only those",
            "genuinely",
            "specific sections",
            "scope",
            "section",
        ),
    ),
    (
        "single_predicate_status_count",
        (
            "single predicate",
            "retrieves",
            "status",
            "count",
        ),
    ),
)
COUNTERFACTUAL_COUNT_QUESTION_HINTS = (
    "if ",
    "reclassif",
    "had been",
    "if the",
    "if a",
    "if an",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-root", action="append", type=Path, default=[])
    parser.add_argument("--qa-json", action="append", type=Path, default=[])
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--sample-limit", type=int, default=12)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    qa_paths = resolve_qa_paths(args.qa_json, args.qa_root)
    report = build_report(qa_paths, sample_limit=args.sample_limit)
    out_json = _resolve(args.out_json)
    out_md = _resolve(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def resolve_qa_paths(paths: list[Path], roots: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        item = _resolve(path)
        if item.is_file():
            found.append(item)
    for root in roots:
        item = _resolve(root)
        if item.is_file():
            found.append(item)
        elif item.is_dir():
            found.extend(sorted(item.rglob("domain_bootstrap_qa_*.json")))
    return sorted(dict.fromkeys(found))


def build_report(qa_paths: list[Path], *, sample_limit: int = 12) -> dict[str, Any]:
    coordinates: list[dict[str, Any]] = []
    artifact_rows: list[dict[str, Any]] = []
    for path in qa_paths:
        artifact = _read_json(path)
        fixture = _fixture_label(path, artifact)
        rows = artifact.get("rows") if isinstance(artifact.get("rows"), list) else []
        counts = Counter()
        for row in rows:
            if not isinstance(row, dict):
                continue
            verdict = _verdict(row)
            surface = _surface(row)
            if verdict:
                counts.update([verdict])
            if verdict and verdict != "exact":
                coordinates.append(_coordinate(path=path, fixture=fixture, row=row, verdict=verdict, surface=surface))
        artifact_rows.append(
            {
                "fixture": fixture,
                "qa_json": _display_path(path),
                "question_count": len(rows),
                "exact": int(counts.get("exact", 0)),
                "partial": int(counts.get("partial", 0)),
                "miss": int(counts.get("miss", 0)),
                "not_exact": int(counts.get("partial", 0) + counts.get("miss", 0)),
            }
        )
    surface_counts = Counter(str(item["failure_surface"]) for item in coordinates)
    compile_class_counts = Counter(
        str(item["compile_surface_class"]) for item in coordinates if item["failure_surface"] == "compile_surface_gap"
    )
    hybrid_join_class_counts = Counter(
        str(item["hybrid_join_class"]) for item in coordinates if item["failure_surface"] == "hybrid_join_gap"
    )
    status_timeline_density_counts = Counter(
        str(item["status_timeline_density_class"])
        for item in coordinates
        if item.get("hybrid_join_class") == "status_timeline_join"
    )
    status_count_evidence_counts = Counter(
        str(item["status_count_evidence_class"])
        for item in coordinates
        if item.get("status_timeline_density_class") == "status_count_aggregation"
    )
    predicate_counts = Counter(
        predicate for item in coordinates for predicate in item.get("predicate_hints", []) if predicate
    )
    helper_volume_rows = sorted(artifact_rows, key=lambda item: (-int(item["not_exact"]), item["fixture"]))
    return {
        "schema_version": "boundary_hunt_plan_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads judged QA artifacts only.",
            "Does not inspect source prose, gold KBs, or answer keys.",
            "Treats fixture names and question ids as artifact coordinates, not architecture.",
            "Classifies compile-surface rows with heuristic audit grammar for human review.",
        ],
        "artifacts": [_display_path(path) for path in qa_paths],
        "summary": {
            "artifact_count": len(qa_paths),
            "question_count": sum(int(item["question_count"]) for item in artifact_rows),
            "exact": sum(int(item["exact"]) for item in artifact_rows),
            "partial": sum(int(item["partial"]) for item in artifact_rows),
            "miss": sum(int(item["miss"]) for item in artifact_rows),
            "not_exact": len(coordinates),
            "failure_surface_counts": dict(sorted(surface_counts.items())),
            "compile_surface_class_counts": dict(sorted(compile_class_counts.items())),
            "hybrid_join_class_counts": dict(sorted(hybrid_join_class_counts.items())),
            "status_timeline_density_class_counts": dict(sorted(status_timeline_density_counts.items())),
            "status_count_evidence_class_counts": dict(sorted(status_count_evidence_counts.items())),
            "top_predicate_hints": dict(predicate_counts.most_common(20)),
        },
        "artifact_rows": artifact_rows,
        "coordinates": coordinates,
        "samples": {
            "compile_surface_gap": _sample(
                [item for item in coordinates if item["failure_surface"] == "compile_surface_gap"],
                limit=sample_limit,
            ),
            "hybrid_join_gap": _sample(
                [item for item in coordinates if item["failure_surface"] == "hybrid_join_gap"],
                limit=sample_limit,
            ),
            "query_surface_gap": _sample(
                [item for item in coordinates if item["failure_surface"] == "query_surface_gap"],
                limit=sample_limit,
            ),
            "top_not_exact_artifacts": helper_volume_rows[:10],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Boundary Hunt Plan",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "## Policy",
        "",
    ]
    for item in report.get("policy", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Artifacts: `{summary.get('artifact_count', 0)}`",
            f"- Questions: `{summary.get('question_count', 0)}`",
            f"- Exact / partial / miss: `{summary.get('exact', 0)} / {summary.get('partial', 0)} / {summary.get('miss', 0)}`",
            f"- Not-exact coordinates: `{summary.get('not_exact', 0)}`",
            f"- Failure surfaces: `{summary.get('failure_surface_counts', {})}`",
            f"- Compile-surface classes: `{summary.get('compile_surface_class_counts', {})}`",
            f"- Hybrid-join classes: `{summary.get('hybrid_join_class_counts', {})}`",
            f"- Status-timeline density classes: `{summary.get('status_timeline_density_class_counts', {})}`",
            f"- Status-count evidence classes: `{summary.get('status_count_evidence_class_counts', {})}`",
            f"- Top predicate hints: `{summary.get('top_predicate_hints', {})}`",
            "",
            "## Compile-Surface Samples",
            "",
            "| Class | Artifact Coordinate | Row | Verdict | Predicates | Question | Rationale |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report.get("samples", {}).get("compile_surface_gap", []):
        lines.append(_sample_row(item, include_class=True))
    lines.extend(
        [
            "",
            "## Hybrid-Join Samples",
            "",
            "| Class | Artifact Coordinate | Row | Verdict | Predicates | Question | Rationale |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report.get("samples", {}).get("hybrid_join_gap", []):
        lines.append(_sample_row(item, include_hybrid_class=True))
    lines.extend(
        [
            "",
            "## Query-Surface Samples",
            "",
            "| Artifact Coordinate | Row | Verdict | Predicates | Question | Rationale |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report.get("samples", {}).get("query_surface_gap", []):
        lines.append(_sample_row(item))
    lines.extend(
        [
            "",
            "## Top Not-Exact Artifact Coordinates",
            "",
            "| Artifact Coordinate | Questions | Exact | Partial | Miss | Not Exact |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in report.get("samples", {}).get("top_not_exact_artifacts", []):
        lines.append(
            f"| `{item.get('fixture', '')}` | {item.get('question_count', 0)} | {item.get('exact', 0)} | "
            f"{item.get('partial', 0)} | {item.get('miss', 0)} | {item.get('not_exact', 0)} |"
        )
    lines.append("")
    return "\n".join(lines)


def _coordinate(*, path: Path, fixture: str, row: dict[str, Any], verdict: str, surface: str) -> dict[str, Any]:
    predicates = sorted({predicate for query in _queries(row) for predicate in PREDICATE_RE.findall(query)})
    question_text = str(row.get("utterance") or "")
    text = " ".join(
        [
            question_text,
            str(row.get("reference_answer") or ""),
            _surface_rationale(row),
            " ".join(predicates),
        ]
    )
    return {
        "fixture": fixture,
        "id": str(row.get("id") or ""),
        "verdict": verdict,
        "failure_surface": surface,
        "compile_surface_class": _compile_surface_class(text, predicates=predicates) if surface == "compile_surface_gap" else "",
        "hybrid_join_class": _hybrid_join_class(text, predicates=predicates) if surface == "hybrid_join_gap" else "",
        "status_timeline_density_class": (
            _status_timeline_density_class(f"{question_text} {' '.join(predicates)}", predicates=predicates)
            if surface == "hybrid_join_gap" and _hybrid_join_class(text, predicates=predicates) == "status_timeline_join"
            else ""
        ),
        "status_count_evidence_class": (
            _status_count_evidence_class(text, predicates=predicates, question_text=question_text)
            if surface == "hybrid_join_gap"
            and _hybrid_join_class(text, predicates=predicates) == "status_timeline_join"
            and _status_timeline_density_class(f"{question_text} {' '.join(predicates)}", predicates=predicates)
            == "status_count_aggregation"
            else ""
        ),
        "question": question_text,
        "reference_answer_present": bool(str(row.get("reference_answer") or "").strip()),
        "predicate_hints": predicates,
        "query_count": len(_queries(row)),
        "rationale": _truncate(_surface_rationale(row), 220),
        "qa_json": _display_path(path),
    }


def _compile_surface_class(text: str, *, predicates: list[str]) -> str:
    lowered = text.casefold()
    if any("source_record" in predicate for predicate in predicates) and not predicates:
        return "opaque_residue_only"
    if "source text" in lowered or "text atom" in lowered or "source_record_text" in lowered:
        return "opaque_residue_only"
    for class_name, hints in COMPILE_CLASS_HINTS:
        if any(hint in lowered for hint in hints):
            return class_name
    if predicates and ("not present" in lowered or "absence" in lowered or "no predicate" in lowered):
        return "predicate_shape_drift"
    if predicates:
        return "predicate_shape_drift"
    return "absent_coordinate"


def _hybrid_join_class(text: str, *, predicates: list[str]) -> str:
    lowered = text.casefold()
    predicate_text = " ".join(predicates).casefold()
    combined = f"{lowered} {predicate_text}"
    for class_name, hints in HYBRID_JOIN_HINTS:
        if any(hint in combined for hint in hints):
            return class_name
    if len(predicates) >= 3:
        return "multi_predicate_join"
    if predicates:
        return "two_surface_join"
    return "unclassified_join"


def _status_timeline_density_class(text: str, *, predicates: list[str]) -> str:
    lowered = text.casefold()
    predicate_text = " ".join(predicates).casefold()
    combined = f"{lowered} {predicate_text}"
    if any(predicate.endswith("_status") for predicate in predicates):
        combined = f"{combined} status"
    for class_name, hints in STATUS_TIMELINE_DENSITY_HINTS:
        if any(hint in combined for hint in hints):
            return class_name
    return "point_state_resolution"


def _status_count_evidence_class(text: str, *, predicates: list[str], question_text: str = "") -> str:
    lowered = text.casefold()
    predicate_text = " ".join(predicates).casefold()
    combined = f"{lowered} {predicate_text}"
    question = str(question_text or "").casefold()
    if any(hint in question for hint in COUNTERFACTUAL_COUNT_QUESTION_HINTS):
        return "counterfactual_increment_count"
    for class_name, hints in STATUS_COUNT_EVIDENCE_HINTS:
        if any(hint in combined for hint in hints):
            return class_name
    if len(predicates) >= 2:
        return "multi_predicate_union_count"
    if predicates:
        return "single_predicate_status_count"
    return "unclassified_status_count"


def _sample(items: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            item.get("compile_surface_class", ""),
            item.get("hybrid_join_class", ""),
            item["fixture"],
            item["id"],
        ),
    )[:limit]


def _sample_row(item: dict[str, Any], *, include_class: bool = False, include_hybrid_class: bool = False) -> str:
    predicates = ", ".join(str(value) for value in item.get("predicate_hints", []))
    question = _escape_table(str(item.get("question") or ""))
    rationale = _escape_table(str(item.get("rationale") or ""))
    if include_class:
        prefix = f"| `{item.get('compile_surface_class', '')}` "
    elif include_hybrid_class:
        prefix = f"| `{item.get('hybrid_join_class', '')}` "
    else:
        prefix = "|"
    return (
        f"{prefix}| `{item.get('fixture', '')}` | `{item.get('id', '')}` | `{item.get('verdict', '')}` | "
        f"`{predicates}` | {question} | {rationale} |"
    )


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def _fixture_label(path: Path, artifact: dict[str, Any]) -> str:
    qa_file = str(artifact.get("qa_file") or "").replace("\\", "/")
    marker = "/datasets/story_worlds/"
    if marker in qa_file:
        return qa_file.split(marker, 1)[1].split("/", 1)[0]
    return path.parent.name


def _verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    return str(judge.get("verdict") or "").strip()


def _surface(row: dict[str, Any]) -> str:
    surface = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
    return str(surface.get("surface") or "").strip()


def _surface_rationale(row: dict[str, Any]) -> str:
    surface = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
    return str(surface.get("rationale") or "").strip()


def _queries(row: dict[str, Any]) -> list[str]:
    queries = row.get("queries")
    if isinstance(queries, list):
        return [str(query) for query in queries]
    if isinstance(queries, str):
        return [queries]
    return []


def _truncate(text: str, limit: int) -> str:
    cleaned = " ".join(text.split())
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 3].rstrip() + "..."


def _escape_table(text: str) -> str:
    return text.replace("|", "/")


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
