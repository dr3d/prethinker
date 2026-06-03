import json
from pathlib import Path

from scripts.validate_domain_transfer_package import build_report


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _registry(path: Path) -> Path:
    signatures = [
        "fda_warning_letter/5",
        "fda_correspondence_party/5",
        "fda_inspection_event/6",
        "fda_cgmp_violation_item/5",
        "fda_violation/5",
        "fda_violation_citation/4",
        "fda_response_requirement/6",
        "fda_response_assessment/5",
        "fda_violation_detail/5",
    ]
    _write(
        path,
        json.dumps({"predicates": [{"signature": signature} for signature in signatures]}, indent=2),
    )
    return path


def test_domain_transfer_package_validation_passes_well_formed_package(tmp_path: Path) -> None:
    package = tmp_path / "fda_warning_letter_domain_transfer_001"
    _write(
        package / "manifest.json",
        json.dumps(
            {
                "fixture_id": package.name,
                "source": "source.md",
                "expected_facts": "expected_facts.pl",
                "forbidden_facts": "forbidden_facts.pl",
                "purpose": "Transfer test.",
            }
        ),
    )
    _write(
        package / "source.md",
        "Source URL: https://example.test/fda\nSource title: FDA Warning Letter\nAccessed: 2026-06-01\n\nBody.",
    )
    _write(package / "source_notes.md", "Why selected: unlike FDA transfer pressure.")
    _write(
        package / "expected_facts.pl",
        "\n".join(
            [
                "fda_warning_letter(Letter, office_x, firm_x, v_2026_01_01, SrcLetter).",
                "fda_correspondence_party(Letter, Party, recipient, firm_x, SrcRecipient).",
                "fda_inspection_event(Inspection, Facility, v_2025_01_01, v_2025_01_02, fda, SrcInspection).",
                "fda_cgmp_violation_item(Violation, Letter, violation_1, cfr_21_211_192, SrcBundle).",
                "fda_violation(Violation, Letter, violation_1, quality_unit_failure, SrcViolation).",
                "fda_violation_citation(Violation, cfr_21_211_192, cgmps_requirement, SrcCitation).",
                "fda_response_requirement(Letter, written_response, fifteen_working_days, fda, corrective_actions_and_documentation, SrcResponse).",
                "fda_response_assessment(Assessment, Violation, response_inadequate, corrective_action_evaluation, SrcAssessment).",
            ]
        ),
    )
    _write(
        package / "forbidden_facts.pl",
        "fda_violation(Violation, Letter, violation_1, paragraph_summary_as_category, SrcViolation).\n",
    )

    report = build_report(
        package_dir=package,
        profile_registry=_registry(tmp_path / "registry.json"),
        expected_min=8,
        expected_max=10,
    )

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["expected_fact_count"] == 8


def test_domain_transfer_package_validation_blocks_outside_registry_and_prose_expected(tmp_path: Path) -> None:
    package = tmp_path / "bad_package"
    _write(package / "manifest.json", json.dumps({"fixture_id": "other", "source": "source.md"}))
    _write(package / "source.md", "No source citation.")
    _write(package / "source_notes.md", "Notes.")
    _write(
        package / "expected_facts.pl",
        "made_up_fact(x).\n"
        "fda_violation_detail(V, affected_lot, this_atom_is_far_too_long_and_should_not_be_used_as_a_typed_value_because_it_reads_like_a_sentence_and_contains_many_words, role, src_line_1).\n",
    )
    _write(package / "forbidden_facts.pl", "made_up_fact(x).\n")

    report = build_report(
        package_dir=package,
        profile_registry=_registry(tmp_path / "registry.json"),
        expected_min=1,
        expected_max=10,
    )

    kinds = {row["kind"] for row in report["blockers"]}
    assert report["summary"]["status"] == "fail"
    assert "fixture_id_folder_mismatch" in kinds
    assert "source_missing_source_url" in kinds
    assert "expected_signature_outside_profile_registry" in kinds
    assert "expected_fact_atom_shape_blockers" in kinds
