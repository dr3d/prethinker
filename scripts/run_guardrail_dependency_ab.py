#!/usr/bin/env python3
"""Compare legacy Python-rescue runtime against semantic_ir_v1 runtime.

Raw traces stay under tmp/ because they include local model outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_semantic_ir_prompt_bakeoff import (  # noqa: E402
    EDGE_SCENARIO_IDS,
    POLICY_DEMO_SCENARIO_IDS,
    RULE_MUTATION_SCENARIO_IDS,
    SILVERTON_NOISY_SCENARIO_IDS,
    SILVERTON_SCENARIO_IDS,
    WEAK_EDGE_SCENARIO_IDS,
    WILD_SCENARIOS,
    _decision_matches,
    flatten_text,
)
from src.mcp_server import PrologMCPServer  # noqa: E402
from src.semantic_ir import projected_semantic_ir_decision  # noqa: E402


DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "guardrail_dependency_ab"
DEFAULT_EDGE_SAMPLE = [
    "edge_identity_repair_oslo_oskar",
    "edge_scope_of_only_after_transfer",
    "edge_alleged_forgery_court_finding",
    "edge_disjunction_leak_cause",
    "edge_comparative_measurement_direction",
    "edge_temporal_correction_warfarin",
    "edge_hypothetical_hazard_pay_query",
    "edge_pronoun_stack_sister_van",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug_component(value: Any, *, fallback: str = "run") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip()).strip("-").lower()
    return slug or fallback


def _looks_like_clause(text: str) -> bool:
    value = str(text or "").strip()
    if not value.endswith("."):
        return False
    return bool(re.match(r"^[a-z_][a-z0-9_]*\s*\(", value))


def _extract_context_clause(text: str) -> str:
    value = str(text or "").strip()
    if _looks_like_clause(value):
        return value
    match = re.search(r"([a-z_][a-z0-9_]*\s*\(.+\)\s*(?::-\s*.+)?\.)\s*$", value)
    if match:
        return match.group(1).strip()
    return ""


def _preload_context(server: PrologMCPServer, scenario: dict[str, Any]) -> list[dict[str, Any]]:
    loaded: list[dict[str, Any]] = []
    context = scenario.get("context", [])
    if not isinstance(context, list):
        return loaded
    recent = getattr(server, "_recent_committed_logic", None)
    for item in context:
        text = str(item or "").strip()
        if not text:
            continue
        if isinstance(recent, list):
            recent.append(text)
        clause = _extract_context_clause(text)
        if clause:
            if ":-" in clause:
                result = server.assert_rule(clause)
            else:
                result = server.assert_fact(clause)
            loaded.append({"context": text, "clause": clause, "assert_result": result})
        else:
            loaded.append({"context": text, "clause": "", "assert_result": None})
    return loaded


def _inject_allowed_predicates(server: PrologMCPServer, scenario: dict[str, Any]) -> None:
    signatures = getattr(server, "_registry_signatures", None)
    if not isinstance(signatures, set):
        return
    allowed = scenario.get("allowed_predicates", [])
    if not isinstance(allowed, list):
        return
    for item in allowed:
        match = re.match(r"^\s*([a-z_][a-z0-9_]*)/(\d+)\s*$", str(item or "").strip())
        if not match:
            continue
        signatures.add((match.group(1), int(match.group(2))))


def _new_server(
    *,
    semantic_ir: bool,
    backend: str,
    base_url: str,
    legacy_model: str,
    semantic_model: str,
    timeout: int,
    active_profile: str,
) -> PrologMCPServer:
    return PrologMCPServer(
        active_profile=active_profile,
        compiler_mode="strict",
        compiler_backend=backend,
        compiler_base_url=base_url,
        compiler_model=legacy_model,
        compiler_timeout=timeout,
        compiler_prompt_enabled=not semantic_ir,
        semantic_ir_enabled=semantic_ir,
        semantic_ir_model=semantic_model,
        semantic_ir_timeout=timeout,
    )


def _extract_applied_rescues(trace: dict[str, Any], section: str) -> list[str]:
    node = trace.get(section, {}) if isinstance(trace, dict) else {}
    if not isinstance(node, dict):
        return []
    summary = node.get("summary", {})
    if isinstance(summary, dict) and isinstance(summary.get("rescues"), list):
        return [str(item) for item in summary.get("rescues", []) if str(item).strip()]
    rescues = node.get("rescues", [])
    if not isinstance(rescues, list):
        return []
    return [
        str(item.get("name", "")).strip()
        for item in rescues
        if isinstance(item, dict) and bool(item.get("applied")) and str(item.get("name", "")).strip()
    ]


def _classify_rescue_name(name: str) -> str:
    value = str(name or "").strip().lower()
    if not value:
        return "unknown"
    if value in {"semantic_ir_mapper", "semantic_ir_prethink_projection"}:
        return "structural_mapper"
    if value == "fallback_classifier":
        return "legacy_route_fallback"
    if any(token in value for token in ("registry", "type_", "predicate_name", "temporal_predicate_namespace")):
        return "authority_admission"
    if any(token in value for token in ("medical", "umls", "bridge")):
        return "domain_medical"
    if "clarification" in value or "freethinker" in value:
        return "clarification_policy"
    if any(
        token in value
        for token in (
            "possessive",
            "family",
            "spouse",
            "pronoun",
            "subject_prefixed",
            "make_with",
            "observed",
            "three_bears",
            "narrative",
            "route_intent_realign",
            "route_fallback",
            "speaker_prefixed",
        )
    ):
        return "semantic_rescue_english"
    if any(token in value for token in ("retract", "query_open_variable", "assert_fact_shape", "alias")):
        return "structural_mapper"
    return "uncategorized"


def _classify_rescues(names: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in names:
        category = _classify_rescue_name(name)
        counts[category] = counts.get(category, 0) + 1
    return dict(sorted(counts.items()))


def _operation_clauses(execution: dict[str, Any]) -> list[str]:
    clauses: list[str] = []
    operations = execution.get("operations", []) if isinstance(execution, dict) else []
    if not isinstance(operations, list):
        return clauses
    for op in operations:
        if not isinstance(op, dict):
            continue
        clause = str(op.get("clause", "")).strip()
        if clause:
            clauses.append(clause)
    return clauses


def _has_stored_logic_conflict_guard(execution: dict[str, Any]) -> bool:
    operations = execution.get("operations", []) if isinstance(execution, dict) else []
    if not isinstance(operations, list):
        return False
    for op in operations:
        if not isinstance(op, dict):
            continue
        if str(op.get("tool", "")).strip() != "stored_logic_conflict_guard":
            continue
        result = op.get("result", {}) if isinstance(op.get("result"), dict) else {}
        if str(result.get("status", "")).strip() == "blocked":
            return True
    return False


def _admission_diagnostics(execution: dict[str, Any]) -> dict[str, Any]:
    parsed = execution.get("parse", {}) if isinstance(execution, dict) else {}
    if not isinstance(parsed, dict):
        return {}
    diagnostics = parsed.get("admission_diagnostics", {})
    return diagnostics if isinstance(diagnostics, dict) else {}


def _kb_snapshot(server: PrologMCPServer) -> list[str]:
    try:
        return list(server._kb_snapshot_clauses(limit=500))  # type: ignore[attr-defined]
    except Exception:
        return []


def _avoid_probe(item: str) -> str:
    probe = str(item or "").lower()
    for suffix in (" as current", " as fact"):
        probe = probe.replace(suffix, "")
    return probe.strip()


def _semantic_ir_decision(result: dict[str, Any]) -> str:
    trace = result.get("compiler_trace", {}) if isinstance(result.get("compiler_trace"), dict) else {}
    parse = trace.get("parse", {}) if isinstance(trace, dict) else {}
    if isinstance(parse, dict):
        normalized = parse.get("normalized", {})
        if isinstance(normalized, dict):
            diagnostics = normalized.get("admission_diagnostics", {})
            if isinstance(diagnostics, dict):
                decision = str(diagnostics.get("projected_decision", "")).strip().lower()
                if decision in {"commit", "clarify", "quarantine", "reject", "answer", "mixed"}:
                    return decision
    for section in ("prethink", "parse"):
        node = trace.get(section, {}) if isinstance(trace, dict) else {}
        if not isinstance(node, dict):
            continue
        semantic_ir = node.get("semantic_ir", {})
        if not isinstance(semantic_ir, dict):
            continue
        parsed = semantic_ir.get("parsed", {})
        if not isinstance(parsed, dict):
            continue
        if str(parsed.get("schema_version", "")).strip() != "semantic_ir_v1":
            continue
        decision = projected_semantic_ir_decision(parsed)
        if decision:
            return decision
    return ""


def _safe_outcome_matches(decision: str, expected_decision: str, *, avoid_ok: bool) -> bool:
    if not avoid_ok:
        return False
    decision = str(decision or "").strip().lower()
    expected = str(expected_decision or "").strip().lower()
    if not expected:
        return False
    if expected == "commit":
        return decision == "commit"
    if expected == "answer":
        return decision == "answer"
    if expected in {"clarify", "quarantine", "reject", "mixed"}:
        return decision in {"clarify", "quarantine", "reject", "mixed"}
    return decision == expected


def _score_runtime_result(
    result: dict[str, Any],
    scenario: dict[str, Any],
    *,
    final_kb: list[str],
) -> dict[str, Any]:
    expect = scenario.get("expect", {})
    expected_decision = str(expect.get("decision", "")).strip().lower()
    execution = result.get("execution", {}) if isinstance(result.get("execution"), dict) else {}
    front_door = result.get("front_door", {}) if isinstance(result.get("front_door"), dict) else {}
    status = str(result.get("status", "")).strip()
    intent = str(execution.get("intent") or front_door.get("compiler_intent") or "").strip()
    ir_decision = _semantic_ir_decision(result)
    if _has_stored_logic_conflict_guard(execution):
        decision = "clarify"
    elif ir_decision in {"commit", "clarify", "quarantine", "reject", "answer", "mixed"}:
        decision = ir_decision
    elif status == "clarification_required" or bool(front_door.get("needs_clarification")):
        decision = "clarify"
    elif intent == "query":
        decision = "answer"
    elif intent in {"assert_fact", "assert_rule", "retract"} and int(execution.get("writes_applied", 0) or 0) > 0:
        decision = "commit"
    elif status in {"blocked", "error"}:
        decision = "quarantine"
    else:
        decision = "other"

    text = flatten_text(result)
    current_text = flatten_text(final_kb)
    must = [str(item).lower() for item in expect.get("must", [])]
    avoid = [_avoid_probe(str(item)) for item in expect.get("avoid", [])]
    noticed = [item for item in must if item in text]
    avoided = [item for item in avoid if item not in current_text]
    decision_ok = _decision_matches(decision, expected_decision) if expected_decision else False
    extraction_score = len(noticed) / len(must) if must else 1.0
    kb_safety_score = len(avoided) / len(avoid) if avoid else 1.0
    safe_outcome_ok = _safe_outcome_matches(
        decision,
        expected_decision,
        avoid_ok=len(avoided) == len(avoid),
    )
    return {
        "decision": decision,
        "expected_decision": expected_decision,
        "decision_ok": decision_ok,
        "safe_outcome_ok": safe_outcome_ok,
        "must_count": len(noticed),
        "must_total": len(must),
        "noticed": noticed,
        "avoid_count": len(avoided),
        "avoid_total": len(avoid),
        "avoided": avoided,
        "decision_score": 1.0 if decision_ok else 0.0,
        "extraction_score": extraction_score,
        "kb_safety_score": kb_safety_score,
        "rough_score": (
            (1 if decision_ok else 0)
            + extraction_score
            + kb_safety_score
        )
        / 3,
    }


def _summarize_result(
    *,
    label: str,
    scenario: dict[str, Any],
    result: dict[str, Any],
    context_load: list[dict[str, Any]],
    final_kb: list[str],
) -> dict[str, Any]:
    execution = result.get("execution", {}) if isinstance(result.get("execution"), dict) else {}
    trace = result.get("compiler_trace", {}) if isinstance(result.get("compiler_trace"), dict) else {}
    parse_rescues = _extract_applied_rescues(trace, "parse")
    prethink_rescues = _extract_applied_rescues(trace, "prethink")
    score = _score_runtime_result(result, scenario, final_kb=final_kb)
    all_rescues = parse_rescues + prethink_rescues
    rescue_classes = _classify_rescues(all_rescues)
    return {
        "label": label,
        "status": str(result.get("status", "")).strip(),
        "result_type": str(result.get("result_type", "")).strip(),
        "writes_applied": int(execution.get("writes_applied", 0) or 0),
        "intent": str(execution.get("intent", "")).strip(),
        "clauses": _operation_clauses(execution),
        "admission_diagnostics": _admission_diagnostics(execution),
        "errors": list(execution.get("errors", [])) if isinstance(execution.get("errors"), list) else [],
        "parse_rescues": parse_rescues,
        "prethink_rescues": prethink_rescues,
        "rescue_classes": rescue_classes,
        "semantic_rescue_english_count": rescue_classes.get("semantic_rescue_english", 0),
        "non_mapper_parse_rescue_count": len([item for item in parse_rescues if item != "semantic_ir_mapper"]),
        "context_load": context_load,
        "final_kb": final_kb,
        "score": score,
        "raw": result,
    }


def run_case(
    *,
    scenario: dict[str, Any],
    backend: str,
    base_url: str,
    legacy_model: str,
    semantic_model: str,
    timeout: int,
    active_profile: str,
) -> dict[str, Any]:
    utterance = str(scenario.get("utterance", "")).strip()
    legacy_server = _new_server(
        semantic_ir=False,
        backend=backend,
        base_url=base_url,
        legacy_model=legacy_model,
        semantic_model=semantic_model,
        timeout=timeout,
        active_profile=active_profile,
    )
    semantic_server = _new_server(
        semantic_ir=True,
        backend=backend,
        base_url=base_url,
        legacy_model=legacy_model,
        semantic_model=semantic_model,
        timeout=timeout,
        active_profile=active_profile,
    )
    legacy_context = _preload_context(legacy_server, scenario)
    semantic_context = _preload_context(semantic_server, scenario)
    _inject_allowed_predicates(legacy_server, scenario)
    _inject_allowed_predicates(semantic_server, scenario)
    legacy_result = legacy_server.process_utterance({"utterance": utterance})
    semantic_result = semantic_server.process_utterance({"utterance": utterance})
    legacy_kb = _kb_snapshot(legacy_server)
    semantic_kb = _kb_snapshot(semantic_server)
    legacy = _summarize_result(
        label="legacy",
        scenario=scenario,
        result=legacy_result,
        context_load=legacy_context,
        final_kb=legacy_kb,
    )
    semantic = _summarize_result(
        label="semantic_ir",
        scenario=scenario,
        result=semantic_result,
        context_load=semantic_context,
        final_kb=semantic_kb,
    )
    return {
        "scenario_id": str(scenario.get("id", "")).strip(),
        "domain": str(scenario.get("domain", "")).strip(),
        "utterance": utterance,
        "expected_decision": str(scenario.get("expect", {}).get("decision", "")).strip(),
        "backend": backend,
        "base_url": base_url,
        "legacy_model": legacy_model,
        "semantic_model": semantic_model,
        "legacy": legacy,
        "semantic_ir": semantic,
        "delta": {
            "parse_rescue_reduction": legacy["non_mapper_parse_rescue_count"]
            - semantic["non_mapper_parse_rescue_count"],
            "score_delta": round(
                float(semantic["score"].get("rough_score", 0.0))
                - float(legacy["score"].get("rough_score", 0.0)),
                4,
            ),
            "semantic_fewer_non_mapper_rescues": semantic["non_mapper_parse_rescue_count"]
            < legacy["non_mapper_parse_rescue_count"],
        },
    }


def _records_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    def avg(path: str, label: str) -> float:
        values: list[float] = []
        for record in records:
            node = record[label]
            for part in path.split("."):
                node = node.get(part, {}) if isinstance(node, dict) else {}
            try:
                values.append(float(node))
            except Exception:
                pass
        return sum(values) / max(1, len(values))

    def rescue_class_totals(label: str) -> dict[str, int]:
        totals: dict[str, int] = {}
        for record in records:
            classes = record[label].get("rescue_classes", {})
            if not isinstance(classes, dict):
                continue
            for key, value in classes.items():
                totals[str(key)] = totals.get(str(key), 0) + int(value or 0)
        return dict(sorted(totals.items()))

    def diagnostic_totals(label: str) -> dict[str, int]:
        totals = {"operation_count": 0, "admitted_count": 0, "skipped_count": 0}
        for record in records:
            diagnostics = record[label].get("admission_diagnostics", {})
            if not isinstance(diagnostics, dict):
                continue
            for key in list(totals):
                try:
                    totals[key] += int(diagnostics.get(key, 0) or 0)
                except Exception:
                    pass
        return totals

    return {
        "runs": len(records),
        "legacy_decision_ok": sum(1 for row in records if row["legacy"]["score"]["decision_ok"]),
        "semantic_decision_ok": sum(1 for row in records if row["semantic_ir"]["score"]["decision_ok"]),
        "legacy_safe_outcome_ok": sum(1 for row in records if row["legacy"]["score"].get("safe_outcome_ok")),
        "semantic_safe_outcome_ok": sum(
            1 for row in records if row["semantic_ir"]["score"].get("safe_outcome_ok")
        ),
        "legacy_avg_score": round(avg("score.rough_score", "legacy"), 3),
        "semantic_avg_score": round(avg("score.rough_score", "semantic_ir"), 3),
        "legacy_avg_extraction": round(avg("score.extraction_score", "legacy"), 3),
        "semantic_avg_extraction": round(avg("score.extraction_score", "semantic_ir"), 3),
        "legacy_avg_kb_safety": round(avg("score.kb_safety_score", "legacy"), 3),
        "semantic_avg_kb_safety": round(avg("score.kb_safety_score", "semantic_ir"), 3),
        "legacy_parse_rescues": sum(row["legacy"]["non_mapper_parse_rescue_count"] for row in records),
        "semantic_non_mapper_parse_rescues": sum(
            row["semantic_ir"]["non_mapper_parse_rescue_count"] for row in records
        ),
        "legacy_rescue_classes": rescue_class_totals("legacy"),
        "semantic_rescue_classes": rescue_class_totals("semantic_ir"),
        "legacy_semantic_rescue_english": sum(row["legacy"]["semantic_rescue_english_count"] for row in records),
        "semantic_semantic_rescue_english": sum(
            row["semantic_ir"]["semantic_rescue_english_count"] for row in records
        ),
        "legacy_admission_diagnostics": diagnostic_totals("legacy"),
        "semantic_admission_diagnostics": diagnostic_totals("semantic_ir"),
        "total_parse_rescue_reduction": sum(row["delta"]["parse_rescue_reduction"] for row in records),
    }


def write_outputs(records: list[dict[str, Any]], jsonl_path: Path) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    summary = _records_summary(records)
    class_keys = sorted(
        set(summary["legacy_rescue_classes"].keys()) | set(summary["semantic_rescue_classes"].keys())
    )
    lines = [
        "# Guardrail Dependency A/B",
        "",
        f"Generated: {_utc_now()}",
        "",
        "## Aggregate",
        "",
        "| Runs | Legacy exact OK | Semantic exact OK | Legacy safe OK | Semantic safe OK | Legacy avg score | Semantic avg score | Legacy parse rescues | Semantic non-mapper rescues | Rescue reduction |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| {summary['runs']} | {summary['legacy_decision_ok']} | {summary['semantic_decision_ok']} | "
            f"{summary['legacy_safe_outcome_ok']} | {summary['semantic_safe_outcome_ok']} | "
            f"{summary['legacy_avg_score']:.3f} | {summary['semantic_avg_score']:.3f} | "
            f"{summary['legacy_parse_rescues']} | {summary['semantic_non_mapper_parse_rescues']} | "
            f"{summary['total_parse_rescue_reduction']} |"
        ),
        "",
        "Exact OK measures policy-label agreement. Safe OK measures whether the run avoided forbidden KB state while landing in an acceptable commit/answer/non-commit bucket.",
        "",
        "## Score Dimensions",
        "",
        "| Path | Extraction avg | KB safety avg |",
        "|---|---:|---:|",
        f"| Legacy | {summary['legacy_avg_extraction']:.3f} | {summary['legacy_avg_kb_safety']:.3f} |",
        f"| Semantic IR | {summary['semantic_avg_extraction']:.3f} | {summary['semantic_avg_kb_safety']:.3f} |",
        "",
        "## Rescue Classes",
        "",
        "| Class | Legacy | Semantic IR |",
        "|---|---:|---:|",
    ]
    for key in class_keys:
        lines.append(
            f"| `{key}` | {summary['legacy_rescue_classes'].get(key, 0)} | "
            f"{summary['semantic_rescue_classes'].get(key, 0)} |"
        )
    lines.extend(
        [
            "",
            "Semantic-rescue-English counts are the deletion-pressure metric: lower is better when scores hold.",
            "",
            "## Admission Diagnostics",
            "",
            "| Path | Operations | Admitted | Skipped |",
            "|---|---:|---:|---:|",
            (
                f"| Legacy | {summary['legacy_admission_diagnostics']['operation_count']} | "
                f"{summary['legacy_admission_diagnostics']['admitted_count']} | "
                f"{summary['legacy_admission_diagnostics']['skipped_count']} |"
            ),
            (
                f"| Semantic IR | {summary['semantic_admission_diagnostics']['operation_count']} | "
                f"{summary['semantic_admission_diagnostics']['admitted_count']} | "
                f"{summary['semantic_admission_diagnostics']['skipped_count']} |"
            ),
            "",
            "## Cases",
            "",
            "| Scenario | Expected | Legacy | Semantic IR | Safe OK L/S | Rescue delta | Score delta |",
            "|---|---|---|---|---|---:|---:|",
        ]
    )
    for record in records:
        legacy = record["legacy"]["score"]
        semantic = record["semantic_ir"]["score"]
        safe_pair = (
            f"{'Y' if legacy.get('safe_outcome_ok') else 'N'}/"
            f"{'Y' if semantic.get('safe_outcome_ok') else 'N'}"
        )
        lines.append(
            f"| `{record['scenario_id']}` | `{record['expected_decision']}` | "
            f"`{legacy['decision']}` {legacy['rough_score']:.2f} | "
            f"`{semantic['decision']}` {semantic['rough_score']:.2f} | "
            f"{safe_pair} | "
            f"{record['delta']['parse_rescue_reduction']} | {record['delta']['score_delta']:+.2f} |"
        )
    lines.extend(["", "## Files", "", f"- JSONL: `{jsonl_path.name}`"])
    jsonl_path.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenario-group",
        choices=[
            "edge_sample",
            "edge",
            "weak_edges",
            "silverton",
            "silverton_noisy",
            "rule_mutation",
            "policy_demo",
            "all",
        ],
        default="edge_sample",
    )
    parser.add_argument("--scenario-ids", default="")
    parser.add_argument("--backend", choices=["ollama", "lmstudio"], default="ollama")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--legacy-model", default="qwen35-semparse:9b")
    parser.add_argument("--semantic-model", default="qwen3.6:35b")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--active-profile", default="general")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backend = str(args.backend or "ollama").strip().lower()
    base_url = str(args.base_url or "").strip()
    if not base_url:
        base_url = "http://127.0.0.1:1234" if backend == "lmstudio" else "http://127.0.0.1:11434"
    scenario_ids = [item.strip() for item in str(args.scenario_ids or "").split(",") if item.strip()]
    if not scenario_ids:
        if args.scenario_group == "edge_sample":
            scenario_ids = list(DEFAULT_EDGE_SAMPLE)
        elif args.scenario_group == "edge":
            scenario_ids = list(EDGE_SCENARIO_IDS)
        elif args.scenario_group == "weak_edges":
            scenario_ids = list(WEAK_EDGE_SCENARIO_IDS)
        elif args.scenario_group == "silverton":
            scenario_ids = list(SILVERTON_SCENARIO_IDS)
        elif args.scenario_group == "silverton_noisy":
            scenario_ids = list(SILVERTON_NOISY_SCENARIO_IDS)
        elif args.scenario_group == "rule_mutation":
            scenario_ids = list(RULE_MUTATION_SCENARIO_IDS)
        elif args.scenario_group == "policy_demo":
            scenario_ids = list(POLICY_DEMO_SCENARIO_IDS)
    by_id = {str(scenario.get("id", "")): scenario for scenario in WILD_SCENARIOS}
    scenarios = [by_id[item] for item in scenario_ids] if scenario_ids else list(WILD_SCENARIOS)

    run_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_slug = (
        f"{run_slug}_{_slug_component(args.scenario_group)}_"
        f"{_slug_component(args.semantic_model)}_pid{os.getpid()}"
    )
    jsonl_path = Path(args.out_dir) / f"guardrail_dependency_ab_{run_slug}.jsonl"
    records: list[dict[str, Any]] = []
    for scenario in scenarios:
        print(f"[{_utc_now()}] {scenario['id']}")
        records.append(
            run_case(
                scenario=scenario,
                backend=backend,
                base_url=base_url,
                legacy_model=str(args.legacy_model),
                semantic_model=str(args.semantic_model),
                timeout=int(args.timeout),
                active_profile=str(args.active_profile),
            )
        )
    write_outputs(records, jsonl_path)
    print(f"Wrote {jsonl_path}")
    print(f"Wrote {jsonl_path.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
