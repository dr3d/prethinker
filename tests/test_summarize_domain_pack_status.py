from pathlib import Path

from scripts.summarize_domain_pack_status import build_report, render_markdown


def test_domain_pack_status_summarizes_live_registries():
    report = build_report()

    assert report["summary"]["schema_status"] == "pass"
    assert report["summary"]["domain_count"] >= 3
    assert report["summary"]["predicate_count"] >= 40
    assert {row["profile_id"] for row in report["domains"]} >= {
        "fda_warning_letter_v1",
        "ntsb_investigation_v1",
        "sec_form_8k_v1",
    }


def test_domain_pack_status_recurses_nested_fixture_batches():
    report = build_report()
    fda = next(row for row in report["domains"] if row["profile_id"] == "fda_warning_letter_v1")
    fixture_ids = {fixture["fixture_id"] for fixture in fda["fixtures"]}

    assert "fda_warning_letter_observation_transfer_001" in fixture_ids
    assert "fda_warning_letter_observation_transfer_002" in fixture_ids
    assert "fda_warning_letter_observation_transfer_003" in fixture_ids


def test_domain_pack_status_keeps_generic_micro_fixtures_unassigned():
    report = build_report()
    unassigned = {fixture["fixture_id"] for fixture in report["unassigned_fixtures"]}

    assert "claim_ground_set_relation_v1" in unassigned
    assert "numbered_inventory_segments_v1" in unassigned
    assert report["summary"]["unassigned_unaccounted_count"] == 0
    assert all(fixture["ledger_status"] == "generic_method_probe" for fixture in report["unassigned_fixtures"])


def test_domain_pack_status_markdown_names_no_source_prose_boundary():
    report = build_report()
    markdown = render_markdown(report)

    assert "does not read source prose" in markdown
    assert "datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json" in markdown
    assert "C:\\prethinker" not in markdown
