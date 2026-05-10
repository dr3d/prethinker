from __future__ import annotations

from pathlib import Path

from scripts.benchmarking.plan_semantic_ab_probes import build_plan, write_probe_files


def test_build_plan_creates_four_probe_variants(tmp_path: Path) -> None:
    plan = build_plan(tmp_path)

    assert plan["schema_version"] == "semantic_ab_probe_plan_v1"
    assert len(plan["fixtures"]) == 10
    assert plan["total_rows"] == 82
    assert {fixture["probe_id"] for fixture in plan["fixtures"]} == {
        "absence_negative_evidence_vs_unresolved",
        "condition_time_vs_certification_time",
    }
    assert "distractor" in {fixture["variant_id"].split("_")[-1] for fixture in plan["fixtures"]}
    assert "hard" in {fixture["variant_id"].split("_")[-1] for fixture in plan["fixtures"]}


def test_write_probe_files_creates_source_questions_oracle(tmp_path: Path) -> None:
    plan = build_plan(tmp_path)

    write_probe_files(plan)

    first = Path(plan["fixtures"][0]["dataset_path"])
    assert (first / "source.md").exists()
    assert (first / "qa_questions.jsonl").read_text(encoding="utf-8").count("\n") == 8
    assert (first / "oracle.jsonl").read_text(encoding="utf-8").count("\n") == 8
    assert (first.parent / "probe_manifest.json").exists()
