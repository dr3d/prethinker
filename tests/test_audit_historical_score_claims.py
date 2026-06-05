import subprocess
from pathlib import Path

from scripts.audit_historical_score_claims import _default_docs, audit_docs


def test_audit_historical_score_claims_allows_disclaimed_scores(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "Older 80.5%, 92.33%, 95%, 98.5%, and 99% figures are not current accuracy claims. "
        "They were contaminated by prose-smuggling paths.\n",
        encoding="utf-8",
    )

    report = audit_docs(root=tmp_path, docs=[Path("doc.md")])

    assert report["summary"] == {
        "blocking_occurrence_count": 0,
        "occurrence_count": 5,
        "skipped_doc_count": 0,
        "stale_status_occurrence_count": 0,
        "status": "pass",
    }
    assert all(item["disclaimed"] for item in report["occurrences"])


def test_audit_historical_score_claims_blocks_undisclaimed_scores(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text("Prethinker achieved 98.5% on the benchmark.\n", encoding="utf-8")

    report = audit_docs(root=tmp_path, docs=[Path("doc.md")])

    assert report["summary"] == {
        "blocking_occurrence_count": 1,
        "occurrence_count": 1,
        "skipped_doc_count": 0,
        "stale_status_occurrence_count": 0,
        "status": "fail",
    }
    assert report["blocking_occurrences"][0]["score"] == "98.5%"


def test_audit_historical_score_claims_blocks_stale_current_status(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "The current standing status is deliberately red: FDA transfer_002 emits a "
        "source-rejected `fda_adulteration_basis/5` 501(a)(2)(A) row.\n",
        encoding="utf-8",
    )

    report = audit_docs(root=tmp_path, docs=[Path("doc.md")])

    assert report["summary"] == {
        "blocking_occurrence_count": 0,
        "occurrence_count": 0,
        "skipped_doc_count": 0,
        "stale_status_occurrence_count": 2,
        "status": "fail",
    }
    assert {item["pattern"] for item in report["stale_status_occurrences"]} == {
        "fda_transfer_002_red_cell"
    }


def test_audit_historical_score_claims_blocks_stale_fda_current_metric(tmp_path: Path) -> None:
    doc = tmp_path / "index.html"
    doc.write_text(
        "<article><span>FDA Case Study</span><strong>21 / 29; 19 / 26</strong></article>\n",
        encoding="utf-8",
    )

    report = audit_docs(root=tmp_path, docs=[Path("index.html")])

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["stale_status_occurrence_count"] == 1
    assert report["stale_status_occurrences"][0]["pattern"] == "fda_transfer_002_stale_21_29_current_metric"


def test_audit_historical_score_claims_allows_historical_fda_21_29_context(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "The prior 21 / 29 contract-only root is historical context, not the current full-lens recall claim.\n",
        encoding="utf-8",
    )

    report = audit_docs(root=tmp_path, docs=[Path("doc.md")])

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["stale_status_occurrence_count"] == 0


def test_audit_historical_score_claims_blocks_stale_sec_current_metric(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "standing breadth check: seed 13 / 13; transfer_001 11 / 13; transfer_002 11 / 12\n",
        encoding="utf-8",
    )

    report = audit_docs(root=tmp_path, docs=[Path("doc.md")])

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["stale_status_occurrence_count"] == 1
    assert report["stale_status_occurrences"][0]["pattern"] == "sec_transfer_001_stale_11_13_current_metric"


def test_audit_historical_score_claims_fails_missing_docs(tmp_path: Path) -> None:
    report = audit_docs(root=tmp_path, docs=[Path("missing.md")])

    assert report["summary"] == {
        "blocking_occurrence_count": 0,
        "occurrence_count": 0,
        "skipped_doc_count": 1,
        "stale_status_occurrence_count": 0,
        "status": "fail",
    }


def test_default_docs_scan_tracked_docs_not_untracked_drafts(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text("# Readme\n", encoding="utf-8")
    (tmp_path / "docs" / "tracked.md").write_text("not current 90%+\n", encoding="utf-8")
    (tmp_path / "docs" / "index.html").write_text("<strong>11 / 29</strong>\n", encoding="utf-8")
    (tmp_path / "docs" / "draft.md").write_text("90%+\n", encoding="utf-8")

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "add", "README.md", "docs/tracked.md", "docs/index.html"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    docs = _default_docs(tmp_path)

    assert Path("README.md") in docs
    assert Path("docs/tracked.md") in docs
    assert Path("docs/index.html") in docs
    assert Path("docs/draft.md") not in docs
