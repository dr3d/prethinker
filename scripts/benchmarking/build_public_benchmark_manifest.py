#!/usr/bin/env python3
"""Build a publication-facing manifest for the story-world benchmark corpus.

The manifest reads fixture structure and scored progress rows. It does not read
source prose to infer answers or fixture meaning.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_ROOT = REPO_ROOT / "datasets" / "story_worlds"
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "public_benchmark" / "corpus_manifest.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "public_benchmark" / "corpus_manifest.md"


QUESTION_FILES = (
    "qa_questions.jsonl",
    "qa_battery.jsonl",
    "qa_battery.json",
    "qa_battery_40.json",
    "qa.md",
)

SCORING_FILES = (
    "oracle.jsonl",
    "oracle_authored.jsonl",
    "qa_answers_private.jsonl",
    "qa_authored_with_answers.jsonl",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dataset_root = _resolve(args.dataset_root)
    out_json = _resolve(args.out_json)
    out_md = _resolve(args.out_md)
    fixtures = [_fixture_manifest(path) for path in sorted(dataset_root.iterdir()) if path.is_dir()]
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_root": str(dataset_root),
        "fixture_count": len(fixtures),
        "summary": _summarize(fixtures),
        "fixtures": fixtures,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(_render_markdown(manifest), encoding="utf-8")
    print(json.dumps({"fixtures": len(fixtures), "json": str(out_json), "markdown": str(out_md)}, indent=2))
    return 0


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _fixture_manifest(path: Path) -> dict[str, Any]:
    source_file = _first_existing(path, ("source.md", "story.md"))
    question_file = _first_existing(path, QUESTION_FILES)
    scoring_file = _first_existing(path, SCORING_FILES)
    progress_path = path / "progress_metrics.jsonl"
    progress_rows = _load_jsonl(progress_path) if progress_path.exists() else []
    latest_progress = _latest_progress_summary(progress_rows)
    question_count = _count_questions(question_file) if question_file else 0
    oracle_count = _count_jsonl(path / "oracle.jsonl") if (path / "oracle.jsonl").exists() else 0
    private_answer_count = (
        _count_jsonl(path / "qa_answers_private.jsonl") if (path / "qa_answers_private.jsonl").exists() else 0
    )
    files = {name: (path / name).exists() for name in (
        "README.md",
        "source.md",
        "story.md",
        "qa.md",
        "qa_questions.jsonl",
        "qa_battery.json",
        "qa_battery.jsonl",
        "oracle.jsonl",
        "qa_answers_private.jsonl",
        "anti_leakage_manifest.md",
        "fixture_notes.md",
        "challenge_strategy.md",
        "progress_journal.md",
        "progress_metrics.jsonl",
    )}
    status = _publication_status(
        has_source=source_file is not None,
        has_question_surface=question_file is not None,
        has_scoring=scoring_file is not None,
        progress_rows=len(progress_rows),
    )
    return {
        "fixture": path.name,
        "path": str(path),
        "publication_status": status,
        "source_file": source_file.name if source_file else "",
        "question_file": question_file.name if question_file else "",
        "scoring_file": scoring_file.name if scoring_file else "",
        "question_count": question_count,
        "oracle_count": oracle_count,
        "private_answer_count": private_answer_count,
        "progress_metric_rows": len(progress_rows),
        "latest_progress": latest_progress,
        "files": files,
    }


def _first_existing(root: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        path = root / name
        if path.exists():
            return path
    return None


def _publication_status(
    *,
    has_source: bool,
    has_question_surface: bool,
    has_scoring: bool,
    progress_rows: int,
) -> str:
    if has_source and has_question_surface and has_scoring and progress_rows:
        return "ready_with_scored_history"
    if has_source and has_question_surface and has_scoring:
        return "ready_unscored"
    missing: list[str] = []
    if not has_source:
        missing.append("source")
    if not has_question_surface:
        missing.append("questions")
    if not has_scoring:
        missing.append("scoring_oracle")
    return "needs_" + "_".join(missing) if missing else "needs_review"


def _count_questions(path: Path | None) -> int:
    if path is None or not path.exists():
        return 0
    if path.suffix.lower() == ".jsonl":
        return _count_jsonl(path)
    if path.suffix.lower() == ".json":
        return _count_json_items(path)
    return _count_markdown_questions(path)


def _count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _count_json_items(path: Path) -> int:
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        for key in ("questions", "items", "rows", "cases"):
            items = value.get(key)
            if isinstance(items, list):
                return len(items)
    return 0


def _count_markdown_questions(path: Path) -> int:
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("- ", "* ")) or stripped[:3].lower().startswith("q"):
            count += 1
    return count


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{index}: expected JSON object")
        rows.append(value)
    return rows


def _latest_progress_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    row = rows[-1]
    compile_row = row.get("compile") if isinstance(row.get("compile"), dict) else {}
    qa_key, qa_row = _find_latest_qa_row(row)
    return {
        "run_id": row.get("run_id", row.get("lane", "")),
        "timestamp": row.get("timestamp", row.get("ts", "")),
        "mode": row.get("mode", row.get("evidence_lane", row.get("lane", ""))),
        "qa_scope": qa_key if qa_row else "",
        "qa_exact": qa_row.get("judge_exact", qa_row.get("exact", "")),
        "qa_partial": qa_row.get("judge_partial", qa_row.get("partial", "")),
        "qa_miss": qa_row.get("judge_miss", qa_row.get("miss", "")),
        "qa_exact_rate": qa_row.get("exact_rate", _flat_exact_rate(qa_row)),
        "admitted_ops": compile_row.get("admitted_ops", ""),
        "signature_recall": compile_row.get("signature_recall", ""),
        "signature_precision": compile_row.get("signature_precision", ""),
    }


def _find_latest_qa_row(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    preferred_keys = ("qa_full100", "qa_first40", "qa_first20", "qa_targeted")
    for key in preferred_keys:
        value = row.get(key)
        if isinstance(value, dict) and _has_verdict_counts(value):
            return key, value
    qa_keys = sorted(key for key, value in row.items() if key.startswith("qa_") and isinstance(value, dict))
    for key in qa_keys:
        value = row.get(key)
        if isinstance(value, dict) and _has_verdict_counts(value):
            return key, value
    if _has_verdict_counts(row):
        return "flat", row
    return "", {}


def _has_verdict_counts(row: dict[str, Any]) -> bool:
    return any(key in row for key in ("judge_exact", "exact")) and any(
        key in row for key in ("judge_partial", "partial")
    ) and any(key in row for key in ("judge_miss", "miss"))


def _flat_exact_rate(row: dict[str, Any]) -> float | str:
    try:
        exact = int(row.get("judge_exact", row.get("exact", 0)) or 0)
        partial = int(row.get("judge_partial", row.get("partial", 0)) or 0)
        miss = int(row.get("judge_miss", row.get("miss", 0)) or 0)
    except (TypeError, ValueError):
        return ""
    total = exact + partial + miss
    return round(exact / total, 4) if total else ""


def _summarize(fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    statuses: dict[str, int] = {}
    total_questions = 0
    total_oracle_rows = 0
    scored_fixtures = 0
    for fixture in fixtures:
        status = str(fixture.get("publication_status", ""))
        statuses[status] = statuses.get(status, 0) + 1
        total_questions += int(fixture.get("question_count", 0) or 0)
        total_oracle_rows += int(fixture.get("oracle_count", 0) or 0)
        if int(fixture.get("progress_metric_rows", 0) or 0) > 0:
            scored_fixtures += 1
    return {
        "publication_status_counts": dict(sorted(statuses.items())),
        "total_question_rows": total_questions,
        "total_oracle_rows": total_oracle_rows,
        "scored_fixture_count": scored_fixtures,
    }


def _render_markdown(manifest: dict[str, Any]) -> str:
    summary = manifest.get("summary", {})
    fixtures = manifest.get("fixtures", [])
    lines = [
        "# Public Benchmark Corpus Manifest",
        "",
        f"- Generated UTC: `{manifest.get('generated_utc', '')}`",
        f"- Dataset root: `{manifest.get('dataset_root', '')}`",
        f"- Fixtures: `{manifest.get('fixture_count', 0)}`",
        f"- Total question rows: `{summary.get('total_question_rows', 0)}`",
        f"- Total oracle rows: `{summary.get('total_oracle_rows', 0)}`",
        f"- Scored fixtures: `{summary.get('scored_fixture_count', 0)}`",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in dict(summary.get("publication_status_counts", {})).items():
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(
        [
            "",
            "## Fixtures",
            "",
            "| Fixture | Status | Source | Questions | Oracle Rows | Private Answers | Latest QA | Metric Rows |",
            "| --- | --- | --- | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for fixture in fixtures:
        latest = fixture.get("latest_progress", {}) if isinstance(fixture.get("latest_progress"), dict) else {}
        latest_qa = _format_latest_qa(latest)
        lines.append(
            "| {fixture} | `{status}` | `{source}` | {questions} | {oracle} | {private} | {latest} | {metrics} |".format(
                fixture=str(fixture.get("fixture", "")),
                status=str(fixture.get("publication_status", "")),
                source=str(fixture.get("source_file", "")),
                questions=int(fixture.get("question_count", 0) or 0),
                oracle=int(fixture.get("oracle_count", 0) or 0),
                private=int(fixture.get("private_answer_count", 0) or 0),
                latest=latest_qa,
                metrics=int(fixture.get("progress_metric_rows", 0) or 0),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _format_latest_qa(latest: dict[str, Any]) -> str:
    if not latest:
        return ""
    exact = latest.get("qa_exact", "")
    partial = latest.get("qa_partial", "")
    miss = latest.get("qa_miss", "")
    if exact == "" and partial == "" and miss == "":
        return str(latest.get("run_id", ""))
    return f"`{exact} / {partial} / {miss}`"


if __name__ == "__main__":
    raise SystemExit(main())
