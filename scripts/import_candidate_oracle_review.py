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
import re
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
    "expected_facts_template.pl",
    "candidate_forbidden_facts.pl",
    "forbidden_facts.pl",
    "forbidden_facts_template.pl",
    "README.md",
    "REVIEW_TEMPLATE.md",
    "adjudication_notes.md",
    "review_notes.md",
}
FACT_RE = re.compile(r"^\s*([a-z][a-z0-9_]*)\((.*)\)\.\s*$")
SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", required=True, type=Path, dest="zip_path")
    parser.add_argument("--dest-root", type=Path, default=DEFAULT_DEST_ROOT)
    parser.add_argument("--review-id", help="Import a specific review_id when the zip contains more than one manifest.")
    parser.add_argument(
        "--fixture-id",
        help=(
            "Fixture id for manifestless standalone review returns. "
            "When no manifest is present, this plus --review-id is required."
        ),
    )
    parser.add_argument(
        "--source-file",
        help="Optional repo-relative source file override for manifestless standalone review returns.",
    )
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
        fixture_id=args.fixture_id,
        source_file=args.source_file,
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
    fixture_id: str | None = None,
    source_file: str | None = None,
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
            return _import_manifestless_standalone_review(
                zip_path=zip_path,
                archive=archive,
                entries=entries,
                dest_root=dest_root,
                review_id=review_id,
                fixture_id=fixture_id,
                source_file=source_file,
                overwrite=overwrite,
                dry_run=dry_run,
            )
        if len(manifest_choices) > 1 and not _is_same_review_fixture_bundle(manifest_choices):
            errors.append("multiple_candidate_review_manifests")
            return _report(zip_path=zip_path, dest_root=dest_root, errors=errors, warnings=warnings, dry_run=dry_run, entries=entries)

        choices = manifest_choices
        imported_reviews: list[dict[str, Any]] = []
        dest_dirs: list[Path] = []
        for choice in choices:
            selected_review_id = _selected_review_id(choice, bundle=len(choices) > 1)
            if not selected_review_id:
                errors.append("selected_manifest_missing_review_id")
                continue
            dest_dir = dest_root / selected_review_id
            if dest_dir.exists() and not overwrite:
                errors.append(f"destination_exists:{selected_review_id}")
            dest_dirs.append(dest_dir)
            imported_reviews.append(
                {
                    "review_id": selected_review_id,
                    "fixture_id": str(choice["manifest"].get("fixture_id") or ""),
                    "dest_dir": _rel(dest_dir),
                    "copied_files": [],
                }
            )
        if errors:
            first = imported_reviews[0] if imported_reviews else {}
            return _report(
                zip_path=zip_path,
                dest_root=dest_root,
                review_id=str(first.get("review_id") or ""),
                dest_dir=dest_dirs[0] if dest_dirs else None,
                imported_reviews=imported_reviews,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )

        with tempfile.TemporaryDirectory(prefix="prethinker_candidate_review_") as tmp:
            manifest_paths: list[Path] = []
            dropped_all: list[str] = []
            copied_all: list[str] = []
            for index, choice in enumerate(choices):
                selected_review_id = imported_reviews[index]["review_id"]
                stage_dir = Path(tmp) / selected_review_id
                stage_dir.mkdir(parents=True, exist_ok=True)
                manifest = _normalized_manifest(choice["manifest"], selected_review_id=selected_review_id)
                copied, dropped = _stage_review_files(archive, entries, choice["prefix"], stage_dir, manifest=manifest)
                imported_reviews[index]["copied_files"] = copied
                copied_all.extend(f"{selected_review_id}/{item}" for item in copied)
                dropped_all.extend(dropped)
                manifest_paths.append(stage_dir / "manifest.json")
            if dropped_all:
                warnings.append(f"dropped_non_review_entries:{len(set(dropped_all))}")
            audit = audit_reviews(manifest_paths)
            warnings.extend(f"audit:{warning}" for warning in _audit_warnings(audit))
            if audit["summary"]["status"] != "pass":
                errors.extend(f"audit:{error}" for row in audit["reviews"] for error in row["errors"])
                first = imported_reviews[0]
                return _report(
                    zip_path=zip_path,
                    dest_root=dest_root,
                    review_id=first["review_id"],
                    dest_dir=dest_dirs[0],
                    copied=copied_all,
                    dropped=sorted(set(dropped_all)),
                    imported_reviews=imported_reviews,
                    audit=audit,
                    dry_run=dry_run,
                    errors=errors,
                    warnings=warnings,
                    entries=entries,
                )
            if not dry_run:
                dest_root.mkdir(parents=True, exist_ok=True)
                for index, item in enumerate(imported_reviews):
                    dest_dir = dest_root / item["review_id"]
                    if dest_dir.exists():
                        shutil.rmtree(dest_dir)
                    shutil.copytree(Path(tmp) / item["review_id"], dest_dir)
            first = imported_reviews[0]
            return _report(
                zip_path=zip_path,
                dest_root=dest_root,
                review_id=first["review_id"],
                dest_dir=dest_dirs[0],
                copied=copied_all,
                dropped=sorted(set(dropped_all)),
                imported_reviews=imported_reviews,
                audit=audit,
                dry_run=dry_run,
                errors=errors,
                warnings=warnings,
                entries=entries,
            )


