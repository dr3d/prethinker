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


def iter_result_payloads(items: Any) -> Iterable[dict[str, Any]]:
    if not isinstance(items, list):
        return
    for item in items:
        if not isinstance(item, dict):
            continue
        result = item.get("result")
        if isinstance(result, dict):
            yield result
        else:
            yield item


def iter_support_result_dicts(payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    """Yield canonical result dicts without counting provenance copies twice."""

    rows = payload.get("rows")
    if not isinstance(rows, list):
        yield from walk_dicts(payload)
        return
    for row in rows:
        if not isinstance(row, dict):
            continue
        query_results = row.get("query_results")
        if isinstance(query_results, list):
            yield from iter_result_payloads(query_results)
            continue
        evidence_results = row.get("evidence_bundle_plan_query_results")
        if isinstance(evidence_results, list):
            yield from iter_result_payloads(evidence_results)


def support_predicate_name(item: dict[str, Any]) -> str:
    predicate = str(item.get("predicate", "") or "").strip()
    if predicate.endswith("_support"):
        return predicate
    return ""


def helper_row_signature(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"), default=str)


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


def support_kind_counts(result: dict[str, Any]) -> Counter[str]:
    counts: Counter[str] = Counter()
    rows = result.get("rows")
    if not isinstance(rows, list):
        return counts
    for row in rows:
        if not isinstance(row, dict):
            continue
        support_kind = str(row.get("SupportKind") or row.get("Kind") or "unknown").strip()
        counts[support_kind or "unknown"] += 1
    return counts


def helper_class_support_kind_counts(result: dict[str, Any]) -> dict[str, Counter[str]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    rows = result.get("rows")
    if not isinstance(rows, list):
        return counts
    for row in rows:
        if not isinstance(row, dict):
            continue
        helper_class = str(row.get("HelperClass") or "unlabeled")
        support_kind = str(row.get("SupportKind") or row.get("Kind") or "unknown").strip() or "unknown"
        counts[helper_class][support_kind] += 1
    return counts


def merge_class_support_kind_counts(
    target: dict[str, Counter[str]],
    source: dict[str, Counter[str]] | dict[str, dict[str, int]],
) -> None:
    for helper_class, counts in source.items():
        target[str(helper_class)].update(counts)


def render_class_support_kind_counts(value: dict[str, Counter[str]]) -> dict[str, dict[str, int]]:
    return {
        helper_class: dict(sorted(counts.items()))
        for helper_class, counts in sorted(value.items())
    }


def pruning_targets(
    *,
    helpers: dict[str, Any],
    limit: int = 12,
) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for helper, item in helpers.items():
        class_support = item.get("helper_class_support_kind_counts", {})
        candidate_counts = class_support.get("candidate-helper", {}) if isinstance(class_support, dict) else {}
        if not isinstance(candidate_counts, dict):
            continue
        helper_rows = int(item.get("row_count", 0) or 0)
        unique_helper_rows = int(item.get("unique_row_count", 0) or 0)
        unique_class_support = item.get("unique_helper_class_support_kind_counts", {})
        unique_candidate_counts = (
            unique_class_support.get("candidate-helper", {}) if isinstance(unique_class_support, dict) else {}
        )
        for support_kind, raw_count in candidate_counts.items():
            count = int(raw_count or 0)
            if count <= 0:
                continue
            unique_count = 0
            if isinstance(unique_candidate_counts, dict):
                unique_count = int(unique_candidate_counts.get(str(support_kind), 0) or 0)
            fixture_count = int(item.get("fixture_count", 0) or 0)
            targets.append(
                {
                    "helper": helper,
                    "support_kind": str(support_kind),
                    "candidate_rows": count,
                    "unique_candidate_rows": unique_count,
                    "helper_rows": helper_rows,
                    "unique_helper_rows": unique_helper_rows,
                    "candidate_share_of_helper": round(float(count) / float(helper_rows), 4) if helper_rows else 0.0,
                    "unique_candidate_share_of_helper": (
                        round(float(unique_count) / float(unique_helper_rows), 4) if unique_helper_rows else 0.0
                    ),
                    "fixture_count": fixture_count,
                    "transfer_signal": candidate_transfer_signal(
                        fixture_count=fixture_count,
                        unique_candidate_rows=unique_count,
                    ),
                }
            )
    return sorted(
        targets,
        key=lambda item: (-int(item["candidate_rows"]), str(item["helper"]), str(item["support_kind"])),
    )[:limit]


def candidate_transfer_signal(*, fixture_count: int, unique_candidate_rows: int) -> str:
    """Classify compatibility-row pressure without naming fixtures or answers."""

    if fixture_count <= 1:
        return "single_fixture_pressure"
    if unique_candidate_rows <= 3:
        return "narrow_transfer_scar"
    return "transferred_candidate_pressure"


def answer_surface_summary(payload: dict[str, Any]) -> dict[str, int]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return {
            "question_count": 0,
            "judge_rows": 0,
            "judge_exact": 0,
            "judge_partial": 0,
            "judge_miss": 0,
        }
    verdicts = Counter()
    for row in rows:
        if not isinstance(row, dict):
            continue
        judge = row.get("reference_judge")
        if not isinstance(judge, dict):
            continue
        verdict = str(judge.get("verdict", "") or "").strip()
        if verdict:
            verdicts[verdict] += 1
    return {
        "question_count": len(rows),
        "judge_rows": sum(verdicts.values()),
        "judge_exact": verdicts.get("exact", 0),
        "judge_partial": verdicts.get("partial", 0),
        "judge_miss": verdicts.get("miss", 0),
    }


def helper_pressure_metrics(
    *,
    row_count: int,
    helper_class_counts: Counter[str] | dict[str, int],
    answer_summary: dict[str, int],
) -> dict[str, Any]:
    exact = int(answer_summary.get("judge_exact", 0) or 0)
    judge_rows = int(answer_summary.get("judge_rows", 0) or 0)
    question_count = int(answer_summary.get("question_count", 0) or 0)
    candidate_rows = int(helper_class_counts.get("candidate-helper", 0) or 0)
    clean_rows = int(helper_class_counts.get("clean-helper", 0) or 0)
    helper_rows_per_exact = round(float(row_count) / float(exact), 3) if exact else None
    helper_rows_per_question = round(float(row_count) / float(question_count), 3) if question_count else None
    candidate_helper_share = round(float(candidate_rows) / float(row_count), 4) if row_count else 0.0
    clean_helper_share = round(float(clean_rows) / float(row_count), 4) if row_count else 0.0
    exact_rate = round(float(exact) / float(judge_rows), 4) if judge_rows else None
    if row_count <= 0:
        pressure_label = "no_compatibility_rows"
    elif judge_rows <= 0:
        pressure_label = "compatibility_volume_without_judged_answers"
    elif row_count >= 500 and candidate_helper_share >= 0.25:
        pressure_label = "high_compatibility_pressure"
    elif row_count >= 500:
        pressure_label = "high_compatibility_volume"
    elif candidate_helper_share >= 0.5:
        pressure_label = "compatibility_dominant"
    else:
        pressure_label = "bounded_compatibility_surface"
    return {
        "candidate_helper_share": candidate_helper_share,
        "clean_helper_share": clean_helper_share,
        "exact_rate": exact_rate,
        "helper_rows_per_exact": helper_rows_per_exact,
        "helper_rows_per_question": helper_rows_per_question,
        "pressure_label": pressure_label,
    }


def display_pressure_label(label: object) -> str:
    raw = str(label or "").strip()
    return {
        "no_helper_rows": "none",
        "no_compatibility_rows": "none",
        "helper_volume_without_judged_answers": "compatibility_volume_without_judged_answers",
        "high_candidate_helper_pressure": "high_compatibility_pressure",
        "high_clean_helper_volume": "high_compatibility_volume",
        "candidate_helper_dominant": "compatibility_dominant",
        "bounded_helper_surface": "bounded_compatibility_surface",
    }.get(raw, raw.replace("candidate_helper", "compatibility").replace("clean_helper", "compatibility").replace("helper", "compatibility"))


def audit_file(path: Path) -> tuple[str, dict[str, dict[str, Any]], dict[str, int]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return path.parent.name, {}, answer_surface_summary({})
    fixture = infer_fixture(payload, path)
    helpers: dict[str, dict[str, Any]] = {}
    for item in iter_support_result_dicts(payload):
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
                "unique_row_signatures": set(),
                "unique_helper_class_counts": Counter(),
                "unique_support_kind_counts": Counter(),
                "unique_helper_class_support_kind_counts": defaultdict(Counter),
                "helper_class_counts": Counter(),
                "support_kind_counts": Counter(),
                "helper_class_support_kind_counts": defaultdict(Counter),
            },
        )
        summary["occurrences"] += 1
        summary["row_count"] += row_count
        summary["helper_class_counts"].update(helper_class_counts(item))
        summary["support_kind_counts"].update(support_kind_counts(item))
        merge_class_support_kind_counts(
            summary["helper_class_support_kind_counts"],
            helper_class_support_kind_counts(item),
        )
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                signature = helper_row_signature(row)
                if signature in summary["unique_row_signatures"]:
                    continue
                summary["unique_row_signatures"].add(signature)
                helper_class = str(row.get("HelperClass") or "unlabeled")
                support_kind = str(row.get("SupportKind") or row.get("Kind") or "unknown").strip() or "unknown"
                summary["unique_helper_class_counts"][helper_class] += 1
                summary["unique_support_kind_counts"][support_kind] += 1
                summary["unique_helper_class_support_kind_counts"][helper_class][support_kind] += 1
    return fixture, helpers, answer_surface_summary(payload)


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
    helper_unique_rows: dict[str, set[str]] = defaultdict(set)
    helper_classes: dict[str, Counter[str]] = defaultdict(Counter)
    helper_unique_classes: dict[str, Counter[str]] = defaultdict(Counter)
    helper_support_kinds: dict[str, Counter[str]] = defaultdict(Counter)
    helper_unique_support_kinds: dict[str, Counter[str]] = defaultdict(Counter)
    helper_class_support_kinds: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    helper_unique_class_support_kinds: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    fixture_helpers: dict[str, set[str]] = defaultdict(set)
    fixture_rows: Counter[str] = Counter()
    fixture_unique_rows: dict[str, set[str]] = defaultdict(set)
    fixture_classes: dict[str, Counter[str]] = defaultdict(Counter)
    fixture_unique_classes: dict[str, Counter[str]] = defaultdict(Counter)
    fixture_support_kinds: dict[str, Counter[str]] = defaultdict(Counter)
    fixture_unique_support_kinds: dict[str, Counter[str]] = defaultdict(Counter)
    fixture_class_support_kinds: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    fixture_unique_class_support_kinds: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    fixture_answer_summaries: dict[str, Counter[str]] = defaultdict(Counter)
    parse_errors: list[dict[str, str]] = []

    for path in files:
        try:
            fixture, helpers, answer_summary = audit_file(path)
        except Exception as exc:  # pragma: no cover - defensive for tmp archaeology
            parse_errors.append({"path": str(path), "error": str(exc)})
            continue
        fixture_answer_summaries[fixture].update(answer_summary)
        for helper, summary in helpers.items():
            helper_fixtures[helper].add(fixture)
            helper_files[helper].add(str(path))
            helper_occurrences[helper] += int(summary.get("occurrences", 0))
            helper_rows[helper] += int(summary.get("row_count", 0))
            helper_unique_rows[helper].update(summary.get("unique_row_signatures", set()))
            helper_classes[helper].update(summary.get("helper_class_counts", Counter()))
            helper_unique_classes[helper].update(summary.get("unique_helper_class_counts", Counter()))
            helper_support_kinds[helper].update(summary.get("support_kind_counts", Counter()))
            helper_unique_support_kinds[helper].update(summary.get("unique_support_kind_counts", Counter()))
            merge_class_support_kind_counts(
                helper_class_support_kinds[helper],
                summary.get("helper_class_support_kind_counts", {}),
            )
            merge_class_support_kind_counts(
                helper_unique_class_support_kinds[helper],
                summary.get("unique_helper_class_support_kind_counts", {}),
            )
            fixture_helpers[fixture].add(helper)
            fixture_rows[fixture] += int(summary.get("row_count", 0))
            fixture_unique_rows[fixture].update(
                f"{helper}:{signature}" for signature in summary.get("unique_row_signatures", set())
            )
            fixture_classes[fixture].update(summary.get("helper_class_counts", Counter()))
            fixture_unique_classes[fixture].update(summary.get("unique_helper_class_counts", Counter()))
            fixture_support_kinds[fixture].update(summary.get("support_kind_counts", Counter()))
            fixture_unique_support_kinds[fixture].update(summary.get("unique_support_kind_counts", Counter()))
            merge_class_support_kind_counts(
                fixture_class_support_kinds[fixture],
                summary.get("helper_class_support_kind_counts", {}),
            )
            merge_class_support_kind_counts(
                fixture_unique_class_support_kinds[fixture],
                summary.get("unique_helper_class_support_kind_counts", {}),
            )

    helpers_out: dict[str, Any] = {}
    for helper in sorted(helper_fixtures):
        fixtures = sorted(helper_fixtures[helper])
        helpers_out[helper] = {
            "fixture_count": len(fixtures),
            "fixtures": fixtures,
            "file_count": len(helper_files[helper]),
            "occurrences": helper_occurrences[helper],
            "row_count": helper_rows[helper],
            "unique_row_count": len(helper_unique_rows[helper]),
            "helper_class_counts": dict(sorted(helper_classes[helper].items())),
            "unique_helper_class_counts": dict(sorted(helper_unique_classes[helper].items())),
            "support_kind_counts": dict(sorted(helper_support_kinds[helper].items())),
            "unique_support_kind_counts": dict(sorted(helper_unique_support_kinds[helper].items())),
            "helper_class_support_kind_counts": render_class_support_kind_counts(helper_class_support_kinds[helper]),
            "unique_helper_class_support_kind_counts": render_class_support_kind_counts(
                helper_unique_class_support_kinds[helper]
            ),
            "suspicious_low_transfer": len(fixtures) <= rare_threshold,
            "implemented": (helper in implemented_helpers) if implemented_helpers is not None else None,
        }

    suspicious = {
        helper: item
        for helper, item in helpers_out.items()
        if item["suspicious_low_transfer"]
    }
    fixtures_out = {
        fixture: dict(
            {
                "helper_count": len(helpers),
                "helpers": sorted(helpers),
                "row_count": fixture_rows[fixture],
                "unique_row_count": len(fixture_unique_rows[fixture]),
                "helper_class_counts": dict(sorted(fixture_classes[fixture].items())),
                "unique_helper_class_counts": dict(sorted(fixture_unique_classes[fixture].items())),
                "support_kind_counts": dict(sorted(fixture_support_kinds[fixture].items())),
                "unique_support_kind_counts": dict(sorted(fixture_unique_support_kinds[fixture].items())),
                "helper_class_support_kind_counts": render_class_support_kind_counts(fixture_class_support_kinds[fixture]),
                "unique_helper_class_support_kind_counts": render_class_support_kind_counts(
                    fixture_unique_class_support_kinds[fixture]
                ),
                "answer_surface_summary": dict(sorted(fixture_answer_summaries[fixture].items())),
            },
            **helper_pressure_metrics(
                row_count=fixture_rows[fixture],
                helper_class_counts=fixture_classes[fixture],
                answer_summary=dict(fixture_answer_summaries[fixture]),
            ),
        )
        for fixture, helpers in sorted(fixture_helpers.items())
    }
    helper_rows_total = sum(helper_rows.values())
    helper_unique_rows_total = len({f"{helper}:{signature}" for helper, signatures in helper_unique_rows.items() for signature in signatures})
    helper_classes_total: Counter[str] = Counter()
    helper_unique_classes_total: Counter[str] = Counter()
    answer_surface_total: Counter[str] = Counter()
    for counter in helper_classes.values():
        helper_classes_total.update(counter)
    for counter in helper_unique_classes.values():
        helper_unique_classes_total.update(counter)
    for counter in fixture_answer_summaries.values():
        answer_surface_total.update(counter)
    return {
        "schema_version": "helper_usage_audit_v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roots": [str(root) for root in roots],
        "json_file_count": len(files),
        "helper_count": len(helpers_out),
        "helper_pressure_summary": dict(
            {
                "row_count": helper_rows_total,
                "unique_row_count": helper_unique_rows_total,
                "helper_class_counts": dict(sorted(helper_classes_total.items())),
                "unique_helper_class_counts": dict(sorted(helper_unique_classes_total.items())),
                "answer_surface_summary": dict(sorted(answer_surface_total.items())),
            },
            **helper_pressure_metrics(
                row_count=helper_rows_total,
                helper_class_counts=helper_classes_total,
                answer_summary=dict(answer_surface_total),
            ),
        ),
        "rare_threshold": rare_threshold,
        "suspicious_helper_count": len(suspicious),
        "candidate_pruning_targets": pruning_targets(helpers=helpers_out),
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
        "# Compatibility Adapter Usage Audit",
        "",
        f"Generated: {payload['generated_at']}",
        f"JSON files scanned: `{payload['json_file_count']}`",
        f"Adapters observed: `{payload['helper_count']}`",
        f"Compatibility rows: `{display_pressure_label(payload.get('helper_pressure_summary', {}).get('pressure_label', ''))}`",
        f"Suspicious low-transfer adapters: `{payload['suspicious_helper_count']}`",
        f"Orphaned artifact adapters: `{payload.get('orphaned_artifact_helper_count', 0)}`",
        "",
        "## Adapter Pruning Targets",
        "",
        "| Adapter | Support kind | Candidate rows | Share of adapter | Fixtures | Signal |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for item in payload.get("candidate_pruning_targets", []):
        if not isinstance(item, dict):
            continue
        lines.append(
            "| {helper} | `{support_kind}` | {rows} ({unique_rows} unique) | {share} ({unique_share} unique) | {fixtures} | `{signal}` |".format(
                helper=item.get("helper", ""),
                support_kind=item.get("support_kind", ""),
                rows=item.get("candidate_rows", 0),
                unique_rows=item.get("unique_candidate_rows", 0),
                share=item.get("candidate_share_of_helper", 0.0),
                unique_share=item.get("unique_candidate_share_of_helper", 0.0),
                fixtures=item.get("fixture_count", 0),
                signal=item.get("transfer_signal", ""),
            )
        )
    lines.extend(
        [
            "",
            "## Suspicious Adapters",
            "",
            "| Adapter | Fixtures | Files | Rows | Implemented | Adapter classes | Top support kinds | Fixture list |",
            "| --- | ---: | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for helper, item in sorted(
        payload["suspicious_helpers"].items(),
        key=lambda pair: (pair[1]["fixture_count"], pair[0]),
    ):
        lines.append(
            "| {helper} | {fixtures} | {files} | {rows} | {implemented} | `{classes}` | `{support_kinds}` | {fixture_list} |".format(
                helper=helper,
                fixtures=item["fixture_count"],
                files=item["file_count"],
                rows=item["row_count"],
                implemented=_display_implemented(item.get("implemented")),
                classes=item.get("helper_class_counts", {}),
                support_kinds=_top_counts(item.get("support_kind_counts", {})),
                fixture_list=", ".join(item.get("fixtures", [])),
            )
        )
    lines.extend(
        [
            "",
            "## Fixtures",
            "",
            "| Fixture | Adapters | Rows | Rows/exact | Candidate share | Pressure | Adapter classes | Top support kinds | Adapter list |",
            "| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for fixture, item in sorted(payload["fixtures"].items(), key=lambda pair: (-pair[1]["helper_count"], pair[0])):
        lines.append(
            "| {fixture} | {helpers} | {rows} | {rows_per_exact} | {candidate_share} | {pressure} | `{classes}` | `{support_kinds}` | {helper_list} |".format(
                fixture=fixture,
                helpers=item["helper_count"],
                rows=item["row_count"],
                rows_per_exact=item.get("helper_rows_per_exact"),
                candidate_share=item.get("candidate_helper_share"),
                pressure=display_pressure_label(item.get("pressure_label", "")),
                classes=item.get("helper_class_counts", {}),
                support_kinds=_top_counts(item.get("support_kind_counts", {})),
                helper_list=", ".join(item.get("helpers", [])),
            )
        )
    lines.extend(
        [
            "",
            "## All Adapters",
            "",
            "| Adapter | Fixtures | Files | Rows | Suspicious | Implemented |",
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


def _top_counts(value: object, *, limit: int = 5) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    pairs: list[tuple[str, int]] = []
    for key, raw_count in value.items():
        try:
            count = int(raw_count)
        except (TypeError, ValueError):
            continue
        pairs.append((str(key), count))
    return dict(sorted(pairs, key=lambda pair: (-pair[1], pair[0]))[:limit])


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
