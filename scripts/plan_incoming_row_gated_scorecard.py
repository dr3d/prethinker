#!/usr/bin/env python3
"""Plan a row-gated incoming scorecard from a row-mode overlay artifact.

This utility reads existing scorecard and row-overlay artifacts only. It does
not read fixture source prose, gold KBs, QA reference answers, strategy files,
or failure labels beyond the labels already present in the scorecard overlay.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VERDICTS = ("exact", "partial", "miss")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-json", type=Path, required=True)
    parser.add_argument("--candidate-json", type=Path, required=True)
    parser.add_argument("--row-overlay-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baseline_path = _resolve(args.baseline_json)
    candidate_path = _resolve(args.candidate_json)
    overlay_path = _resolve(args.row_overlay_json)
    report = build_report(
        baseline=_load_json(baseline_path),
        candidate=_load_json(candidate_path),
        overlay=_load_json(overlay_path),
        baseline_path=baseline_path,
        candidate_path=candidate_path,
        overlay_path=overlay_path,
    )
    out_json = _resolve(args.out_json) if args.out_json else candidate_path.with_name("row_gated_scorecard_plan.json")
    out_md = _resolve(args.out_md) if args.out_md else candidate_path.with_name("row_gated_scorecard_plan.md")
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
    candidate: dict[str, Any],
    overlay: dict[str, Any],
    baseline_path: Path | None = None,
    candidate_path: Path | None = None,
    overlay_path: Path | None = None,
) -> dict[str, Any]:
    baseline_counts = _summary_counts(baseline)
    candidate_counts = _summary_counts(candidate)
    gated_counts = Counter(baseline_counts)
    fixture_rows: list[dict[str, Any]] = []
    accepted_total = 0
    rejected_total = 0
    unchanged_total = 0
    for fixture in overlay.get("fixtures", []) if isinstance(overlay.get("fixtures"), list) else []:
        if not isinstance(fixture, dict):
            continue
        accepted = _rows(fixture, "accepted_candidate_rows")
        rejected = _rows(fixture, "rejected_candidate_rows")
        unchanged = _rows(fixture, "unchanged_non_exact_rows")
        accepted_total += len(accepted)
        rejected_total += len(rejected)
        unchanged_total += len(unchanged)
        fixture_delta = Counter()
        for row in accepted:
            delta = _verdict_delta(
                baseline_verdict=str(row.get("baseline_verdict", "unknown")),
                candidate_verdict=str(row.get("candidate_verdict", "unknown")),
            )
            gated_counts.update(delta)
            fixture_delta.update(delta)
        fixture_rows.append(
            {
                "fixture": str(fixture.get("fixture", "")),
                "accepted_candidate_rows": accepted,
                "rejected_candidate_rows": rejected,
                "unchanged_non_exact_rows": unchanged,
                "gated_delta": {verdict: int(fixture_delta.get(verdict, 0)) for verdict in VERDICTS},
                "recommended_policy": str(fixture.get("recommended_policy", "")),
            }
        )
    gated_counts = Counter({verdict: max(0, int(gated_counts.get(verdict, 0))) for verdict in VERDICTS})
    qa_rows = int((baseline.get("summary") or {}).get("qa_rows", 0) or sum(gated_counts.values()))
    delta_vs_baseline = _count_delta(baseline_counts, gated_counts)
    delta_vs_candidate = _count_delta(candidate_counts, gated_counts)
    return {
        "schema_version": "incoming_row_gated_scorecard_plan_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads scorecard and row-overlay artifacts only.",
            "Does not inspect fixture source prose, gold KBs, QA reference answers, or strategy files.",
            "Accepted candidate rows are applied over the baseline; rejected rows keep baseline behavior.",
            "This is a row-gated planning artifact, not a global compile-mode promotion.",
        ],
        "artifacts": {
            "baseline_json": _display_path(baseline_path),
            "candidate_json": _display_path(candidate_path),
            "row_overlay_json": _display_path(overlay_path),
        },
        "summary": {
            "qa_rows": qa_rows,
            "baseline_counts": dict(baseline_counts),
            "candidate_counts": dict(candidate_counts),
            "row_gated_counts": dict(gated_counts),
            "delta_vs_baseline": dict(delta_vs_baseline),
            "delta_vs_candidate": dict(delta_vs_candidate),
            "accepted_candidate_row_count": accepted_total,
            "rejected_candidate_row_count": rejected_total,
            "unchanged_non_exact_row_count": unchanged_total,
            "recommendation": _recommendation(
                accepted=accepted_total,
                rejected=rejected_total,
                delta_vs_baseline=delta_vs_baseline,
            ),
        },
        "fixtures": fixture_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    gated = summary.get("row_gated_counts", {}) if isinstance(summary.get("row_gated_counts"), dict) else {}
    baseline = summary.get("baseline_counts", {}) if isinstance(summary.get("baseline_counts"), dict) else {}
    candidate = summary.get("candidate_counts", {}) if isinstance(summary.get("candidate_counts"), dict) else {}
    delta_base = summary.get("delta_vs_baseline", {}) if isinstance(summary.get("delta_vs_baseline"), dict) else {}
    lines = [
        "# Incoming Row-Gated Scorecard Plan",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "This report reads scorecard and row-overlay artifacts only. It does not read",
        "source prose, gold KBs, QA reference answers, or strategy files.",
        "",
        "## Summary",
        "",
        f"- Recommendation: `{summary.get('recommendation', '')}`",
        f"- Baseline: `{_label(baseline)}`",
        f"- Candidate: `{_label(candidate)}`",
        f"- Row-gated: `{_label(gated)}`",
        f"- Delta vs baseline: `{_label(delta_base, signed=True)}`",
        f"- Accepted candidate rows: `{summary.get('accepted_candidate_row_count', 0)}`",
        f"- Rejected candidate rows: `{summary.get('rejected_candidate_row_count', 0)}`",
        f"- Unchanged non-exact rows: `{summary.get('unchanged_non_exact_row_count', 0)}`",
        "",
        "## Fixture Gates",
        "",
        "| Fixture | Policy | Delta | Accept | Reject | Unchanged |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for fixture in report.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        delta = fixture.get("gated_delta", {}) if isinstance(fixture.get("gated_delta"), dict) else {}
        lines.append(
            f"| `{fixture.get('fixture', '')}` | `{fixture.get('recommended_policy', '')}` | "
            f"`{_label(delta, signed=True)}` | "
            f"{len(fixture.get('accepted_candidate_rows', []))} | "
            f"{len(fixture.get('rejected_candidate_rows', []))} | "
            f"{len(fixture.get('unchanged_non_exact_rows', []))} |"
        )
    lines.extend(["", "## Accepted Rows", ""])
    for fixture in report.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        for row in fixture.get("accepted_candidate_rows", []):
            if not isinstance(row, dict):
                continue
            question = str(row.get("question", "")).replace("|", "/")
            lines.append(
                f"- `{fixture.get('fixture', '')}` `{row.get('id', '')}`: "
                f"`{row.get('baseline_verdict', '')}` -> `{row.get('candidate_verdict', '')}`; {question}"
            )
    lines.extend(["", "## Rejected Rows", ""])
    for fixture in report.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        for row in fixture.get("rejected_candidate_rows", []):
            if not isinstance(row, dict):
                continue
            question = str(row.get("question", "")).replace("|", "/")
            lines.append(
                f"- `{fixture.get('fixture', '')}` `{row.get('id', '')}`: "
                f"`{row.get('baseline_verdict', '')}` -> `{row.get('candidate_verdict', '')}`; {question}"
            )
    lines.append("")
    return "\n".join(lines)


def _recommendation(*, accepted: int, rejected: int, delta_vs_baseline: Counter[str]) -> str:
    exact_delta = int(delta_vs_baseline.get("exact", 0))
    miss_delta = int(delta_vs_baseline.get("miss", 0))
    if accepted and (exact_delta > 0 or miss_delta < 0):
        if rejected:
            return "row_gated_overlay_required"
        return "row_gated_overlay_candidate"
    if rejected:
        return "protect_baseline_only"
    return "no_row_gated_gain"


def _summary_counts(scorecard: dict[str, Any]) -> Counter[str]:
    summary = scorecard.get("summary", {}) if isinstance(scorecard.get("summary"), dict) else {}
    return Counter(
        {
            "exact": int(summary.get("exact_rows", 0) or 0),
            "partial": int(summary.get("partial_rows", 0) or 0),
            "miss": int(summary.get("miss_rows", 0) or 0),
        }
    )


def _verdict_delta(*, baseline_verdict: str, candidate_verdict: str) -> Counter[str]:
    delta: Counter[str] = Counter()
    baseline = _normalize_verdict(baseline_verdict)
    candidate = _normalize_verdict(candidate_verdict)
    if baseline in VERDICTS:
        delta[baseline] -= 1
    if candidate in VERDICTS:
        delta[candidate] += 1
    return delta


def _count_delta(before: Counter[str], after: Counter[str]) -> Counter[str]:
    return Counter({verdict: int(after.get(verdict, 0)) - int(before.get(verdict, 0)) for verdict in VERDICTS})


def _rows(fixture: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = fixture.get(key, [])
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def _normalize_verdict(value: str) -> str:
    text = str(value or "").strip()
    return text if text in VERDICTS else "unknown"


def _label(counts: dict[str, Any], *, signed: bool = False) -> str:
    values: list[str] = []
    for verdict in VERDICTS:
        number = int(counts.get(verdict, 0) or 0)
        if signed and number > 0:
            values.append(f"+{number}")
        else:
            values.append(str(number))
    return " / ".join(values)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return payload


def _resolve(path: Path | None) -> Path:
    if path is None:
        return REPO_ROOT
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


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
