import json
from pathlib import Path

from scripts.audit_hard_road_floor import build_report


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_hard_road_floor_requires_typed_redacted_and_atom_shape_clean(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile"
    compile_json = compile_root / "fixture_a" / "compile.json"
    _write_json(
        compile_json,
        {
            "source_compile": {
                "facts": [
                    "document_date(doc_a, issue_date, v_2026_05_30).",
                    "document_title(doc_a, this_title_is_a_complete_sentence_that_should_not_be_treated_as_a_compact_typed_atom_because_it_smuggles_source_text).",
                ]
            }
        },
    )
    qa_json = tmp_path / "qa" / "fixture_a" / "domain_bootstrap_qa.json"
    _write_json(
        qa_json,
        {
            "run_json": str(compile_json),
            "rows": [
                {
                    "id": "q001",
                    "reference_answer": "v_2026_05_30",
                    "reference_judge": {"verdict": "exact"},
                    "queries": ["document_date(doc_a, issue_date, Date)."],
                    "query_results": [
                        {
                            "query": "document_date(doc_a, issue_date, Date).",
                            "result": {
                                "status": "success",
                                "predicate": "document_date",
                                "rows": [{"Date": "v_2026_05_30"}],
                            },
                        }
                    ],
                },
                {
                    "id": "q002",
                    "reference_answer": (
                        "This title is a complete sentence that should not be treated as a compact typed atom "
                        "because it smuggles source text."
                    ),
                    "reference_judge": {"verdict": "exact"},
                    "queries": ["document_title(doc_a, Title)."],
                    "query_results": [
                        {
                            "query": "document_title(doc_a, Title).",
                            "result": {
                                "status": "success",
                                "predicate": "document_title",
                                "rows": [
                                    {
                                        "Title": (
                                            "this_title_is_a_complete_sentence_that_should_not_be_treated_as_a_"
                                            "compact_typed_atom_because_it_smuggles_source_text"
                                        )
                                    }
                                ],
                            },
                        }
                    ],
                },
                {
                    "id": "q003",
                    "reference_answer": "not exact",
                    "reference_judge": {"verdict": "partial"},
                    "queries": [],
                    "query_results": [],
                },
            ],
        },
    )

    report = build_report(qa_files=[qa_json], compile_root=compile_root)

    assert report["summary"]["row_count"] == 3
    assert report["summary"]["product_exact"] == 2
    assert report["summary"]["typed_plan_exact"] == 1
    assert report["summary"]["redaction_survived_exact"] == 2
    assert report["summary"]["atom_shape_clean_product_exact"] == 1
    assert report["summary"]["hard_clean_exact"] == 1
    rows = {row["id"]: row for row in report["rows"]}
    assert rows["q001"]["hard_clean"] is True
    assert rows["q002"]["hard_clean"] is False
    assert rows["q002"]["atom_shape_hits"]
