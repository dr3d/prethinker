from pathlib import Path
import subprocess
import sys

from scripts.run_autolab_direct_artifact_drill import run_cycle


def test_direct_artifact_drill_writes_valid_source_and_blocked_reports(tmp_path: Path) -> None:
    report = run_cycle(out_dir=tmp_path / "cycle", include_blocked=True, include_source=True)

    assert report["validation_report"]["summary"]["failed_artifact_count"] == 0
    assert report["validation_report"]["summary"]["source_candidate_count"] == 1
    assert report["validation_report"]["summary"]["blocked_report_count"] == 1
    assert report["summary_report"]["summary"]["source_candidate_count"] == 1
    assert report["summary_report"]["summary"]["blocked_report_count"] == 1
    assert (tmp_path / "cycle" / "candidate_validation.json").exists()
    assert (tmp_path / "cycle" / "candidate_summary.md").exists()
    assert (tmp_path / "cycle" / "manifest.json").exists()


def test_direct_artifact_drill_can_run_blocked_only(tmp_path: Path) -> None:
    report = run_cycle(out_dir=tmp_path / "cycle", include_blocked=True, include_source=False)

    assert report["validation_report"]["summary"]["failed_artifact_count"] == 0
    assert report["validation_report"]["summary"]["source_candidate_count"] == 0
    assert report["validation_report"]["summary"]["blocked_report_count"] == 1


def test_direct_artifact_drill_cli_entrypoint(tmp_path: Path) -> None:
    out_dir = tmp_path / "cli_cycle"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/run_autolab_direct_artifact_drill.py",
            "--out-dir",
            str(out_dir),
            "--include-blocked",
            "--include-source",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert "Autolab candidate artifact validation" in proc.stdout
    assert (out_dir / "candidate_validation.json").exists()
