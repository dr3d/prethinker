#!/usr/bin/env python3
"""Populate and score an ACH stress payload without mutating KB state."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from typing import Any
import urllib.error
import urllib.request


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.ach_overlay import analyze_ach_overlay  # noqa: E402
from src.model_path import (  # noqa: E402
    apply_openrouter_provider_env,
    is_openrouter_base_url,
    openrouter_api_key,
    openrouter_generation_metadata,
    openrouter_metadata_headers,
    openrouter_provider_routing_from_env,
    provider_family,
)
from src.semantic_ir import bootstrap_env_local  # noqa: E402


DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "ach_payload_proposer_runs"
VALID_ASSESSMENTS = {"consistent", "inconsistent", "neutral", "not_applicable"}
VALID_DIAGNOSTICITY = {"low", "medium", "high", "critical"}
VALID_QUESTION_AXES = {"cause", "responsibility", "scope", "chronology", "status", "identity", "comparison", "other"}
VALID_HYPOTHESIS_AXIS_FITS = {"direct", "partial", "off_axis"}
VALID_EVIDENCE_ROLES = {
    "question_anchor",
    "occurrence_anchor",
    "mechanism_support",
    "exclusion_or_counterevidence",
    "scope_boundary",
    "context",
    "remedy_or_consequence",
    "other",
}


PROPOSER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "question_axis",
        "hypothesis_axis_fit",
        "evidence_roles",
        "evidence_diagnosticity",
        "judgments",
        "judgment_dependencies",
        "omission_effects",
    ],
    "properties": {
        "question_axis": {"type": "string", "enum": sorted(VALID_QUESTION_AXES)},
        "hypothesis_axis_fit": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["hypothesis_id", "axis_fit", "rationale"],
                "properties": {
                    "hypothesis_id": {"type": "string"},
                    "axis_fit": {"type": "string", "enum": sorted(VALID_HYPOTHESIS_AXIS_FITS)},
                    "rationale": {"type": "string", "maxLength": 360},
                },
            },
        },
        "evidence_roles": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["evidence_id", "role", "rationale"],
                "properties": {
                    "evidence_id": {"type": "string"},
                    "role": {"type": "string", "enum": sorted(VALID_EVIDENCE_ROLES)},
                    "rationale": {"type": "string", "maxLength": 360},
                },
            },
        },
        "evidence_diagnosticity": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["evidence_id", "diagnosticity", "rationale"],
                "properties": {
                    "evidence_id": {"type": "string"},
                    "diagnosticity": {"type": "string", "enum": sorted(VALID_DIAGNOSTICITY)},
                    "rationale": {"type": "string", "maxLength": 360},
                },
            },
        },
        "judgments": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["evidence_id", "hypothesis_id", "assessment", "weight", "rationale"],
                "properties": {
                    "evidence_id": {"type": "string"},
                    "hypothesis_id": {"type": "string"},
                    "assessment": {"type": "string", "enum": sorted(VALID_ASSESSMENTS)},
                    "weight": {"type": "integer", "minimum": 1, "maximum": 5},
                    "rationale": {"type": "string", "maxLength": 360},
                },
            },
        },
        "judgment_dependencies": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "evidence_id",
                    "hypothesis_id",
                    "depends_on_evidence_id",
                    "assessment_without_dependency",
                    "weight_without_dependency",
                    "rationale",
                ],
                "properties": {
                    "evidence_id": {"type": "string"},
                    "hypothesis_id": {"type": "string"},
                    "depends_on_evidence_id": {"type": "string"},
                    "assessment_without_dependency": {"type": "string", "enum": sorted(VALID_ASSESSMENTS)},
                    "weight_without_dependency": {"type": "integer", "minimum": 1, "maximum": 5},
                    "rationale": {"type": "string", "maxLength": 360},
                },
            },
        },
        "omission_effects": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "omitted_evidence_id",
                    "evidence_id",
                    "hypothesis_id",
                    "assessment",
                    "weight",
                    "rationale",
                ],
                "properties": {
                    "omitted_evidence_id": {"type": "string"},
                    "evidence_id": {"type": "string"},
                    "hypothesis_id": {"type": "string"},
                    "assessment": {"type": "string", "enum": sorted(VALID_ASSESSMENTS)},
                    "weight": {"type": "integer", "minimum": 1, "maximum": 5},
                    "rationale": {"type": "string", "maxLength": 360},
                },
            },
        },
    },
}


def proposer_schema(*, evidence_role_diagnostics: bool = False) -> dict[str, Any]:
    schema = deepcopy(PROPOSER_SCHEMA)
    if evidence_role_diagnostics:
        return schema
    required = [
        item
        for item in schema.get("required", [])
        if item != "evidence_roles"
    ]
    schema["required"] = required
    return schema


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, required=True, help="ACH stress payload JSON.")
    parser.add_argument("--source", type=Path, default=None, help="Optional source.md for local excerpt context.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--model", default=os.environ.get("PRETHINKER_MODEL", "qwen/qwen3.6-35b-a3b"))
    parser.add_argument("--base-url", default=os.environ.get("PRETHINKER_BASE_URL", "https://openrouter.ai/api/v1"))
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--proposal-contract-retries", type=int, default=1)
    parser.add_argument(
        "--evidence-role-diagnostics",
        action="store_true",
        help="Require one structural role classification per evidence row for diagnostic reporting.",
    )
    parser.add_argument("--openrouter-provider-order", default="")
    parser.add_argument("--openrouter-provider-only", default="")
    parser.add_argument("--openrouter-provider-ignore", default="")
    parser.add_argument("--openrouter-quantizations", default="")
    parser.add_argument("--openrouter-allow-fallbacks", choices=["", "true", "false"], default="")
    parser.add_argument("--openrouter-require-parameters", choices=["", "true", "false"], default="")
    parser.add_argument(
        "--counterfactual-sensitivity",
        action="store_true",
        help="Re-propose the ACH matrix once per omitted evidence row and report winner flips.",
    )
    return parser.parse_args()


def main() -> int:
    bootstrap_env_local()
    args = parse_args()
    apply_openrouter_provider_env(
        order=args.openrouter_provider_order,
        only=args.openrouter_provider_only,
        ignore=args.openrouter_provider_ignore,
        quantizations=args.openrouter_quantizations,
        allow_fallbacks=args.openrouter_allow_fallbacks,
        require_parameters=args.openrouter_require_parameters,
    )
    payload_path = _resolve(args.payload)
    payload = json.loads(payload_path.read_text(encoding="utf-8-sig"))
    source_path = _resolve(args.source) if args.source else payload_path.parent / "source.md"
    source_text = source_path.read_text(encoding="utf-8-sig", errors="replace") if source_path.exists() else ""

    baseline = propose_and_score(
        payload=payload,
        source_text=source_text,
        base_url=str(args.base_url),
        model=str(args.model),
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        max_tokens=int(args.max_tokens),
        proposal_contract_retries=int(args.proposal_contract_retries),
        evidence_role_diagnostics=bool(args.evidence_role_diagnostics),
    )
    proposal = baseline["proposal"]
    scorer_payload = baseline["scorer_payload"]
    ach_report = baseline["ach_report"]
    call = baseline["call"]
    counterfactual_sensitivity = []
    if bool(args.counterfactual_sensitivity):
        counterfactual_sensitivity = run_counterfactual_sensitivity(
            payload=payload,
            source_text=source_text,
            baseline_top=_top_hypotheses(ach_report),
            base_url=str(args.base_url),
            model=str(args.model),
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=int(args.max_tokens),
            proposal_contract_retries=int(args.proposal_contract_retries),
            evidence_role_diagnostics=bool(args.evidence_role_diagnostics),
        )
    report = build_report(
        payload=payload,
        payload_path=payload_path,
        source_path=source_path,
        scorer_payload=scorer_payload,
        proposal=proposal,
        ach_report=ach_report,
        call=call,
        model=str(args.model),
        base_url=str(args.base_url),
        counterfactual_sensitivity=counterfactual_sensitivity,
    )

    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(payload.get("fixture_id") or payload_path.parent.name or payload_path.stem))
    out_json = _resolve(args.out_json) if args.out_json else out_dir / f"{slug}_ach_payload_proposal.json"
    out_md = _resolve(args.out_md) if args.out_md else out_dir / f"{slug}_ach_payload_proposal.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def propose_and_score(
    *,
    payload: dict[str, Any],
    source_text: str,
    base_url: str,
    model: str,
    timeout: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
    proposal_contract_retries: int = 0,
    omitted_evidence: dict[str, Any] | None = None,
    evidence_role_diagnostics: bool = False,
) -> dict[str, Any]:
    messages = build_messages(
        payload=payload,
        source_text=source_text,
        omitted_evidence=omitted_evidence,
        evidence_role_diagnostics=evidence_role_diagnostics,
    )
    contract_violations: list[dict[str, Any]] = []
    for attempt in range(max(0, proposal_contract_retries) + 1):
        call = call_json_schema(
            base_url=base_url,
            model=model,
            messages=messages,
            schema=proposer_schema(evidence_role_diagnostics=evidence_role_diagnostics),
            schema_name="ach_judgment_proposal_v1",
            timeout=timeout,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        proposal = json.loads(call["content"])
        contract_violations = proposal_contract_violations(
            payload,
            proposal,
            require_evidence_roles=evidence_role_diagnostics,
        )
        if not contract_violations or attempt >= max(0, proposal_contract_retries):
            break
        messages = [
            *messages,
            {"role": "assistant", "content": call["content"]},
            {
                "role": "user",
                "content": (
                    "Your proposal violated the structured dependency contract. "
                    "When a judgment rationale cites another evidence id, it must include a matching judgment_dependencies row. "
                    "Return a corrected complete JSON proposal with the same schema.\n\n"
                    + json.dumps({"contract_violations": contract_violations}, ensure_ascii=False, indent=2, sort_keys=True)
                ),
            },
        ]
    call["proposal_contract_retry_count"] = attempt
    call["proposal_contract_violations"] = contract_violations
    scorer_payload = build_scorer_payload(payload, proposal)
    ach_report = analyze_ach_overlay(scorer_payload)
    return {"proposal": proposal, "scorer_payload": scorer_payload, "ach_report": ach_report, "call": call}




def run_counterfactual_sensitivity(
    *,
    payload: dict[str, Any],
    source_text: str,
    baseline_top: list[str],
    base_url: str,
    model: str,
    timeout: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
    proposal_contract_retries: int = 0,
    evidence_role_diagnostics: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for evidence_item in payload.get("evidence_rows", []) or []:
        if not isinstance(evidence_item, dict):
            continue
        evidence_id = str(evidence_item.get("id") or "").strip()
        if not evidence_id:
            continue
        reduced_payload = {
            **payload,
            "evidence_rows": [
                item
                for item in payload.get("evidence_rows", []) or []
                if isinstance(item, dict) and str(item.get("id") or "").strip() != evidence_id
            ],
        }
        run = propose_and_score(
            payload=reduced_payload,
            source_text="",
            base_url=base_url,
            model=model,
            timeout=timeout,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            proposal_contract_retries=proposal_contract_retries,
            omitted_evidence=evidence_item,
            evidence_role_diagnostics=evidence_role_diagnostics,
        )
        top = _top_hypotheses(run["ach_report"])
        rows.append(
            {
                "evidence_id": evidence_id,
                "label": str(evidence_item.get("label") or evidence_id),
                "baseline_top": list(baseline_top),
                "top_without_evidence": top,
                "winner_changed": top != baseline_top,
                "matrix_complete": bool(run["ach_report"].get("matrix_complete")),
                "warning_count": len(run["ach_report"].get("warnings", []) or []),
                "judgment_count": int(run["ach_report"].get("judgment_count", 0) or 0),
                "latency_ms": int((run.get("call") or {}).get("latency_ms", 0) or 0),
            }
        )
    return rows


def build_messages(
    *,
    payload: dict[str, Any],
    source_text: str,
    omitted_evidence: dict[str, Any] | None = None,
    evidence_role_diagnostics: bool = False,
) -> list[dict[str, str]]:
    prompt_payload = public_prompt_payload(payload, omitted_evidence=omitted_evidence)
    hypothesis_count = len(prompt_payload.get("hypotheses", []) or [])
    evidence_count = len(prompt_payload.get("evidence_rows", []) or [])
    required_judgment_count = hypothesis_count * evidence_count
    source = str(source_text or "")
    if len(source) > 36000:
        source = source[:36000] + "\n[TRUNCATED]"
    evidence_role_instruction = (
        "For each evidence row, set exactly one evidence_roles item. "
        "Use question_anchor when the row directly states the answer to the ACH question; "
        "occurrence_anchor when it is the concrete finding, event, or outcome that anchors whether the questioned issue occurred; "
        "mechanism_support when it explains how or why; "
        "exclusion_or_counterevidence when it rules in or rules out alternatives; "
        "scope_boundary for limits, timing, status, or jurisdiction; "
        "context for background; remedy_or_consequence for later penalties, fixes, or effects; "
        "other only when none fit. "
        if evidence_role_diagnostics
        else ""
    )
    return [
        {
            "role": "system",
            "content": (
                "/no_think\n"
                "You populate an Analysis of Competing Hypotheses matrix. "
                "Use only the supplied source text, hypotheses, and evidence anchors. "
                "First classify the ACH question_axis. The question axis controls cell weights. "
                "Do not decide by counting supportive rows; mark each evidence row against each hypothesis. "
                "If the question asks for a cause, driver, explanation, or responsibility, give decisive weight only to evidence that bears on that axis. "
                "Evidence about scope, severity, consequence, timing, or background may be true and consistent, but it should be neutral or low weight unless it answers the question axis. "
                "If two hypotheses can both be true, do not let proof of a narrower compatible claim outrank the broader explanatory claim unless the narrower claim contradicts or better answers the question axis. "
                "For each hypothesis, set hypothesis_axis_fit to direct only when the hypothesis directly answers the ACH question; partial when it is true or relevant but mainly qualifies scope, consequence, timing, or background; and off_axis when it does not answer the question. "
                + evidence_role_instruction
                +
                "Assessments must be one of consistent, inconsistent, neutral, or not_applicable. "
                "Use weight 1 for weak evidence and 5 for decisive evidence in each evidence-hypothesis cell. "
                "Diagnosticity describes how much the evidence discriminates among hypotheses. "
                "Use omission_effects only when removing one evidence row changes how another evidence row should be assessed. "
                "For example, if a physical finding or source conclusion reframes an otherwise ambiguous row, omitting the anchor may make the ambiguous row neutral, inconsistent, or supportive of a competing hypothesis. "
                "Also fill judgment_dependencies when a cell judgment depends on another evidence row for its interpretation; leave it empty only when every cell is independent of every other evidence row. "
                "Assess each judgment first from that evidence row's own text_anchor. If you need any fact from another row or from a source conclusion to make the assessment, declare the dependency. "
                "After filling the matrix, audit every evidence row as a possible interpretation anchor: if removing that row would change any other evidence-hypothesis assessment or weight, add the matching judgment_dependencies and omission_effects rows. "
                "This dependency audit is required even when the judgment rationale does not explicitly name the other evidence id. "
                "Do not make a dependent judgment look independent by omitting the other row's id from the rationale. "
                "Do not cite another evidence id in a judgment rationale unless you also add the matching judgment_dependencies row. "
                "Do not add omission effects for ordinary independent rows. "
                "In counterfactual mode, use only the evidence rows listed in the task payload. Do not infer any missing evidence row. "
                "The judgments array must contain exactly one item for every evidence_id and hypothesis_id pair."
            ),
        },
        {
            "role": "user",
            "content": (
                "ACH task payload, with fixture oracle fields intentionally omitted:\n"
                + json.dumps(prompt_payload, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n\nSOURCE TEXT:\n"
                + source
                + f"\n\nRequired matrix size: {evidence_count} evidence rows x {hypothesis_count} hypotheses = {required_judgment_count} judgments. "
                + "Return a complete matrix: every evidence row against every hypothesis. "
                + "Do not stop after the most important evidence row. "
                + "Return judgment_dependencies and omission_effects as empty arrays only when no conditional reassessment is justified by the source."
            ),
        },
    ]


def public_prompt_payload(
    payload: dict[str, Any],
    *,
    omitted_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out = {
        "fixture_id": payload.get("fixture_id", ""),
        "ach_question": payload.get("ach_question", ""),
        "hypotheses": [
            {
                "id": item.get("id", ""),
                "label": item.get("label", ""),
                "claim": item.get("claim", ""),
            }
            for item in payload.get("hypotheses", [])
            if isinstance(item, dict)
        ],
        "evidence_rows": [
            {
                "id": item.get("id", ""),
                "label": item.get("label", ""),
                "source_coords": item.get("source_coords", ""),
                "text_anchor": item.get("text_anchor", ""),
            }
            for item in payload.get("evidence_rows", [])
            if isinstance(item, dict)
        ],
    }
    if isinstance(omitted_evidence, dict):
        out["counterfactual_mode"] = True
        out["counterfactual_instruction"] = "This is a reduced evidence set. Assess only the listed evidence rows."
    return out


def proposal_contract_violations(
    payload: dict[str, Any],
    proposal: dict[str, Any],
    *,
    require_evidence_roles: bool = False,
) -> list[dict[str, Any]]:
    evidence_ids = {
        str(item.get("id") or "").strip()
        for item in payload.get("evidence_rows", []) or []
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }
    role_ids = {
        str(item.get("evidence_id") or "").strip()
        for item in proposal.get("evidence_roles", []) or []
        if isinstance(item, dict) and str(item.get("evidence_id") or "").strip()
    }
    dependency_keys = set()
    for item in proposal.get("judgment_dependencies", []) or []:
        if not isinstance(item, dict):
            continue
        dependency_keys.add(
            (
                str(item.get("evidence_id") or "").strip(),
                str(item.get("hypothesis_id") or "").strip(),
                str(item.get("depends_on_evidence_id") or "").strip(),
            )
        )
    for item in proposal.get("omission_effects", []) or []:
        if not isinstance(item, dict):
            continue
        dependency_keys.add(
            (
                str(item.get("evidence_id") or "").strip(),
                str(item.get("hypothesis_id") or "").strip(),
                str(item.get("omitted_evidence_id") or "").strip(),
            )
        )

    out: list[dict[str, Any]] = []
    if require_evidence_roles:
        for evidence_id in sorted(evidence_ids - role_ids):
            out.append({"kind": "missing_evidence_role", "evidence_id": evidence_id})
    for item in proposal.get("judgments", []) or []:
        if not isinstance(item, dict):
            continue
        evidence_id = str(item.get("evidence_id") or "").strip()
        hypothesis_id = str(item.get("hypothesis_id") or "").strip()
        rationale = str(item.get("rationale") or "")
        for referenced_id in _referenced_evidence_ids(rationale, evidence_ids):
            if referenced_id == evidence_id:
                continue
            if (evidence_id, hypothesis_id, referenced_id) in dependency_keys:
                continue
            out.append(
                {
                    "kind": "missing_judgment_dependency",
                    "evidence_id": evidence_id,
                    "hypothesis_id": hypothesis_id,
                    "referenced_evidence_id": referenced_id,
                }
            )
    return out


def _referenced_evidence_ids(text: str, evidence_ids: set[str]) -> list[str]:
    normalized = "".join(char if char.isalnum() else " " for char in text.casefold())
    tokens = set(normalized.split())
    return sorted(evidence_id for evidence_id in evidence_ids if evidence_id.casefold() in tokens)


def build_scorer_payload(payload: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
    axis_fit_by_id = {
        str(item.get("hypothesis_id") or "").strip(): str(item.get("axis_fit") or "direct").strip().casefold()
        for item in proposal.get("hypothesis_axis_fit", [])
        if isinstance(item, dict)
    }
    diagnosticity_by_id = {
        str(item.get("evidence_id") or "").strip(): str(item.get("diagnosticity") or "medium").strip().casefold()
        for item in proposal.get("evidence_diagnosticity", [])
        if isinstance(item, dict)
    }
    evidence_role_by_id = {
        str(item.get("evidence_id") or "").strip(): str(item.get("role") or "other").strip().casefold()
        for item in proposal.get("evidence_roles", [])
        if isinstance(item, dict)
    }
    evidence = []
    for item in payload.get("evidence_rows", []) or []:
        if not isinstance(item, dict):
            continue
        evidence_id = str(item.get("id") or "").strip()
        diagnosticity = diagnosticity_by_id.get(evidence_id, "medium")
        if diagnosticity not in VALID_DIAGNOSTICITY:
            diagnosticity = "medium"
        evidence_role = evidence_role_by_id.get(evidence_id, "other")
        if evidence_role not in VALID_EVIDENCE_ROLES:
            evidence_role = "other"
        evidence.append(
            {
                "id": evidence_id,
                "label": str(item.get("label") or evidence_id),
                "role": evidence_role,
                "diagnosticity": diagnosticity,
                "source_coords": str(item.get("source_coords") or ""),
                "text_anchor": str(item.get("text_anchor") or ""),
            }
        )
    hypothesis_ids = {str(item.get("id") or "").strip() for item in payload.get("hypotheses", []) if isinstance(item, dict)}
    evidence_ids = {item["id"] for item in evidence}
    judgments = []
    seen: set[tuple[str, str]] = set()
    for item in proposal.get("judgments", []) or []:
        if not isinstance(item, dict):
            continue
        evidence_id = str(item.get("evidence_id") or "").strip()
        hypothesis_id = str(item.get("hypothesis_id") or "").strip()
        key = (evidence_id, hypothesis_id)
        if evidence_id not in evidence_ids or hypothesis_id not in hypothesis_ids or key in seen:
            continue
        assessment = str(item.get("assessment") or "").strip().casefold()
        if assessment not in VALID_ASSESSMENTS:
            continue
        seen.add(key)
        judgments.append(
            {
                "evidence_id": evidence_id,
                "hypothesis_id": hypothesis_id,
                "assessment": assessment,
                "weight": _bounded_weight(item.get("weight"), default=1),
                "rationale": str(item.get("rationale") or "").strip()[:360],
            }
        )
    omission_effects = []
    for item in _combined_omission_effect_items(proposal):
        if not isinstance(item, dict):
            continue
        omitted_evidence_id = str(item.get("omitted_evidence_id") or "").strip()
        evidence_id = str(item.get("evidence_id") or "").strip()
        hypothesis_id = str(item.get("hypothesis_id") or "").strip()
        assessment = str(item.get("assessment") or "").strip().casefold()
        if omitted_evidence_id not in evidence_ids or evidence_id not in evidence_ids or hypothesis_id not in hypothesis_ids:
            continue
        if omitted_evidence_id == evidence_id or assessment not in VALID_ASSESSMENTS:
            continue
        omission_effects.append(
            {
                "omitted_evidence_id": omitted_evidence_id,
                "evidence_id": evidence_id,
                "hypothesis_id": hypothesis_id,
                "assessment": assessment,
                "weight": _bounded_weight(item.get("weight"), default=1),
                "rationale": str(item.get("rationale") or "").strip()[:360],
            }
        )
    return {
        "schema_version": "ach_overlay_payload_v1",
        "hypotheses": [
            {
                "id": str(item.get("id") or ""),
                "label": str(item.get("label") or ""),
                "claim": str(item.get("claim") or ""),
                "axis_fit": (
                    axis_fit_by_id.get(str(item.get("id") or "").strip())
                    if axis_fit_by_id.get(str(item.get("id") or "").strip()) in VALID_HYPOTHESIS_AXIS_FITS
                    else "direct"
                ),
            }
            for item in payload.get("hypotheses", [])
            if isinstance(item, dict)
        ],
        "evidence": evidence,
        "judgments": judgments,
        "omission_effects": omission_effects,
    }


def _combined_omission_effect_items(proposal: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in proposal.get("omission_effects", []) or []:
        if isinstance(item, dict):
            items.append(item)
    for item in proposal.get("judgment_dependencies", []) or []:
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "omitted_evidence_id": item.get("depends_on_evidence_id", ""),
                "evidence_id": item.get("evidence_id", ""),
                "hypothesis_id": item.get("hypothesis_id", ""),
                "assessment": item.get("assessment_without_dependency", ""),
                "weight": item.get("weight_without_dependency", 1),
                "rationale": item.get("rationale", ""),
            }
        )
    return items


def build_report(
    *,
    payload: dict[str, Any],
    payload_path: Path,
    source_path: Path,
    scorer_payload: dict[str, Any],
    proposal: dict[str, Any],
    ach_report: dict[str, Any],
    call: dict[str, Any],
    model: str,
    base_url: str,
    counterfactual_sensitivity: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    top = _top_hypotheses(ach_report)
    expected = payload.get("expected_read") if isinstance(payload.get("expected_read"), dict) else {}
    expected_best = str(expected.get("best_hypothesis") or "").strip()
    sensitivity = ach_report.get("sensitivity", []) if isinstance(ach_report.get("sensitivity"), list) else []
    pivotal = str(expected.get("pivotal_evidence") or "").strip()
    counterfactual_rows = counterfactual_sensitivity or []
    counterfactual_flips = [row for row in counterfactual_rows if isinstance(row, dict) and row.get("winner_changed")]
    support_contributions = (
        ach_report.get("top_support_contributions", [])
        if isinstance(ach_report.get("top_support_contributions"), list)
        else []
    )
    evidence_roles = {
        str(item.get("id") or ""): str(item.get("role") or "other")
        for item in scorer_payload.get("evidence", []) or []
        if isinstance(item, dict)
    }
    evidence_role_counts: dict[str, int] = {}
    for role in evidence_roles.values():
        evidence_role_counts[role] = evidence_role_counts.get(role, 0) + 1
    return {
        "schema_version": "ach_payload_proposal_run_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "payload_path": _display_path(payload_path),
        "source_path": _display_path(source_path),
        "policy": [
            "The LLM proposes ACH judgments only; it does not write KB facts or mutate QA verdicts.",
            "The prompt omits expected_read and expected_relevance fields to avoid oracle leakage.",
            "The deterministic scorer ranks hypotheses by least disconfirmation and computes single-row sensitivity.",
        ],
        "model_serving_path": {
            "provider_family": provider_family(backend="lmstudio", base_url=base_url),
            "model": model,
            "base_url": base_url,
            "provider_routing": openrouter_provider_routing_from_env() if is_openrouter_base_url(base_url) else {},
        },
        "openrouter_generation_metadata": call.get("openrouter_generation_metadata", {}),
        "proposal_contract_violations": call.get("proposal_contract_violations", []),
        "summary": {
            "fixture_id": str(payload.get("fixture_id") or ""),
            "question_axis": str(proposal.get("question_axis") or ""),
            "matrix_complete": bool(ach_report.get("matrix_complete")),
            "warning_count": len(ach_report.get("warnings", []) or []),
            "hypothesis_count": int(ach_report.get("hypothesis_count", 0) or 0),
            "evidence_count": int(ach_report.get("evidence_count", 0) or 0),
            "judgment_count": int(ach_report.get("judgment_count", 0) or 0),
            "top_hypotheses": top,
            "expected_best_hypothesis": expected_best,
            "best_matches_expected": bool(expected_best and top == [expected_best]),
            "sensitivity_count": len(sensitivity),
            "sensitivity_evidence_ids": [str(item.get("evidence_id") or "") for item in sensitivity if isinstance(item, dict)],
            "omission_effect_count": len(scorer_payload.get("omission_effects", []) or []),
            "proposal_contract_retry_count": int(call.get("proposal_contract_retry_count", 0) or 0),
            "proposal_contract_violation_count": len(call.get("proposal_contract_violations", []) or []),
            "counterfactual_sensitivity_count": len(counterfactual_flips),
            "counterfactual_sensitivity_evidence_ids": [
                str(item.get("evidence_id") or "") for item in counterfactual_flips
            ],
            "top_support_evidence_ids": [
                str(item.get("evidence_id") or "")
                for item in support_contributions
                if isinstance(item, dict) and int(item.get("support_weight", 0) or 0) > 0
            ][:5],
            "evidence_role_counts": dict(sorted(evidence_role_counts.items())),
            "expected_sensitivity": str(expected.get("sensitivity_expectation") or ""),
            "expected_pivotal_evidence": pivotal,
            "expected_pivotal_evidence_role": evidence_roles.get(pivotal, ""),
            "pivotal_found_in_sensitivity": bool(
                pivotal
                and (
                    any(item.get("evidence_id") == pivotal for item in sensitivity if isinstance(item, dict))
                    or any(item.get("evidence_id") == pivotal for item in counterfactual_flips if isinstance(item, dict))
                )
            ),
            "latency_ms": int(call.get("latency_ms", 0) or 0),
        },
        "scorer_payload": scorer_payload,
        "proposal": proposal,
        "ach_report": ach_report,
        "counterfactual_sensitivity": counterfactual_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# ACH Payload Proposal Run",
        "",
        f"Generated: `{report.get('generated_at', '')}`",
        f"Payload: `{report.get('payload_path', '')}`",
        f"Source: `{report.get('source_path', '')}`",
        "",
        "## Summary",
        "",
        f"- Fixture: `{summary.get('fixture_id', '')}`",
        f"- Question axis: `{summary.get('question_axis', '')}`",
        f"- Matrix complete: `{summary.get('matrix_complete', False)}`",
        f"- Hypotheses / evidence / judgments: `{summary.get('hypothesis_count', 0)} / {summary.get('evidence_count', 0)} / {summary.get('judgment_count', 0)}`",
        f"- Warnings: `{summary.get('warning_count', 0)}`",
        f"- Top hypotheses: `{summary.get('top_hypotheses', [])}`",
        f"- Expected best: `{summary.get('expected_best_hypothesis', '')}`",
        f"- Best matches expected: `{summary.get('best_matches_expected', False)}`",
        f"- Sensitivity rows: `{summary.get('sensitivity_count', 0)}`",
        f"- Sensitivity evidence ids: `{summary.get('sensitivity_evidence_ids', [])}`",
        f"- Omission effects: `{summary.get('omission_effect_count', 0)}`",
        f"- Proposal contract retries: `{summary.get('proposal_contract_retry_count', 0)}`",
        f"- Proposal contract violations: `{summary.get('proposal_contract_violation_count', 0)}`",
        f"- Counterfactual sensitivity rows: `{summary.get('counterfactual_sensitivity_count', 0)}`",
        f"- Counterfactual sensitivity evidence ids: `{summary.get('counterfactual_sensitivity_evidence_ids', [])}`",
        f"- Top support evidence ids: `{summary.get('top_support_evidence_ids', [])}`",
        f"- Evidence role counts: `{summary.get('evidence_role_counts', {})}`",
        f"- Expected sensitivity: `{summary.get('expected_sensitivity', '')}`",
        f"- Expected pivotal evidence: `{summary.get('expected_pivotal_evidence', '')}`",
        f"- Expected pivotal evidence role: `{summary.get('expected_pivotal_evidence_role', '')}`",
        f"- Pivotal found in sensitivity: `{summary.get('pivotal_found_in_sensitivity', False)}`",
        "",
        "## Hypothesis Scores",
        "",
        "| Rank | Hypothesis | Inconsistency | Consistency | Missing |",
        "| ---: | --- | ---: | ---: | ---: |",
    ]
    ach_report = report.get("ach_report", {}) if isinstance(report.get("ach_report"), dict) else {}
    for row in ach_report.get("hypothesis_scores", []) or []:
        if not isinstance(row, dict):
            continue
        label = str(row.get("label", row.get("hypothesis_id", ""))).replace("|", "/")
        lines.append(
            f"| {row.get('rank', '')} | `{row.get('hypothesis_id', '')}` {label} | "
            f"{row.get('inconsistency_weight', 0)} | {row.get('consistency_weight', 0)} | "
            f"{row.get('missing_judgment_count', 0)} |"
        )
    sensitivity = ach_report.get("sensitivity", []) if isinstance(ach_report.get("sensitivity"), list) else []
    if sensitivity:
        lines.extend(["", "## Sensitivity", "", "| Evidence | Baseline Top | Top Without Evidence |", "| --- | --- | --- |"])
        for row in sensitivity:
            if not isinstance(row, dict):
                continue
            label = str(row.get("label", row.get("evidence_id", ""))).replace("|", "/")
            lines.append(
                f"| `{row.get('evidence_id', '')}` {label} | `{row.get('baseline_top', [])}` | "
                f"`{row.get('top_without_evidence', [])}` |"
            )
    counterfactual_rows = report.get("counterfactual_sensitivity", [])
    if isinstance(counterfactual_rows, list) and counterfactual_rows:
        lines.extend(
            [
                "",
                "## Counterfactual Sensitivity",
                "",
                "| Evidence | Changed | Baseline Top | Top Without Evidence |",
                "| --- | ---: | --- | --- |",
            ]
        )
        for row in counterfactual_rows:
            if not isinstance(row, dict):
                continue
            label = str(row.get("label", row.get("evidence_id", ""))).replace("|", "/")
            lines.append(
                f"| `{row.get('evidence_id', '')}` {label} | `{row.get('winner_changed', False)}` | "
                f"`{row.get('baseline_top', [])}` | `{row.get('top_without_evidence', [])}` |"
            )
    lines.append("")
    return "\n".join(lines)


def _top_hypotheses(ach_report: dict[str, Any]) -> list[str]:
    return [
        str(item.get("hypothesis_id") or "")
        for item in ach_report.get("hypothesis_scores", []) or []
        if isinstance(item, dict) and item.get("rank") == 1
    ]


def call_json_schema(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    schema: dict[str, Any],
    schema_name: str,
    timeout: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "think": False,
        "thinking": False,
        "reasoning": {"effort": "none", "exclude": True},
        "include_reasoning": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
    }
    if is_openrouter_base_url(base_url):
        provider_routing = openrouter_provider_routing_from_env()
        if provider_routing:
            payload["provider"] = provider_routing
    started = time.perf_counter()
    request = urllib.request.Request(
        _chat_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers=_headers(base_url),
        method="POST",
    )
    raw: dict[str, Any] = {}
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(request, timeout=int(timeout)) as response:
                raw = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if int(exc.code) != 429 or attempt >= 4:
                raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
            time.sleep(_retry_after_seconds(exc, body, default=attempt))
    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    if not content:
        content = str(message.get("reasoning_content", "") if isinstance(message, dict) else "").strip()
    if not content:
        raise RuntimeError("model returned empty ACH proposal content")
    metadata = openrouter_generation_metadata(
        raw_response=raw,
        request_payload=payload,
        base_url=base_url,
        timeout=min(int(timeout), 30),
        call_role=schema_name,
    )
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "content": content,
        "raw": raw,
        "openrouter_generation_metadata": metadata,
    }


def _retry_after_seconds(exc: urllib.error.HTTPError, body: str, *, default: int) -> float:
    header = str(exc.headers.get("Retry-After", "") if exc.headers else "").strip()
    try:
        return max(1.0, float(header))
    except ValueError:
        pass
    try:
        payload = json.loads(body)
        error = payload.get("error") if isinstance(payload, dict) else {}
        retry_after = error.get("metadata", {}).get("retry_after_seconds") if isinstance(error, dict) else None
        return max(1.0, float(retry_after))
    except Exception:
        return float(max(1, default))


def _headers(base_url: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if is_openrouter_base_url(base_url):
        key = openrouter_api_key()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        headers.update(openrouter_metadata_headers(base_url))
        headers["HTTP-Referer"] = "https://github.com/dr3d/prethinker"
        headers["X-Title"] = "ach-payload-proposer"
        headers["X-OpenRouter-Title"] = "ach-payload-proposer"
    else:
        key = str(os.environ.get("PRETHINKER_API_KEY") or "").strip()
        if key:
            headers["Authorization"] = f"Bearer {key}"
    return headers


def _chat_url(base_url: str) -> str:
    base = str(base_url or "").rstrip("/")
    return f"{base}/chat/completions" if base.endswith("/v1") else f"{base}/v1/chat/completions"


def _bounded_weight(value: Any, *, default: int) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError):
        out = int(default)
    return max(1, min(5, out))


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return ""
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


def _slug(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or ""))
    out = "-".join(part for part in out.split("-") if part)
    return out or "ach-payload-proposal"


if __name__ == "__main__":
    raise SystemExit(main())
