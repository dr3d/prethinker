#!/usr/bin/env python3
"""Validate and import a legal-authority fixture package.

The importer is intentionally validation-first: it refuses to copy returned
fixtures or update the corpus manifest unless the offline intake validator
passes. It does not call an LLM or a live resolver.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_legal_authority_fixture_package import (  # noqa: E402
    _extract_zip_safely,
    _fixture_dirs,
    _payload_root,
    build_report as build_validation_report,
    render_markdown as render_validation_markdown,
)


DEFAULT_MANIFEST = REPO_ROOT / "datasets" / "legal_authority_verification" / "fixture_corpus_manifest.json"
DEFAULT_DEST_ROOTS = {
    "clean_public_filings": REPO_ROOT / "datasets" / "legal_authority_verification" / "clean_public_filings",
    "known_hallucination_or_sanction_filings": (
        REPO_ROOT / "datasets" / "legal_authority_verification" / "known_hallucination_or_sanction_filings"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--fixture-class", default="clean_public_filings")
    parser.add_argument("--expected-fixture-count", type=int, default=3)
    parser.add_argument("--dest-root", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = import_package(
        package_path=args.package,
        fixture_class=args.fixture_class,
        expected_fixture_count=args.expected_fixture_count,
        dest_root=args.dest_root,
        manifest_path=args.manifest,
        dry_run=args.dry_run,
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
    failed = report["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not failed else 1


def import_package(
    *,
    package_path: Path,
    fixture_class: str = "clean_public_filings",
    expected_fixture_count: int = 3,
    dest_root: Path | None = None,
    manifest_path: Path = DEFAULT_MANIFEST,
    dry_run: bool = False,
) -> dict[str, Any]:
    package_path = _resolve(package_path)
    dest_root = _resolve(dest_root or _default_dest_root(fixture_class))
    manifest_path = _resolve(manifest_path)
    validation = build_validation_report(
        package_path=package_path,
        fixture_class=fixture_class,
        expected_fixture_count=expected_fixture_count,
    )
    if validation["summary"]["status"] != "pass":
        return _report(
            package_path=package_path,
            dest_root=dest_root,
            manifest_path=manifest_path,
            dry_run=dry_run,
            validation=validation,
            imported=[],
            errors=["validation_failed"],
        )

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    errors: list[str] = []
    imported: list[dict[str, str]] = []
    try:
        if package_path.is_file() and package_path.suffix.casefold() == ".zip":
            temp_dir = tempfile.TemporaryDirectory(prefix="prethinker_legal_fixture_import_")
            extract_root = Path(temp_dir.name)
            errors.extend(_extract_zip_safely(package_path, extract_root))
            root = _payload_root(extract_root)
        else:
            root = _payload_root(package_path)
        fixture_dirs = _fixture_dirs(root)
        destinations = [(fixture_dir, dest_root / fixture_dir.name) for fixture_dir in fixture_dirs]
        for _source, dest in destinations:
            if dest.exists():
                errors.append(f"destination_exists:{_display_path(dest)}")
        if not manifest_path.exists():
            errors.append(f"manifest_missing:{_display_path(manifest_path)}")
        else:
            errors.extend(_manifest_update_errors(manifest_path=manifest_path, fixture_class=fixture_class))
        if errors:
            return _report(
                package_path=package_path,
                dest_root=dest_root,
                manifest_path=manifest_path,
                dry_run=dry_run,
                validation=validation,
                imported=[],
                errors=errors,
            )
        for source, dest in destinations:
            imported.append({"fixture_id": source.name, "source": _display_path(source), "destination": _display_path(dest)})
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, dest)
        if not dry_run:
            _update_manifest(
                manifest_path=manifest_path,
                fixture_class=fixture_class,
                fixture_paths=[_display_path(dest) for _source, dest in destinations],
            )
        return _report(
            package_path=package_path,
            dest_root=dest_root,
            manifest_path=manifest_path,
            dry_run=dry_run,
            validation=validation,
            imported=imported,
            errors=[],
        )
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Legal Authority Fixture Package Import",
        "",
        f"- Package: `{summary['package']}`",
        f"- Destination root: `{summary['dest_root']}`",
        f"- Manifest: `{summary['manifest']}`",
        f"- Dry run: `{summary['dry_run']}`",
        f"- Validation status: `{summary['validation_status']}`",
        f"- Imported fixtures: `{summary['imported_fixture_count']}`",
        f"- Blocking errors: `{summary['blocking_errors']}`",
        f"- Status: `{summary['status']}`",
        "",
        "## Imported Fixtures",
        "",
    ]
    if report.get("imported"):
        lines.extend(["| Fixture | Destination |", "| --- | --- |"])
        for row in report["imported"]:
            lines.append(f"| `{row['fixture_id']}` | `{row['destination']}` |")
    else:
        lines.append("_No fixtures imported._")
    if report.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- `{error}`" for error in report["errors"])
    if report["validation"]["summary"]["status"] != "pass":
        lines.extend(["", "## Validation Report", "", render_validation_markdown(report["validation"]).rstrip()])
    return "\n".join(lines) + "\n"


def _update_manifest(*, manifest_path: Path, fixture_class: str, fixture_paths: list[str]) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    classes = manifest.get("fixture_classes")
    if not isinstance(classes, list):
        raise ValueError("manifest fixture_classes must be a list")
    target = next((row for row in classes if isinstance(row, dict) and row.get("id") == fixture_class), None)
    if target is None:
        raise ValueError(f"manifest fixture class not found: {fixture_class}")
    existing = [str(item) for item in target.get("fixtures", []) if str(item).strip()]
    merged = sorted(dict.fromkeys([*existing, *fixture_paths]))
    target["fixtures"] = merged
    if fixture_class == "clean_public_filings" and merged:
        target["status"] = "seeded"
        manifest["next_external_work_order_needed"] = {
            "needed_now": False,
            "reason": (
                "Clean-public legal filings have been imported. Next expansion should be decided from "
                "the imported baseline audit before known hallucination/sanction fixtures are opened."
            ),
        }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _manifest_update_errors(*, manifest_path: Path, fixture_class: str) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [f"manifest_unreadable:{_display_path(manifest_path)}"]
    classes = manifest.get("fixture_classes")
    if not isinstance(classes, list):
        return ["manifest_fixture_classes_not_list"]
    if not any(isinstance(row, dict) and row.get("id") == fixture_class for row in classes):
        errors.append(f"manifest_fixture_class_not_found:{fixture_class}")
    return errors


def _default_dest_root(fixture_class: str) -> Path:
    return DEFAULT_DEST_ROOTS.get(
        fixture_class,
        REPO_ROOT / "datasets" / "legal_authority_verification" / fixture_class,
    )


def _report(
    *,
    package_path: Path,
    dest_root: Path,
    manifest_path: Path,
    dry_run: bool,
    validation: dict[str, Any],
    imported: list[dict[str, str]],
    errors: list[str],
) -> dict[str, Any]:
    return {
        "schema": "prethinker.legal_authority_fixture_package_import.v1",
        "summary": {
            "package": _display_path(package_path),
            "dest_root": _display_path(dest_root),
            "manifest": _display_path(manifest_path),
            "dry_run": dry_run,
            "validation_status": validation["summary"]["status"],
            "imported_fixture_count": len(imported),
            "blocking_errors": len(errors),
            "status": "pass" if not errors else "fail",
        },
        "validation": validation,
        "imported": imported,
        "errors": errors,
    }


def _resolve(path: Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
