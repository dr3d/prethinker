import json
from pathlib import Path

from scripts.audit_candidate_oracle_reviews import build_report, main, render_markdown


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _review_dir(root: Path, **overrides: object) -> Path:
    review = root / "demo_review"
    payload = {
        "review_id": "demo_review",
        "fixture_id": "demo_fixture",
        "predicate": "demo_candidate/3",
        "reviewer_blind_to_model_outputs": True,
        "reviewer_read_forbidden_inputs": False,
        "source_files": ["datasets/compile_micro_fixtures/fda_warning_letter_domain_transfer_002/source.md"],
        **overrides,
    }
    _write(review / "manifest.json", json.dumps(payload, indent=2))
    _write(review / "candidate_expected_facts.pl", "demo_candidate(Row, alpha, Src).\n")
    _write(review / "candidate_forbidden_facts.pl", "demo_candidate(_, forbidden_value, _).\n")
    _write(review / "README.md", "# Demo review\n")
    return review


def test_candidate_oracle_review_audit_accepts_blind_source_only_review(tmp_path: Path) -> None:
    review = _review_dir(tmp_path)

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "pass"
    row = report["reviews"][0]
    assert row["expected_fact_count"] == 1
    assert row["forbidden_fact_count"] == 1
    rendered = render_markdown(report)
    assert "does not read source prose" in rendered
    assert "demo_candidate/3" in rendered


def test_candidate_oracle_review_audit_blocks_non_blind_review(tmp_path: Path) -> None:
    review = _review_dir(tmp_path, reviewer_blind_to_model_outputs=False)

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "reviewer_not_declared_blind_to_model_outputs" in report["reviews"][0]["errors"]


def test_candidate_oracle_review_audit_blocks_review_id_folder_mismatch(tmp_path: Path) -> None:
    review = _review_dir(tmp_path, review_id="different_review_id")

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "review_id_folder_mismatch:different_review_id!=demo_review" in report["reviews"][0]["errors"]


def test_candidate_oracle_review_audit_blocks_missing_source_reference(tmp_path: Path) -> None:
    review = _review_dir(tmp_path, source_files=["datasets/compile_micro_fixtures/missing/source.md"])

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "source_file_missing:datasets/compile_micro_fixtures/missing/source.md" in report["reviews"][0]["errors"]


def test_candidate_oracle_review_audit_blocks_non_dataset_source_reference(tmp_path: Path) -> None:
    review = _review_dir(tmp_path, source_files=["README.md"])

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "source_file_not_under_datasets:README.md" in report["reviews"][0]["errors"]


def test_candidate_oracle_review_audit_blocks_forbidden_input_exposure(tmp_path: Path) -> None:
    review = _review_dir(tmp_path, reviewer_read_forbidden_inputs=True)

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "reviewer_forbidden_input_exposure_not_false" in report["reviews"][0]["errors"]


def test_candidate_oracle_review_audit_blocks_fact_shape_mismatch(tmp_path: Path) -> None:
    review = _review_dir(tmp_path)
    _write(review / "candidate_forbidden_facts.pl", "other_candidate(_, forbidden_value, _).\n")

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "candidate_forbidden_facts.pl:line_1:predicate_mismatch:other_candidate" in report["reviews"][0]["errors"]


def test_candidate_oracle_review_audit_blocks_fact_arity_mismatch(tmp_path: Path) -> None:
    review = _review_dir(tmp_path)
    _write(review / "candidate_expected_facts.pl", "demo_candidate(Row, alpha).\n")

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "candidate_expected_facts.pl:line_1:arity_mismatch:2" in report["reviews"][0]["errors"]


def test_candidate_oracle_review_audit_blocks_unfilled_template_placeholder(tmp_path: Path) -> None:
    review = _review_dir(tmp_path, fixture_id="REPLACE_WITH_FIXTURE_ID")

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "manifest_placeholder:fixture_id" in report["reviews"][0]["errors"]


def test_candidate_oracle_review_audit_blocks_empty_review(tmp_path: Path) -> None:
    review = _review_dir(tmp_path)
    _write(review / "candidate_expected_facts.pl", "% RESULT: NO EXPECTED FACTS.\n")
    _write(review / "candidate_forbidden_facts.pl", "% RESULT: NO FORBIDDEN FACTS.\n")

    report = build_report([review / "manifest.json"])

    assert report["summary"]["status"] == "fail"
    assert "review_has_no_expected_or_forbidden_facts" in report["reviews"][0]["errors"]


def test_candidate_oracle_review_audit_expect_md_marks_stale_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    review = _review_dir(tmp_path / "reviews")
    expected = tmp_path / "status.md"
    expected.write_text("stale\n", encoding="utf-8")
    monkeypatch.chdir(Path(__file__).resolve().parents[1])

    # Exercise the CLI through argv because freshness is applied in main().
    import sys

    old_argv = sys.argv
    sys.argv = [
        "audit_candidate_oracle_reviews.py",
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
