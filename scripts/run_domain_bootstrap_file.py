#!/usr/bin/env python3
"""Bootstrap a draft domain profile from one raw text file.

This runner is intentionally small and literal: Python reads the file and hands
the raw text to the LLM profile-bootstrap pass. It does not derive predicates,
split the text semantically, rewrite phrases, or inspect the language. The model
proposes the candidate predicate surface; deterministic code only validates,
scores, and optionally uses that draft surface in the ordinary Semantic IR path.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_file"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

NARRATIVE_SOURCE_COMPILER_CONTEXT_V1 = [
    "narrative_source_compiler_strategy_v1: Use this only for sources classified by the LLM intake plan or domain hint as story, narrative, fable, fiction, plot, or source-fidelity story-world material.",
    "Narrative source rule: compile the closed world of this source text. Do not import facts, character names, motives, objects, or endings from famous stories, genre priors, or likely variants.",
    "Narrative source rule: preserve source-local names and aliases. If the text says Little Slip of an Otter, Great Long Otter, or Tilly Tumbletop, do not normalize them to unrelated familiar names.",
    "Narrative source rule: build a story spine when the profile supports it. Prefer event records with actor, action/type, target/object, place, source span/phase, and story order over isolated verb facts.",
    "Narrative source rule: separate static state, event occurrence, character speech, narrator judgment, causal consequence, and final state. These are different epistemic jobs even when they share entities.",
    "Narrative source rule: subjective fit or quality language such as too hot, too cold, just right, too hard, too soft, or too high should be tied to an evaluator or narrator context when the profile supports it.",
    "Narrative source rule: quoted speech is a speech act by a character unless the source independently states the spoken content as narrator fact.",
    "Narrative source rule: when an event changes state, preserve both the event and the resulting state if the profile supports it. If a later repair changes the final state, preserve final-state or remediation outcome rather than leaving only the broken intermediate state.",
    "Narrative source rule: preserve errand, intention, forgetfulness, discovery, consequence, repair, and final emotional/condition states as queryable structure when stated by the source.",
    "Narrative story-world canonical palette preference: when the draft profile offers equivalent choices, prefer event/5 for event_id, actor, action, object, place; story_time/2 for event order; before/2 and after/2 for temporal ordering; causes/2 and caused_by/2 for consequence links.",
    "Narrative story-world canonical palette preference: prefer said/3 for event-scoped quoted speech or source-stated speech acts; prefer judged/4 for evaluator, item, dimension, judgment; prefer owned_by/2 for item-to-owner ownership; prefer designed_for/2 for items made for a character.",
    "Narrative story-world canonical palette preference: prefer initial_location/2 and location_after_event/3 when the source gives object locations or movement; prefer final_state/1 and condition_after_story/2 for repaired, remaining, or resolved end-state facts.",
    "Narrative story-world canonical palette preference: prefer household/1, household_member/2, character/1, object/1, place/1, food/1, name/2, kind/2, and property/2 for source-local cast and object taxonomy when the profile supports these classes.",
    "Narrative story-world canonical palette warning: do not invent near-synonym predicate surfaces such as happens_before/2, says/3, evaluates_as/3, located_at/2, owns/2, or results_in/2 when the draft profile also provides the canonical story-world predicates before/2, said/3, judged/4, initial_location/2, owned_by/2, or causes/2.",
    "Narrative story-world coverage warning: canonical predicates should not make the compile timid. Preserve representative facts for cast/entity taxonomy, ownership/design, locations, event spine, story order, speech, subjective judgment, causality, remediation, and final state when the source and profile support them.",
    "Narrative source rule: if the profile lacks event, temporal-order, causal, or final-state predicates needed for the current pass, mention those missing capabilities in self_check rather than inventing out-of-palette predicates.",
]

POLICY_INCIDENT_SOURCE_COMPILER_CONTEXT_V1 = [
    "policy_incident_source_compiler_strategy_v1: Use this for sources classified by the LLM intake plan or domain hint as policy, compliance, incident, operations log, regulatory record, timeline, or municipal/organizational procedure.",
    "Policy incident rule: separate standing rules from observed incident facts. A threshold, deadline, required role, exception, or validity condition is not the same kind of state as a timestamped reading, notification, outage, authorization, correction, or review statement.",
    "Policy incident rule: when the profile offers exact predicates for measurements, thresholds, intervals, state changes, notifications, authorizations, inspections, corrections, and temporal ordering, prefer those exact predicates over generic event/status wrappers.",
    "Policy incident rule: preserve scoped applicability and exclusions. If the source distinguishes residential zones, industrial zones, downstream zones, affected zones, or excluded zones, compile those classifications and scope relations before deriving any compliance conclusion.",
    "Policy incident rule: preserve timestamps as queryable values on the relevant event or observation predicates. Do not hide deadlines or times inside long normalized labels when the profile provides date/time slots.",
    "Policy incident rule: preserve corrections as authoritative corrected facts plus parked claims or self_check notes for superseded values when the profile supports that distinction. Do not commit both old and corrected values as equal truth.",
    "Policy incident rule: preserve joint authorization and prerequisite validity as structured policy requirements and timestamped authorization/inspection facts when the profile supports them.",
    "Policy incident rule: preserve notification recipients, notice type, time, method, and notifying actor separately when the profile supports those slots.",
    "Policy incident rule: preserve review-board statements, witness statements, disclosures, and allegations as claims or review records unless the source states an authoritative finding.",
    "Policy incident coverage warning: a useful skeleton should include roles, scoped zones/entities, core facilities/systems, standing policy thresholds/deadlines, key measurements, advisory or trigger state, facility status changes, notifications, authorizations, inspections, corrections, and temporal order when the source and profile support them.",
    "Policy incident canonical palette warning: do not invent vague substitutes such as event_occurred/4, policy_constraint/3, or compliance_status/3 when the draft profile provides a more precise predicate for the same job.",
]

from src.profile_bootstrap import (  # noqa: E402
    PROFILE_BOOTSTRAP_JSON_SCHEMA,
    PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA,
    build_profile_bootstrap_messages,
    build_profile_bootstrap_review_messages,
    parse_profile_bootstrap_json,
    parse_profile_bootstrap_review_json,
    profile_bootstrap_allowed_predicates,
    profile_bootstrap_domain_context,
    profile_bootstrap_predicate_contracts,
    profile_bootstrap_score,
)
from src.document_intake_plan import (  # noqa: E402
    INTAKE_PLAN_JSON_SCHEMA,
    build_intake_plan_messages,
    intake_plan_context,
    parse_intake_plan_json,
)
from src.semantic_ir import (  # noqa: E402
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLM-owned profile bootstrap over a raw text file.")
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument(
        "--expected-prolog",
        type=Path,
        default=None,
        help="Optional expected Prolog file used for structural signature comparison only.",
    )
    parser.add_argument(
        "--use-expected-signatures-as-guidance",
        action="store_true",
        help="Calibration-only mode: include expected Prolog predicate signatures in the LLM profile-bootstrap input.",
    )
    parser.add_argument(
        "--profile-registry",
        type=Path,
        default=None,
        help="Optional source/domain ontology registry used as candidate profile vocabulary, not target facts.",
    )
    parser.add_argument(
        "--use-profile-registry-direct",
        action="store_true",
        help="Use --profile-registry directly as the draft profile palette instead of asking the LLM to rediscover it.",
    )
    parser.add_argument("--domain-hint", default="")
    parser.add_argument("--backend", choices=["lmstudio"], default="lmstudio")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=32768)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument(
        "--skip-intake-plan",
        action="store_true",
        help="Disable the LLM-owned intake_plan_v1 pre-pass.",
    )
    parser.add_argument(
        "--compile-source",
        action="store_true",
        help="After profile bootstrap, run the same raw source through Semantic IR using the draft profile.",
    )
    parser.add_argument(
        "--compile-plan-passes",
        action="store_true",
        help="When an intake plan exists, compile once per LLM-authored pass_plan item instead of one flat source compile.",
    )
    parser.add_argument("--max-plan-passes", type=int, default=8)
    parser.add_argument("--include-model-input", action="store_true")
    parser.add_argument(
        "--review-profile",
        action="store_true",
        help="Run an LLM-owned profile review pass before optional source compilation.",
    )
    parser.add_argument(
        "--profile-review-retry",
        action="store_true",
        help="If profile review recommends retry, rerun profile bootstrap with review guidance.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text_path = args.text_file if args.text_file.is_absolute() else (REPO_ROOT / args.text_file).resolve()
    source_text = text_path.read_text(encoding="utf-8-sig")
    expected_path = None
    expected_signatures: list[str] = []
    if args.expected_prolog:
        expected_path = args.expected_prolog if args.expected_prolog.is_absolute() else (REPO_ROOT / args.expected_prolog).resolve()
        if args.use_expected_signatures_as_guidance:
            expected_signatures = sorted(_prolog_signatures(expected_path.read_text(encoding="utf-8-sig")))
    sample = {
        "id": text_path.stem,
        "source": str(text_path),
        "domain_hint": str(args.domain_hint or "").strip(),
        "text": source_text,
        "context": [
            "Raw source file. Python has not segmented, summarized, or derived predicates from this text.",
            "The LLM bootstrap pass must propose the candidate predicate/entity surface.",
        ],
    }
    profile_registry = _load_profile_registry(args.profile_registry)
    if profile_registry:
        sample["candidate_profile_registry_v1"] = profile_registry
        sample["context"].append(
            "candidate_profile_registry_v1 is a source/domain ontology scaffold: predicate signatures, categories, "
            "and notes only. It is not a gold fact set and it does not authorize writes. Prefer these signatures when "
            "they fit the source and preserve epistemic boundaries; omit registry predicates that the source does not need."
        )
    if expected_signatures:
        sample["target_prolog_signatures_for_calibration"] = expected_signatures
        sample["context"].append(
            "Calibration-only: target_prolog_signatures_for_calibration is a human-supplied expected predicate roster. "
            "Prefer matching those signatures when they fit the source and profile design."
        )
    intake_plan: dict[str, Any] | None = None
    intake_error = ""
    intake_latency_ms = 0
    if not args.skip_intake_plan:
        intake_started = time.perf_counter()
        intake_response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=build_intake_plan_messages(
                source_text=source_text,
                source_name=text_path.name,
                domain_hint=str(args.domain_hint or ""),
            ),
            schema=INTAKE_PLAN_JSON_SCHEMA,
            schema_name="intake_plan_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), 12000),
        )
        intake_latency_ms = int((time.perf_counter() - intake_started) * 1000)
        intake_plan, intake_error = parse_intake_plan_json(str(intake_response.get("content", "")))
        if isinstance(intake_plan, dict):
            sample["intake_plan_v1"] = intake_plan
            sample["context"].append(
                "The intake_plan_v1 object is an LLM-owned document-to-logic strategy. Use it as planning guidance, not as approved facts."
            )
    started = time.perf_counter()
    messages: list[dict[str, str]] = []
    if bool(args.use_profile_registry_direct):
        if not profile_registry:
            raise ValueError("--use-profile-registry-direct requires --profile-registry")
        parsed = _profile_from_registry(profile_registry, domain_hint=str(args.domain_hint or ""))
        error = ""
        response = {"content": json.dumps(parsed, ensure_ascii=False)}
    else:
        messages = build_profile_bootstrap_messages(samples=[sample], domain_hint=str(args.domain_hint or ""))
        response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=messages,
            schema=PROFILE_BOOTSTRAP_JSON_SCHEMA,
            schema_name="profile_bootstrap_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=int(args.max_tokens),
        )
        parsed, error = parse_profile_bootstrap_json(str(response.get("content", "")))
    profile_retry: dict[str, Any] | None = None
    if not isinstance(parsed, dict):
        retry_sample = dict(sample)
        retry_context = list(sample.get("context", [])) if isinstance(sample.get("context"), list) else []
        retry_context.append(
            "Retry after invalid/truncated profile JSON: emit a compact profile with at most 80 unique predicate signatures. "
            "Do not duplicate synonymous predicate surfaces; choose one canonical predicate for each role."
        )
        retry_sample["context"] = retry_context
        retry_messages = build_profile_bootstrap_messages(samples=[retry_sample], domain_hint=str(args.domain_hint or ""))
        retry_started = time.perf_counter()
        retry_response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=retry_messages,
            schema=PROFILE_BOOTSTRAP_JSON_SCHEMA,
            schema_name="profile_bootstrap_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), 18000),
        )
        retry_parsed, retry_error = parse_profile_bootstrap_json(str(retry_response.get("content", "")))
        profile_retry = {
            "latency_ms": int((time.perf_counter() - retry_started) * 1000),
            "parsed_ok": isinstance(retry_parsed, dict),
            "parse_error": retry_error,
            "raw_content": str(retry_response.get("content", ""))[:20000],
        }
        if isinstance(retry_parsed, dict):
            parsed = retry_parsed
            error = retry_error
    profile_review: dict[str, Any] | None = None
    profile_review_retry: dict[str, Any] | None = None
    if bool(args.review_profile) and isinstance(parsed, dict) and not bool(args.use_profile_registry_direct):
        profile_review = _review_profile_bootstrap(
            source_text=source_text,
            source_name=text_path.name,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
        )
        review_parsed = profile_review.get("parsed") if isinstance(profile_review.get("parsed"), dict) else {}
        should_retry = (
            bool(args.profile_review_retry)
            and isinstance(review_parsed, dict)
            and (
                review_parsed.get("coverage_ok") is False
                or str(review_parsed.get("verdict", "")).strip() in {"retry_recommended", "reject_profile"}
            )
        )
        if should_retry:
            retry_sample = dict(sample)
            retry_context = list(sample.get("context", [])) if isinstance(sample.get("context"), list) else []
            retry_context.append(
                "Profile review pass recommended one more profile-bootstrap attempt. "
                "This is LLM control-plane guidance, not approved facts or a target Prolog file."
            )
            retry_context.append(
                "Profile review retry safety: preserve source-local vocabulary. If review guidance uses a famous story, "
                "archetype, trope, or template label that is not literally present in the source, translate it into a "
                "source-local structural name before proposing profile predicates or repeated structures. Do not repeat "
                "the absent external label in risks, examples, explanations, or retry-derived notes."
            )
            for item in review_parsed.get("retry_guidance", []) if isinstance(review_parsed.get("retry_guidance"), list) else []:
                text = str(item).strip()
                if text:
                    retry_context.append(f"profile_review_retry_guidance: {text}")
            for item in review_parsed.get("missing_capabilities", []) if isinstance(review_parsed.get("missing_capabilities"), list) else []:
                if not isinstance(item, dict):
                    continue
                capability = str(item.get("capability", "")).strip()
                suggested = ", ".join(str(sig).strip() for sig in item.get("suggested_signatures", []) if str(sig).strip()) if isinstance(item.get("suggested_signatures"), list) else ""
                if capability or suggested:
                    retry_context.append(f"profile_review_missing_capability: {capability}; suggested_signatures: {suggested}")
            retry_sample["context"] = retry_context
            retry_messages = build_profile_bootstrap_messages(samples=[retry_sample], domain_hint=str(args.domain_hint or ""))
            retry_started = time.perf_counter()
            retry_response = _call_lmstudio_json_schema(
                base_url=str(args.base_url),
                model=str(args.model),
                messages=retry_messages,
                schema=PROFILE_BOOTSTRAP_JSON_SCHEMA,
                schema_name="profile_bootstrap_v1",
                timeout=int(args.timeout),
                temperature=float(args.temperature),
                top_p=float(args.top_p),
                max_tokens=int(args.max_tokens),
            )
            retry_parsed, retry_error = parse_profile_bootstrap_json(str(retry_response.get("content", "")))
            profile_review_retry = {
                "latency_ms": int((time.perf_counter() - retry_started) * 1000),
                "parsed_ok": isinstance(retry_parsed, dict),
                "parse_error": retry_error,
                "raw_content": str(retry_response.get("content", ""))[:20000],
            }
            if isinstance(retry_parsed, dict):
                parsed = retry_parsed
                error = retry_error
    score = profile_bootstrap_score(parsed)
    record: dict[str, Any] = {
        "ts": _utc_now(),
        "text_file": str(text_path),
        "domain_hint": str(args.domain_hint or ""),
        "backend": str(args.backend),
        "model": str(args.model),
        "profile_registry": str(args.profile_registry or ""),
        "profile_registry_direct": bool(args.use_profile_registry_direct),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parsed_ok": isinstance(parsed, dict),
        "parse_error": error,
        "score": score,
        "parsed": parsed or {},
        "raw_content": str(response.get("content", ""))[:20000],
    }
    if profile_retry is not None:
        record["profile_retry"] = profile_retry
    if profile_review is not None:
        record["profile_review"] = profile_review
    if profile_review_retry is not None:
        record["profile_review_retry"] = profile_review_retry
    if not args.skip_intake_plan:
        record["intake_plan"] = {
            "parsed_ok": isinstance(intake_plan, dict),
            "parse_error": intake_error,
            "latency_ms": intake_latency_ms,
            "parsed": intake_plan or {},
        }
    if args.include_model_input:
        record["model_input"] = {"messages": messages}
    if bool(args.compile_source) and isinstance(parsed, dict) and bool(args.compile_plan_passes) and isinstance(intake_plan, dict):
        record["source_compile"] = _compile_source_with_plan_passes(
            source_text=source_text,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
        )
    elif bool(args.compile_source) and isinstance(parsed, dict):
        record["source_compile"] = _compile_source_with_draft_profile(
            source_text=source_text,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
        )
    if args.expected_prolog:
        record["expected_prolog"] = _compare_expected_prolog(
            expected_path=expected_path or (REPO_ROOT / args.expected_prolog).resolve(),
            parsed_profile=parsed if isinstance(parsed, dict) else {},
            source_compile=record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {},
        )

    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(text_path.stem)}_{_slug(str(args.model))}"
    json_path = out_dir / f"domain_bootstrap_file_{slug}.json"
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(record, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(
        json.dumps(
            {
                "parsed_ok": record["parsed_ok"],
                "score": score,
                "candidate_predicates": score.get("predicate_count", 0),
                "compile_admitted": (record.get("source_compile") or {}).get("admitted_count"),
                "compile_skipped": (record.get("source_compile") or {}).get("skipped_count"),
                "expected_signature_recall": (record.get("expected_prolog") or {}).get("signature_recall"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _review_profile_bootstrap(
    *,
    source_text: str,
    source_name: str,
    parsed_profile: dict[str, Any],
    intake_plan: dict[str, Any] | None,
    args: argparse.Namespace,
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=build_profile_bootstrap_review_messages(
                source_text=source_text,
                source_name=source_name,
                domain_hint=str(args.domain_hint or ""),
                intake_plan=intake_plan,
                proposed_profile=parsed_profile,
            ),
            schema=PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA,
            schema_name="profile_bootstrap_review_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), 6000),
        )
    except Exception as exc:
        return {
            "parsed_ok": False,
            "parse_error": str(exc),
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "parsed": {},
        }
    parsed, error = parse_profile_bootstrap_review_json(str(response.get("content", "")))
    return {
        "parsed_ok": isinstance(parsed, dict),
        "parse_error": error,
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parsed": parsed or {},
        "raw_content": str(response.get("content", ""))[:12000],
    }


def _load_profile_registry(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    registry_path = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    parsed = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    if not isinstance(parsed, dict):
        return {}
    predicates = parsed.get("predicates", [])
    compact_predicates: list[dict[str, str]] = []
    if isinstance(predicates, list):
        for item in predicates:
            if not isinstance(item, dict):
                continue
            signature = str(item.get("signature", "")).strip()
            if not signature:
                continue
            compact_predicates.append(
                {
                    "signature": signature,
                    "args": [
                        str(arg).strip()
                        for arg in item.get("args", [])
                        if isinstance(item.get("args"), list) and str(arg).strip()
                    ],
                    "category": str(item.get("category", "")).strip(),
                    "notes": str(item.get("notes", "")).strip(),
                }
            )
    return {
        "schema": str(parsed.get("schema", "")).strip(),
        "fixture": str(parsed.get("fixture", "")).strip(),
        "source": str(parsed.get("source", "")).strip(),
        "purpose": str(parsed.get("purpose", "")).strip(),
        "predicates": compact_predicates,
    }


def _profile_from_registry(registry: dict[str, Any], *, domain_hint: str = "") -> dict[str, Any]:
    predicates: list[dict[str, Any]] = []
    for item in registry.get("predicates", []) if isinstance(registry.get("predicates"), list) else []:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature", "")).strip()
        match = re.match(r"^[a-z][a-zA-Z0-9_]*\/(\d+)$", signature)
        if not signature or not match:
            continue
        arity = int(match.group(1))
        args = [
            str(arg).strip()
            for arg in item.get("args", [])
            if isinstance(item.get("args"), list) and str(arg).strip()
        ]
        if len(args) != arity:
            args = [f"arg_{index}" for index in range(1, arity + 1)]
        predicates.append(
            {
                "signature": signature,
                "args": args,
                "description": str(item.get("notes", "")).strip() or str(item.get("category", "")).strip(),
                "why": f"registry_category={str(item.get('category', '')).strip()}",
                "admission_notes": [
                    "Registry-provided predicate candidate. Direct source support and mapper admission are still required."
                ],
            }
        )
    return {
        "schema_version": "profile_bootstrap_v1",
        "domain_guess": str(domain_hint or registry.get("fixture") or "registry_profile").strip(),
        "domain_scope": str(registry.get("purpose", "")).strip(),
        "confidence": 1.0,
        "source_summary": [
            "Profile generated directly from candidate_profile_registry_v1. The registry supplies predicate vocabulary only, not facts."
        ],
        "entity_types": [
            {"name": "entity", "description": "Registry-backed story-world entity.", "examples": []}
        ],
        "candidate_predicates": predicates,
        "repeated_structures": [],
        "likely_functional_predicates": [],
        "provenance_sensitive_predicates": [],
        "admission_risks": [
            "Registry predicates still require direct source support.",
            "A broad registry can permit semantically weak writes if the compiler is not source-faithful.",
        ],
        "clarification_policy": [],
        "unsafe_transformations": [
            "Do not treat registry examples, categories, or notes as source facts."
        ],
        "starter_frontier_cases": [],
        "self_check": {
            "profile_authority": "proposal_only",
            "notes": ["direct_registry_profile"],
        },
    }


def _compare_expected_prolog(
    *,
    expected_path: Path,
    parsed_profile: dict[str, Any],
    source_compile: dict[str, Any],
) -> dict[str, Any]:
    expected_text = expected_path.read_text(encoding="utf-8-sig")
    expected_signatures = _prolog_signatures(expected_text)
    profile_signatures = {
        str(item.get("signature", "")).strip().casefold()
        for item in parsed_profile.get("candidate_predicates", [])
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    emitted_text = "\n".join(
        [
            *[str(item) for item in source_compile.get("facts", []) if str(item).strip()],
            *[str(item) for item in source_compile.get("rules", []) if str(item).strip()],
        ]
    )
    emitted_signatures = _prolog_signatures(emitted_text)
    profile_overlap = sorted(expected_signatures & profile_signatures)
    overlap = sorted(expected_signatures & emitted_signatures)
    profile_missing = sorted(expected_signatures - profile_signatures)
    missing = sorted(expected_signatures - emitted_signatures)
    extra = sorted(emitted_signatures - expected_signatures)
    return {
        "expected_path": str(expected_path),
        "expected_signature_count": len(expected_signatures),
        "profile_signature_count": len(profile_signatures),
        "profile_overlap_signature_count": len(profile_overlap),
        "profile_signature_recall": round(len(profile_overlap) / max(1, len(expected_signatures)), 3),
        "emitted_signature_count": len(emitted_signatures),
        "overlap_signature_count": len(overlap),
        "signature_recall": round(len(overlap) / max(1, len(expected_signatures)), 3),
        "signature_precision": round(len(overlap) / max(1, len(emitted_signatures)), 3),
        "profile_overlap_signatures": profile_overlap,
        "profile_missing_signatures": profile_missing[:80],
        "overlap_signatures": overlap,
        "missing_signatures": missing[:80],
        "extra_signatures": extra[:80],
    }


def _prolog_signatures(text: str) -> set[str]:
    signatures: set[str] = set()
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%") or line.startswith(":-"):
            continue
        head = line.split(":-", 1)[0].strip()
        match = re.match(r"^([a-z][a-zA-Z0-9_]*)\s*\((.*)\)", head)
        if not match:
            continue
        signatures.add(f"{match.group(1).casefold()}/{_prolog_arity(match.group(2))}")
    return signatures


def _prolog_arity(args_text: str) -> int:
    text = str(args_text or "").strip()
    if not text:
        return 0
    depth = 0
    quote = ""
    count = 1
    for char in text:
        if quote:
            if char == quote:
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            count += 1
    return count


def _compile_source_with_draft_profile(
    *,
    source_text: str,
    parsed_profile: dict[str, Any],
    intake_plan: dict[str, Any] | None,
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
    compact_retry: bool = True,
) -> dict[str, Any]:
    allowed_predicates = profile_bootstrap_allowed_predicates(parsed_profile)
    predicate_contracts = profile_bootstrap_predicate_contracts(parsed_profile)
    domain_context = profile_bootstrap_domain_context(parsed_profile)
    source_compiler_context = _source_compiler_context(
        intake_plan=intake_plan,
        domain_hint=str(getattr(args, "domain_hint", "") or ""),
    )
    config = SemanticIRCallConfig(
        backend="lmstudio",
        base_url=str(args.base_url),
        model=str(args.model),
        context_length=int(args.num_ctx),
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        top_k=int(args.top_k),
        max_tokens=int(args.max_tokens),
        think_enabled=False,
        reasoning_effort="none",
    )
    plan_context = intake_plan_context(intake_plan)
    try:
        result = call_semantic_ir(
            utterance=source_text,
            config=config,
            context=[
                *plan_context,
                *source_compiler_context,
                *(extra_context or []),
                "Compile the raw source text using the draft profile proposed by profile_bootstrap_v1.",
                "Treat intake_plan_v1.pass_plan as the coverage checklist for this compile. Allocate candidate_operations across the planned passes instead of spending the whole operation budget on the first repeated structure you encounter.",
                "When pass_plan names source boundary, principles/rules, repeated records, final declarations, appeals, or pledges, emit at least one representative safe operation from each supported pass before adding extra repeated-record details.",
                "Use the breadth of the draft profile. If many allowed predicates are available, prefer a diverse skeleton that exercises distinct source/provenance, entity, claim, rule, repeated-record, declaration, and commitment predicate families over many operations using only one predicate family.",
                "Predicate contracts are binding. Preserve the exact argument order from predicate_contracts/allowed profile args. Do not swap subject/object, actor/time, recipient/type, facility/officer, or status/timestamp slots to make a fact fit. If the source supports a fact but the argument order is uncertain, skip it or note the uncertainty in self_check instead of emitting a malformed clause.",
                "Avoid predicate canonicalization drift. If the allowed palette contains synonymous prefixed and reusable detail predicates, such as grievance_observation_location/2 and observation_location/2, prefer the reusable detail predicate when its first argument is already the grievance/incident/record id.",
                "Use one canonical predicate surface consistently for a repeated slot. Do not mix grievance_method/2 with method/2, grievance_effect/2 with effect_claimed/2, or grievance_explanation_given/2 with explanation_given/2 unless their meanings are explicitly different in the profile contract.",
                "Do not add facts not present in the source text.",
                "If the whole source contains more safe facts than fit, preserve a balanced document skeleton: source/provenance boundary, core declaration or action, representative repeated records, and concluding commitments. Do not let one repeated list consume the whole candidate_operation budget.",
                "When a draft profile offers source-attributed claim predicates such as claim_made/3 or source_claim/3, prefer those for normative principles, rights, accusations, character judgments, and legitimacy statements that the source asserts but does not externally prove.",
                "If both a direct normative predicate and a source-attributed claim predicate are available, use the source-attributed claim predicate for rights, principles, legitimacy, and character judgments unless the direct predicate itself has a source/document argument.",
                "Preserve reporting and ledger-record acts as first-class queryable details when the draft profile supports them. If a source says someone reported, complained, witnessed, recorded, entered in a ledger, certified, or observed something, prefer reporter/2, complainant/2, reported_observation/2, ledger_entry/2, or similar profile predicates over collapsing the detail into only affected_person/2 or grievance/2.",
                "Preserve epistemic status for source-owned repeated records when the draft profile supports it. For grievances, allegations, complaints, and accusations, emit status/provenance facts such as grievance_status(Grievance, source_bound_accusation) or the profile's equivalent rather than leaving the accusation-vs-fact distinction only implicit in predicate names.",
                "When the source names a reporting actor and a role, preserve both if the palette supports it, e.g. a reporter/person predicate plus person_role/2. This is structural source fidelity, not a domain-specific language patch.",
                "When a source contrasts two ledgers or records, preserve both the individual ledger entries and the conflict relation if the palette supports them. Do not keep only the conflict wrapper if a later question may ask which ledger recorded which event.",
                "When the allowed palette contains ledger_entry plus a ledger-conflict predicate, emit ledger_entry facts for each side of the conflict before the conflict summary whenever the source identifies each ledger's content.",
                "When the allowed palette contains explanation/detail predicates, preserve explicitly given explanations as queryable facts rather than only encoding the resulting rule, separation, or violation.",
                "For recall, impoundment, remedy, declaration, and not-fit actions, keep item, status, location, label, authority, and condition queryable as separate attributes when the palette supports them. Do not hide Dock C or a quoted label only inside a long item atom if a later question may ask for it.",
                "Do not emit source_priority, override, conflict, or authority-ranking facts unless the source explicitly ranks sources or states an override/conflict policy.",
                "When a predicate contract names an argument source, source_document, or document, bind that argument to a stable source/document id such as doc_1 or a normalized document id. Do not put the speaker, claimant, or claim subject in a source/document argument.",
                "For whole-source compilation, hard-cap any single repeated structure at 24 total candidate_operations, counting the record predicate and every property predicate. Do not exceed 6 representative records for any one repeated structure in a whole-source skeleton pass. If the source contains more records, list the omitted structure in self_check rather than emitting more operations.",
                "Emit source identity, core declaration/conclusion acts, and commitment/pledge operations before representative repeated records. A repeated structure must not crowd out the source boundary or conclusion.",
                "For a long document skeleton, aim for this mix when the profile supports it: 2-4 source/provenance operations, 2-6 source-attributed principles or rights, 12-24 operations for representative repeated records, 2-6 declaration/conclusion operations, and 2-6 commitment/pledge operations. The exact predicates must still come from the draft profile.",
                "If complete ingestion requires more operations than the schema cap, write the balanced skeleton and put segment_required_for_complete_ingestion in self_check.missing_slots/notes with the omitted section types.",
            ],
            domain_context=domain_context,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
            kb_context_pack={},
            domain=f"profile_bootstrap:{parsed_profile.get('domain_guess', 'unknown')}",
            include_model_input=False,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    ir = result.get("parsed") if isinstance(result, dict) else None
    if not isinstance(ir, dict):
        if compact_retry:
            return _compile_source_with_draft_profile(
                source_text=source_text,
                parsed_profile=parsed_profile,
                intake_plan=intake_plan,
                args=args,
                extra_context=[
                    *(extra_context or []),
                    "COMPACT RETRY: the previous Semantic IR response for this same planned pass was not parseable.",
                    "Return a smaller valid semantic_ir_v1 object. Keep entities sparse and reusable.",
                    "For repeated-record/evidence passes, emit at most 24 candidate_operations and at most 8 entities total.",
                    "Prioritize high-query-value details: reporting actors, complainants, ledger entries, conflicts between ledgers, affected items, locations, measurements, and rule violations.",
                    "Keep self_check.notes to at most two short notes.",
                ],
                compact_retry=False,
            )
        return {
            "ok": False,
            "error": str(result.get("parse_error", "semantic_ir_parse_failed")) if isinstance(result, dict) else "semantic_ir_failed",
            "raw_content": str((result or {}).get("content", ""))[:4000] if isinstance(result, dict) else "",
        }
    mapped, warnings = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    return {
        "ok": True,
        "model_decision": ir.get("decision", ""),
        "projected_decision": diagnostics.get("projected_decision", ""),
        "admitted_count": int(diagnostics.get("admitted_count", 0) or 0),
        "skipped_count": int(diagnostics.get("skipped_count", 0) or 0),
        "warnings": warnings,
        "facts": mapped.get("facts", []),
        "rules": mapped.get("rules", []),
        "queries": mapped.get("queries", []),
        "self_check": ir.get("self_check", {}),
    }


def _compile_source_with_plan_passes(
    *,
    source_text: str,
    parsed_profile: dict[str, Any],
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    pass_plan = intake_plan.get("pass_plan") if isinstance(intake_plan.get("pass_plan"), list) else []
    pass_records: list[dict[str, Any]] = []
    unique_facts: list[str] = []
    unique_rules: list[str] = []
    unique_queries: list[str] = []
    seen_facts: set[str] = set()
    seen_rules: set[str] = set()
    seen_queries: set[str] = set()
    max_passes = max(1, int(getattr(args, "max_plan_passes", 8) or 8))
    for index, item in enumerate(pass_plan[:max_passes]):
        if not isinstance(item, dict):
            continue
        pass_id = str(item.get("pass_id", f"pass_{index + 1}")).strip() or f"pass_{index + 1}"
        purpose = str(item.get("purpose", "")).strip()
        focus = str(item.get("focus", "")).strip()
        completion = str(item.get("completion_policy", "")).strip()
        predicates = ", ".join(
            str(row).strip()
            for row in item.get("recommended_predicates", [])
            if str(row).strip()
        ) if isinstance(item.get("recommended_predicates"), list) else ""
        compiled = _compile_source_with_draft_profile(
            source_text=source_text,
            parsed_profile=parsed_profile,
            intake_plan=intake_plan,
            args=args,
            extra_context=[
                "This is focused plan-pass compilation, not a whole-source gulp.",
                f"current_intake_pass_id: {pass_id}",
                f"current_intake_pass_purpose: {purpose}",
                f"current_intake_pass_focus: {focus}",
                f"current_intake_pass_completion_policy: {completion}",
                f"current_intake_pass_recommended_predicates: {predicates}",
                "For this call, emit only operations that belong to the current intake pass. Defer other source material to its own pass.",
                "It is better to be complete for this pass than broadly summary-like across the entire source.",
                "Keep focused pass JSON compact: reuse normalized atoms directly in candidate_operations instead of listing every named thing as an entity.",
                "For focused pass compilation, aim for at most 12 entities, 32 candidate_operations, and 3 short self_check notes.",
            ],
        )
        compiled["pass_id"] = pass_id
        compiled["purpose"] = purpose
        compiled["focus"] = focus
        pass_records.append(compiled)
        for target, seen, values in [
            (unique_facts, seen_facts, compiled.get("facts", [])),
            (unique_rules, seen_rules, compiled.get("rules", [])),
            (unique_queries, seen_queries, compiled.get("queries", [])),
        ]:
            for value in values if isinstance(values, list) else []:
                text = str(value).strip()
                if text and text not in seen:
                    seen.add(text)
                    target.append(text)
    return {
        "ok": all(bool(item.get("ok")) for item in pass_records) if pass_records else False,
        "mode": "intake_plan_passes",
        "pass_count": len(pass_records),
        "admitted_count": sum(int(item.get("admitted_count", 0) or 0) for item in pass_records),
        "skipped_count": sum(int(item.get("skipped_count", 0) or 0) for item in pass_records),
        "unique_fact_count": len(unique_facts),
        "unique_rule_count": len(unique_rules),
        "unique_query_count": len(unique_queries),
        "facts": unique_facts,
        "rules": unique_rules,
        "queries": unique_queries,
        "passes": pass_records,
    }


def _source_compiler_context(*, intake_plan: dict[str, Any] | None, domain_hint: str = "") -> list[str]:
    """Return context modules selected from LLM-owned/source-external control data.

    This does not inspect the source prose. The branch uses either a user-supplied
    domain hint or the structured source type proposed by intake_plan_v1.
    """
    terms: list[str] = [str(domain_hint or "").casefold()]
    if isinstance(intake_plan, dict):
        boundary = intake_plan.get("source_boundary") if isinstance(intake_plan.get("source_boundary"), dict) else {}
        terms.extend(
            [
                str(boundary.get("source_type", "")).casefold(),
                str(boundary.get("epistemic_stance", "")).casefold(),
            ]
        )
        for item in intake_plan.get("pass_plan", []) if isinstance(intake_plan.get("pass_plan"), list) else []:
            if isinstance(item, dict):
                terms.extend(
                    [
                        str(item.get("purpose", "")).casefold(),
                        str(item.get("focus", "")).casefold(),
                    ]
                )
    label = " ".join(terms)
    contexts: list[str] = []
    if any(token in label for token in ["story", "narrative", "fable", "fiction", "plot"]):
        contexts.extend(NARRATIVE_SOURCE_COMPILER_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "policy",
            "compliance",
            "incident",
            "operations",
            "regulatory",
            "timeline",
            "municipal",
            "procedure",
            "threshold",
            "authorization",
        ]
    ):
        contexts.extend(POLICY_INCIDENT_SOURCE_COMPILER_CONTEXT_V1)
    return contexts


def _call_lmstudio_json_schema(
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
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema,
            },
        },
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc
    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    reasoning_content = str(message.get("reasoning_content", "") if isinstance(message, dict) else "").strip()
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": content or reasoning_content,
    }


def _write_summary(record: dict[str, Any], path: Path) -> None:
    parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
    score = record.get("score") if isinstance(record.get("score"), dict) else {}
    compile_record = record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {}
    lines = [
        "# Domain Bootstrap File Run",
        "",
        f"- Source file: `{record.get('text_file', '')}`",
        f"- Backend/model: `{record.get('backend', '')}` / `{record.get('model', '')}`",
        f"- Parsed: `{record.get('parsed_ok', False)}`",
        f"- Rough score: `{score.get('rough_score', 0.0)}`",
        f"- Entity types: `{score.get('entity_type_count', 0)}`",
        f"- Candidate predicates: `{score.get('predicate_count', 0)}`",
        f"- Generic predicates: `{score.get('generic_predicate_count', 0)}`",
        f"- Repeated structures: `{score.get('repeated_structure_count', 0)}`",
        f"- Repeated-structure unknown predicate refs: `{score.get('repeated_structure_unknown_predicate_refs', [])}`",
        f"- Repeated-structure id-only record refs: `{score.get('repeated_structure_id_only_record_refs', [])}`",
        f"- Repeated-structure role mismatch refs: `{score.get('repeated_structure_role_mismatch_refs', [])}`",
        f"- Frontier unknown positive predicate refs: `{score.get('frontier_unknown_positive_predicate_refs', [])}`",
        "",
    ]
    intake = record.get("intake_plan") if isinstance(record.get("intake_plan"), dict) else {}
    if intake:
        plan = intake.get("parsed") if isinstance(intake.get("parsed"), dict) else {}
        boundary = plan.get("source_boundary") if isinstance(plan.get("source_boundary"), dict) else {}
        lines.extend(
            [
                "## Intake Plan",
                "",
                f"- Parsed: `{intake.get('parsed_ok', False)}`",
                f"- Source type: `{boundary.get('source_type', '')}`",
                f"- Epistemic stance: `{boundary.get('epistemic_stance', '')}`",
                f"- Passes: `{len(plan.get('pass_plan', [])) if isinstance(plan.get('pass_plan'), list) else 0}`",
                "",
            ]
        )
        for item in plan.get("pass_plan", []) if isinstance(plan.get("pass_plan"), list) else []:
            if isinstance(item, dict):
                lines.append(
                    f"- `{item.get('pass_id', '')}` {item.get('purpose', '')}: {item.get('focus', '')}"
                )
        lines.append("")
    review = record.get("profile_review") if isinstance(record.get("profile_review"), dict) else {}
    if review:
        parsed_review = review.get("parsed") if isinstance(review.get("parsed"), dict) else {}
        lines.extend(
            [
                "## Profile Review",
                "",
                f"- Parsed: `{review.get('parsed_ok', False)}`",
                f"- Verdict: `{parsed_review.get('verdict', '')}`",
                f"- Coverage OK: `{parsed_review.get('coverage_ok', '')}`",
                f"- Missing capabilities: `{len(parsed_review.get('missing_capabilities', [])) if isinstance(parsed_review.get('missing_capabilities'), list) else 0}`",
                "",
            ]
        )
        for item in parsed_review.get("retry_guidance", []) if isinstance(parsed_review.get("retry_guidance"), list) else []:
            text = str(item).strip()
            if text:
                lines.append(f"- Retry guidance: {text}")
        lines.append("")
    review_retry = record.get("profile_review_retry") if isinstance(record.get("profile_review_retry"), dict) else {}
    if review_retry:
        lines.extend(
            [
                "## Profile Review Retry",
                "",
                f"- Parsed: `{review_retry.get('parsed_ok', False)}`",
                f"- Parse error: `{review_retry.get('parse_error', '')}`",
                "",
            ]
        )
    lines.extend(["## Candidate Predicates", ""])
    for item in parsed.get("candidate_predicates", []) if isinstance(parsed.get("candidate_predicates"), list) else []:
        if isinstance(item, dict):
            lines.append(f"- `{item.get('signature', '')}` args={item.get('args', [])}: {item.get('description', '')}")
    if not lines[-1].startswith("- `"):
        lines.append("- none")
    lines.extend(["", "## Repeated Structures", ""])
    repeated = parsed.get("repeated_structures", []) if isinstance(parsed.get("repeated_structures"), list) else []
    if repeated:
        for item in repeated:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- `{item.get('name', '')}` record=`{item.get('record_predicate', '')}` "
                f"properties={item.get('property_predicates', [])}: {item.get('why', '')}"
            )
            examples = item.get("example_records", []) if isinstance(item.get("example_records"), list) else []
            for example in examples[:3]:
                lines.append(f"  - `{example}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Admission Risks", ""])
    risks = [str(item).strip() for item in parsed.get("admission_risks", []) if str(item).strip()] if isinstance(parsed.get("admission_risks"), list) else []
    lines.extend([f"- {item}" for item in risks] or ["- none"])
    if compile_record:
        lines.extend(
            [
                "",
                "## Source Compile",
                "",
                f"- OK: `{compile_record.get('ok', False)}`",
                f"- Model decision: `{compile_record.get('model_decision', '')}`",
                f"- Projected decision: `{compile_record.get('projected_decision', '')}`",
                f"- Admitted: `{compile_record.get('admitted_count', 0)}`",
                f"- Skipped: `{compile_record.get('skipped_count', 0)}`",
                "",
                "### Facts",
                "",
                "```prolog",
                *[str(item) for item in compile_record.get("facts", [])],
                "```",
                "",
                "### Rules",
                "",
                "```prolog",
                *[str(item) for item in compile_record.get("rules", [])],
                "```",
            ]
        )
    expected = record.get("expected_prolog") if isinstance(record.get("expected_prolog"), dict) else {}
    if expected:
        lines.extend(
            [
                "",
                "## Expected Prolog Signature Comparison",
                "",
                f"- Expected: `{expected.get('expected_path', '')}`",
                f"- Expected signatures: `{expected.get('expected_signature_count', 0)}`",
                f"- Profile candidate signatures: `{expected.get('profile_signature_count', 0)}`",
                f"- Profile overlap signatures: `{expected.get('profile_overlap_signature_count', 0)}`",
                f"- Profile signature recall: `{expected.get('profile_signature_recall', 0.0)}`",
                f"- Emitted signatures: `{expected.get('emitted_signature_count', 0)}`",
                f"- Overlap signatures: `{expected.get('overlap_signature_count', 0)}`",
                f"- Signature recall: `{expected.get('signature_recall', 0.0)}`",
                f"- Signature precision: `{expected.get('signature_precision', 0.0)}`",
                "",
                "### Overlap",
                "",
                "```text",
                "\n".join(expected.get("overlap_signatures", [])),
                "```",
                "",
                "### Profile Overlap",
                "",
                "```text",
                "\n".join(expected.get("profile_overlap_signatures", [])),
                "```",
                "",
                "### Missing From Profile",
                "",
                "```text",
                "\n".join(expected.get("profile_missing_signatures", [])),
                "```",
                "",
                "### Missing From Emitted",
                "",
                "```text",
                "\n".join(expected.get("missing_signatures", [])),
                "```",
                "",
                "### Extra In Emitted",
                "",
                "```text",
                "\n".join(expected.get("extra_signatures", [])),
                "```",
            ]
        )
    lines.extend(["", "## Full Profile JSON", "", "```json", json.dumps(parsed, ensure_ascii=False, indent=2, sort_keys=True), "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(value: str) -> str:
    import re

    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip()).strip("-").lower()
    return text[:60] or "run"


if __name__ == "__main__":
    raise SystemExit(main())
