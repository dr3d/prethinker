#!/usr/bin/env python3
"""Run a support-row acquisition pass over an existing safe compile.

This is a post-backbone source pass. Python does not inspect source prose for
facts, entities, or predicates. It hands the raw source plus an already-admitted
KB surface to an LLM and asks for support/rationale rows only. The deterministic
Semantic IR mapper still decides which proposals become admitted clauses.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_file"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_domain_bootstrap_file import (  # noqa: E402
    SOURCE_PASS_OPS_JSON_SCHEMA,
    _call_lmstudio_json_schema,
    _load_profile_registry,
    _profile_from_registry,
    _slug,
    _source_pass_ops_to_semantic_ir,
)
from src.semantic_ir import semantic_ir_to_legacy_parse  # noqa: E402
from src.profile_bootstrap import (  # noqa: E402
    profile_bootstrap_allowed_predicates,
    profile_bootstrap_domain_context,
    profile_bootstrap_predicate_contracts,
)


SUPPORT_PREDICATES = [
    {
        "signature": "support_reason/2",
        "args": ["anchor", "reason"],
        "description": "Reason or rationale directly stated by the source for an existing admitted guidance anchor.",
        "why": "support_acquisition",
        "admission_notes": ["Support rows must be grounded in raw source text and link to an existing admitted anchor atom."],
    },
    {
        "signature": "support_effect/2",
        "args": ["anchor", "effect"],
        "description": "Effect or consequence directly stated by the source for an existing admitted guidance anchor.",
        "why": "support_acquisition",
        "admission_notes": ["Support rows must be grounded in raw source text and link to an existing admitted anchor atom."],
    },
    {
        "signature": "support_tradeoff/3",
        "args": ["anchor", "benefit", "cost_or_risk"],
        "description": "Benefit and downside directly stated by the source for an existing admitted choice or tactic.",
        "why": "support_acquisition",
        "admission_notes": ["Support rows must be grounded in raw source text and link to an existing admitted anchor atom."],
    },
    {
        "signature": "support_exception/2",
        "args": ["anchor", "exception"],
        "description": "Exception, caveat, or boundary directly stated by the source for an existing admitted guidance anchor.",
        "why": "support_acquisition",
        "admission_notes": ["Support rows must be grounded in raw source text and link to an existing admitted anchor atom."],
    },
    {
        "signature": "support_positive_counterpart/2",
        "args": ["anchor", "preferred_action"],
        "description": "Positive replacement or preferred action directly stated for an admitted avoid/risk anchor.",
        "why": "support_acquisition",
        "admission_notes": ["Support rows must be grounded in raw source text and link to an existing admitted anchor atom."],
    },
]

SUPPORT_LIKE_SIGNATURES = {
    "action_when/2",
    "debugging_tactic/2",
    "delta_load_pattern/2",
    "does_not_directly_determine/2",
    "enables/2",
    "export_reason/2",
    "guard_effect/1",
    "guard_mechanism/1",
    "guard_value/1",
    "list_load_risk/2",
    "metric_semantics/2",
    "priority_reason/2",
    "reduce_list_load_impact/1",
    "source_detail/4",
    "summary_review_question/1",
    "tradeoff/3",
    "validates_when_high/2",
}

BODY_FACT_PREDICATES = [
    {
        "signature": "required_condition/2",
        "args": ["anchor", "condition"],
        "description": "A source-stated condition, requirement, or checklist item attached to an admitted anchor such as an applicant, proposal, approval, or procedure.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for explicitly stated required conditions needed by later rule bodies."],
    },
    {
        "signature": "recovered_from_water/3",
        "args": ["person", "cargo", "time"],
        "description": "A source-stated recovery event where a person recovered cargo from water at a time.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only when directly stated in raw source text."],
    },
    {
        "signature": "abandoned/1",
        "args": ["cargo"],
        "description": "Cargo or object directly stated as abandoned.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for source-stated abandoned cargo/items."],
    },
    {
        "signature": "sacred/1",
        "args": ["cargo"],
        "description": "Cargo or object directly stated as marked sacred.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for source-stated sacred cargo/items."],
    },
    {
        "signature": "not_sacred/1",
        "args": ["cargo"],
        "description": "Cargo or object directly stated as not marked sacred.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for explicit not-sacred source statements."],
    },
    {
        "signature": "quarantine_patient/1",
        "args": ["patient"],
        "description": "Person directly stated to be a quarantine patient.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for source-stated quarantine-patient status."],
    },
    {
        "signature": "no_fever/2",
        "args": ["patient", "time"],
        "description": "Physician record directly states that the patient had no fever at a time.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for source-stated physician no-fever records."],
    },
    {
        "signature": "negative_test/2",
        "args": ["patient", "time"],
        "description": "Physician record directly states a negative quarantine test at a time.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for source-stated negative test records."],
    },
    {
        "signature": "proposal/1",
        "args": ["proposal"],
        "description": "A source-stated council proposal or motion.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for source-stated proposals/motions."],
    },
    {
        "signature": "budget_matter/1",
        "args": ["proposal"],
        "description": "A proposal directly stated to be a budget matter.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for source-stated budget-matter classification."],
    },
    {
        "signature": "supported/2",
        "args": ["proposal", "officer"],
        "description": "A source-stated council officer support vote for a proposal.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for explicit support votes."],
    },
    {
        "signature": "treasurer_veto/2",
        "args": ["proposal", "treasurer"],
        "description": "A source-stated Treasurer veto of a proposal.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for explicit Treasurer veto statements."],
    },
    {
        "signature": "no_emergency_override/1",
        "args": ["proposal"],
        "description": "Source directly states that no emergency override was issued for a proposal.",
        "why": "body_fact_acquisition",
        "admission_notes": ["Use only for explicit absence of emergency override."],
    },
]


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
    parser.add_argument("--operation-target", type=int, default=48)
    parser.add_argument("--max-tokens", type=int, default=10000)
    parser.add_argument("--lens", choices=["support", "body_fact"], default="support")
    parser.add_argument("--source-line-start", type=int, default=0)
    parser.add_argument("--source-line-end", type=int, default=0)
    parser.add_argument(
        "--allowed-predicate-filter",
        default="",
        help="Optional comma-separated predicate names/signatures to expose in the active lens palette.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text_path = args.text_file if args.text_file.is_absolute() else (REPO_ROOT / args.text_file).resolve()
    backbone_path = args.backbone_json if args.backbone_json.is_absolute() else (REPO_ROOT / args.backbone_json).resolve()
    registry = _load_profile_registry(args.profile_registry)
    if not registry:
        raise SystemExit("--profile-registry did not load")
    parsed_profile = _support_acquisition_profile(
        _profile_from_registry(registry, domain_hint=str(args.domain_hint or "")),
        lens=str(args.lens or "support"),
    )
    allowed_predicate_filter = _predicate_filter(str(args.allowed_predicate_filter or ""))
    if allowed_predicate_filter:
        parsed_profile = _filter_profile_predicates(parsed_profile, allowed_predicate_filter)
    source_text = text_path.read_text(encoding="utf-8-sig")
    if int(args.source_line_start or 0) > 0 or int(args.source_line_end or 0) > 0:
        source_text = _line_range(source_text, int(args.source_line_start or 0), int(args.source_line_end or 0))
    backbone = json.loads(backbone_path.read_text(encoding="utf-8-sig"))
    backbone_facts = _compile_items(backbone, "facts")
    backbone_rules = _compile_items(backbone, "rules")
    started = time.perf_counter()
    support_compile = _run_support_pass(
        args=args,
        source_text=source_text,
        source_name=text_path.name,
        parsed_profile=parsed_profile,
        backbone_facts=backbone_facts,
        backbone_rules=backbone_rules,
    )
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": "support_acquisition_pass",
        "text_file": str(text_path),
        "domain_hint": str(args.domain_hint or ""),
        "backend": "lmstudio",
        "model": str(args.model),
        "profile_registry": str(args.profile_registry),
        "support_backbone_json": str(backbone_path),
        "lens": str(args.lens or "support"),
        "source_line_start": int(args.source_line_start or 0),
        "source_line_end": int(args.source_line_end or 0),
        "allowed_predicate_filter": sorted(allowed_predicate_filter),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parsed_ok": True,
        "score": {
            "predicate_count": len(parsed_profile.get("candidate_predicates", [])),
            "support_predicate_count": len(SUPPORT_PREDICATES),
        },
        "parsed": parsed_profile,
        "source_compile": support_compile,
        "support_acquisition_policy": [
            "The raw source document is direct evidence.",
            "The admitted backbone surface is context guidance and anchor vocabulary only.",
            "The pass may add support/rationale rows but must not rewrite the backbone.",
            "The deterministic mapper decides admission.",
        ],
    }
    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(text_path.stem)}-support_{_slug(str(args.model))}"
    json_path = out_dir / f"domain_bootstrap_file_{slug}.json"
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(
        json.dumps(
            {
                "compile_admitted": support_compile.get("admitted_count"),
                "compile_skipped": support_compile.get("skipped_count"),
                "facts": len(support_compile.get("facts", [])),
                "rules": len(support_compile.get("rules", [])),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _support_acquisition_profile(profile: dict[str, Any], *, lens: str = "support") -> dict[str, Any]:
    support_like = []
    for item in profile.get("candidate_predicates", []) if isinstance(profile.get("candidate_predicates"), list) else []:
        if not isinstance(item, dict):
            continue
        if str(item.get("signature", "")).strip() in SUPPORT_LIKE_SIGNATURES:
            support_like.append(item)
    out = dict(profile)
    out["domain_guess"] = str(out.get("domain_guess", "") or "support_acquisition")
    out["domain_scope"] = (
        str(out.get("domain_scope", "")).strip()
        + " | support acquisition pass: rationale/effect/tradeoff rows only"
    ).strip(" |")
    if str(lens).strip().lower() == "body_fact":
        out["candidate_predicates"] = BODY_FACT_PREDICATES
        out["domain_scope"] = (
            str(out.get("domain_scope", "")).strip()
            + " | body-fact acquisition pass: rule-body support rows only"
        ).strip(" |")
    else:
        out["candidate_predicates"] = [*support_like, *SUPPORT_PREDICATES]
    out["admission_risks"] = [
        *[str(item) for item in out.get("admission_risks", []) if str(item).strip()],
        "Support acquisition must not introduce new backbone recommendations or facts.",
        "Support rows must be source-grounded and must link to existing admitted anchor atoms when using support_* predicates.",
        "Body-fact acquisition must emit only source-stated rows needed by rule bodies.",
    ]
    out["self_check"] = {
        **(out.get("self_check") if isinstance(out.get("self_check"), dict) else {}),
        "profile_authority": "proposal_only",
        "support_acquisition_only": str(lens).strip().lower() != "body_fact",
        "body_fact_acquisition_only": str(lens).strip().lower() == "body_fact",
    }
    return out


def _run_support_pass(
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
    target = max(1, int(args.operation_target or 48))
    payload = {
        "task": "Emit pass-specific source_pass_ops_v1 rows for an existing safe compile.",
        "authority": "proposal_only_mapper_remains_authoritative",
        "domain_hint": str(args.domain_hint or ""),
        "source_name": source_name,
        "raw_source_text": source_text,
        "existing_admitted_backbone": {
            "facts": backbone_facts,
            "rules": backbone_rules,
            "policy": [
                "These clauses are context anchors, not raw evidence.",
                "Use their atoms to link support rows to already-admitted guidance.",
                "Do not re-emit or rewrite these rows.",
            ],
        },
        "current_pass": {
            "pass_id": "support_acquisition_v1",
            "lens": str(args.lens or "support"),
            "purpose": "Add source-grounded rows for the current semantic lens.",
            "focus": (
                "Only rule-body support facts directly stated in the raw source span."
                if str(args.lens or "support") == "body_fact"
                else "Only support/rationale rows that make existing admitted guidance more answerable."
            ),
            "completion_policy": "Prefer high-query-value support rows for why/how/tradeoff questions. Omit unsupported rows.",
            "operation_target": target,
        },
        "allowed_predicates": allowed_predicates,
        "predicate_contracts": predicate_contracts,
        "domain_context": domain_context,
        "guidance_context": _support_guidance_context(lens=str(args.lens or "support")),
    }
    try:
        response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=[
                {
                    "role": "system",
                    "content": _support_system_prompt(lens=str(args.lens or "support")),
                },
                {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
            ],
            schema=SOURCE_PASS_OPS_JSON_SCHEMA,
            schema_name="source_pass_ops_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), max(4000, min(12000, target * 220))),
        )
        parsed = json.loads(str(response.get("content", "{}")))
    except Exception as exc:
        return {"ok": False, "error": f"support_acquisition_failed:{exc}", "facts": [], "rules": [], "queries": []}
    ir = _source_pass_ops_to_semantic_ir(parsed if isinstance(parsed, dict) else {})
    mapped, warnings = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    return {
        "ok": bool(isinstance(parsed, dict) and parsed.get("schema_version") == "source_pass_ops_v1"),
        "mode": "support_acquisition_pass",
        "model_decision": ir.get("decision", ""),
        "projected_decision": diagnostics.get("projected_decision", ""),
        "admitted_count": int(diagnostics.get("admitted_count", 0) or 0),
        "skipped_count": int(diagnostics.get("skipped_count", 0) or 0),
        "warnings": warnings,
        "admission_diagnostics": diagnostics,
        "facts": mapped.get("facts", []),
        "rules": mapped.get("rules", []),
        "queries": mapped.get("queries", []),
        "self_check": ir.get("self_check", {}),
        "source_pass_ops": parsed if isinstance(parsed, dict) else {},
    }


def _support_guidance_context(*, lens: str) -> list[str]:
    common = [
        "This is not a second default compile. It is a support-row acquisition pass.",
        "The raw source text is direct evidence; the existing admitted backbone is anchor context only.",
        "Do not create new recommendation families, new priority targets, or broad source facts.",
        "Set source='direct' only for operations grounded in raw_source_text. Context anchors alone are not enough.",
    ]
    if str(lens or "").strip().lower() == "body_fact":
        return [
            *common,
            "For body_fact lens, emit only assert operations using the active allowed body-fact predicates.",
            "Do not emit rules, queries, generic entity_property fallbacks, or generic rationale predicates such as support_reason/2, support_effect/2, support_tradeoff/3, support_exception/2, or support_positive_counterpart/2.",
            "Do not treat allowed vote predicates such as supported/2 as banned generic support_* rows; if supported/2 is active, it is a source-stated body fact for vote-count helpers.",
            "Do not reject explicit instance rows merely because the backbone also has an aggregate result. Body-fact lenses intentionally expose atomic rows needed by helper predicates and later executable rule bodies.",
            "If the active palette can represent an explicit source-stated instance needed by a helper or rule body, emit that row even when it is also implied by a summary line.",
            "Emit no rows when the active allowed predicate palette cannot represent the source span.",
        ]
    return [
        *common,
        "Use support_* predicates only when the first argument is an atom already visible in existing_admitted_backbone or a directly matching source-local guidance anchor.",
        "If an existing allowed support-like predicate fits exactly, prefer it over generic support_*.",
        "For why questions, preserve directly stated reason/effect/tradeoff text as compact snake_case atoms.",
        "Do not over-compress named examples, error classes, exception cases, or product feature names into generic categories. If the source says an action helps catch a named error class, preserve both the general class and the named example in the support atom when possible.",
        "Preserve negative mechanisms as support rows, not only positive replacements. Blocking, increasing memory, increasing cell count, forcing more cells to calculate, preventing on-demand calculation, or creating dense line items are answer-bearing effects when directly stated.",
        "Preserve contrastive conditions exactly. A low-complexity/high-populated-cell case is not the same anchor as a high-complexity/high-cell-count case; if the source contrasts them, emit separate support rows.",
        "For avoid/use-instead questions, preserve the positive counterpart separately from the avoid anchor.",
    ]


def _support_system_prompt(*, lens: str) -> str:
    base = (
        "You are a pass-specific acquisition compiler for a governed symbolic memory system. "
        "You do not decide truth and you do not mutate the KB. Emit only source_pass_ops_v1 JSON. "
    )
    if str(lens or "").strip().lower() == "body_fact":
        return (
            base
            + "Your only job is to propose source-grounded body facts using the active allowed predicates, "
            + "so later helper predicates and executable rule bodies can bind to explicit rows."
        )
    return (
        base
        + "Your only job is to propose source-grounded rationale/effect/tradeoff rows that attach "
        + "to an already-admitted backbone."
    )


def _compile_items(record: dict[str, Any], key: str) -> list[str]:
    source_compile = record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {}
    return [str(item).strip() for item in source_compile.get(key, []) if str(item).strip()]


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


def _filter_profile_predicates(profile: dict[str, Any], predicate_filter: set[str]) -> dict[str, Any]:
    rows = profile.get("candidate_predicates", [])
    if not isinstance(rows, list):
        return profile
    kept = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        signature = str(row.get("signature", "")).strip()
        name = signature.split("/", 1)[0] if signature else ""
        if signature in predicate_filter or name in predicate_filter:
            kept.append(row)
    out = dict(profile)
    out["candidate_predicates"] = kept
    out["active_predicate_filter"] = sorted(predicate_filter)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
