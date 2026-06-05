#!/usr/bin/env python3
"""Import a returned source-only expected/forbidden oracle review zip.

These reviews are not candidate-row adjudications. They are independent
source-only oracle packages for draft domain predicate packs: per-fixture
expected_facts.pl and forbidden_facts.pl, plus a manifest. The importer keeps
only review outputs, enriches package metadata from the proposal file, and
requires the staged result to pass audit_source_oracle_reviews.py before it is
written to datasets/source_oracle_reviews.
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

from scripts.audit_source_oracle_reviews import build_report as audit_reviews  # noqa: E402


DEFAULT_DEST_ROOT = REPO_ROOT / "datasets" / "source_oracle_reviews"
REVIEW_NOTE_FILES = {"review_notes.md", "README.md"}
FACT_FILES = {"expected_facts.pl", "forbidden_facts.pl"}
SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", required=True, type=Path, dest="zip_path")
    parser.add_argument("--proposal", required=True, type=Path)
    parser.add_argument("--dest-root", type=Path, default=DEFAULT_DEST_ROOT)
    parser.add_argument("--review-id")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = import_review_zip(
        zip_path=args.zip_path,
        proposal_path=args.proposal,
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
    proposal_path: Path,
    dest_root: Path = DEFAULT_DEST_ROOT,
    review_id: str | None = None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    zip_path = _resolve_path(zip_path)
    proposal_path = _resolve_path(proposal_path)
    dest_root = _resolve_path(dest_root)
    errors: list[str] = []
    warnings: list[str] = []
    proposal = _load_json(proposal_path)
    if not zip_path.exists():
        errors.append(f"missing_zip:{zip_path}")
    elif not zipfile.is_zipfile(zip_path):
        errors.append(f"not_zip:{zip_path}")
    if not proposal:
        errors.append(f"missing_or_invalid_proposal:{_rel(proposal_path)}")
    if errors:
        return _report(
            zip_path=zip_path,
            proposal_path=proposal_path,
            dest_root=dest_root,
            errors=errors,
            warnings=warnings,
            dry_run=dry_run,
        )

    with zipfile.ZipFile(zip_path) as archive:
        entries = [_entry_name(entry) for entry in archive.infolist() if not entry.is_dir()]
        unsafe = _unsafe_entries(entries)
        if unsafe:
            errors.extend(f"unsafe_zip_entry:{entry}" for entry in unsafe)
            return _report(
                zip_path=zip_path,
                proposal_path=proposal_path,
                dest_root=dest_root,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )
        manifest_entry, manifest = _select_manifest(archive, entries)
        if not manifest_entry:
            errors.append("missing_manifest.json")
            return _report(
                zip_path=zip_path,
                proposal_path=proposal_path,
                dest_root=dest_root,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )
        independence_errors = _manifest_independence_errors(manifest)
        if independence_errors:
            errors.extend(independence_errors)
            return _report(
                zip_path=zip_path,
                proposal_path=proposal_path,
                dest_root=dest_root,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )
        proposed_review_id = review_id or str(manifest.get("review_id") or "").strip()
        selected_review_id = _safe_id(proposed_review_id or f"{proposal['proposal_id']}_{zip_path.stem}")
        if not selected_review_id:
            errors.append("missing_review_id")
            return _report(
                zip_path=zip_path,
                proposal_path=proposal_path,
                dest_root=dest_root,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )
        fact_entries = _fact_entries(entries)
        fixture_ids = sorted(set(_manifest_fixture_ids(manifest)) | set(fact_entries))
        if not fixture_ids:
            errors.append("no_fixture_outputs")
            return _report(
                zip_path=zip_path,
                proposal_path=proposal_path,
                dest_root=dest_root,
                review_id=selected_review_id,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )
        source_map, source_errors = _source_file_map(fixture_ids)
        errors.extend(source_errors)
        if errors:
            return _report(
                zip_path=zip_path,
                proposal_path=proposal_path,
                dest_root=dest_root,
                review_id=selected_review_id,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )
        dest_dir = dest_root / selected_review_id
        if dest_dir.exists() and not overwrite:
            errors.append(f"destination_exists:{selected_review_id}")
            return _report(
                zip_path=zip_path,
                proposal_path=proposal_path,
                dest_root=dest_root,
                review_id=selected_review_id,
                dest_dir=dest_dir,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )

        with tempfile.TemporaryDirectory(prefix="prethinker_source_oracle_review_") as tmp:
            stage_dir = Path(tmp) / selected_review_id
            stage_dir.mkdir(parents=True, exist_ok=True)
            copied, dropped, normalized_manifest = _stage_review(
                archive=archive,
                entries=entries,
                fact_entries=fact_entries,
                manifest=manifest,
                proposal=proposal,
                proposal_path=proposal_path,
                review_id=selected_review_id,
                fixture_ids=fixture_ids,
                source_map=source_map,
                stage_dir=stage_dir,
            )
            if dropped:
                warnings.append(f"dropped_non_review_entries:{len(dropped)}")
            audit = audit_reviews([stage_dir / "manifest.json"])
            if audit["summary"]["status"] != "pass":
                errors.extend(
                    f"audit:{error}"
                    for row in audit["reviews"]
                    for error in (row["errors"] + [item for output in row["outputs"] for item in output["errors"]])
                )
                return _report(
                    zip_path=zip_path,
                    proposal_path=proposal_path,
                    dest_root=dest_root,
                    review_id=selected_review_id,
                    dest_dir=dest_dir,
                    copied=copied,
                    dropped=dropped,
                    audit=audit,
                    normalized_manifest=normalized_manifest,
                    errors=errors,
                    warnings=warnings,
                    dry_run=dry_run,
                    entries=entries,
                )
            if not dry_run:
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                dest_root.mkdir(parents=True, exist_ok=True)
                shutil.copytree(stage_dir, dest_dir)
            return _report(
                zip_path=zip_path,
                proposal_path=proposal_path,
                dest_root=dest_root,
                review_id=selected_review_id,
                dest_dir=dest_dir,
                copied=copied,
                dropped=dropped,
                audit=audit,
                normalized_manifest=normalized_manifest,
                errors=errors,
                warnings=warnings,
                dry_run=dry_run,
                entries=entries,
            )


def _stage_review(
    *,
    archive: zipfile.ZipFile,
    entries: list[str],
    fact_entries: dict[str, dict[str, str]],
    manifest: dict[str, Any],
    proposal: dict[str, Any],
    proposal_path: Path,
    review_id: str,
    fixture_ids: list[str],
    source_map: dict[str, str],
    stage_dir: Path,
) -> tuple[list[str], list[str], dict[str, Any]]:
    copied: list[str] = []
    retained_entries: set[str] = set()
    outputs: dict[str, dict[str, Any]] = {}
    raw_outputs = manifest.get("outputs") if isinstance(manifest.get("outputs"), dict) else {}
    for fixture_id in fixture_ids:
        fixture_dir = stage_dir / fixture_id
        fixture_dir.mkdir(parents=True, exist_ok=True)
        fixture_entries = fact_entries.get(fixture_id, {})
        expected_entry = fixture_entries.get("expected_facts.pl")
        forbidden_entry = fixture_entries.get("forbidden_facts.pl")
        if expected_entry:
            (fixture_dir / "expected_facts.pl").write_bytes(archive.read(expected_entry))
            retained_entries.add(expected_entry)
            copied.append(f"{fixture_id}/expected_facts.pl")
        else:
            (fixture_dir / "expected_facts.pl").write_text("", encoding="utf-8")
            copied.append(f"{fixture_id}/expected_facts.pl")
        if forbidden_entry:
            (fixture_dir / "forbidden_facts.pl").write_bytes(archive.read(forbidden_entry))
            retained_entries.add(forbidden_entry)
            copied.append(f"{fixture_id}/forbidden_facts.pl")
        else:
            (fixture_dir / "forbidden_facts.pl").write_text("", encoding="utf-8")
            copied.append(f"{fixture_id}/forbidden_facts.pl")
        expected_count = _fact_count(fixture_dir / "expected_facts.pl")
        forbidden_count = _fact_count(fixture_dir / "forbidden_facts.pl")
        raw_output = raw_outputs.get(fixture_id) if isinstance(raw_outputs.get(fixture_id), dict) else {}
        outputs[fixture_id] = {
            "expected_fact_count": expected_count,
            "forbidden_fact_count": forbidden_count,
            "source_files": [source_map[fixture_id]],
            "source_only_basis": str(raw_output.get("source_only_basis") or "").strip(),
        }

    for note_name in REVIEW_NOTE_FILES:
        note_entry = _entry_by_basename(entries, note_name)
        if note_entry:
            (stage_dir / note_name).write_bytes(archive.read(note_entry))
            retained_entries.add(note_entry)
            copied.append(note_name)

    total_expected = sum(row["expected_fact_count"] for row in outputs.values())
    total_forbidden = sum(row["forbidden_fact_count"] for row in outputs.values())
    blocked_reason = str(manifest.get("blocked_reason") or "").strip()
    status = "blocked" if blocked_reason and not (total_expected or total_forbidden) else "complete"
    normalized_manifest = {
        "schema": "prethinker.source_oracle_review.v1",
        "review_id": review_id,
        "proposal_id": str(proposal.get("proposal_id") or "").strip(),
        "proposal_file": _rel(proposal_path),
        "predicate": str(proposal.get("candidate_signature") or "").strip(),
        "status": status,
        "source_only_review": True,
        "reviewer": str(manifest.get("reviewer") or "external_source_only_agent").strip(),
        "reviewer_blind_to_model_outputs": True,
        "reviewer_read_model_outputs": False,
        "blocked_reason": blocked_reason,
        "outputs": outputs,
        "notes": str(manifest.get("notes") or "").strip(),
    }
    (stage_dir / "manifest.json").write_text(
        json.dumps(normalized_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    copied.append("manifest.json")
    dropped = [
        entry
        for entry in entries
        if entry not in retained_entries and Path(entry).name not in {"manifest.json"}
    ]
    return copied, dropped, normalized_manifest


def _select_manifest(archive: zipfile.ZipFile, entries: list[str]) -> tuple[str, dict[str, Any]]:
    candidates = [entry for entry in entries if Path(entry).name == "manifest.json"]
    for entry in candidates:
        try:
            payload = json.loads(archive.read(entry).decode("utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict):
            return entry, payload
    return "", {}


def _fact_entries(entries: list[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for entry in entries:
        path = Path(entry)
        basename = path.name
        if basename not in FACT_FILES or len(path.parts) < 2:
            continue
        fixture_id = path.parent.name
        if fixture_id.lower() in {"output_template", "template"}:
            continue
        result.setdefault(fixture_id, {})[basename] = entry
    return result


def _manifest_fixture_ids(manifest: dict[str, Any]) -> list[str]:
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict):
        return []
    return [str(key).strip() for key in outputs if str(key).strip()]


def _manifest_independence_errors(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("reviewer_blind_to_model_outputs") is False:
        errors.append("returned_manifest_declares_not_blind_to_model_outputs")
    if manifest.get("reviewer_read_model_outputs") is True:
        errors.append("returned_manifest_declares_model_output_exposure")
    if manifest.get("source_only_review") is False:
        errors.append("returned_manifest_declares_not_source_only")
    return errors


def _source_file_map(fixture_ids: list[str]) -> tuple[dict[str, str], list[str]]:
    source_map: dict[str, str] = {}
    errors: list[str] = []
    for fixture_id in fixture_ids:
        matches = sorted((REPO_ROOT / "datasets").rglob(f"{fixture_id}/source.md"))
        if not matches:
            errors.append(f"source_file_not_found_for_fixture:{fixture_id}")
            continue
        if len(matches) > 1:
            rendered = ",".join(_rel(path) for path in matches)
            errors.append(f"ambiguous_source_file_for_fixture:{fixture_id}:{rendered}")
            continue
        source_map[fixture_id] = _rel(matches[0])
    return source_map, errors


def _fact_count(path: Path) -> int:
    count = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        text = raw.strip()
        if text and not text.startswith("%"):
            count += 1
    return count


def _entry_by_basename(entries: list[str], basename: str) -> str:
    matches = [entry for entry in entries if Path(entry).name == basename]
    return matches[0] if matches else ""


def _unsafe_entries(entries: list[str]) -> list[str]:
    unsafe: list[str] = []
    for entry in entries:
        path = Path(entry)
        if path.is_absolute() or ".." in path.parts:
            unsafe.append(entry)
    return unsafe


def _entry_name(entry: zipfile.ZipInfo) -> str:
    return entry.filename.replace("\\", "/").strip("/")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_id(value: str) -> str:
    lowered = value.strip().lower()
    safe = SAFE_ID_RE.sub("_", lowered).strip("_")
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe


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


def _report(
    *,
    zip_path: Path,
    proposal_path: Path,
    dest_root: Path,
    errors: list[str],
    warnings: list[str],
    review_id: str = "",
    dest_dir: Path | None = None,
    copied: list[str] | None = None,
    dropped: list[str] | None = None,
    audit: dict[str, Any] | None = None,
    normalized_manifest: dict[str, Any] | None = None,
    dry_run: bool = False,
    entries: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema": "prethinker.source_oracle_review_import.v1",
        "summary": {
            "status": "pass" if not errors else "fail",
            "blocking_errors": len(errors),
            "warnings": len(warnings),
            "dry_run": bool(dry_run),
        },
        "zip_path": _rel(zip_path),
        "proposal_path": _rel(proposal_path),
        "dest_root": _rel(dest_root),
        "review_id": review_id,
        "dest_dir": _rel(dest_dir) if dest_dir else "",
        "copied_files": copied or [],
        "dropped_entries": dropped or [],
        "zip_entry_count": len(entries or []),
        "audit_summary": (audit or {}).get("summary", {}),
        "normalized_manifest": normalized_manifest or {},
        "errors": errors,
        "warnings": warnings,
    }


if __name__ == "__main__":
    raise SystemExit(main())
