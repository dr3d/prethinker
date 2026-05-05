import json
from pathlib import Path

from scripts.plan_cross_fixture_repair_slices import build_report, classify_theme, render_markdown


def _write_targets(path: Path, targets: list[dict]) -> None:
    path.write_text(json.dumps({"targets": targets}), encoding="utf-8")


def test_classify_theme_prefers_acquisition_lens() -> None:
    assert (
        classify_theme(
            {
                "acquisition_lens": "authority_document_surface",
                "question": "Does this comply with the rule?",
                "queries": ["rule_text(x, Y)."],
            }
        )
        == "authority_document_control"
    )


def test_cross_fixture_repair_slices_require_transfer_shape(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    _write_targets(
        first,
        [
            {
                "fixture": "alpha",
                "id": "q001",
                "verdict": "miss",
                "failure_surface": "compile_surface_gap",
                "repair_lane": "scoped_source_surface_repair",
                "acquisition_lens": "temporal_deadline_surface",
                "question": "What was the deadline?",
                "queries": ["deadline(x, Y)."],
            },
            {
                "fixture": "alpha",
                "id": "q002",
                "verdict": "miss",
                "failure_surface": "compile_surface_gap",
                "repair_lane": "scoped_source_surface_repair",
                "acquisition_lens": "object_state_transition_surface",
                "question": "What condition is the device in?",
            },
        ],
    )
    _write_targets(
        second,
        [
            {
                "fixture": "beta",
                "id": "q003",
                "verdict": "partial",
                "failure_surface": "hybrid_join_gap",
                "repair_lane": "helper_or_query_join_repair",
                "question": "What was the permit status on May 1?",
                "queries": ["permit_status_at(p, may_1_2026, Status)."],
            }
        ],
    )

    report = build_report([first, second], min_fixtures=2)

    assert report["summary"]["recommended_slice_count"] == 1
    assert report["recommended_slices"][0]["theme"] == "temporal_status_deadline"
    assert report["recommended_slices"][0]["fixture_count"] == 2


def test_cross_fixture_repair_slices_markdown_renders(tmp_path: Path) -> None:
    targets = tmp_path / "targets.json"
    _write_targets(
        targets,
        [
            {
                "fixture": "alpha",
                "id": "q001",
                "verdict": "miss",
                "failure_surface": "compile_surface_gap",
                "repair_lane": "scoped_source_surface_repair",
                "question": "Who is the facilities director?",
            },
            {
                "fixture": "beta",
                "id": "q002",
                "verdict": "miss",
                "failure_surface": "compile_surface_gap",
                "repair_lane": "scoped_source_surface_repair",
                "question": "Who sits on the review panel?",
            },
        ],
    )
    report = build_report([targets], min_fixtures=2)
    markdown = render_markdown(report)

    assert "# Cross-Fixture Repair Slices" in markdown
    assert "`entity_role_identity`" in markdown
