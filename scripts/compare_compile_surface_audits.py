"""Compare compile-surface invariant audits before QA replay.

This gate is meant for direct-surface architecture work. A replay compile can improve
one surface while silently dropping another; this script makes those tradeoffs
visible before spending QA/judge cycles.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STATUS_RANK = {
    "not_applicable": 0,
    "fail": 1,
    "missing_structural_surface": 1,
    "missing_companion": 1,
    "missing_status_companion": 1,
    "ledger_only": 2,
    "candidate_only": 3,
    "partial": 4,
    "companion_only": 4,
    "pass": 5,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-audit", type=Path, required=True)
    parser.add_argument("--candidate-audit", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--min-direct-fact-ratio", type=float, default=0.85)
    parser.add_argument(
        "--max-lost-predicates",
        type=int,
        default=0,
        help="Maximum baseline direct predicates the candidate may drop before the gate fails.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compare_audits(
        _load(args.baseline_audit),
        _load(args.candidate_audit),
        min_direct_fact_ratio=args.min_direct_fact_ratio,
        max_lost_predicates=args.max_lost_predicates,
    )
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


def compare_audits(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    min_direct_fact_ratio: float = 0.85,
    max_lost_predicates: int = 0,
) -> dict[str, Any]:
    baseline_reports = {report["fixture"]: report for report in baseline.get("reports", [])}
    candidate_reports = {report["fixture"]: report for report in candidate.get("reports", [])}
    fixtures = sorted(set(baseline_reports) & set(candidate_reports))
    comparisons = [
        _compare_fixture(
            baseline_reports[fixture],
            candidate_reports[fixture],
            min_direct_fact_ratio=min_direct_fact_ratio,
            max_lost_predicates=max_lost_predicates,
        )
        for fixture in fixtures
    ]
    summary = {
        "fixture_count": len(comparisons),
        "gate_status_counts": _count_by(comparisons, "gate_status"),
        "direct_fact_regression_count": sum(1 for row in comparisons if row["direct_fact_regression"]),
        "family_regression_count": sum(len(row["family_regressions"]) for row in comparisons),
        "contract_regression_count": sum(len(row["contract_regressions"]) for row in comparisons),
        "predicate_loss_count": sum(len(row["lost_predicates"]) for row in comparisons),
        "predicate_loss_regression_count": sum(1 for row in comparisons if row["predicate_loss_regression"]),
    }
    return {
        "schema_version": "compile_surface_audit_comparison_v1",
        "min_direct_fact_ratio": min_direct_fact_ratio,
        "max_lost_predicates": max_lost_predicates,
        "summary": summary,
        "comparisons": comparisons,
    }


def _compare_fixture(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    min_direct_fact_ratio: float,
    max_lost_predicates: int,
) -> dict[str, Any]:
    base_direct = int(baseline.get("direct_fact_count") or 0)
    cand_direct = int(candidate.get("direct_fact_count") or 0)
    direct_ratio = cand_direct / base_direct if base_direct else 1.0
    family_regressions = _status_regressions(
        baseline.get("families", []),
        candidate.get("families", []),
        key_name="family",
    )
    contract_regressions = _status_regressions(
        baseline.get("relation_contracts", []),
        candidate.get("relation_contracts", []),
        key_name="contract",
    )
    base_predicates = set(baseline.get("direct_predicates") or [])
    cand_predicates = set(candidate.get("direct_predicates") or [])
    lost_predicates = sorted(base_predicates - cand_predicates)
    gained_predicates = sorted(cand_predicates - base_predicates)
    direct_fact_regression = direct_ratio < min_direct_fact_ratio
    predicate_loss_regression = len(lost_predicates) > max_lost_predicates
    gate_status = "pass"
    if direct_fact_regression or family_regressions or contract_regressions or predicate_loss_regression:
        gate_status = "regression"
    return {
        "fixture": candidate.get("fixture") or baseline.get("fixture"),
        "baseline_run": baseline.get("run", ""),
        "candidate_run": candidate.get("run", ""),
        "baseline_direct_fact_count": base_direct,
        "candidate_direct_fact_count": cand_direct,
        "direct_fact_ratio": round(direct_ratio, 4),
        "direct_fact_regression": direct_fact_regression,
        "predicate_loss_regression": predicate_loss_regression,
        "family_regressions": family_regressions,
        "contract_regressions": contract_regressions,
        "lost_predicates": lost_predicates,
        "gained_predicates": gained_predicates,
        "gate_status": gate_status,
    }


def _status_regressions(
    baseline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    *,
    key_name: str,
) -> list[dict[str, Any]]:
    baseline = {str(row[key_name]): str(row.get("status", "")) for row in baseline_rows if key_name in row}
    candidate = {str(row[key_name]): str(row.get("status", "")) for row in candidate_rows if key_name in row}
    regressions: list[dict[str, Any]] = []
    for key, base_status in sorted(baseline.items()):
        cand_status = candidate.get(key, "missing")
        if _rank(cand_status) < _rank(base_status):
            regressions.append(
                {
                    key_name: key,
                    "baseline_status": base_status,
                    "candidate_status": cand_status,
                }
            )
    return regressions


def _rank(status: str) -> int:
    return STATUS_RANK.get(status, -1)


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Compile Surface Audit Comparison",
        "",
        f"- Schema: `{payload['schema_version']}`",
        f"- Min direct-fact ratio: `{payload['min_direct_fact_ratio']}`",
        f"- Max lost predicates: `{payload['max_lost_predicates']}`",
        f"- Summary: `{payload['summary']}`",
        "",
        "| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["comparisons"]:
        lines.append(
            "| {fixture} | {gate} | {base} -> {cand} | {ratio} | {families} | {contracts} | {lost} |".format(
                fixture=f"`{row['fixture']}`",
                gate=f"`{row['gate_status']}`",
                base=row["baseline_direct_fact_count"],
                cand=row["candidate_direct_fact_count"],
                ratio=row["direct_fact_ratio"],
                families=len(row["family_regressions"]),
                contracts=len(row["contract_regressions"]),
                lost=len(row["lost_predicates"]),
            )
        )
    lines.extend(["", "## Regressions", ""])
    for row in payload["comparisons"]:
        if row["gate_status"] == "pass":
            continue
        lines.append(f"### `{row['fixture']}`")
        if row["direct_fact_regression"]:
            lines.append(
                f"- Direct fact count regressed: `{row['baseline_direct_fact_count']}` -> `{row['candidate_direct_fact_count']}`."
            )
        if row["predicate_loss_regression"]:
            lines.append(f"- Predicate preservation failed: `{len(row['lost_predicates'])}` lost predicates.")
        for item in row["family_regressions"]:
            lines.append(
                f"- Family `{item['family']}`: `{item['baseline_status']}` -> `{item['candidate_status']}`."
            )
        for item in row["contract_regressions"]:
            lines.append(
                f"- Contract `{item['contract']}`: `{item['baseline_status']}` -> `{item['candidate_status']}`."
            )
        if row["lost_predicates"]:
            shown = ", ".join(f"`{name}`" for name in row["lost_predicates"][:25])
            suffix = "" if len(row["lost_predicates"]) <= 25 else f" ... +{len(row['lost_predicates']) - 25} more"
            lines.append(f"- Lost predicates: {shown}{suffix}.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
