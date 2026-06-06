import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_fda_violation_alignment.py"


def _write_compile(path: Path, facts: list[str]) -> None:
    path.write_text(
        json.dumps(
            {
                "text_file": str(path.parent),
                "source_compile": {"facts": facts},
            }
        ),
        encoding="utf-8",
    )


def test_fda_violation_alignment_audit_flags_mismatch_and_merge(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_a" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_violation(violation_1, letter_1, violation_1, contamination_control, src_1).",
            "fda_violation_citation(violation_1, cfr_21_211_113_b, cgmps_requirement, src_2).",
            "fda_violation_citation(violation_1, cfr_21_211_192, cgmps_requirement, src_3).",
        ],
    )
    out_json = tmp_path / "audit.json"

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json), "--out-json", str(out_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(out_json.read_text(encoding="utf-8"))
    issues = {item["issue"] for item in report["findings"]}
    assert "merged_citation_category_families" in issues
    assert "category_citation_mismatch" in issues
    assert report["policy"]["mutates_facts"] is False
    assert report["policy"]["reads_source_prose"] is False


def test_fda_violation_alignment_audit_flags_unattached_citation(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_b" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_violation(violation_1, letter_1, violation_1, contamination_control, src_1).",
            "fda_violation_citation(violation_2, cfr_21_211_192, cgmps_requirement, src_2).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any(item["issue"] == "citation_without_matching_violation_id" for item in report["findings"])


def test_fda_violation_alignment_audit_flags_wrapper_id_as_numbered_key(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_key" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_violation(wl_715795, letter_1, violation_2, contamination_control, src_1).",
            "fda_violation_citation(wl_715795, cfr_21_211_113_b, cgmps_requirement, src_2).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    issues = {item["issue"] for item in report["findings"]}
    assert "violation_id_not_numbered_key" in issues
    assert "cgmps_citation_subject_not_numbered_key" in issues


def test_fda_violation_alignment_audit_flags_shared_id_across_numbers(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_shared" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_violation(wl_715795, letter_1, violation_2, contamination_control, src_1).",
            "fda_violation(wl_715795, letter_1, violation_4, investigation_failure, src_2).",
            "fda_violation_citation(wl_715795, cfr_21_211_113_b, cgmps_requirement, src_3).",
            "fda_violation_citation(wl_715795, cfr_21_211_192, cgmps_requirement, src_4).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    issues = {item["issue"] for item in report["findings"]}
    assert "duplicate_violation_id_multiple_numbers" in issues
    assert "violation_id_not_numbered_key" in issues


def test_fda_violation_alignment_audit_flags_fdca_authority_on_numbered_violation(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_authority" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_violation(violation_1, letter_1, violation_1, process_validation, src_1).",
            "fda_violation_citation(violation_1, fdca_501_a_2_b, adulteration_authority, src_2).",
            "fda_violation_citation(violation_1, cfr_21_211_100_a, cgmps_requirement, src_3).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any(
        item["issue"] == "adulteration_authority_attached_to_numbered_violation"
        for item in report["findings"]
    )


def test_fda_violation_alignment_expect_md_allows_recorded_boundary(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_expected_hold" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_violation(violation_1, letter_1, violation_1, process_validation, src_1).",
            "fda_violation_citation(violation_1, fdca_501_a_2_b, adulteration_authority, src_2).",
        ],
    )
    expected_md = tmp_path / "expected.md"

    first = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--compile-json",
            str(compile_json),
            "--out-md",
            str(expected_md),
            "--exit-zero",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert first.returncode == 0

    matched = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--compile-json",
            str(compile_json),
            "--expect-md",
            str(expected_md),
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert matched.returncode == 0

    expected_md.write_text("# stale\n", encoding="utf-8")
    mismatched = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--compile-json",
            str(compile_json),
            "--expect-md",
            str(expected_md),
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert mismatched.returncode == 1


def test_fda_violation_alignment_cli_collapses_duplicate_findings(tmp_path: Path) -> None:
    compile_paths = []
    for index in (1, 2):
        compile_json = tmp_path / "fixture_repeat" / f"compile_{index}.json"
        compile_json.parent.mkdir(exist_ok=True)
        _write_compile(
            compile_json,
            [
                "fda_violation_citation(violation_1, cfr_21_211_192, cgmps_requirement, src_1).",
            ],
        )
        compile_paths.append(compile_json)

    command = [sys.executable, str(SCRIPT)]
    for compile_path in compile_paths:
        command.extend(["--compile-json", str(compile_path)])
    result = subprocess.run(command, check=False, text=True, capture_output=True)

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["raw_finding_count"] == 2
    assert report["finding_count"] == 1
    assert report["findings"][0]["support_count"] == "2"


def test_fda_violation_alignment_audit_flags_reused_cgmp_citation(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_reused" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_violation(violation_1, letter_1, violation_1, contamination_control, src_1).",
            "fda_violation_citation(violation_1, cfr_21_211_113_b, cgmps_requirement, src_2).",
            "fda_violation(violation_3, letter_1, violation_3, contamination_control, src_3).",
            "fda_violation_citation(violation_3, cfr_21_211_113_b, cgmps_requirement, src_4).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any(
        item["issue"] == "cgmps_citation_reused_across_numbered_violations"
        for item in report["findings"]
    )


def test_fda_violation_alignment_audit_flags_malformed_cgmp_bundle(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_bundle" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_cgmp_violation_item(wl_715795, letter_1, violation_1, fdca_501_a_2_b, src_1).",
            "fda_cgmp_violation_item(violation_2, letter_1, violation_2, cfr_21_211_113_b, src_2).",
            "fda_cgmp_violation_item(violation_2, letter_1, violation_2, cfr_21_211_192, src_3).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    issues = {item["issue"] for item in report["findings"]}
    assert "cgmp_bundle_key_mismatch" in issues
    assert "cgmp_bundle_unmapped_citation" in issues
    assert "cgmp_bundle_ambiguous_citations" in issues


def test_fda_violation_alignment_audit_allows_context_dependent_cgmp_citation(
    tmp_path: Path,
) -> None:
    compile_json = tmp_path / "fixture_context_dependent" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_cgmp_violation_item(violation_1, letter_1, violation_1, cfr_21_211_42_c_10_v, src_1).",
            "fda_violation(violation_1, letter_1, violation_1, aseptic_processing, src_2).",
            "fda_violation_citation(violation_1, cfr_21_211_42_c_10_v, cgmps_requirement, src_3).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["finding_count"] == 0


def test_fda_violation_alignment_audit_flags_reused_cgmp_bundle_citation(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_bundle_reuse" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_cgmp_violation_item(violation_1, letter_1, violation_1, cfr_21_211_113_b, src_1).",
            "fda_cgmp_violation_item(violation_3, letter_1, violation_3, cfr_21_211_113_b, src_2).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any(
        item["issue"] == "cgmp_bundle_citation_reused_across_numbered_violations"
        for item in report["findings"]
    )


def test_fda_violation_alignment_audit_flags_sequence_not_starting_at_one(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_sequence" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_cgmp_violation_item(violation_2, letter_1, violation_2, cfr_21_211_113_b, src_1).",
            "fda_violation(violation_2, letter_1, violation_2, contamination_control, src_2).",
            "fda_violation_citation(violation_2, cfr_21_211_113_b, cgmps_requirement, src_3).",
            "fda_cgmp_violation_item(violation_3, letter_1, violation_3, cfr_21_211_192, src_4).",
            "fda_violation(violation_3, letter_1, violation_3, investigation_failure, src_5).",
            "fda_violation_citation(violation_3, cfr_21_211_192, cgmps_requirement, src_6).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any(
        item["issue"] == "numbered_violation_sequence_does_not_start_at_one"
        for item in report["findings"]
    )


def test_fda_violation_alignment_audit_flags_unattached_response_assessment(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_response" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_cgmp_violation_item(violation_1, letter_1, violation_1, cfr_21_211_113_b, src_1).",
            "fda_response_assessment(wl_assessment, wl_701889, response_inadequate, corrective_action_evaluation, src_2).",
            "fda_response_assessment(assessment_2, violation_2, response_inadequate, corrective_action_evaluation, src_3).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    issues = {item["issue"] for item in report["findings"]}
    assert "response_assessment_subject_not_numbered_key" in issues
    assert "response_assessment_without_matching_cgmp_bundle" in issues


def test_fda_violation_alignment_audit_passes_aligned_rows(tmp_path: Path) -> None:
    compile_json = tmp_path / "fixture_c" / "compile.json"
    compile_json.parent.mkdir()
    _write_compile(
        compile_json,
        [
            "fda_violation(violation_1, letter_1, violation_1, investigation_failure, src_1).",
            "fda_violation_citation(violation_1, cfr_21_211_192, cgmps_requirement, src_2).",
            "fda_cgmp_violation_item(violation_2, letter_1, violation_2, cfr_21_211_68_b, src_3).",
            "fda_violation(violation_2, letter_1, violation_2, data_integrity, src_4).",
            "fda_violation_citation(violation_2, cfr_21_211_68_b, cgmps_requirement, src_5).",
            "fda_cgmp_violation_item(violation_3, letter_1, violation_3, cfr_21_211_110_a, src_6).",
            "fda_violation(violation_3, letter_1, violation_3, process_validation, src_7).",
            "fda_violation_citation(violation_3, cfr_21_211_110_a, cgmps_requirement, src_8).",
            "fda_response_assessment(assessment_3, violation_3, response_inadequate, corrective_action_evaluation, src_9).",
        ],
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--compile-json", str(compile_json)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["finding_count"] == 0
