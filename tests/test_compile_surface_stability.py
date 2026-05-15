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
    assert report["summary"]["unstable_fixture_count"] == 1
