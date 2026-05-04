from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import types
from pathlib import Path

from src.kb_pipeline_clean.parity_harness import (
    canonical_compiler_trace,
    canonical_process_result,
    compare_signatures,
    normalizer_inventory_audit,
)
from src.kb_pipeline_clean.instrument import instrument_manifest, render_instrument_markdown
from src.kb_pipeline_clean.parse_normalization import NORMALIZER_PIPELINE


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_kb_pipeline_clean_harness.py"
SPEC = importlib.util.spec_from_file_location("run_kb_pipeline_clean_harness", SCRIPT_PATH)
assert SPEC and SPEC.loader
HARNESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARNESS)


def test_canonical_process_result_tracks_front_door_and_execution_shape() -> None:
    result = {
        "status": "success",
        "result_type": "process_utterance",
        "front_door": {
            "route": "commit",
            "compiler_intent": "assert_rule",
            "needs_clarification": False,
            "ambiguity_score": 0.123456,
        },
        "execution": {
            "status": "success",
            "intent": "assert_rule",
            "writes_applied": 2,
            "operations": [
                {"tool": "assert_fact", "clause": "parent(alice, bob).", "result": {"status": "success"}},
                {"tool": "assert_rule", "clause": "ancestor(X, Y) :- parent(X, Y).", "result": {"status": "success"}},
                {
                    "tool": "query_rows",
                    "query": "ancestor(alice, bob).",
                    "result": {
                        "status": "success",
                        "result_type": "query",
                        "prolog_query": "ancestor(alice, bob).",
                        "num_rows": 1,
                        "rows": [{"Y": "bob", "X": "alice"}],
                    },
                },
            ],
            "query_result": {
                "status": "success",
                "prolog_query": "ancestor(alice, bob).",
                "num_rows": 1,
                "rows": [{"Y": "bob", "X": "alice"}],
            },
        },
        "compiler_trace": {
            "summary": {
                "route": "commit",
                "compiler_intent": "assert_rule",
                "needs_clarification": False,
                "prethink_source": "compiler",
            },
            "semantic_ir": {"schema_version": "semantic_ir_v1"},
        },
    }

    signature = canonical_process_result(result)

    assert signature["front_door"]["ambiguity_score"] == 0.1235
    assert signature["execution"]["operation_tools"] == ["assert_fact", "assert_rule", "query_rows"]
    assert signature["execution"]["query_result"]["rows"] == [{"Y": "bob", "X": "alice"}]
    assert signature["compiler_trace"]["semantic_ir_schema"] == "semantic_ir_v1"


def test_compare_signatures_reports_path_oriented_diffs() -> None:
    baseline = {"execution": {"writes_applied": 2, "operation_tools": ["assert_fact", "query_rows"]}}
    candidate = {"execution": {"writes_applied": 1, "operation_tools": ["assert_fact"]}}

    comparison = compare_signatures(baseline, candidate)

    assert comparison["status"] == "fail"
    paths = {row["path"] for row in comparison["diffs"]}
    assert "execution.writes_applied" in paths
    assert "execution.operation_tools[1]" in paths


def test_canonical_compiler_trace_detects_nested_semantic_ir() -> None:
    trace = {
        "summary": {"route": "query", "compiler_intent": "query"},
        "parse": {"semantic_ir": {"parsed": {"schema_version": "semantic_ir_v1"}}},
    }

    signature = canonical_compiler_trace(trace)

    assert signature["semantic_ir_present"] is True
    assert signature["semantic_ir_schema"] == "semantic_ir_v1"


def test_normalizer_inventory_audit_rejects_fixture_named_new_specs() -> None:
    fake = types.ModuleType("fake_kb_pipeline_for_clean_harness")
    for spec in NORMALIZER_PIPELINE:
        for symbol in spec.legacy_symbols:
            setattr(fake, symbol, object())
    sys.modules[fake.__name__] = fake

    audit = normalizer_inventory_audit(fake.__name__)

    assert audit["status"] == "pass"
    assert audit["missing_legacy_symbols"] == []
    assert audit["duplicate_legacy_symbols"] == []
    assert audit["fixture_named_new_specs"] == []


