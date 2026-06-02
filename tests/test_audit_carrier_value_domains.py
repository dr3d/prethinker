import json
from pathlib import Path

from scripts.audit_carrier_value_domains import build_report


def _write_compile(path: Path, facts: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"source_compile": {"facts": facts}}, indent=2),
        encoding="utf-8",
    )
    return path


def test_carrier_value_domain_audit_passes_allowed_fda_values(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "fda" / "compile.json",
        [
            "fda_violation(v1, letter, violation_1, quality_unit_failure, src_line_1).",
            "fda_response_requirement(letter, written_response, fifteen_working_days, fda, corrective_actions_and_documentation, src_line_2).",
            "fda_conclusion_scope(letter, cited_violations_not_exhaustive, not_all_inclusive, src_line_3).",
            "domain_omission(letter, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_line_4).",
        ],
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["violation_count"] == 0
    assert report["summary"]["checked_slot_count"] >= 5


def test_carrier_value_domain_audit_discovers_nested_run_fixture_compile_jsons(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile"
    (compile_root / "run1_violation").mkdir(parents=True)
    (compile_root / "run1_violation" / "batch.json").write_text(
        json.dumps({"rows": [{"fixture": "fixture_a"}]}),
        encoding="utf-8",
    )
    _write_compile(
        compile_root / "run1_violation" / "fixture_a" / "run.json",
        ["fda_violation(v1, letter, violation_1, quality_unit_review_failure, src_line_1)."],
    )

    from scripts.audit_carrier_value_domains import _compile_paths

    paths = _compile_paths(compile_root=compile_root, compile_jsons=[], fixtures={"fixture_a"})
    report = build_report(paths)

    assert len(paths) == 1
    assert report["summary"]["status"] == "fail"
    assert report["violations"][0]["value"] == "quality_unit_review_failure"


def test_carrier_value_domain_audit_blocks_off_palette_fda_values(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "fda" / "compile.json",
        [
            "fda_violation(v1, letter, 1, quality_unit_review_failure, src_line_1).",
            "fda_violation_citation(v1, 21_cfr_211_192, governing_regulation, src_line_2).",
            "fda_conclusion_scope(letter, not_all_inclusive, not_intended_to_be_an_all_inclusive_list_of_violations, src_line_3).",
        ],
    )

    report = build_report([compile_json])
    violations = {(row["signature"], row["arg_name"], row["value"]) for row in report["violations"]}

    assert report["summary"]["status"] == "fail"
    assert ("fda_violation/5", "violation_category", "quality_unit_review_failure") in violations
    assert ("fda_violation_citation/4", "citation_role", "governing_regulation") in violations
    assert ("fda_conclusion_scope/4", "scope_kind", "not_all_inclusive") in violations
    assert (
        "fda_conclusion_scope/4",
        "scope_value",
        "not_intended_to_be_an_all_inclusive_list_of_violations",
    ) in violations


def test_carrier_value_domain_audit_blocks_citation_payload_in_source_scope(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "fda" / "compile.json",
        [
            "fda_consultant_recommendation(letter, qualified_cgmp_consultant, consultant_engagement, cfr_21_211_34).",
        ],
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["violation_count"] == 1
    assert report["violations"][0]["signature"] == "fda_consultant_recommendation/4"
    assert report["violations"][0]["arg_name"] == "source_or_scope"
    assert report["violations"][0]["issue"] == "citation_payload_in_source_or_scope"
