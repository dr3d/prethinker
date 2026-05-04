"""Instrument manifest for the clean KB pipeline harness.

The harness is treated as a research instrument: named controls, calibrated
outputs, explicit provenance, and guardrails that keep Python structural.
"""

from __future__ import annotations

from typing import Any


INSTRUMENT_VERSION = "kb_pipeline_clean_instrument_v1"


def instrument_manifest() -> dict[str, Any]:
    """Return the operator-facing manifest for the clean harness."""

    return {
        "schema_version": INSTRUMENT_VERSION,
        "name": "KB Pipeline Clean Harness",
        "role": "daily_driver_research_instrument",
        "purpose": (
            "Replay live Prethinker behavior, capture canonical structural signatures, "
            "and make compiler/gate/apply extraction readable and testable."
        ),
        "authority_boundary": [
            "Live behavior remains owned by src.mcp_server.PrologMCPServer.process_utterance until extracted behind parity checks.",
            "Python may normalize structured payloads, traces, clauses, and result records.",
            "Python must not infer source-language meaning from raw prose.",
            "Selector and transfer summaries choose among existing evidence artifacts only; they have no write authority.",
        ],
        "control_surfaces": [
            {
                "name": "trace_plan",
                "command": "python scripts/run_kb_pipeline_clean_harness.py --trace-plan",
                "reason": "Shows the ordered structural normalizer inventory and migration labels.",
                "reads": ["src/kb_pipeline_clean/parse_normalization.py"],
                "writes": [],
            },
            {
                "name": "normalizer_audit",
                "command": "python scripts/run_kb_pipeline_clean_harness.py --audit-normalizers",
                "reason": "Checks that proposed normalizer homes map to live legacy symbols without fixture-named new specs.",
                "reads": ["src/kb_pipeline_clean/parse_normalization.py", "kb_pipeline.py"],
                "writes": [],
            },
            {
                "name": "process_replay",
                "command": "python scripts/run_kb_pipeline_clean_harness.py --pack <pack.json>",
                "reason": "Runs live process_utterance and captures raw results plus canonical signatures.",
                "reads": ["pack JSON", "src/mcp_server.py"],
                "writes": ["tmp/runs/kb_pipeline_clean_harness/<run>/summary.json", "tmp/runs/kb_pipeline_clean_harness/<run>/cases/*.json"],
            },
            {
                "name": "signature_compare",
                "command": "python docs/refactor_proposals/kb_pipeline_clean/scenario_cli.py --compare <baseline.json> <candidate.json>",
                "reason": "Diffs canonical signatures by structural path for extraction parity.",
                "reads": ["canonical signature JSON"],
                "writes": [],
            },
            {
                "name": "story_world_rule_activation_transfer",
                "command": "python scripts/summarize_rule_activation_transfer.py --comparison <label=mode_comparison.json>",
                "reason": "Summarizes Sable/Avalon-style activation rescues, regressions, and volatile rows.",
                "reads": ["rule activation mode-comparison JSON"],
                "writes": ["tmp/rule_activation_transfer/*.json", "tmp/rule_activation_transfer/*.md"],
            },
        ],
        "canonical_outputs": [
            {
                "name": "canonical_process_signature",
                "producer": "src.kb_pipeline_clean.canonical_process_result",
                "fields": ["status", "result_type", "front_door", "execution", "compiler_trace"],
                "calibration_use": "Pins process_utterance shape across compiler/gate/apply extraction.",
            },
            {
                "name": "canonical_execution_signature",
                "producer": "src.kb_pipeline_clean.canonical_execution_result",
                "fields": ["status", "intent", "writes_applied", "operation_tools", "operations", "query_result", "errors"],
                "calibration_use": "Pins deterministic KB mutation/query result shape.",
            },
            {
                "name": "normalizer_trace_plan",
                "producer": "src.kb_pipeline_clean.trace_plan",
                "fields": ["phase", "normalizer", "trace_event", "legacy_symbols", "operates_on"],
                "calibration_use": "Keeps migration names tied to guardrail reasons rather than fixture history.",
            },
        ],
        "docs": [
            "docs/CURRENT_HARNESS_INSTRUMENT.md",
            "docs/ACTIVE_RESEARCH_LANES.md",
            "docs/refactor_proposals/kb_pipeline_clean/README.md",
            "docs/refactor_proposals/kb_pipeline_clean/MIGRATION_MATRIX.md",
        ],
        "next_extraction_rule": "wrap -> replay -> extract -> compare -> retire",
    }


def render_instrument_markdown(manifest: dict[str, Any] | None = None) -> str:
    """Render the manifest as an operator note."""

    payload = manifest or instrument_manifest()
    lines = [
        "# Current Harness Instrument",
        "",
        f"Schema: `{payload.get('schema_version', '')}`",
        "",
        str(payload.get("purpose", "")).strip(),
        "",
        "## Authority Boundary",
        "",
    ]
    for item in payload.get("authority_boundary", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Control Surfaces", ""])
    for control in payload.get("control_surfaces", []):
        lines.append(f"### {control.get('name', '')}")
        lines.append("")
        lines.append(f"- Command: `{control.get('command', '')}`")
        lines.append(f"- Reason: {control.get('reason', '')}")
        reads = ", ".join(f"`{item}`" for item in control.get("reads", []))
        writes = ", ".join(f"`{item}`" for item in control.get("writes", [])) or "`none`"
        lines.append(f"- Reads: {reads}")
        lines.append(f"- Writes: {writes}")
        lines.append("")
    lines.extend(["## Canonical Outputs", ""])
    for output in payload.get("canonical_outputs", []):
        fields = ", ".join(f"`{item}`" for item in output.get("fields", []))
        lines.append(f"- `{output.get('name', '')}` from `{output.get('producer', '')}`: {output.get('calibration_use', '')} Fields: {fields}.")
    lines.extend(["", "## Extraction Rule", "", f"`{payload.get('next_extraction_rule', '')}`", ""])
    return "\n".join(lines)

