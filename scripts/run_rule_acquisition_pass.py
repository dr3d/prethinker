#!/usr/bin/env python3
"""Run a rule-acquisition lens over an existing safe compile.

This is a post-backbone source pass. Python does not inspect source prose for
rules, facts, entities, or answers. It hands the raw source plus an already
mapper-admitted KB surface to an LLM and asks for executable rule operations
only. The normal Semantic IR mapper still decides which rule proposals are
admitted, and the optional runtime trial loads only admitted clauses.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_file"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_pipeline import CorePrologRuntime  # noqa: E402
from scripts.run_domain_bootstrap_file import (  # noqa: E402
    SOURCE_PASS_OPS_JSON_SCHEMA,
    _call_lmstudio_json_schema,
    _load_profile_registry,
    _profile_from_registry,
    _slug,
    _source_pass_ops_to_semantic_ir,
)
from src.profile_bootstrap import (  # noqa: E402
    profile_bootstrap_allowed_predicates,
    profile_bootstrap_domain_context,
    profile_bootstrap_predicate_contracts,
)
from src.semantic_ir import semantic_ir_to_legacy_parse  # noqa: E402


RULE_HEAD_PREDICATES = [
    {
        "signature": "derived_status/3",
        "args": ["subject", "status", "time_or_context"],
        "description": "Query-only derived status from source-stated conditions and admitted facts.",
        "why": "rule_acquisition",
        "admission_notes": ["Use only as a rule head or directly stated status; never as a guessed fact."],
    },
    {
        "signature": "derived_condition/3",
        "args": ["subject", "condition", "scope"],
        "description": "Query-only intermediate condition from source-stated rule prerequisites; not a final outcome.",
        "why": "rule_acquisition",
        "admission_notes": ["Use for threshold_met, veto_present, override_absent, and similar intermediate rule conditions."],
    },
    {
        "signature": "derived_permission/4",
        "args": ["actor_or_subject", "action", "place_or_object", "time_or_context"],
        "description": "Query-only derived permission from explicit source-stated authorization rules.",
        "why": "rule_acquisition",
        "admission_notes": ["Permission is not occurrence; do not use for event facts."],
    },
    {
        "signature": "derived_obligation/3",
        "args": ["actor_or_subject", "obligation", "scope"],
        "description": "Query-only derived obligation or required path from explicit source-stated rules.",
        "why": "rule_acquisition",
        "admission_notes": ["Use for stated obligations, not inferred moral blame."],
    },
    {
        "signature": "derived_authorization/3",
        "args": ["subject", "authorization_status", "scope"],
        "description": "Query-only derived authorization status from rule requirements and admitted facts.",
        "why": "rule_acquisition",
        "admission_notes": ["Keep authorization separate from event occurrence."],
    },
    {
        "signature": "derived_tax_status/3",
        "args": ["cargo_or_owner", "tax_status", "scope"],
        "description": "Query-only derived tax status from value, cargo class, and exception facts.",
        "why": "rule_acquisition",
        "admission_notes": ["Use only when source-stated tax rules and admitted cargo facts support it."],
    },
    {
        "signature": "derived_reward_status/3",
        "args": ["actor", "reward_status", "cargo_or_scope"],
        "description": "Query-only derived reward status from explicit salvage/reward rules.",
        "why": "rule_acquisition",
        "admission_notes": ["Use only for explicit reward/exception rules."],
    },
    {
        "signature": "derived_clearance_status/3",
        "args": ["subject", "clearance_status", "scope"],
        "description": "Query-only derived clearance state from explicit test/fever/clearance rules.",
        "why": "rule_acquisition",
        "admission_notes": ["Use only when required evidence rows are present in the admitted surface."],
    },
    {
        "signature": "derived_source_priority/3",
        "args": ["stronger_source", "weaker_source", "scope"],
        "description": "Query-only derived source-priority result from explicit evidence-ranking rules.",
        "why": "rule_acquisition",
        "admission_notes": ["Do not turn a claim into a finding; keep priority separate from truth."],
    },
]

RULE_BODY_HELPER_PREDICATES = [
    {
        "signature": "value_greater_than/2",
        "args": ["entity", "threshold"],
        "description": "Query-only deterministic helper: entity_property(Entity, value, Value) and Value > Threshold.",
        "why": "rule_acquisition_numeric_helper",
        "admission_notes": ["Use only in rule bodies; runtime resolves it from admitted value facts."],
    },
    {
        "signature": "value_at_most/2",
        "args": ["entity", "threshold"],
        "description": "Query-only deterministic helper: entity_property(Entity, value, Value) and Value =< Threshold.",
        "why": "rule_acquisition_numeric_helper",
        "admission_notes": ["Use only in rule bodies; runtime resolves it from admitted value facts."],
    },
    {
        "signature": "hours_at_least/3",
        "args": ["start_time", "end_time", "threshold_hours"],
        "description": "Query-only deterministic helper: true when End is at least ThresholdHours after Start.",
        "why": "rule_acquisition_temporal_helper",
        "admission_notes": ["Use only in rule bodies for source-stated minimum-hour spacing conditions."],
    },
    {
        "signature": "number_greater_than/2",
        "args": ["value", "threshold"],
        "description": "Query-only deterministic helper: true when an already-bound numeric Value is greater than Threshold.",
        "why": "rule_acquisition_numeric_helper",
        "admission_notes": ["Use only after a prior body goal binds Value to a number."],
    },
    {
        "signature": "number_at_most/2",
        "args": ["value", "threshold"],
        "description": "Query-only deterministic helper: true when an already-bound numeric Value is at most Threshold.",
        "why": "rule_acquisition_numeric_helper",
        "admission_notes": ["Use only after a prior body goal binds Value to a number."],
    },
    {
        "signature": "support_count_at_least/2",
        "args": ["proposal", "threshold"],
        "description": "Query-only deterministic helper: true when supported(Proposal, Officer) has at least Threshold distinct officers.",
        "why": "rule_acquisition_aggregation_helper",
        "admission_notes": ["Use only in rule bodies for source-stated vote-count thresholds."],
    },
    {
        "signature": "percent_at_least/3",
        "args": ["part_value", "whole_value", "threshold_percent"],
        "description": "Query-only deterministic helper: true when PartValue is at least ThresholdPercent percent of WholeValue.",
        "why": "rule_acquisition_ratio_helper",
        "admission_notes": ["Use only after body goals bind numeric part and whole variables, such as Match and Amount."],
    },
    {
        "signature": "percent_below/3",
        "args": ["part_value", "whole_value", "threshold_percent"],
        "description": "Query-only deterministic helper: true when PartValue is below ThresholdPercent percent of WholeValue.",
        "why": "rule_acquisition_ratio_helper",
        "admission_notes": ["Use only for explicit below-threshold or insufficient-percentage conditions."],
    },
]

CONTEXT_DEPENDENT_HELPER_SIGNATURES = {
    "hours_at_least/3",
    "number_greater_than/2",
    "number_at_most/2",
    "percent_at_least/3",
    "percent_below/3",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument("--backbone-json", type=Path, required=True)
    parser.add_argument("--profile-registry", type=Path, required=True)
    parser.add_argument("--domain-hint", default="")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--operation-target", type=int, default=32)
    parser.add_argument("--max-tokens", type=int, default=9000)
    parser.add_argument("--backbone-fact-limit", type=int, default=180)
    parser.add_argument("--backbone-rule-limit", type=int, default=80)
    parser.add_argument(
        "--backbone-predicate-filter",
        default="",
        help="Optional comma-separated predicate names/signatures to keep from admitted backbone clauses.",
    )
    parser.add_argument(
        "--allowed-predicate-filter",
        default="",
        help=(
            "Optional comma-separated predicate names/signatures to expose in the active rule palette. "
            "This is structural pass-planning over predicate contracts, not source prose parsing."
        ),
    )
    parser.add_argument(
        "--rule-class",
        default="",
        help=(
            "Optional authored class label for this rule-lens run, such as role_join, threshold, "
            "exception, temporal_window, bounded_negation, priority_override, claim_boundary, or permission_not_event."
        ),
    )
    parser.add_argument(
        "--positive-query",
        action="append",
        default=[],
        help=(
            "Optional authored Prolog query that should return at least one row after temporary rule loading. "
            "May be supplied more than once."
        ),
    )
    parser.add_argument(
        "--negative-query",
        action="append",
        default=[],
        help=(
            "Optional authored Prolog query that should return zero rows after temporary rule loading. "
            "May be supplied more than once."
        ),
    )
    parser.add_argument(
        "--source-char-limit",
        type=int,
        default=0,
        help="Optional deterministic prefix budget for raw_source_text. This is token budgeting, not prose parsing.",
    )
    parser.add_argument(
        "--compact-guidance",
        action="store_true",
        help=(
            "Use a shorter rule-lens payload for narrow source-span probes. This preserves the same mapper "
            "authority boundary while reducing model context pressure."
        ),
    )
    parser.add_argument(
        "--source-heading",
        default="",
        help=(
            "Optional exact Markdown heading to pass as raw_source_text. This is authored-span selection, "
            "not prose parsing; rule meaning remains LLM-owned."
        ),
    )
    parser.add_argument("--source-line-start", type=int, default=0)
    parser.add_argument("--source-line-end", type=int, default=0)
    parser.add_argument("--no-runtime-trial", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text_path = args.text_file if args.text_file.is_absolute() else (REPO_ROOT / args.text_file).resolve()
    backbone_path = args.backbone_json if args.backbone_json.is_absolute() else (REPO_ROOT / args.backbone_json).resolve()
    registry = _load_profile_registry(args.profile_registry)
    if not registry:
        raise SystemExit("--profile-registry did not load")
    source_text = text_path.read_text(encoding="utf-8-sig")
    if str(args.source_heading or "").strip():
        source_text = _markdown_section_by_heading(source_text, str(args.source_heading).strip())
    if int(args.source_line_start or 0) > 0 or int(args.source_line_end or 0) > 0:
        source_text = _line_range(source_text, int(args.source_line_start or 0), int(args.source_line_end or 0))
    if int(args.source_char_limit or 0) > 0:
        source_text = source_text[: int(args.source_char_limit)]
    backbone = json.loads(backbone_path.read_text(encoding="utf-8-sig"))
    predicate_filter = _predicate_filter(str(args.backbone_predicate_filter or ""))
    backbone_facts = _filter_clauses(_compile_items(backbone, "facts"), predicate_filter)[
        : max(0, int(args.backbone_fact_limit or 0))
    ]
    backbone_rules = _filter_clauses(_compile_items(backbone, "rules"), predicate_filter)[
        : max(0, int(args.backbone_rule_limit or 0))
    ]
    parsed_profile = _rule_acquisition_profile(
        _profile_from_registry(registry, domain_hint=str(args.domain_hint or "")),
        backbone_facts=backbone_facts,
        backbone_rules=backbone_rules,
    )
    allowed_predicate_filter = _predicate_filter(str(args.allowed_predicate_filter or ""))
    if allowed_predicate_filter:
        parsed_profile = _filter_profile_predicates(parsed_profile, allowed_predicate_filter)
    started = time.perf_counter()
    rule_compile = _run_rule_pass(
        args=args,
        source_text=source_text,
        source_name=text_path.name,
        parsed_profile=parsed_profile,
        backbone_facts=backbone_facts,
        backbone_rules=backbone_rules,
    )
    runtime_trial = {}
    if not bool(args.no_runtime_trial):
        runtime_trial = _runtime_trial(
            facts=backbone_facts,
            backbone_rules=backbone_rules,
            rule_lens_rules=_compile_items({"source_compile": rule_compile}, "rules"),
            positive_queries=[str(item) for item in args.positive_query if str(item).strip()],
            negative_queries=[str(item) for item in args.negative_query if str(item).strip()],
        )
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": "rule_acquisition_pass",
        "text_file": str(text_path),
        "domain_hint": str(args.domain_hint or ""),
        "backend": "lmstudio",
        "model": str(args.model),
        "profile_registry": str(args.profile_registry),
        "rule_backbone_json": str(backbone_path),
        "backbone_fact_limit": int(args.backbone_fact_limit or 0),
        "backbone_rule_limit": int(args.backbone_rule_limit or 0),
        "backbone_predicate_filter": sorted(predicate_filter),
        "allowed_predicate_filter": sorted(allowed_predicate_filter),
        "rule_class": str(args.rule_class or ""),
        "positive_queries": [str(item) for item in args.positive_query if str(item).strip()],
        "negative_queries": [str(item) for item in args.negative_query if str(item).strip()],
        "source_char_limit": int(args.source_char_limit or 0),
        "source_heading": str(args.source_heading or ""),
        "source_line_start": int(args.source_line_start or 0),
        "source_line_end": int(args.source_line_end or 0),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parsed_ok": True,
        "score": {
            "predicate_count": len(parsed_profile.get("candidate_predicates", [])),
            "rule_head_predicate_count": len(RULE_HEAD_PREDICATES),
        },
        "parsed": parsed_profile,
        "source_compile": rule_compile,
        "runtime_trial": runtime_trial,
        "rule_acquisition_policy": [
            "The raw source document is direct evidence.",
            "The admitted backbone surface is context and body-predicate vocabulary only.",
            "The pass may emit rule operations only.",
            "The deterministic mapper decides rule admission.",
            "Runtime trial loads mapper-admitted rules into a temporary KB only.",
        ],
    }
    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(text_path.stem)}-rules_{_slug(str(args.model))}"
    json_path = out_dir / f"domain_bootstrap_file_{slug}.json"
    tmp_json_path = json_path.with_suffix(json_path.suffix + ".tmp")
    tmp_json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp_json_path.replace(json_path)
    print(f"Wrote {json_path}")
    print(
        json.dumps(
            {
                "compile_admitted": rule_compile.get("admitted_count"),
                "compile_skipped": rule_compile.get("skipped_count"),
                "facts": len(rule_compile.get("facts", [])),
                "rules": len(rule_compile.get("rules", [])),
                "runtime_rule_errors": len(runtime_trial.get("rule_load_errors", [])) if runtime_trial else None,
                "firing_rules": runtime_trial.get("firing_rule_count") if runtime_trial else None,
                "promotion_ready_rules": runtime_trial.get("promotion_ready_rule_count") if runtime_trial else None,
                "composition_ready_rules": runtime_trial.get("composition_ready_rule_count") if runtime_trial else None,
                "composition_rescued_rules": runtime_trial.get("composition_rescued_rule_count") if runtime_trial else None,
                "unsupported_body_goals": runtime_trial.get("unsupported_body_goal_count") if runtime_trial else None,
                "positive_probe_passes": runtime_trial.get("positive_probe_pass_count") if runtime_trial else None,
                "negative_probe_passes": runtime_trial.get("negative_probe_pass_count") if runtime_trial else None,
                "unexpected_probe_solutions": runtime_trial.get("unexpected_solution_count") if runtime_trial else None,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _markdown_section_by_heading(source_text: str, heading: str) -> str:
    lines = source_text.splitlines()
    target_index = -1
    target_level = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        title = stripped[level:].strip()
        if title == heading:
            target_index = index
            target_level = level
            break
    if target_index < 0:
        raise SystemExit(f"--source-heading not found: {heading}")
    end_index = len(lines)
    for index in range(target_index + 1, len(lines)):
        stripped = lines[index].strip()
        if not stripped.startswith("#"):
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        if level <= target_level:
            end_index = index
            break
    return "\n".join(lines[target_index:end_index]).strip() + "\n"


def _line_range(source_text: str, start: int, end: int) -> str:
    lines = source_text.splitlines()
    if start <= 0:
        start = 1
    if end <= 0:
        end = len(lines)
    if end < start:
        raise SystemExit("--source-line-end must be greater than or equal to --source-line-start")
    return "\n".join(lines[start - 1 : end]).strip() + "\n"


def _predicate_filter(raw: str) -> set[str]:
    values: set[str] = set()
    for item in raw.split(","):
        token = item.strip()
        if not token:
            continue
        values.add(token)
        if "/" in token:
            values.add(token.split("/", 1)[0])
    return values


def _filter_clauses(clauses: list[str], predicate_filter: set[str]) -> list[str]:
    if not predicate_filter:
        return clauses
    out: list[str] = []
    for clause in clauses:
        match = re.match(r"^\s*([a-z_][a-z0-9_]*)\s*\(", str(clause))
        if match and match.group(1) in predicate_filter:
            out.append(clause)
    return out


def _filter_profile_predicates(profile: dict[str, Any], predicate_filter: set[str]) -> dict[str, Any]:
    if not predicate_filter:
        return profile
    rows = profile.get("candidate_predicates", [])
    if not isinstance(rows, list):
        return profile
    kept = [
        row
        for row in rows
        if isinstance(row, dict) and _predicate_row_matches_filter(row, predicate_filter)
    ]
    out = dict(profile)
    out["candidate_predicates"] = kept
    out["active_predicate_filter"] = sorted(predicate_filter)
    return out


def _predicate_row_matches_filter(row: dict[str, Any], predicate_filter: set[str]) -> bool:
    signature = str(row.get("signature", "")).strip()
    name = signature.split("/", 1)[0] if signature else ""
    return bool(signature and (signature in predicate_filter or name in predicate_filter))


def _rule_acquisition_profile(
    profile: dict[str, Any],
    *,
    backbone_facts: list[str],
    backbone_rules: list[str],
) -> dict[str, Any]:
    predicate_rows = [
        item
        for item in profile.get("candidate_predicates", [])
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    ]
    by_signature = {str(item.get("signature", "")).strip(): item for item in predicate_rows}
    for signature in sorted(_signatures_from_clauses([*backbone_facts, *backbone_rules])):
        if signature not in by_signature:
            arity = int(signature.split("/", 1)[1])
            by_signature[signature] = {
                "signature": signature,
                "args": [f"arg_{index}" for index in range(1, arity + 1)],
                "description": "Predicate already present in the mapper-admitted backbone surface.",
                "why": "admitted_backbone_body_predicate",
                "admission_notes": [
                    "Included for rule-body compatibility only; raw source support and mapper admission still required."
                ],
            }
    for item in RULE_HEAD_PREDICATES:
        by_signature.setdefault(item["signature"], item)
    for item in RULE_BODY_HELPER_PREDICATES:
        by_signature.setdefault(item["signature"], item)
    out = dict(profile)
    out["domain_guess"] = str(out.get("domain_guess", "") or "rule_acquisition")
    out["domain_scope"] = (str(out.get("domain_scope", "")).strip() + " | executable rule acquisition lens").strip(" |")
    out["candidate_predicates"] = list(by_signature.values())
    out["admission_risks"] = [
        *[str(item) for item in out.get("admission_risks", []) if str(item).strip()],
        "Rule acquisition must not add ordinary facts.",
        "Rule clauses must use only allowed predicates and simple conjunctions supported by the runtime.",
        "A rule that needs negation, arithmetic, aggregation, or source priority should be deferred unless it can be expressed with admitted helper predicates.",
    ]
    out["self_check"] = {
        **(out.get("self_check") if isinstance(out.get("self_check"), dict) else {}),
        "profile_authority": "proposal_only",
        "rule_acquisition_only": True,
    }
    return out


def _run_rule_pass(
    *,
    args: argparse.Namespace,
    source_text: str,
    source_name: str,
    parsed_profile: dict[str, Any],
    backbone_facts: list[str],
    backbone_rules: list[str],
) -> dict[str, Any]:
    allowed_predicates = profile_bootstrap_allowed_predicates(parsed_profile)
    predicate_contracts = profile_bootstrap_predicate_contracts(parsed_profile)
    domain_context = profile_bootstrap_domain_context(parsed_profile)
    target = max(1, int(args.operation_target or 32))
    guidance_context = _rule_guidance_context(
        target=target,
        rule_class=str(args.rule_class or ""),
        compact=bool(args.compact_guidance),
    )
    payload = {
        "task": "Emit executable rule candidate_operations for an existing safe compile.",
        "authority": "proposal_only_mapper_remains_authoritative",
        "domain_hint": str(args.domain_hint or ""),
        "source_name": source_name,
        "raw_source_text": source_text,
        "existing_admitted_backbone": {
            "facts": backbone_facts,
            "rules": backbone_rules,
            "policy": [
                "These admitted clauses are context for rule bodies and anchors, not raw evidence by themselves.",
                "Do not re-emit or rewrite these clauses as facts.",
                "Do not re-emit existing backbone rules; add only new rule clauses.",
                "Use their predicate names and atoms when writing rule clauses.",
            ],
        },
        "current_pass": {
            "pass_id": "rule_acquisition_v1",
            "rule_class": str(args.rule_class or ""),
            "purpose": "Convert explicit source-stated conditional rules into executable Prolog-style rule candidates.",
            "focus": "Rules only. No ordinary assert facts, no queries, no retractions.",
            "completion_policy": "Prefer a small set of safe executable rules over broad or clever rules.",
            "operation_target": target,
        },
        "allowed_predicates": allowed_predicates,
        "predicate_contracts": predicate_contracts,
        "domain_context": {} if bool(args.compact_guidance) else domain_context,
        "guidance_context": guidance_context,
    }
    try:
        response = _call_lmstudio_json_schema_with_deadline(
            deadline_seconds=max(10, int(args.timeout) + 10),
            base_url=str(args.base_url),
            model=str(args.model),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a rule-acquisition compiler for a governed symbolic memory system. "
                        "You do not decide truth and you do not mutate the KB. "
                        "Your only job is to propose executable rule operations grounded in explicit source rules. "
                        "Emit only source_pass_ops_v1 JSON."
                    ),
                },
                {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
            ],
            schema=SOURCE_PASS_OPS_JSON_SCHEMA,
            schema_name="source_pass_ops_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), max(4000, min(12000, target * 260))),
        )
        parsed = json.loads(str(response.get("content", "{}")))
    except Exception as exc:
        raw = ""
        if "response" in locals() and isinstance(response, dict):
            raw = str(response.get("content", ""))[:4000]
        return {
            "ok": False,
            "error": f"rule_acquisition_failed:{exc}",
            "raw_content": raw,
            "facts": [],
            "rules": [],
            "queries": [],
        }
    ir = _source_pass_ops_to_semantic_ir(parsed if isinstance(parsed, dict) else {})
    mapped, warnings = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    raw_rules = _derived_head_rules(mapped.get("rules", []))
    rules, duplicate_backbone_rules = _drop_backbone_duplicate_rules(raw_rules, backbone_rules)
    warnings_out = list(warnings)
    if duplicate_backbone_rules:
        warnings_out.append(f"duplicate_backbone_rule_skipped:{len(duplicate_backbone_rules)}")
    return {
        "ok": bool(isinstance(parsed, dict) and parsed.get("schema_version") == "source_pass_ops_v1"),
        "mode": "rule_acquisition_pass",
        "model_decision": ir.get("decision", ""),
        "projected_decision": diagnostics.get("projected_decision", ""),
        "admitted_count": len(mapped.get("facts", [])) + len(rules) + len(mapped.get("queries", [])),
        "mapper_admitted_count": int(diagnostics.get("admitted_count", 0) or 0),
        "skipped_count": int(diagnostics.get("skipped_count", 0) or 0) + len(duplicate_backbone_rules),
        "duplicate_backbone_rule_count": len(duplicate_backbone_rules),
        "duplicate_backbone_rules": duplicate_backbone_rules,
        "warnings": warnings_out,
        "admission_diagnostics": diagnostics,
        "facts": mapped.get("facts", []),
        "rules": rules,
        "queries": mapped.get("queries", []),
        "self_check": ir.get("self_check", {}),
        "source_pass_ops": parsed if isinstance(parsed, dict) else {},
    }


def _call_lmstudio_json_schema_with_deadline(*, deadline_seconds: int, **kwargs: Any) -> dict[str, Any]:
    if deadline_seconds <= 0:
        return _call_lmstudio_json_schema(**kwargs)
    queue: mp.Queue = mp.Queue(maxsize=1)
    process = mp.Process(target=_lmstudio_call_worker, args=(queue, kwargs))
    process.start()
    process.join(timeout=deadline_seconds)
    if process.is_alive():
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
            process.join(timeout=5)
        raise TimeoutError(f"lmstudio_call_deadline_exceeded:{deadline_seconds}s")
    if queue.empty():
        if process.exitcode:
            raise RuntimeError(f"lmstudio_call_worker_exit:{process.exitcode}")
        raise RuntimeError("lmstudio_call_worker_no_response")
    message = queue.get()
    if isinstance(message, dict) and message.get("ok"):
        response = message.get("response")
        return response if isinstance(response, dict) else {}
    error = str(message.get("error", "lmstudio_call_worker_error")) if isinstance(message, dict) else "lmstudio_call_worker_error"
    raise RuntimeError(error)


def _derived_head_rules(rules: Any) -> list[str]:
    if not isinstance(rules, list):
        return []
    allowed_names = {str(item["signature"]).split("/", 1)[0] for item in RULE_HEAD_PREDICATES}
    kept: list[str] = []
    for rule in rules:
        text = str(rule).strip()
        if _rule_head_name(text) in allowed_names:
            kept.append(text)
    return kept


def _drop_backbone_duplicate_rules(rules: list[str], backbone_rules: list[str]) -> tuple[list[str], list[str]]:
    backbone_keys = {_clause_key(rule) for rule in backbone_rules}
    kept: list[str] = []
    duplicates: list[str] = []
    for rule in rules:
        if _clause_key(rule) in backbone_keys:
            duplicates.append(rule)
        else:
            kept.append(rule)
    return kept, duplicates


def _clause_key(clause: str) -> str:
    return re.sub(r"\s+", " ", str(clause).strip().rstrip("."))


def _rule_head_name(rule: str) -> str:
    head = str(rule).split(":-", 1)[0].strip()
    match = re.match(r"^([a-z_][a-z0-9_]*)\s*\(", head)
    return match.group(1) if match else ""


def _lmstudio_call_worker(queue: mp.Queue, kwargs: dict[str, Any]) -> None:
    try:
        response = _call_lmstudio_json_schema(**kwargs)
        queue.put({"ok": True, "response": response})
    except Exception as exc:  # pragma: no cover - subprocess path
        queue.put({"ok": False, "error": str(exc)})


def _rule_guidance_context(*, target: int, rule_class: str, compact: bool) -> list[str]:
    core = [
        "This is a semantic lens, not a second default compile.",
        "Emit only operation='rule' candidate_operations. Do not emit assert/retract/query operations.",
        f"Hard cap: emit at most {target} candidate_operations total. Fewer is better than JSON overflow.",
        "Only emit rules explicitly supported by raw_source_text.",
        "Do not re-emit an existing_admitted_backbone rule. Use those rules as body support or leave the pass empty.",
        "Every rule operation must include candidate_operations[].clause with one executable single-line Prolog-style clause.",
        "Use only predicate names and arities in allowed_predicates. The mapper will reject clauses outside this palette.",
        "Head variables must appear in the body. Prolog variables must start uppercase; lowercase tokens are constants.",
        "Do not use lowercase role placeholders such as warden, engineer, repair_order, cargo, actor, patient, vessel, or person when a value must bind; use uppercase variables or source atoms from existing_admitted_backbone.",
        "Every body goal should match actual predicate/arity and argument patterns visible in existing_admitted_backbone.",
        "Do not derive current answers as facts. Rule heads should be query-only derived predicates.",
        "Executable rule heads in this lens must use derived_* predicates from the rule-head palette. Do not use source/backbone predicates such as rule_exception/2 as executable rule heads.",
        "For derived_* head scope arguments, use the governed domain, action, or object from the source (for example harbor, glass_tide_repair, quarantine), not a rule id, proof reason, or clause label.",
        "For derived_reward_status/3, preserve the source reward-status atom such as salvage_reward or no_salvage_reward; do not shorten it to generic reward or no_reward.",
        "For value_greater_than/2 and value_at_most/2, the first argument is the entity being measured (for example Cargo), not the numeric Value variable from entity_property(Cargo, value, Value).",
        "For numeric variables already bound by prior body goals, use number_greater_than/2 or number_at_most/2 instead of value_greater_than/2 or value_at_most/2.",
        "For percent_at_least/3, use numeric variables after they are bound by prior body goals: percent_at_least(PartValue, WholeValue, ThresholdPercent). Do not use it as a final outcome by itself.",
        "For insufficient percentage or below-threshold exception branches, use percent_below(PartValue, WholeValue, ThresholdPercent), not percent_at_least/3 with a negative status.",
        "For support_count_at_least/2, do not add extra supported(Proposal, role_label) goals unless the source explicitly makes that officer role a condition. The helper already proves the threshold count from supported/2 rows.",
        "Set source='direct' only because the source document explicitly states the rule.",
    ]
    if "aggregation" in str(rule_class).casefold():
        core.extend(
            [
                "For aggregation rule classes, prefer derived_condition/3 heads such as derived_condition(Proposal, support_threshold_met, council_vote).",
                "Do not derive final passed/failed outcome from the aggregation lens when veto, override, exception, or priority rules also affect the outcome.",
                "Use support_count_at_least(Proposal, Threshold) as the body proof for threshold_met and stop there.",
            ]
        )
    if compact:
        if "exception" in str(rule_class).casefold():
            core.extend(
                [
                    "For exception-bearing rule classes, prefer one explicit exception-branch clause when raw_source_text states the exception and existing_admitted_backbone contains matching support rows.",
                    "Do not invert exception semantics: exempt support must derive exempt status, not taxable status.",
                ]
            )
        return core
    return [
        *core,
        "Do not use other charter rules visible in profile summaries or admitted backbone context as direct rule evidence.",
        "Each clause must be a single-line JSON string. Do not put literal line breaks, comments, markdown, bullets, or explanatory prose inside candidate_operations[].clause.",
        "For this first rule-lens trial, prefer runtime-simple clauses: Head :- Body1, Body2. Avoid negation, arithmetic, comparisons, lists, disjunction, aggregation, and nested structures unless the existing runtime explicitly supports the helper predicate.",
        "Do not write a lowercase generic placeholder like repair_order when you mean a variable.",
        "Prefer copying body goals directly from existing_admitted_backbone clauses. Preserve the admitted predicate, argument positions, property keys, and property values instead of rewriting them into a nearby semantic shape.",
        "Prefer clauses that can actually fire against the current admitted backbone when the source contains an instance. General dormant rules are allowed only when the body predicates and argument contracts are visibly present but no current instance is stated.",
        "Avoid class-predicate fanout. Do not bind a head variable only with broad class predicates such as person/1, place/1, cargo/1, or vessel/1. Every head variable should either be a source-stated constant or be joined through a non-class relation such as event_at, status_at, certified_record, claim, permission_at, temporal_window, requirement, exception, override, taxable_if, or another admitted relation.",
        "Prefer source-stated constants over fake generality when the admitted backbone only contains instance-level facts. If the source says the relevant place is archive_vault, put archive_vault in the head/body rather than place(ArchiveVault).",
        "For rule-head scope/context arguments, copy an existing admitted rule/source anchor atom from existing_admitted_backbone. Do not invent a generic scope atom merely because it describes the domain area.",
        "Do not use member/2, lists, square brackets, equality/unification goals such as X = value, comparison operators, \\+, not/1, or arithmetic in this rule-lens mode. If a source has multiple required signers or supports, use repeated admitted relation goals with source-stated constants.",
        "Match allowed rule-head arities exactly: derived_permission/4 needs four arguments; derived_authorization/3 needs three; derived_obligation/3 needs three.",
        "Do not infer permission from occurrence. An event_at row that someone entered, signed, recovered, baked, arrived, or voted is not by itself a rule body proving the action was permitted or authorized.",
        "Do not invert exception-summary predicates. If a row says taxable_if(lamp_rice, relief_cargo, exempt), that supports an exempt status, not a taxable status.",
        "Rules must be grounded in explicit source-stated rule language in raw_source_text and should use admitted backbone predicates as body support.",
        "If a charter rule requires negation or exception semantics that cannot be expressed safely, do not force it. Add a short self_check note naming the missing helper instead.",
        "If current_pass.rule_class names an exception-bearing rule class, prefer one explicit exception-branch clause when raw_source_text states the exception and existing_admitted_backbone contains matching support rows.",
        "Claim/finding, permission/event, and source-priority boundaries must survive: do not write a rule that turns a claim into a finding or permission into occurrence.",
        "Keep self_check tiny: at most one note under eight words. Do not explain each rule. Spend output on valid JSON candidate_operations only.",
    ]


def _runtime_trial(
    *,
    facts: list[str],
    backbone_rules: list[str],
    rule_lens_rules: list[str],
    positive_queries: list[str] | None = None,
    negative_queries: list[str] | None = None,
) -> dict[str, Any]:
    runtime = CorePrologRuntime(max_depth=500)
    fact_signature_counts = _fact_signature_counts(facts)
    fact_errors: list[str] = []
    backbone_rule_errors: list[str] = []
    rule_load_errors: list[str] = []
    for fact in facts:
        result = runtime.assert_fact(fact)
        if str(result.get("status", "")) != "success":
            fact_errors.append(f"{fact}: {result.get('message', result)}")
    for rule in backbone_rules:
        result = runtime.assert_rule(rule)
        if str(result.get("status", "")) != "success":
            backbone_rule_errors.append(f"{rule}: {result.get('message', result)}")
    loaded_rules: list[str] = []
    combined_derived_queries: list[dict[str, Any]] = []
    isolated_derived_queries: list[dict[str, Any]] = []
    for rule in rule_lens_rules:
        result = runtime.assert_rule(rule)
        if str(result.get("status", "")) == "success":
            loaded_rules.append(rule)
            query = _rule_head_query(rule)
            if query:
                query_result = runtime.query_rows(query)
                combined_derived_queries.append(
                    {
                        "rule": rule,
                        "head_query": query,
                        "trial_scope": "combined_rules",
                        "status": str(query_result.get("status", "")),
                        "num_rows": int(query_result.get("num_rows", 0) or 0),
                        "rows": query_result.get("rows", [])[:10] if isinstance(query_result.get("rows"), list) else [],
                    }
                )
                isolated_derived_queries.append(
                    _isolated_rule_trial_item(
                        rule=rule,
                        facts=facts,
                        backbone_rules=backbone_rules,
                        fact_signature_counts=fact_signature_counts,
                    )
                )
        else:
            rule_load_errors.append(f"{rule}: {result.get('message', result)}")
    for item in isolated_derived_queries:
        item["lifecycle_status"] = _rule_trial_item_lifecycle(item)
    composition_derived_queries = [
        _composition_rule_trial_item(
            rule=rule,
            sibling_rules=loaded_rules,
            facts=facts,
            backbone_rules=backbone_rules,
            fact_signature_counts=fact_signature_counts,
        )
        for rule in loaded_rules
    ]
    for item in composition_derived_queries:
        item["lifecycle_status"] = _rule_trial_item_lifecycle(item)
    promotion_ready_rule_count = sum(1 for item in isolated_derived_queries if _rule_trial_item_promotion_ready(item))
    composition_ready_rule_count = sum(
        1 for item in composition_derived_queries if _rule_trial_item_promotion_ready(item)
    )
    isolated_ready_rules = {
        str(item.get("rule", "")).strip()
        for item in isolated_derived_queries
        if _rule_trial_item_promotion_ready(item)
    }
    composition_ready_rules = {
        str(item.get("rule", "")).strip()
        for item in composition_derived_queries
        if _rule_trial_item_promotion_ready(item)
    }
    positive_probe_results = _probe_queries(runtime, positive_queries or [], expect_rows=True)
    negative_probe_results = _probe_queries(runtime, negative_queries or [], expect_rows=False)
    unexpected_solution_count = sum(
        int(item.get("num_rows", 0) or 0)
        for item in negative_probe_results
        if not bool(item.get("passed", False))
    )
    return {
        "facts_loaded": len(facts) - len(fact_errors),
        "backbone_rules_loaded": len(backbone_rules) - len(backbone_rule_errors),
        "rule_lens_rules_loaded": len(loaded_rules),
        "fact_load_errors": fact_errors[:20],
        "backbone_rule_load_errors": backbone_rule_errors[:20],
        "rule_load_errors": rule_load_errors[:40],
        "loaded_rule_examples": loaded_rules[:20],
        "trial_scope": "isolated_rule_for_promotion_combined_rules_for_probes",
        "derived_head_queries": isolated_derived_queries,
        "composition_head_queries": composition_derived_queries,
        "combined_head_queries": combined_derived_queries,
        "firing_rule_count": sum(1 for item in isolated_derived_queries if int(item.get("num_rows", 0) or 0) > 0),
        "composition_firing_rule_count": sum(
            1 for item in composition_derived_queries if int(item.get("num_rows", 0) or 0) > 0
        ),
        "high_fanout_rule_count": sum(1 for item in isolated_derived_queries if int(item.get("num_rows", 0) or 0) > 5),
        "promotion_ready_rule_count": promotion_ready_rule_count,
        "composition_ready_rule_count": composition_ready_rule_count,
        "composition_rescued_rule_count": len(composition_ready_rules - isolated_ready_rules),
        "lifecycle_counts": _rule_lifecycle_counts(isolated_derived_queries, rule_load_errors),
        "composition_lifecycle_counts": _rule_lifecycle_counts(composition_derived_queries, rule_load_errors),
        "dormant_rule_count": sum(1 for item in isolated_derived_queries if int(item.get("num_rows", 0) or 0) == 0),
        "unsupported_body_signature_count": sum(
            len(item.get("unsupported_body_signatures", []))
            for item in isolated_derived_queries
            if isinstance(item.get("unsupported_body_signatures"), list)
        ),
        "unsupported_body_goal_count": sum(
            len(item.get("unsupported_body_goals", []))
            for item in isolated_derived_queries
            if isinstance(item.get("unsupported_body_goals"), list)
        ),
        "unsupported_body_fragment_count": sum(
            len(item.get("unsupported_body_fragments", []))
            for item in isolated_derived_queries
            if isinstance(item.get("unsupported_body_fragments"), list)
        ),
        "positive_probe_results": positive_probe_results,
        "negative_probe_results": negative_probe_results,
        "expected_positive_count": len(positive_probe_results),
        "expected_negative_count": len(negative_probe_results),
        "positive_probe_pass_count": sum(1 for item in positive_probe_results if bool(item.get("passed", False))),
        "negative_probe_pass_count": sum(1 for item in negative_probe_results if bool(item.get("passed", False))),
        "missed_positive_count": sum(1 for item in positive_probe_results if not bool(item.get("passed", False))),
        "unexpected_solution_count": unexpected_solution_count,
        "probe_adjusted_promotion_ready": bool(
            promotion_ready_rule_count > 0
            and all(bool(item.get("passed", False)) for item in positive_probe_results)
            and all(bool(item.get("passed", False)) for item in negative_probe_results)
        ),
        "composition_probe_adjusted_promotion_ready": bool(
            composition_ready_rule_count > 0
            and all(bool(item.get("passed", False)) for item in positive_probe_results)
            and all(bool(item.get("passed", False)) for item in negative_probe_results)
        ),
    }


def _composition_rule_trial_item(
    *,
    rule: str,
    sibling_rules: list[str],
    facts: list[str],
    backbone_rules: list[str],
    fact_signature_counts: dict[str, int],
) -> dict[str, Any]:
    target_head_signature = _clause_head_signature(rule)
    dependency_signatures = {
        signature
        for signature in _rule_body_signatures(rule)
        if signature.split("/", 1)[0].startswith("derived_")
    }
    dependency_rules = [
        sibling
        for sibling in sibling_rules
        if sibling != rule
        and _clause_head_signature(sibling) in dependency_signatures
        and _clause_head_signature(sibling) != target_head_signature
    ]
    item = _isolated_rule_trial_item(
        rule=rule,
        facts=facts,
        backbone_rules=[*backbone_rules, *dependency_rules],
        fact_signature_counts=fact_signature_counts,
    )
    item["trial_scope"] = "composition_dependency_rule"
    item["dependency_rule_count"] = len(dependency_rules)
    item["dependency_rule_examples"] = dependency_rules[:10]
    item["dependency_signatures"] = sorted(dependency_signatures)
    item["same_head_sibling_rules_excluded"] = [
        sibling
        for sibling in sibling_rules
        if sibling != rule and _clause_head_signature(sibling) == target_head_signature
    ][:10]
    return item


def _isolated_rule_trial_item(
    *,
    rule: str,
    facts: list[str],
    backbone_rules: list[str],
    fact_signature_counts: dict[str, int],
) -> dict[str, Any]:
    runtime = CorePrologRuntime(max_depth=500)
    fact_errors: list[str] = []
    backbone_rule_errors: list[str] = []
    for fact in facts:
        result = runtime.assert_fact(fact)
        if str(result.get("status", "")) != "success":
            fact_errors.append(f"{fact}: {result.get('message', result)}")
    for backbone_rule in backbone_rules:
        result = runtime.assert_rule(backbone_rule)
        if str(result.get("status", "")) != "success":
            backbone_rule_errors.append(f"{backbone_rule}: {result.get('message', result)}")
    query = _rule_head_query(rule)
    body_support = [
        {
            "signature": signature,
            "matching_fact_count": int(fact_signature_counts.get(signature, 0)),
        }
        for signature in _rule_body_signatures(rule)
    ]
    result = runtime.assert_rule(rule)
    if str(result.get("status", "")) != "success":
        return {
            "rule": rule,
            "head_query": query,
            "trial_scope": "isolated_rule",
            "status": str(result.get("status", "")),
            "num_rows": 0,
            "rows": [],
            "body_support": body_support,
            "unsupported_body_signatures": [],
            "body_goal_support": [],
            "unsupported_body_goals": [],
            "unsupported_body_fragments": _unsupported_body_fragments(rule),
            "isolated_fact_load_errors": fact_errors[:10],
            "isolated_backbone_rule_load_errors": backbone_rule_errors[:10],
        }
    query_result = runtime.query_rows(query) if query else {"status": "skipped", "num_rows": 0, "rows": []}
    num_rows = int(query_result.get("num_rows", 0) or 0)
    body_goal_support = _rule_body_goal_support(rule, facts, runtime=runtime)
    supported_goal_signatures = {
        str(item.get("signature", ""))
        for item in body_goal_support
        if int(item.get("matching_fact_count", 0) or 0) > 0
    }
    runtime_supported_goal_signatures = set(supported_goal_signatures)
    if num_rows > 0:
        runtime_supported_goal_signatures.update(CONTEXT_DEPENDENT_HELPER_SIGNATURES)
    return {
        "rule": rule,
        "head_query": query,
        "trial_scope": "isolated_rule",
        "status": str(query_result.get("status", "")),
        "num_rows": num_rows,
        "rows": query_result.get("rows", [])[:10] if isinstance(query_result.get("rows"), list) else [],
        "body_support": body_support,
        "unsupported_body_signatures": [
            item["signature"]
            for item in body_support
            if int(item["matching_fact_count"]) == 0
            and str(item.get("signature", "")) not in runtime_supported_goal_signatures
        ],
        "body_goal_support": body_goal_support,
        "unsupported_body_goals": [
            item["goal"]
            for item in body_goal_support
            if int(item["matching_fact_count"]) == 0
            and str(item.get("signature", "")) not in runtime_supported_goal_signatures
        ],
        "unsupported_body_fragments": _unsupported_body_fragments(rule),
        "isolated_fact_load_errors": fact_errors[:10],
        "isolated_backbone_rule_load_errors": backbone_rule_errors[:10],
    }


def _rule_trial_item_lifecycle(item: dict[str, Any]) -> str:
    if _rule_trial_item_promotion_ready(item):
        return "promotion_ready_rule"
    if int(item.get("num_rows", 0) or 0) > 0:
        return "firing_rule"
    if str(item.get("status", "")).strip() in {"success", "no_results"}:
        return "runtime_loadable_rule"
    return "mapper_admitted_rule"


def _rule_lifecycle_counts(derived_queries: list[dict[str, Any]], rule_load_errors: list[str]) -> dict[str, int]:
    counts = {
        "candidate_rule": len(derived_queries) + len(rule_load_errors),
        "mapper_admitted_rule": len(derived_queries) + len(rule_load_errors),
        "runtime_loadable_rule": len(derived_queries),
        "firing_rule": sum(1 for item in derived_queries if int(item.get("num_rows", 0) or 0) > 0),
        "promotion_ready_rule": sum(1 for item in derived_queries if _rule_trial_item_promotion_ready(item)),
        "durable_rule": 0,
    }
    return counts


def _rule_trial_item_promotion_ready(item: dict[str, Any]) -> bool:
    if int(item.get("num_rows", 0) or 0) <= 0:
        return False
    if int(item.get("num_rows", 0) or 0) > 5:
        return False
    for key in ("unsupported_body_signatures", "unsupported_body_goals", "unsupported_body_fragments"):
        value = item.get(key, [])
        if isinstance(value, list) and value:
            return False
    return str(item.get("status", "")).strip() == "success"


def _probe_queries(runtime: CorePrologRuntime, queries: list[str], *, expect_rows: bool) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for query in queries:
        clean_query = str(query).strip()
        if not clean_query:
            continue
        result = runtime.query_rows(clean_query)
        num_rows = int(result.get("num_rows", 0) or 0)
        passed = num_rows > 0 if expect_rows else num_rows == 0
        results.append(
            {
                "query": clean_query,
                "expectation": "rows" if expect_rows else "no_rows",
                "status": str(result.get("status", "")),
                "num_rows": num_rows,
                "passed": passed,
                "rows": result.get("rows", [])[:10] if isinstance(result.get("rows"), list) else [],
            }
        )
    return results


def _compile_items(record: dict[str, Any], key: str) -> list[str]:
    source_compile = record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {}
    return [str(item).strip() for item in source_compile.get(key, []) if str(item).strip()]


def _signatures_from_clauses(clauses: list[str]) -> set[str]:
    signatures: set[str] = set()
    for clause in clauses:
        for name, args_text in re.findall(r"\b([a-z_][a-z0-9_]*)\s*\(([^()]*)\)", str(clause)):
            args = [] if not args_text.strip() else [part.strip() for part in args_text.split(",")]
            signatures.add(f"{name}/{len(args)}")
    return signatures


def _rule_head_query(rule: str) -> str:
    head = str(rule).split(":-", 1)[0].strip()
    match = re.match(r"^([a-z_][a-z0-9_]*)\s*\((.*)\)\s*$", head)
    if not match:
        return ""
    name = match.group(1)
    args_text = match.group(2).strip()
    arity = 0 if not args_text else len([part.strip() for part in args_text.split(",")])
    args = [f"V{index}" for index in range(1, arity + 1)]
    return f"{name}({', '.join(args)})."


def _fact_signature_counts(facts: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for fact in facts:
        signature = _clause_head_signature(fact)
        if signature:
            counts[signature] = counts.get(signature, 0) + 1
    return counts


def _clause_head_signature(clause: str) -> str:
    head = str(clause).split(":-", 1)[0].strip().rstrip(".")
    match = re.match(r"^([a-z_][a-z0-9_]*)\s*\((.*)\)\s*$", head)
    if not match:
        return ""
    args_text = match.group(2).strip()
    arity = 0 if not args_text else len([part.strip() for part in args_text.split(",")])
    return f"{match.group(1)}/{arity}"


def _rule_body_signatures(rule: str) -> list[str]:
    if ":-" not in str(rule):
        return []
    body = str(rule).split(":-", 1)[1].strip().rstrip(".")
    signatures: list[str] = []
    for name, args_text in re.findall(r"\b([a-z_][a-z0-9_]*)\s*\(([^()]*)\)", body):
        arity = 0 if not args_text.strip() else len([part.strip() for part in args_text.split(",")])
        signature = f"{name}/{arity}"
        if signature not in signatures:
            signatures.append(signature)
    return signatures


def _rule_body_goal_support(rule: str, facts: list[str], runtime: CorePrologRuntime | None = None) -> list[dict[str, Any]]:
    fact_goals = [_parse_simple_goal(fact.rstrip(".")) for fact in facts]
    fact_goals = [goal for goal in fact_goals if goal]
    support: list[dict[str, Any]] = []
    for goal_text in _rule_body_goal_texts(rule):
        goal = _parse_simple_goal(goal_text)
        if not goal:
            continue
        matches = [fact for fact in fact_goals if _goal_pattern_matches_fact(goal, fact)]
        virtual_rows: list[dict[str, Any]] = []
        if not matches and runtime is not None:
            virtual_query = _format_goal(goal)
            query_result = runtime.query_rows(virtual_query)
            if str(query_result.get("status", "")) == "success" and isinstance(query_result.get("rows"), list):
                virtual_rows = query_result.get("rows", [])[:5]
        support.append(
            {
                "goal": goal_text,
                "signature": f"{goal[0]}/{len(goal[1])}",
                "matching_fact_count": len(matches) if matches else len(virtual_rows),
                "matching_fact_examples": [_format_goal(item) for item in matches[:5]],
                "virtual_row_examples": virtual_rows,
            }
        )
    return support


def _rule_body_goal_texts(rule: str) -> list[str]:
    if ":-" not in str(rule):
        return []
    body = str(rule).split(":-", 1)[1].strip().rstrip(".")
    return [
        match.group(0).strip()
        for match in re.finditer(r"\b[a-z_][a-z0-9_]*\s*\([^()]*\)", body)
    ]


def _unsupported_body_fragments(rule: str) -> list[str]:
    if ":-" not in str(rule):
        return []
    body = str(rule).split(":-", 1)[1].strip().rstrip(".")
    remainder = body
    for goal in _rule_body_goal_texts(rule):
        remainder = remainder.replace(goal, " ", 1)
    fragments: list[str] = []
    for raw in re.split(r"\s*,\s*", remainder):
        fragment = raw.strip()
        if not fragment:
            continue
        if re.fullmatch(r"[\s,]+", fragment):
            continue
        fragments.append(fragment)
    fragments.extend(_unsupported_helper_goal_fragments(rule))
    return fragments


def _unsupported_helper_goal_fragments(rule: str) -> list[str]:
    value_variables: set[str] = set()
    fragments: list[str] = []
    for goal_text in _rule_body_goal_texts(rule):
        goal = _parse_simple_goal(goal_text)
        if not goal:
            continue
        name, args = goal
        if name == "entity_property" and len(args) == 3 and args[1] == "value" and _is_rule_variable(args[2]):
            value_variables.add(args[2])
    for goal_text in _rule_body_goal_texts(rule):
        goal = _parse_simple_goal(goal_text)
        if not goal:
            continue
        name, args = goal
        if name not in {"value_greater_than", "value_at_most"} or len(args) != 2:
            continue
        first_arg = args[0]
        threshold_arg = args[1]
        if first_arg in value_variables:
            fragments.append(f"{goal_text} uses value variable where entity argument is required")
        elif _looks_like_numeric_measure_variable(first_arg):
            fragments.append(f"{goal_text} uses numeric measure variable where entity argument is required")
        elif re.fullmatch(r"-?\d+(?:\.\d+)?", first_arg):
            fragments.append(f"{goal_text} uses numeric literal where entity argument is required")
        if _looks_like_unsupported_helper_threshold(threshold_arg):
            fragments.append(f"{goal_text} uses computed or variable threshold where literal threshold is required")
    return fragments


def _parse_simple_goal(text: str) -> tuple[str, list[str]] | None:
    match = re.match(r"^\s*([a-z_][a-z0-9_]*)\s*\((.*)\)\s*$", str(text).strip())
    if not match:
        return None
    args_text = match.group(2).strip()
    args = [] if not args_text else [part.strip() for part in args_text.split(",")]
    return match.group(1), args


def _goal_pattern_matches_fact(goal: tuple[str, list[str]], fact: tuple[str, list[str]]) -> bool:
    goal_name, goal_args = goal
    fact_name, fact_args = fact
    if goal_name != fact_name or len(goal_args) != len(fact_args):
        return False
    for goal_arg, fact_arg in zip(goal_args, fact_args):
        if _is_rule_variable(goal_arg):
            continue
        if goal_arg != fact_arg:
            return False
    return True


def _is_rule_variable(value: str) -> bool:
    text = str(value or "").strip()
    return bool(text == "_" or re.match(r"^[A-Z][A-Za-z0-9_]*$", text))


def _looks_like_numeric_measure_variable(value: str) -> bool:
    text = str(value or "").strip()
    if not _is_rule_variable(text):
        return False
    return bool(
        re.search(
            r"(amount|value|match|threshold|count|total|number|hours|days|percent|percentage|ratio|n)$",
            text,
            flags=re.IGNORECASE,
        )
    )


def _looks_like_unsupported_helper_threshold(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return True
    if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        return False
    return bool(_is_rule_variable(text) or re.search(r"[+*/]|(?<!^)-", text))


def _format_goal(goal: tuple[str, list[str]]) -> str:
    return f"{goal[0]}({', '.join(goal[1])})."


if __name__ == "__main__":
    raise SystemExit(main())
