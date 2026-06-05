import json
from pathlib import Path

import scripts.audit_compile_fact_qa_exclusions as exclusions
from scripts.audit_compile_fact_qa_exclusions import audit_manifests


def test_compile_fact_exclusion_audit_accepts_complete_ledger(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(exclusions, "REPO_ROOT", tmp_path / "repo")
    measured = _write_measurement_manifest(tmp_path, ["fixture_a"])
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    exclusion = _write_exclusion_manifest(
        tmp_path,
        [
            {
                "fixture_id": "fixture_b",
                "reason_code": "diagnostic_boundary_probe",
                "status": "not_promoted",
                "note": "Boundary cell.",
                "evidence_roots": [str(evidence)],
            }
        ],
    )

    report = audit_manifests(
        measurement_manifest=measured,
        exclusion_manifest=exclusion,
        domain_status_report=_domain_status(["fixture_a", "fixture_b"]),
    )

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["measured_fixture_count"] == 1
    assert report["summary"]["excluded_fixture_count"] == 1


def test_compile_fact_exclusion_audit_blocks_missing_exclusion(tmp_path: Path) -> None:
    measured = _write_measurement_manifest(tmp_path, ["fixture_a"])
    exclusion = _write_exclusion_manifest(tmp_path, [])

    report = audit_manifests(
        measurement_manifest=measured,
        exclusion_manifest=exclusion,
        domain_status_report=_domain_status(["fixture_a", "fixture_b"]),
    )

    assert report["summary"]["status"] == "fail"
    assert any("fixture_b:associated_fixture_missing" in reason for reason in report["summary"]["blocking_reasons"])


def test_compile_fact_exclusion_audit_blocks_tmp_evidence(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    tmp_evidence = repo_root / "tmp" / "evidence"
    tmp_evidence.mkdir(parents=True)
    monkeypatch.setattr(exclusions, "REPO_ROOT", repo_root)
    measured = _write_measurement_manifest(tmp_path, ["fixture_a"])
    exclusion = _write_exclusion_manifest(
        tmp_path,
        [
            {
                "fixture_id": "fixture_b",
                "reason_code": "diagnostic_boundary_probe",
                "status": "not_promoted",
                "note": "Boundary cell.",
                "evidence_roots": [str(tmp_evidence)],
            }
        ],
    )

    report = exclusions.audit_manifests(
        measurement_manifest=measured,
        exclusion_manifest=exclusion,
        domain_status_report=_domain_status(["fixture_a", "fixture_b"]),
    )

    assert report["summary"]["status"] == "fail"
    assert any("evidence_root_under_repo_tmp" in reason for reason in report["summary"]["blocking_reasons"])


def _write_measurement_manifest(tmp_path: Path, fixture_ids: list[str]) -> Path:
    path = tmp_path / "measurement.json"
    path.write_text(
        json.dumps(
            {
                "schema": "prethinker.compile_fact_qa_manifest.v1",
                "cells": [{"id": fixture_id, "fixture_id": fixture_id} for fixture_id in fixture_ids],
            }
        ),
        encoding="utf-8",
    )
    return path


def _write_exclusion_manifest(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "exclusions.json"
    path.write_text(
        json.dumps(
            {
                "schema": "prethinker.compile_fact_qa_exclusion_manifest.v1",
                "exclusions": rows,
            }
        ),
        encoding="utf-8",
    )
    return path


def _domain_status(fixture_ids: list[str]) -> dict:
    return {
        "domains": [
            {
                "profile_id": "demo_domain",
                "fixtures": [{"fixture_id": fixture_id} for fixture_id in fixture_ids],
            }
        ]
    }
