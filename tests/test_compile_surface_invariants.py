import json
from pathlib import Path

from scripts.audit_compile_surface_invariants import audit_compile, summarize_reports


def _write_compile(path: Path, facts: list[str], candidate_predicates: list[str] | None = None) -> Path:
    path.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "parsed": {"candidate_predicates": candidate_predicates or []},
                "source_compile": {"facts": facts},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_audit_compile_surface_invariants_passes_direct_surfaces(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, section_8_2_inferences_not_available).",
            "source_record_text_atom(src_line_002, vendor_sentec_model_rh_220_plus_operator_r_kim).",
            "source_record_text_atom(src_line_003, procedure_qhp_04_requires_72_hours).",
            "source_record_text_atom(src_line_004, registrar_report_dated_2026_04_02_is_authority_for_item_access_status).",
            "section_title(section_8_2, inferences_not_available).",
            "sensor_info(hum_d_04, sentec, rh_220_plus).",
            "operator_note(r_kim, 2026_04_22_15_15, line_stopped).",
            "policy_rule(qhp_04, off_spec_material, held_for_72_hours).",
            "source_authority(report_2026_04_02, registrar, item_7, access_status).",
        ],
    )

    report = audit_compile(compile_json)

    statuses = {row["family"]: row["status"] for row in report["families"]}
    assert statuses["source_addressability_surface"] == "pass"
    assert statuses["object_device_surface"] == "pass"
    assert statuses["identity_role_surface"] == "pass"
    assert statuses["source_authority_surface"] == "pass"
    assert statuses["rule_policy_surface"] == "pass"


def test_audit_compile_surface_invariants_detects_candidate_only_surface(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        ["source_record_text_atom(src_line_001, registrar_beatrice_caulfield_compiled_register)."],
        candidate_predicates=["registrar_identity/2"],
    )

    report = audit_compile(compile_json)

    identity = next(row for row in report["families"] if row["family"] == "identity_role_surface")
    assert identity["status"] == "candidate_only"
    assert "registrar_or_recorder" in identity["missing_groups"]


def test_audit_compile_surface_invariants_detects_source_authority_ledger_only(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, court_order_document_dated_2026_04_02_is_authority_for_item_access_status).",
            "access_authorized_to(item_7, requester).",
        ],
    )

    report = audit_compile(compile_json)

    source_authority = next(row for row in report["families"] if row["family"] == "source_authority_surface")
    assert source_authority["status"] == "partial"
    assert "source_document_or_correspondence" in source_authority["missing_groups"]
    assert "authority_or_evidence_role" in source_authority["covered_groups"]


def test_audit_compile_surface_invariants_detects_answer_detail_ledger_only(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, application_pending_because_commitment_not_available_outside_scope).",
            "application_status(app_1, pending).",
        ],
    )

    report = audit_compile(compile_json)

    detail = next(row for row in report["families"] if row["family"] == "answer_detail_surface")
    assert detail["status"] == "partial"
    assert "detail_or_explanation" in detail["missing_groups"]
    assert "availability_or_scope" in detail["missing_groups"]
    assert "negative_or_exclusion_detail" in detail["missing_groups"]
    assert "commitment_or_future_action" in detail["covered_groups"]


def test_audit_compile_surface_invariants_detects_access_source_pair_gap(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "access_authorized_to(item_1, requester_a, physical).",
            "access_source(item_1, requester_a, order_7).",
            "access_authorized_to(item_2, requester_a, observation_only).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(row for row in report["relation_contracts"] if row["contract"] == "access_authority_source_pair")
    assert contract["status"] == "partial"
    assert contract["required_key_count"] == 2
    assert contract["companion_key_count"] == 1
    assert contract["missing_keys"] == [("item_2", "requester_a")]


def test_audit_compile_surface_invariants_passes_access_source_pair_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "access_authorized_to(item_1, requester_a, physical).",
            "access_source(item_1, requester_a, order_7).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(row for row in report["relation_contracts"] if row["contract"] == "access_authority_source_pair")
    assert contract["status"] == "pass"


def test_summarize_reports_counts_family_statuses(tmp_path: Path) -> None:
    first = audit_compile(
        _write_compile(
            tmp_path / "first.json",
            [
                "source_record_text_atom(src_line_001, sensor_vendor_model).",
                "sensor_info(s1, vendor_a, model_b).",
            ],
        )
    )
    second = audit_compile(
        _write_compile(
            tmp_path / "second.json",
            ["source_record_text_atom(src_line_001, sensor_vendor_model)."],
        )
    )

    summary = summarize_reports([first, second])

    assert summary["family_status_counts"]["object_device_surface"]["pass"] == 1
    assert summary["family_status_counts"]["object_device_surface"]["ledger_only"] == 1
