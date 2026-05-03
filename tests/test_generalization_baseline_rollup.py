import json
from pathlib import Path

from scripts.summarize_generalization_baselines import build_rollup, collect_runs, render_markdown


ROOT = Path(__file__).resolve().parents[1]


def test_collect_cold_unseen_generalization_runs() -> None:
    runs = collect_runs(ROOT / "datasets", "cold_unseen")
    run_ids = {run["run_id"] for run in runs}

    assert {"MMM-001", "V9-001", "RF-001", "CAL-001", "BLM-001"}.issubset(run_ids)
    assert all(run["evidence_lane"] == "cold_unseen" for run in runs)
    assert all(run["qa_artifact"] for run in runs)


def test_cold_rollup_preserves_failure_surface_counts() -> None:
    runs = collect_runs(ROOT / "datasets", "cold_unseen")
    rollup = build_rollup(runs, "cold_unseen")

    assert rollup["run_count"] >= 5
    assert rollup["verdict_counts"]["exact"] >= 100
    assert rollup["surface_counts"]["compile_surface_gap"] >= 90
    assert rollup["surface_counts"]["hybrid_join_gap"] >= 20
    assert "Reads progress_metrics.jsonl and QA artifacts only." in rollup["policy"]


def test_cold_rollup_markdown_is_public_readable() -> None:
    runs = collect_runs(ROOT / "datasets", "cold_unseen")
    markdown = render_markdown(build_rollup(runs, "cold_unseen"))

    assert "# Cold Baseline Failure Rollup" in markdown
    assert "## Cross-Fixture Failure Surfaces" in markdown
    assert "Compile gaps dominate the cold set" in markdown
    assert "source prose" in markdown


def test_generated_failure_rollup_json_is_valid_if_present() -> None:
    path = ROOT / "tmp" / "cold_baselines" / "failure_rollup.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "cold_baseline_failure_rollup_v1"
