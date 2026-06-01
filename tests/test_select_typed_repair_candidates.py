import json
from pathlib import Path

from scripts.select_typed_repair_candidates import build_report, render_markdown


def _write_qa(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"rows": rows}), encoding="utf-8")


def test_select_typed_repair_candidates_splits_query_and_compile_pressure(tmp_path: Path) -> None:
    qa_root = tmp_path / "qa"
    typed_path = tmp_path / "typed.json"
    _write_qa(
        qa_root / "fixture_a" / "qa.json",
        [
            {
                "id": "q001",
                "utterance": "Question one?",
                "reference_answer": "Alpha 42.",
                "reference_judge": {"verdict": "miss"},
                "failure_surface": {"surface": "query_surface_gap"},
            },
            {
                "id": "q002",
                "utterance": "Question two?",
                "reference_answer": "Beta.",
                "reference_judge": {"verdict": "partial"},
                "failure_surface": {"surface": "compile_surface_gap"},
            },
            {
                "id": "q003",
                "utterance": "Question three?",
                "reference_answer": "Gamma.",
                "reference_judge": {"verdict": "exact"},
                "failure_surface": {"surface": "not_applicable"},
            },
        ],
    )
    typed_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_a",
                        "id": "q001",
                        "answer_type": "identifier",
                        "typed_strict": {
                            "class": "likely_available",
                            "token_coverage": 1.0,
                            "missing_tokens": [],
                        },
                        "typed_registered": {
                            "class": "partial_available",
                            "token_coverage": 0.75,
                            "missing_tokens": ["alpha"],
                        },
                    },
                    {
                        "fixture": "fixture_a",
                        "id": "q002",
                        "answer_type": "date_or_event",
                        "typed_strict": {
                            "class": "not_available",
                            "token_coverage": 0.0,
                            "missing_tokens": ["beta"],
                        },
                        "typed_registered": {
                            "class": "not_available",
                            "token_coverage": 0.0,
                            "missing_tokens": ["beta"],
                        },
                    },
                    {
                        "fixture": "fixture_a",
                        "id": "q003",
                        "answer_type": "quantity_or_amount",
                        "typed_strict": {
                            "class": "likely_available",
                            "token_coverage": 1.0,
                            "missing_tokens": [],
                        },
                        "typed_registered": {
                            "class": "likely_available",
                            "token_coverage": 1.0,
                            "missing_tokens": [],
                        },
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_root=qa_root, typed_recall_json=typed_path)

    assert report["summary"]["row_count"] == 3
    assert report["summary"]["exact"] == 1
    assert report["summary"]["non_exact"] == 2
    assert report["query_join_candidate_count"] == 1
    assert report["query_join_candidates"][0]["id"] == "q001"
    assert report["compile_recall_pressure_count"] == 1
    assert report["compile_recall_pressure"][0]["id"] == "q002"
    assert "Query/Join Candidates" in render_markdown(report)
