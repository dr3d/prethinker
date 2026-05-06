import json
from pathlib import Path

from scripts.rollup_domain_bootstrap_qa_scorecard import (
    build_scorecard,
    render_markdown,
    summarize_qa_artifact,
)


def _write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_summarize_qa_artifact_counts_judges_and_failures(tmp_path: Path) -> None:
    path = _write_json(
        tmp_path / "qa.json",
        {
            "qa_file": "datasets/story_worlds/demo/qa.md",
            "model": "qwen/test",
            "summary": {
                "question_count": 3,
                "runtime_load_error_count": 0,
                "write_proposal_rows": 0,
            },
            "rows": [
                {"id": "q001", "utterance": "A?", "reference_judge": {"verdict": "exact"}},
                {
                    "id": "q002",
                    "utterance": "B?",
                    "queries": ["p(X)."],
                    "reference_judge": {"verdict": "partial"},
                    "failure_surface": {"surface": "compile_surface_gap"},
                },
                {
                    "id": "q003",
                    "utterance": "C?",
                    "reference_judge": {"verdict": "miss"},
                    "failure_surface": {"surface": "query_surface_gap"},
                },
            ],
        },
    )

    summary = summarize_qa_artifact(path)

    assert summary["label"] == "demo"
    assert summary["question_count"] == 3
    assert summary["judge_counts"] == {"exact": 1, "miss": 1, "partial": 1}
    assert summary["failure_surface_counts"] == {"compile_surface_gap": 1, "query_surface_gap": 1}
    assert [row["id"] for row in summary["non_exact_rows"]] == ["q002", "q003"]


def test_build_scorecard_rolls_up_multiple_artifacts() -> None:
    scorecard = build_scorecard(
        [
            {
                "label": "a",
                "question_count": 2,
                "judge_counts": {"exact": 1, "partial": 1},
                "failure_surface_counts": {"compile_surface_gap": 1},
                "runtime_load_error_count": 0,
                "write_proposal_rows": 0,
            },
            {
                "label": "b",
                "question_count": 2,
                "judge_counts": {"exact": 1, "miss": 1},
                "failure_surface_counts": {"hybrid_join_gap": 1},
                "runtime_load_error_count": 1,
                "write_proposal_rows": 0,
            },
        ]
    )

    assert scorecard["summary"]["artifact_count"] == 2
    assert scorecard["summary"]["question_count"] == 4
    assert scorecard["summary"]["exact_rows"] == 2
    assert scorecard["summary"]["partial_rows"] == 1
    assert scorecard["summary"]["miss_rows"] == 1
    assert scorecard["summary"]["exact_rate"] == 0.5
    assert scorecard["summary"]["runtime_load_error_count"] == 1


def test_render_markdown_lists_fixture_rows() -> None:
    scorecard = build_scorecard(
        [
            {
                "label": "demo",
                "question_count": 1,
                "judge_counts": {"exact": 1},
                "failure_surface_counts": {"not_applicable": 1},
                "runtime_load_error_count": 0,
                "write_proposal_rows": 0,
            }
        ]
    )

    markdown = render_markdown(scorecard)

    assert "# Domain Bootstrap QA Scorecard" in markdown
    assert "| `demo` | 1 | 1 | 0 | 0" in markdown
