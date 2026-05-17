"""Compare QA batch outputs for replay promotion decisions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-qa", type=Path, required=True)
    parser.add_argument("--candidate-qa", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compare_qa_runs(_load(args.baseline_qa), _load(args.candidate_qa))
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(payload), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_qa_runs(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_rows = _fixture_summaries(baseline)
    candidate_rows = _fixture_summaries(candidate)
    fixtures = sorted(set(baseline_rows) & set(candidate_rows))
    comparisons = [_compare_fixture(fixture, baseline_rows[fixture], candidate_rows[fixture]) for fixture in fixtures]
    return {
        "schema_version": "qa_run_comparison_v1",
        "summary": {
            "fixture_count": len(comparisons),
            "promotable_count": sum(1 for row in comparisons if row["promotion_status"] == "promotable"),
            "regression_count": sum(1 for row in comparisons if row["promotion_status"] == "regression"),
        },
        "comparisons": comparisons,
    }


def _fixture_summaries(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if isinstance(payload.get("results"), list):
        for result in payload["results"]:
            fixture = result.get("fixture")
            summary = result.get("summary")
            if fixture and isinstance(summary, dict):
                rows[str(fixture)] = summary
    if not rows and isinstance(payload.get("summary"), dict):
        fixture = str(payload.get("fixture") or "single_fixture")
        rows[fixture] = payload["summary"]
    return rows


def _compare_fixture(fixture: str, baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    base_exact = int(baseline.get("judge_exact") or 0)
    base_partial = int(baseline.get("judge_partial") or 0)
    base_miss = int(baseline.get("judge_miss") or 0)
    cand_exact = int(candidate.get("judge_exact") or 0)
    cand_partial = int(candidate.get("judge_partial") or 0)
    cand_miss = int(candidate.get("judge_miss") or 0)
    exact_delta = cand_exact - base_exact
    partial_delta = cand_partial - base_partial
    miss_delta = cand_miss - base_miss
    promotion_status = "promotable" if exact_delta >= 0 and miss_delta <= 0 else "regression"
    return {
        "fixture": fixture,
        "baseline": {"exact": base_exact, "partial": base_partial, "miss": base_miss},
        "candidate": {"exact": cand_exact, "partial": cand_partial, "miss": cand_miss},
        "delta": {"exact": exact_delta, "partial": partial_delta, "miss": miss_delta},
        "promotion_status": promotion_status,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# QA Run Comparison",
        "",
        f"- Schema: `{payload['schema_version']}`",
        f"- Summary: `{payload['summary']}`",
        "",
        "| Fixture | Status | Exact | Partial | Miss | Delta |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["comparisons"]:
        lines.append(
            "| {fixture} | {status} | {exact} | {partial} | {miss} | {delta} |".format(
                fixture=f"`{row['fixture']}`",
                status=f"`{row['promotion_status']}`",
                exact=f"{row['baseline']['exact']} -> {row['candidate']['exact']}",
                partial=f"{row['baseline']['partial']} -> {row['candidate']['partial']}",
                miss=f"{row['baseline']['miss']} -> {row['candidate']['miss']}",
                delta=f"`{row['delta']}`",
            )
        )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
