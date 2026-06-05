import json
from pathlib import Path

from scripts.audit_source_oracle_reviews import build_report, main, render_markdown


SOURCE_FILE = "datasets/compile_micro_fixtures/fda_warning_letter_domain_transfer_002/source.md"


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _review_dir(root: Path, **overrides: object) -> Path:
    review = root / "demo_source_oracle_review"
    payload = {
        "schema": "prethinker.source_oracle_review.v1",
        "review_id": "demo_source_oracle_review",
        "proposal_id": "demo_proposal_v1",
        "proposal_file": "datasets/domain_predicate_proposals/demo_proposal_v1.json",
        "predicate": "demo_oracle/3",
        "status": "complete",
        "source_only_review": True,
        "reviewer_blind_to_model_outputs": True,
        "reviewer_read_model_outputs": False,
        "outputs": {
            "fda_warning_letter_domain_transfer_002": {
                "expected_fact_count": 1,
                "forbidden_fact_count": 1,
                "source_files": [SOURCE_FILE],
            }
        },
        **overrides,
    }
    _write(review / "manifest.json", json.dumps(payload, indent=2))
    _write(
        review / "fda_warning_letter_domain_transfer_002" / "expected_facts.pl",
        "demo_oracle(Row, alpha, Src).\n",
    )
    _write(
        review / "fda_warning_letter_domain_transfer_002" / "forbidden_facts.pl",
        "demo_oracle(_, forbidden_value, _).\n",
    )
    _write(review / "review_notes.md", "Source-only notes.\n")
    return review


def test_source_oracle_review_audit_accepts_complete_source_only_review(tmp_path: Path) -> None:
    review = _review_dir(tmp_path)

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["output_count"] == 1
    rendered = render_markdown(report)
    assert "source-only expected/forbidden oracle packages" in rendered
    assert "demo_oracle/3" in rendered


def test_source_oracle_review_audit_blocks_non_blind_review(tmp_path: Path) -> None:
    review = _review_dir(tmp_path, reviewer_blind_to_model_outputs=False)

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "reviewer_not_declared_blind_to_model_outputs" in report["reviews"][0]["errors"]


def test_source_oracle_review_audit_blocks_model_output_exposure(tmp_path: Path) -> None:
    review = _review_dir(tmp_path, reviewer_read_model_outputs=True)

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "reviewer_model_output_exposure_not_false" in report["reviews"][0]["errors"]


def test_source_oracle_review_audit_blocks_fact_predicate_mismatch(tmp_path: Path) -> None:
    review = _review_dir(tmp_path)
    _write(
        review / "fda_warning_letter_domain_transfer_002" / "expected_facts.pl",
        "other_oracle(Row, alpha, Src).\n",
    )

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    output_errors = report["reviews"][0]["outputs"][0]["errors"]
    assert "expected_facts.pl:line_1:predicate_mismatch:other_oracle" in output_errors


def test_source_oracle_review_audit_blocks_fact_arity_mismatch(tmp_path: Path) -> None:
    review = _review_dir(tmp_path)
    _write(
        review / "fda_warning_letter_domain_transfer_002" / "forbidden_facts.pl",
        "demo_oracle(_, forbidden_value).\n",
    )

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    output_errors = report["reviews"][0]["outputs"][0]["errors"]
    assert "forbidden_facts.pl:line_1:arity_mismatch:2" in output_errors


def test_source_oracle_review_audit_blocks_count_mismatch(tmp_path: Path) -> None:
    review = _review_dir(tmp_path)
    manifest = json.loads((review / "manifest.json").read_text(encoding="utf-8"))
    manifest["outputs"]["fda_warning_letter_domain_transfer_002"]["expected_fact_count"] = 2
    _write(review / "manifest.json", json.dumps(manifest, indent=2))

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    output_errors = report["reviews"][0]["outputs"][0]["errors"]
    assert "expected_fact_count_mismatch:2!=1" in output_errors


def test_source_oracle_review_audit_blocks_unexpected_retained_source(tmp_path: Path) -> None:
    review = _review_dir(tmp_path)
    _write(review / "fda_warning_letter_domain_transfer_002" / "source.md", "must not be retained\n")

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "unexpected_retained_file:fda_warning_letter_domain_transfer_002/source.md" in report["reviews"][0]["errors"]


def test_source_oracle_review_audit_accepts_blocked_review_without_facts(tmp_path: Path) -> None:
    review = _review_dir(
        tmp_path,
        status="blocked",
        blocked_reason="source packet missing required source files",
        outputs={},
    )
    fixture_dir = review / "fda_warning_letter_domain_transfer_002"
    for child in fixture_dir.iterdir():
        child.unlink()
    fixture_dir.rmdir()

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "pass"
    assert report["reviews"][0]["status"] == "blocked"


def test_source_oracle_review_audit_expect_md_marks_stale_report(tmp_path: Path, monkeypatch) -> None:
    review = _review_dir(tmp_path / "reviews")
    expected = tmp_path / "status.md"
    expected.write_text("stale\n", encoding="utf-8")
    monkeypatch.chdir(Path(__file__).resolve().parents[1])

    import sys

    old_argv = sys.argv
    sys.argv = [
        "audit_source_oracle_reviews.py",
        "--review",
        str(review / "manifest.json"),
        "--expect-md",
        str(expected),
        "--out-md",
        str(tmp_path / "fresh.md"),
    ]
    try:
        result = main()
    finally:
        sys.argv = old_argv

    assert result == 1
