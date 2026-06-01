import json

from scripts.summarize_hard_clean_answer_classes import build_report, classify_answer_class


def test_classify_substantive_and_scaffolding_rows():
    assert (
        classify_answer_class(
            qa_row={"utterance": "Under what statutory provision did the agency act?"},
            hard_row={"reference_answer": "Section 301(a)."},
        )
        == "legal_authority"
    )
    assert (
        classify_answer_class(
            qa_row={"utterance": "What is the docket number and issue date?"},
            hard_row={"reference_answer": "No. 123; issued May 1."},
        )
        == "document_metadata_bundle"
    )
    assert (
        classify_answer_class(
            qa_row={"utterance": "List the three numbered violations and their citations."},
            hard_row={"reference_answer": "Violation 1, violation 2, violation 3."},
        )
        == "violation_or_deficiency"
    )


def test_build_report_summarizes_answer_classes(tmp_path):
    hard_path = tmp_path / "hard.json"
    hard_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fda_warning_ugly_007",
                        "id": "q001",
                        "product_verdict": "exact",
                        "typed_plan_status": "all_queries_success",
                        "redaction_thesis_verdict": "survived",
                        "atom_shape_clean": True,
                        "hard_clean": True,
                        "reference_answer": "Warning Letter 1; issued May 1.",
                    },
                    {
                        "fixture": "fda_warning_ugly_007",
                        "id": "q002",
                        "product_verdict": "exact",
                        "typed_plan_status": "partial_query_success",
                        "redaction_thesis_verdict": "survived",
                        "atom_shape_clean": True,
                        "hard_clean": False,
                        "reference_answer": "21 U.S.C. 351(a)(2)(B).",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    qa_dir = tmp_path / "qa" / "fda_warning_ugly_007"
    qa_dir.mkdir(parents=True)
    (qa_dir / "qa.json").write_text(
        json.dumps(
            {
                "rows": [
                    {"id": "q001", "utterance": "What is the Warning Letter number and issue date?"},
                    {"id": "q002", "utterance": "Under what statutory provision are the drugs adulterated?"},
                ]
            }
        ),
        encoding="utf-8",
    )
    dataset_dir = tmp_path / "dataset" / "fda_warning_ugly_007"
    dataset_dir.mkdir(parents=True)
    (dataset_dir / "metadata.json").write_text(
        json.dumps({"fixture_id": "fda_warning_ugly_007", "source_family": "fda_warning"}),
        encoding="utf-8",
    )

    report = build_report(hard_road_json=hard_path, qa_root=tmp_path / "qa", dataset_root=tmp_path / "dataset")

    assert report["summary"]["row_count"] == 2
    assert report["summary"]["hard_clean_exact"] == 1
    assert report["by_source_family"]["fda_warning"]["row_count"] == 2
    assert report["by_answer_class"]["violation_or_deficiency"]["failure_reasons"]["typed_plan_not_full"] == 1
