import json

from scripts.audit_typed_artifact_recall import build_report


def test_typed_artifact_recall_excludes_source_record_prose_and_predicate_names(tmp_path):
    dataset_root = tmp_path / "dataset"
    compile_root = tmp_path / "compile"
    fixture_dir = dataset_root / "fixture_one"
    compile_dir = compile_root / "fixture_one"
    fixture_dir.mkdir(parents=True)
    compile_dir.mkdir(parents=True)

    oracle_rows = [
        {"id": "q001", "reference_answer": "Hidden Answer 99"},
        {"id": "q002", "reference_answer": "Alpha 42"},
        {"id": "q003", "reference_answer": "event date"},
        {"id": "q004", "reference_answer": "The agency explained the denial by citing missing support."},
        {"id": "q005", "reference_answer": "Three open items."},
        {"id": "q006", "reference_answer": "Alice Example, Chair."},
        {"id": "q007", "reference_answer": "report date"},
        {"id": "q008", "reference_answer": "Union One."},
    ]
    fixture_dir.joinpath("oracle.jsonl").write_text(
        "\n".join(json.dumps(row) for row in oracle_rows) + "\n",
        encoding="utf-8",
    )
    fixture_dir.joinpath("qa.md").write_text(
        "\n".join(
            [
                "q004. How did the agency explain the denial?",
                "q005. How many open items were identified?",
                "q006. Who signed the order?",
                "q007. What date role was provided?",
                "q008. Who was the petitioner?",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    compile_dir.joinpath("compile.json").write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "source_record_text_atom(row1, 'Hidden Answer 99').",
                        "claim_text(case_a, 'Hidden Answer 99').",
                        "typed_fact(case_a, alpha, 42).",
                        "event_date(case_a, d_2026_01_01).",
                        "document_date(case_a, report_date, d_2026_01_01).",
                        "party_role_context(case_a, union_one, petitioner, direct).",
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    report = build_report(
        dataset_root=dataset_root,
        compile_root=compile_root,
        coverage_threshold=0.85,
        partial_threshold=0.55,
    )

    rows = {row["id"]: row for row in report["rows"]}
    assert rows["q001"]["typed_any"]["class"] == "likely_available"
    assert rows["q001"]["typed_strict"]["class"] == "not_available"
    assert rows["q002"]["typed_strict"]["class"] == "likely_available"
    assert rows["q002"]["typed_registered"]["class"] == "not_available"
    assert rows["q003"]["typed_any"]["class"] == "not_available"
    assert rows["q003"]["typed_strict"]["class"] == "not_available"
    assert rows["q007"]["typed_registered"]["class"] == "likely_available"
    assert rows["q004"]["answer_type"] != "quantity_or_amount"
    assert rows["q005"]["answer_type"] == "quantity_or_amount"
    assert rows["q006"]["answer_type"] == "person_role_roster"
    assert rows["q008"]["typed_registered"]["class"] == "likely_available"

    assert report["summary"]["typed_any"]["likely_available"] == 4
    assert report["summary"]["typed_strict"]["likely_available"] == 3
    assert report["summary"]["typed_registered"]["likely_available"] == 2
