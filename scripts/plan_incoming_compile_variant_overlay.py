#!/usr/bin/env python3
"""Plan judged row overlays across multiple incoming compile variants."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VERDICT_RANK = {"exact": 3, "partial": 2, "miss": 1, "not_judged": 0, "unknown": 0, "": 0}
VERDICT_KEYS = ("exact", "partial", "miss")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-json", type=Path, required=True)
    parser.add_argument(
        "--candidate-json",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Candidate scorecard path labeled by compile/query variant name. May be repeated.",
    )
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baseline_path = _resolve(args.baseline_json)
    candidates = [_parse_named_path(value) for value in args.candidate_json]
    report = build_report(
        baseline=json.loads(baseline_path.read_text(encoding="utf-8-sig")),
        candidates=[
            (name, json.loads(path.read_text(encoding="utf-8-sig")), path)
            for name, path in candidates
        ],
        baseline_path=baseline_path,
    )
    out_json = _resolve(args.out_json) if args.out_json else baseline_path.with_name("compile_variant_overlay_plan.json")
    out_md = _resolve(args.out_md) if args.out_md else baseline_path.with_name("compile_variant_overlay_plan.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_report(
    *,
    baseline: dict[str, Any],
    candidates: list[tuple[str, dict[str, Any], Path | None]],
    baseline_path: Path | None = None,
) -> dict[str, Any]:
    variant_names = ["baseline", *[name for name, _scorecard, _path in candidates]]
    fixture_rows = _fixture_rows(baseline, candidates)
    accepted_rows = [
        item
        for fixture in fixture_rows
        for item in fixture.get("accepted_variant_rows", [])
        if isinstance(item, dict)
    ]
    protected_rows = [
        item
        for fixture in fixture_rows
        for item in fixture.get("protected_baseline_exact_rows", [])
        if isinstance(item, dict)
    ]
    unchanged_rows = [
        item
        for fixture in fixture_rows
        for item in fixture.get("unchanged_non_exact_rows", [])
        if isinstance(item, dict)
    ]
    baseline_counts = _counts(baseline)
    overlay_counts = dict(baseline_counts)
    for item in accepted_rows:
        before = str(item.get("baseline_verdict", "unknown"))
        after = str(item.get("selected_verdict", "unknown"))
        if before in overlay_counts:
            overlay_counts[before] -= 1
        if after in overlay_counts:
            overlay_counts[after] += 1

    return {
        "schema_version": "incoming_compile_variant_overlay_plan_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads judged scorecard artifacts only.",
            "Does not inspect fixture source prose, gold KBs, or reinterpret answer meaning.",
            "This is a diagnostic upper-bound planner for compile/query variant selection, not a deployable selector policy.",
            "A missing row in non_exact_rows is treated as exact within that scorecard artifact.",
        ],
        "artifacts": {
            "baseline_json": _display_path(baseline_path),
            "candidate_jsons": [
                {"name": name, "path": _display_path(path)}
                for name, _scorecard, path in candidates
            ],
        },
        "summary": {
            "variant_count": len(variant_names),
            "variants": variant_names,
            "qa_rows": int(baseline.get("summary", {}).get("qa_rows", 0) or 0),
            "baseline_counts": baseline_counts,
            "overlay_counts": overlay_counts,
            "delta_vs_baseline": {
                key: int(overlay_counts.get(key, 0) - baseline_counts.get(key, 0))
                for key in VERDICT_KEYS
            },
            "accepted_variant_row_count": len(accepted_rows),
            "protected_baseline_exact_row_count": len(protected_rows),
            "unchanged_non_exact_row_count": len(unchanged_rows),
            "recommendation": _recommendation(accepted=len(accepted_rows), protected=len(protected_rows)),
        },
        "fixtures": fixture_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    baseline = summary.get("baseline_counts", {}) if isinstance(summary.get("baseline_counts"), dict) else {}
    overlay = summary.get("overlay_counts", {}) if isinstance(summary.get("overlay_counts"), dict) else {}
    delta = summary.get("delta_vs_baseline", {}) if isinstance(summary.get("delta_vs_baseline"), dict) else {}
    lines = [
        "# Incoming Compile-Variant Overlay Plan",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "This report is a judged-artifact diagnostic upper bound. It does not read source prose,",
        "gold KBs, or strategy files, and it is not a deployable selector policy.",
        "",
        "## Summary",
        "",
        f"- Recommendation: `{summary.get('recommendation', '')}`",
        f"- Variants: `{', '.join(str(item) for item in summary.get('variants', []))}`",
        f"- Baseline: `{_fmt_counts(baseline)}`",
        f"- Overlay: `{_fmt_counts(overlay)}`",
        f"- Delta vs baseline: `{_fmt_delta(delta)}`",
        f"- Accepted variant rows: `{summary.get('accepted_variant_row_count', 0)}`",
        f"- Protected baseline-exact rows: `{summary.get('protected_baseline_exact_row_count', 0)}`",
        f"- Unchanged non-exact rows: `{summary.get('unchanged_non_exact_row_count', 0)}`",
        "",
        "## Fixture Gates",
        "",
        "| Fixture | Policy | Accept | Protect | Unchanged |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for fixture in report.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        lines.append(
            f"| `{fixture.get('fixture', '')}` | `{fixture.get('recommended_policy', '')}` | "
            f"{len(fixture.get('accepted_variant_rows', []))} | "
            f"{len(fixture.get('protected_baseline_exact_rows', []))} | "
            f"{len(fixture.get('unchanged_non_exact_rows', []))} |"
        )
    lines.extend(["", "## Accepted Variant Rows", ""])
    _append_rows(lines, report, "accepted_variant_rows", include_selected=True)
    lines.extend(["", "## Protected Baseline-Exact Rows", ""])
    _append_rows(lines, report, "protected_baseline_exact_rows", include_selected=False)
    lines.append("")
    return "\n".join(lines)


def _fixture_rows(
    baseline: dict[str, Any],
    candidates: list[tuple[str, dict[str, Any], Path | None]],
) -> list[dict[str, Any]]:
    scorecards = [("baseline", baseline), *[(name, scorecard) for name, scorecard, _path in candidates]]
    fixture_names = sorted(
        {
            str(row.get("fixture", ""))
            for _name, scorecard in scorecards
            for row in scorecard.get("fixtures", [])
            if isinstance(row, dict) and row.get("fixture")
        }
    )
    rows: list[dict[str, Any]] = []
    for fixture in fixture_names:
        by_variant = {
            name: _non_exact_by_id(_fixture(scorecard, fixture))
            for name, scorecard in scorecards
        }
        row_ids = sorted({row_id for rows_by_id in by_variant.values() for row_id in rows_by_id})
        accepted: list[dict[str, Any]] = []
        protected: list[dict[str, Any]] = []
        unchanged: list[dict[str, Any]] = []
        for row_id in row_ids:
            variants = [
                _variant_row(name=name, row=rows_by_id.get(row_id))
                for name, rows_by_id in by_variant.items()
            ]
            baseline_variant = variants[0]
            selected = _select_variant(variants)
            comparison = {
                "id": row_id,
                "question": _question_for(variants),
                "baseline_verdict": baseline_variant["verdict"],
                "selected_variant": selected["name"],
                "selected_verdict": selected["verdict"],
                "variants": variants,
            }
            if _rank(selected["verdict"]) > _rank(baseline_variant["verdict"]):
                accepted.append(comparison)
            elif baseline_variant["verdict"] == "exact" and any(
                _rank(item["verdict"]) < _rank("exact") for item in variants[1:]
            ):
                protected.append(comparison)
            elif baseline_variant["verdict"] != "exact":
                unchanged.append(comparison)
        rows.append(
            {
                "fixture": fixture,
                "recommended_policy": _fixture_policy(accepted=accepted, protected=protected),
                "accepted_variant_rows": accepted,
                "protected_baseline_exact_rows": protected,
                "unchanged_non_exact_rows": unchanged,
            }
        )
    return rows


def _append_rows(lines: list[str], report: dict[str, Any], key: str, *, include_selected: bool) -> None:
    found = False
    for fixture in report.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        for item in fixture.get(key, []):
            if not isinstance(item, dict):
                continue
            found = True
            question = str(item.get("question", "")).replace("|", "/")
            if include_selected:
                lines.append(
                    f"- `{fixture.get('fixture', '')}` `{item.get('id', '')}`: "
                    f"`{item.get('baseline_verdict', '')}` -> `{item.get('selected_verdict', '')}` "
                    f"via `{item.get('selected_variant', '')}`; {question}"
                )
            else:
                lines.append(
                    f"- `{fixture.get('fixture', '')}` `{item.get('id', '')}`: "
                    f"kept `baseline`; {question}"
                )
    if not found:
        lines.append("- none")


def _variant_row(*, name: str, row: dict[str, Any] | None) -> dict[str, Any]:
    payload = row or {}
    return {
        "name": name,
        "verdict": _row_verdict(row),
        "failure_surface": str(payload.get("failure_surface", "")),
        "question": str(payload.get("question", "")),
    }


def _select_variant(variants: list[dict[str, Any]]) -> dict[str, Any]:
    return max(variants, key=lambda item: (_rank(str(item.get("verdict", ""))), item.get("name") == "baseline"))


def _question_for(variants: list[dict[str, Any]]) -> str:
    for item in variants:
        question = str(item.get("question", ""))
        if question:
            return question
    return ""


def _fixture(scorecard: dict[str, Any], fixture: str) -> dict[str, Any]:
    for row in scorecard.get("fixtures", []):
        if isinstance(row, dict) and str(row.get("fixture", "")) == fixture:
            return row
    return {}


def _non_exact_by_id(fixture_row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = fixture_row.get("non_exact_rows", []) if isinstance(fixture_row.get("non_exact_rows"), list) else []
    return {str(row.get("id", "")): row for row in rows if isinstance(row, dict) and row.get("id")}


def _row_verdict(row: dict[str, Any] | None) -> str:
    if not row:
        return "exact"
    return str(row.get("verdict", "unknown") or "unknown")


def _rank(verdict: str) -> int:
    return VERDICT_RANK.get(str(verdict), 0)


def _counts(scorecard: dict[str, Any]) -> dict[str, int]:
    summary = scorecard.get("summary", {}) if isinstance(scorecard.get("summary"), dict) else {}
    return {key: int(summary.get(f"{key}_rows", 0) or 0) for key in VERDICT_KEYS}


def _recommendation(*, accepted: int, protected: int) -> str:
    if accepted and protected:
        return "row_variant_selector_with_exact_protection"
    if accepted:
        return "row_variant_overlay_available"
    return "no_variant_overlay_gain"


def _fixture_policy(*, accepted: list[dict[str, Any]], protected: list[dict[str, Any]]) -> str:
    if accepted and protected:
        return "row_variant_selector_required"
    if accepted:
        return "accept_variant_rows"
    if protected:
        return "protect_baseline_exact_rows"
    return "no_row_delta"


def _fmt_counts(counts: dict[str, Any]) -> str:
    return f"{counts.get('exact', 0)} / {counts.get('partial', 0)} / {counts.get('miss', 0)}"


def _fmt_delta(delta: dict[str, Any]) -> str:
    return f"{int(delta.get('exact', 0)):+d} / {int(delta.get('partial', 0)):+d} / {int(delta.get('miss', 0)):+d}"


def _parse_named_path(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise SystemExit(f"--candidate-json must be NAME=PATH, got: {value}")
    name, raw_path = value.split("=", 1)
    clean_name = name.strip()
    if not clean_name:
        raise SystemExit(f"--candidate-json name cannot be empty: {value}")
    return clean_name, _resolve(Path(raw_path.strip()))


def _resolve(path: Path | None) -> Path:
    if path is None:
        return REPO_ROOT
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return ""
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
