#!/usr/bin/env python3
"""Import a returned candidate-oracle review zip into the retained review set.

The importer reads only review-control files from the zip: manifest,
candidate expected/forbidden Prolog, README, and adjudication notes. It does
not copy source files, fixture payloads, model outputs, or work-order templates.
The staged review must pass `audit_candidate_oracle_reviews.py` before it is
written to `datasets/candidate_oracle_reviews`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.audit_candidate_oracle_reviews import build_report as audit_reviews  # noqa: E402


DEFAULT_DEST_ROOT = REPO_ROOT / "datasets" / "candidate_oracle_reviews"
REVIEW_FILE_NAMES = {
    "manifest.json",
    "candidate_expected_facts.pl",
    "expected_facts.pl",
    "candidate_forbidden_facts.pl",
    "forbidden_facts.pl",
    "README.md",
    "adjudication_notes.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", required=True, type=Path, dest="zip_path")
    parser.add_argument("--dest-root", type=Path, default=DEFAULT_DEST_ROOT)
    parser.add_argument("--review-id", help="Import a specific review_id when the zip contains more than one manifest.")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = import_review_zip(
        zip_path=args.zip_path,
        dest_root=args.dest_root,
        review_id=args.review_id,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["summary"]["status"] == "pass" else 1


def import_review_zip(
    *,
    zip_path: Path,
    dest_root: Path = DEFAULT_DEST_ROOT,
    review_id: str | None = None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    zip_path = _resolve_path(zip_path)
    dest_root = _resolve_path(dest_root)
    errors: list[str] = []
    warnings: list[str] = []
    if not zip_path.exists():
        errors.append(f"missing_zip:{zip_path}")
    elif not zipfile.is_zipfile(zip_path):
        errors.append(f"not_zip:{zip_path}")
    if errors:
        return _report(zip_path=zip_path, dest_root=dest_root, errors=errors, warnings=warnings, dry_run=dry_run)

    with zipfile.ZipFile(zip_path) as archive:
        entries = [_entry_info(entry) for entry in archive.infolist() if not entry.is_dir()]
        manifest_choices = _candidate_manifests(archive, entries)
        if review_id:
            manifest_choices = [item for item in manifest_choices if item["manifest"].get("review_id") == review_id]
        if not manifest_choices:
            errors.append("no_candidate_review_manifest")
            return _report(zip_path=zip_path, dest_root=dest_root, errors=errors, warnings=warnings, dry_run=dry_run, entries=entries)
        if len(manifest_choices) > 1:
            errors.append("multiple_candidate_review_manifests")
            return _report(zip_path=zip_path, dest_root=dest_root, errors=errors, warnings=warnings, dry_run=dry_run, entries=entries)

        choice = manifest_choices[0]
        manifest = choice["manifest"]
        selected_review_id = str(manifest.get("review_id") or "").strip()
        if not selected_review_id:
            errors.append("selected_manifest_missing_review_id")
            return _report(zip_path=zip_path, dest_root=dest_root, errors=errors, warnings=warnings, dry_run=dry_run, entries=entries)
        dest_dir = dest_root / selected_review_id
        if dest_dir.exists() and not overwrite:
            errors.append(f"destination_exists:{selected_review_id}")
            return _report(
                zip_path=zip_path,
                dest_root=dest_root,
                review_id=selected_review_id,
                dest_dir=dest_dir,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )

        with tempfile.TemporaryDirectory(prefix="prethinker_candidate_review_") as tmp:
            stage_dir = Path(tmp) / selected_review_id
            stage_dir.mkdir(parents=True, exist_ok=True)
            copied, dropped = _stage_review_files(archive, entries, choice["prefix"], stage_dir)
            if dropped:
                warnings.append(f"dropped_non_review_entries:{len(dropped)}")
            audit = audit_reviews([stage_dir / "manifest.json"])
            warnings.extend(f"audit:{warning}" for warning in _audit_warnings(audit))
            if audit["summary"]["status"] != "pass":
                errors.extend(f"audit:{error}" for row in audit["reviews"] for error in row["errors"])
                return _report(
                    zip_path=zip_path,
                    dest_root=dest_root,
                    review_id=selected_review_id,
                    dest_dir=dest_dir,
                    copied=copied,
                    dropped=dropped,
                    audit=audit,
                    dry_run=dry_run,
                    errors=errors,
                    warnings=warnings,
                    entries=entries,
                )
            if not dry_run:
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                dest_root.mkdir(parents=True, exist_ok=True)
                shutil.copytree(stage_dir, dest_dir)
            return _report(
                zip_path=zip_path,
                dest_root=dest_root,
                review_id=selected_review_id,
                dest_dir=dest_dir,
                copied=copied,
                dropped=dropped,
                audit=audit,
                dry_run=dry_run,
                errors=errors,
                warnings=warnings,
                entries=entries,
            )


def _candidate_manifests(archive: zipfile.ZipFile, entries: list[dict[str, str]]) -> list[dict[str, Any]]:
    choices: list[dict[str, Any]] = []
    for entry in entries:
        if Path(entry["name"]).name != "manifest.json":
            continue
        try:
            manifest = json.loads(archive.read(entry["name"]).decode("utf-8"))
        except Exception:
            continue
        if not isinstance(manifest, dict):
            continue
        if not manifest.get("review_id") or not manifest.get("predicate"):
            continue
        choices.append({"entry": entry["name"], "prefix": _prefix(entry["name"]), "manifest": manifest})
    return choices


def _stage_review_files(
    archive: zipfile.ZipFile,
    entries: list[dict[str, str]],
    prefix: str,
    stage_dir: Path,
) -> tuple[list[str], list[str]]:
    copied: list[str] = []
    dropped: list[str] = []
    selected = {
        Path(entry["name"]).name: entry["name"]
        for entry in entries
        if _prefix(entry["name"]) == prefix and Path(entry["name"]).name in REVIEW_FILE_NAMES
    }
    _copy_entry(archive, selected["manifest.json"], stage_dir / "manifest.json")
    copied.append("manifest.json")
    expected = selected.get("candidate_expected_facts.pl") or selected.get("expected_facts.pl")
    forbidden = selected.get("candidate_forbidden_facts.pl") or selected.get("forbidden_facts.pl")
    if expected:
        _copy_entry(archive, expected, stage_dir / "candidate_expected_facts.pl")
        copied.append("candidate_expected_facts.pl")
    if forbidden:
        _copy_entry(archive, forbidden, stage_dir / "candidate_forbidden_facts.pl")
        copied.append("candidate_forbidden_facts.pl")
    for optional in ("README.md", "adjudication_notes.md"):
        if optional in selected:
            _copy_entry(archive, selected[optional], stage_dir / optional)
            copied.append(optional)
    allowed_sources = set(selected.values())
    for entry in entries:
        if entry["name"] not in allowed_sources:
            dropped.append(entry["name"])
    return copied, dropped


def _audit_warnings(audit: dict[str, Any]) -> list[str]:
    return [warning for row in audit.get("reviews", []) for warning in row.get("warnings", [])]


def _copy_entry(archive: zipfile.ZipFile, name: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(archive.read(name))


def _entry_info(entry: zipfile.ZipInfo) -> dict[str, str]:
    return {"name": entry.filename.replace("\\", "/").strip("/")}


def _prefix(name: str) -> str:
    value = name.replace("\\", "/").strip("/")
    if "/" not in value:
        return ""
    return value.rsplit("/", 1)[0]


def _report(
    *,
    zip_path: Path,
    dest_root: Path,
    errors: list[str],
    warnings: list[str],
    review_id: str = "",
    dest_dir: Path | None = None,
    copied: list[str] | None = None,
    dropped: list[str] | None = None,
    audit: dict[str, Any] | None = None,
    dry_run: bool = False,
    entries: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "schema": "prethinker.candidate_oracle_review_import.v1",
        "summary": {
            "status": "pass" if not errors else "fail",
            "blocking_errors": len(errors),
            "warnings": len(warnings),
            "dry_run": bool(dry_run),
        },
        "zip_path": _rel(zip_path),
        "dest_root": _rel(dest_root),
        "review_id": review_id,
        "dest_dir": _rel(dest_dir) if dest_dir else "",
        "copied_files": copied or [],
        "dropped_entries": dropped or [],
        "zip_entry_count": len(entries or []),
        "audit_summary": (audit or {}).get("summary", {}),
        "errors": errors,
        "warnings": warnings,
    }


def _resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
