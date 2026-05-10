#!/usr/bin/env python
"""Audit query-companion helper-class provenance from compile artifacts.

This is intentionally artifact-only: it loads admitted facts/rules from
domain_bootstrap_file JSON outputs, invokes selected query companions with the
current code, and counts emitted rows by HelperClass.
"""

from __future__ import annotations

import argparse
import inspect
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

try:
    from run_domain_bootstrap_qa import (
        _clinic_device_recall_companion,
        _authority_custody_companion,
        _grant_award_companion,
        _industrial_sensor_companion,
        _roster_state_companion,
        _source_record_packet_metadata_companion,
        load_runtime,
    )
except ModuleNotFoundError:
    from scripts.run_domain_bootstrap_qa import (
        _clinic_device_recall_companion,
        _authority_custody_companion,
        _grant_award_companion,
        _industrial_sensor_companion,
        _roster_state_companion,
        _source_record_packet_metadata_companion,
        load_runtime,
    )


CompanionFn = Callable[..., dict[str, Any] | None]


COMPANIONS: dict[str, tuple[CompanionFn, str, str]] = {
    "archive_authority_custody_support": (
        _authority_custody_companion,
        "object_custody_status",
        "object_custody_status(Object, Holder, StatusKind, TimeOrDate, SourceDocument).",
    ),
    "source_record_packet_metadata_support": (
        _source_record_packet_metadata_companion,
        "source_record_field",
        "source_record_field(SourceRow, Header, Value).",
    ),
    "industrial_sensor_support": (
        _industrial_sensor_companion,
        "source_record_field",
        "source_record_field(SourceRow, Header, Value).",
    ),
    "clinic_recall_support": (
        _clinic_device_recall_companion,
        "source_record_text_atom",
        "source_record_text_atom(SourceRow, TextAtom).",
    ),
    "grant_award_support": (
        _grant_award_companion,
        "application_eligibility",
        "application_eligibility(App, Rule, Result).",
    ),
    "roster_state_support": (
        _roster_state_companion,
        "student_group_assignment",
        "student_group_assignment(Student, Version, Group).",
    ),
}


def iter_compile_artifacts(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    artifacts = sorted(root.rglob("domain_bootstrap_file_*.json"))
    return [path for path in artifacts if path.is_file()]


def artifact_label(path: Path) -> str:
    parent = path.parent.name
    if parent:
        return parent
    return path.stem


def load_artifact_runtime(path: Path) -> tuple[Any | None, list[str], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    source_compile = payload.get("source_compile") if isinstance(payload, dict) else {}
    facts = source_compile.get("facts", []) if isinstance(source_compile, dict) else []
    rules = source_compile.get("rules", []) if isinstance(source_compile, dict) else []
    runtime, errors = load_runtime(facts=[str(item) for item in facts], rules=[str(item) for item in rules])
    return runtime, errors, payload


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    helper_classes = Counter(str(row.get("HelperClass", "") or "unlabeled") for row in rows)
    support_kinds = Counter(str(row.get("SupportKind") or row.get("Kind") or "unknown") for row in rows)
    return {
        "row_count": len(rows),
        "helper_class_counts": dict(sorted(helper_classes.items())),
        "support_kind_counts": dict(sorted(support_kinds.items())),
    }


def audit_artifact(path: Path) -> dict[str, Any]:
    runtime, load_errors, payload = load_artifact_runtime(path)
    entry: dict[str, Any] = {
        "artifact": str(path),
        "fixture": artifact_label(path),
        "model": payload.get("model", ""),
        "load_error_count": len(load_errors),
        "companions": {},
    }
    if load_errors:
        entry["load_errors"] = load_errors[:20]
    if runtime is None:
        return entry

    for name, (fn, predicate, query) in COMPANIONS.items():
        kwargs: dict[str, Any] = {"predicate": predicate, "query": query}
        if "args" in inspect.signature(fn).parameters:
            kwargs["args"] = []
        result = fn(runtime, **kwargs)
        if not result:
            entry["companions"][name] = {
                "available": False,
                "row_count": 0,
                "helper_class_counts": {},
                "support_kind_counts": {},
            }
            continue
        rows = result.get("result", {}).get("rows", [])
        companion_summary = summarize_rows(rows if isinstance(rows, list) else [])
        companion_summary["available"] = True
        entry["companions"][name] = companion_summary
    return entry


def rollup(entries: list[dict[str, Any]]) -> dict[str, Any]:
    companion_totals: dict[str, Counter[str]] = {}
    companion_rows: Counter[str] = Counter()
    unlabeled: list[dict[str, Any]] = []
    for entry in entries:
        for name, summary in entry.get("companions", {}).items():
            if not summary.get("available"):
                continue
            companion_rows[name] += int(summary.get("row_count", 0))
            companion_totals.setdefault(name, Counter()).update(summary.get("helper_class_counts", {}))
            if int(summary.get("helper_class_counts", {}).get("unlabeled", 0)):
                unlabeled.append({"fixture": entry.get("fixture"), "companion": name})
    return {
        "artifact_count": len(entries),
        "companion_row_totals": dict(sorted(companion_rows.items())),
        "companion_helper_class_totals": {
            name: dict(sorted(counter.items())) for name, counter in sorted(companion_totals.items())
        },
        "unlabeled_companion_results": unlabeled,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Helper-Class Audit",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Rollup",
        "",
        "| Companion | Rows | clean-helper | candidate-helper | unlabeled |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    totals = payload["rollup"]["companion_helper_class_totals"]
    rows_by_companion = payload["rollup"]["companion_row_totals"]
    for companion, counts in totals.items():
        lines.append(
            "| {companion} | {rows} | {clean} | {candidate} | {unlabeled} |".format(
                companion=companion,
                rows=rows_by_companion.get(companion, 0),
                clean=counts.get("clean-helper", 0),
                candidate=counts.get("candidate-helper", 0),
                unlabeled=counts.get("unlabeled", 0),
            )
        )
    lines.extend(["", "## Fixtures", ""])
    for entry in payload["entries"]:
        lines.append(f"### {entry['fixture']}")
        lines.append("")
        lines.append("| Companion | Rows | clean-helper | candidate-helper | unlabeled |")
        lines.append("| --- | ---: | ---: | ---: | ---: |")
        for companion, summary in sorted(entry.get("companions", {}).items()):
            counts = summary.get("helper_class_counts", {})
            lines.append(
                "| {companion} | {rows} | {clean} | {candidate} | {unlabeled} |".format(
                    companion=companion,
                    rows=summary.get("row_count", 0),
                    clean=counts.get("clean-helper", 0),
                    candidate=counts.get("candidate-helper", 0),
                    unlabeled=counts.get("unlabeled", 0),
                )
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Compile JSON file or directory to scan.")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path.")
    parser.add_argument("--markdown", type=Path, help="Optional Markdown report path.")
    args = parser.parse_args()

    artifacts = iter_compile_artifacts(args.root)
    entries = [audit_artifact(path) for path in artifacts]
    payload = {
        "schema_version": "helper_class_audit_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(args.root),
        "entries": entries,
        "rollup": rollup(entries),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["rollup"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
