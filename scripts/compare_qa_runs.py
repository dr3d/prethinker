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
    parser.add_argument(
        "--baseline-artifact-root",
        type=Path,
        default=None,
        help="Optional archive root used to resolve qa_json paths that point at an old tmp tree.",
    )
    parser.add_argument(
        "--candidate-artifact-root",
        type=Path,
        default=None,
        help="Optional archive root used to resolve qa_json paths that point at an old tmp tree.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compare_qa_runs(
        _load(args.baseline_qa),
        _load(args.candidate_qa),
        baseline_artifact_root=args.baseline_artifact_root,
        candidate_artifact_root=args.candidate_artifact_root,
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


def compare_qa_runs(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    baseline_artifact_root: Path | None = None,
    candidate_artifact_root: Path | None = None,
) -> dict[str, Any]:
    baseline_rows = _fixture_summaries(baseline)
    candidate_rows = _fixture_summaries(candidate)
    fixtures = sorted(set(baseline_rows) & set(candidate_rows))
    comparisons = [_compare_fixture(fixture, baseline_rows[fixture], candidate_rows[fixture]) for fixture in fixtures]
    baseline_detail_rows = _fixture_detail_rows(baseline, artifact_root=baseline_artifact_root)
    candidate_detail_rows = _fixture_detail_rows(candidate, artifact_root=candidate_artifact_root)
    row_changes = _compare_detail_rows(baseline_detail_rows, candidate_detail_rows)
    aggregate = _aggregate_comparison(comparisons)
    return {
        "schema_version": "qa_run_comparison_v1",
        "summary": {
            "fixture_count": len(comparisons),
            "promotable_count": sum(1 for row in comparisons if row["promotion_status"] == "promotable"),
            "regression_count": sum(1 for row in comparisons if row["promotion_status"] == "regression"),
            "aggregate_promotion_status": aggregate["promotion_status"],
            "aggregate_delta": aggregate["delta"],
            "row_change_count": row_changes["summary"]["row_change_count"],
            "row_improvement_count": row_changes["summary"]["row_improvement_count"],
            "row_regression_count": row_changes["summary"]["row_regression_count"],
            "baseline_exact_regression_count": row_changes["summary"]["baseline_exact_regression_count"],
            "baseline_exact_to_miss_count": row_changes["summary"]["baseline_exact_to_miss_count"],
        },
        "aggregate": aggregate,
        "comparisons": comparisons,
        "row_changes": row_changes,
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


def _fixture_detail_rows(payload: dict[str, Any], *, artifact_root: Path | None = None) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    if isinstance(payload.get("results"), list):
        for result in payload["results"]:
            fixture = str(result.get("fixture") or "").strip()
            qa_json = str(result.get("qa_json") or "").strip()
            if not fixture or not qa_json:
                continue
            path = _resolve_artifact_path(Path(qa_json), artifact_root=artifact_root)
            if not path.exists():
                continue
            try:
                run_payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            out.update(_rows_from_run_payload(run_payload, fixture=fixture))
    out.update(_rows_from_run_payload(payload, fixture=str(payload.get("fixture") or "single_fixture")))
    return out


def _resolve_artifact_path(path: Path, *, artifact_root: Path | None) -> Path:
    if path.exists() or artifact_root is None:
        return path
    root = artifact_root if artifact_root.is_absolute() else Path.cwd() / artifact_root
    text = str(path)
    parts = path.parts
    if "tmp" in parts:
        index = parts.index("tmp")
        candidate = root.joinpath(*parts[index + 1 :])
        if candidate.exists():
            return candidate
    # Windows summaries may contain old absolute paths while the comparison is
    # running on another platform or from an archive root.
    lowered = text.lower()
    tmp_marker = "\\tmp\\"
    if tmp_marker in lowered:
        rel = text[lowered.index(tmp_marker) + len(tmp_marker) :]
        candidate = root / Path(rel)
        if candidate.exists():
            return candidate
    return path


def _rows_from_run_payload(payload: dict[str, Any], *, fixture: str) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        qid = str(row.get("id") or "").strip()
        if not qid:
            continue
        out[(fixture, qid)] = _row_summary(row, fixture=fixture, qid=qid)
    return out


def _row_summary(row: dict[str, Any], *, fixture: str, qid: str) -> dict[str, Any]:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    failure = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
    query_predicates: set[str] = set()
    helper_predicates: set[str] = set()
    nonempty_predicates: set[str] = set()
    for query_result in row.get("query_results", []) or []:
        if not isinstance(query_result, dict):
            continue
        result = query_result.get("result")
        if not isinstance(result, dict):
            continue
        predicate = str(result.get("predicate") or "").strip()
        if not predicate:
            continue
        query_predicates.add(predicate)
        result_rows = result.get("rows")
        if isinstance(result_rows, list) and result_rows:
            nonempty_predicates.add(predicate)
        if _is_helper_predicate(predicate):
            helper_predicates.add(predicate)
    return {
        "fixture": fixture,
        "id": qid,
        "question": str(row.get("utterance") or ""),
        "reference_answer": str(row.get("reference_answer") or ""),
        "verdict": str(judge.get("verdict") or "unknown"),
        "failure_surface": str(failure.get("surface") or ""),
        "judge_note": str(judge.get("concise_answer") or ""),
        "query_predicates": sorted(query_predicates),
        "nonempty_predicates": sorted(nonempty_predicates),
        "helper_predicates": sorted(helper_predicates),
    }


def _is_helper_predicate(predicate: str) -> bool:
    name = str(predicate or "")
    return (
        name.endswith("_support")
        or name.endswith("_companion")
        or name.endswith("_helper")
        or "_helper_" in name
    )


VERDICT_RANK = {"exact": 3, "partial": 2, "miss": 1, "not_judged": 0, "unknown": 0, "": 0}


def _compare_detail_rows(
    baseline_rows: dict[tuple[str, str], dict[str, Any]],
    candidate_rows: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    for key in sorted(set(baseline_rows) & set(candidate_rows)):
        baseline = baseline_rows[key]
        candidate = candidate_rows[key]
        before = str(baseline.get("verdict") or "unknown")
        after = str(candidate.get("verdict") or "unknown")
        if before == after:
            continue
        baseline_helpers = set(baseline.get("helper_predicates", []) or [])
        candidate_helpers = set(candidate.get("helper_predicates", []) or [])
        changes.append(
            {
                "fixture": key[0],
                "id": key[1],
                "question": candidate.get("question") or baseline.get("question") or "",
                "reference_answer": candidate.get("reference_answer") or baseline.get("reference_answer") or "",
                "baseline_verdict": before,
                "candidate_verdict": after,
                "verdict_delta": _rank(after) - _rank(before),
                "movement": _movement(before, after),
                "baseline_failure_surface": baseline.get("failure_surface", ""),
                "candidate_failure_surface": candidate.get("failure_surface", ""),
                "baseline_helper_predicates": sorted(baseline_helpers),
                "candidate_helper_predicates": sorted(candidate_helpers),
                "added_helper_predicates": sorted(candidate_helpers - baseline_helpers),
                "removed_helper_predicates": sorted(baseline_helpers - candidate_helpers),
                "candidate_nonempty_predicates": candidate.get("nonempty_predicates", []),
                "candidate_judge_note": candidate.get("judge_note", ""),
            }
        )
    summary = {
        "row_count_with_details": len(set(baseline_rows) & set(candidate_rows)),
        "row_change_count": len(changes),
        "row_improvement_count": sum(1 for row in changes if int(row["verdict_delta"]) > 0),
        "row_regression_count": sum(1 for row in changes if int(row["verdict_delta"]) < 0),
        "baseline_exact_regression_count": sum(
            1 for row in changes if row["baseline_verdict"] == "exact" and row["candidate_verdict"] != "exact"
        ),
        "baseline_exact_to_miss_count": sum(
            1 for row in changes if row["baseline_verdict"] == "exact" and row["candidate_verdict"] == "miss"
        ),
        "regression_with_added_helper_count": sum(
            1 for row in changes if int(row["verdict_delta"]) < 0 and row["added_helper_predicates"]
        ),
    }
    return {"summary": summary, "changes": changes}


def _rank(verdict: str) -> int:
    return VERDICT_RANK.get(str(verdict or ""), 0)


def _movement(before: str, after: str) -> str:
    delta = _rank(after) - _rank(before)
    if delta > 0:
        return "improved"
    if delta < 0:
        return "regressed"
    return "changed"


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


def _aggregate_comparison(comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    baseline = {
        "exact": sum(int(row["baseline"]["exact"]) for row in comparisons),
        "partial": sum(int(row["baseline"]["partial"]) for row in comparisons),
        "miss": sum(int(row["baseline"]["miss"]) for row in comparisons),
    }
    candidate = {
        "exact": sum(int(row["candidate"]["exact"]) for row in comparisons),
        "partial": sum(int(row["candidate"]["partial"]) for row in comparisons),
        "miss": sum(int(row["candidate"]["miss"]) for row in comparisons),
    }
    delta = {
        "exact": candidate["exact"] - baseline["exact"],
        "partial": candidate["partial"] - baseline["partial"],
        "miss": candidate["miss"] - baseline["miss"],
    }
    promotion_status = "promotable" if delta["exact"] >= 0 and delta["miss"] <= 0 else "regression"
    return {
        "baseline": baseline,
        "candidate": candidate,
        "delta": delta,
        "promotion_status": promotion_status,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    row_summary = payload.get("row_changes", {}).get("summary", {})
    lines = [
        "# QA Run Comparison",
        "",
        f"- Schema: `{payload['schema_version']}`",
        f"- Summary: `{payload['summary']}`",
        f"- Aggregate: `{payload['aggregate']}`",
        f"- Row churn: `{row_summary}`",
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
    changes = payload.get("row_changes", {}).get("changes", [])
    if changes:
        lines.extend(
            [
                "",
                "## Row Verdict Changes",
                "",
                "| Row | Movement | Verdict | Failure Surface | Added Helpers |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in changes:
            added = ", ".join(f"`{item}`" for item in row.get("added_helper_predicates", [])) or "-"
            lines.append(
                "| `{fixture}` `{qid}` | `{movement}` | `{before}` -> `{after}` | `{base_surface}` -> `{cand_surface}` | {added} |".format(
                    fixture=row.get("fixture", ""),
                    qid=row.get("id", ""),
                    movement=row.get("movement", ""),
                    before=row.get("baseline_verdict", ""),
                    after=row.get("candidate_verdict", ""),
                    base_surface=row.get("baseline_failure_surface", ""),
                    cand_surface=row.get("candidate_failure_surface", ""),
                    added=added,
                )
            )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
