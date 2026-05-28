import json
from pathlib import Path

from scripts.adjudicate_qa_residue import build_report, render_markdown


def _write_qa(path: Path, *, fixture: str) -> None:
    path.parent.mkdir(parents=True)
    rows = [
        _row("q001", "exact", "compile_surface_gap", ["date"]),
        _row("q002", "miss", "compile_surface_gap", ["incomplete_in_source"]),
        _row("q003", "partial", "compile_surface_gap", ["legal_citation"]),
        _row("q004", "miss", "query_surface_gap", ["role"]),
    ]
    path.write_text(
        json.dumps(
            {
                "qa_file": str(Path("datasets") / fixture / "qa.md"),
                "summary": {
                    "runtime_load_error_count": 0,
                    "write_proposal_rows": 0,
                    "compatibility_row_summary": {"row_count": 0},
                },
                "rows": rows,
            }
        ),
        encoding="utf-8",
    )


def _row(row_id: str, verdict: str, surface: str, pressure_tags: list[str]) -> dict:
    return {
        "id": row_id,
        "oracle": {"pressure_tags": pressure_tags},
        "reference_judge": {"verdict": verdict, "answer_supported": verdict != "miss"},
        "failure_surface": {"surface": surface},
        "response_envelope": {"status": "coverage_gap", "failure_surface": surface},
    }


def test_adjudicate_qa_residue_classifies_non_exact_rows(tmp_path) -> None:
    fixture = "sample_fixture_001"
    qa_path = tmp_path / "qa" / fixture / "domain_bootstrap_qa_20260528.json"
    _write_qa(qa_path, fixture=fixture)
    validation_path = tmp_path / "validation.json"
    validation_path.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "fixture": fixture,
                        "warning_details": [
                            {
                                "kind": "reference_terms_absent_from_source_but_in_notes_or_metadata",
                                "row_id": f"{fixture}_q03",
                                "missing_terms": ["outside"],
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_roots=(tmp_path / "qa",), validation_json=validation_path)

    assert report["summary"]["question_count"] == 4
    assert report["summary"]["residue_count"] == 3
    assert report["summary"]["classification_counts"] == {
        "declared_source_or_oracle_limit": 1,
        "query_planning_gap": 1,
        "source_support_adjudication_needed": 1,
    }
    rows = {(row["row_id"], row["classification"]) for row in report["residue"]}
    assert ("q002", "declared_source_or_oracle_limit") in rows
    assert ("q003", "source_support_adjudication_needed") in rows
    assert ("q004", "query_planning_gap") in rows


def test_adjudicate_qa_residue_render_markdown(tmp_path) -> None:
    fixture = "sample_fixture_001"
    qa_path = tmp_path / "qa" / fixture / "domain_bootstrap_qa_20260528.json"
    _write_qa(qa_path, fixture=fixture)

    report = build_report(qa_jsons=(qa_path,))
    markdown = render_markdown(report)

    assert "# QA Residue Adjudication" in markdown
    assert "`repairable_compile_gap`" in markdown
    assert "| `sample_fixture_001` | `q002` | `miss` |" in markdown


def test_adjudicate_qa_residue_applies_targeted_row_overrides(tmp_path) -> None:
    fixture = "sample_fixture_001"
    full_path = tmp_path / "qa_full" / fixture / "domain_bootstrap_qa_20260528.json"
    _write_qa(full_path, fixture=fixture)
    override_path = tmp_path / "qa_override" / "domain_bootstrap_qa_20260529.json"
    override_path.parent.mkdir(parents=True)
    override_path.write_text(
        json.dumps(
            {
                "qa_file": str(Path("datasets") / fixture / "qa.md"),
                "summary": {
                    "runtime_load_error_count": 0,
                    "write_proposal_rows": 0,
                    "compatibility_row_summary": {"row_count": 0},
                },
                "rows": [_row("q002", "exact", "compile_surface_gap", ["date"])],
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_roots=(tmp_path / "qa_full",), qa_jsons=(override_path,))

    assert report["summary"]["question_count"] == 4
    assert report["summary"]["selected_qa_artifact_count"] == 2
    assert report["summary"]["verdict_counts"] == {"exact": 2, "miss": 1, "partial": 1}
    rows = {(row["row_id"], row["classification"]) for row in report["residue"]}
    assert ("q002", "declared_source_or_oracle_limit") not in rows
