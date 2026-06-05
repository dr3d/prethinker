#!/usr/bin/env python3
"""Audit retained independent candidate-oracle review packages.

This check validates review package structure only. It does not read source
prose, inspect model outputs, decide expected facts, or judge whether a
reviewer's source-only calls are true. Its job is to make sure candidate review
folders keep the independence metadata and predicate-shape discipline required
before downstream proposal-evidence summaries consume them.
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

DEFAULT_REVIEW_ROOT = REPO_ROOT / "datasets" / "candidate_oracle_reviews"
SIGNATURE_RE = re.compile(r"^([a-z][a-z0-9_]*)/([1-9][0-9]*)$")
FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
PLACEHOLDER_RE = re.compile(r"(?:REPLACE_WITH|TODO|TBD)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-root", type=Path, default=DEFAULT_REVIEW_ROOT)
    parser.add_argument("--review", action="append", default=[], type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--expect-md", type=Path)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(_review_paths(root=args.review_root, explicit=args.review))
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


def build_report(review_paths: list[Path]) -> dict[str, Any]:
    rows = [_audit_review(path) for path in review_paths]
    errors = [error for row in rows for error in row["errors"]]
    warnings = [warning for row in rows for warning in row["warnings"]]
    return {
        "schema": "prethinker.candidate_oracle_review_audit.v1",
        "summary": {
            "review_count": len(rows),
            "blocking_errors": len(errors),
            "warnings": len(warnings),
            "status": "pass" if not errors else "fail",
        },
        "reviews": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Candidate Oracle Review Audit",
        "",
        "This report validates retained candidate-review package structure only.",
        "It does not read source prose, inspect model outputs, or decide facts.",
        "It verifies review folder identity and repo-relative source-file references without opening those sources.",
        "",
        f"- Reviews: `{summary['review_count']}`",
        f"- Blocking errors: `{summary['blocking_errors']}`",
        f"- Warnings: `{summary['warnings']}`",
        f"- Status: `{summary['status']}`",
        "",
        "| Review | Fixture | Predicate | Expected | Forbidden | Blind | Read Forbidden Inputs | Errors | Warnings |",
        "| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
    ]
    for row in report["reviews"]:
        lines.append(
            "| `{}` | `{}` | `{}` | {} | {} | `{}` | `{}` | `{}` | `{}` |".format(
                row["review_id"],
                row["fixture_id"],
                row["predicate"],
                row["expected_fact_count"],
                row["forbidden_fact_count"],
                row["reviewer_blind_to_model_outputs"],
                row["reviewer_read_forbidden_inputs"],
                row["errors"],
                row["warnings"],
            )
        )
    return "\n".join(lines) + "\n"


def _audit_review(path: Path) -> dict[str, Any]:
    manifest_path = path / "manifest.json" if path.is_dir() else path
    review_dir = manifest_path.parent
    errors: list[str] = []
    warnings: list[str] = []
    manifest = _load_json(manifest_path)
    if not manifest:
        errors.append("missing_or_invalid_manifest")

    review_id = str(manifest.get("review_id") or review_dir.name).strip()
    fixture_id = str(manifest.get("fixture_id") or "").strip()
    predicate = str(manifest.get("predicate") or "").strip()
    signature = _parse_signature(predicate)
    if not review_id:
        errors.append("missing_review_id")
    elif review_id != review_dir.name:
        errors.append(f"review_id_folder_mismatch:{review_id}!={review_dir.name}")
    if not fixture_id:
        errors.append("missing_fixture_id")
    if signature is None:
        errors.append("invalid_predicate_signature")
    if manifest.get("reviewer_blind_to_model_outputs") is not True:
        errors.append("reviewer_not_declared_blind_to_model_outputs")
    if manifest.get("reviewer_read_forbidden_inputs") is not False:
        errors.append("reviewer_forbidden_input_exposure_not_false")
    source_files = _string_list(manifest.get("source_files"))
    if not source_files:
        errors.append("missing_source_files")
    else:
        errors.extend(_source_file_errors(source_files))
    placeholder_paths = _placeholder_paths(manifest)
    errors.extend(f"manifest_placeholder:{path}" for path in placeholder_paths)

    expected_path = review_dir / "candidate_expected_facts.pl"
    forbidden_path = review_dir / "candidate_forbidden_facts.pl"
    if not expected_path.exists():
        errors.append("missing_candidate_expected_facts.pl")
    if not forbidden_path.exists():
        errors.append("missing_candidate_forbidden_facts.pl")
    if not (review_dir / "README.md").exists():
        warnings.append("missing_README.md")

    expected_facts, expected_errors = _fact_lines(expected_path, signature=signature)
    forbidden_facts, forbidden_errors = _fact_lines(forbidden_path, signature=signature)
    errors.extend(f"candidate_expected_facts.pl:{error}" for error in expected_errors)
    errors.extend(f"candidate_forbidden_facts.pl:{error}" for error in forbidden_errors)
    if not expected_facts and not forbidden_facts:
        errors.append("review_has_no_expected_or_forbidden_facts")

    return {
        "path": _rel(manifest_path),
        "review_id": review_id,
        "fixture_id": fixture_id,
        "predicate": predicate,
        "reviewer_blind_to_model_outputs": manifest.get("reviewer_blind_to_model_outputs"),
        "reviewer_read_forbidden_inputs": manifest.get("reviewer_read_forbidden_inputs"),
        "expected_fact_count": len(expected_facts),
        "forbidden_fact_count": len(forbidden_facts),
        "errors": errors,
        "warnings": warnings,
    }


def _fact_lines(path: Path, *, signature: tuple[str, int] | None) -> tuple[list[str], list[str]]:
    if not path.exists():
        return [], []
    facts: list[str] = []
    errors: list[str] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = raw.strip()
        if not text or text.startswith("%"):
            continue
        if not text.endswith(".") or "(" not in text:
            errors.append(f"line_{line_no}:not_fact_clause")
            continue
        parsed = _parse_fact(text)
        if parsed is None:
            errors.append(f"line_{line_no}:invalid_fact_clause")
            continue
        name, args = parsed
        if signature is not None:
            sig_name, sig_arity = signature
            if name != sig_name:
                errors.append(f"line_{line_no}:predicate_mismatch:{name}")
            if len(args) != sig_arity:
                errors.append(f"line_{line_no}:arity_mismatch:{len(args)}")
        facts.append(text)
    return facts, errors


def _parse_fact(text: str) -> tuple[str, list[str]] | None:
    match = FACT_RE.match(text)
    if not match:
        return None
    name = match.group(1)
    args_text = match.group(2)
    return name, _split_args(args_text)


def _split_args(value: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote = False
    depth = 0
    index = 0
    while index < len(value):
        char = value[index]
        if char == "'":
            quote = not quote
            current.append(char)
        elif not quote and char in "([":
            depth += 1
            current.append(char)
        elif not quote and char in ")]":
            depth = max(0, depth - 1)
            current.append(char)
        elif not quote and depth == 0 and char == ",":
            args.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    tail = "".join(current).strip()
    if tail or value.strip():
        args.append(tail)
    return args


def _parse_signature(value: str) -> tuple[str, int] | None:
    match = SIGNATURE_RE.match(value)
    if not match:
        return None
    return match.group(1), int(match.group(2))


def _review_paths(*, root: Path, explicit: list[Path]) -> list[Path]:
    paths = [path.resolve() for path in explicit]
    root_path = root.resolve()
    if root_path.exists():
        paths.extend(sorted(root_path.rglob("manifest.json")))
    unique: dict[str, Path] = {}
    for path in paths:
        manifest = path / "manifest.json" if path.is_dir() else path
        unique[str(manifest.resolve())] = manifest.resolve()
    return list(unique.values())


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _source_file_errors(source_files: list[str]) -> list[str]:
    errors: list[str] = []
    for value in source_files:
        normalized = value.replace("\\", "/").strip()
        path = Path(normalized)
        if path.is_absolute():
            errors.append(f"source_file_not_repo_relative:{normalized}")
            continue
        if ".." in path.parts:
            errors.append(f"source_file_path_traversal:{normalized}")
            continue
        if not normalized.startswith("datasets/"):
            errors.append(f"source_file_not_under_datasets:{normalized}")
            continue
        if not (REPO_ROOT / path).exists():
            errors.append(f"source_file_missing:{normalized}")
    return errors


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _placeholder_paths(value: Any, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            hits.extend(_placeholder_paths(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(_placeholder_paths(item, f"{prefix}[{index}]"))
    elif isinstance(value, str) and PLACEHOLDER_RE.search(value):
        hits.append(prefix or "<root>")
    return hits


if __name__ == "__main__":
    raise SystemExit(main())
