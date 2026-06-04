from pathlib import Path

from scripts.audit_historical_score_claims import audit_docs


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
        "status": "fail",
    }
    assert report["blocking_occurrences"][0]["score"] == "98.5%"


def test_audit_historical_score_claims_fails_missing_docs(tmp_path: Path) -> None:
    report = audit_docs(root=tmp_path, docs=[Path("missing.md")])

    assert report["summary"] == {
        "blocking_occurrence_count": 0,
        "occurrence_count": 0,
        "skipped_doc_count": 1,
        "status": "fail",
    }
