import pytest

from src.ach_overlay import analyze_ach_overlay
from scripts.run_ach_overlay import build_report, render_markdown


def test_ach_ranks_by_least_inconsistency_not_most_support() -> None:
    report = analyze_ach_overlay(
        {
            "hypotheses": [
                {"id": "h_accident", "label": "Accidental failure"},
                {"id": "h_sabotage", "label": "Sabotage"},
            ],
            "evidence": [
                {"id": "e_alarm", "label": "Alarm was disabled", "diagnosticity": "low"},
                {"id": "e_lock", "label": "Lock was untouched", "diagnosticity": "critical"},
                {"id": "e_access", "label": "Access log matches staff", "diagnosticity": "low"},
            ],
            "judgments": [
                {"evidence_id": "e_alarm", "hypothesis_id": "h_accident", "assessment": "neutral"},
                {"evidence_id": "e_alarm", "hypothesis_id": "h_sabotage", "assessment": "consistent"},
                {"evidence_id": "e_lock", "hypothesis_id": "h_accident", "assessment": "consistent"},
                {"evidence_id": "e_lock", "hypothesis_id": "h_sabotage", "assessment": "inconsistent"},
                {"evidence_id": "e_access", "hypothesis_id": "h_accident", "assessment": "consistent"},
                {"evidence_id": "e_access", "hypothesis_id": "h_sabotage", "assessment": "consistent"},
            ],
        }
    )

    assert report["matrix_complete"] is True
    assert report["hypothesis_scores"][0]["hypothesis_id"] == "h_accident"
    assert report["hypothesis_scores"][0]["inconsistency_weight"] == 0
    assert report["hypothesis_scores"][1]["hypothesis_id"] == "h_sabotage"
    assert report["hypothesis_scores"][1]["inconsistency_weight"] == 5


