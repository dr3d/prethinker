import json
from pathlib import Path

from scripts.validate_fresh_ugly_batch import validate_batch


def _write_fixture(root: Path, name: str, *, question_count: int = 25, answer_count: int = 25) -> None:
    fixture = root / name
    fixture.mkdir(parents=True)
    (fixture / "source.md").write_text("# Source\n\nMessy public text.\n", encoding="utf-8")
    (fixture / "qa.md").write_text(
        "# QA\n\n" + "\n".join(f"{index}. Question {index}?" for index in range(1, question_count + 1)),
        encoding="utf-8",
    )
    (fixture / "qa_authored_with_answers.md").write_text(
        "# QA With Answers\n\n"
        + "\n\n".join(
            f"## q{index:03d}\n\n**Question.** Question {index}?\n\n**Reference answer.** Answer {index}."
            for index in range(1, answer_count + 1)
        ),
        encoding="utf-8",
    )
    (fixture / "oracle.jsonl").write_text(
        "\n".join(
            json.dumps({"id": f"q{index:03d}", "reference_answer": f"Answer {index}."})
            for index in range(1, answer_count + 1)
        )
        + "\n",
        encoding="utf-8",
    )
    (fixture / "fixture_notes.md").write_text("Public source URL and pressure notes.\n", encoding="utf-8")
    (fixture / "metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "fresh_ugly_public_batch_v1",
                "batch_id": "fresh_ugly_public_20260524_03",
                "document_id": name,
                "source_family": "fda",
                "source_url": "https://example.com/source",
                "llm_authored_source": False,
                "llm_rewritten_source": False,
                "question_count": 25,
                "pressure_tags": ["dates", "tables"],
            }
        ),
        encoding="utf-8",
    )


def test_validate_fresh_ugly_batch_accepts_complete_batch(tmp_path) -> None:
    batch = tmp_path / "fresh_ugly_public_20260524_03"
    _write_fixture(batch, "fda_warning_ugly_006")

    report = validate_batch(batch, expected_documents=1, expected_questions=25)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["issue_count"] == 0
    assert report["fixtures"][0]["question_count"] == 25
    assert report["fixtures"][0]["reference_answer_count"] == 25
    assert report["fixtures"][0]["oracle_row_count"] == 25


def test_validate_fresh_ugly_batch_flags_missing_files_and_count_mismatch(tmp_path) -> None:
    batch = tmp_path / "fresh_ugly_public_20260524_03"
    _write_fixture(batch, "osha_incident_ugly_006", question_count=24, answer_count=23)
    (batch / "osha_incident_ugly_006" / "fixture_notes.md").unlink()

    report = validate_batch(batch, expected_documents=1, expected_questions=25)
    issues = report["fixtures"][0]["issues"]

    assert report["summary"]["status"] == "fail"
    assert "missing_file:fixture_notes.md" in issues
    assert "empty_fixture_notes" in issues
    assert "qa_question_count:24 expected:25" in issues
    assert "reference_answer_count:23 expected:25" in issues
    assert "oracle_row_count:23 expected:25" in issues


def test_validate_fresh_ugly_batch_flags_document_count(tmp_path) -> None:
    batch = tmp_path / "fresh_ugly_public_20260524_03"
    _write_fixture(batch, "sec_material_event_ugly_006")

    report = validate_batch(batch, expected_documents=2, expected_questions=25)

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["batch_issues"] == ["document_count:1 expected:2"]


def test_validate_fresh_ugly_batch_counts_bold_numbered_answer_style(tmp_path) -> None:
    batch = tmp_path / "fresh_ugly_public_20260524_03"
    _write_fixture(batch, "other_ugly_006")
    authored = batch / "other_ugly_006" / "qa_authored_with_answers.md"
    authored.write_text(
        "# Questions with Reference Answers\n\n"
        + "\n\n".join(
            f"**{index}. Question {index}?**\n\nAnswer {index} with source support."
            for index in range(1, 26)
        ),
        encoding="utf-8",
    )

    report = validate_batch(batch, expected_documents=1, expected_questions=25)

    assert report["summary"]["status"] == "pass"
    assert report["fixtures"][0]["reference_answer_count"] == 25


def test_validate_fresh_ugly_batch_ignores_indented_numbered_answer_lists(tmp_path) -> None:
    batch = tmp_path / "fresh_ugly_public_20260524_03"
    _write_fixture(batch, "sec_ugly_006")
    authored = batch / "sec_ugly_006" / "qa_authored_with_answers.md"
    authored.write_text(
        "# Questions with Reference Answers\n\n"
        + "\n\n".join(
            f"{index}. Question {index}?\n\n"
            f"   Answer {index}.\n"
            f"   1. Nested support point.\n"
            f"   2. Nested support point."
            for index in range(1, 26)
        ),
        encoding="utf-8",
    )

    report = validate_batch(batch, expected_documents=1, expected_questions=25)

    assert report["summary"]["status"] == "pass"
    assert report["fixtures"][0]["reference_answer_count"] == 25


