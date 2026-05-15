import json
from pathlib import Path

from scripts.audit_operational_lifecycle_palette import (
    audit_compile,
    detect_alias_splits,
    detect_phase_classification_missing,
    detect_supersession_target_collapse,
    fact_rows,
    identity_code,
)


def _compile(path: Path, facts: list[str]) -> Path:
    path.write_text(json.dumps({"parsed_ok": True, "source_compile": {"facts": facts}}), encoding="utf-8")
    return path


def test_identity_code_groups_prefixed_and_bare_record_ids() -> None:
    assert identity_code("gq_5") == "gq5"
    assert identity_code("queue_gq5") == "gq5"
    assert identity_code("hold_notice_h_2") == "h2"
    assert identity_code("on_2026_05_07") == ""


def test_detect_alias_split_from_direct_rows() -> None:
    rows = fact_rows(["status_at(gq_5, approved, d1).", "status_at(queue_gq5, approved_with_revision, d2)."])

    findings = detect_alias_splits(rows, [])

    assert findings
    assert findings[0]["class"] == "alias_split"
    assert findings[0]["code"] == "gq5"


def test_detect_supersession_target_collapse_to_resulting_status() -> None:
    rows = fact_rows(["status_superseded_by(approved_subject_to_payment, pending_payment)."])
    source = ["the_approval_was_superseded_by_hold_notice_h_2_and_returned_to_pending_payment_status"]

    findings = detect_supersession_target_collapse(rows, source)

    assert findings
    assert findings[0]["class"] == "supersession_target_collapse"


def test_supersession_target_plan_or_entry_is_not_status_collapse() -> None:
    rows = fact_rows(
        [
            "superseded_by(digitization_only_plan, approved_display_plan).",
            "entry_supersedes(approved_result_entry, pending_lab_receipt_note).",
            "supersedes(evt_reinstated_20260507, evt_denied_20260505).",
        ]
    )
    source = ["a_prior_digitization_only_plan_was_superseded_by_the_approved_display_plan"]

    findings = detect_supersession_target_collapse(rows, source)

    assert findings == []


def test_detect_missing_initial_status_phase() -> None:
    rows = fact_rows(["docket_final_status(ws_12, completed_below_threshold)."])
    source = ["field_collector_received_sample_and_filed_docket_ws_12_with_status_pending_lab_receipt"]

    findings = detect_phase_classification_missing(rows, source)

    assert findings
    assert findings[0]["class"] == "phase_classification_missing"
    assert findings[0]["phase"] == "initial"


def test_audit_compile_reports_expected_classes(tmp_path: Path) -> None:
    compile_json = _compile(
        tmp_path / "domain_bootstrap_file_test.json",
        [
            "source_record_text_atom(src_1, filed_queue_gq_5_with_status_pending_review).",
            "source_record_text_atom(src_2, current_status_is_approved_with_revised_budget).",
            "status_at(gq_5, approved_with_revised_budget, d2).",
            "status_at(queue_gq5, approved, d2).",
        ],
    )

    report = audit_compile(compile_json)

    assert report["finding_counts"]["alias_split"] == 1