def test_ach_reports_missing_matrix_cells() -> None:
    report = analyze_ach_overlay(
        {
            "hypotheses": [{"id": "h1"}, {"id": "h2"}],
            "evidence": [{"id": "e1"}],
            "judgments": [
                {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent"}
            ],
        }
    )

    assert report["matrix_complete"] is False
    assert report["matrix"]["e1"]["h2"]["assessment"] == "missing"
    assert report["warnings"] == [
        {"kind": "missing_judgments", "items": [{"evidence_id": "e1", "hypothesis_id": "h2"}]}
    ]


def test_ach_surfaces_diagnostic_and_sensitivity_evidence() -> None:
    report = analyze_ach_overlay(
        {
            "hypotheses": [{"id": "h1"}, {"id": "h2"}],
            "evidence": [{"id": "e1", "diagnosticity": "critical"}],
            "judgments": [
                {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent"},
                {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "inconsistent"},
            ],
        }
    )

    assert report["diagnostic_evidence"][0]["evidence_id"] == "e1"
    assert report["diagnostic_evidence"][0]["diagnostic_score"] == 10
    assert report["sensitivity"] == [
        {
            "evidence_id": "e1",
            "label": "e1",
            "baseline_top": ["h1"],
            "top_without_evidence": ["h1", "h2"],
            "reason": "top_hypothesis_set_changes_if_evidence_removed",
            "applied_omission_effect_count": 0,
        }
    ]


def test_ach_axis_fit_keeps_compatible_side_claim_from_winning() -> None:
    report = analyze_ach_overlay(
        {
            "hypotheses": [
                {"id": "h_cause", "axis_fit": "direct"},
                {"id": "h_scope", "axis_fit": "partial"},
            ],
            "evidence": [{"id": "e1"}, {"id": "e2"}],
            "judgments": [
                {"evidence_id": "e1", "hypothesis_id": "h_cause", "assessment": "consistent", "weight": 4},
                {"evidence_id": "e1", "hypothesis_id": "h_scope", "assessment": "consistent", "weight": 4},
                {"evidence_id": "e2", "hypothesis_id": "h_cause", "assessment": "neutral", "weight": 1},
                {"evidence_id": "e2", "hypothesis_id": "h_scope", "assessment": "consistent", "weight": 5},
            ],
        }
    )

    assert report["hypothesis_scores"][0]["hypothesis_id"] == "h_cause"
    assert report["hypothesis_scores"][0]["axis_fit_penalty"] == 0
    assert report["hypothesis_scores"][1]["axis_fit"] == "partial"


def test_ach_sensitivity_can_apply_omission_effects() -> None:
    report = analyze_ach_overlay(
        {
            "hypotheses": [{"id": "h1"}, {"id": "h2"}],
            "evidence": [{"id": "e1", "diagnosticity": "critical"}, {"id": "e2", "diagnosticity": "critical"}],
            "judgments": [
                {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent"},
                {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "inconsistent"},
                {"evidence_id": "e2", "hypothesis_id": "h1", "assessment": "consistent"},
                {"evidence_id": "e2", "hypothesis_id": "h2", "assessment": "consistent"},
            ],
            "omission_effects": [
                {
                    "omitted_evidence_id": "e1",
                    "evidence_id": "e2",
                    "hypothesis_id": "h1",
                    "assessment": "inconsistent",
                    "weight": 5,
                    "rationale": "Without e1, e2 no longer supports h1.",
                }
            ],
        }
    )

    assert report["hypothesis_scores"][0]["hypothesis_id"] == "h1"
    assert report["sensitivity"] == [
        {
            "evidence_id": "e1",
            "label": "e1",
            "baseline_top": ["h1"],
            "top_without_evidence": ["h2"],
            "reason": "top_hypothesis_set_changes_after_evidence_omission_effects",
            "applied_omission_effect_count": 1,
        }
    ]


def test_ach_sensitivity_surfaces_top_support_drop_from_row_dependency() -> None:
    report = analyze_ach_overlay(
        {
            "hypotheses": [{"id": "h1"}, {"id": "h2"}],
            "evidence": [{"id": "e1"}, {"id": "e2"}, {"id": "e3"}],
            "judgments": [
                {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent", "weight": 5},
                {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "neutral", "weight": 1},
                {"evidence_id": "e2", "hypothesis_id": "h1", "assessment": "consistent", "weight": 5},
                {"evidence_id": "e2", "hypothesis_id": "h2", "assessment": "neutral", "weight": 1},
                {"evidence_id": "e3", "hypothesis_id": "h1", "assessment": "consistent", "weight": 1},
                {"evidence_id": "e3", "hypothesis_id": "h2", "assessment": "inconsistent", "weight": 1},
            ],
            "omission_effects": [
                {
                    "omitted_evidence_id": "e1",
                    "evidence_id": "e2",
                    "hypothesis_id": "h2",
                    "assessment": "neutral",
                    "weight": 1,
                    "rationale": "row e2 depends on e1",
                }
            ],
        }
    )

    assert report["sensitivity"] == [
        {
            "evidence_id": "e1",
            "label": "e1",
            "baseline_top": ["h1"],
            "top_without_evidence": ["h1"],
            "reason": "top_hypothesis_support_drops_after_evidence_omission_effects",
            "applied_omission_effect_count": 1,
            "support_drop": 10,
            "support_drop_ratio": 0.9091,
        }
    ]


def test_ach_ignores_invalid_omission_effect_references() -> None:
    report = analyze_ach_overlay(
        {
            "hypotheses": [{"id": "h1"}, {"id": "h2"}],
            "evidence": [{"id": "e1"}],
            "judgments": [
                {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent"},
                {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "inconsistent"},
            ],
            "omission_effects": [
                {
                    "omitted_evidence_id": "missing",
                    "evidence_id": "e1",
                    "hypothesis_id": "h1",
                    "assessment": "inconsistent",
                    "weight": 3,
                    "rationale": "bad reference",
                }
            ],
        }
    )

    assert report["warnings"][0]["kind"] == "unknown_omission_effect_reference"


def test_ach_rejects_invalid_assessment() -> None:
    with pytest.raises(ValueError, match="invalid ACH assessment"):
        analyze_ach_overlay(
            {
                "hypotheses": [{"id": "h1"}],
                "evidence": [{"id": "e1"}],
                "judgments": [
                    {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "probably"}
                ],
            }
        )


def test_ach_runner_wraps_report_with_harness_summary() -> None:
    report = build_report(
        payload={
            "id": "demo",
            "hypotheses": [{"id": "h1"}, {"id": "h2"}],
            "evidence": [{"id": "e1", "diagnosticity": "critical"}],
            "judgments": [
                {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent"},
                {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "inconsistent"},
            ],
        }
    )

    assert report["schema_version"] == "ach_overlay_run_v1"
    assert report["summary"]["matrix_complete"] is True
    assert report["summary"]["top_hypotheses"] == ["h1"]
    assert report["ach_report"]["surviving_hypotheses"][0]["hypothesis_id"] == "h1"

    markdown = render_markdown(report)
    assert "# ACH Overlay Report" in markdown
    assert "| Rank | Hypothesis | Inconsistency | Consistency | Missing |" in markdown
    assert "`h1`" in markdown
