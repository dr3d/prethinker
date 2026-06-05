import copy
import json
from pathlib import Path

from scripts.validate_domain_predicate_proposals import TEMPLATE, build_report, render_markdown


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _valid_payload() -> dict:
    payload = copy.deepcopy(TEMPLATE)
    payload["proposal_id"] = "fda_warning_letter_new_compact_lane_v1"
    payload["domain_profile"] = "fda_warning_letter_v1"
    payload["candidate_signature"] = "fda_new_compact_lane/5"
    payload["lens_owner"] = "violation"
    payload["allowed_lenses"] = ["violation"]
    payload["positive_examples"] = [
        {
            "fixture_id": "fda_warning_letter_domain_v1",
            "fact": "fda_new_compact_lane(Subject, example_kind, example_value, stated, Src).",
        }
    ]
    payload["forbidden_examples"] = [
        {
            "fixture_id": "fda_warning_letter_domain_v1",
            "fact": "fda_new_compact_lane(Subject, full_source_sentence_blob, example_value, stated, Src).",
        }
    ]
    return payload


def test_domain_predicate_proposal_validator_accepts_governed_draft(tmp_path: Path) -> None:
    path = _write(tmp_path / "proposal.json", _valid_payload())

    report = build_report([path])

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["blocking_errors"] == 0
    assert report["proposals"][0]["warnings"] == ["candidate_signature_not_yet_registered"]


