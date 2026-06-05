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
    assert "source_only_expected_forbidden_oracle:tmp/example_domain_work_order.zip" in rendered
