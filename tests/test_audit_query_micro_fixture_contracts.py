import json
from pathlib import Path

from scripts.audit_query_micro_fixture_contracts import audit_manifests, render_markdown


def test_query_micro_fixture_contract_accepts_atom_library_packet(tmp_path: Path) -> None:
    manifest = _write_query_fixture(
        tmp_path,
        questions=[
            "Which `sec_registrant/4` registrant_id and jurisdiction are compiled?",
            "Which exhibits are listed, and what is each exhibit status?",
        ],
        answers=[
            "entity_example_inc; delaware.",
            "Exhibit 10.1 is an agreement and filed.",
        ],
        question_count=2,
    )

    report = audit_manifests(root=tmp_path, manifests=[manifest])
    md = render_markdown(report)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["manifest_count"] == 1
    assert report["summary"]["cell_count"] == 1
    assert report["summary"]["qa_file_count"] == 1
    assert "source-display questions require" in md


def test_query_micro_fixture_contract_blocks_exact_legal_name_without_display_carrier(
    tmp_path: Path,
) -> None:
    manifest = _write_query_fixture(
        tmp_path,
        questions=[
            "What is the registrant's exact legal name?",
        ],
        answers=[
            "Example Holdings Inc.",
        ],
        question_count=1,
    )

    report = audit_manifests(root=tmp_path, manifests=[manifest])

    assert report["summary"]["status"] == "fail"
    assert report["manifests"][0]["errors"] == [
        "cell_1:question_1:source_display_question_requires_typed_display_carrier:exact_legal_name"
    ]


def test_query_micro_fixture_contract_allows_display_question_with_typed_display_carrier(
    tmp_path: Path,
) -> None:
    manifest = _write_query_fixture(
        tmp_path,
        questions=[
            "What is the registrant's exact legal name?",
        ],
        answers=[
            "Example Holdings Inc.",
        ],
        question_count=1,
        typed_display_carriers=["sec_registrant_display_name/4"],
    )

    report = audit_manifests(root=tmp_path, manifests=[manifest])

    assert report["summary"]["status"] == "pass"


def test_query_micro_fixture_contract_blocks_invalid_display_carrier(tmp_path: Path) -> None:
    manifest = _write_query_fixture(
        tmp_path,
        questions=["Which `sec_registrant/4` registrant_id is compiled?"],
        answers=["entity_example_inc."],
        question_count=1,
        typed_display_carriers=["ServiceNow Inc."],
    )

    report = audit_manifests(root=tmp_path, manifests=[manifest])

    assert report["summary"]["status"] == "fail"
    assert report["manifests"][0]["errors"] == [
        "invalid_typed_display_carrier:ServiceNow Inc."
    ]


def test_query_micro_fixture_contract_blocks_count_mismatches(tmp_path: Path) -> None:
    manifest = _write_query_fixture(
        tmp_path,
        questions=[
            "Which `sec_registrant/4` registrant_id is compiled?",
            "Which exhibits are listed?",
        ],
        answers=["entity_example_inc."],
        question_count=3,
    )

    report = audit_manifests(root=tmp_path, manifests=[manifest])

    assert report["summary"]["status"] == "fail"
    assert report["manifests"][0]["errors"] == [
        "cell_1:question_count_mismatch:manifest=3:questions=2",
        "cell_1:question_answer_count_mismatch:questions=2:answers=1",
    ]


def test_query_micro_fixture_contract_blocks_missing_atom_library_flag(tmp_path: Path) -> None:
    manifest = _write_query_fixture(
        tmp_path,
        questions=["Which `sec_registrant/4` registrant_id is compiled?"],
        answers=["entity_example_inc."],
        question_count=1,
        required_runner_flags=[],
    )

    report = audit_manifests(root=tmp_path, manifests=[manifest])

    assert report["summary"]["status"] == "fail"
    assert report["manifests"][0]["errors"] == [
        "missing_required_runner_flag:--atom-library-query-grounding"
    ]


def _write_query_fixture(
    tmp_path: Path,
    *,
    questions: list[str],
    answers: list[str],
    question_count: int,
    required_runner_flags: list[str] | None = None,
    typed_display_carriers: list[str] | None = None,
) -> Path:
    fixture_root = tmp_path / "datasets" / "query_micro_fixtures" / "example_query_v1"
    fixture_root.mkdir(parents=True)
    qa_file = fixture_root / "qa.md"
    qa_file.write_text(_qa_text(questions=questions, answers=answers), encoding="utf-8")
    manifest = {
        "schema": "prethinker.query_micro_fixture_manifest.v1",
        "fixture_id": "example_atom_library_query_v1",
        "purpose": "Measure atom-library query planning.",
        "required_runner_flags": (
            ["--sign-clean-strict", "--judge-reference-answers", "--atom-library-query-grounding"]
            if required_runner_flags is None
            else required_runner_flags
        ),
        "cells": [
            {
                "id": "cell_1",
                "fixture_id": "example_fixture",
                "qa_file": "datasets/query_micro_fixtures/example_query_v1/qa.md",
                "run_json": "C:/prethinker_tmp_archive/example/domain_bootstrap_file.json",
                "question_count": question_count,
            }
        ],
    }
    if typed_display_carriers is not None:
        manifest["typed_display_carriers"] = typed_display_carriers
    manifest_path = fixture_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def _qa_text(*, questions: list[str], answers: list[str]) -> str:
    lines: list[str] = []
    lines.extend(f"{index}. {question}" for index, question in enumerate(questions, start=1))
    lines.extend(["", "## Answers", ""])
    lines.extend(f"{index}. {answer}" for index, answer in enumerate(answers, start=1))
    return "\n".join(lines) + "\n"
