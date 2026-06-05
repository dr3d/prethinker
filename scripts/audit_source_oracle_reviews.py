#!/usr/bin/env python3
"""Audit retained source-only expected/forbidden oracle review packages.

This lane is for external reviews that author expected and forbidden facts for
draft domain-predicate packs. It validates package structure, independence
metadata, fact predicate/arity shape, per-fixture counts, and source-file
references. It does not read source prose, inspect model outputs, or decide
whether a reviewer's facts are true.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.report_freshness import apply_markdown_freshness_check  # noqa: E402
from scripts.oracle_fact_governance import audit_oracle_fact_clause  # noqa: E402


DEFAULT_REVIEW_ROOT = REPO_ROOT / "datasets" / "source_oracle_reviews"
SIGNATURE_RE = re.compile(r"^([a-z][a-z0-9_]*)/([1-9][0-9]*)$")
FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
PLACEHOLDER_RE = re.compile(r"(?:REPLACE_WITH|TODO|TBD)", re.IGNORECASE)
VALID_STATUSES = {"complete", "blocked"}
OPTIONAL_ROOT_FILES = {"README.md", "review_notes.md"}
ALLOWED_FIXTURE_FILES = {"expected_facts.pl", "forbidden_facts.pl"}


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
    errors = [
        error
        for row in rows
        for error in (row["errors"] + [item for output in row["outputs"] for item in output["errors"]])
    ]
    warnings = [
        warning
        for row in rows
        for warning in (row["warnings"] + [item for output in row["outputs"] for item in output["warnings"]])
    ]
    output_count = sum(len(row["outputs"]) for row in rows)
    return {
        "schema": "prethinker.source_oracle_review_audit.v1",
        "summary": {
            "review_count": len(rows),
            "output_count": output_count,
            "blocking_errors": len(errors),
            "warnings": len(warnings),
            "warning_kind_counts": _warning_kind_counts(warnings),
            "status": "pass" if not errors else "fail",
        },
        "reviews": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Source Oracle Review Audit",
        "",
        "This report validates retained source-only expected/forbidden oracle packages.",
        "It does not read source prose, inspect model outputs, or decide facts.",
        "Expected facts are hard-gated for compact atom shape and registered carrier value domains.",
        "Forbidden facts are negative sentinels; off-domain or prose-shaped sentinel values are warnings, not support.",
        "",
        f"- Reviews: `{summary['review_count']}`",
        f"- Outputs: `{summary['output_count']}`",
        f"- Blocking errors: `{summary['blocking_errors']}`",
        f"- Warnings: `{summary['warnings']}`",
        f"- Status: `{summary['status']}`",
        "",
    ]
    warning_kinds = summary.get("warning_kind_counts") or {}
    if warning_kinds:
        lines.extend(["## Warning Classes", "", "| Warning class | Count |", "| --- | ---: |"])
        for kind, count in warning_kinds.items():
            lines.append(f"| `{kind}` | {count} |")
        lines.append("")
    lines.extend(
        [
            "| Review | Proposal | Predicate | Status | Fixture | Expected | Forbidden | Errors | Warnings |",
            "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in report["reviews"]:
        if not row["outputs"]:
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` |  | 0 | 0 | `{}` | `{}` |".format(
                    row["review_id"],
                    row["proposal_id"],
                    row["predicate"],
                    row["status"],
                    row["errors"],
                    row["warnings"],
                )
            )
            continue
        for output in row["outputs"]:
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` | `{}` | {} | {} | `{}` | `{}` |".format(
                    row["review_id"],
                    row["proposal_id"],
                    row["predicate"],
                    row["status"],
                    output["fixture_id"],
                    output["expected_fact_count"],
                    output["forbidden_fact_count"],
                    output["errors"] + row["errors"],
                    output["warnings"] + row["warnings"],
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
    proposal_id = str(manifest.get("proposal_id") or "").strip()
    predicate = str(manifest.get("predicate") or "").strip()
    status = str(manifest.get("status") or "").strip()
    signature = _parse_signature(predicate)

    if not review_id:
        errors.append("missing_review_id")
    elif review_id != review_dir.name:
        errors.append(f"review_id_folder_mismatch:{review_id}!={review_dir.name}")
    if not proposal_id:
        errors.append("missing_proposal_id")
    if signature is None:
        errors.append("invalid_predicate_signature")
    if status not in VALID_STATUSES:
        errors.append("invalid_status")
    if manifest.get("source_only_review") is not True:
        errors.append("source_only_review_not_true")
    if manifest.get("reviewer_blind_to_model_outputs") is not True:
        errors.append("reviewer_not_declared_blind_to_model_outputs")
    if manifest.get("reviewer_read_model_outputs") is not False:
        errors.append("reviewer_model_output_exposure_not_false")
    if status == "blocked" and not str(manifest.get("blocked_reason") or "").strip():
        errors.append("blocked_review_missing_blocked_reason")

    errors.extend(f"manifest_placeholder:{item}" for item in _placeholder_paths(manifest))
    errors.extend(_unexpected_retained_files(review_dir))

    outputs = _audit_outputs(
        review_dir=review_dir,
        manifest=manifest,
        signature=signature,
        review_status=status,
    )
    total_expected = sum(row["expected_fact_count"] for row in outputs)
    total_forbidden = sum(row["forbidden_fact_count"] for row in outputs)
    if status == "complete" and not outputs:
        errors.append("complete_review_has_no_outputs")
    if status == "complete" and not total_expected and not total_forbidden:
        errors.append("complete_review_has_no_expected_or_forbidden_facts")
    if status == "blocked" and (total_expected or total_forbidden):
        errors.append("blocked_review_contains_facts")

    return {
        "path": _rel(manifest_path),
        "review_id": review_id,
        "proposal_id": proposal_id,
        "proposal_file": str(manifest.get("proposal_file") or "").strip(),
        "predicate": predicate,
        "status": status,
        "source_only_review": manifest.get("source_only_review"),
        "reviewer_blind_to_model_outputs": manifest.get("reviewer_blind_to_model_outputs"),
        "reviewer_read_model_outputs": manifest.get("reviewer_read_model_outputs"),
        "expected_fact_count": total_expected,
        "forbidden_fact_count": total_forbidden,
        "outputs": outputs,
        "errors": errors,
        "warnings": warnings,
    }


def _audit_outputs(
    *,
    review_dir: Path,
    manifest: dict[str, Any],
    signature: tuple[str, int] | None,
    review_status: str,
) -> list[dict[str, Any]]:
    manifest_outputs = manifest.get("outputs")
    outputs = manifest_outputs if isinstance(manifest_outputs, dict) else {}
    fixture_ids = set(outputs)
    for child in review_dir.iterdir() if review_dir.exists() else []:
        if child.is_dir():
            fixture_ids.add(child.name)
    rows: list[dict[str, Any]] = []
    for fixture_id in sorted(fixture_ids):
        fixture_manifest = outputs.get(fixture_id) if isinstance(outputs.get(fixture_id), dict) else {}
        fixture_dir = review_dir / fixture_id
        errors: list[str] = []
        warnings: list[str] = []
        expected_path = fixture_dir / "expected_facts.pl"
        forbidden_path = fixture_dir / "forbidden_facts.pl"
        if not fixture_dir.exists():
            errors.append("missing_fixture_output_dir")
        if review_status == "complete" and not expected_path.exists():
            errors.append("missing_expected_facts.pl")
        if review_status == "complete" and not forbidden_path.exists():
            errors.append("missing_forbidden_facts.pl")
        source_files = _string_list(fixture_manifest.get("source_files"))
        if not source_files:
            errors.append("missing_source_files")
        else:
            errors.extend(_source_file_errors(source_files))
        errors.extend(f"manifest_placeholder:{item}" for item in _placeholder_paths(fixture_manifest))
        expected_facts, expected_errors, expected_warnings = _fact_lines(
            expected_path,
            signature=signature,
            role="expected",
        )
        forbidden_facts, forbidden_errors, forbidden_warnings = _fact_lines(
            forbidden_path,
            signature=signature,
            role="forbidden",
        )
        errors.extend(f"expected_facts.pl:{error}" for error in expected_errors)
        errors.extend(f"forbidden_facts.pl:{error}" for error in forbidden_errors)
        warnings.extend(f"expected_facts.pl:{warning}" for warning in expected_warnings)
        warnings.extend(f"forbidden_facts.pl:{warning}" for warning in forbidden_warnings)
        expected_count = len(expected_facts)
        forbidden_count = len(forbidden_facts)
        manifest_expected = _optional_int(fixture_manifest.get("expected_fact_count"))
        manifest_forbidden = _optional_int(fixture_manifest.get("forbidden_fact_count"))
        if manifest_expected is not None and manifest_expected != expected_count:
            errors.append(f"expected_fact_count_mismatch:{manifest_expected}!={expected_count}")
        if manifest_forbidden is not None and manifest_forbidden != forbidden_count:
            errors.append(f"forbidden_fact_count_mismatch:{manifest_forbidden}!={forbidden_count}")
        rows.append(
            {
                "fixture_id": fixture_id,
                "source_files": source_files,
                "expected_fact_count": expected_count,
                "forbidden_fact_count": forbidden_count,
                "errors": errors,
                "warnings": warnings,
            }
        )
    return rows


def _fact_lines(path: Path, *, signature: tuple[str, int] | None, role: str) -> tuple[list[str], list[str], list[str]]:
    if not path.exists():
        return [], [], []
    facts: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = raw.strip()
        if not text or text.startswith("%"):
            continue
        if PLACEHOLDER_RE.search(text):
            errors.append(f"line_{line_no}:placeholder")
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
        fact_errors, fact_warnings = audit_oracle_fact_clause(
            predicate=name,
            args=args,
            clause=text,
            line_no=line_no,
            role=role,
        )
        errors.extend(fact_errors)
        warnings.extend(fact_warnings)
        facts.append(text)
    return facts, errors, warnings


def _parse_fact(text: str) -> tuple[str, list[str]] | None:
    match = FACT_RE.match(text)
    if not match:
        return None
    return match.group(1), _split_args(match.group(2))


def _split_args(value: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    escape = False
    for char in value:
        if quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char in "([{":
            depth += 1
            current.append(char)
            continue
        if char in ")]}":
            depth = max(0, depth - 1)
            current.append(char)
            continue
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
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


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _unexpected_retained_files(review_dir: Path) -> list[str]:
    if not review_dir.exists():
        return []
    errors: list[str] = []
    for path in review_dir.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(review_dir)
        parts = rel.parts
        if len(parts) == 1:
            if parts[0] not in {"manifest.json", *OPTIONAL_ROOT_FILES}:
                errors.append(f"unexpected_retained_file:{rel.as_posix()}")
            continue
        if len(parts) == 2 and parts[1] in ALLOWED_FIXTURE_FILES:
            continue
        errors.append(f"unexpected_retained_file:{rel.as_posix()}")
    return errors


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


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _warning_kind_counts(warnings: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(_warning_kind(warning) for warning in warnings).items()))


def _warning_kind(warning: str) -> str:
    for token in str(warning).split(":"):
        if token.endswith("_value_domain") or token.endswith("_atom_shape"):
            return token
    return str(warning).split(":", 1)[0] or "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
