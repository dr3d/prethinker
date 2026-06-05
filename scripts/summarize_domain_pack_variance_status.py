#!/usr/bin/env python3
"""Summarize repeated domain-pack bundle roots as variance bands.

This report is a guard against favorable-draw promotion. It reads retained
domain-lens bundle manifests and typed summary reports; it does not read source
prose, QA questions, judge output, or oracle answers.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.report_freshness import apply_markdown_freshness_check


DEFAULT_MANIFEST = REPO_ROOT / "datasets" / "domain_pack_measurements" / "domain_pack_variance_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument(
        "--expect-md",
        type=Path,
        default=None,
        help="Fail if this markdown file differs from the freshly rendered report.",
    )
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(manifest_path=args.manifest)
    rendered_md = render_markdown(report)
    if args.expect_md:
        apply_markdown_freshness_check(
            report=report,
            expected_path=args.expect_md,
            rendered_md=rendered_md,
        )
        rendered_md = render_markdown(report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(rendered_md, encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    blocked = report["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not blocked else 1


def build_report(*, manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    groups = [_group_row(group) for group in manifest.get("groups", []) if isinstance(group, dict)]
    blockers = [
        reason
        for group in groups
        for reason in group.get("blocking_reasons", [])
    ]
    warnings = [
        warning
        for group in groups
        for warning in group.get("warnings", [])
    ]
    root_count = sum(len(group.get("roots", [])) for group in groups)
    return {
        "schema_version": "domain_pack_variance_status_v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "summary": {
            "status": "pass" if not blockers else "fail",
            "group_count": len(groups),
            "root_count": root_count,
            "blocking_reasons": blockers,
            "warning_count": len(warnings),
            "warnings": warnings,
        },
        "groups": groups,
    }


def _group_row(group: dict[str, Any]) -> dict[str, Any]:
    fixture_id = str(group.get("fixture_id") or "")
    roots = [
        _root_row(root_spec=root_spec, fixture_id=fixture_id)
        for root_spec in group.get("roots", [])
        if isinstance(root_spec, dict)
    ]
    blockers = [
        reason
        for root in roots
        for reason in root.get("blocking_reasons", [])
    ]
    warnings = [
        warning
        for root in roots
        for warning in root.get("warnings", [])
    ]
    supported_values = [
        int(root["supported_fact_count"])
        for root in roots
        if root.get("manifest_status") == "present"
    ]
    expected_values = [
        int(root["expected_fact_count"])
        for root in roots
        if root.get("manifest_status") == "present"
    ]
    forbidden_values = [
        int(root["supported_forbidden_fact_count"])
        for root in roots
        if root.get("manifest_status") == "present"
    ]
    unexpected_values = [
        int(root["unexpected_fact_count"])
        for root in roots
        if root.get("manifest_status") == "present"
    ]
    return {
        "id": str(group.get("id") or ""),
        "title": str(group.get("title") or group.get("id") or ""),
        "fixture_id": fixture_id,
        "claim_read": str(group.get("claim_read") or ""),
        "root_count": len(roots),
        "supported_min": min(supported_values) if supported_values else None,
        "supported_max": max(supported_values) if supported_values else None,
        "expected_min": min(expected_values) if expected_values else None,
        "expected_max": max(expected_values) if expected_values else None,
        "supported_forbidden_total": sum(forbidden_values),
        "unexpected_min": min(unexpected_values) if unexpected_values else None,
        "unexpected_max": max(unexpected_values) if unexpected_values else None,
        "blocking_reasons": blockers,
        "warnings": warnings,
        "status": "pass" if not blockers else "fail",
        "roots": roots,
    }


def _root_row(*, root_spec: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    root_id = str(root_spec.get("id") or "")
    root = Path(str(root_spec.get("path") or ""))
    manifest_path = root / "manifest.json"
    row: dict[str, Any] = {
        "id": root_id,
        "role": str(root_spec.get("role") or ""),
        "root": str(root),
        "manifest_status": "missing",
        "blocking_reasons": [],
        "warnings": [],
    }
    if not manifest_path.exists():
        row["blocking_reasons"].append(f"{root_id}:missing_manifest:{manifest_path}")
        return row

    manifest = _load_json(manifest_path)
    score = dict(manifest.get("score_summary") or {})
    settings = dict(manifest.get("settings") or {})
    union_atom = dict(manifest.get("union_atom_audit_summary") or {})
    value_domain = manifest.get("union_carrier_value_domain_summary")
    typed_reconcile = manifest.get("typed_reconcile_summary")
    series = _load_optional_json(root / "reports" / "typed_micro_series_summary.json")
    per_run_exact, per_run_rows = _per_run_counts(series=series, score=score)

    row.update(
        {
            "manifest_status": "present",
            "label": str(manifest.get("label") or ""),
            "fixture_id": str(manifest.get("fixture") or ""),
            "compile_count": int(score.get("compile_count") or manifest.get("repeat") or 0),
            "expected_fact_count": int(score.get("expected_fact_count") or 0),
            "supported_fact_count": int(score.get("supported_fact_count") or 0),
            "forbidden_fact_count": int(score.get("forbidden_fact_count") or 0),
            "supported_forbidden_fact_count": int(score.get("supported_forbidden_fact_count") or 0),
            "unexpected_fact_count": int(score.get("unexpected_fact_count") or 0),
            "per_run_exact": per_run_exact,
            "per_run_rows": per_run_rows,
            "backend": str(settings.get("backend") or ""),
            "model": str(settings.get("model") or ""),
            "temperature": settings.get("temperature", ""),
            "top_p": settings.get("top_p", ""),
            "num_ctx": settings.get("num_ctx", ""),
            "matcher": str(settings.get("matcher") or ""),
            "support_threshold": settings.get("support_threshold", ""),
            "atom_shape_blocker_count": int(union_atom.get("atom_shape_blocker_count") or 0),
            "lens_scope_blocker_count": int(union_atom.get("lens_scope_blocker_count") or 0),
            "registered_fact_rate": union_atom.get("registered_fact_rate", ""),
            "value_domain_status": _value_domain_status(value_domain),
            "value_domain_violation_count": _value_domain_violation_count(value_domain),
            "typed_reconcile_fact_count": _typed_reconcile_fact_count(typed_reconcile),
        }
    )
    _add_root_blockers(row=row, expected_fixture_id=fixture_id)
    return row


def _add_root_blockers(*, row: dict[str, Any], expected_fixture_id: str) -> None:
    root_id = str(row.get("id") or "")
    if expected_fixture_id and row.get("fixture_id") != expected_fixture_id:
        row["blocking_reasons"].append(
            f"{root_id}:fixture_mismatch:{row.get('fixture_id')}!={expected_fixture_id}"
        )
    if int(row.get("supported_forbidden_fact_count") or 0) > 0:
        row["blocking_reasons"].append(f"{root_id}:supported_forbidden_fact")
    if int(row.get("atom_shape_blocker_count") or 0) > 0:
        row["blocking_reasons"].append(f"{root_id}:atom_shape_blocker")
    if int(row.get("lens_scope_blocker_count") or 0) > 0:
        row["blocking_reasons"].append(f"{root_id}:lens_scope_blocker")
    value_violations = row.get("value_domain_violation_count")
    if isinstance(value_violations, int) and value_violations > 0:
        row["blocking_reasons"].append(f"{root_id}:value_domain_violation")
    if value_violations is None:
        row["warnings"].append(f"{root_id}:value_domain_report_not_recorded")


def _per_run_counts(*, series: dict[str, Any] | None, score: dict[str, Any]) -> tuple[int, int]:
    if isinstance(series, dict):
        runs = [run for run in series.get("runs", []) if isinstance(run, dict)]
        if runs:
            exact = sum(int(run.get("matched_fact_count") or 0) for run in runs)
            expected = sum(int(run.get("expected_fact_count") or 0) for run in runs)
            return exact, expected
    compile_count = int(score.get("compile_count") or 0)
    expected_count = int(score.get("expected_fact_count") or 0)
    supported_count = int(score.get("supported_fact_count") or 0)
    return supported_count, compile_count * expected_count


def _value_domain_status(value_domain: Any) -> str:
    if not isinstance(value_domain, dict):
        return "not_recorded"
    return str(value_domain.get("status") or "unknown")


def _value_domain_violation_count(value_domain: Any) -> int | None:
    if not isinstance(value_domain, dict):
        return None
    return int(value_domain.get("violation_count") or 0)


def _typed_reconcile_fact_count(typed_reconcile: Any) -> int | None:
    if not isinstance(typed_reconcile, dict):
        return None
    value = typed_reconcile.get("reconciled_fact_count")
    return int(value) if value is not None else None


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Domain Pack Variance Status",
        "",
        "Generated from retained domain-lens bundle manifests and typed summary reports.",
        "This report does not read source prose, QA questions, judge output, or oracle answers.",
        "",
        "## Summary",
        "",
        f"- Status: `{summary['status']}`",
        f"- Groups: `{summary['group_count']}`",
        f"- Roots: `{summary['root_count']}`",
        f"- Warnings: `{summary['warning_count']}`",
    ]
    blockers = summary.get("blocking_reasons") or []
    if blockers:
        lines.extend(["", "Blocking reasons:"])
        lines.extend(f"- `{reason}`" for reason in blockers)
    warnings = summary.get("warnings") or []
    if warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- `{warning}`" for warning in warnings)

    lines.extend(
        [
            "",
            "## Groups",
            "",
            "| Group | Fixture | Roots | Support Band | Forbidden Total | Unexpected Band | Status |",
            "| --- | --- | ---: | --- | ---: | --- | --- |",
        ]
    )
    for group in report.get("groups", []):
        lines.append(
            "| `{}` | `{}` | {} | {} | {} | {} | `{}` |".format(
                group["id"],
                group["fixture_id"],
                group["root_count"],
                _band(group.get("supported_min"), group.get("supported_max"), group.get("expected_min"), group.get("expected_max")),
                group["supported_forbidden_total"],
                _count_band(group.get("unexpected_min"), group.get("unexpected_max")),
                group["status"],
            )
        )

    for group in report.get("groups", []):
        lines.extend(["", f"## {group['title']}", ""])
        lines.extend(
            [
                f"- Group: `{group['id']}`",
                f"- Fixture: `{group['fixture_id']}`",
                f"- Read: {group['claim_read']}",
                f"- Support band: {_band(group.get('supported_min'), group.get('supported_max'), group.get('expected_min'), group.get('expected_max'))}",
                f"- Supported forbidden total: `{group['supported_forbidden_total']}`",
                f"- Unexpected band: {_count_band(group.get('unexpected_min'), group.get('unexpected_max'))}",
                f"- Status: `{group['status']}`",
                "",
                "| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |",
                "| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
            ]
        )
        for root in group.get("roots", []):
            if root.get("manifest_status") != "present":
                lines.append(
                    "| `{}` | {} | missing |  |  |  | `{}` |  |  |".format(
                        root["id"],
                        root["role"],
                        "; ".join(root.get("blocking_reasons") or []),
                    )
                )
                continue
            lines.append(
                "| `{}` | {} | `{}/{}` | `{}/{}` | {} | {} | {} | {} | {} |".format(
                    root["id"],
                    root["role"],
                    root["supported_fact_count"],
                    root["expected_fact_count"],
                    root["per_run_exact"],
                    root["per_run_rows"],
                    root["supported_forbidden_fact_count"],
                    root["unexpected_fact_count"],
                    _gate_summary(root),
                    _settings_summary(root),
                    _reconcile_summary(root),
                )
            )
        lines.extend(["", "Roots:"])
        for root in group.get("roots", []):
            lines.append(f"- `{root['id']}`: `{root['root']}`")

    return "\n".join(lines).rstrip() + "\n"


def _band(
    supported_min: int | None,
    supported_max: int | None,
    expected_min: int | None,
    expected_max: int | None,
) -> str:
    if supported_min is None or supported_max is None:
        return "`n/a`"
    expected = str(expected_min) if expected_min == expected_max else f"{expected_min}-{expected_max}"
    supported = str(supported_min) if supported_min == supported_max else f"{supported_min}-{supported_max}"
    return f"`{supported}/{expected}`"


def _count_band(min_value: int | None, max_value: int | None) -> str:
    if min_value is None or max_value is None:
        return "`n/a`"
    if min_value == max_value:
        return f"`{min_value}`"
    return f"`{min_value}-{max_value}`"


def _gate_summary(root: dict[str, Any]) -> str:
    return (
        f"atom `{root['atom_shape_blocker_count']}`; "
        f"lens `{root['lens_scope_blocker_count']}`; "
        f"value `{root['value_domain_status']}`"
    )


def _settings_summary(root: dict[str, Any]) -> str:
    return (
        f"`{root['backend']}` `{root['model']}`; "
        f"temp `{root['temperature']}`; top_p `{root['top_p']}`; "
        f"ctx `{root['num_ctx']}`; matcher `{root['matcher']}`"
    )


def _reconcile_summary(root: dict[str, Any]) -> str:
    count = root.get("typed_reconcile_fact_count")
    if count is None:
        return "`not_recorded`"
    return f"`{count}` value-mode facts"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


if __name__ == "__main__":
    raise SystemExit(main())
