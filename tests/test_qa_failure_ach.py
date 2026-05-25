import json

from src.qa_failure_ach import analyze_qa_failure_batch, analyze_qa_failure_row
from scripts.run_qa_failure_ach_probe import render_markdown


def _row(
    *,
    row_id: str = "q001",
    verdict: str = "miss",
    surface: str = "compile_surface_gap",
    status: str = "coverage_gap",
    question: str = "List every section heading.",
    query_results: list[dict] | None = None,
) -> dict:
    return {
        "id": row_id,
        "utterance": question,
        "reference_answer": "Reference.",
        "reference_judge": {"verdict": verdict, "concise_answer": "No support."},
        "failure_surface": {"surface": surface},
        "response_envelope": {"status": status, "failure_surface": surface},
        "query_results": query_results or [],
    }


def _query(predicate: str, *, rows: list[dict] | None = None, status: str = "success") -> dict:
    return {"result": {"predicate": predicate, "rows": rows or [], "status": status}}


def test_qa_failure_ach_routes_coverage_gap_to_compile_preservation() -> None:
    report = analyze_qa_failure_row(
        _row(
            query_results=[
                _query("source_record_text_atom", rows=[{"Row": "src_line_1"}]),
                _query("source_record_question_overlap_support", rows=[{"SupportClass": "deterministic-source-record-summary"}]),
            ]
        ),
        fixture="fda_ugly_001",
    )

    assert report["top_hypotheses"] == ["h_compile_preservation"]
    assert report["classifier_agreement"] == "agree"
    assert report["feature_summary"]["source_record_nonempty_count"] == 1
    assert report["feature_summary"]["support_surface_count"] == 1


def test_qa_failure_ach_routes_direct_rows_nonexact_to_join_or_query() -> None:
    report = analyze_qa_failure_row(
        _row(
            surface="hybrid_join_gap",
            status="not_established",
            question="What is the duration between the two dates?",
            query_results=[
                _query("document_date", rows=[{"Date": "2026_01_01"}]),
                _query("elapsed_days", rows=[]),
            ],
        ),
        fixture="fda_ugly_001",
    )

    assert "h_join_computation" in report["top_hypotheses"]


def test_qa_failure_ach_batch_reads_summary_artifacts(tmp_path) -> None:
    run = {
        "fixture": "fixture_a",
        "rows": [
            _row(row_id="q001"),
            _row(row_id="q002", verdict="exact", surface="not_applicable", status="established"),
        ],
    }
    run_path = tmp_path / "run.json"
    run_path.write_text(json.dumps(run), encoding="utf-8")
    summary = {
        "results": [
            {
                "fixture": "fixture_a",
                "qa_json": str(run_path),
                "summary": {"judge_exact": 1, "judge_partial": 0, "judge_miss": 1},
            }
        ]
    }

    report = analyze_qa_failure_batch(summary)

    assert report["summary"]["row_count"] == 1
    assert report["summary"]["top_hypothesis_counts"] == {"h_compile_preservation": 1}

    markdown = render_markdown({"generated_at": "now", "qa_summary": str(run_path), **report})
    assert "# QA Failure ACH Probe" in markdown
    assert "`fixture_a` `q001`" in markdown
