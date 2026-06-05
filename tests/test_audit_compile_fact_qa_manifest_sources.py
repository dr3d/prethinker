import json
from pathlib import Path

import scripts.audit_compile_fact_qa_manifest_sources as source_audit
from scripts.audit_compile_fact_qa_manifest_sources import audit_manifest


def test_audit_compile_fact_manifest_sources_accepts_manifested_bundle(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    _write_bundle_compile_json(bundle, "run1")
    _write_bundle_compile_json(bundle, "run2")
    _write_bundle_compile_json(bundle, "run3")
    _write_score_report(bundle)
    (bundle / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "domain_lens_bundle_run_v1",
                "repeat": 3,
                "runs": [{"cycle": 1}, {"cycle": 2}, {"cycle": 3}],
                "lens_atom_audit_summary": _atom_gate_summary(),
                "union_atom_audit_summary": _atom_gate_summary(),
                "settings": {
                    "backend": "lmstudio",
                    "model": "qwen/qwen3.6-35b-a3b",
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "num_ctx": 65536,
                    "max_tokens": 12000,
                    "timeout": 420,
                    "support_threshold": 2,
                    "matcher": "constant_slot",
                },
            }
        ),
        encoding="utf-8",
    )
    manifest = _write_manifest(tmp_path, bundle)

    report = audit_manifest(manifest)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["warning_count"] == 0
    assert report["cells"][0]["run_count"] == 3
    assert report["cells"][0]["effective_settings"]["model"] == "qwen/qwen3.6-35b-a3b"
    assert report["cells"][0]["gate_summaries"]["lens_atom_audit_summary"]["status"] == "pass"
    assert report["cells"][0]["artifact_gate_summaries"]["lens_atom_inventory"]["status"] == "pass"


def test_audit_compile_fact_manifest_sources_recovers_legacy_bundle_metadata(tmp_path: Path) -> None:
    bundle = tmp_path / "legacy_bundle"
    _write_flat_bundle_compile_json(bundle, "run1")
    _write_flat_bundle_compile_json(bundle, "run2")
    _write_flat_bundle_compile_json(bundle, "run3")
    _write_score_report(bundle)
    manifest = _write_manifest(tmp_path, bundle)

    report = audit_manifest(manifest)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["warning_count"] == 1
    assert report["cells"][0]["bundle_manifest_status"] == "missing_recovered_from_compile_json"
    assert report["cells"][0]["effective_settings"]["support_threshold"] == 2
    assert report["cells"][0]["setting_sources"]["support_threshold"] == "score_report"


def test_audit_compile_fact_manifest_sources_blocks_missing_root(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path, tmp_path / "missing_bundle")

    report = audit_manifest(manifest)

    assert report["summary"]["status"] == "fail"
    assert any("domain_lens_bundle_missing" in reason for reason in report["summary"]["blocking_reasons"])


def test_audit_compile_fact_manifest_sources_blocks_mixed_compile_settings(tmp_path: Path) -> None:
    bundle = tmp_path / "mixed_bundle"
    _write_bundle_compile_json(bundle, "run1", model="qwen/qwen3.6-35b-a3b")
    _write_bundle_compile_json(bundle, "run2", model="qwen/qwen3.6-35b-a3b")
    _write_bundle_compile_json(bundle, "run3", model="other/model")
    _write_score_report(bundle)
    manifest = _write_manifest(tmp_path, bundle)

    report = audit_manifest(manifest)

    assert report["summary"]["status"] == "fail"
    assert any("mixed_compile_setting:model" in reason for reason in report["summary"]["blocking_reasons"])


def test_audit_compile_fact_manifest_sources_blocks_failed_bundle_atom_gate(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    _write_bundle_compile_json(bundle, "run1")
    _write_bundle_compile_json(bundle, "run2")
    _write_bundle_compile_json(bundle, "run3")
    _write_score_report(bundle)
    (bundle / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "domain_lens_bundle_run_v1",
                "repeat": 3,
                "runs": [{"cycle": 1}, {"cycle": 2}, {"cycle": 3}],
                "lens_atom_audit_summary": _atom_gate_summary(atom_shape_blocker_count=1),
                "union_atom_audit_summary": _atom_gate_summary(),
                "settings": {
                    "backend": "lmstudio",
                    "model": "qwen/qwen3.6-35b-a3b",
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "num_ctx": 65536,
                    "max_tokens": 12000,
                    "timeout": 420,
                    "support_threshold": 2,
                    "matcher": "constant_slot",
                },
            }
        ),
        encoding="utf-8",
    )
    manifest = _write_manifest(tmp_path, bundle)

    report = audit_manifest(manifest)

    assert report["summary"]["status"] == "fail"
    assert any(
        "lens_atom_audit_summary:atom_shape_blocker_count_nonzero:1" in reason
        for reason in report["summary"]["blocking_reasons"]
    )


