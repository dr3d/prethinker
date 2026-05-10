from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmarking.plan_axis2_context_probe import build_axis2_plan
from scripts.benchmarking.summarize_axis2_context_probe import summarize


def test_axis2_plan_builds_synthetic_assemblies_with_target_oracle(tmp_path: Path) -> None:
    fixtures = []
    for name in [
        "contradictory_evidence_packet",
        "rule_activation_exception_matrix",
        "hospital_shift_exception_log",
        "authority_possession_custody_packet",
        "count_composition_roster",
    ]:
        fixture_dir = tmp_path / name
        fixture_dir.mkdir()
        (fixture_dir / "source.md").write_text(f"{name} source body.", encoding="utf-8")
        (fixture_dir / "qa_questions.jsonl").write_text(
            '{"id":"q001","question":"What?","category":"lookup"}\n',
            encoding="utf-8",
        )
        (fixture_dir / "oracle.jsonl").write_text(
            '{"id":"q001","reference_answer":"Answer."}\n',
            encoding="utf-8",
        )
        fixtures.append(
            {
                "fixture": name,
                "dataset_path": str(fixture_dir),
                "source_file": "source.md",
                "question_file": "qa_questions.jsonl",
                "scoring_file": "oracle.jsonl",
                "question_count": 1,
                "oracle_count": 1,
                "planned_rows": 1,
            }
        )

    plan = build_axis2_plan(
        {"prompt_contract": {"system": "s"}, "run_settings": {"runs_per_model": 3}, "fixtures": fixtures},
        out_dir=tmp_path / "axis2",
        target_fixture="contradictory_evidence_packet",
        runs_per_model=2,
        rows_per_fixture=1,
    )

    runner_plan = plan["runner_plan"]
    recipes = plan["recipe_artifact"]["recipes"]

    assert len(runner_plan["fixtures"]) == 4
    assert runner_plan["expected_rows_per_model"] == 8
    assert {recipe["condition"] for recipe in recipes} == {
        "standalone",
        "stuffed_first",
        "stuffed_middle",
        "stuffed_last",
    }
    for fixture in runner_plan["fixtures"]:
        dataset_path = Path(str(fixture["dataset_path"]))
        assert (dataset_path / "source.md").exists()
        assert json.loads((dataset_path / "oracle.jsonl").read_text(encoding="utf-8"))["reference_answer"] == "Answer."
        assert "Answer." not in (dataset_path / "source.md").read_text(encoding="utf-8")


def test_axis2_summary_reports_condition_delta() -> None:
    rows = [
        _row("model-a", "target__standalone", "q001", "lookup", "exact"),
        _row("model-a", "target__standalone", "q001", "lookup", "exact"),
        _row("model-a", "target__stuffed_last", "q001", "lookup", "exact"),
        _row("model-a", "target__stuffed_last", "q001", "lookup", "miss"),
    ]
    recipes = {
        "target_fixture": "target",
        "recipes": [
            {"assembly_id": "target__standalone", "condition": "standalone", "target_position": 1},
            {"assembly_id": "target__stuffed_last", "condition": "stuffed_last", "target_position": 5},
        ],
    }

    summary = summarize(rows, recipes=recipes)
    model = summary["models"][0]
    stuffed = next(item for item in model["conditions"] if item["name"] == "stuffed_last")

    assert stuffed["exact_rate_judged"] == 0.5
    assert stuffed["delta_from_standalone_exact_judged"] == -0.5
    assert model["question_flips"][0]["delta"] == -0.5


def _row(model: str, fixture: str, question_id: str, category: str, verdict: str) -> dict[str, object]:
    return {
        "model": model,
        "fixture": fixture,
        "question_id": question_id,
        "category": category,
        "reference_judge": {"verdict": verdict},
    }
