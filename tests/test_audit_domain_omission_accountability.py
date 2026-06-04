import json
from pathlib import Path

from scripts.audit_domain_omission_accountability import build_report
from scripts.audit_domain_omission_accountability import _compile_paths


def _compile_payload(*, facts: list[str], notes: list[str]) -> dict:
    return {
        "parsed": {
            "candidate_predicates": [
                {"signature": "domain_omission/5", "args": ["domain", "carrier", "kind", "reason", "source"]}
            ]
        },
        "source_compile": {
            "facts": facts,
            "self_check": {"notes": notes},
        },
    }


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def test_domain_omission_accountability_flags_self_check_only_omission(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=["fda_correspondence_party(letter, party, recipient, firm, source_utterance)."],
            notes=["Signatory explicitly stated as absent; no domain_omission emitted."],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "self_check_omission_without_domain_omission_fact"


def test_domain_omission_accountability_discovers_nested_run_fixture_compile_jsons(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile"
    (compile_root / "run1_chronology").mkdir(parents=True)
    (compile_root / "run1_chronology" / "batch.json").write_text(
        json.dumps({"rows": [{"fixture": "fixture_a"}]}),
        encoding="utf-8",
    )
    compile_json = compile_root / "run1_chronology" / "fixture_a" / "run.json"
    _write(
        compile_json,
        {
            **_compile_payload(
                facts=[],
                notes=["Meeting explicitly not held; no domain_omission emitted."],
            ),
            "active_profile_registry_lens": {
                "allowed_signatures": [
                    "fda_regulatory_meeting/4",
                    "domain_omission/5",
                ],
                "accountability_requirement_count": 1,
            },
        },
    )

    paths = _compile_paths(compile_root=compile_root, compile_jsons=[], fixtures={"fixture_a"})
    report = build_report(paths)

    assert len(paths) == 1
    assert report["summary"]["blocker_count"] == 1
    assert report["rows"][0]["class"] == "self_check_omission_without_domain_omission_fact"


def test_domain_omission_accountability_passes_when_fact_exists(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(letter, 'fda_correspondence_party/5', role_missing, signatory_not_stated, source_utterance)."
            ],
            notes=["Signatory explicitly stated as absent."],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["blocker_count"] == 0


def test_domain_omission_accountability_blocks_invalid_carrier_signature(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(letter, fda_correspondence_party_5, role_missing, signatory_not_stated, source_utterance)."
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "invalid_domain_omission_carrier_signature"
    assert report["rows"][0]["carrier_signature"] == "fda_correspondence_party_5"


def test_domain_omission_accountability_blocks_unregistered_omission_kind_reason(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(blackstone_inc, 'sec_signatory/5', subject_missing, former_name_address_not_applicable, src_line_1)."
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "invalid_domain_omission_registry_value"
    assert report["rows"][0]["carrier_signature"] == "sec_signatory/5"


def test_domain_omission_accountability_blocks_ordinary_placeholder_carrier(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "fda_correspondence_party(letter, not_stated, signatory, not_stated, source_utterance).",
                "domain_omission(letter, 'fda_correspondence_party/5', role_missing, signatory_not_stated, source_utterance).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "ordinary_carrier_omission_placeholder"
    assert report["rows"][0]["carrier_signature"] == "fda_correspondence_party/5"


def test_domain_omission_accountability_blocks_sec_signature_omission_contradiction(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "sec_signatory(filing_1, michael_s_chae, chief_financial_officer, v_2025_10_23, src_signature).",
                "domain_omission(filing_1, 'sec_signatory/5', role_missing, signature_block_not_stated, src_signature).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "domain_omission_contradicts_emitted_carrier"
    assert report["rows"][0]["carrier_signature"] == "sec_signatory/5"


def test_domain_omission_accountability_blocks_sec_dummy_signatory_with_omission(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "sec_signatory(filing_1, not_stated, not_stated, not_stated, src_signature).",
                "domain_omission(filing_1, 'sec_signatory/5', role_missing, signature_block_not_stated, src_signature).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "domain_omission_contradicts_emitted_carrier"
    assert report["rows"][0]["carrier_signature"] == "sec_signatory/5"
    assert report["rows"][0]["fact"].startswith("sec_signatory(")


def test_domain_omission_accountability_blocks_osha_accident_omission_contradiction(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(accident_yarmouth_2025_11, 'osha_accident/7', none_found, accident_summary_not_stated, direct).",
                "osha_accident(accident_yarmouth_2025_11, inspection_1, accident_summary_yarmouth_2025_11, v_2025_11_18, trench_collapse, 1, direct).",
                "osha_injured_employee(accident_yarmouth_2025_11, employee_1, not_stated, not_stated, fatality, construction_worker, direct).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["blocker_count"] == 2
    assert {row["class"] for row in report["rows"]} == {"domain_omission_contradicts_emitted_carrier"}
    assert {row["carrier_signature"] for row in report["rows"]} == {"osha_accident/7"}


def test_domain_omission_accountability_allows_osha_accident_omission_different_scope(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(accident_1, 'osha_accident/7', none_found, accident_summary_not_stated, source_inspection_detail).",
                "osha_accident(accident_1, inspection_1, accident_summary_1, v_2025_11_18, trench_collapse, 1, source_accident_report).",
                "osha_injured_employee(accident_1, employee_1, not_stated, not_stated, fatality, construction_worker, source_accident_report).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["blocker_count"] == 0


def test_domain_omission_accountability_blocks_ntsb_report_omission_contradiction(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(occurrence_1, 'ntsb_report/5', role_missing, report_identifier_not_stated, src_missing_report_id).",
                "ntsb_report(not_stated, preliminary_report, preliminary, v_2026_03_03, src_missing_report_id).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "domain_omission_contradicts_emitted_carrier"
    assert report["rows"][0]["carrier_signature"] == "ntsb_report/5"
    assert report["rows"][0]["fact"].startswith("ntsb_report(")


def test_domain_omission_accountability_blocks_ntsb_report_omission_when_real_report_exists(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(occurrence_1, 'ntsb_report/5', role_missing, report_identifier_not_stated, src_report).",
                "ntsb_report(hwym24fh001, final_report, final, v_2026_04_01, src_report).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "domain_omission_contradicts_emitted_carrier"
    assert report["rows"][0]["carrier_signature"] == "ntsb_report/5"
    assert report["rows"][0]["fact"].startswith("domain_omission(")


def test_domain_omission_accountability_allows_ntsb_report_omission_different_scope(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(occurrence_1, 'ntsb_report/5', role_missing, report_identifier_not_stated, src_missing_report_id).",
                "ntsb_report(report_123, final_report, final, v_2026_04_01, src_final_report).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["blocker_count"] == 0


def test_domain_omission_accountability_audits_union_artifact_with_omission_fact(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        {
            "parsed": {"candidate_predicates": [{"signature": "sec_signatory/5"}]},
            "source_compile": {
                "facts": [
                    "sec_signatory(filing_1, michael_s_chae, chief_financial_officer, v_2025_10_23, src_signature).",
                    "domain_omission(filing_1, 'sec_signatory/5', role_missing, signature_block_not_stated, src_signature).",
                ],
                "self_check": {},
            },
        },
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "domain_omission_contradicts_emitted_carrier"


def test_domain_omission_accountability_allows_fda_signatory_omission_with_recipient(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "fda_correspondence_party(letter, acme_inc, recipient, acme_inc, src_recipient).",
                "domain_omission(letter, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_omission).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"


def test_domain_omission_accountability_ignores_profiles_without_domain_omission(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        {
            "parsed": {"candidate_predicates": [{"signature": "fda_warning_letter/5"}]},
            "source_compile": {"facts": [], "self_check": {"notes": ["missing signatory"]}},
        },
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"


def test_domain_omission_accountability_respects_lens_without_accountability_requirements(tmp_path: Path) -> None:
    payload = _compile_payload(
        facts=["fda_violation(violation_1, letter_1, violation_1, quality_unit_failure, src_line_1)."],
        notes=["Signatory explicitly stated as absent; no domain_omission emitted because wrapper carrier is outside this lens."],
    )
    payload["active_profile_registry_lens"] = {
        "id": "violation",
        "allowed_signatures": [
            "fda_violation/5",
            "fda_violation_detail/5",
            "domain_omission/5",
        ],
        "accountability_requirement_count": 0,
    }
    compile_json = _write(tmp_path / "fixture" / "compile.json", payload)

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"


def test_domain_omission_accountability_enforces_lens_accountability_requirements(tmp_path: Path) -> None:
    payload = _compile_payload(
        facts=["fda_correspondence_party(letter, party, recipient, firm, src_line_1)."],
        notes=["Signatory explicitly stated as absent; no domain_omission emitted."],
    )
    payload["active_profile_registry_lens"] = {
        "id": "wrapper",
        "allowed_signatures": [
            "fda_correspondence_party/5",
            "domain_omission/5",
        ],
        "accountability_requirement_count": 1,
    }
    compile_json = _write(tmp_path / "fixture" / "compile.json", payload)

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "self_check_omission_without_domain_omission_fact"
