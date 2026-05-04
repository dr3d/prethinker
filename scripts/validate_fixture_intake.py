#!/usr/bin/env python3
"""Validate incoming source-plus-QA fixture folders.

This is an intake gate for newly authored challenge fixtures. It checks file
shape, counts, and obvious oracle-boundary leaks. It does not read source prose
for meaning, infer answers, or score fixture quality.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "datasets" / "incoming_fixtures"
REQUIRED_FILES = ("source.md", "qa.jsonl", "fixture_notes.md")
ANSWERISH_KEYS = {
    "answer",
    "answers",
    "reference_answer",
    "gold_answer",
    "expected_answer",
    "oracle_answer",
}
QUESTION_KEYS = ("question", "utterance", "prompt")


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
        fixture_dirs.extend([path for path in sorted(root.iterdir()) if path.is_dir()] if root.exists() else [])
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
    errors: list[str] = []
    warnings: list[str] = []
    present = {child.name for child in path.iterdir()} if path.exists() and path.is_dir() else set()
    if not path.exists():
        errors.append("fixture_dir_missing")
    elif not path.is_dir():
        errors.append("fixture_path_not_directory")
    for name in REQUIRED_FILES:
        if name not in present:
            errors.append(f"missing_{name}")

    source = _read_text(path / "source.md") if "source.md" in present else ""
    source_word_count = _word_count(source)
    if source and not 900 <= source_word_count <= 1600:
        warnings.append(f"source_word_count_outside_requested_range:{source_word_count}")

    notes_text = _read_text(path / "fixture_notes.md") if "fixture_notes.md" in present else ""
    expected_failure_text = _read_text(path / "expected_failure_modes.md") if "expected_failure_modes.md" in present else ""
    for label, text in (("fixture_notes", notes_text), ("expected_failure_modes", expected_failure_text)):
        if _looks_answer_keyish(text):
            warnings.append(f"{label}_may_contain_answer_key_language")

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
            "required_present": sorted(name for name in REQUIRED_FILES if name in present),
            "optional_present": sorted(name for name in ("expected_failure_modes.md", "answer_key.jsonl", "answer_key.md") if name in present),
        },
        "source": {
            "word_count": source_word_count,
            "requested_range": [900, 1600],
        },
        "qa": {
            "row_count": len(qa_rows),
            "requested_row_count": 40,
            "ids": [str(row.get("id", "")) for row in qa_rows[:5]],
        },
    }


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
