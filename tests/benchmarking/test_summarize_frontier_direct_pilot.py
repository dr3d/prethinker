from __future__ import annotations

from scripts.benchmarking.summarize_frontier_direct_pilot import render_markdown, summarize


def test_summarize_reports_micro_and_macro_fixture_rates() -> None:
    rows = [
        _row("model-a", "short", "q001", "exact"),
        _row("model-a", "short", "q002", "miss"),
        _row("model-a", "long", "q001", "exact"),
        _row("model-a", "long", "q002", "exact"),
        _row("model-a", "long", "q003", "partial"),
        _row("model-a", "long", "q004", "not_judged"),
    ]

    summary = summarize(rows)
    model = summary["models"][0]

    assert model["micro"]["exact_rate_all"] == 0.5
    assert model["micro"]["exact_rate_judged"] == 0.6
    assert model["macro_fixture_exact_rate_judged"] == 0.5834
    assert len(model["fixtures"]) == 2


def test_summarize_question_variance_counts_mixed_runs() -> None:
    rows = [
        _row("model-a", "fixture", "q001", "exact"),
        _row("model-a", "fixture", "q001", "partial"),
        _row("model-a", "fixture", "q002", "miss"),
        _row("model-a", "fixture", "q002", "partial"),
        _row("model-a", "fixture", "q003", "exact"),
        _row("model-a", "fixture", "q003", "exact"),
    ]

    summary = summarize(rows)
    variance = summary["models"][0]["question_variance"]

    assert variance["questions"] == 3
    assert variance["stable_exact_questions"] == 1
    assert variance["stable_non_exact_questions"] == 1
    assert variance["mixed_verdict_questions"] == 1


def test_render_markdown_includes_model_summary() -> None:
    markdown = render_markdown(summarize([_row("model-a", "fixture", "q001", "exact")]))

    assert "# Frontier Direct Pilot Rollup" in markdown
    assert "`model-a`" in markdown
    assert "Macro Fixture Exact" in markdown


def _row(model: str, fixture: str, question_id: str, verdict: str) -> dict[str, object]:
    return {
        "model": model,
        "fixture": fixture,
        "bucket": "bucket",
        "category": "category",
        "question_id": question_id,
        "reference_judge": {"verdict": verdict},
    }