def test_instrument_manifest_names_daily_driver_controls() -> None:
    manifest = instrument_manifest()

    controls = {row["name"]: row for row in manifest["control_surfaces"]}
    assert manifest["role"] == "daily_driver_research_instrument"
    assert "process_replay" in controls
    assert "normalizer_audit" in controls
    assert controls["process_replay"]["writes"]
    assert "wrap -> replay -> extract -> compare -> retire" == manifest["next_extraction_rule"]


def test_instrument_markdown_renders_operator_surface() -> None:
    markdown = render_instrument_markdown()

    assert "# Current Harness Instrument" in markdown
    assert "Authority Boundary" in markdown
    assert "process_replay" in markdown
    assert "wrap -> replay -> extract -> compare -> retire" in markdown


def test_scenario_cli_can_run_direct_trace_plan() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "docs/refactor_proposals/kb_pipeline_clean/scenario_cli.py",
            "--trace-plan",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    plan = json.loads(completed.stdout)
    names = {row["normalizer"] for row in plan}
    assert "nested_event_observation_normalizer" in names
    assert "story_world_observation_normalizer" not in names


def test_daily_driver_cli_prints_instrument_manifest() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_kb_pipeline_clean_harness.py",
            "--instrument-manifest",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    manifest = json.loads(completed.stdout)
    assert manifest["schema_version"] == "kb_pipeline_clean_instrument_v1"
    assert manifest["role"] == "daily_driver_research_instrument"


def test_docs_proposal_imports_promoted_harness_surface() -> None:
    from docs.refactor_proposals.kb_pipeline_clean.parity_harness import canonical_process_result as docs_canonical
    from docs.refactor_proposals.kb_pipeline_clean.parse_normalization import trace_plan as docs_trace_plan

    assert docs_canonical is canonical_process_result
    assert docs_trace_plan()[0]["normalizer"] == "schema_field_normalizer"


def test_daily_driver_replay_process_case_emits_signature_and_comparison() -> None:
    calls = []

    def run_turn(
        utterance: str,
        context: list[str] | None = None,
        clarification_answer: str = "",
        prethink_id: str = "",
    ) -> dict:
        calls.append((utterance, context or [], clarification_answer, prethink_id))
        return {
            "status": "success",
            "result_type": "utterance_processed",
            "front_door": {
                "route": "commit",
                "compiler_intent": "assert_fact",
                "needs_clarification": False,
            },
            "execution": {
                "status": "success",
                "intent": "assert_fact",
                "writes_applied": 1,
                "operations": [
                    {
                        "tool": "assert_fact",
                        "clause": "parent(alice, bob).",
                        "result": {"status": "success"},
                    }
                ],
            },
        }

    baseline = canonical_process_result(run_turn("Alice is Bob's parent."))
    calls.clear()
    record = HARNESS.replay_process_case(
        case={
            "id": "parent_fact",
            "utterance": "Alice is Bob's parent.",
            "context": ["Family relation memory."],
            "canonical_signature": baseline,
        },
        index=1,
        run_turn=run_turn,
    )

    assert calls == [("Alice is Bob's parent.", ["Family relation memory."], "", "")]
    assert record["case_id"] == "parent_fact"
    assert record["context"] == ["Family relation memory."]
    assert record["comparison"]["status"] == "pass"
    assert record["canonical_signature"]["execution"]["operation_tools"] == ["assert_fact"]


def test_daily_driver_replay_pack_counts_comparisons() -> None:
    pack = {"pack_id": "tiny", "cases": [{"case_id": "a"}, {"case_id": "b"}]}

    def run_case(case: dict, index: int) -> dict:
        return {
            "case_id": case["case_id"],
            "status": "success",
            "result_type": "utterance_processed",
            "comparison": {"status": "no_baseline" if index == 1 else "pass"},
        }

    summary = HARNESS.replay_process_pack(pack=pack, run_case=run_case)

    assert summary["cases_total"] == 2
    assert summary["status_counts"] == {"success": 2}
    assert summary["comparison_counts"] == {"no_baseline": 1, "pass": 1}
