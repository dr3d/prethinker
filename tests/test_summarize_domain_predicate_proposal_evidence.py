import json
from pathlib import Path

from scripts.summarize_domain_predicate_proposal_evidence import build_report, render_markdown


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _compile(path: Path, facts: list[str]) -> Path:
    payload = {"source_compile": {"facts": facts}}
    return _write(path, json.dumps(payload, indent=2))


def _proposal(path: Path, *, signature: str = "demo_candidate/3") -> Path:
    payload = {
        "proposal_id": "demo_candidate_v1",
        "status": "candidate",
        "candidate_signature": signature,
    }
    return _write(path, json.dumps(payload, indent=2))


def test_proposal_evidence_marks_stable_unexpected_as_candidate_signal_not_score(tmp_path: Path) -> None:
    micro_root = tmp_path / "micro"
    fixture = micro_root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "other_fact(A, alpha).\n")
    _write(fixture / "forbidden_facts.pl", "")
    proposal = _proposal(tmp_path / "proposal.json")
    run1 = _compile(tmp_path / "run1" / "compile.json", ["demo_candidate(row_1, alpha, src_a)."])
    run2 = _compile(tmp_path / "run2" / "compile.json", ["demo_candidate(row_1, alpha, src_a)."])

    report = build_report(
        fixture_id="demo_fixture",
        proposal_paths=[proposal],
        micro_root=micro_root,
        compile_paths=[run1, run2],
        support_threshold=2,
        matcher="constant_slot",
    )

    row = report["proposals"][0]
    assert row["state"] == "candidate_signal_no_oracle"
    assert row["summary"]["expected_fact_count"] == 0
    assert row["supported_unexpected_examples"]
    rendered = render_markdown(report)
    assert "not score credit" in rendered
    assert "Supported unexpected facts require independent oracle review" in rendered


def test_proposal_evidence_blocks_when_no_proposal_files(tmp_path: Path) -> None:
    micro_root = tmp_path / "micro"
    fixture = micro_root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "")
    _write(fixture / "forbidden_facts.pl", "")
    run1 = _compile(tmp_path / "run1" / "compile.json", ["demo_candidate(row_1, alpha, src_a)."])

    report = build_report(
        fixture_id="demo_fixture",
        proposal_paths=[],
        micro_root=micro_root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
    )

    assert report["summary"]["status"] == "fail"
    assert report["errors"] == ["missing_proposal_files"]


def test_proposal_evidence_blocks_supported_forbidden_facts(tmp_path: Path) -> None:
    micro_root = tmp_path / "micro"
    fixture = micro_root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "")
    _write(fixture / "forbidden_facts.pl", "demo_candidate(_, forbidden_value, _).\n")
    proposal = _proposal(tmp_path / "proposal.json")
    run1 = _compile(tmp_path / "run1" / "compile.json", ["demo_candidate(row_1, forbidden_value, src_a)."])

    report = build_report(
        fixture_id="demo_fixture",
        proposal_paths=[proposal],
        micro_root=micro_root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
    )

    row = report["proposals"][0]
    assert row["state"] == "blocked_forbidden"
    assert row["supported_forbidden_examples"]


def test_candidate_review_forbidden_facts_block_prior_candidate_signal(tmp_path: Path) -> None:
    micro_root = tmp_path / "micro"
    fixture = micro_root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "")
    _write(fixture / "forbidden_facts.pl", "")
    proposal = _proposal(tmp_path / "proposal.json")
    run1 = _compile(tmp_path / "run1" / "compile.json", ["demo_candidate(row_1, forbidden_value, src_a)."])
    run2 = _compile(tmp_path / "run2" / "compile.json", ["demo_candidate(row_2, forbidden_value, src_b)."])
    review_dir = tmp_path / "reviews" / "demo_review"
    _write(
        review_dir / "manifest.json",
        json.dumps(
            {
                "review_id": "demo_review",
                "fixture_id": "demo_fixture",
                "predicate": "demo_candidate/3",
                "reviewer_blind_to_model_outputs": True,
                "reviewer_read_forbidden_inputs": False,
            },
            indent=2,
        ),
    )
    _write(review_dir / "candidate_expected_facts.pl", "")
    _write(review_dir / "candidate_forbidden_facts.pl", "demo_candidate(_, forbidden_value, _).\n")

    report = build_report(
        fixture_id="demo_fixture",
        proposal_paths=[proposal],
        micro_root=micro_root,
        compile_paths=[run1, run2],
        support_threshold=2,
        matcher="constant_slot",
        candidate_review_paths=[review_dir / "manifest.json"],
    )

    row = report["proposals"][0]
    assert row["state"] == "blocked_forbidden"
    assert row["summary"]["forbidden_fact_count"] == 1
    assert row["summary"]["supported_forbidden_fact_count"] == 1
    assert row["candidate_reviews"][0]["reviewer_blind_to_model_outputs"] is True


def test_proposal_evidence_reports_oracle_supported_when_expected_facts_match(tmp_path: Path) -> None:
    micro_root = tmp_path / "micro"
    fixture = micro_root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "demo_candidate(Item, alpha, Src).\n")
    _write(fixture / "forbidden_facts.pl", "")
    proposal = _proposal(tmp_path / "proposal.json")
    run1 = _compile(tmp_path / "run1" / "compile.json", ["demo_candidate(row_1, alpha, src_a)."])
    run2 = _compile(tmp_path / "run2" / "compile.json", ["demo_candidate(row_2, alpha, src_b)."])

    report = build_report(
        fixture_id="demo_fixture",
        proposal_paths=[proposal],
        micro_root=micro_root,
        compile_paths=[run1, run2],
        support_threshold=2,
        matcher="constant_slot",
    )

    row = report["proposals"][0]
    assert row["state"] == "oracle_supported"
    assert row["summary"]["supported_fact_count"] == 1