def test_validate_fresh_ugly_batch_accepts_q_heading_answer_style(tmp_path) -> None:
    batch = tmp_path / "fresh_non_english_wild_20260526_01"
    _write_fixture(batch, "fr_regulator_001")
    authored = batch / "fr_regulator_001" / "qa_authored_with_answers.md"
    authored.write_text(
        "# QA With Answers\n\n"
        + "\n\n".join(
            f"**Q{index} [DF, FR/FR]** Question {index}?\n"
            f"**Réponse :** Réponse {index}.\n"
            f"**Coordonnées :** Section {index}."
            for index in range(1, 26)
        ),
        encoding="utf-8",
    )

    report = validate_batch(batch, expected_documents=1, expected_questions=25)

    assert report["summary"]["status"] == "pass"
    assert report["fixtures"][0]["reference_answer_count"] == 25


def test_validate_fresh_ugly_batch_accepts_complete_oracle_when_markdown_answer_style_is_unknown(tmp_path) -> None:
    batch = tmp_path / "fresh_non_english_wild_20260526_01"
    _write_fixture(batch, "ja_regulator_001")
    authored = batch / "ja_regulator_001" / "qa_authored_with_answers.md"
    authored.write_text("# QA With Answers\n\nThis file preserves an author-specific answer layout.\n", encoding="utf-8")

    report = validate_batch(batch, expected_documents=1, expected_questions=25)

    assert report["summary"]["status"] == "pass"
    assert report["fixtures"][0]["reference_answer_count"] == 0
    assert report["fixtures"][0]["oracle_row_count"] == 25


def test_validate_fresh_ugly_batch_accepts_qa_markdown_as_answer_key(tmp_path) -> None:
    batch = tmp_path / "fresh_ach_stress_public_20260528_01"
    _write_fixture(batch, "ntsb_engine_power_001", question_count=15, answer_count=15)
    fixture = batch / "ntsb_engine_power_001"
    (fixture / "qa_authored_with_answers.md").unlink()
    (fixture / "qa.md").write_text(
        "# QA\n\n"
        + "\n\n".join(
            f"**Q{index} [direct_fact]** Question {index}?\n"
            f"**A:** Answer {index}.\n"
            f"**Coords:** [SECTION {index}]"
            for index in range(1, 16)
        ),
        encoding="utf-8",
    )
    (fixture / "metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "fresh_ach_stress_public_batch_v1",
                "document_id": "ntsb_engine_power_001",
                "source_url": "https://example.com/source",
                "llm_authored_source": False,
                "llm_rewritten_source": False,
                "question_count": 15,
                "pressure_tags": ["ach"],
            }
        ),
        encoding="utf-8",
    )

    report = validate_batch(batch, expected_documents=1, expected_questions=15)

    assert report["summary"]["status"] == "pass"
    assert report["fixtures"][0]["question_count"] == 15
    assert report["fixtures"][0]["reference_answer_count"] == 15


def test_validate_fresh_ugly_batch_checks_oracle_jsonl_shape(tmp_path) -> None:
    batch = tmp_path / "fresh_ugly_public_20260524_03"
    _write_fixture(batch, "fda_ugly_006")
    oracle = batch / "fda_ugly_006" / "oracle.jsonl"
    oracle.write_text(
        json.dumps({"id": "q001", "reference_answer": "Answer 1."})
        + "\n"
        + json.dumps({"id": "q001", "reference_answer": ""})
        + "\n"
        + "{not-json}\n",
        encoding="utf-8",
    )

    report = validate_batch(batch, expected_documents=1, expected_questions=25)
    issues = report["fixtures"][0]["issues"]

    assert report["summary"]["status"] == "fail"
    assert "oracle_row_count:3 expected:25" in issues
    assert "oracle_jsonl_duplicate_id:q001" in issues
    assert "oracle_jsonl_missing_reference_answer:q001" in issues
    assert any(issue.startswith("oracle_jsonl_error:line_3:") for issue in issues)