def _import_manifestless_standalone_review(
    *,
    zip_path: Path,
    archive: zipfile.ZipFile,
    entries: list[dict[str, str]],
    dest_root: Path,
    review_id: str | None,
    fixture_id: str | None,
    source_file: str | None,
    overwrite: bool,
    dry_run: bool,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    base_review_id = _safe_id(review_id or "")
    fixture = str(fixture_id or "").strip()
    if not base_review_id:
        errors.append("manifestless_review_requires_review_id")
    if not fixture:
        errors.append("manifestless_review_requires_fixture_id")
    source_path = _manifestless_source_file(fixture_id=fixture, source_file=source_file)
    if fixture and not source_path:
        errors.append(f"source_file_not_found_for_fixture:{fixture}")
    grouped = _manifestless_fact_groups(archive=archive, entries=entries)
    invalid_lines = grouped.pop("__invalid__", {"expected": [], "forbidden": []})
    for role, lines in invalid_lines.items():
        for line in lines:
            errors.append(f"manifestless_{role}_fact_line_not_parseable:{line}")
    if not grouped:
        errors.append("manifestless_review_has_no_fact_rows")
    if errors:
        return _report(
            zip_path=zip_path,
            dest_root=dest_root,
            errors=errors,
            warnings=warnings,
            dry_run=dry_run,
            entries=entries,
        )

    imported_reviews: list[dict[str, Any]] = []
    dest_dirs: list[Path] = []
    for predicate, files in sorted(grouped.items()):
        selected_review_id = f"{base_review_id}_{predicate}_{_predicate_arity(files)}"
        dest_dir = dest_root / selected_review_id
        if dest_dir.exists() and not overwrite:
            errors.append(f"destination_exists:{selected_review_id}")
        dest_dirs.append(dest_dir)
        imported_reviews.append(
            {
                "review_id": selected_review_id,
                "fixture_id": fixture,
                "predicate": f"{predicate}/{_predicate_arity(files)}",
                "dest_dir": _rel(dest_dir),
                "copied_files": [],
            }
        )
    if errors:
        return _report(
            zip_path=zip_path,
            dest_root=dest_root,
            review_id=base_review_id,
            dest_dir=dest_dirs[0] if dest_dirs else None,
            imported_reviews=imported_reviews,
            errors=errors,
            warnings=warnings,
            dry_run=dry_run,
            entries=entries,
        )

    with tempfile.TemporaryDirectory(prefix="prethinker_candidate_review_") as tmp:
        manifest_paths: list[Path] = []
        copied_all: list[str] = []
        dropped_all: list[str] = []
        for index, item in enumerate(imported_reviews):
            stage_dir = Path(tmp) / item["review_id"]
            stage_dir.mkdir(parents=True, exist_ok=True)
            files = grouped[item["predicate"].rsplit("/", 1)[0]]
            manifest = {
                "review_id": item["review_id"],
                "fixture_id": fixture,
                "predicate": item["predicate"],
                "source_files": [source_path],
                "reviewer_blind_to_model_outputs": True,
                "reviewer_read_forbidden_inputs": False,
                "source_only_review": True,
                "bundle_review_id": base_review_id,
            }
            (stage_dir / "manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (stage_dir / "candidate_expected_facts.pl").write_text(
                "\n".join(files["expected"]) + ("\n" if files["expected"] else ""),
                encoding="utf-8",
            )
            (stage_dir / "candidate_forbidden_facts.pl").write_text(
                "\n".join(files["forbidden"]) + ("\n" if files["forbidden"] else ""),
                encoding="utf-8",
            )
            copied = [
                "manifest.json",
                "candidate_expected_facts.pl",
                "candidate_forbidden_facts.pl",
            ]
            readme_entry = _entry_by_basename(entries, "README.md") or _entry_by_basename(entries, "REVIEW_TEMPLATE.md")
            if readme_entry:
                _copy_entry(archive, readme_entry, stage_dir / "README.md")
                copied.append("README.md")
            notes_entry = _entry_by_basename(entries, "adjudication_notes.md") or _entry_by_basename(entries, "review_notes.md")
            if notes_entry:
                _copy_entry(archive, notes_entry, stage_dir / "adjudication_notes.md")
                copied.append("adjudication_notes.md")
            item["copied_files"] = copied
            copied_all.extend(f"{item['review_id']}/{name}" for name in copied)
            manifest_paths.append(stage_dir / "manifest.json")
        retained = {
            str(path)
            for name in {
                "README.md",
                "REVIEW_TEMPLATE.md",
                "adjudication_notes.md",
                "review_notes.md",
                "expected_facts.pl",
                "expected_facts_template.pl",
                "candidate_expected_facts.pl",
                "forbidden_facts.pl",
                "forbidden_facts_template.pl",
                "candidate_forbidden_facts.pl",
            }
            for path in [_entry_by_basename(entries, name)]
            if path
        }
        dropped_all = sorted(entry["name"] for entry in entries if entry["name"] not in retained)
        if dropped_all:
            warnings.append(f"dropped_non_review_entries:{len(set(dropped_all))}")
        audit = audit_reviews(manifest_paths)
        warnings.extend(f"audit:{warning}" for warning in _audit_warnings(audit))
        if audit["summary"]["status"] != "pass":
            errors.extend(f"audit:{error}" for row in audit["reviews"] for error in row["errors"])
            return _report(
                zip_path=zip_path,
                dest_root=dest_root,
                review_id=base_review_id,
                dest_dir=dest_dirs[0],
                copied=copied_all,
                dropped=sorted(set(dropped_all)),
                imported_reviews=imported_reviews,
                audit=audit,
                dry_run=dry_run,
                errors=errors,
                warnings=warnings,
                entries=entries,
            )
        if not dry_run:
            dest_root.mkdir(parents=True, exist_ok=True)
            for item in imported_reviews:
                dest_dir = dest_root / item["review_id"]
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(Path(tmp) / item["review_id"], dest_dir)
        return _report(
            zip_path=zip_path,
            dest_root=dest_root,
            review_id=base_review_id,
            dest_dir=dest_dirs[0],
            copied=copied_all,
            dropped=sorted(set(dropped_all)),
            imported_reviews=imported_reviews,
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


def _is_same_review_fixture_bundle(choices: list[dict[str, Any]]) -> bool:
    if len(choices) < 2:
        return False
    review_ids = {str(choice["manifest"].get("review_id") or "").strip() for choice in choices}
    fixture_ids = [str(choice["manifest"].get("fixture_id") or "").strip() for choice in choices]
    return len(review_ids) == 1 and bool(next(iter(review_ids))) and all(fixture_ids) and len(set(fixture_ids)) == len(fixture_ids)


def _selected_review_id(choice: dict[str, Any], *, bundle: bool) -> str:
    manifest = choice["manifest"]
    review_id = str(manifest.get("review_id") or "").strip()
    if not bundle:
        return review_id
    fixture_id = str(manifest.get("fixture_id") or "").strip()
    if not review_id or not fixture_id:
        return ""
    return f"{review_id}_{fixture_id}"


def _normalized_manifest(manifest: dict[str, Any], *, selected_review_id: str) -> dict[str, Any]:
    normalized = dict(manifest)
    original_review_id = str(manifest.get("review_id") or "").strip()
    if original_review_id and original_review_id != selected_review_id:
        normalized["bundle_review_id"] = original_review_id
    normalized["review_id"] = selected_review_id
    fixture_id = str(normalized.get("fixture_id") or "").strip()
    normalized["source_files"] = [
        _normalized_source_file(str(item), fixture_id=fixture_id)
        for item in normalized.get("source_files", [])
        if str(item).strip()
    ]
    return normalized


def _normalized_source_file(value: str, *, fixture_id: str) -> str:
    normalized = value.replace("\\", "/").strip()
    if fixture_id and normalized == f"fixtures/{fixture_id}/source.md":
        candidate = f"datasets/compile_micro_fixtures/{fixture_id}/source.md"
        if (REPO_ROOT / candidate).exists():
            return candidate
    return normalized


def _stage_review_files(
    archive: zipfile.ZipFile,
    entries: list[dict[str, str]],
    prefix: str,
    stage_dir: Path,
    *,
    manifest: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    copied: list[str] = []
    dropped: list[str] = []
    selected = {
        Path(entry["name"]).name: entry["name"]
        for entry in entries
        if _prefix(entry["name"]) == prefix and Path(entry["name"]).name in REVIEW_FILE_NAMES
    }
    if manifest is None:
        _copy_entry(archive, selected["manifest.json"], stage_dir / "manifest.json")
    else:
        (stage_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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


def _manifestless_fact_groups(
    *,
    archive: zipfile.ZipFile,
    entries: list[dict[str, str]],
) -> dict[str, dict[str, list[str]]]:
    grouped: dict[str, dict[str, list[str]]] = {}
    for role, names in {
        "expected": ("candidate_expected_facts.pl", "expected_facts.pl", "expected_facts_template.pl"),
        "forbidden": ("candidate_forbidden_facts.pl", "forbidden_facts.pl", "forbidden_facts_template.pl"),
    }.items():
        entry_name = ""
        for name in names:
            entry_name = _entry_by_basename(entries, name)
            if entry_name:
                break
        if not entry_name:
            continue
        text = archive.read(entry_name).decode("utf-8")
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("%"):
                continue
            match = FACT_RE.match(line)
            if not match:
                grouped.setdefault("__invalid__", {"expected": [], "forbidden": []})[role].append(line)
                continue
            predicate = match.group(1)
            grouped.setdefault(predicate, {"expected": [], "forbidden": []})[role].append(line)
    return grouped


def _predicate_arity(files: dict[str, list[str]]) -> int:
    for role in ("expected", "forbidden"):
        for line in files.get(role, []):
            match = FACT_RE.match(line)
            if match:
                return len(_split_fact_args(match.group(2)))
    return 0


def _split_fact_args(value: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote = False
    depth = 0
    for char in value:
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
    tail = "".join(current).strip()
    if tail or value.strip():
        args.append(tail)
    return args


def _manifestless_source_file(*, fixture_id: str, source_file: str | None) -> str:
    if source_file:
        normalized = source_file.replace("\\", "/").strip()
        path = REPO_ROOT / normalized
        return normalized if normalized.startswith("datasets/") and path.exists() else ""
    if not fixture_id:
        return ""
    matches = sorted((REPO_ROOT / "datasets").rglob(f"{fixture_id}/source.md"))
    if len(matches) != 1:
        return ""
    return _rel(matches[0])


def _entry_by_basename(entries: list[dict[str, str]], basename: str) -> str:
    matches = [entry["name"] for entry in entries if Path(entry["name"]).name == basename]
    return matches[0] if matches else ""


def _safe_id(value: str) -> str:
    lowered = value.strip().lower()
    safe = SAFE_ID_RE.sub("_", lowered).strip("_")
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe


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
    imported_reviews: list[dict[str, Any]] | None = None,
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
        "imported_reviews": imported_reviews or [],
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
