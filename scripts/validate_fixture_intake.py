#!/usr/bin/env python3
"""Validate incoming source-plus-QA fixture folders.

This is an intake gate for newly authored challenge fixtures. It checks file
shape, counts, and obvious oracle-boundary leaks. It does not read source prose
for meaning, infer answers, or score fixture quality.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "datasets" / "incoming_fixtures"
REQUIRED_FILES = ("source.md", "qa.jsonl", "fixture_notes.md")
ISOLATED_AUTHORING_FILES = ("source.md", "qa.md", "oracle.jsonl")
SEALED_STORY_FILES = (
    "README.md",
    "story.md",
    "qa_questions.md",
    "qa_answers_private.jsonl",
    "challenge_strategy.md",
    "anti_leakage_manifest.md",
)
ANSWERISH_KEYS = {
    "answer",
    "answers",
    "reference_answer",
    "gold_answer",
    "expected_answer",
    "oracle_answer",
}
QUESTION_KEYS = ("question", "utterance", "prompt")
SOURCE_WORD_RANGE = (900, 2600)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-dir", action="append", type=Path, default=[])
    parser.add_argument("--root", type=Path, default=None, help="Directory whose immediate children are fixture dirs.")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--allow-answer-key", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture_dirs = [path if path.is_absolute() else REPO_ROOT / path for path in args.fixture_dir]
    if args.root:
        root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
        fixture_dirs.extend(
            [
                path
                for path in sorted(root.iterdir())
                if path.is_dir() or (path.is_file() and path.suffix.casefold() == ".zip")
            ]
            if root.exists()
            else []
        )
    if not fixture_dirs:
        fixture_dirs = [path for path in sorted(DEFAULT_ROOT.iterdir()) if path.is_dir()] if DEFAULT_ROOT.exists() else []
    report = build_report(fixture_dirs=fixture_dirs, allow_answer_key=bool(args.allow_answer_key))
    if args.out_json:
        out = args.out_json if args.out_json.is_absolute() else REPO_ROOT / args.out_json
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote {out}")
    print(render_text(report))
    return 0 if report["summary"]["failed_fixture_count"] == 0 else 1


def build_report(*, fixture_dirs: list[Path], allow_answer_key: bool = False) -> dict[str, Any]:
    fixtures = [validate_fixture_dir(path, allow_answer_key=allow_answer_key) for path in fixture_dirs]
    status_counts = Counter(str(item.get("status", "unknown")) for item in fixtures)
    return {
        "schema_version": "fixture_intake_validation_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Checks fixture file shape, QA row counts, ids, and oracle-boundary hygiene only.",
            "Does not interpret source prose, infer answers, compile, query, or judge.",
        ],
        "summary": {
            "fixture_count": len(fixtures),
            "passed_fixture_count": int(status_counts.get("pass", 0)),
            "warning_fixture_count": int(status_counts.get("warning", 0)),
            "failed_fixture_count": int(status_counts.get("fail", 0)),
            "status_counts": dict(status_counts),
        },
        "fixtures": fixtures,
    }


def validate_fixture_dir(path: Path, *, allow_answer_key: bool = False) -> dict[str, Any]:
    if path.is_file() and path.suffix.casefold() == ".zip":
        with tempfile.TemporaryDirectory(prefix="prethinker_fixture_intake_") as tmp:
            try:
                with zipfile.ZipFile(path) as archive:
                    archive.extractall(tmp)
            except zipfile.BadZipFile:
                return _fixture_error(path, ["zip_read_error:bad_zip_file"])
            payload = _fixture_payload_dir(Path(tmp), fallback_name=path.stem)
            report = validate_fixture_dir(payload, allow_answer_key=allow_answer_key)
            report["fixture"] = path.stem
            report["path"] = _display_path(path)
            report["archive_payload_dir"] = payload.name
            return report

    errors: list[str] = []
    warnings: list[str] = []
    path = _fixture_payload_dir(path, fallback_name=path.name)
    present = {child.name for child in path.iterdir()} if path.exists() and path.is_dir() else set()
    if not path.exists():
        errors.append("fixture_dir_missing")
    elif not path.is_dir():
        errors.append("fixture_path_not_directory")

    sealed_story_shape = {"story.md", "qa_questions.md", "qa_answers_private.jsonl"}.issubset(present)
    isolated_authoring_shape = {"source.md", "qa.md", "oracle.jsonl"}.issubset(present)
    if sealed_story_shape:
        for name in SEALED_STORY_FILES:
            if name not in present:
                errors.append(f"missing_{name}")
    elif isolated_authoring_shape:
        for name in ISOLATED_AUTHORING_FILES:
            if name not in present:
                errors.append(f"missing_{name}")
    else:
        for name in REQUIRED_FILES:
            if name not in present:
                errors.append(f"missing_{name}")

    source_name = "story.md" if sealed_story_shape else "source.md"
    source = _read_text(path / source_name) if source_name in present else ""
    source_word_count = _word_count(source)
    if source and not SOURCE_WORD_RANGE[0] <= source_word_count <= SOURCE_WORD_RANGE[1]:
        warnings.append(f"source_word_count_outside_requested_range:{source_word_count}")

    notes_name = "challenge_strategy.md" if sealed_story_shape else "strategy.md" if isolated_authoring_shape else "fixture_notes.md"
    notes_text = _read_text(path / notes_name) if notes_name in present else ""
    expected_failure_text = _read_text(path / "expected_failure_modes.md") if "expected_failure_modes.md" in present else ""
    for label, text in (("fixture_notes", notes_text), ("expected_failure_modes", expected_failure_text)):
        if _looks_answer_keyish(text):
            warnings.append(f"{label}_may_contain_answer_key_language")

    if sealed_story_shape:
        qa_rows, qa_errors, qa_warnings = _validate_sealed_story_qa(
            questions_path=path / "qa_questions.md",
            answers_path=path / "qa_answers_private.jsonl",
        )
    elif isolated_authoring_shape:
        qa_rows, qa_errors, qa_warnings = _validate_sealed_story_qa(
            questions_path=path / "qa.md",
            answers_path=path / "oracle.jsonl",
        )
    else:
        qa_rows, qa_errors, qa_warnings = _validate_qa_jsonl(path / "qa.jsonl", allow_answer_key=allow_answer_key)
    errors.extend(qa_errors)
    warnings.extend(qa_warnings)

    status = "fail" if errors else "warning" if warnings else "pass"
    return {
        "fixture": path.name,
        "path": _display_path(path),
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "files": {
            "format": "sealed_story_zip_v1"
            if sealed_story_shape
            else "source_qa_md_oracle_jsonl_v1"
            if isolated_authoring_shape
            else "source_qa_jsonl_v1",
            "required_present": sorted(
                name
                for name in (
                    SEALED_STORY_FILES
                    if sealed_story_shape
                    else ISOLATED_AUTHORING_FILES
                    if isolated_authoring_shape
                    else REQUIRED_FILES
                )
                if name in present
            ),
            "optional_present": sorted(
                name
                for name in (
                    "expected_failure_modes.md",
                    "answer_key.jsonl",
                    "answer_key.md",
                    "fixture_notes.md",
                    "strategy.md",
                    "anti_leakage_manifest.md",
                )
                if name in present
            ),
        },
        "source": {
            "word_count": source_word_count,
            "requested_range": list(SOURCE_WORD_RANGE),
        },
        "qa": {
            "row_count": len(qa_rows),
            "requested_row_count": 40,
            "ids": [str(row.get("id", "")) for row in qa_rows[:5]],
        },
    }


def _fixture_error(path: Path, errors: list[str]) -> dict[str, Any]:
    return {
        "fixture": path.stem if path.suffix else path.name,
        "path": _display_path(path),
        "status": "fail",
        "errors": errors,
        "warnings": [],
        "files": {"required_present": [], "optional_present": []},
        "source": {"word_count": 0, "requested_range": list(SOURCE_WORD_RANGE)},
        "qa": {"row_count": 0, "requested_row_count": 40, "ids": []},
    }


def _fixture_payload_dir(path: Path, *, fallback_name: str) -> Path:
    if not path.exists() or not path.is_dir():
        return path
    present = {child.name for child in path.iterdir()}
    if present & (set(REQUIRED_FILES) | set(ISOLATED_AUTHORING_FILES) | set(SEALED_STORY_FILES)):
        return path
    children = [child for child in path.iterdir() if child.is_dir()]
    if len(children) == 1:
        return children[0]
    named = path / fallback_name
    return named if named.exists() and named.is_dir() else path


def _validate_sealed_story_qa(*, questions_path: Path, answers_path: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    questions = _load_markdown_questions(questions_path)
    answers, answer_errors = _load_answer_rows(answers_path)
    errors.extend(answer_errors)
    if len(questions) != 40:
        errors.append(f"qa_row_count_expected_40_got_{len(questions)}")
    if len(answers) != 40:
        errors.append(f"answer_row_count_expected_40_got_{len(answers)}")
    question_ids = [str(row.get("id", "")).strip() for row in questions]
    answer_ids = [str(row.get("id", "")).strip() for row in answers]
    if len(set(question_ids)) != len(question_ids):
        errors.append("qa_duplicate_ids")
    if len(set(answer_ids)) != len(answer_ids):
        errors.append("answer_duplicate_ids")
    if question_ids and answer_ids and set(question_ids) != set(answer_ids):
        errors.append("question_answer_id_mismatch")
    missing_answer = [
        str(row.get("id", "")).strip()
        for row in answers
        if not str(row.get("reference_answer") or row.get("answer") or "").strip()
    ]
    if missing_answer:
        errors.append(f"qa_rows_missing_private_answer:{','.join(missing_answer[:8])}")
    questions_text = _read_text(questions_path)
    if _looks_answer_keyish(questions_text):
        warnings.append("qa_questions_may_contain_answer_key_language")
    return questions, errors, warnings


def _load_markdown_questions(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        qid = ""
        question = ""
        qid_match = re.match(r"^\*{0,2}(q\d{1,4})\s*[:.)-]\*{0,2}\s*(.*\S)\s*$", stripped, flags=re.IGNORECASE)
        numbered_match = re.match(r"^(\d{1,3})[.)]\s+(.*\S)\s*$", stripped)
        if qid_match:
            qid = f"q{int(qid_match.group(1)[1:]):03d}"
            question = qid_match.group(2)
        elif numbered_match:
            qid = f"q{int(numbered_match.group(1)):03d}"
            question = numbered_match.group(2)
        if qid and question:
            rows.append({"id": qid, "question": question.strip()})
    return rows


def _load_answer_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        return rows, errors
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"answer_jsonl_invalid_json_line_{line_number}:{exc.msg}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"answer_jsonl_line_{line_number}_not_object")
            continue
        row = dict(payload)
        qid = str(row.get("id", "")).strip()
        if qid.casefold().startswith("q"):
            try:
                qid = f"q{int(qid[1:]):03d}"
            except ValueError:
                pass
        row["id"] = qid
        rows.append(row)
    return rows, errors


def _validate_qa_jsonl(path: Path, *, allow_answer_key: bool) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows, errors, warnings
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"qa_jsonl_invalid_json_line_{line_number}:{exc.msg}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"qa_jsonl_line_{line_number}_not_object")
            continue
        rows.append(payload)
    if len(rows) != 40:
        errors.append(f"qa_row_count_expected_40_got_{len(rows)}")
    ids = [str(row.get("id", "")).strip() for row in rows]
    if any(not item for item in ids):
        errors.append("qa_rows_missing_id")
    duplicate_ids = sorted(item for item, count in Counter(ids).items() if item and count > 1)
    if duplicate_ids:
        errors.append(f"qa_duplicate_ids:{','.join(duplicate_ids[:8])}")
    for index, row in enumerate(rows, start=1):
        if not any(str(row.get(key, "")).strip() for key in QUESTION_KEYS):
            errors.append(f"qa_row_{index}_missing_question")
            break
        answer_keys = sorted(key for key in row if str(key) in ANSWERISH_KEYS)
        if answer_keys and not allow_answer_key:
            errors.append(f"qa_row_{index}_contains_answer_key:{','.join(answer_keys)}")
            break
    return rows, errors, warnings


def _looks_answer_keyish(text: str) -> bool:
    lowered = str(text or "").casefold()
    return any(token in lowered for token in ("answer key", "correct answer", "reference answer", "gold answer"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _word_count(text: str) -> int:
    return len([part for part in str(text or "").replace("-", " ").split() if part.strip()])


def render_text(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "Fixture intake validation",
        f"fixtures={summary.get('fixture_count', 0)} pass={summary.get('passed_fixture_count', 0)} warning={summary.get('warning_fixture_count', 0)} fail={summary.get('failed_fixture_count', 0)}",
    ]
    for fixture in report.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        bits = [
            str(fixture.get("fixture", "")),
            str(fixture.get("status", "")),
            f"qa={((fixture.get('qa') or {}).get('row_count', 0))}",
            f"words={((fixture.get('source') or {}).get('word_count', 0))}",
        ]
        if fixture.get("errors"):
            bits.append("errors=" + ",".join(str(item) for item in fixture.get("errors", [])[:3]))
        if fixture.get("warnings"):
            bits.append("warnings=" + ",".join(str(item) for item in fixture.get("warnings", [])[:3]))
        lines.append(" | ".join(bits))
    return "\n".join(lines)


def _display_path(value: Path | str) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
