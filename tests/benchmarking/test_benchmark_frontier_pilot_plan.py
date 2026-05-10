from __future__ import annotations

import pytest

from scripts.benchmarking.plan_benchmark_frontier_pilot import _models, _select_fixtures


def test_select_default_pilot_fixtures_matches_fairness_buckets() -> None:
    fixture_rows = {
        slug: {
            "fixture": slug,
            "publication_status": "ready_with_scored_history",
            "source_file": "source.md",
            "question_file": "qa_questions.jsonl",
            "scoring_file": "oracle.jsonl",
            "question_count": 40,
            "oracle_count": 40,
            "path": f"datasets/story_worlds/{slug}",
        }
        for slug in (
            "fenmore_seedbank",
            "greywell_pipeline",
            "larkspur_clockwork_fair",
            "dream_library_index",
            "lantern_school_field_trip",
            "tournament_borrowed_names",
            "hospital_shift_exception_log",
            "estate_archive_access_dispute",
            "rule_activation_exception_matrix",
            "contradictory_evidence_packet",
        )
    }
    fixture_rows["fenmore_seedbank"]["oracle_count"] = 25
    fixture_rows["fenmore_seedbank"]["question_count"] = 25
    fixture_rows["greywell_pipeline"]["oracle_count"] = 25
    fixture_rows["greywell_pipeline"]["question_count"] = 25

    fixtures = _select_fixtures(fixture_rows, override=[], rows_per_fixture=40)

    assert len(fixtures) == 10
    assert sum(int(row["planned_rows"]) for row in fixtures) == 370
    assert fixtures[0]["bucket"] == "surgical"
    assert fixtures[-1]["bucket"] == "precision_batch"


def test_select_pilot_rejects_non_ready_fixture() -> None:
    fixture_rows = {
        "draft_fixture": {
            "fixture": "draft_fixture",
            "publication_status": "needs_scoring_oracle",
            "question_count": 40,
            "oracle_count": 0,
        }
    }

    with pytest.raises(ValueError, match="not publication-ready"):
        _select_fixtures(fixture_rows, override=["draft_fixture"], rows_per_fixture=40)


def test_models_use_verified_frontier_ids_by_default() -> None:
    models = _models([])

    assert [row["provider_family"] for row in models] == ["openai", "anthropic", "google"]
    assert [row["model_id"] for row in models] == [
        "openai/gpt-5.5",
        "anthropic/claude-opus-4.7",
        "google/gemini-3.1-pro-preview",
    ]


def test_models_accept_explicit_ids() -> None:
    models = _models(["provider/model-a", "provider/model-b"])

    assert [row["model_id"] for row in models] == ["provider/model-a", "provider/model-b"]
    assert models[0]["model_role"] == "frontier_model_01"