def test_audit_compile_fact_manifest_sources_replays_artifact_atom_gate(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    _write_bundle_compile_json(bundle, "run1", facts=["unregistered_fact(a)."])
    _write_bundle_compile_json(bundle, "run2")
    _write_bundle_compile_json(bundle, "run3")
    _write_score_report(bundle)
    (bundle / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "domain_lens_bundle_run_v1",
                "repeat": 3,
                "runs": [{"cycle": 1}, {"cycle": 2}, {"cycle": 3}],
                "lens_atom_audit_summary": _atom_gate_summary(),
                "union_atom_audit_summary": _atom_gate_summary(),
                "settings": {
                    "backend": "lmstudio",
                    "model": "qwen/qwen3.6-35b-a3b",
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "num_ctx": 65536,
                    "max_tokens": 12000,
                    "timeout": 420,
                    "support_threshold": 2,
                    "matcher": "constant_slot",
                },
            }
        ),
        encoding="utf-8",
    )
    manifest = _write_manifest(tmp_path, bundle)

    report = audit_manifest(manifest)

    assert report["summary"]["status"] == "fail"
    assert any(
        "lens_atom_inventory:unregistered_fact_count_nonzero" in reason
        for reason in report["summary"]["blocking_reasons"]
    )


def test_audit_compile_fact_manifest_sources_blocks_repo_tmp_claim_roots(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = tmp_path / "repo"
    bundle = repo_root / "tmp" / "bundle"
    _write_bundle_compile_json(bundle, "run1")
    _write_bundle_compile_json(bundle, "run2")
    _write_bundle_compile_json(bundle, "run3")
    _write_score_report(bundle)
    manifest = _write_manifest(tmp_path, bundle)
    monkeypatch.setattr(source_audit, "REPO_ROOT", repo_root)

    report = source_audit.audit_manifest(manifest)

    assert report["summary"]["status"] == "fail"
    assert any(
        "claim_bearing_bundle_under_repo_tmp" in reason for reason in report["summary"]["blocking_reasons"]
    )


def _write_manifest(tmp_path: Path, bundle: Path) -> Path:
    manifest = tmp_path / "claim_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "prethinker.compile_fact_qa_manifest.v1",
                "cells": [
                    {
                        "id": "cell_a",
                        "fixture_id": "fixture_a",
                        "domain_lens_bundle": str(bundle),
                        "expect": {"support.exact_support_ge_2": 1},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return manifest


def _write_bundle_compile_json(
    bundle: Path,
    run_id: str,
    *,
    model: str = "qwen/qwen3.6-35b-a3b",
    facts: list[str] | None = None,
) -> None:
    run_dir = bundle / "unions" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = _compile_payload(model=model, facts=facts or [])
    (run_dir / "compile.json").write_text(json.dumps(payload), encoding="utf-8")
    lens_dir = bundle / "lens_compiles" / run_id / "wrapper"
    lens_dir.mkdir(parents=True, exist_ok=True)
    (lens_dir / "compile.json").write_text(json.dumps(payload), encoding="utf-8")


def _write_flat_bundle_compile_json(bundle: Path, run_id: str) -> None:
    union_dir = bundle / "unions"
    union_dir.mkdir(parents=True, exist_ok=True)
    (union_dir / f"bundle-{run_id}.json").write_text(
        json.dumps(_compile_payload(model="qwen/qwen3.6-35b-a3b")),
        encoding="utf-8",
    )


def _write_score_report(bundle: Path) -> None:
    report_dir = bundle / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "typed_micro_series_summary.json").write_text(
        json.dumps({"support_threshold": 2, "matcher": "constant_slot"}),
        encoding="utf-8",
    )


def _atom_gate_summary(**overrides: int) -> dict[str, int]:
    payload = {
        "atom_shape_blocker_count": 0,
        "lens_scope_blocker_count": 0,
        "unregistered_fact_count": 0,
    }
    payload.update(overrides)
    return payload


def _compile_payload(*, model: str, facts: list[str] | None = None) -> dict:
    return {
        "backend": "lmstudio",
        "model": model,
        "model_serving_path": {
            "base_url": "http://127.0.0.1:1234",
            "decoding": {
                "context_length": 65536,
                "max_tokens": 12000,
                "temperature": 0.0,
                "top_k_requested": 20,
                "top_p": 1.0,
            },
            "execution": {"timeout_seconds": 420},
            "model": model,
            "observed_runtime": {"api_v0_model": {"quantization": "Q4_K_M"}},
            "provider_family": "local_lmstudio",
            "transport_backend": "lmstudio",
        },
        "source_compile": {"facts": facts or []},
    }
