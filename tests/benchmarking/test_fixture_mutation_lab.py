from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmarking.plan_fixture_mutation_lab import (
    _international_dates,
    _multilingual_headings,
    _split_battery_rows,
    _telegraphic_grammar,
    _typo_noise,
    _wrap_questions,
    build_mutation_lab_plan,
)


def test_split_battery_rows_creates_questions_and_oracle() -> None:
    questions, oracle = _split_battery_rows(
        [
            {
                "id": "TV-001",
                "category": "lookup",
                "question": "Who?",
                "answer": "Ada.",
            }
        ],
        source_id="fixture",
    )

    assert questions == [{"id": "TV-001", "question": "Who?", "category": "lookup", "source_id": "fixture"}]
    assert oracle == [{"id": "TV-001", "reference_answer": "Ada.", "category": "lookup", "source_id": "fixture"}]


def test_mutation_lab_plan_records_platforms_and_oracle_policy(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    fixture = repo / "datasets" / "story_worlds" / "demo_fixture"
    fixture.mkdir(parents=True)
    (fixture / "source.md").write_text("# Demo\n\n## A\nOne.\n\n## B\nTwo.", encoding="utf-8")
    (fixture / "qa_questions.jsonl").write_text(
        '{"id":"q001","question":"What?","category":"lookup"}\n',
        encoding="utf-8",
    )
    (fixture / "oracle.jsonl").write_text(
        '{"id":"q001","reference_answer":"One.","category":"lookup"}\n',
        encoding="utf-8",
    )

    import scripts.benchmarking.plan_fixture_mutation_lab as module

    monkeypatch.setattr(module, "REPO_ROOT", repo)

    plan = build_mutation_lab_plan(
        fixtures=["demo_fixture"],
        out_dir=tmp_path / "out",
        runs_per_model=1,
        rows_per_fixture=1,
    )

    assert plan["runner_plan"]["expected_rows_per_model"] == 13
    assert any(platform["platform"] == "POWER" for platform in plan["recipe_artifact"]["execution_platforms"])
    assert all(recipe["answer_oracle_policy"] == "unchanged_oracle_reused" for recipe in plan["recipe_artifact"]["recipes"])
    assert plan["recipe_artifact"]["semantic_perturbation_candidates"]
    synthetic_dir = Path(plan["runner_plan"]["fixtures"][0]["dataset_path"])
    assert json.loads((synthetic_dir / "oracle.jsonl").read_text(encoding="utf-8"))["reference_answer"] == "One."


def test_perception_mangles_are_deterministic_and_oracle_preserving() -> None:
    source = "# Packet\n\n## Evidence\nThe investigation was authorized on 2026-04-17 under TICKET-2026-04-17-001."

    assert "investigatoin" in _typo_noise(source, heavy=False)
    assert "17 Apr 2026" in _international_dates(source)
    assert "TICKET-2026-04-17-001" in _international_dates(source)
    assert "Seccion: Packet" in _multilingual_headings(source)
    assert " the " not in f" {_telegraphic_grammar(source).casefold()} "


def test_question_wrappers_preserve_question_ids_and_categories() -> None:
    wrapped = _wrap_questions(
        [{"id": "q001", "question": "Who compiled it?", "category": "lookup"}],
        "Pregunta / Question",
    )

    assert wrapped[0]["id"] == "q001"
    assert wrapped[0]["category"] == "lookup"
    assert wrapped[0]["question"] == "Pregunta / Question: Who compiled it?"
