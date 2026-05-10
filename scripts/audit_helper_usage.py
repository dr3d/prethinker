#!/usr/bin/env python
"""Audit helper/support predicate usage across QA artifacts.

The goal is not to prove a helper is good or bad. It is to find helpers whose
observed surface is narrow enough to deserve suspicion: support predicates that
appear on only one or two fixtures are likely candidate scars or lens companions
until transfer evidence says otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def iter_json_files(roots: Iterable[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix.lower() == ".json":
            out.append(root)
        elif root.is_dir():
            out.extend(path for path in root.rglob("*.json") if path.is_file())
    return sorted(out)


def infer_fixture(payload: dict[str, Any], path: Path) -> str:
    for key in ("qa_file", "text_file"):
        value = str(payload.get(key, "") or "")
        if value:
            parts = Path(value).parts
            if len(parts) >= 2:
                return Path(value).parent.name
    run_json = str(payload.get("run_json", "") or "")
    if run_json:
        parent = Path(run_json).parent.name
        if parent:
            return parent
    for part in reversed(path.parts):
        if part.startswith("domain_bootstrap_"):
            continue
        if part.startswith("tmp"):
            continue
        if part.endswith("_20260510") or part.endswith("_20260509"):
            continue
        if part:
            return part
    return path.parent.name or path.stem


def walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def support_predicate_name(item: dict[str, Any]) -> str:
    predicate = str(item.get("predicate", "") or "").strip()
    if predicate.endswith("_support"):
        return predicate
    return ""


def implemented_support_predicates(paths: Iterable[Path]) -> set[str]:
    implemented: set[str] = set()
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        implemented.update(re.findall(r"[\"']([a-zA-Z0-9_]+_support)[\"']", text))
    return implemented


def helper_class_counts(result: dict[str, Any]) -> Counter[str]:
    counts: Counter[str] = Counter()
    rows = result.get("rows")
    if not isinstance(rows, list):
        return counts
    for row in rows:
        if not isinstance(row, dict):
            continue
        counts[str(row.get("HelperClass") or "unlabeled")] += 1
    return counts


def audit_file(path: Path) -> tuple[str, dict[str, dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return path.parent.name, {}
    fixture = infer_fixture(payload, path)
    helpers: dict[str, dict[str, Any]] = {}
    for item in walk_dicts(payload):
        predicate = support_predicate_name(item)
        if not predicate:
            continue
        rows = item.get("rows")
        row_count = len(rows) if isinstance(rows, list) else 0
        summary = helpers.setdefault(
            predicate,
            {
                "occurrences": 0,
                "row_count": 0,
                "helper_class_counts": Counter(),
            },
        )
        summary["occurrences"] += 1
        summary["row_count"] += row_count
        summary["helper_class_counts"].update(helper_class_counts(item))
    return fixture, helpers


def audit_roots(
    roots: list[Path],
    *,
    rare_threshold: int,
    implemented_helpers: set[str] | None = None,
) -> dict[str, Any]:
    files = iter_json_files(roots)
    helper_fixtures: dict[str, set[str]] = defaultdict(set)
    helper_files: dict[str, set[str]] = defaultdict(set)
    helper_occurrences: Counter[str] = Counter()
    helper_rows: Counter[str] = Counter()
    helper_classes: dict[str, Counter[str]] = defaultdict(Counter)
    fixture_helpers: dict[str, set[str]] = defaultdict(set)
    fixture_rows: Counter[str] = Counter()
    fixture_classes: dict[str, Counter[str]] = defaultdict(Counter)
    parse_errors: list[dict[str, str]] = []

    for path in files:
        try:
            fixture, helpers = audit_file(path)
        except Exception as exc:  # pragma: no cover - defensive for tmp archaeology
            parse_errors.append({"path": str(path), "error": str(exc)})
            continue
        for helper, summary in helpers.items():
            helper_fixtures[helper].add(fixture)
            helper_files[helper].add(str(path))
            helper_occurrences[helper] += int(summary.get("occurrences", 0))
            helper_rows[helper] += int(summary.get("row_count", 0))
            helper_classes[helper].update(summary.get("helper_class_counts", Counter()))
            fixture_helpers[fixture].add(helper)
            fixture_rows[fixture] += int(summary.get("row_count", 0))
            fixture_classes[fixture].update(summary.get("helper_class_counts", Counter()))

    helpers_out: dict[str, Any] = {}
    for helper in sorted(helper_fixtures):
        fixtures = sorted(helper_fixtures[helper])
        helpers_out[helper] = {
            "fixture_count": len(fixtures),
            "fixtures": fixtures,
            "file_count": len(helper_files[helper]),
            "occurrences": helper_occurrences[helper],
            "row_count": helper_rows[helper],
            "helper_class_counts": dict(sorted(helper_classes[helper].items())),
            "suspicious_low_transfer": len(fixtures) <= rare_threshold,
            "implemented": (helper in implemented_helpers) if implemented_helpers is not None else None,
        }

    suspicious = {
        helper: item
        for helper, item in helpers_out.items()
        if item["suspicious_low_transfer"]
    }
    fixtures_out = {
        fixture: {
            "helper_count": len(helpers),
            "helpers": sorted(helpers),
            "row_count": fixture_rows[fixture],
            "helper_class_counts": dict(sorted(fixture_classes[fixture].items())),
        }
        for fixture, helpers in sorted(fixture_helpers.items())
    }
    return {
        "schema_version": "helper_usage_audit_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roots": [str(root) for root in roots],
        "json_file_count": len(files),
        "helper_count": len(helpers_out),
        "rare_threshold": rare_threshold,
        "suspicious_helper_count": len(suspicious),
        "helpers": helpers_out,
        "fixtures": fixtures_out,
        "suspicious_helpers": suspicious,
        "orphaned_artifact_helpers": {
            helper: item
            for helper, item in helpers_out.items()
            if item.get("implemented") is False
        },
        "orphaned_artifact_helper_count": sum(
            1 for item in helpers_out.values() if item.get("implemented") is False
        ),
        "parse_errors": parse_errors[:50],
        "parse_error_count": len(parse_errors),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Helper Usage Audit",
        "",
        f"Generated: {payload['generated_at']}",
        f"JSON files scanned: `{payload['json_file_count']}`",
        f"Helpers observed: `{payload['helper_count']}`",
        f"Suspicious low-transfer helpers: `{payload['suspicious_helper_count']}`",
        f"Orphaned artifact helpers: `{payload.get('orphaned_artifact_helper_count', 0)}`",
        "",
        "## Suspicious Helpers",
        "",
        "| Helper | Fixtures | Files | Rows | Implemented | Helper classes | Fixture list |",
        "| --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for helper, item in sorted(
        payload["suspicious_helpers"].items(),
        key=lambda pair: (pair[1]["fixture_count"], pair[0]),
    ):
        lines.append(
            "| {helper} | {fixtures} | {files} | {rows} | {implemented} | `{classes}` | {fixture_list} |".format(
                helper=helper,
                fixtures=item["fixture_count"],
                files=item["file_count"],
                rows=item["row_count"],
                implemented=_display_implemented(item.get("implemented")),
                classes=item.get("helper_class_counts", {}),
                fixture_list=", ".join(item.get("fixtures", [])),
            )
        )
    lines.extend(
        [
            "",
            "## Fixtures",
            "",
            "| Fixture | Helpers | Rows | Helper classes | Helper list |",
            "| --- | ---: | ---: | --- | --- |",
        ]
    )
    for fixture, item in sorted(payload["fixtures"].items(), key=lambda pair: (-pair[1]["helper_count"], pair[0])):
        lines.append(
            "| {fixture} | {helpers} | {rows} | `{classes}` | {helper_list} |".format(
                fixture=fixture,
                helpers=item["helper_count"],
                rows=item["row_count"],
                classes=item.get("helper_class_counts", {}),
                helper_list=", ".join(item.get("helpers", [])),
            )
        )
    lines.extend(
        [
            "",
            "## All Helpers",
            "",
            "| Helper | Fixtures | Files | Rows | Suspicious | Implemented |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for helper, item in sorted(payload["helpers"].items()):
        lines.append(
            "| {helper} | {fixtures} | {files} | {rows} | {suspicious} | {implemented} |".format(
                helper=helper,
                fixtures=item["fixture_count"],
                files=item["file_count"],
                rows=item["row_count"],
                suspicious="yes" if item["suspicious_low_transfer"] else "no",
                implemented=_display_implemented(item.get("implemented")),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def _display_implemented(value: object) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", type=Path, required=True, help="Root file/dir to scan; repeatable.")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path.")
    parser.add_argument("--markdown", type=Path, help="Optional Markdown output path.")
    parser.add_argument("--rare-threshold", type=int, default=2, help="Flag helpers used on <= this many fixtures.")
    parser.add_argument(
        "--registry-source",
        action="append",
        type=Path,
        default=[Path("scripts/run_domain_bootstrap_qa.py")],
        help="Source file containing currently implemented helper predicate names; repeatable.",
    )
    args = parser.parse_args()

    implemented = implemented_support_predicates(args.registry_source)
    payload = audit_roots(args.root, rare_threshold=int(args.rare_threshold), implemented_helpers=implemented)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {k: payload[k] for k in ["json_file_count", "helper_count", "suspicious_helper_count", "orphaned_artifact_helper_count"]},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
