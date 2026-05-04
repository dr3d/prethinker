#!/usr/bin/env python3
"""Stage incoming challenge fixtures into compiler-safe benchmark folders.

The incoming authoring format may include answers inline in qa.jsonl. This
script separates those answers into oracle.jsonl and writes a numbered qa.md
that the QA runner can use without exposing answers to query planning.

Some incoming drops are already answer-isolated as qa.md + oracle.jsonl. Those
are normalized into the same promoted fixture shape without interpreting source
prose or answer content.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "tmp" / "incoming"
DEFAULT_OUT_ROOT = REPO_ROOT / "tmp" / "incoming_staged"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--fixture", action="append", default=[], help="Optional fixture directory name to stage.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    out_root = args.out_root if args.out_root.is_absolute() else REPO_ROOT / args.out_root
    selected = {str(item).strip() for item in args.fixture if str(item).strip()}
    fixture_dirs = [path for path in sorted(root.iterdir()) if path.is_dir()]
    if selected:
        fixture_dirs = [path for path in fixture_dirs if path.name in selected]
    report = stage_fixtures(fixture_dirs=fixture_dirs, out_root=out_root)
    print(json.dumps(report["summary"], sort_keys=True))
    return 0 if report["summary"]["failed_fixture_count"] == 0 else 1


def stage_fixtures(*, fixture_dirs: list[Path], out_root: Path) -> dict[str, Any]:
    out_root.mkdir(parents=True, exist_ok=True)
    fixtures = [stage_fixture(path, out_root=out_root) for path in fixture_dirs]
    manifest = {
        "schema_version": "incoming_fixture_stage_manifest_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Copies source and notes as authored.",
            "Writes qa.md with questions only.",
            "Writes oracle.jsonl with reference answers for after-the-fact scoring.",
            "Does not interpret source prose or answers.",
        ],
        "summary": {
            "fixture_count": len(fixtures),
            "failed_fixture_count": sum(1 for item in fixtures if item.get("status") == "fail"),
            "staged_fixture_count": sum(1 for item in fixtures if item.get("status") == "staged"),
        },
        "fixtures": fixtures,
    }
    (out_root / "stage_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest


def stage_fixture(path: Path, *, out_root: Path) -> dict[str, Any]:
    out_dir = out_root / path.name
    errors: list[str] = []
    source_path = _source_asset(path)
    raw_qa_path = path / "qa.jsonl"
    qa_md_path = path / "qa.md"
    oracle_path = path / "oracle.jsonl"

    if source_path is None:
        errors.append("missing_source.md_or_turns.md")
    raw_authoring = raw_qa_path.exists()
    isolated_authoring = qa_md_path.exists() and oracle_path.exists()
    if not raw_authoring and not isolated_authoring:
        errors.append("missing_qa.jsonl_or_qa.md_plus_oracle.jsonl")
    if errors:
        return {"fixture": path.name, "status": "fail", "errors": errors}

    if raw_authoring:
        rows = _load_raw_qa_rows(raw_qa_path)
        if len(rows) != 40:
            errors.append(f"qa_row_count_expected_40_got_{len(rows)}")
        missing_answers = [
            str(row.get("id", index + 1))
            for index, row in enumerate(rows)
            if not str(row.get("answer", "")).strip()
        ]
        if missing_answers:
            errors.append(f"qa_rows_missing_answer:{','.join(missing_answers[:8])}")
    else:
        rows = _load_isolated_qa_rows(qa_md_path=qa_md_path, oracle_path=oracle_path)
        if not rows:
            errors.append("qa_row_count_expected_positive_got_0")
        missing_answers = [
            str(row.get("source_id") or row.get("id") or index + 1)
            for index, row in enumerate(rows)
            if not str(row.get("answer", "")).strip()
        ]
        if missing_answers:
            errors.append(f"qa_rows_missing_answer:{','.join(missing_answers[:8])}")
    if errors:
        return {"fixture": path.name, "status": "fail", "errors": errors}

    out_dir.mkdir(parents=True, exist_ok=True)
    assert source_path is not None
    shutil.copyfile(source_path, out_dir / "source.md")
    shutil.copyfile(source_path, out_dir / "story.md")
    if source_path.name == "turns.md":
        shutil.copyfile(source_path, out_dir / "turns.md")
    if (path / "fixture_notes.md").exists():
        shutil.copyfile(path / "fixture_notes.md", out_dir / "fixture_notes.md")
    else:
        (out_dir / "fixture_notes.md").write_text(_render_fixture_notes(fixture=path.name), encoding="utf-8")
    if (path / "expected_failure_modes.md").exists():
        shutil.copyfile(path / "expected_failure_modes.md", out_dir / "expected_failure_modes.md")
    if raw_authoring:
        shutil.copyfile(raw_qa_path, out_dir / "qa_authored_with_answers.jsonl")
    else:
        shutil.copyfile(qa_md_path, out_dir / "qa_source.md")
        shutil.copyfile(oracle_path, out_dir / "oracle_authored.jsonl")
    (out_dir / "qa_questions.jsonl").write_text(_render_question_jsonl(rows), encoding="utf-8")
    (out_dir / "oracle.jsonl").write_text(_render_oracle_jsonl(rows), encoding="utf-8")
    (out_dir / "qa_battery.json").write_text(
        json.dumps(_render_qa_battery(rows), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "qa.md").write_text(_render_qa_markdown(fixture=path.name, rows=rows), encoding="utf-8")
    (out_dir / "README.md").write_text(_render_readme(fixture=path.name, qa_rows=len(rows)), encoding="utf-8")
    _write_progress_scaffold(out_dir=out_dir, fixture=path.name, source_path=source_path, qa_rows=len(rows))
    return {
        "fixture": path.name,
        "status": "staged",
        "path": _display_path(out_dir),
        "qa_rows": len(rows),
        "categories": _category_counts(rows),
        "source": _display_path(out_dir / "source.md"),
        "qa_file": _display_path(out_dir / "qa.md"),
        "oracle_jsonl": _display_path(out_dir / "oracle.jsonl"),
    }


def _source_asset(path: Path) -> Path | None:
    for name in ("source.md", "story.md", "turns.md"):
        candidate = path / name
        if candidate.exists():
            return candidate
    return None


def _load_raw_qa_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            item = json.loads(line)
            if isinstance(item, dict):
                rows.append(item)
    return rows


def _load_isolated_qa_rows(*, qa_md_path: Path, oracle_path: Path) -> list[dict[str, Any]]:
    questions = _load_markdown_questions(qa_md_path)
    oracle = _load_oracle_rows(oracle_path)
    rows: list[dict[str, Any]] = []
    for question in questions:
        qid = str(question.get("id", "")).strip()
        answer = oracle.get(qid, {})
        rows.append(
            {
                "id": qid,
                "source_id": str(answer.get("source_id") or qid),
                "category": str(answer.get("category") or answer.get("behavior") or ""),
                "behavior": str(answer.get("behavior") or ""),
                "question": str(question.get("question", "")).strip(),
                "answer": str(answer.get("reference_answer") or answer.get("answer") or "").strip(),
            }
        )
    return rows


def _load_markdown_questions(path: Path) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        qid = ""
        question = ""
        qid_match = re.match(r"^(q\d{1,4})\s*:\s*(.*\S)\s*$", stripped, flags=re.IGNORECASE)
        numbered_match = re.match(r"^(\d+)\.\s+(.*\S)\s*$", stripped)
        if qid_match:
            qid = f"q{int(qid_match.group(1)[1:]):03d}"
            question = qid_match.group(2)
        elif numbered_match:
            qid = f"q{int(numbered_match.group(1)):03d}"
            question = numbered_match.group(2)
        if qid and question:
            questions.append({"id": qid, "question": question.strip()})
    return questions


def _load_oracle_rows(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if isinstance(item, dict) and str(item.get("id", "")).strip():
            qid = str(item.get("id", "")).strip()
            if qid.casefold().startswith("q"):
                try:
                    qid = f"q{int(qid[1:]):03d}"
                except ValueError:
                    pass
            out[qid] = item
    return out


def _render_question_jsonl(rows: list[dict[str, Any]]) -> str:
    out = []
    for index, row in enumerate(rows, start=1):
        out.append(
            json.dumps(
                {
                    "id": f"q{index:03d}",
                    "source_id": str(row.get("source_id") or row.get("id", "")).strip(),
                    "category": str(row.get("category", "")).strip(),
                    "question": str(row.get("question", "")).strip(),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    return "\n".join(out) + "\n"


def _render_oracle_jsonl(rows: list[dict[str, Any]]) -> str:
    out = []
    for index, row in enumerate(rows, start=1):
        out.append(
            json.dumps(
                {
                    "id": f"q{index:03d}",
                    "source_id": str(row.get("source_id") or row.get("id", "")).strip(),
                    "category": str(row.get("category", "")).strip(),
                    "reference_answer": str(row.get("answer", "")).strip(),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    return "\n".join(out) + "\n"


def _render_qa_battery(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"q{index:03d}",
            "source_id": str(row.get("source_id") or row.get("id", "")).strip(),
            "category": str(row.get("category", "")).strip(),
            "behavior": str(row.get("behavior", "")).strip(),
            "question": str(row.get("question", "")).strip(),
            "reference_answer": str(row.get("answer", "")).strip(),
        }
        for index, row in enumerate(rows, start=1)
    ]


def _render_qa_markdown(*, fixture: str, rows: list[dict[str, Any]]) -> str:
    lines = [f"# {fixture} QA", "", "Questions only. Reference answers are isolated in `oracle.jsonl`.", ""]
    for index, row in enumerate(rows, start=1):
        lines.append(f"{index}. {str(row.get('question', '')).strip()}")
    lines.append("")
    return "\n".join(lines)


def _render_readme(*, fixture: str, qa_rows: int) -> str:
    return "\n".join(
        [
            f"# {fixture}",
            "",
            "Promoted incoming challenge fixture.",
            "",
            "- `source.md` is the source document for compilation.",
            "- `story.md` is a source-compatible alias for story-world harnesses.",
            "- `qa.md` contains questions only.",
            f"- `qa_battery.json` contains `{qa_rows}` structured QA rows with reference answers for after-the-fact scoring.",
            "- `qa_questions.jsonl` contains structured question rows without reference answers.",
            "- `oracle.jsonl` contains reference answers for after-the-fact scoring.",
            "- `qa_authored_with_answers.jsonl` or `oracle_authored.jsonl` preserves the original incoming answer-bearing authoring format when present.",
            "- `progress_journal.md` records durable research findings.",
            "- `progress_metrics.jsonl` records append-only run metrics.",
            "",
            "Do not feed `oracle.jsonl`, `qa_battery.json`, `qa_authored_with_answers.jsonl`, or `oracle_authored.jsonl` into source compilation.",
            "",
        ]
    )


def _render_fixture_notes(*, fixture: str) -> str:
    return "\n".join(
        [
            f"# {fixture} Fixture Notes",
            "",
            "No separate fixture notes were supplied in the incoming zip.",
            "This file exists so the promoted fixture has the standard review surface.",
            "",
        ]
    )


def _write_progress_scaffold(*, out_dir: Path, fixture: str, source_path: Path, qa_rows: int) -> None:
    prefix = _run_prefix(fixture)
    journal = out_dir / "progress_journal.md"
    metrics = out_dir / "progress_metrics.jsonl"
    if not journal.exists():
        journal.write_text(
            "\n".join(
                [
                    f"# {_title(fixture)} Progress Journal",
                    "",
                    f"Fixture id: `{fixture}`",
                    "",
                    "This journal records durable research findings for this promoted incoming fixture.",
                    "Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.",
                    "",
                    f"## {prefix}-000 - Fixture Admission",
                    "",
                    "Date: 2026-05-04",
                    "",
                    "Evidence lane: `fixture_admission`",
                    "",
                    f"Source admitted from: `{_display_path(source_path.parent)}`",
                    "",
                    "Files admitted:",
                    "",
                    "- `source.md` / `story.md`",
                    "- `fixture_notes.md`",
                    "- `qa.md`",
                    "- `qa_questions.jsonl`",
                    "- `oracle.jsonl`",
                    "- `qa_battery.json`",
                    "",
                    "Benchmark discipline:",
                    "",
                    "- `source.md`/`story.md` is the only cold compile source.",
                    "- `oracle.jsonl`, `qa_battery.json`, `qa.md`, and `fixture_notes.md` are scoring/review assets, not compile context.",
                    "- No Python source-prose interpretation is allowed.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    if not metrics.exists():
        metrics.write_text(
            json.dumps(
                {
                    "timestamp": "2026-05-04",
                    "run_id": f"{prefix}-000",
                    "evidence_lane": "fixture_admission",
                    "compile_run": False,
                    "qa_rows": qa_rows,
                    "oracle_supplied": True,
                    "starter_profile_supplied": False,
                    "source_path": _display_path(out_dir / "source.md"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )


def _run_prefix(fixture: str) -> str:
    parts = [part for part in str(fixture).replace("-", "_").split("_") if part]
    return "".join(part[0].upper() for part in parts[:4]) or "FX"


def _title(fixture: str) -> str:
    return " ".join(part.capitalize() for part in str(fixture).replace("-", "_").split("_") if part)


def _category_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        category = str(row.get("category", "")).strip() or "uncategorized"
        counts[category] = counts.get(category, 0) + 1
    return counts


def _display_path(value: Path | str) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
