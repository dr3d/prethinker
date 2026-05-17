"""Select the best compile candidate from preservation-gate comparisons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison-json", action="append", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = select_candidate([_load(path) for path in args.comparison_json])
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
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["_comparison_path"] = str(path)
    return payload


def select_candidate(comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for payload in comparisons:
        path = payload.get("_comparison_path", "")
        for row in payload.get("comparisons", []):
            candidates.append(_score_candidate(path, row))
    ranked = sorted(candidates, key=lambda row: row["sort_key"])
    selected = ranked[0] if ranked else None
    return {
        "schema_version": "compile_candidate_selection_v1",
        "candidate_count": len(candidates),
        "selected": selected,
        "ranked_candidates": ranked,
    }


def _score_candidate(path: str, row: dict[str, Any]) -> dict[str, Any]:
    gate_penalty = 0 if row.get("gate_status") == "pass" else 1
    family_regressions = len(row.get("family_regressions") or [])
    contract_regressions = len(row.get("contract_regressions") or [])
    direct_ratio = float(row.get("direct_fact_ratio") or 0.0)
    lost_predicates = len(row.get("lost_predicates") or [])
    sort_key = (
        gate_penalty,
        family_regressions + contract_regressions,
        -direct_ratio,
        lost_predicates,
    )
    return {
        "comparison_path": path,
        "fixture": row.get("fixture"),
        "candidate_run": row.get("candidate_run"),
        "gate_status": row.get("gate_status"),
        "direct_fact_ratio": direct_ratio,
        "family_regression_count": family_regressions,
        "contract_regression_count": contract_regressions,
        "lost_predicate_count": lost_predicates,
        "qa_eligible": row.get("gate_status") == "pass",
        "sort_key": list(sort_key),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Compile Candidate Selection",
        "",
        f"- Schema: `{payload['schema_version']}`",
        f"- Candidates: `{payload['candidate_count']}`",
    ]
    selected = payload.get("selected")
    if selected:
        lines.extend(
            [
                f"- Selected: `{selected['candidate_run']}` / `{selected['fixture']}`",
                f"- QA eligible: `{selected['qa_eligible']}`",
                "",
            ]
        )
    lines.extend(
        [
            "| Rank | Fixture | Candidate run | Gate | Ratio | Family regressions | Contract regressions | Lost predicates | QA eligible |",
            "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for index, row in enumerate(payload["ranked_candidates"], start=1):
        lines.append(
            "| {rank} | {fixture} | {run} | {gate} | {ratio} | {families} | {contracts} | {lost} | {eligible} |".format(
                rank=index,
                fixture=f"`{row['fixture']}`",
                run=f"`{row['candidate_run']}`",
                gate=f"`{row['gate_status']}`",
                ratio=row["direct_fact_ratio"],
                families=row["family_regression_count"],
                contracts=row["contract_regression_count"],
                lost=row["lost_predicate_count"],
                eligible=f"`{row['qa_eligible']}`",
            )
        )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
