import json
from pathlib import Path

from scripts.audit_compile_surface_stability import audit_paths


def _write_compile(path: Path, facts: list[str]) -> Path:
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "source_compile": {"facts": facts},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_compile_surface_stability_detects_parallel_assignment_drift(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_a" / "domain_bootstrap_file_a.json",
            [
                "task_assigned_to(task_alpha, person_one, 2026_01_01).",
                "task_description(task_alpha, first_task).",
                "task_description(task_beta, second_task).",
                "source_record_text_atom(src_0, person_one_was_assigned_to_first_task).",
                "source_record_text_atom(src_1, person_two_was_assigned_to_second_task).",
            ],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_a" / "domain_bootstrap_file_b.json",
        [
                "task_assigned_to(task_alpha, person_one, 2026_01_01).",
                "task_assigned_to(task_beta, person_two, 2026_01_02).",
                "task_description(task_alpha, first_task).",
                "task_description(task_beta, second_task).",
                "source_record_text_atom(src_0, person_one_was_assigned_to_first_task).",
                "source_record_text_atom(src_1, person_two_was_assigned_to_second_task).",
            ],
    )

    report = audit_paths([draw1, draw2])

    fixture = report["fixtures"][0]
    assert fixture["stable"] is False
    assert fixture["unstable_fact_count"] == 1
    assert fixture["predicate_drift"] == [
        {"predicate": "task_assigned_to", "counts": [1, 2], "min": 1, "max": 2, "delta": 1}
    ]
    surface_drift = {row["surface"]: row for row in fixture["surface_drift"]}
    assert surface_drift["assignment_binding_surface"] == {
        "surface": "assignment_binding_surface",
        "counts": [1, 2],
        "min": 1,
        "max": 2,
        "delta": 1,
    }
    first_contracts = {row["contract"]: row for row in fixture["draws"][0]["contracts"]}
    second_contracts = {row["contract"]: row for row in fixture["draws"][1]["contracts"]}
    assert first_contracts["parallel_assignment_event_preservation"]["status"] == "partial"
    assert second_contracts["parallel_assignment_event_preservation"]["status"] == "pass"
    assert report["summary"]["unstable_fixture_count"] == 1


def test_source_authority_contract_requires_shared_subject_and_recipient_slots(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_b" / "domain_bootstrap_file_a.json",
        [
            "access_authorized_to(item_a, reader_one, physical).",
            "access_source(item_a, reader_two, policy_a).",
            "court_order(order_1, 2026_01_01).",
            "source_record_text_atom(src_1, policy_authorized_access_for_item_a_party_reader_one).",
        ],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_b" / "domain_bootstrap_file_b.json",
        [
            "access_authorized_to(item_a, reader_one, physical).",
            "access_source(item_a, reader_one, policy_a).",
            "source_record_text_atom(src_1, policy_authorized_access_for_item_a_party_reader_one).",
        ],
    )

    report = audit_paths([draw1, draw2])

    fixture = report["fixtures"][0]
    first_contracts = {row["contract"]: row for row in fixture["draws"][0]["contracts"]}
    second_contracts = {row["contract"]: row for row in fixture["draws"][1]["contracts"]}
    assert first_contracts["source_authority_pair_preservation"]["status"] == "ledger_only"
    assert first_contracts["source_authority_pair_preservation"]["direct_complete_count"] == 0
    assert first_contracts["source_authority_pair_preservation"]["direct_partial_count"] == 2
    assert second_contracts["source_authority_pair_preservation"]["status"] == "pass"
    assert second_contracts["source_authority_pair_preservation"]["direct_complete_count"] == 1
