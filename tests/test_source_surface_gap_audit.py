from __future__ import annotations

from kb_pipeline import CorePrologRuntime
from scripts.audit_source_surface_gaps import audit_scorecard
from scripts.run_domain_bootstrap_qa import (
    compiled_kb_inventory,
    _source_field_question_key_hint_queries,
    _source_text_question_token_hint_queries,
    run_query_plan,
)


def test_source_text_question_token_hints_use_question_tokens_only() -> None:
    queries = _source_text_question_token_hint_queries(
        utterance="What is the label and material for case QR-17?",
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
    )

    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("qr_17", TextAtom).' in queries
    assert all("ceramic" not in query for query in queries)


def test_source_text_question_token_hints_prioritize_initial_surname() -> None:
    queries = _source_text_question_token_hint_queries(
        utterance="What events did R. Kim not originate?",
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
    )

    assert queries[0] == 'source_record_text_atom(SourceRow, TextAtom), memberchk("r_kim", TextAtom).'


def test_source_text_question_token_hints_include_quantity_questions() -> None:
    queries = _source_text_question_token_hint_queries(
        utterance="How many books were damaged in the pipe burst?",
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
    )

    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("the_pipe_burst", TextAtom).' in queries
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("books", TextAtom).' in queries


def test_source_field_question_key_hints_use_existing_source_field_headers() -> None:
    queries = _source_field_question_key_hint_queries(
        utterance="What is the vendor and model number for device QR-17?",
        kb_inventory={
            "signatures": ["source_record_field/3"],
            "examples": {
                "source_record_field/3": [
                    "source_record_field(src_line_1, vendor, northstar).",
                    "source_record_field(src_line_1, model, nx_4).",
                    "source_record_field(src_line_1, location, bay_3).",
                ]
            },
        },
    )

    assert "source_record_field(SourceRow, vendor, Value)." in queries
    assert "source_record_field(SourceRow, model, Value)." in queries
    assert "source_record_field(SourceRow, location, Value)." not in queries


def test_source_field_question_key_hints_use_all_inventory_headers_beyond_examples() -> None:
    facts = [
        f"source_record_field(src_line_{index:04d}, filler_{index}, value_{index})."
        for index in range(12)
    ]
    facts.append("source_record_field(src_line_9999, vendor, northstar).")
    inventory = compiled_kb_inventory(facts=facts, rules=[])

    queries = _source_field_question_key_hint_queries(
        utterance="Which vendor is listed for device QR-17?",
        kb_inventory=inventory,
    )

    assert "source_record_field(SourceRow, vendor, Value)." in queries


def test_run_query_plan_filters_source_text_memberchk_queries() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    runtime.assert_fact("source_record_text_atom(src_line_1, case_qr_17_material_ceramic_blue).")
    runtime.assert_fact("source_record_text_atom(src_line_2, unrelated_record_summary).")

    rows = run_query_plan(
        runtime,
        ['source_record_text_atom(SourceRow, TextAtom), memberchk("qr_17", TextAtom).'],
        helper_companions_enabled=False,
    )

    assert rows[0]["result"]["status"] == "success"
    assert rows[0]["result"]["num_rows"] == 1
    assert rows[0]["result"]["rows"][0]["SourceRow"] == "src_line_1"
    assert rows[0]["result"]["reasoning_basis"]["validation"] == "source_text_contains_filter_repaired"


def test_source_surface_gap_audit_separates_stranded_source_from_direct_rows(tmp_path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        """
        {
          "source_compile": {
            "facts": [
              "item_id(case_qr_17).",
              "source_record_text_atom(src_line_1, case_qr_17_material_ceramic_blue)."
            ],
            "rules": []
          }
        }
        """,
        encoding="utf-8",
    )
    qa_json = tmp_path / "qa.json"
    qa_json.write_text(
        """
        {
          "rows": [
            {
              "id": "q001",
              "utterance": "What material is case QR-17?",
              "reference_answer": "Ceramic blue."
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    scorecard = {
        "artifacts": [
            {
                "label": "unlike_fixture",
                "path": str(qa_json),
                "run_json": str(compile_json),
                "non_exact_rows": [
                    {
                        "id": "q001",
                        "verdict": "miss",
                        "failure_surface": "compile_surface_gap",
                        "question": "What material is case QR-17?",
                        "queries": ["item_material(case_qr_17, Material)."],
                    }
                ],
            }
        ]
    }

    report = audit_scorecard(scorecard)

    assert report["summary"]["evidence_class_counts"] == {"answer_stranded_in_source_record": 1}
