"""Structural struggle detection for multi-pass semantic harnesses.

This module does not inspect source prose or infer answers. It summarizes
already-recorded harness telemetry so a run can stop when extra passes are no
longer producing new admitted structure or safer selection behavior.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def assess_semantic_progress(
    *,
    surface_contribution: list[dict[str, Any]] | None = None,
    selector_governor_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Return a structural progress/struggle assessment for a harness run."""

    rows = [row for row in surface_contribution or [] if isinstance(row, dict)]
    pass_count = len(rows)
    unique_total = sum(int(row.get("unique_contribution_count", 0) or 0) for row in rows)
    duplicate_total = sum(int(row.get("duplicate_count", 0) or 0) for row in rows)
    emitted_total = unique_total + duplicate_total
    duplicate_ratio = round(duplicate_total / emitted_total, 3) if emitted_total else 0.0
    flag_counts = _surface_flag_counts(rows)
    stale_tail_count = _stale_tail_count(rows)
    recent_unique = sum(int(row.get("unique_contribution_count", 0) or 0) for row in rows[-2:])
    selector_counts = {str(key): int(value or 0) for key, value in (selector_governor_counts or {}).items()}
    selector_fail_count = sum(count for key, count in selector_counts.items() if key.endswith("_fail"))

    stop_reasons: list[str] = []
    caution_reasons: list[str] = []
    if pass_count and unique_total == 0:
        stop_reasons.append("no_new_admitted_surface")
    if stale_tail_count >= 2:
        stop_reasons.append("repeated_stale_pass_tail")
    if int(flag_counts.get("skip_heavy", 0)) >= 2:
        stop_reasons.append("repeated_skip_heavy_passes")
    if int(flag_counts.get("skip_heavy", 0)):
        caution_reasons.append("skip_heavy_pass_present")
    if selector_fail_count:
        caution_reasons.append("selector_governor_failures_present")
    if duplicate_ratio >= 0.65 and emitted_total >= 8:
        caution_reasons.append("high_duplicate_surface_ratio")
    if int(flag_counts.get("thin_surface", 0)):
        caution_reasons.append("thin_surface")
    if pass_count >= 2 and recent_unique == 0:
        caution_reasons.append("recent_passes_added_no_unique_surface")

    if stop_reasons:
        zombie_risk = "high"
        recommended_action = "stop_and_report_struggle"
    elif caution_reasons:
        zombie_risk = "medium"
        recommended_action = "continue_only_with_named_expected_contribution"
    else:
        zombie_risk = "low"
        recommended_action = "continue"

    return {
        "schema_version": "semantic_progress_assessment_v1",
        "zombie_risk": zombie_risk,
        "recommended_action": recommended_action,
        "stop_reasons": stop_reasons,
        "caution_reasons": caution_reasons,
        "pass_count": pass_count,
        "semantic_progress_delta": {
            "unique_contribution_total": unique_total,
            "duplicate_total": duplicate_total,
            "duplicate_ratio": duplicate_ratio,
            "recent_unique_contribution_count": recent_unique,
            "stale_tail_count": stale_tail_count,
        },
        "surface_flag_counts": dict(flag_counts),
        "selector_governor": {
            "counts": selector_counts,
            "fail_count": selector_fail_count,
        },
    }


def _surface_flag_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        flags = row.get("health_flags", [])
        if not isinstance(flags, list):
            continue
        for flag in flags:
            text = str(flag).strip()
            if text:
                counts[text] += 1
    return counts


def _stale_tail_count(rows: list[dict[str, Any]]) -> int:
    count = 0
    for row in reversed(rows):
        flags = {str(flag).strip() for flag in row.get("health_flags", []) if str(flag).strip()} if isinstance(row.get("health_flags"), list) else set()
        unique_count = int(row.get("unique_contribution_count", 0) or 0)
        if unique_count == 0 or "zero_yield" in flags or "no_unique_surface" in flags:
            count += 1
            continue
        break
    return count
