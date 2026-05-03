#!/usr/bin/env python3
"""Summarize cold generalization baseline failure surfaces.

This is a post-run research utility. It reads progress metrics and existing QA
artifacts, but it does not read source stories, rerun query planning, infer
facts from prose, or expose oracle material to any compiler path.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASETS_DIR = REPO_ROOT / "datasets"
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "COLD_BASELINE_FAILURE_ROLLUP.md"
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "cold_baselines" / "failure_rollup.json"

SURFACE_LABELS = {
    "compile_surface_gap": "Compile",
    "query_surface_gap": "Query",
    "hybrid_join_gap": "Hybrid/Reasoning",
    "answer_surface_gap": "Answer",
    "judge_uncertain": "Uncertain",
    "not_applicable": "Exact",
}

SURFACE_ACTIONS = {
    "compile_surface_gap": "Improve lens coverage or acquisition passes; do not tune from one fixture alone.",
    "query_surface_gap": "Improve post-ingestion query support bundles over already admitted rows.",
    "hybrid_join_gap": "Add or exercise deterministic reasoning helpers, joins, set-difference, aggregation, or temporal substrate.",
    "answer_surface_gap": "Tighten answer normalization or judge/verbalization policy without changing ingestion.",
    "judge_uncertain": "Inspect row evidence before choosing a layer to change.",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _latest_lane_run(metrics_path: Path, evidence_lane: str) -> dict[str, Any] | None:
    matches = [
        row
        for row in _read_jsonl(metrics_path)
        if isinstance(row.get("qa"), dict) and str(row.get("evidence_lane", "")) == evidence_lane
    ]
    if not matches:
        return None
    return matches[-1]


def _resolve_repo_path(value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _row_verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    return str(judge.get("verdict", "")).strip() or "unknown"


def _row_surface(row: dict[str, Any]) -> str:
    failure = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
    return str(failure.get("surface", "")).strip() or "unclassified"


def _row_failure(row: dict[str, Any]) -> dict[str, Any]:
    failure = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
    return {
        "id": row.get("id", ""),
        "verdict": _row_verdict(row),
        "surface": _row_surface(row),
        "confidence": failure.get("confidence"),
        "question": row.get("utterance", ""),
        "reference_answer": row.get("reference_answer", ""),
        "suggested_next_action": failure.get("suggested_next_action", ""),
    }


def collect_runs(datasets_dir: Path, evidence_lane: str) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for metrics_path in sorted(datasets_dir.glob("**/progress_metrics.jsonl")):
        run = _latest_lane_run(metrics_path, evidence_lane)
        if not run:
            continue
        fixture_dir = metrics_path.parent
        qa = run.get("qa") if isinstance(run.get("qa"), dict) else {}
        compile_summary = run.get("compile") if isinstance(run.get("compile"), dict) else {}
        artifact = run.get("local_artifacts") if isinstance(run.get("local_artifacts"), dict) else {}
        qa_path = _resolve_repo_path(str(artifact.get("qa_json", "")))
        failures: list[dict[str, Any]] = []
        if qa_path and qa_path.exists():
            qa_record = json.loads(qa_path.read_text(encoding="utf-8-sig"))
            for row in qa_record.get("rows", []) if isinstance(qa_record.get("rows"), list) else []:
                if isinstance(row, dict) and _row_verdict(row) != "exact":
                    failures.append(_row_failure(row))
        runs.append(
            {
                "run_id": run.get("run_id", ""),
                "fixture": fixture_dir.name,
                "fixture_path": str(fixture_dir.relative_to(REPO_ROOT)),
                "timestamp": run.get("timestamp", ""),
                "evidence_lane": run.get("evidence_lane", ""),
                "mode": run.get("mode", ""),
                "model": run.get("model", ""),
                "compile": compile_summary,
                "qa": qa,
                "qa_artifact": str(qa_path.relative_to(REPO_ROOT)) if qa_path and qa_path.exists() else "",
                "failures": failures,
            }
        )
    return runs


def build_rollup(runs: list[dict[str, Any]], evidence_lane: str) -> dict[str, Any]:
    surface_counts: Counter[str] = Counter()
    verdict_counts: Counter[str] = Counter()
    fixture_surface_counts: dict[str, Counter[str]] = {}
    top_non_exact: list[dict[str, Any]] = []
    for run in runs:
        qa = run.get("qa") if isinstance(run.get("qa"), dict) else {}
        verdict_counts["exact"] += int(qa.get("judge_exact", 0) or 0)
        verdict_counts["partial"] += int(qa.get("judge_partial", 0) or 0)
        verdict_counts["miss"] += int(qa.get("judge_miss", 0) or 0)
        fixture_counter: Counter[str] = Counter()
        for failure in run.get("failures", []):
            surface = str(failure.get("surface", "unclassified"))
            surface_counts[surface] += 1
            fixture_counter[surface] += 1
            top_non_exact.append({**failure, "run_id": run.get("run_id"), "fixture": run.get("fixture")})
        fixture_surface_counts[str(run.get("run_id"))] = fixture_counter

    ranked_surfaces = [
        {
            "surface": surface,
            "label": SURFACE_LABELS.get(surface, surface),
            "count": count,
            "general_next_action": SURFACE_ACTIONS.get(surface, "Inspect before changing harness behavior."),
        }
        for surface, count in surface_counts.most_common()
        if surface != "not_applicable"
    ]
    top_non_exact.sort(key=lambda item: (str(item.get("surface", "")), str(item.get("fixture", "")), str(item.get("id", ""))))
    return {
        "schema_version": "cold_baseline_failure_rollup_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evidence_lane": evidence_lane,
        "policy": [
            "Reads progress_metrics.jsonl and QA artifacts only.",
            "Does not read source prose, gold KBs, oracle strategy files, or answer-shaped profile material.",
            "Does not rerun compilation, query planning, judging, or failure classification.",
        ],
        "run_count": len(runs),
        "verdict_counts": dict(verdict_counts),
        "surface_counts": dict(surface_counts),
        "ranked_surfaces": ranked_surfaces,
        "runs": runs,
        "top_non_exact_rows": top_non_exact[:80],
    }


def _pct(num: int, den: int) -> str:
    if den <= 0:
        return "0.000"
    return f"{num / den:.3f}"


def render_markdown(rollup: dict[str, Any]) -> str:
    runs = rollup.get("runs", []) if isinstance(rollup.get("runs"), list) else []
    verdicts = rollup.get("verdict_counts", {}) if isinstance(rollup.get("verdict_counts"), dict) else {}
    surfaces = rollup.get("ranked_surfaces", []) if isinstance(rollup.get("ranked_surfaces"), list) else []
    question_total = sum(int((run.get("qa") or {}).get("questions", 0) or 0) for run in runs if isinstance(run, dict))
    exact = int(verdicts.get("exact", 0) or 0)
    partial = int(verdicts.get("partial", 0) or 0)
    miss = int(verdicts.get("miss", 0) or 0)
    lines = [
        "# Cold Baseline Failure Rollup",
        "",
        f"Generated: {rollup.get('generated_at', '')}",
        "",
        "This report aggregates existing `cold_unseen` QA artifacts. It does not read",
        "source prose, gold KBs, oracle strategies, or answer-shaped profile material.",
        "",
        "## Headline",
        "",
        f"- Runs: `{len(runs)}`",
        f"- Questions: `{question_total}`",
        f"- Exact / partial / miss: `{exact}` / `{partial}` / `{miss}`",
        f"- Exact rate: `{_pct(exact, question_total)}`",
        f"- Exact+partial rate: `{_pct(exact + partial, question_total)}`",
        "",
        "## Run Table",
        "",
        "| Run | Fixture | Qs | Exact | Partial | Miss | Admitted | Skipped | Facts | Rules | Artifact |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for run in runs:
        qa = run.get("qa") if isinstance(run.get("qa"), dict) else {}
        compile_summary = run.get("compile") if isinstance(run.get("compile"), dict) else {}
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{run.get('run_id', '')}`",
                    str(run.get("fixture", "")),
                    str(qa.get("questions", 0)),
                    str(qa.get("judge_exact", 0)),
                    str(qa.get("judge_partial", 0)),
                    str(qa.get("judge_miss", 0)),
                    str(compile_summary.get("admitted_ops", 0)),
                    str(compile_summary.get("skipped_ops", 0)),
                    str(compile_summary.get("unique_facts", 0)),
                    str(compile_summary.get("unique_rules", 0)),
                    f"`{run.get('qa_artifact', '')}`",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Cross-Fixture Failure Surfaces", ""])
    lines.extend(["| Surface | Count | General next action |", "| --- | ---: | --- |"])
    for item in surfaces:
        lines.append(
            f"| {item.get('label', item.get('surface', ''))} | {item.get('count', 0)} | {item.get('general_next_action', '')} |"
        )
    lines.extend(["", "## Fixture Surface Matrix", ""])
    lines.extend(["| Run | Compile | Query | Hybrid/Reasoning | Answer | Uncertain |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
    for run in runs:
        counts = Counter(str(item.get("surface", "unclassified")) for item in run.get("failures", []))
        lines.append(
            f"| `{run.get('run_id', '')}` | {counts.get('compile_surface_gap', 0)} | {counts.get('query_surface_gap', 0)} | {counts.get('hybrid_join_gap', 0)} | {counts.get('answer_surface_gap', 0)} | {counts.get('judge_uncertain', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Current Read",
            "",
            "- Compile gaps dominate the cold set, so the next broad architecture work should",
            "  improve source-surface acquisition and lens coverage rather than only query wording.",
            "- Hybrid/reasoning gaps are the next largest signal and should be attacked with",
            "  deterministic helper substrates, joins, aggregation, and rule-promotion probes.",
            "- Query and answer gaps are real but smaller in this snapshot; they should be",
            "  handled with targeted replay packs after compile/reasoning changes.",
            "",
            "## Non-Exact Row Index",
            "",
            "This is an index for choosing targeted replays. It is not a prompt source.",
            "",
            "| Run | Row | Verdict | Surface | Suggested next action |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in rollup.get("top_non_exact_rows", []):
        action = str(row.get("suggested_next_action", "")).replace("\n", " ").strip()
        if len(action) > 180:
            action = action[:177].rstrip() + "..."
        lines.append(
            f"| `{row.get('run_id', '')}` | `{row.get('id', '')}` | {row.get('verdict', '')} | {row.get('surface', '')} | {action} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets-dir", type=Path, default=DEFAULT_DATASETS_DIR)
    parser.add_argument("--evidence-lane", default="cold_unseen")
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    datasets_dir = args.datasets_dir if args.datasets_dir.is_absolute() else REPO_ROOT / args.datasets_dir
    runs = collect_runs(datasets_dir, str(args.evidence_lane))
    rollup = build_rollup(runs, str(args.evidence_lane))
    out_json = args.out_json if args.out_json.is_absolute() else REPO_ROOT / args.out_json
    out_md = args.out_md if args.out_md.is_absolute() else REPO_ROOT / args.out_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(rollup, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(rollup), encoding="utf-8")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
