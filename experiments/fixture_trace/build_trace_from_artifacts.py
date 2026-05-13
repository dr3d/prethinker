#!/usr/bin/env python3
"""Build an artifact-backed Fixture Trace event log."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_FIXTURE = "black_lantern_maze"
DEFAULT_COMPILE = (
    REPO_ROOT
    / "../prethinker_tmp_archive/tmp_offload_20260504_001651/cold_baselines/black_lantern_maze/"
    / "domain_bootstrap_file_20260503T055307250452Z_story_qwen-qwen3-6-35b-a3b.json"
)
DEFAULT_QA = (
    REPO_ROOT
    / "../prethinker_tmp_archive/tmp_offload_20260504_001651/cold_baselines/black_lantern_maze/"
    / "domain_bootstrap_qa_20260503T060152766469Z_qa_qwen-qwen3-6-35b-a3b.json"
)
DEFAULT_SOURCE = REPO_ROOT / f"datasets/story_worlds/{DEFAULT_FIXTURE}/source.md"
DEFAULT_OUT = HERE / "trace_events.json"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return value


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _display_fixture_name(name: str) -> str:
    return str(name or "").replace("_", " ").title()


def _relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _parse_source_transcript(path: Path) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current_label = ""
    current_lines: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        turn_match = re.match(r"^###\s+Turn\s+(\d+)", stripped, flags=re.IGNORECASE)
        heading_match = re.match(r"^(#{1,3})\s+(.+?)\s*$", stripped)
        label = ""
        if turn_match:
            label = f"Turn {turn_match.group(1)}"
        elif heading_match:
            label = heading_match.group(2)
        if label:
            if current_label and current_lines:
                sections.append({"label": current_label, "text": " ".join(current_lines).strip()})
            current_label = label
            current_lines = []
            continue
        if current_label and stripped:
            current_lines.append(stripped)
    if current_label and current_lines:
        sections.append({"label": current_label, "text": " ".join(current_lines).strip()})
    return sections


def _parse_fixture_title(path: Path, fallback: str) -> str:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", raw_line.strip())
        if match:
            return match.group(1)
    return fallback


def _compact_query_rows(row: dict[str, Any], *, limit: int = 8) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in _as_list(row.get("query_results")):
        if not isinstance(item, dict):
            continue
        result = item.get("result") if isinstance(item.get("result"), dict) else {}
        out.append(
            {
                "query": item.get("query", ""),
                "status": result.get("status", ""),
                "predicate": result.get("predicate", ""),
                "num_rows": result.get("num_rows", 0),
                "rows": _as_list(result.get("rows"))[:4],
            }
        )
        if len(out) >= limit:
            break
    return out


def _phase_table(title: str, columns: list[str], rows: list[list[Any]]) -> dict[str, Any]:
    return {
        "title": title,
        "columns": columns,
        "rows": [[str(cell) for cell in row] for row in rows],
    }


def build_trace(*, compile_path: Path, qa_path: Path, source_path: Path) -> dict[str, Any]:
    qa_artifact_path = qa_path
    compile_run = _load_json(compile_path)
    qa_run = _load_json(qa_artifact_path)
    source_compile = compile_run.get("source_compile") if isinstance(compile_run.get("source_compile"), dict) else {}
    health = source_compile.get("compile_health") if isinstance(source_compile.get("compile_health"), dict) else {}
    qa_summary = qa_run.get("summary") if isinstance(qa_run.get("summary"), dict) else {}
    qa_rows = _as_list(qa_run.get("rows"))
    facts = [str(item) for item in _as_list(source_compile.get("facts"))]
    rules = [str(item) for item in _as_list(source_compile.get("rules"))]
    surface_contribution = _as_list(source_compile.get("surface_contribution"))
    fixture_name = source_path.parent.name
    display_name = _display_fixture_name(fixture_name)
    fixture_title = _parse_fixture_title(source_path, display_name)
    qa_path = source_path.with_name("qa.md")
    oracle_path = source_path.with_name("oracle.jsonl")
    source_transcript = _parse_source_transcript(source_path)
    source_word_count = len(re.findall(r"\S+", source_path.read_text(encoding="utf-8")))

    contribution_rows = []
    lens_plan_rows = []
    for item in surface_contribution:
        if not isinstance(item, dict):
            continue
        pass_index = int(item.get("pass_index", 0) or 0)
        lens_role = "base skeleton" if pass_index == 0 else "selected focused lens"
        focus = item.get("focus", "")
        purpose = item.get("purpose", "")
        lens_plan_rows.append(
            [
                pass_index,
                lens_role,
                item.get("pass_id", ""),
                purpose,
                focus,
                item.get("admitted_count", 0),
                item.get("skipped_count", 0),
            ]
        )
        contribution_rows.append(
            [
                pass_index,
                lens_role,
                item.get("pass_id", ""),
                item.get("focus", ""),
                item.get("admitted_count", 0),
                item.get("skipped_count", 0),
                item.get("unique_contribution_count", 0),
            ]
        )

    verdict_counts: dict[str, int] = {}
    for row in qa_rows:
        if not isinstance(row, dict):
            continue
        verdict = str((row.get("reference_judge") or {}).get("verdict", "unknown"))
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

    questions = []
    for row in qa_rows:
        if not isinstance(row, dict):
            continue
        judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
        verdict = str(judge.get("verdict", "unknown"))
        questions.append(
            {
                "id": row.get("id", ""),
                "question": row.get("utterance", ""),
                "answer": str(row.get("projected_decision") or row.get("model_decision") or "answer"),
                "reference": row.get("reference_answer", ""),
                "verdict": verdict,
                "query_plan": _as_list(row.get("queries")),
                "rows": _compact_query_rows(row),
                "why": str(judge.get("concise_answer") or "Reference judge details are available in the raw QA trace."),
                "raw": {
                    "latency_ms": row.get("latency_ms"),
                    "projected_decision": row.get("projected_decision"),
                    "model_decision": row.get("model_decision"),
                    "evidence_bundle_plan": row.get("evidence_bundle_plan"),
                    "evidence_bundle_plan_query_results": row.get("evidence_bundle_plan_query_results"),
                    "query_results": row.get("query_results"),
                    "reference_judge": judge,
                    "warnings": row.get("warnings", []),
                },
            }
        )

    return {
        "schema_version": "fixture_trace_artifact_v1",
        "fixture": {
            "name": fixture_name,
            "display_name": display_name,
            "title": fixture_title,
            "source_path": _relative_or_absolute(source_path),
            "compile_artifact": _relative_or_absolute(compile_path),
            "qa_artifact": _relative_or_absolute(qa_artifact_path),
            "qa_path": _relative_or_absolute(qa_path),
            "oracle_path": _relative_or_absolute(oracle_path),
            "source_word_count": source_word_count,
            "compile_pass_count": source_compile.get("pass_count", 0),
            "qa_total": len(qa_rows),
            "qa_shown": len(questions),
            "status": "real contrast artifact run",
        },
        "source_turns": source_transcript,
        "phases": [
            {
                "id": "source",
                "title": "Source Packet",
                "summary": f"{len(source_transcript)} transcript sections from the checked-in fixture source.",
                "status": f"{source_word_count} words",
                "decisions": [
                    "This section is copied from the fixture source, not simulated trace text.",
                    "Section order matters because later corrections and operational notes override earlier packet context.",
                ],
                "artifacts": [_relative_or_absolute(source_path)],
            },
            {
                "id": "compile-summary",
                "title": "Compile Run",
                "summary": "Archived domain bootstrap compile artifact.",
                "status": str(source_compile.get("mode", "compile")),
                "decisions": [
                    f"Compiled with model {compile_run.get('model', '')}.",
                    f"Compile health verdict: {health.get('verdict', 'unknown')} / {health.get('recommendation', 'unknown')}.",
                    f"Admitted {source_compile.get('admitted_count', 0)} facts and skipped {source_compile.get('skipped_count', 0)} candidates.",
                ],
                "tables": [
                    _phase_table(
                        "Compile Counts",
                        ["metric", "value"],
                        [
                            ["pass_count", source_compile.get("pass_count", 0)],
                            ["unique_fact_count", source_compile.get("unique_fact_count", 0)],
                            ["unique_rule_count", source_compile.get("unique_rule_count", 0)],
                            ["unique_query_count", source_compile.get("unique_query_count", 0)],
                            ["latency_ms", compile_run.get("latency_ms", "")],
                        ],
                    )
                ],
                "raw": {
                    "compile_artifact": _relative_or_absolute(compile_path),
                    "parsed_ok": compile_run.get("parsed_ok"),
                    "source_compile_summary": {
                        key: source_compile.get(key)
                        for key in (
                            "ok",
                            "mode",
                            "pass_count",
                            "admitted_count",
                            "skipped_count",
                            "unique_fact_count",
                            "unique_rule_count",
                            "unique_query_count",
                        )
                    },
                    "compile_health": health,
                },
            },
            {
                "id": "lens-pass-plan",
                "title": "Lens Pass Plan",
                "summary": "Base skeleton compile followed by selected focused semantic perspectives.",
                "status": f"1 base + {max(0, len(lens_plan_rows) - 1)} focused",
                "decisions": [
                    "The first pass is the broad base lens: source-wide stable facts, roles, thresholds, core events, and corrections.",
                    "The later passes are selected focused perspectives from the intake plan, not a blind run of every possible lens.",
                    "Each focused pass contributes a narrower semantic surface: entities/roles, financial thresholds, corrected timeline, technical measurements, or uncertainty markers.",
                ],
                "tables": [
                    _phase_table(
                        "Lens Passes",
                        ["#", "role", "pass", "purpose", "focus", "admitted", "skipped"],
                        lens_plan_rows,
                    )
                ],
                "raw": {
                    "interpretation": (
                        "Artifact-backed view of source_compile.surface_contribution. "
                        "pass_index=0 is the base skeleton; later pass_index rows are selected focused lenses."
                    ),
                    "surface_contribution": surface_contribution,
                },
            },
            {
                "id": "compile-passes",
                "title": "Compile Surface Contributions",
                "summary": "Per-pass contribution ledger from the compile artifact.",
                "status": f"{len(contribution_rows)} pass rows",
                "decisions": [
                    "These rows are real contribution summaries from `source_compile.surface_contribution`.",
                    "They show why the compile was considered healthy: new unique contribution continued across passes.",
                ],
                "tables": [
                    _phase_table(
                        "Surface Contributions",
                        ["#", "role", "pass", "focus", "admitted", "skipped", "unique"],
                        contribution_rows,
                    )
                ],
                "raw": {"surface_contribution": surface_contribution},
            },
            {
                "id": "package",
                "title": "Package Artifacts",
                "summary": "Admitted facts and package counts from the run.",
                "status": f"{len(facts)} facts",
                "decisions": [
                    "The world excerpt below is from the actual admitted fact list.",
                    "The world excerpt below is intentionally raw: it shows admitted facts without polishing them into prose.",
                ],
                "raw": {
                    "fact_excerpt": facts[:80],
                    "rule_excerpt": rules[:40],
                    "all_fact_count": len(facts),
                    "all_rule_count": len(rules),
                },
            },
            {
                "id": "qa-replay",
                "title": "QA Replay",
                "summary": "QA replay with real query plans, query results, and judge outcomes.",
                "status": f"{qa_summary.get('judge_exact', 0)} / {qa_summary.get('judge_partial', 0)} / {qa_summary.get('judge_miss', 0)}",
                "decisions": [
                    f"QA rows: {qa_summary.get('question_count', len(qa_rows))}.",
                    f"Parsed OK: {qa_summary.get('parsed_ok', 0)}.",
                    f"Runtime load errors: {qa_summary.get('runtime_load_error_count', 0)}.",
                    "All question cards below are artifact-backed, including any partial/miss outcomes.",
                ],
                "tables": [
                    _phase_table(
                        "QA Counts",
                        ["verdict", "count"],
                        sorted(verdict_counts.items()),
                    )
                ],
                "raw": {"qa_artifact": _relative_or_absolute(qa_artifact_path), "summary": qa_summary},
            },
        ],
        "questions": questions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile", type=Path, default=DEFAULT_COMPILE)
    parser.add_argument("--qa", type=Path, default=DEFAULT_QA)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    trace = build_trace(compile_path=args.compile, qa_path=args.qa, source_path=args.source)
    args.out.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