def test_domain_predicate_proposal_candidate_without_review_is_visible_warning(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["status"] = "candidate"
    path = _write(tmp_path / "proposal.json", payload)

    report = build_report([path])

    assert report["summary"]["warning_count"] == 2
    assert "candidate_has_no_review_results" in report["proposals"][0]["warnings"]


def test_domain_predicate_proposal_validator_blocks_missing_anti_leak_guard(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["anti_leak_guards"] = ["no_source_prose"]
    path = _write(tmp_path / "proposal.json", payload)

    report = build_report([path])

    assert report["summary"]["status"] == "fail"
    assert any(error.startswith("missing_anti_leak_guards:") for error in report["proposals"][0]["errors"])


def test_domain_predicate_proposal_validator_blocks_prose_shaped_slot(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["argument_roles"][2]["name"] = "source_excerpt"
    path = _write(tmp_path / "proposal.json", payload)

    report = build_report([path])

    assert report["summary"]["status"] == "fail"
    assert "argument_role_source_excerpt:prose_shaped_slot_name" in report["proposals"][0]["errors"]


def test_domain_predicate_proposal_validator_blocks_weak_transfer_plan(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["unlike_transfer_plan"]["n"] = 1
    payload["unlike_transfer_plan"]["support_threshold"] = 1
    path = _write(tmp_path / "proposal.json", payload)

    report = build_report([path])

    assert report["summary"]["status"] == "fail"
    assert "unlike_transfer_plan_n_lt_3" in report["proposals"][0]["errors"]
    assert "unlike_transfer_plan_support_threshold_lt_2" in report["proposals"][0]["errors"]


def test_promoted_domain_predicate_proposal_must_be_registered_and_lens_allowed(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["status"] = "promoted"
    path = _write(tmp_path / "proposal.json", payload)

    report = build_report([path])

    assert report["summary"]["status"] == "fail"
    assert "promoted_signature_not_registered" in report["proposals"][0]["errors"]
    assert "promoted_signature_not_in_domain_profile" in report["proposals"][0]["errors"]
    assert "promoted_signature_not_in_lens_owner_allowlist" in report["proposals"][0]["errors"]
    assert "promoted_requires_review_results" in report["proposals"][0]["errors"]


def test_blocked_review_requires_rejected_status(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["review_results"] = [
        {
            "fixture_id": "fda_warning_letter_domain_transfer_002",
            "result": "blocked_forbidden",
        }
    ]
    path = _write(tmp_path / "proposal.json", payload)

    report = build_report([path])

    assert report["summary"]["status"] == "fail"
    assert "blocked_review_requires_rejected_status" in report["proposals"][0]["errors"]


def test_rejected_blocked_review_does_not_warn_about_unregistered_signature(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["status"] = "rejected"
    payload["review_results"] = [
        {
            "fixture_id": "fda_warning_letter_domain_transfer_002",
            "result": "blocked_forbidden",
        }
    ]
    path = _write(tmp_path / "proposal.json", payload)

    report = build_report([path])

    assert report["summary"]["status"] == "pass"
    assert report["proposals"][0]["errors"] == []
    assert report["proposals"][0]["warnings"] == []


def test_retained_review_for_signature_must_be_linked_from_proposal(tmp_path: Path) -> None:
    payload = _valid_payload()
    proposal = _write(tmp_path / "proposal.json", payload)
    review_root = tmp_path / "reviews"
    _write(
        review_root / "demo_review" / "manifest.json",
        {
            "review_id": "demo_review",
            "fixture_id": "fda_warning_letter_domain_transfer_002",
            "predicate": payload["candidate_signature"],
            "reviewer_blind_to_model_outputs": True,
            "reviewer_read_forbidden_inputs": False,
            "source_files": ["fixtures/demo/source.md"],
        },
    )

    report = build_report([proposal], candidate_review_root=review_root)

    assert report["summary"]["status"] == "fail"
    assert "retained_review_missing_from_proposal:demo_review" in report["proposals"][0]["errors"]


def test_linked_review_path_must_match_signature_and_fixture(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["review_results"] = [
        {
            "review_id": "demo_review",
            "fixture_id": "wrong_fixture",
            "review_path": str(tmp_path / "reviews" / "demo_review" / "manifest.json"),
            "result": "oracle_supported",
        }
    ]
    proposal = _write(tmp_path / "proposal.json", payload)
    _write(
        tmp_path / "reviews" / "demo_review" / "manifest.json",
        {
            "review_id": "demo_review",
            "fixture_id": "right_fixture",
            "predicate": "other_candidate/3",
        },
    )

    report = build_report([proposal], candidate_review_root=tmp_path / "reviews")

    errors = report["proposals"][0]["errors"]
    assert "review_result_1:fixture_id_mismatch" in errors
    assert "review_result_1:predicate_mismatch" in errors


def test_linked_retained_review_passes_when_metadata_matches(tmp_path: Path) -> None:
    payload = _valid_payload()
    review_path = tmp_path / "reviews" / "demo_review" / "manifest.json"
    payload["review_results"] = [
        {
            "review_id": "demo_review",
            "fixture_id": "fda_warning_letter_domain_transfer_002",
            "review_path": str(review_path),
            "result": "oracle_supported",
        }
    ]
    proposal = _write(tmp_path / "proposal.json", payload)
    _write(
        review_path,
        {
            "review_id": "demo_review",
            "fixture_id": "fda_warning_letter_domain_transfer_002",
            "predicate": payload["candidate_signature"],
        },
    )
    (review_path.parent / "candidate_expected_facts.pl").write_text(
        "fda_new_compact_lane(subject, example_kind, example_value, stated, src_a).\n",
        encoding="utf-8",
    )
    (review_path.parent / "candidate_forbidden_facts.pl").write_text(
        "fda_new_compact_lane(subject, example_kind, forbidden_value, stated, src_b).\n"
        "fda_new_compact_lane(subject, example_kind, prose_blob, stated, src_c).\n",
        encoding="utf-8",
    )

    report = build_report([proposal], candidate_review_root=tmp_path / "reviews")
    rendered = render_markdown(report)

    assert report["summary"]["status"] == "pass"
    assert report["proposals"][0]["errors"] == []
    assert report["proposals"][0]["review_results"][0]["expected_fact_count"] == 1
    assert report["proposals"][0]["review_results"][0]["forbidden_fact_count"] == 2
    assert "oracle_supported (expected 1, forbidden 2)" in rendered


def test_retained_source_oracle_review_for_proposal_must_be_linked(tmp_path: Path) -> None:
    payload = _valid_payload()
    proposal = _write(tmp_path / "proposal.json", payload)
    review_root = tmp_path / "source_reviews"
    _write(
        review_root / "demo_source_review" / "manifest.json",
        {
            "review_id": "demo_source_review",
            "proposal_id": payload["proposal_id"],
            "predicate": payload["candidate_signature"],
            "status": "complete",
        },
    )

    report = build_report([proposal], source_oracle_review_root=review_root)

    assert report["summary"]["status"] == "fail"
    assert (
        "retained_source_oracle_review_missing_from_proposal:demo_source_review"
        in report["proposals"][0]["errors"]
    )


def test_linked_source_oracle_review_path_must_match_proposal_and_signature(tmp_path: Path) -> None:
    payload = _valid_payload()
    review_path = tmp_path / "source_reviews" / "demo_source_review" / "manifest.json"
    payload["source_oracle_review_results"] = [
        {
            "review_id": "demo_source_review",
            "review_path": str(review_path),
            "result": "source_oracle_complete",
        }
    ]
    proposal = _write(tmp_path / "proposal.json", payload)
    _write(
        review_path,
        {
            "review_id": "demo_source_review",
            "proposal_id": "different_proposal",
            "predicate": "other_candidate/3",
            "status": "complete",
        },
    )

    report = build_report([proposal], source_oracle_review_root=tmp_path / "source_reviews")

    errors = report["proposals"][0]["errors"]
    assert "source_oracle_review_result_1:proposal_id_mismatch" in errors
    assert "source_oracle_review_result_1:predicate_mismatch" in errors


def test_linked_source_oracle_review_passes_when_metadata_matches(tmp_path: Path) -> None:
    payload = _valid_payload()
    review_path = tmp_path / "source_reviews" / "demo_source_review" / "manifest.json"
    payload["source_oracle_review_results"] = [
        {
            "review_id": "demo_source_review",
            "review_path": str(review_path),
            "result": "source_oracle_complete",
        }
    ]
    proposal = _write(tmp_path / "proposal.json", payload)
    _write(
        review_path,
        {
            "review_id": "demo_source_review",
            "proposal_id": payload["proposal_id"],
            "predicate": payload["candidate_signature"],
            "status": "complete",
            "outputs": {
                "demo_fixture_001": {
                    "expected_fact_count": 2,
                    "forbidden_fact_count": 3,
                },
                "demo_fixture_002": {
                    "expected_fact_count": 1,
                    "forbidden_fact_count": 4,
                },
            },
        },
    )

    report = build_report([proposal], source_oracle_review_root=tmp_path / "source_reviews")
    rendered = render_markdown(report)

    assert report["summary"]["status"] == "pass"
    assert report["proposals"][0]["errors"] == []
    assert report["proposals"][0]["source_oracle_review_results"][0]["expected_fact_count"] == 3
    assert report["proposals"][0]["source_oracle_review_results"][0]["forbidden_fact_count"] == 7
    assert "source_oracle_complete (expected 3, forbidden 7)" in rendered


def test_blocked_source_oracle_review_requires_rejected_status(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["source_oracle_review_results"] = [
        {
            "review_id": "demo_source_review",
            "result": "blocked_source_packet",
        }
    ]
    path = _write(tmp_path / "proposal.json", payload)

    report = build_report([path])

    assert report["summary"]["status"] == "fail"
    assert "blocked_source_oracle_review_requires_rejected_status" in report["proposals"][0]["errors"]


def test_linked_blocked_source_oracle_manifest_requires_blocked_result(tmp_path: Path) -> None:
    payload = _valid_payload()
    review_path = tmp_path / "source_reviews" / "demo_source_review" / "manifest.json"
    payload["source_oracle_review_results"] = [
        {
            "review_id": "demo_source_review",
            "review_path": str(review_path),
            "result": "source_oracle_complete",
        }
    ]
    proposal = _write(tmp_path / "proposal.json", payload)
    _write(
        review_path,
        {
            "review_id": "demo_source_review",
            "proposal_id": payload["proposal_id"],
            "predicate": payload["candidate_signature"],
            "status": "blocked",
        },
    )

    report = build_report([proposal], source_oracle_review_root=tmp_path / "source_reviews")

    errors = report["proposals"][0]["errors"]
    assert "source_oracle_review_result_1:blocked_status_requires_blocked_result" in errors


def test_rejected_blocked_source_oracle_review_passes_when_linked(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["status"] = "rejected"
    review_path = tmp_path / "source_reviews" / "demo_source_review" / "manifest.json"
    payload["source_oracle_review_results"] = [
        {
            "review_id": "demo_source_review",
            "review_path": str(review_path),
            "result": "blocked_source_packet",
        }
    ]
    proposal = _write(tmp_path / "proposal.json", payload)
    _write(
        review_path,
        {
            "review_id": "demo_source_review",
            "proposal_id": payload["proposal_id"],
            "predicate": payload["candidate_signature"],
            "status": "blocked",
        },
    )

    report = build_report([proposal], source_oracle_review_root=tmp_path / "source_reviews")

    assert report["summary"]["status"] == "pass"
    assert report["proposals"][0]["errors"] == []


def test_domain_predicate_proposal_status_report_disclaims_promotion(tmp_path: Path) -> None:
    path = _write(tmp_path / "proposal.json", _valid_payload())
    report = build_report([path])

    rendered = render_markdown(report)

    assert "validates proposal shape only" in rendered
    assert "not a" in rendered
    assert "promoted domain-pack claim" in rendered


def test_domain_predicate_proposal_status_report_shows_pending_work_order(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["pending_external_work_orders"] = [
        {
            "kind": "source_only_expected_forbidden_oracle",
            "path": "tmp/example_domain_work_order.zip",
            "fixtures": ["example_transfer_v1"],
        }
    ]
    path = _write(tmp_path / "proposal.json", payload)
    report = build_report([path])

    rendered = render_markdown(report)

    assert "Pending Work" in rendered
    assert "Source Oracles" in rendered
    assert "source_only_expected_forbidden_oracle:tmp/example_domain_work_order.zip" in rendered
