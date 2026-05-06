import json

from scripts.compare_domain_bootstrap_compiles import (
    compare_to_baseline,
    render_markdown,
    summarize_compile,
    summarize_qa,
)


def _write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_summarize_compile_counts_source_surface_without_source_prose(tmp_path) -> None:
    path = _write_json(
        tmp_path / "compile.json",
        {
            "model": "qwen/test",
            "domain_hint": "seed ledger",
            "parsed_ok": True,
            "score": {"rough_score": 0.75},
            "parsed": {
                "candidate_predicates": [
                    {"signature": "accession_id/1"},
                    {"signature": "collector/2"},
                ],
                "repeated_structures": [
                    {"name": "accession_row", "record": "seed lot", "properties": ["id", "collector"]}
                ],
            },
            "source_compile": {
                "mode": "flat_plus_focused_source",
                "ok": True,
                "admitted_count": 3,
                "skipped_count": 1,
                "unique_fact_count": 3,
                "facts": [
                    "accession_id(fb_2026_001).",
                    "collector(fb_2026_001, dr_matsuda).",
                    "collector(fb_2026_002, ava_chen).",
                ],
                "rules": ["known_accession(X) :- accession_id(X)."],
                "queries": ["accession_id(X)."],
                "compile_health": {
                    "verdict": "healthy",
                    "recommendation": "continue",
                    "semantic_progress": {"zombie_risk": "low"},
                },
            },
        },
    )

    summary = summarize_compile(path, {"accession_id", "collector", "stored_in_vault"})

    assert summary["candidate_predicate_count"] == 2
    assert summary["repeated_structure_count"] == 1
    assert summary["compile_health_verdict"] == "healthy"
    assert summary["semantic_zombie_risk"] == "low"
    assert summary["fact_predicate_counts"] == {"accession_id": 1, "collector": 2}
    assert summary["focus_predicate_counts"] == {
        "accession_id": 1,
        "collector": 2,
        "stored_in_vault": 0,
    }


def test_compare_to_baseline_reports_predicate_and_count_deltas(tmp_path) -> None:
    baseline = {
        "path": str(tmp_path / "base.json"),
        "admitted_count": 2,
        "skipped_count": 0,
        "unique_fact_count": 2,
        "candidate_predicates": ["accession_id/1", "collector/2"],
        "fact_predicate_counts": {"accession_id": 2, "collector": 1},
        "focus_predicate_counts": {"accession_id": 2, "stored_in_vault": 0},
    }
    candidate = {
        "path": str(tmp_path / "candidate.json"),
        "admitted_count": 5,
        "skipped_count": 1,
        "unique_fact_count": 4,
        "candidate_predicates": ["accession_id/1", "stored_in_vault/2"],
        "fact_predicate_counts": {"accession_id": 4, "stored_in_vault": 4},
        "focus_predicate_counts": {"accession_id": 4, "stored_in_vault": 4},
    }

    delta = compare_to_baseline([baseline, candidate])[1]

    assert delta["admitted_delta"] == 3
    assert delta["skipped_delta"] == 1
    assert delta["unique_fact_delta"] == 2
    assert delta["candidate_predicates_added"] == ["stored_in_vault/2"]
    assert delta["candidate_predicates_removed"] == ["collector/2"]
    assert delta["fact_predicates_added"] == ["stored_in_vault"]
    assert delta["fact_predicates_removed"] == ["collector"]
    assert delta["focus_predicate_deltas"] == {"accession_id": 2, "stored_in_vault": 4}


def test_summarize_qa_reads_nested_summary_and_judge_verdicts(tmp_path) -> None:
    path = _write_json(
        tmp_path / "qa.json",
        {
            "summary": {
                "question_count": 3,
                "judge_exact": 1,
                "judge_partial": 1,
                "judge_miss": 1,
                "runtime_load_error_count": 0,
                "write_proposal_rows": 0,
                "failure_surface_counts": {"compile_surface_gap": 2, "not_applicable": 1},
            },
            "rows": [
                {"reference_judge": {"verdict": "exact"}},
                {"reference_judge": {"verdict": "partial"}},
                {"reference_judge": {"verdict": "miss"}},
            ],
        },
    )

    summary = summarize_qa(path)

    assert summary["question_count"] == 3
    assert summary["judge_exact"] == 1
    assert summary["failure_surface_counts"] == {"compile_surface_gap": 2, "not_applicable": 1}
    assert summary["row_labels"] == ["exact", "partial", "miss"]


def test_render_markdown_includes_focus_and_qa_sections(tmp_path) -> None:
    payload = {
        "focus_predicates": ["accession_id"],
        "compiles": [
            {
                "path": str(tmp_path / "base.json"),
                "admitted_count": 2,
                "skipped_count": 0,
                "unique_fact_count": 2,
                "candidate_predicate_count": 1,
                "repeated_structure_count": 0,
                "compile_health_verdict": "healthy",
                "compile_mode": "source",
                "focus_predicate_counts": {"accession_id": 2},
            },
            {
                "path": str(tmp_path / "candidate.json"),
                "admitted_count": 4,
                "skipped_count": 1,
                "unique_fact_count": 4,
                "candidate_predicate_count": 2,
                "repeated_structure_count": 0,
                "compile_health_verdict": "healthy",
                "compile_mode": "source",
                "focus_predicate_counts": {"accession_id": 4},
            },
        ],
        "comparisons": [
            {"path": str(tmp_path / "base.json")},
            {
                "path": str(tmp_path / "candidate.json"),
                "admitted_delta": 2,
                "skipped_delta": 1,
                "unique_fact_delta": 2,
                "candidate_predicates_added": ["stored_in_vault/2"],
                "candidate_predicates_removed": [],
                "fact_predicates_added": ["stored_in_vault"],
                "fact_predicates_removed": [],
                "focus_predicate_deltas": {"accession_id": 2},
            },
        ],
        "qa": [
            {
                "path": str(tmp_path / "qa.json"),
                "judge_exact": 1,
                "judge_partial": 1,
                "judge_miss": 1,
                "runtime_load_error_count": 0,
                "write_proposal_rows": 0,
            }
        ],
    }

    markdown = render_markdown(payload)

    assert "## Focus Predicate Counts" in markdown
    assert "## QA Summary" in markdown
    assert "admitted delta: `2`" in markdown
    assert "`qa.json` | 1 | 1 | 1" in markdown
