#!/usr/bin/env python3
"""Roll up incoming fixture smoke summaries into a compact scorecard."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "tmp" / "incoming_smoke_summaries"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = _resolve(args.root)
    reports = [
        json.loads(path.read_text(encoding="utf-8-sig"))
        for path in sorted(root.glob("*_smoke_summary.json"))
        if path.name != "scorecard_smoke_summary.json"
    ]
    scorecard = build_scorecard(reports, root=root)

    out_json = _resolve(args.out_json) if args.out_json else root / "scorecard.json"
    out_md = _resolve(args.out_md) if args.out_md else root / "scorecard.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(scorecard, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(scorecard), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(scorecard["summary"], sort_keys=True))
    return 0


def build_scorecard(reports: list[dict[str, Any]], *, root: Path | None = None) -> dict[str, Any]:
    fixtures = [_fixture_row(report) for report in reports]
    fixtures.sort(key=lambda row: str(row.get("fixture", "")))

    judge_counts: Counter[str] = Counter()
    failure_counts: Counter[str] = Counter()
    semantic_counts: Counter[str] = Counter()
    compile_counts: Counter[str] = Counter()
    for row in fixtures:
        judge_counts.update(_counter_from_dict(row.get("judge_counts")))
        failure_counts.update(_counter_from_dict(row.get("failure_surface_counts")))
        semantic_counts.update([str(row.get("semantic_progress_risk", "")) or "unknown"])
        compile_counts.update([str(row.get("compile_status", "")) or "unknown"])

    qa_rows = sum(int(row.get("qa_rows", 0) or 0) for row in fixtures)
    exact = int(judge_counts.get("exact", 0))
    scorecard = {
        "schema_version": "incoming_fixture_smoke_scorecard_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": _display_path(root) if root else "",
        "policy": [
            "Rolls up smoke-summary artifacts only.",
            "Does not inspect fixture source prose or reinterpret answers.",
        ],
        "summary": {
            "fixture_count": len(fixtures),
            "compiled_count": int(compile_counts.get("compiled", 0)),
            "compile_failed_count": int(sum(count for status, count in compile_counts.items() if status != "compiled")),
            "qa_rows": qa_rows,
            "exact_rows": exact,
            "partial_rows": int(judge_counts.get("partial", 0)),
            "miss_rows": int(judge_counts.get("miss", 0)),
            "exact_rate": round(exact / qa_rows, 4) if qa_rows else None,
            "judge_counts": dict(sorted(judge_counts.items())),
            "compile_status_counts": dict(sorted(compile_counts.items())),
            "failure_surface_counts": dict(sorted(failure_counts.items())),
            "semantic_progress_risk_counts": dict(sorted(semantic_counts.items())),
            "write_proposal_rows": sum(int(row.get("write_proposal_rows", 0) or 0) for row in fixtures),
        },
        "fixtures": fixtures,
    }
    return scorecard


def render_markdown(scorecard: dict[str, Any]) -> str:
    summary = scorecard.get("summary", {}) if isinstance(scorecard.get("summary"), dict) else {}
    lines = [
        "# Incoming Fixture Smoke Scorecard",
        "",
        f"Generated: {scorecard.get('generated_at', '')}",
        "",
        "## Batch Summary",
        "",
        f"- Fixtures: `{summary.get('fixture_count', 0)}`",
        f"- Compiled / failed: `{summary.get('compiled_count', 0)}` / `{summary.get('compile_failed_count', 0)}`",
        f"- QA rows: `{summary.get('qa_rows', 0)}`",
        f"- Exact / partial / miss: `{summary.get('exact_rows', 0)}` / `{summary.get('partial_rows', 0)}` / `{summary.get('miss_rows', 0)}`",
        f"- Exact rate: `{summary.get('exact_rate', None)}`",
        f"- Failure surfaces: `{summary.get('failure_surface_counts', {})}`",
        f"- Semantic progress risks: `{summary.get('semantic_progress_risk_counts', {})}`",
        f"- Write proposal rows: `{summary.get('write_proposal_rows', 0)}`",
        "",
        "## Fixture Rows",
        "",
        "| Fixture | Compile | Health | Progress | QA | Exact | Partial | Miss | Failure Surfaces |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in scorecard.get("fixtures", []):
        if not isinstance(row, dict):
            continue
        judge = row.get("judge_counts", {}) if isinstance(row.get("judge_counts"), dict) else {}
        failures = row.get("failure_surface_counts", {}) if isinstance(row.get("failure_surface_counts"), dict) else {}
        lines.append(
            f"| `{row.get('fixture', '')}` | `{_compile_label(row)}` | "
            f"`{row.get('compile_health', '')}` | `{row.get('semantic_progress_risk', '')}` | "
            f"{row.get('qa_rows', 0)} | {judge.get('exact', 0)} | {judge.get('partial', 0)} | "
            f"{judge.get('miss', 0)} | `{failures}` |"
        )
    lines.append("")
    return "\n".join(lines)


def _fixture_row(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    return {
        "fixture": str(report.get("fixture", "")),
        "profile_fallback": str(summary.get("profile_fallback", "")),
        "compile_status": str(summary.get("compile_status", "")),
        "compile_parsed_ok": bool(summary.get("compile_parsed_ok", True)),
        "compile_parse_error": str(summary.get("compile_parse_error", "")),
        "compile_admitted": int(summary.get("compile_admitted", 0) or 0),
        "compile_skipped": int(summary.get("compile_skipped", 0) or 0),
        "compile_health": str(summary.get("compile_health", "")),
        "semantic_progress_risk": str(summary.get("semantic_progress_risk", "")),
        "semantic_progress_action": str(summary.get("semantic_progress_action", "")),
        "qa_rows": int(summary.get("qa_rows", 0) or 0),
        "judge_counts": dict(summary.get("judge_counts", {}) if isinstance(summary.get("judge_counts"), dict) else {}),
        "failure_surface_counts": dict(
            summary.get("failure_surface_counts", {}) if isinstance(summary.get("failure_surface_counts"), dict) else {}
        ),
        "write_proposal_rows": int(summary.get("write_proposal_rows", 0) or 0),
        "non_exact_rows": report.get("non_exact_rows", []) if isinstance(report.get("non_exact_rows"), list) else [],
    }


def _counter_from_dict(value: Any) -> Counter[str]:
    if not isinstance(value, dict):
        return Counter()
    return Counter({str(key): int(count or 0) for key, count in value.items()})


def _compile_label(row: dict[str, Any]) -> str:
    status = str(row.get("compile_status", ""))
    fallback = str(row.get("profile_fallback", ""))
    if fallback:
        return f"{status}; {fallback}"
    return status


def _resolve(path: Path | None) -> Path:
    if path is None:
        return DEFAULT_ROOT
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
