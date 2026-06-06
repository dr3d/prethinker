from __future__ import annotations

import json
import zipfile
from pathlib import Path

from scripts.import_legal_authority_fixture_package import import_package
from test_validate_legal_authority_fixture_package import _convert_package_to_known_sanction_shape, _write_package


def test_import_legal_authority_fixture_package_copies_fixtures_and_updates_manifest(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    manifest_path = _write_manifest(tmp_path)
    dest_root = tmp_path / "imported_clean_public"

    report = import_package(package_path=package, dest_root=dest_root, manifest_path=manifest_path)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["imported_fixture_count"] == 3
    assert (dest_root / "clean_legal_filing_001" / "source.md").exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    clean_public = next(row for row in manifest["fixture_classes"] if row["id"] == "clean_public_filings")
    assert clean_public["status"] == "seeded"
    assert len(clean_public["fixtures"]) == 3
    assert manifest["next_external_work_order_needed"]["needed_now"] is False


def test_import_legal_authority_fixture_package_accepts_zip_with_top_level_folder(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    zip_path = tmp_path / "legal_authority_clean_public_filings_20260606_01.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in package.rglob("*"):
            if path.is_file():
                archive.write(path, arcname=str(Path(package.name) / path.relative_to(package)))
    manifest_path = _write_manifest(tmp_path)
    dest_root = tmp_path / "imported_clean_public"

    report = import_package(package_path=zip_path, dest_root=dest_root, manifest_path=manifest_path)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["imported_fixture_count"] == 3
    assert (dest_root / "clean_legal_filing_003" / "manifest.json").exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    clean_public = next(row for row in manifest["fixture_classes"] if row["id"] == "clean_public_filings")
    assert len(clean_public["fixtures"]) == 3
    assert clean_public["fixtures"][0].endswith("imported_clean_public/clean_legal_filing_001")
    assert clean_public["fixtures"][1].endswith("imported_clean_public/clean_legal_filing_002")
    assert clean_public["fixtures"][2].endswith("imported_clean_public/clean_legal_filing_003")


def test_import_legal_authority_fixture_package_dry_run_does_not_mutate(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    manifest_path = _write_manifest(tmp_path)
    original_manifest = manifest_path.read_text(encoding="utf-8")
    dest_root = tmp_path / "imported_clean_public"

    report = import_package(package_path=package, dest_root=dest_root, manifest_path=manifest_path, dry_run=True)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["imported_fixture_count"] == 3
    assert not dest_root.exists()
    assert manifest_path.read_text(encoding="utf-8") == original_manifest


def test_import_legal_authority_fixture_package_refuses_failed_validation(tmp_path: Path) -> None:
    package = tmp_path / "bad_package"
    package.mkdir()
    manifest_path = _write_manifest(tmp_path)
    dest_root = tmp_path / "imported_clean_public"

    report = import_package(package_path=package, dest_root=dest_root, manifest_path=manifest_path)

    assert report["summary"]["status"] == "fail"
    assert report["errors"] == ["validation_failed"]
    assert not dest_root.exists()


def test_import_legal_authority_fixture_package_refuses_existing_destination(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    manifest_path = _write_manifest(tmp_path)
    dest_root = tmp_path / "imported_clean_public"
    (dest_root / "clean_legal_filing_001").mkdir(parents=True)

    report = import_package(package_path=package, dest_root=dest_root, manifest_path=manifest_path)

    assert report["summary"]["status"] == "fail"
    assert any(error.startswith("destination_exists:") for error in report["errors"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    clean_public = next(row for row in manifest["fixture_classes"] if row["id"] == "clean_public_filings")
    assert clean_public["fixtures"] == []


def test_import_legal_authority_fixture_package_defaults_destination_by_fixture_class(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import scripts.import_legal_authority_fixture_package as importer

    package = _write_package(tmp_path)
    _convert_package_to_known_sanction_shape(package)
    manifest_path = _write_manifest(tmp_path)
    monkeypatch.setattr(
        importer,
        "DEFAULT_DEST_ROOTS",
        {
            "clean_public_filings": tmp_path / "wrong_clean_public",
            "known_hallucination_or_sanction_filings": tmp_path / "known_sanction_default",
        },
    )

    report = import_package(
        package_path=package,
        fixture_class="known_hallucination_or_sanction_filings",
        manifest_path=manifest_path,
    )

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["dest_root"].endswith("known_sanction_default")
    assert (tmp_path / "known_sanction_default" / "clean_legal_filing_001" / "sanction_or_correction_source.md").exists()
    assert not (tmp_path / "wrong_clean_public").exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    known = next(row for row in manifest["fixture_classes"] if row["id"] == "known_hallucination_or_sanction_filings")
    assert known["status"] == "seeded"
    assert manifest["next_external_work_order_needed"]["needed_now"] is False
    assert "false-verification audit" in manifest["next_external_work_order_needed"]["reason"]


def test_import_legal_authority_fixture_package_allows_explicit_destination_override(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import scripts.import_legal_authority_fixture_package as importer

    package = _write_package(tmp_path)
    _convert_package_to_known_sanction_shape(package)
    manifest_path = _write_manifest(tmp_path)
    monkeypatch.setattr(
        importer,
        "DEFAULT_DEST_ROOTS",
        {"known_hallucination_or_sanction_filings": tmp_path / "known_sanction_default"},
    )
    dest_root = tmp_path / "explicit_known_sanction_dest"

    report = import_package(
        package_path=package,
        fixture_class="known_hallucination_or_sanction_filings",
        dest_root=dest_root,
        manifest_path=manifest_path,
    )

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["dest_root"].endswith("explicit_known_sanction_dest")
    assert (dest_root / "clean_legal_filing_002" / "sanction_or_correction_source.md").exists()
    assert not (tmp_path / "known_sanction_default").exists()


def _write_manifest(tmp_path: Path) -> Path:
    path = tmp_path / "fixture_corpus_manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema": "prethinker.legal_authority_verification.fixture_corpus_manifest.v1",
                "status": "candidate_research_lane",
                "fixture_classes": [
                    {"id": "controlled_adversarial_mutations", "status": "seeded", "fixtures": []},
                    {"id": "clean_public_filings", "status": "planned", "fixtures": []},
                    {
                        "id": "known_hallucination_or_sanction_filings",
                        "status": "deferred_until_clean_public_baseline",
                        "fixtures": [],
                    },
                ],
                "next_external_work_order_needed": {"needed_now": True, "reason": "test"},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path
