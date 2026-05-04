#!/usr/bin/env python3
"""Build selector training targets from an incoming compile-variant overlay.

This is a post-run harness utility. It reads the judged overlay artifact created
by plan_incoming_compile_variant_overlay.py and turns its accepted/protected
rows into selector-risk training rows. It does not read source prose, gold KBs,
QA answer keys, strategy files, or raw compile outputs.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overlay-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    overlay_path = _resolve(args.overlay_json)
    report = build_report(
        overlay=json.loads(overlay_path.read_text(encoding="utf-8-sig")),
        overlay_path=overlay_path,
    )
    out_json = _resolve(args.out_json) if args.out_json else overlay_path.with_name("variant_selector_training_plan.json")
    out_md = _resolve(args.out_md) if args.out_md else overlay_path.with_name("variant_selector_training_plan.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_report(*, overlay: dict[str, Any], overlay_path: Path | None = None) -> dict[str, Any]:
    training_rows = _training_rows(overlay)
    variant_risks = _variant_risks(training_rows)
    for row in training_rows:
        selected_variant = str(row.get("selected_variant", ""))
        row["selected_variant_global_risk"] = _variant_global_risk(
            variant_risks.get(selected_variant, {}),
            selected_variant=selected_variant,
        )
        row["selector_recommendation"] = _row_recommendation(row)
    category_counts = Counter(str(row.get("category", "")) for row in training_rows)
    variant_modes = Counter(str(row.get("selector_recommendation", "")) for row in training_rows)
    summary = {
        "row_count": len(training_rows),
        "activation_training_target_count": int(category_counts.get("activation_training_target", 0)),
        "exact_protection_target_count": int(category_counts.get("exact_protection_target", 0)),
        "repair_training_target_count": int(category_counts.get("repair_training_target", 0)),
        "row_gated_only_target_count": int(variant_modes.get("row_gated_only", 0)),
        "safe_global_variant_target_count": int(variant_modes.get("safe_global_variant_candidate", 0)),
        "variant_count": len(variant_risks),
        "global_recommendation": _global_recommendation(training_rows, variant_risks),
    }
    return {
        "schema_version": "incoming_variant_selector_training_plan_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads incoming compile-variant overlay artifacts only.",
            "Does not read source prose, gold KBs, QA answer keys, strategy files, or raw compile outputs.",
            "Uses judged overlay rows to create selector/risk-gate training targets, not a deployable selector.",
            "Rows that accept a variant are activation examples; rows that keep baseline exact are exact-protection examples.",
        ],
        "artifacts": {"overlay_json": _display_path(overlay_path)},
        "overlay_summary": overlay.get("summary", {}),
        "summary": summary,
        "variant_risks": [variant_risks[key] for key in sorted(variant_risks)],
        "training_rows": training_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    overlay_summary = report.get("overlay_summary", {}) if isinstance(report.get("overlay_summary"), dict) else {}
    lines = [
        "# Incoming Variant Selector Training Plan",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "This report turns a judged overlay artifact into selector/risk-gate training rows.",
        "It does not read source prose, gold KBs, QA answer keys, strategy files, or raw compile outputs.",
        "",
        "## Summary",
        "",
        f"- Recommendation: `{summary.get('global_recommendation', '')}`",
        f"- Overlay target: `{_fmt_counts(overlay_summary.get('overlay_counts', {}))}`",
        f"- Activation training targets: `{summary.get('activation_training_target_count', 0)}`",
        f"- Exact-protection targets: `{summary.get('exact_protection_target_count', 0)}`",
        f"- Repair training targets: `{summary.get('repair_training_target_count', 0)}`",
        f"- Row-gated-only targets: `{summary.get('row_gated_only_target_count', 0)}`",
        "",
        "## Variant Risk Buckets",
        "",
        "| Variant | Accepted | Protected Regressions | Risk |",
        "| --- | ---: | ---: | --- |",
    ]
    for variant in report.get("variant_risks", []):
        if not isinstance(variant, dict):
            continue
        lines.append(
            f"| `{variant.get('variant', '')}` | {variant.get('accepted_row_count', 0)} | "
            f"{variant.get('protected_regression_row_count', 0)} | `{variant.get('global_risk', '')}` |"
        )
    lines.extend(
        [
            "",
            "## Training Rows",
            "",
            "| Category | Fixture | Row | Selected | Baseline | Risk | Question |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.get("training_rows", []):
        if not isinstance(row, dict):
            continue
        question = str(row.get("question", "")).replace("|", "/")
        lines.append(
            f"| `{row.get('category', '')}` | `{row.get('fixture', '')}` | `{row.get('id', '')}` | "
            f"`{row.get('selected_variant', '')}:{row.get('selected_verdict', '')}` | "
            f"`baseline:{row.get('baseline_verdict', '')}` | "
            f"`{row.get('selected_variant_global_risk', '')}` | {question} |"
        )
    lines.append("")
    return "\n".join(lines)


def _training_rows(overlay: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fixture in overlay.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        fixture_name = str(fixture.get("fixture", ""))
        rows.extend(
            _row_payload(fixture_name, item, category="activation_training_target")
            for item in fixture.get("accepted_variant_rows", [])
            if isinstance(item, dict)
        )
        rows.extend(
            _row_payload(fixture_name, item, category="exact_protection_target")
            for item in fixture.get("protected_baseline_exact_rows", [])
            if isinstance(item, dict)
        )
        rows.extend(
            _row_payload(fixture_name, item, category="repair_training_target")
            for item in fixture.get("unchanged_non_exact_rows", [])
            if isinstance(item, dict)
        )
    return rows


def _row_payload(fixture: str, item: dict[str, Any], *, category: str) -> dict[str, Any]:
    variants = item.get("variants", []) if isinstance(item.get("variants"), list) else []
    verdicts = {str(row.get("name", "")): str(row.get("verdict", "")) for row in variants if isinstance(row, dict)}
    failure_surfaces = {
        str(row.get("name", "")): str(row.get("failure_surface", ""))
        for row in variants
        if isinstance(row, dict)
    }
    selected_variant = str(item.get("selected_variant", ""))
    baseline_verdict = str(item.get("baseline_verdict", ""))
    selected_verdict = str(item.get("selected_verdict", ""))
    return {
        "fixture": fixture,
        "id": str(item.get("id", "")),
        "question": str(item.get("question", "")),
        "category": category,
        "baseline_verdict": baseline_verdict,
        "selected_variant": selected_variant,
        "selected_verdict": selected_verdict,
        "variant_verdicts": verdicts,
        "variant_failure_surfaces": failure_surfaces,
        "exact_variant_count": sum(1 for verdict in verdicts.values() if verdict == "exact"),
        "non_exact_variant_count": sum(1 for verdict in verdicts.values() if verdict != "exact"),
        "variant_disagreement": len(set(verdicts.values())) > 1,
        "row_signal": _row_signal(category=category, baseline_verdict=baseline_verdict, selected_verdict=selected_verdict),
    }


def _variant_risks(training_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    risks: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "variant": "",
            "accepted_row_count": 0,
            "protected_regression_row_count": 0,
            "repair_row_count": 0,
            "accepted_rows": [],
            "protected_regression_rows": [],
            "global_risk": "no_signal",
        }
    )
    for row in training_rows:
        category = str(row.get("category", ""))
        selected = str(row.get("selected_variant", ""))
        if selected and selected != "baseline":
            risks[selected]["variant"] = selected
        if category == "activation_training_target" and selected:
            risks[selected]["accepted_row_count"] += 1
            risks[selected]["accepted_rows"].append(_row_ref(row))
        for variant, verdict in (row.get("variant_verdicts", {}) or {}).items():
            if not variant or variant == "baseline":
                continue
            risks[variant]["variant"] = variant
            if category == "exact_protection_target" and verdict != "exact":
                risks[variant]["protected_regression_row_count"] += 1
                risks[variant]["protected_regression_rows"].append(_row_ref(row))
            elif category == "repair_training_target":
                risks[variant]["repair_row_count"] += 1
    for risk in risks.values():
        accepted = int(risk.get("accepted_row_count", 0))
        protected = int(risk.get("protected_regression_row_count", 0))
        if accepted and protected:
            risk["global_risk"] = "unsafe_global_variant_row_gate_required"
        elif accepted:
            risk["global_risk"] = "candidate_global_variant"
        elif protected:
            risk["global_risk"] = "regression_only_variant"
        else:
            risk["global_risk"] = "no_activation_signal"
    return dict(risks)


def _row_ref(row: dict[str, Any]) -> dict[str, str]:
    return {"fixture": str(row.get("fixture", "")), "id": str(row.get("id", ""))}


def _variant_global_risk(risk: dict[str, Any], *, selected_variant: str) -> str:
    if selected_variant == "baseline":
        return "baseline_protection"
    return str(risk.get("global_risk", "unmeasured_variant"))


def _row_recommendation(row: dict[str, Any]) -> str:
    category = str(row.get("category", ""))
    global_risk = str(row.get("selected_variant_global_risk", ""))
    if category == "exact_protection_target":
        return "protect_baseline"
    if category == "repair_training_target":
        return "needs_compile_or_query_repair"
    if global_risk == "candidate_global_variant":
        return "safe_global_variant_candidate"
    return "row_gated_only"


def _row_signal(*, category: str, baseline_verdict: str, selected_verdict: str) -> str:
    if category == "activation_training_target":
        return f"improve_{baseline_verdict}_to_{selected_verdict}"
    if category == "exact_protection_target":
        return "protect_baseline_exact"
    return "no_exact_variant_available"


def _global_recommendation(training_rows: list[dict[str, Any]], variant_risks: dict[str, dict[str, Any]]) -> str:
    if not training_rows:
        return "no_selector_training_signal"
    if any(str(row.get("global_risk")) == "unsafe_global_variant_row_gate_required" for row in variant_risks.values()):
        return "train_row_variant_selector_with_exact_protection"
    if any(str(row.get("category")) == "activation_training_target" for row in training_rows):
        return "train_variant_activation_selector"
    return "repair_compile_or_query_surface"


def _fmt_counts(counts: Any) -> str:
    if not isinstance(counts, dict):
        counts = {}
    return f"{counts.get('exact', 0)} / {counts.get('partial', 0)} / {counts.get('miss', 0)}"


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
