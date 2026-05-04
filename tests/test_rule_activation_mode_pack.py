import json
from argparse import Namespace
from pathlib import Path

from scripts.run_rule_activation_mode_pack import (
    _resolve_mode_spec,
    _run_selector_report,
    _runs_by_id,
)


def _qa(path: Path, verdicts: dict[str, str], *, direct_rows: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": row_id,
                        "utterance": f"Question {row_id}?",
                        "reference_judge": {"verdict": verdict},
                        "query_results": [
                            {
                                "query": "answer_row(X).",
                                "result": {
                                    "status": "success" if direct_rows else "no_results",
                                    "predicate": "answer_row",
                                    "num_rows": direct_rows,
                                    "rows": [{"X": row_id}] if direct_rows else [],
                                },
                            }
                        ],
                    }
                    for row_id, verdict in verdicts.items()
                ]
            }
        ),
        encoding="utf-8",
    )


def test_resolve_mode_spec_finds_nested_qa_artifact(tmp_path: Path) -> None:
    qa_path = tmp_path / "qa.json"
    _qa(qa_path, {"q1": "exact"})
    runs = {
        "R-001": {
            "run_id": "R-001",
            "mode": "baseline",
            "evidence_lane": "cold_unseen",
            "qa": {"judge_exact": 1, "judge_partial": 0, "judge_miss": 0},
            "local_artifacts": {"qa_json": str(qa_path)},
        },
        "R-002": {
            "run_id": "R-002",
            "mode": "rule_union",
            "evidence_lane": "diagnostic_replay",
            "qa": {
                "artifact": str(qa_path),
                "judge_exact": 1,
                "judge_partial": 0,
                "judge_miss": 0,
            },
        },
    }

    baseline = _resolve_mode_spec("baseline=R-001", runs=runs)
    rule_union = _resolve_mode_spec("rule_union=R-002:qa.artifact", runs=runs)

    assert baseline["artifact_exists"] is True
    assert baseline["artifact_key"] == "auto"
    assert rule_union["artifact_exists"] is True
    assert rule_union["artifact_key"] == "qa.artifact"


def test_runs_by_id_reads_progress_metrics(tmp_path: Path) -> None:
    metrics = tmp_path / "progress_metrics.jsonl"
    metrics.write_text(
        '{"run_id":"R-001","evidence_lane":"cold_unseen"}\n'
        '{"run_id":"R-002","evidence_lane":"diagnostic_replay"}\n',
        encoding="utf-8",
    )

    runs = _runs_by_id(metrics)

    assert sorted(runs) == ["R-001", "R-002"]


def test_rule_activation_selector_report_can_run_structurally(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline.json"
    rule_path = tmp_path / "rule.json"
    _qa(baseline_path, {"q1": "miss"}, direct_rows=0)
    _qa(rule_path, {"q1": "exact"}, direct_rows=2)
    group = {
        "name": "toy",
        "labels": ["baseline", "rule_union"],
        "artifacts": [
            {"label": "baseline", "path": baseline_path, "record": json.loads(baseline_path.read_text())},
            {"label": "rule_union", "path": rule_path, "record": json.loads(rule_path.read_text())},
        ],
    }
    args = Namespace(
        selector_policy="structural",
        hybrid_llm_policy="direct",
        hybrid_margin=1.5,
        hybrid_min_score=3.0,
        base_url="http://127.0.0.1:1234/v1",
        model="unused",
        timeout=1,
        temperature=0.0,
        top_p=1.0,
        max_tokens=100,
        sample_row_limit=12,
        include_self_check=False,
    )

    report = _run_selector_report(group=group, args=args)

    assert report["summary"]["selected_exact"] == 1
    assert report["summary"]["selected_best_count"] == 1
    assert report["rows"][0]["selected_mode"] == "rule_union"
