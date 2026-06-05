import json
from pathlib import Path

from scripts.summarize_query_grounding_status import build_report, render_markdown


def test_query_grounding_status_summarizes_retained_artifacts(tmp_path: Path) -> None:
    artifact = _artifact(
        tmp_path,
        redaction_rows=[
            _redaction_row("q001", thesis_verdict="survived"),
            _redaction_row("q002", thesis_verdict="survived"),
        ],
        typed_rows=[
            _typed_row("q001"),
            _typed_row("q002"),
        ],
    )
    manifest = _manifest(
        tmp_path,
        artifact,
        expect={
            "row_count": 2,
            "product_exact": 2,
            "typed_plan_exact": 2,
            "redaction_survived": 2,
            "prose_dependent_exact": 0,
            "unregistered_plan_exact_rows": 0,
            "blocked_source_record_plan_rows": 0,
            "runtime_load_error_rows": 0,
        },
    )

    report = build_report(manifest)
    md = render_markdown(report)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["product_exact"] == 2
    assert report["summary"]["typed_plan_exact"] == 2
    assert report["summary"]["redaction_survived"] == 2
    assert report["cells"][0]["metadata"]["quantizations"] == ["Q4_K_M"]
    assert "Query Grounding Status" in md
    assert "qwen/qwen3.6-35b-a3b" in md


def test_query_grounding_status_blocks_expectation_mismatch(tmp_path: Path) -> None:
    artifact = _artifact(
        tmp_path,
        redaction_rows=[
            _redaction_row("q001", thesis_verdict="survived"),
            _redaction_row("q002", thesis_verdict="prose_dependent"),
        ],
        typed_rows=[
            _typed_row("q001"),
            _typed_row("q002", unregistered=1),
        ],
    )
    manifest = _manifest(
        tmp_path,
        artifact,
        expect={
            "row_count": 2,
            "product_exact": 2,
            "typed_plan_exact": 2,
            "redaction_survived": 2,
            "prose_dependent_exact": 0,
            "unregistered_plan_exact_rows": 0,
            "blocked_source_record_plan_rows": 0,
            "runtime_load_error_rows": 0,
        },
    )

    report = build_report(manifest)

    assert report["summary"]["status"] == "fail"
    errors = report["cells"][0]["errors"]
    assert "expectation_mismatch:typed_plan_exact:expected_2:actual_1" in errors
    assert "expectation_mismatch:redaction_survived:expected_2:actual_1" in errors
    assert "expectation_mismatch:prose_dependent_exact:expected_0:actual_1" in errors
    assert "expectation_mismatch:unregistered_plan_exact_rows:expected_0:actual_1" in errors


def _artifact(tmp_path: Path, *, redaction_rows: list[dict], typed_rows: list[dict]) -> Path:
    artifact = tmp_path / "artifact"
    query_dir = artifact / "demo_query"
    query_dir.mkdir(parents=True)
    (artifact / "redaction_replay.json").write_text(
        json.dumps({"rows": redaction_rows}) + "\n",
        encoding="utf-8",
    )
    (artifact / "typed_plan_replay.json").write_text(
        json.dumps({"rows": typed_rows}) + "\n",
        encoding="utf-8",
    )
    (query_dir / "domain_bootstrap_qa_demo.json").write_text(
        json.dumps(
            {
                "model": "qwen/qwen3.6-35b-a3b",
                "model_serving_path": {
                    "model": "qwen/qwen3.6-35b-a3b",
                    "provider_family": "local_lmstudio",
                    "decoding": {
                        "context_length": 32768,
                        "temperature": 0.0,
                        "top_p": 0.82,
                    },
                    "observed_runtime": {
                        "api_v0_model": {
                            "loaded_context_length": 65536,
                            "quantization": "Q4_K_M",
                        }
                    },
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return artifact


def _manifest(tmp_path: Path, artifact: Path, *, expect: dict) -> Path:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "prethinker.current_query_grounding_manifest.v1",
                "cells": [
                    {
                        "id": "demo_query",
                        "query_packet": "demo_packet",
                        "artifact_root": str(artifact),
                        "expect": expect,
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def _redaction_row(row_id: str, *, thesis_verdict: str) -> dict:
    return {
        "id": row_id,
        "product_verdict": "exact",
        "thesis_verdict": thesis_verdict,
    }


def _typed_row(row_id: str, *, unregistered: int = 0) -> dict:
    return {
        "id": row_id,
        "product_verdict": "exact",
        "status": "all_queries_success",
        "queries": ["demo_fact(X)."],
        "unregistered_query_signature_count": unregistered,
    }
