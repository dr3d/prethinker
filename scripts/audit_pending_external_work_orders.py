#!/usr/bin/env python3
"""Audit pending external oracle work-order packets.

This check inspects proposal-declared work-order zip packages without reading
source prose. It lists zip entries only and verifies that each pending packet
has enough structure for an offsite/source-only reviewer to do the work.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.report_freshness import apply_markdown_freshness_check  # noqa: E402

DEFAULT_PROPOSAL_ROOT = REPO_ROOT / "datasets" / "domain_predicate_proposals"
DEFAULT_TMP_ROOT = REPO_ROOT / "tmp"

ANSWER_FACT_BASENAMES = {
    "expected_facts.pl",
    "forbidden_facts.pl",
    "candidate_expected_facts.pl",
    "candidate_forbidden_facts.pl",
}
RUN_ARTIFACT_BASENAMES = {
    "current_judged_qa_manifest.json",
    "judged_qa_manifest.json",
    "qa_manifest.json",
    "score_manifest.json",
}
RUN_ARTIFACT_PATH_PARTS = {
    "compile_artifacts",
    "compile_outputs",
    "current_judged_qa",
    "judged_qa",
    "model_outputs",
    "oracle_reviews",
    "prior_runs",
    "run_artifacts",
    "scored_runs",
    "source_oracle_reviews",
    "candidate_oracle_reviews",
}
TEMPLATE_LITERAL_ALLOWLIST = {
    "full_source_sentence_blob",
}
FACT_LIKE_RE = re.compile(r"^\s*%?\s*(?:[\w -]+:\s*)?([a-z][a-z0-9_]*)\(([^)]*)\)\.?\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal-root", type=Path, default=DEFAULT_PROPOSAL_ROOT)
    parser.add_argument("--proposal", action="append", default=[], type=Path)
    parser.add_argument("--tmp-root", type=Path, default=DEFAULT_TMP_ROOT)
    parser.add_argument(
        "--include-tmp-zips",
        action="store_true",
        help="Also inventory standalone tmp/*.zip work-order packets not declared by proposals.",
    )
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument(
        "--expect-md",
        type=Path,
        help="Fail if this markdown file differs from the freshly rendered report.",
    )
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        _proposal_paths(root=args.proposal_root, explicit=args.proposal),
        tmp_root=args.tmp_root,
        include_tmp_zips=args.include_tmp_zips,
    )
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


def build_report(
    proposal_paths: list[Path],
    *,
    tmp_root: Path | None = None,
    include_tmp_zips: bool = False,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    declared_paths: set[Path] = set()
    for path in proposal_paths:
        payload = _load_json(path)
        for index, item in enumerate(_pending_work_orders(payload)):
            row = _audit_work_order(proposal_path=path, proposal=payload, item=item, index=index)
            rows.append(row)
            if row["resolved_path"]:
                declared_paths.add(Path(row["resolved_path"]).resolve())
    if include_tmp_zips and tmp_root:
        for zip_path in sorted(tmp_root.glob("*.zip")):
            if zip_path.resolve() in declared_paths:
                continue
            rows.append(_audit_standalone_zip(zip_path=zip_path))
    blocking_errors = [error for row in rows for error in row["errors"]]
    warnings = [warning for row in rows for warning in row["warnings"]]
    return {
        "schema": "prethinker.pending_external_work_order_audit.v1",
        "summary": {
            "proposal_count": len(proposal_paths),
            "work_order_count": len(rows),
            "standalone_work_order_count": sum(1 for row in rows if row.get("source") == "tmp_zip"),
            "blocking_errors": len(blocking_errors),
            "warnings": len(warnings),
            "status": "pass" if not blocking_errors else "fail",
        },
        "work_orders": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    scope = (
        "proposal-declared and standalone tmp work-order zip structure"
        if summary.get("standalone_work_order_count")
        else "proposal-declared work-order zip structure"
    )
    lines = [
        "# Pending External Work Order Audit",
        "",
        f"This report validates {scope} plus entry-name and template-content leak policy only.",
        "It blocks pending packets that include filled oracle files, judged-QA manifests, model outputs, compile/run artifacts, or literal fact examples inside oracle templates.",
        "It may read packet-control/template files, but it does not read source prose or decide expected/forbidden facts.",
        "",
        f"- Proposals scanned: `{summary['proposal_count']}`",
        f"- Pending work orders: `{summary['work_order_count']}`",
        f"- Standalone tmp work orders: `{summary['standalone_work_order_count']}`",
        f"- Blocking errors: `{summary['blocking_errors']}`",
        f"- Warnings: `{summary['warnings']}`",
        f"- Status: `{summary['status']}`",
        "",
        "| Source | Proposal | Kind | Path | Fixtures | Entries | Errors | Warnings |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in report["work_orders"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | {} | `{}` | `{}` |".format(
                row["source"],
                row["proposal_id"],
                row["kind"],
                row["path"],
                ", ".join(row["fixtures"]),
                row["entry_count"],
                row["errors"],
                row["warnings"],
            )
        )
    return "\n".join(lines) + "\n"


def _audit_work_order(
    *,
    proposal_path: Path,
    proposal: dict[str, Any],
    item: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    proposal_id = str(proposal.get("proposal_id") or proposal_path.stem).strip()
    kind = str(item.get("kind") or "").strip()
    path_text = str(item.get("path") or "").strip()
    fixtures = _string_list(item.get("fixtures"))
    resolved = _resolve_path(path_text)
    entries: list[str] = []

    if not kind:
        errors.append(f"work_order_{index + 1}:missing_kind")
    if not path_text:
        errors.append(f"work_order_{index + 1}:missing_path")
    elif not resolved.exists():
        errors.append(f"missing_zip:{path_text}")
    elif not zipfile.is_zipfile(resolved):
        errors.append(f"not_zip:{path_text}")
    else:
        with zipfile.ZipFile(resolved) as archive:
            archive_entries = [info for info in archive.infolist() if info.filename.strip()]
            raw_entries = [info.filename for info in archive_entries]
            _validate_template_content_no_answer_examples(
                archive=archive,
                archive_entries=archive_entries,
                errors=errors,
            )
        errors.extend(_zip_entry_name_errors(raw_entries))
        entries = sorted(_normalize_entry(name) for name in raw_entries)
        _validate_no_answer_leakage(entries=entries, errors=errors, warnings=warnings)
        _validate_entries(
            entries=entries,
            proposal_id=proposal_id,
            kind=kind,
            fixtures=fixtures,
            errors=errors,
            warnings=warnings,
        )

    return {
        "proposal_path": str(proposal_path),
        "source": "proposal",
        "proposal_id": proposal_id,
        "kind": kind,
        "path": path_text,
        "resolved_path": str(resolved) if path_text else "",
        "fixtures": fixtures,
        "entry_count": len(entries),
        "errors": errors,
        "warnings": warnings,
    }


def _audit_standalone_zip(*, zip_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    entries: list[str] = []
    if not zipfile.is_zipfile(zip_path):
        errors.append(f"not_zip:{zip_path}")
    else:
        with zipfile.ZipFile(zip_path) as archive:
            archive_entries = [info for info in archive.infolist() if info.filename.strip()]
            raw_entries = [info.filename for info in archive_entries]
            _validate_template_content_no_answer_examples(
                archive=archive,
                archive_entries=archive_entries,
                errors=errors,
            )
        errors.extend(_zip_entry_name_errors(raw_entries))
        entries = sorted(_normalize_entry(name) for name in raw_entries)
        _validate_no_answer_leakage(entries=entries, errors=errors, warnings=warnings)
        _validate_standalone_entries(entries=entries, errors=errors, warnings=warnings)
    return {
        "proposal_path": "",
        "source": "tmp_zip",
        "proposal_id": zip_path.stem,
        "kind": "standalone_external_work_order",
        "path": _display_path(zip_path),
        "resolved_path": str(zip_path.resolve()),
        "fixtures": _fixture_dirs(entries),
        "entry_count": len(entries),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_entries(
    *,
    entries: list[str],
    proposal_id: str,
    kind: str,
    fixtures: list[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    entry_set = set(entries)
    basenames = {Path(entry).name for entry in entries}
    if not entries:
        errors.append("zip_has_no_entries")
    if kind == "source_only_expected_forbidden_oracle" and "WORK_ORDER.md" not in basenames:
        errors.append("missing_WORK_ORDER.md")
    elif "WORK_ORDER.md" not in basenames and "README.md" not in basenames:
        errors.append("missing_work_order_or_readme")
    if not any(_is_expected_template(entry) for entry in entries):
        errors.append("missing_expected_facts_template")
    if not any(_is_forbidden_template(entry) for entry in entries):
        errors.append("missing_forbidden_facts_template")
    if kind == "source_only_expected_forbidden_oracle" and not any("manifest" in entry.lower() for entry in entries):
        errors.append("missing_manifest_template")
    proposal_file = f"{proposal_id}.json"
    if proposal_file not in basenames:
        errors.append(f"missing_proposal_json:{proposal_file}")
    if not fixtures:
        warnings.append("no_declared_fixtures")
    for fixture in fixtures:
        fixture_entries = _fixture_entries(entry_set, fixture)
        if kind == "source_only_candidate_oracle_review":
            if "source.md" not in fixture_entries:
                errors.append(f"{fixture}:missing_source.md")
            if "manifest.json" not in fixture_entries:
                errors.append(f"{fixture}:missing_manifest.json")
        else:
            if "source.md" not in fixture_entries:
                errors.append(f"{fixture}:missing_source.md")
            if "metadata.json" not in fixture_entries:
                errors.append(f"{fixture}:missing_metadata.json")
            if "provenance.md" not in fixture_entries:
                errors.append(f"{fixture}:missing_provenance.md")
            if "fixture_notes.md" not in fixture_entries:
                warnings.append(f"{fixture}:missing_fixture_notes.md")


def _validate_standalone_entries(
    *,
    entries: list[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    basenames = {Path(entry).name for entry in entries}
    if not entries:
        errors.append("zip_has_no_entries")
    if "WORK_ORDER.md" not in basenames and "README.md" not in basenames:
        errors.append("missing_work_order_or_readme")
    if not any(_is_expected_template(entry) for entry in entries):
        errors.append("missing_expected_facts_template")
    if not any(_is_forbidden_template(entry) for entry in entries):
        errors.append("missing_forbidden_facts_template")
    if not any(Path(entry).name == "source.md" for entry in entries):
        errors.append("missing_source.md")
    if not any(Path(entry).name in {"metadata.json", "manifest.json", "current_judged_qa_manifest.json", "ontology_registry.json"} for entry in entries):
        warnings.append("no_metadata_or_registry_file")
    if not any(Path(entry).name in {"provenance.md", "README.md", "WORK_ORDER.md"} for entry in entries):
        warnings.append("no_provenance_or_instruction_file")


def _is_expected_template(entry: str) -> bool:
    name = Path(entry).name.lower()
    return bool(re.match(r"(candidate_)?expected_facts(_template)?\.pl$", name)) and _is_output_template(entry)


def _is_forbidden_template(entry: str) -> bool:
    name = Path(entry).name.lower()
    return bool(re.match(r"(candidate_)?forbidden_facts(_template)?\.pl$", name)) and _is_output_template(entry)


def _validate_no_answer_leakage(
    *,
    entries: list[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    for entry in entries:
        normalized = _normalize_entry(entry)
        lower_entry = normalized.lower()
        name = Path(normalized).name.lower()
        path_parts = {part.lower() for part in PurePosixPath(lower_entry).parts}
        if name in ANSWER_FACT_BASENAMES and not _is_output_template(normalized):
            errors.append(f"answer_oracle_file_not_template:{normalized}")
        if name in RUN_ARTIFACT_BASENAMES:
            errors.append(f"run_artifact_file_not_allowed:{normalized}")
        leaking_parts = sorted(path_parts & RUN_ARTIFACT_PATH_PARTS)
        for part in leaking_parts:
            errors.append(f"run_artifact_path_not_allowed:{part}:{normalized}")
        if name in {"model_output.json", "llm_output.json", "compile.json", "compile_output.json"}:
            errors.append(f"model_or_compile_output_not_allowed:{normalized}")
        if name == "candidate_fact.pl":
            warnings.append(f"candidate_fact_focus_review_not_full_blind:{normalized}")


def _validate_template_content_no_answer_examples(
    *,
    archive: zipfile.ZipFile,
    archive_entries: list[zipfile.ZipInfo],
    errors: list[str],
) -> None:
    for archive_entry in archive_entries:
        entry = _normalize_entry(archive_entry.filename)
        if not _is_fact_template_file(entry):
            continue
        try:
            text = archive.read(archive_entry).decode("utf-8")
        except zipfile.BadZipFile as exc:
            errors.append(f"template_unreadable_zip_header:{entry}:{exc}")
            continue
        except UnicodeDecodeError:
            errors.append(f"template_not_utf8:{entry}")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            literal_atoms = _template_line_literal_atoms(line)
            if not literal_atoms:
                continue
            atoms = ",".join(literal_atoms[:3])
            errors.append(f"template_contains_literal_fact_example:{entry}:line_{line_number}:{atoms}")


def _template_line_literal_atoms(line: str) -> list[str]:
    match = FACT_LIKE_RE.match(line)
    if not match:
        return []
    args = [arg.strip() for arg in match.group(2).split(",")]
    literal_atoms: list[str] = []
    for arg in args:
        if not arg or arg == "_" or arg[0].isupper():
            continue
        if arg in TEMPLATE_LITERAL_ALLOWLIST:
            continue
        if re.match(r"^[a-z][a-z0-9_]*$", arg):
            literal_atoms.append(arg)
    return literal_atoms


def _is_fact_template_file(entry: str) -> bool:
    name = Path(entry).name.lower()
    return bool(re.match(r"(candidate_)?(expected|forbidden)_facts(_template)?\.pl$", name))


def _is_output_template(entry: str) -> bool:
    normalized = _normalize_entry(entry).lower()
    name = Path(normalized).name.lower()
    return name.endswith("_template.pl") or normalized.startswith("output_template/")


def _proposal_paths(*, root: Path, explicit: list[Path]) -> list[Path]:
    paths = [path.resolve() for path in explicit]
    root_path = root.resolve()
    if root_path.exists():
        paths.extend(sorted(root_path.rglob("*.json")))
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path)] = path
    return list(unique.values())


def _pending_work_orders(payload: dict[str, Any]) -> list[dict[str, Any]]:
    value = payload.get("pending_external_work_orders")
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _resolve_path(value: str) -> Path:
    if not value:
        return Path("")
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / value


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _fixture_dirs(entries: list[str]) -> list[str]:
    dirs = sorted({entry.rsplit("/", 1)[0] for entry in entries if "/" in entry and entry.endswith("/source.md")})
    if dirs:
        return dirs
    return ["."] 


def _fixture_entries(entry_set: set[str], fixture: str) -> set[str]:
    prefixes = [f"{fixture}/"]
    if not fixture.startswith("fixtures/"):
        prefixes.append(f"fixtures/{fixture}/")
    found: set[str] = set()
    for prefix in prefixes:
        found.update(entry[len(prefix) :] for entry in entry_set if entry.startswith(prefix))
    return found


def _normalize_entry(value: str) -> str:
    return value.replace("\\", "/").strip("/")


def _zip_entry_name_errors(entries: list[str]) -> list[str]:
    errors: list[str] = []
    for value in entries:
        normalized = value.replace("\\", "/").strip()
        if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
            errors.append(f"unsafe_zip_entry_absolute:{normalized}")
            continue
        parts = PurePosixPath(normalized).parts
        if any(part == ".." for part in parts):
            errors.append(f"unsafe_zip_entry_traversal:{normalized}")
    return errors


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


if __name__ == "__main__":
    raise SystemExit(main())
