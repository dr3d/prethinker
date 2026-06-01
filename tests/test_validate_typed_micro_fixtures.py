import json
from pathlib import Path

from scripts.audit_kb_atom_inventory import build_report as build_atom_inventory_report
from scripts.validate_typed_micro_fixtures import DEFAULT_ROOT, build_report


def test_builtin_typed_micro_fixtures_are_structurally_valid() -> None:
    report = build_report(root=DEFAULT_ROOT)

    assert report["summary"]["fixture_count"] >= 2
    assert report["summary"]["blocking_errors"] == 0
    fixture_ids = {row["fixture_id"] for row in report["rows"]}
    assert "numbered_inventory_segments_v1" in fixture_ids
    assert "claim_ground_set_relation_v1" in fixture_ids
    assert "party_role_context_v1" in fixture_ids
    assert "fda_warning_letter_domain_v1" in fixture_ids


def test_typed_micro_fixture_compile_comparison_reports_missing_facts(tmp_path: Path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        json.dumps(
            {
                "source_compile": {
                        "facts": [
                        "list_member(count_set_1, 2, count, src_line_0003).",
                        "item_range(count_set_1, 4, 6, src_line_0003).",
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    report = build_report(
        root=DEFAULT_ROOT,
        compile_map={"numbered_inventory_segments_v1": compile_json},
    )

    row = next(row for row in report["rows"] if row["fixture_id"] == "numbered_inventory_segments_v1")
    assert row["compile_result"]["matched_fact_count"] == 2
    assert row["compile_result"]["variable_bindings"] == {"Set": "count_set_1"}
    assert row["compile_result"]["missing_expected_facts"] == [
        "list_member(Set, 9, count, src_line_0003)."
    ]
    assert "compile_missing_expected_facts" in row["errors"]


def test_typed_micro_fixture_compile_comparison_reports_forbidden_range_expansion(tmp_path: Path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "list_member(count_set_1, 2, count, src_line_0003).",
                        "item_range(count_set_1, 4, 6, src_line_0003).",
                        "list_member(count_set_1, 9, count, src_line_0003).",
                        "list_member(count_set_1, 5, count, src_line_0003).",
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    report = build_report(
        root=DEFAULT_ROOT,
        compile_map={"numbered_inventory_segments_v1": compile_json},
    )

    row = next(row for row in report["rows"] if row["fixture_id"] == "numbered_inventory_segments_v1")
    assert row["compile_result"]["matched_fact_count"] == 3
    assert row["compile_result"]["matched_forbidden_facts"] == [
        "list_member(count_set_1, 5, count, src_line_0003)."
    ]
    assert "compile_emitted_forbidden_facts" in row["errors"]


def test_typed_micro_fixture_accepts_declared_alternative_groups(tmp_path: Path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "list_member(claim_set_1, 1, claim, src_line_0003).",
                        "claim_range(claim_set_1, 3, 5, src_line_0003).",
                        "list_member(claim_set_1, 8, claim, src_line_0003).",
                        "claim_ground(claim_set_1, anticipation, reference_alpha, rejected).",
                        "review_outcome(claim_set_1, board, affirmed, src_line_0003).",
                        "legal_citation_detail(claim_set_1, section_102, statutory_ground, src_line_0003).",
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    report = build_report(
        root=DEFAULT_ROOT,
        compile_map={"claim_ground_set_relation_v1": compile_json},
    )

    row = next(row for row in report["rows"] if row["fixture_id"] == "claim_ground_set_relation_v1")
    assert row["compile_result"]["matched_fact_count"] == 4
    assert row["compile_result"]["matched_alternative_group_count"] == 2
    assert row["compile_result"]["selected_alternatives"] == [
        {"group_id": "claim_1_singleton_membership", "alternative_id": "explicit_list_member"},
        {"group_id": "claim_8_singleton_membership", "alternative_id": "explicit_list_member"},
    ]
    assert row["compile_result"]["passed"] is True
    assert row["errors"] == []


def test_typed_micro_fixture_reports_missing_alternative_group(tmp_path: Path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "list_member(claim_set_1, 1, claim, src_line_0003).",
                        "claim_range(claim_set_1, 3, 5, src_line_0003).",
                        "claim_ground(claim_set_1, anticipation, reference_alpha, rejected).",
                        "review_outcome(claim_set_1, board, affirmed, src_line_0003).",
                        "legal_citation_detail(claim_set_1, section_102, statutory_ground, src_line_0003).",
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    report = build_report(
        root=DEFAULT_ROOT,
        compile_map={"claim_ground_set_relation_v1": compile_json},
    )

    row = next(row for row in report["rows"] if row["fixture_id"] == "claim_ground_set_relation_v1")
    assert row["compile_result"]["matched_fact_count"] == 4
    assert row["compile_result"]["matched_alternative_group_count"] == 1
    assert row["compile_result"]["missing_expected_alternatives"] == [
        "claim_8_singleton_membership"
    ]
    assert "compile_missing_expected_alternatives" in row["errors"]


def test_typed_micro_fixture_compile_matching_handles_duplicate_heavy_artifacts(tmp_path: Path) -> None:
    decoys = [
        f"claim_range(decoy_set_{index}, 1, 1, src_line_0003)."
        for index in range(80)
    ]
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        *decoys,
                        "claim_ground(claim_set_1, anticipation, reference_alpha, rejected).",
                        "review_outcome(claim_set_1, board, affirmed, src_line_0003).",
                        "legal_citation_detail(claim_set_1, section_102, statutory_ground, src_line_0003).",
                        "claim_range(claim_set_1, 3, 5, src_line_0003).",
                        "list_member(claim_set_1, 1, claim, src_line_0003).",
                        "list_member(claim_set_1, 8, claim, src_line_0003).",
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    report = build_report(
        root=DEFAULT_ROOT,
        compile_map={"claim_ground_set_relation_v1": compile_json},
    )

    row = next(row for row in report["rows"] if row["fixture_id"] == "claim_ground_set_relation_v1")
    assert row["compile_result"]["passed"] is True
    assert row["compile_result"]["matched_fact_count"] == 4
    assert row["compile_result"]["matched_alternative_group_count"] == 2


def test_fda_micro_expected_facts_are_atom_shape_clean(tmp_path: Path) -> None:
    fixture_id = "fda_warning_letter_domain_v1"
    expected_path = DEFAULT_ROOT / fixture_id / "expected_facts.pl"
    facts = [
        line.strip()
        for line in expected_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("%")
    ]
    compile_dir = tmp_path / fixture_id
    compile_dir.mkdir(parents=True)
    (compile_dir / "compile.json").write_text(
        json.dumps({"source_compile": {"facts": facts}}, indent=2),
        encoding="utf-8",
    )

    report = build_atom_inventory_report(
        compile_root=tmp_path,
        fixtures={fixture_id},
        include_source_record=False,
        include_prose_like=False,
    )

    assert report["summary"]["registered_signature_count"] > 0
    assert report["summary"]["registered_fact_count"] == len(facts)
    assert report["summary"]["unregistered_fact_count"] == 0
    assert report["atom_shape"]["status"] == "pass"
