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
