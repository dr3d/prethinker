import json

from scripts import audit_reference_judge_null_controls as audit


def test_reference_judge_null_controls_sample_and_count(tmp_path, monkeypatch):
    qa_dir = tmp_path / "fixture_a"
    qa_dir.mkdir()
    qa_file = qa_dir / "qa.json"
    qa_file.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "utterance": "What is A?",
                        "reference_answer": "A",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {"result": {"predicate": "fact", "rows": [{"Thing": "a"}]}}
                        ],
                    },
                    {
                        "id": "q002",
                        "utterance": "What is B?",
                        "reference_answer": "B",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {"result": {"predicate": "fact", "rows": [{"Thing": "b"}]}}
                        ],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    def fake_judge_reference_answer(*, row, config, sign_clean_strict=False):
        assert sign_clean_strict
        return {"verdict": "miss", "answer_supported": False, "concise_answer": ""}

    monkeypatch.setattr(audit, "judge_reference_answer", fake_judge_reference_answer)

    report = audit.build_report(
        qa_files=[qa_file],
        config=object(),
        sample_per_fixture=1,
        seed=1,
    )

    assert report["summary"]["sampled_product_exact_rows"] == 1
    assert report["summary"]["control_judgments"] == 2
    assert report["summary"]["exact_null_verdicts"] == 0
    assert report["summary"]["status"] == "pass"


def test_reference_judge_null_controls_blocks_when_no_product_exact_rows(tmp_path, monkeypatch):
    qa_dir = tmp_path / "fixture_a"
    qa_dir.mkdir()
    qa_file = qa_dir / "qa.json"
    qa_file.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "utterance": "What is A?",
                        "reference_answer": "A",
                        "reference_judge": {"verdict": "miss"},
                        "query_results": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    def fake_judge_reference_answer(*, row, config, sign_clean_strict=False):
        raise AssertionError("judge should not be called when no product-exact rows are sampled")

    monkeypatch.setattr(audit, "judge_reference_answer", fake_judge_reference_answer)

    report = audit.build_report(
        qa_files=[qa_file],
        config=object(),
        sample_per_fixture=1,
        seed=1,
    )

    assert report["summary"]["sampled_product_exact_rows"] == 0
    assert report["summary"]["blocking_reasons"] == ["no_sampled_product_exact_rows"]
    assert report["summary"]["status"] == "blocked"


def test_wrong_reference_control_neutralizes_original_question(tmp_path, monkeypatch):
    qa_dir = tmp_path / "fixture_a"
    qa_dir.mkdir()
    qa_file = qa_dir / "qa.json"
    qa_file.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "utterance": "Does the KB contain fact A?",
                        "question": "Does the KB contain fact A?",
                        "reference_answer": "fact_a.",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {"result": {"predicate": "fact", "rows": [{"Thing": "a"}]}}
                        ],
                    },
                    {
                        "id": "q002",
                        "utterance": "Does the KB contain fact B?",
                        "question": "Does the KB contain fact B?",
                        "reference_answer": "fact_b.",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {"result": {"predicate": "fact", "rows": [{"Thing": "b"}]}}
                        ],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    seen_wrong_rows = []

    def fake_judge_reference_answer(*, row, config, sign_clean_strict=False):
        assert sign_clean_strict
        if row.get("null_control") == "wrong_reference":
            seen_wrong_rows.append(row)
        return {"verdict": "miss", "answer_supported": False, "concise_answer": ""}

    monkeypatch.setattr(audit, "judge_reference_answer", fake_judge_reference_answer)

    audit.build_report(
        qa_files=[qa_file],
        config=object(),
        sample_per_fixture=1,
        seed=1,
    )

    assert seen_wrong_rows
    wrong_row = seen_wrong_rows[0]
    assert "Does the KB contain fact" not in wrong_row["utterance"]
    assert "NULL CONTROL" in wrong_row["utterance"]
    assert wrong_row["question"] == wrong_row["utterance"]
    assert wrong_row["model_decision"] == ""
    assert wrong_row["projected_decision"] == ""
