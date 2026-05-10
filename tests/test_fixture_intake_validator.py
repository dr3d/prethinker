from pathlib import Path
import zipfile

from scripts.validate_fixture_intake import build_report


def _write_valid_fixture(path: Path) -> None:
    path.mkdir(parents=True)
    sentence = "The board record states a procedural fact without revealing answers. "
    (path / "source.md").write_text(sentence * 140, encoding="utf-8")
    rows = [f'{{"id":"q{i:03d}","question":"Question {i}?"}}' for i in range(1, 41)]
    (path / "qa.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (path / "fixture_notes.md").write_text("Challenge: temporal and authority traps.\n", encoding="utf-8")


def test_fixture_intake_validator_accepts_requested_shape(tmp_path: Path) -> None:
    fixture = tmp_path / "meridian_permit_board"
    _write_valid_fixture(fixture)

    report = build_report(fixture_dirs=[fixture])

    assert report["summary"]["passed_fixture_count"] == 1
    assert report["fixtures"][0]["status"] == "pass"
    assert report["fixtures"][0]["qa"]["row_count"] == 40


def test_fixture_intake_validator_blocks_answer_keys_in_qa(tmp_path: Path) -> None:
    fixture = tmp_path / "harrowgate_witness_file"
    _write_valid_fixture(fixture)
    rows = [f'{{"id":"q{i:03d}","question":"Question {i}?"}}' for i in range(1, 40)]
    rows.append('{"id":"q040","question":"Question 40?","answer":"secret"}')
    (fixture / "qa.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")

    report = build_report(fixture_dirs=[fixture])

    assert report["summary"]["failed_fixture_count"] == 1
    assert any("contains_answer_key" in item for item in report["fixtures"][0]["errors"])


def test_fixture_intake_validator_warns_on_answerish_notes(tmp_path: Path) -> None:
    fixture = tmp_path / "northbridge_authority_packet"
    _write_valid_fixture(fixture)
    (fixture / "fixture_notes.md").write_text("The answer key says too much.\n", encoding="utf-8")

    report = build_report(fixture_dirs=[fixture])

    assert report["summary"]["warning_fixture_count"] == 1
    assert "fixture_notes_may_contain_answer_key_language" in report["fixtures"][0]["warnings"]


def test_fixture_intake_validator_requires_forty_rows(tmp_path: Path) -> None:
    fixture = tmp_path / "larkspur_clockwork_fair"
    _write_valid_fixture(fixture)
    (fixture / "qa.jsonl").write_text('{"id":"q001","question":"Only one?"}\n', encoding="utf-8")

    report = build_report(fixture_dirs=[fixture])

    assert report["summary"]["failed_fixture_count"] == 1
    assert "qa_row_count_expected_40_got_1" in report["fixtures"][0]["errors"]


def test_fixture_intake_validator_accepts_sealed_story_zip_shape(tmp_path: Path) -> None:
    fixture = tmp_path / "nested_puppet_court"
    inner = fixture / "nested_puppet_court"
    inner.mkdir(parents=True)
    story = "The nested court record keeps fiction and testimony apart. "
    (inner / "README.md").write_text("# Nested Puppet Court\n", encoding="utf-8")
    (inner / "story.md").write_text(story * 160, encoding="utf-8")
    (inner / "challenge_strategy.md").write_text("Attacks quoted-world contamination.\n", encoding="utf-8")
    (inner / "anti_leakage_manifest.md").write_text("Questions are separate from private answers.\n", encoding="utf-8")
    (inner / "qa_questions.md").write_text(
        "\n".join(f"q{i:03d}: Question {i}?" for i in range(1, 41)) + "\n",
        encoding="utf-8",
    )
    (inner / "qa_answers_private.jsonl").write_text(
        "\n".join(f'{{"id":"q{i:03d}","reference_answer":"Answer {i}."}}' for i in range(1, 41)) + "\n",
        encoding="utf-8",
    )
    archive = tmp_path / "nested_puppet_court.zip"
    with zipfile.ZipFile(archive, "w") as zipf:
        for path in inner.iterdir():
            zipf.write(path, arcname=f"nested_puppet_court/{path.name}")

    report = build_report(fixture_dirs=[archive])

    assert report["summary"]["passed_fixture_count"] == 1
    fixture_report = report["fixtures"][0]
    assert fixture_report["fixture"] == "nested_puppet_court"
    assert fixture_report["files"]["format"] == "sealed_story_zip_v1"
    assert fixture_report["qa"]["row_count"] == 40


def test_fixture_intake_validator_accepts_isolated_markdown_oracle_shape(tmp_path: Path) -> None:
    fixture = tmp_path / "identifier_ledger_torture"
    fixture.mkdir(parents=True)
    sentence = "The evidence-room audit preserves exact labels and custody facts. "
    (fixture / "source.md").write_text(sentence * 220, encoding="utf-8")
    (fixture / "qa.md").write_text(
        "\n".join(f"**q{i:03d}.** Question {i}?" for i in range(1, 41)) + "\n",
        encoding="utf-8",
    )
    (fixture / "oracle.jsonl").write_text(
        "\n".join(
            f'{{"id":"q{i:03d}","source_id":"q{i:03d}","category":"lookup","reference_answer":"Answer {i}."}}'
            for i in range(1, 41)
        )
        + "\n",
        encoding="utf-8",
    )
    (fixture / "strategy.md").write_text("Attacks exact identifier preservation.\n", encoding="utf-8")
    (fixture / "anti_leakage_manifest.md").write_text("Answers are separated for scoring.\n", encoding="utf-8")

    report = build_report(fixture_dirs=[fixture])

    assert report["summary"]["passed_fixture_count"] == 1
    fixture_report = report["fixtures"][0]
    assert fixture_report["files"]["format"] == "source_qa_md_oracle_jsonl_v1"
    assert fixture_report["qa"]["row_count"] == 40
