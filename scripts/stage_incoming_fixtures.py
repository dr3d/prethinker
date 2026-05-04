#!/usr/bin/env python3
"""Stage incoming challenge fixtures into compiler-safe benchmark folders.

The incoming authoring format may include answers inline in qa.jsonl. This
script separates those answers into oracle.jsonl and writes a numbered qa.md
that the QA runner can use without exposing answers to query planning.
"""

from __future__ import annotations

import argparse
import json
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
    for name in ("source.md", "fixture_notes.md", "qa.jsonl"):
        if not (path / name).exists():
            errors.append(f"missing_{name}")
    if errors:
        return {"fixture": path.name, "status": "fail", "errors": errors}

    rows = _load_qa_rows(path / "qa.jsonl")
    if len(rows) != 40:
        errors.append(f"qa_row_count_expected_40_got_{len(rows)}")
    missing_answers = [str(row.get("id", index + 1)) for index, row in enumerate(rows) if not str(row.get("answer", "")).strip()]
    if missing_answers:
        errors.append(f"qa_rows_missing_answer:{','.join(missing_answers[:8])}")
    if errors:
        return {"fixture": path.name, "status": "fail", "errors": errors}

    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path / "source.md", out_dir / "source.md")
    shutil.copyfile(path / "fixture_notes.md", out_dir / "fixture_notes.md")
    if (path / "expected_failure_modes.md").exists():
        shutil.copyfile(path / "expected_failure_modes.md", out_dir / "expected_failure_modes.md")
    shutil.copyfile(path / "qa.jsonl", out_dir / "qa_authored_with_answers.jsonl")
    (out_dir / "qa_questions.jsonl").write_text(_render_question_jsonl(rows), encoding="utf-8")
    (out_dir / "oracle.jsonl").write_text(_render_oracle_jsonl(rows), encoding="utf-8")
    (out_dir / "qa.md").write_text(_render_qa_markdown(fixture=path.name, rows=rows), encoding="utf-8")
    (out_dir / "README.md").write_text(_render_readme(fixture=path.name), encoding="utf-8")
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


def _load_qa_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            item = json.loads(line)
            if isinstance(item, dict):
                rows.append(item)
    return rows


def _render_question_jsonl(rows: list[dict[str, Any]]) -> str:
    out = []
    for index, row in enumerate(rows, start=1):
        out.append(
            json.dumps(
                {
                    "id": f"q{index:03d}",
                    "source_id": str(row.get("id", "")).strip(),
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
                    "source_id": str(row.get("id", "")).strip(),
                    "category": str(row.get("category", "")).strip(),
                    "reference_answer": str(row.get("answer", "")).strip(),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    return "\n".join(out) + "\n"


def _render_qa_markdown(*, fixture: str, rows: list[dict[str, Any]]) -> str:
    lines = [f"# {fixture} QA", "", "Questions only. Reference answers are isolated in `oracle.jsonl`.", ""]
    for index, row in enumerate(rows, start=1):
        lines.append(f"{index}. {str(row.get('question', '')).strip()}")
    lines.append("")
    return "\n".join(lines)


def _render_readme(*, fixture: str) -> str:
    return "\n".join(
        [
            f"# {fixture}",
            "",
            "Staged incoming challenge fixture.",
            "",
            "- `source.md` is the source document for compilation.",
            "- `qa.md` contains questions only.",
            "- `oracle.jsonl` contains reference answers for after-the-fact scoring.",
            "- `qa_authored_with_answers.jsonl` preserves the original incoming authoring format.",
            "",
            "Do not feed `oracle.jsonl` or `qa_authored_with_answers.jsonl` into source compilation.",
            "",
        ]
    )


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
