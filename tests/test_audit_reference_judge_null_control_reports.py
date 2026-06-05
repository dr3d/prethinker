import json
from pathlib import Path

import scripts.audit_reference_judge_null_control_reports as null_reports
from scripts.audit_reference_judge_null_control_reports import audit_manifest


def test_audit_reference_judge_null_control_reports_accepts_pass(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(null_reports, "REPO_ROOT", tmp_path / "repo")
    report = tmp_path / "report.json"
    _write_report(report)
    manifest = _write_manifest(tmp_path, report)

    result = audit_manifest(manifest)

    assert result["summary"]["status"] == "pass"
    assert result["reports"][0]["sampled_product_exact_rows"] == 6
    assert result["reports"][0]["exact_null_verdicts"] == 0


def test_audit_reference_judge_null_control_reports_blocks_exact_null(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(null_reports, "REPO_ROOT", tmp_path / "repo")
    report = tmp_path / "report.json"
    _write_report(report, exact_null_verdicts=1, status="blocked")
    manifest = _write_manifest(tmp_path, report)

    result = audit_manifest(manifest)

    assert result["summary"]["status"] == "fail"
    assert any("exact_null_verdicts" in reason for reason in result["summary"]["blocking_reasons"])


def test_audit_reference_judge_null_control_reports_blocks_repo_tmp_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = tmp_path / "repo"
    report = repo_root / "tmp" / "report.json"
    _write_report(report)
    manifest = _write_manifest(tmp_path, report)
    monkeypatch.setattr(null_reports, "REPO_ROOT", repo_root)

    result = null_reports.audit_manifest(manifest)

    assert result["summary"]["status"] == "fail"
    assert any("under_repo_tmp" in reason for reason in result["summary"]["blocking_reasons"])


def _write_manifest(tmp_path: Path, report: Path) -> Path:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "prethinker.reference_judge_null_control_manifest.v1",
                "reports": [
                    {
                        "id": "sample_report",
                        "report_json": str(report),
                        "expect": {
                            "sample_per_fixture": 3,
                            "sampled_product_exact_rows_min": 6,
                            "control_judgments_min": 12,
                            "exact_null_verdicts": 0,
                            "unclassified_redaction_fields": 0,
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return manifest


def _write_report(path: Path, *, exact_null_verdicts: int = 0, status: str = "pass") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "reference_judge_null_control_audit_v1",
                "sample_per_fixture": 3,
                "summary": {
                    "status": status,
                    "sampled_product_exact_rows": 6,
                    "control_judgments": 12,
                    "exact_null_verdicts": exact_null_verdicts,
                    "unclassified_redaction_fields": [],
                    "blocking_reasons": [] if status == "pass" else ["exact_null_verdicts"],
                },
            }
        ),
        encoding="utf-8",
    )
