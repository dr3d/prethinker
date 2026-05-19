import json
from pathlib import Path

from scripts.audit_query_surface_residuals import audit_paths, render_markdown


def test_query_surface_residual_audit_counts_fallback_signals(tmp_path: Path) -> None:
    qa_json = tmp_path / "qa.json"
    qa_json.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "utterance": "What value is current?",
                        "reference_judge": {"verdict": "partial"},
                        "failure_surface": {"surface": "query_surface_gap"},
                        "query_results": [
                            {
                                "query": "record_state(Item, value).",
                                "result": {
                                    "reasoning_basis": {
                                        "note": (
                                            "placeholder query repair converted generic lowercase slot labels "
                                            "to Prolog variables after the original placeholder-like query returned no rows"
                                        ),
                                        "repairs": [{"index": 2, "from": "value", "to": "Value"}],
                                    }
                                },
                            },
                            {
                                "query": "record_state(Item, Relaxed2).",
                                "result": {
                                    "reasoning_basis": {
                                        "note": (
                                            "diagnostic relaxed query synthesized after an over-bound structured "
                                            "query returned no results"
                                        ),
                                        "original_query": "record_state(Item, current_value).",
                                    },
                                    "relaxed_constants": [{"index": 2, "value": "current_value"}],
                                },
                            },
                            {
                                "query": "source_record_text_atom(SourceRow, TextAtom).",
                                "result": {
                                    "reasoning_basis": {
                                        "validation": "source_text_contains_filter_repaired",
                                        "contains_needles": ["current_value"],
                                    }
                                },
                            },
                        ],
                    },
                    {
                        "id": "q002",
                        "reference_judge": {"verdict": "exact"},
                        "failure_surface": {"surface": "not_applicable"},
                    },
                    {
                        "id": "q003",
                        "reference_judge": {"verdict": "miss"},
                        "failure_surface": {"surface": "compile_surface_gap"},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    report = audit_paths([qa_json])

    assert report["residual_count"] == 1
    assert report["summary"]["rows_with_fallback_signal"] == 1
    assert report["summary"]["signal_class_counts"] == {
        "placeholder_repair_used": 1,
        "relaxed_overbound_used": 1,
        "source_text_filter_repaired": 1,
    }
    assert report["rows"][0]["signal_classes"] == [
        "placeholder_repair_used",
        "relaxed_overbound_used",
        "source_text_filter_repaired",
    ]
    markdown = render_markdown(report)
    assert "Query Surface Residual Audit" in markdown
    assert "placeholder_repair_used" in markdown