def test_validate_fresh_ugly_batch_warns_when_reference_terms_live_outside_source(tmp_path) -> None:
    batch = tmp_path / "fresh_non_english_wild_20260526_01"
    _write_fixture(batch, "de_corporate_001")
    fixture = batch / "de_corporate_001"
    (fixture / "source.md").write_text("# Source\n\nThe company updated its forecast.\n", encoding="utf-8")
    (fixture / "fixture_notes.md").write_text(
        "Pressure note: Art. 17 MAR and ISIN DE000PAH0038 appear in external footer material.\n",
        encoding="utf-8",
    )
    (fixture / "metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "fresh_ugly_public_batch_v1",
                "batch_id": "fresh_non_english_wild_20260526_01",
                "document_id": "de_corporate_001",
                "source_family": "ad_hoc_disclosure_under_art_17_mar",
                "source_url": "https://example.com/source",
                "llm_authored_source": False,
                "llm_rewritten_source": False,
                "question_count": 2,
                "pressure_tags": ["legal_citation"],
            }
        ),
        encoding="utf-8",
    )
    (fixture / "qa.md").write_text("1. Legal basis?\n2. ISIN?\n", encoding="utf-8")
    (fixture / "oracle.jsonl").write_text(
        json.dumps({"id": "q001", "reference_answer": "Art. 17 MAR."})
        + "\n"
        + json.dumps({"id": "q002", "reference_answer": "DE000PAH0038."})
        + "\n",
        encoding="utf-8",
    )

    report = validate_batch(batch, expected_documents=1, expected_questions=2)
    warnings = report["fixtures"][0]["warnings"]

    assert report["summary"]["status"] == "pass"
    assert "reference_terms_absent_from_source_but_in_notes_or_metadata:2" in warnings
    assert "reference_terms_found_in_fixture_notes:2" in warnings
    assert "reference_terms_found_in_metadata:1" in warnings
    details = report["fixtures"][0]["warning_details"]
    assert {
        detail["kind"]
        for detail in details
    } == {
        "reference_terms_absent_from_source",
        "reference_terms_absent_from_source_but_in_notes_or_metadata",
    }
    assert {detail["row_id"] for detail in details} == {"q001", "q002"}


def test_validate_fresh_ugly_batch_warns_when_oracle_declares_incomplete_source_pressure(tmp_path) -> None:
    batch = tmp_path / "fresh_non_english_wild_20260526_01"
    _write_fixture(batch, "de_regulator_001")
    fixture = batch / "de_regulator_001"
    (fixture / "qa.md").write_text("1. Settlement practice?\n", encoding="utf-8")
    (fixture / "qa_authored_with_answers.md").write_text(
        "# QA With Answers\n\n**Q1 [OV, DE/DE]** Settlement practice?\n**Antwort:** Source gives the section only.\n",
        encoding="utf-8",
    )
    (fixture / "metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "fresh_ugly_public_batch_v1",
                "batch_id": "fresh_non_english_wild_20260526_01",
                "document_id": "de_regulator_001",
                "source_family": "regulatory",
                "source_url": "https://example.com/source",
                "llm_authored_source": False,
                "llm_rewritten_source": False,
                "question_count": 1,
                "pressure_tags": ["legal_citation"],
            }
        ),
        encoding="utf-8",
    )
    (fixture / "oracle.jsonl").write_text(
        json.dumps(
            {
                "id": "q001",
                "reference_answer": "Source gives the section; practice conditions are not detailed.",
                "pressure_tags": ["legal_citation", "incomplete_in_source"],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    report = validate_batch(batch, expected_documents=1, expected_questions=1)
    warnings = report["fixtures"][0]["warnings"]

    assert report["summary"]["status"] == "pass"
    assert "oracle_declares_incomplete_source_rows:1" in warnings
    assert "oracle_incomplete_source_examples:q001" in warnings
    details = report["fixtures"][0]["warning_details"]
    assert {
        "kind": "oracle_declares_incomplete_source",
        "row_id": "q001",
        "pressure_tags": ["legal_citation", "incomplete_in_source"],
    } in details


def test_validate_fresh_ugly_batch_tracks_decimal_percentage_terms(tmp_path) -> None:
    batch = tmp_path / "fresh_non_english_wild_20260526_01"
    _write_fixture(batch, "de_corporate_001")
    fixture = batch / "de_corporate_001"
    (fixture / "source.md").write_text("Prior range was 6,5 % to 7,0 %. New value is absolute only.\n", encoding="utf-8")
    (fixture / "qa.md").write_text("1. What was the new percentage?\n", encoding="utf-8")
    (fixture / "oracle.jsonl").write_text(
        json.dumps({"id": "q001", "reference_answer": "New value ~5,6 %."}) + "\n",
        encoding="utf-8",
    )

    report = validate_batch(batch, expected_documents=1, expected_questions=1)
    details = report["fixtures"][0]["warning_details"]

    assert any(
        detail["kind"] == "reference_terms_absent_from_source"
        and detail["row_id"] == "q001"
        and "5,6%" in detail["missing_terms"]
        for detail in details
    )
