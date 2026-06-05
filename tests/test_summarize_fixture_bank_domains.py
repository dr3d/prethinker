import json
from pathlib import Path

from scripts.summarize_fixture_bank_domains import build_report, render_markdown


def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_fixture_bank_inventory_uses_metadata_and_profile_selection(tmp_path):
    transfer_root = tmp_path / "datasets" / "real_world_transfer"
    profile_root = tmp_path / "datasets" / "domain_profiles"

    selected = transfer_root / "batch_a" / "sec_material_event_001"
    unselected = transfer_root / "batch_b" / "sec_material_event_002"
    other = transfer_root / "batch_b" / "puc_order_001"
    _write_json(
        selected / "metadata.json",
        {
            "fixture_id": "sec_material_event_001",
            "source_family": "sec",
            "language": "en",
            "question_count": 25,
            "public_source": True,
        },
    )
    _write_json(
        unselected / "metadata.json",
        {
            "fixture_id": "sec_material_event_002",
            "source_family": "sec",
            "language": "en",
            "question_count": 25,
            "public_source": True,
        },
    )
    _write_json(
        other / "metadata.json",
        {
            "fixture_id": "puc_order_001",
            "source_family": "puc",
            "language": "en",
            "question_count": 25,
            "public_source": True,
        },
    )
    (selected / "source.md").write_text("SOURCE PROSE MUST NOT APPEAR", encoding="utf-8")
    _write_json(
        profile_root / "sec_form_8k_v1" / "ontology_registry.json",
        {
            "fixture": "sec_form_8k_v1",
            "selection": {
                "mode": "fixture_bank_internal_pack",
                "source_families": [str(selected)],
            },
        },
    )

    report = build_report(transfer_root=transfer_root, profile_root=profile_root)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["fixture_count"] == 3
    sec = next(row for row in report["families"] if row["family_key"] == "sec")
    assert sec["fixture_count"] == 2
    assert sec["selected_profile_ids"] == ["sec_form_8k_v1"]
    selected_row = next(row for row in report["fixtures"] if row["fixture_id"] == "sec_material_event_001")
    unselected_row = next(row for row in report["fixtures"] if row["fixture_id"] == "sec_material_event_002")
    assert selected_row["selected_by_profiles"] == ["sec_form_8k_v1"]
    assert unselected_row["selected_by_profiles"] == []

    markdown = render_markdown(report)
    assert "SOURCE PROSE MUST NOT APPEAR" not in markdown
    assert "does not read source prose" in markdown


def test_fixture_bank_inventory_flags_unprofiled_multi_fixture_candidates(tmp_path):
    transfer_root = tmp_path / "datasets" / "real_world_transfer"
    profile_root = tmp_path / "datasets" / "domain_profiles"

    for suffix in ("001", "002"):
        _write_json(
            transfer_root / f"batch_{suffix}" / f"puc_order_{suffix}" / "metadata.json",
            {
                "fixture_id": f"puc_order_{suffix}",
                "source_family": "puc",
                "language": "en",
                "question_count": 25,
            },
        )
    _write_json(
        profile_root / "sec_form_8k_v1" / "ontology_registry.json",
        {"fixture": "sec_form_8k_v1", "selection": {"source_families": []}},
    )

    report = build_report(transfer_root=transfer_root, profile_root=profile_root)

    assert report["summary"]["candidate_unprofiled_family_count"] == 1
    assert report["summary"]["qa_bearing_candidate_unprofiled_family_count"] == 1
    puc = next(row for row in report["families"] if row["family_key"] == "puc")
    assert puc["status"] == "candidate_unprofiled"


def test_fixture_bank_inventory_separates_zero_question_control_duplicates(tmp_path: Path):
    transfer_root = tmp_path / "datasets" / "real_world_transfer"
    profile_root = tmp_path / "datasets" / "domain_profiles"

    for suffix in ("001", "002"):
        _write_json(
            transfer_root / f"control_{suffix}" / "public_order_low_001" / "metadata.json",
            {
                "fixture_id": "public_order_low_001",
                "source_family": "public_order_low_001",
                "language": "en",
                "question_count": 0,
            },
        )
    _write_json(
        profile_root / "sec_form_8k_v1" / "ontology_registry.json",
        {"fixture": "sec_form_8k_v1", "selection": {"source_families": []}},
    )

    report = build_report(transfer_root=transfer_root, profile_root=profile_root)
    markdown = render_markdown(report)

    assert report["summary"]["candidate_unprofiled_family_count"] == 1
    assert report["summary"]["qa_bearing_candidate_unprofiled_family_count"] == 0
    assert "QA-Bearing Unprofiled Multi-Fixture Families" in markdown
