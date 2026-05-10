from __future__ import annotations

from pathlib import Path

from scripts.benchmarking.plan_semantic_ab_probes import build_plan as build_semantic_plan
from scripts.benchmarking.plan_semantic_ab_probes import write_probe_files
from scripts.benchmarking.plan_semantic_axis2_probe import build_plan


def test_build_plan_creates_axis2_conditions_for_hard_absence(tmp_path: Path) -> None:
    semantic_root = tmp_path / "semantic"
    semantic_plan = build_semantic_plan(semantic_root)
    write_probe_files(semantic_plan)

    plan = build_plan(semantic_plan, out_dir=tmp_path / "axis2", runs_per_model=1)

    fixtures = plan["runner_plan"]["fixtures"]
    assert len(fixtures) == 8
    assert plan["runner_plan"]["expected_rows_per_model"] == 72
    assert {fixture["semantic_axis2_condition"] for fixture in fixtures} == {
        "standalone",
        "stuffed_first",
        "stuffed_middle",
        "stuffed_last",
    }
    assert all((Path(fixture["dataset_path"]) / "source.md").exists() for fixture in fixtures)
