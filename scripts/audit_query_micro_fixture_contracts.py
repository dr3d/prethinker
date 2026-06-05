#!/usr/bin/env python3
"""Audit query micro-fixture manifests and QA packet contracts.

This check is intentionally narrow. It validates only query-fixture control
files and QA packet shape; it does not read source prose, model outputs, run
artifacts, or answer keys beyond counting numbered answers.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.report_freshness import apply_markdown_freshness_check  # noqa: E402


DEFAULT_ROOT = REPO_ROOT / "datasets" / "query_micro_fixtures"
MANIFEST_SCHEMA = "prethinker.query_micro_fixture_manifest.v1"
REQUIRED_ATOM_LIBRARY_FLAG = "--atom-library-query-grounding"
DISPLAY_CARRIER_RE = re.compile(r"^[a-z][a-z0-9_]*/[1-9][0-9]*$")
ANSWERS_HEADING_RE = re.compile(r"^\s*##\s+Answers\s*$", re.IGNORECASE | re.MULTILINE)
NUMBERED_ITEM_RE = re.compile(r"^\s*(\d+)\.\s+(.*\S)\s*$")

SOURCE_DISPLAY_QUESTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("exact_legal_name", re.compile(r"\bexact\s+legal\s+name\b", re.IGNORECASE)),
    ("source_display", re.compile(r"\bsource[-\s]+display\b", re.IGNORECASE)),
    ("display_name", re.compile(r"\bdisplay[-\s]+name\b", re.IGNORECASE)),
    ("exact_source_text", re.compile(r"\bexact\s+(?:source\s+)?text\b", re.IGNORECASE)),
    ("verbatim_source", re.compile(r"\bverbatim\b.*\b(?:source|text|wording|name)\b", re.IGNORECASE)),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--manifest", action="append", default=[], type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--expect-md", type=Path)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifests = args.manifest or _manifest_paths(args.root)
    report = audit_manifests(root=REPO_ROOT, manifests=manifests)
    rendered_md = render_markdown(report)
    if args.expect_md:
        apply_markdown_freshness_check(
            report=report,
            expected_path=args.expect_md,
            rendered_md=rendered_md,
        )
        rendered_md = render_markdown(report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(rendered_md, encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    blocked = report["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not blocked else 1


def audit_manifests(*, root: Path, manifests: list[Path]) -> dict[str, Any]:
    rows = [_audit_manifest(root=root, manifest_path=manifest) for manifest in manifests]
    errors = [error for row in rows for error in row["errors"]]
    warnings = [warning for row in rows for warning in row["warnings"]]
    return {
        "schema": "prethinker.query_micro_fixture_contract_audit.v1",
        "summary": {
            "manifest_count": len(rows),
            "cell_count": sum(row["cell_count"] for row in rows),
            "qa_file_count": sum(row["qa_file_count"] for row in rows),
            "blocking_errors": len(errors),
            "warnings": len(warnings),
            "status": "pass" if not errors else "fail",
        },
        "manifests": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Query Micro-Fixture Contract Audit",
        "",
        "This report validates query micro-fixture manifests and QA packet shape only.",
        "It does not read source prose, model outputs, compile artifacts, or judged QA run artifacts.",
        "Atom-library query packets must keep the planner inside compiled atoms; source-display questions require an explicit typed display carrier declaration.",
        "",
        f"- Manifests: `{summary['manifest_count']}`",
        f"- Cells: `{summary['cell_count']}`",
        f"- QA files: `{summary['qa_file_count']}`",
        f"- Blocking errors: `{summary['blocking_errors']}`",
        f"- Warnings: `{summary['warnings']}`",
        f"- Status: `{summary['status']}`",
        "",
        "| Manifest | Fixture | Cells | QA Files | Errors | Warnings |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in report["manifests"]:
        lines.append(
            "| `{}` | `{}` | {} | {} | `{}` | `{}` |".format(
                row["path"],
                row["fixture_id"],
                row["cell_count"],
                row["qa_file_count"],
                row["errors"],
                row["warnings"],
            )
        )
    return "\n".join(lines) + "\n"


def _manifest_paths(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.rglob("manifest.json"))


def _audit_manifest(*, root: Path, manifest_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    path = manifest_path if manifest_path.is_absolute() else root / manifest_path
    display_carriers: list[str] = []
    fixture_id = ""
    cell_count = 0
    qa_file_count = 0

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return _manifest_row(
            manifest_path=manifest_path,
            fixture_id="",
            cell_count=0,
            qa_file_count=0,
            errors=[f"manifest_unreadable:{exc}"],
            warnings=[],
        )
    except json.JSONDecodeError as exc:
        return _manifest_row(
            manifest_path=manifest_path,
            fixture_id="",
            cell_count=0,
            qa_file_count=0,
            errors=[f"manifest_invalid_json:{exc.msg}"],
            warnings=[],
        )

    if not isinstance(payload, dict):
        errors.append("manifest_not_object")
        payload = {}
    schema = payload.get("schema")
    if schema != MANIFEST_SCHEMA:
        errors.append(f"unexpected_schema:{schema}")
    fixture_id = str(payload.get("fixture_id") or "").strip()
    if not fixture_id:
        errors.append("missing_fixture_id")
    required_flags = _string_list(payload.get("required_runner_flags"))
    if _is_atom_library_manifest(payload) and REQUIRED_ATOM_LIBRARY_FLAG not in required_flags:
        errors.append(f"missing_required_runner_flag:{REQUIRED_ATOM_LIBRARY_FLAG}")
    display_carriers = _typed_display_carriers(payload)
    errors.extend(_typed_display_carrier_errors(display_carriers))

    cells = payload.get("cells")
    if not isinstance(cells, list) or not cells:
        errors.append("missing_cells")
        cells = []
    cell_count = len(cells)
    seen_qa_files: set[str] = set()
    for index, cell in enumerate(cells):
        if not isinstance(cell, dict):
            errors.append(f"cell_{index + 1}:not_object")
            continue
        cell_id = str(cell.get("id") or f"cell_{index + 1}").strip()
        qa_file = str(cell.get("qa_file") or "").strip()
        expected_count = cell.get("question_count")
        if not qa_file:
            errors.append(f"{cell_id}:missing_qa_file")
            continue
        seen_qa_files.add(qa_file)
        qa_path = _resolve_repo_path(root=root, path_text=qa_file)
        errors.extend(
            _audit_qa_packet(
                cell_id=cell_id,
                qa_file=qa_file,
                qa_path=qa_path,
                expected_count=expected_count,
                display_carriers=display_carriers,
            )
        )
    qa_file_count = len(seen_qa_files)
    return _manifest_row(
        manifest_path=manifest_path,
        fixture_id=fixture_id,
        cell_count=cell_count,
        qa_file_count=qa_file_count,
        errors=errors,
        warnings=warnings,
    )


def _manifest_row(
    *,
    manifest_path: Path,
    fixture_id: str,
    cell_count: int,
    qa_file_count: int,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "path": _repo_display_path(manifest_path),
        "fixture_id": fixture_id,
        "cell_count": cell_count,
        "qa_file_count": qa_file_count,
        "errors": errors,
        "warnings": warnings,
    }


def _audit_qa_packet(
    *,
    cell_id: str,
    qa_file: str,
    qa_path: Path,
    expected_count: Any,
    display_carriers: list[str],
) -> list[str]:
    errors: list[str] = []
    if not qa_path.exists():
        return [f"{cell_id}:missing_qa_file:{qa_file}"]
    try:
        text = qa_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{cell_id}:qa_file_unreadable:{qa_file}:{exc}"]
    try:
        questions, answers = _split_qa_packet(text)
    except ValueError as exc:
        return [f"{cell_id}:{qa_file}:{exc}"]
    if not isinstance(expected_count, int):
        errors.append(f"{cell_id}:question_count_not_integer:{expected_count}")
    elif len(questions) != expected_count:
        errors.append(f"{cell_id}:question_count_mismatch:manifest={expected_count}:questions={len(questions)}")
    if len(questions) != len(answers):
        errors.append(f"{cell_id}:question_answer_count_mismatch:questions={len(questions)}:answers={len(answers)}")
    for question in questions:
        for pattern_id, pattern in SOURCE_DISPLAY_QUESTION_PATTERNS:
            if pattern.search(question["text"]) and not display_carriers:
                errors.append(
                    f"{cell_id}:question_{question['number']}:"
                    f"source_display_question_requires_typed_display_carrier:{pattern_id}"
                )
    return errors


def _split_qa_packet(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    match = ANSWERS_HEADING_RE.search(text)
    if not match:
        raise ValueError("missing_answers_heading")
    question_block = text[: match.start()]
    answer_block = text[match.end() :]
    questions = _numbered_items(question_block)
    answers = _numbered_items(answer_block)
    if not questions:
        raise ValueError("no_numbered_questions")
    if not answers:
        raise ValueError("no_numbered_answers")
    return questions, answers


def _numbered_items(block: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        match = NUMBERED_ITEM_RE.match(line)
        if match:
            if current:
                items.append(current)
            current = {"number": int(match.group(1)), "text": match.group(2).strip()}
            continue
        if current and line.strip():
            current["text"] += " " + line.strip()
    if current:
        items.append(current)
    return items


def _is_atom_library_manifest(payload: dict[str, Any]) -> bool:
    values = [
        payload.get("fixture_id"),
        payload.get("purpose"),
        *(payload.get("claim_boundary") if isinstance(payload.get("claim_boundary"), list) else []),
    ]
    return any("atom-library" in str(value).casefold() or "atom library" in str(value).casefold() for value in values)


def _typed_display_carriers(payload: dict[str, Any]) -> list[str]:
    return _string_list(payload.get("typed_display_carriers"))


def _typed_display_carrier_errors(carriers: list[str]) -> list[str]:
    errors: list[str] = []
    for carrier in carriers:
        if not DISPLAY_CARRIER_RE.match(carrier):
            errors.append(f"invalid_typed_display_carrier:{carrier}")
    return errors


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _resolve_repo_path(*, root: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return root / path


def _repo_display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
