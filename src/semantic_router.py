from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from src.semantic_ir import SemanticIRCallConfig


SEMANTIC_ROUTER_SYSTEM = (
    "You are semantic_router_v1 for a governed symbolic memory ingestion system. "
    "You do not answer the user, do not extract final facts, and do not authorize KB writes. "
    "Your job is context engineering and action planning: choose the domain/profile, guidance modules, "
    "retrieval hints, segmentation plan, and minimal next processing actions that should be handed to "
    "the semantic_ir_v1 compiler. "
    "Emit only semantic_router_v1 JSON. Be multilingual-capable and uncertainty-preserving. "
    "Never treat routing-policy examples as recent_context; only the INPUT_JSON.recent_context array is recent context."
)


GUIDANCE_MODULES = [
    "claim_vs_fact",
    "source_fidelity",
    "medical_advice_boundary",
    "medical_entity_normalization",
    "legal_claim_finding_boundary",
    "contract_obligation_semantics",
    "rule_query_boundary",
    "temporal_scope",
    "correction_retraction",
    "identity_ambiguity",
    "predicate_contract_obedience",
    "story_world_source_locality",
    "non_english_normalization",
    "profile_bootstrap",
]


CONTROLLER_ACTIONS = [
    "compile_semantic_ir",
    "segment_before_compile",
    "include_kb_context",
    "include_temporal_graph_guidance",
    "include_truth_maintenance_guidance",
    "extract_query_operations",
    "review_before_admission",
    "profile_bootstrap_review",
    "ask_clarification_first",
]


ROUTER_SCHEMA_CONTRACT: dict[str, Any] = {
    "schema_version": "semantic_router_v1",
    "selected_profile_id": "medical@v0|story_world@v0|probate@v0|sec_contracts@v0|legal_courtlistener@v0|general|bootstrap",
    "candidate_profile_ids": ["medical@v0"],
    "routing_confidence": 0.0,
    "turn_shape": "state_update|query|correction|rule_update|mixed|story_or_document|unknown",
    "should_segment": False,
    "segments": [
        {
            "span_id": "s1",
            "text": "",
            "purpose": "state_update|query|correction|rule_update|mixed|context|unknown",
            "reason": "",
        }
    ],
    "guidance_modules": ["claim_vs_fact"],
    "action_plan": {
        "actions": ["compile_semantic_ir"],
        "skip_heavy_steps": [],
        "review_triggers": [],
        "why": "",
    },
    "retrieval_hints": {
        "entity_terms": [],
        "predicate_terms": [],
        "context_needs": [],
    },
    "risk_flags": [],
    "context_audit": {
        "why_this_profile": "",
        "selected_context_sources": [],
        "secondary_profiles_considered": [],
        "why_not_secondary": [],
    },
    "bootstrap_request": {
        "needed": False,
        "proposed_domain_name": "",
        "why": "",
        "candidate_predicate_concepts": [],
    },
    "notes": [],
}


SEMANTIC_ROUTER_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "selected_profile_id",
        "candidate_profile_ids",
        "routing_confidence",
        "turn_shape",
        "should_segment",
        "segments",
        "guidance_modules",
        "action_plan",
        "retrieval_hints",
        "risk_flags",
        "context_audit",
        "bootstrap_request",
        "notes",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "semantic_router_v1"},
        "selected_profile_id": {"type": "string"},
        "candidate_profile_ids": {
            "type": "array",
            "maxItems": 4,
            "items": {"type": "string"},
        },
        "routing_confidence": {"type": "number"},
        "turn_shape": {
            "type": "string",
            "enum": ["state_update", "query", "correction", "rule_update", "mixed", "story_or_document", "unknown"],
        },
        "should_segment": {"type": "boolean"},
        "segments": {
            "type": "array",
            "maxItems": 16,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["span_id", "text", "purpose", "reason"],
                "properties": {
                    "span_id": {"type": "string"},
                    "text": {"type": "string"},
                    "purpose": {
                        "type": "string",
                        "enum": ["state_update", "query", "correction", "rule_update", "mixed", "context", "unknown"],
                    },
                    "reason": {"type": "string"},
                },
            },
        },
        "guidance_modules": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "string",
                "enum": GUIDANCE_MODULES,
            },
        },
        "action_plan": {
            "type": "object",
            "additionalProperties": False,
            "required": ["actions", "skip_heavy_steps", "review_triggers", "why"],
            "properties": {
                "actions": {
                    "type": "array",
                    "maxItems": 8,
                    "items": {"type": "string", "enum": CONTROLLER_ACTIONS},
                },
                "skip_heavy_steps": {
                    "type": "array",
                    "maxItems": 8,
                    "items": {"type": "string"},
                },
                "review_triggers": {
                    "type": "array",
                    "maxItems": 8,
                    "items": {"type": "string"},
                },
                "why": {"type": "string"},
            },
        },
        "retrieval_hints": {
            "type": "object",
            "additionalProperties": False,
            "required": ["entity_terms", "predicate_terms", "context_needs"],
            "properties": {
                "entity_terms": {"type": "array", "maxItems": 16, "items": {"type": "string"}},
                "predicate_terms": {"type": "array", "maxItems": 16, "items": {"type": "string"}},
                "context_needs": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
            },
        },
        "risk_flags": {"type": "array", "maxItems": 10, "items": {"type": "string"}},
        "context_audit": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "why_this_profile",
                "selected_context_sources",
                "secondary_profiles_considered",
                "why_not_secondary",
            ],
            "properties": {
                "why_this_profile": {"type": "string"},
                "selected_context_sources": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
                "secondary_profiles_considered": {"type": "array", "maxItems": 6, "items": {"type": "string"}},
                "why_not_secondary": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
            },
        },
        "bootstrap_request": {
            "type": "object",
            "additionalProperties": False,
            "required": ["needed", "proposed_domain_name", "why", "candidate_predicate_concepts"],
            "properties": {
                "needed": {"type": "boolean"},
                "proposed_domain_name": {"type": "string"},
                "why": {"type": "string"},
                "candidate_predicate_concepts": {
                    "type": "array",
                    "maxItems": 12,
                    "items": {"type": "string"},
                },
            },
        },
        "notes": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
    },
}


@dataclass(frozen=True)
class SemanticRouterCallConfig:
    backend: str = "lmstudio"
    base_url: str = "http://127.0.0.1:1234"
    model: str = "qwen/qwen3.6-35b-a3b"
    context_length: int = 16384
    timeout: int = 120
    temperature: float = 0.0
    top_p: float = 0.82
    top_k: int = 20
    think_enabled: bool = False
    reasoning_effort: str = "none"
    max_tokens: int = 4000

    @classmethod
    def from_semantic_ir_config(cls, config: SemanticIRCallConfig) -> "SemanticRouterCallConfig":
        return cls(
            backend=config.backend,
            base_url=config.base_url,
            model=config.model,
            context_length=config.context_length,
            timeout=config.timeout,
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            think_enabled=config.think_enabled,
            reasoning_effort=config.reasoning_effort,
            max_tokens=min(int(config.max_tokens), 4000),
        )


def build_semantic_router_input_payload(
    *,
    utterance: str,
    context: list[str] | None = None,
    available_domain_profiles: list[dict[str, Any]] | None = None,
    kb_manifest: dict[str, Any] | None = None,
    include_schema_contract: bool = True,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "task": "Analyze the utterance and choose the context package for the next semantic_ir_v1 compiler pass.",
        "output_instruction": "Return exactly one semantic_router_v1 JSON object.",
        "utterance": utterance,
        "recent_context": context or [],
        "available_domain_profiles": available_domain_profiles or [],
        "available_guidance_modules": GUIDANCE_MODULES,
        "available_controller_actions": CONTROLLER_ACTIONS,
        "kb_manifest": kb_manifest or {},
        "routing_policy": [
            "Select one known profile when a domain profile clearly fits and context_available is true.",
            "Do not select profiles with context_available=false; use general or bootstrap instead and mention the near-miss profile in notes.",
            "Use general when no known profile clearly fits but the utterance can still be compiled with generic predicates.",
            "Use bootstrap when the utterance needs a new domain profile or predicate vocabulary before safe compilation.",
            "Use bootstrap when the utterance or recent_context explicitly introduces a new, ad hoc, specialized, or no-existing-profile domain whose core predicates are not in the known profile roster. Do this even when a known profile such as sec_contracts@v0 could express some generic rule shape; list that known profile as a candidate/advisory lane instead of making it primary.",
            "Do not invent recent context. Router notes may refer to recent_context only when that content is actually present in the provided recent_context array. If no relevant context is present, say so rather than supplying a remembered scenario, name, ledger, beneficiary, or domain from prior runs.",
            "Routing policy text is not evidence. Do not claim the context mentions examples from this policy such as Silverton, probate ledger, beneficiary, charter, forfeiture, access_log_entry, or pharmacy log unless those words appear in the current utterance or recent_context.",
            "Choose profiles by semantic toolset, not by whether the text is fictional or real. A fictional deed, charter, filing, covenant, policy, or court-like statement may still need the legal/probate/contracts toolset.",
            "Use story_world for ordinary narrative event/source fidelity. Do not choose story_world merely because names or settings are invented when formal rules, obligations, approvals, legal instruments, claims, findings, or conditional validity dominate.",
            "If recent_context explicitly labels the turn as story-world scene memory, and the utterance concerns ordinary object location, possession, entry/exit, finding, hiding, tasting, sitting, lying, or a hypothetical about story objects, prefer story_world@v0 unless legal/probate/contract instruments are explicit in the utterance or context.",
            "Use contracts/policy profiles for rule validity, obligations, exceptions, approvals, clearance conditions, access/support/launch/payment policy, only-if/default/exception logic, and conditional state when no more specific implemented operational profile exists. sec_contracts@v0 is also the current implemented generic business/policy-rule toolset, not only SEC filings.",
            "Use sec_contracts@v0 for corrections, clarifications, or uncertainty about operational/contractual states such as waived notice, approval, access, support priority, delivery, payment, default, maturity, covenant, or agreement terms. Draft/final/source uncertainty inside a contract or policy record is still contract/policy ownership unless the source is explicitly a court docket, pleading, deposition, opinion, or legal evidence record.",
            "Safety ownership beats avoid_when. If the utterance is a clinical advice, dose, hold, start, stop, or treatment question, select medical@v0 so the compiler receives the medical rejection/advice-boundary guidance; do not route such turns to general merely because medical@v0 will reject the requested action.",
            "Use probate/legal profiles for deeds, charters, estate-like claims, beneficiaries, witnesses, amendments, legal records, source-backed claims, and document/evidence conflicts.",
            "Disambiguation: choose legal_courtlistener@v0 for legal or administrative source records such as deeds, board minutes, logs, notes, affidavits, access stamps, countersignatures, document dates, and source-backed claim/evidence conflicts when the turn is not specifically about inheritance, beneficiaries, wills, estate shares, probate ledgers, or forfeiture.",
            "Disambiguation: choose probate@v0 only when estate/probate/inheritance concepts dominate: will, estate, beneficiary, share, charter amendment, probate ledger, forfeiture, guardianship, or named probate scenario pressure.",
            "Do not choose probate@v0 merely because a witness, identity, signature, or legal statement is mentioned. Generic witness testimony, deposition statements, pleadings, source-record disputes, and subject/object corrections belong to legal_courtlistener@v0 unless estate/probate concepts are explicit.",
            "If recent_context explicitly says the active setting is probate, estate, beneficiary, codicil, will, guardianship, or probate identity ambiguity, keep follow-up witness/register/initial/identity disputes in probate@v0 unless the utterance clearly changes to a court opinion, docket, complaint, deposition, or non-probate legal source.",
            "When medical facts appear inside depositions, complaints, affidavits, witness statements, docket records, or disputed legal evidence, choose legal_courtlistener@v0 as primary and medical@v0 as candidate/advisory. The legal source/provenance lane owns the claim; the medical lane may normalize clinical terms but does not admit the testimony as clinical truth.",
            "Disambiguation: choose sec_contracts@v0 for conditional operational governance when it centers on if/unless/before/after approvals, clearances, freezes, release authority, obligations, or conditions, even if the item names are fictional or logistics-like and logistics@v0 is unavailable.",
            "Recent context is routing evidence. For short corrections, fragments, pronouns, aliases, or date repairs, inherit the domain pressure from recent_context unless the new utterance clearly changes domains.",
            "If recent_context mentions Silverton, probate ledger, beneficiary, charter, estate, forfeiture, guardianship, or known probate scenario identities, prefer probate@v0 for follow-up corrections even when the current utterance is terse.",
            "If recent_context or utterance mentions access_log_entry, access stamp, pharmacy log, room, board minutes, deed, document date, or source log correction, prefer legal_courtlistener@v0 over unavailable logistics@v0.",
            "Do not infer facts. Do not produce candidate_operations. Do not answer the user.",
            "If segmentation is useful, copy exact source text spans in order. Do not summarize segments.",
            "Prefer focused guidance modules over dumping all guidance into the compiler.",
            "Choose the smallest useful action plan. Do not force every turn through every expensive step.",
            "Use compile_semantic_ir for ordinary governed ingestion. Use segment_before_compile for long documents, multi-question turns, or mixed query/write turns where focused passes should reduce confusion.",
            "Use include_kb_context for corrections, pronouns, current-state replacement, conflict checks, or query turns that depend on stored facts.",
            "Use extract_query_operations whenever the utterance asks an explicit question, even if it also asserts rules or facts. Mixed write+query turns should usually include compile_semantic_ir and extract_query_operations.",
            "Use include_temporal_graph_guidance for before/after/during/last/next/date correction, interval, deadline, expiry, maturity, or effective-date language.",
            "Use include_truth_maintenance_guidance for corrections, conflicting sources, claim-vs-observation, retraction planning, derived consequences, and dependency-sensitive updates.",
            "Use review_before_admission when routing confidence is low, when candidate profiles compete, when temporal facts are being corrected, or when a wrong profile could cause unsafe writes.",
            "Use ask_clarification_first when the safest next step is a question rather than a compile pass, but still leave admission authority to the mapper/compiler path.",
            "Use profile_bootstrap_review for unknown domains or when a predicate vocabulary must be designed before safe durable writes.",
            "Fill context_audit with why the selected profile/context was chosen, which context sources should be loaded, and why close secondary profiles were not primary. This is an audit trail only, not evidence or admission authority.",
        ],
        "authority_boundary": "Routing is advisory context engineering only. The mapper remains the authority for durable KB mutation.",
    }
    if include_schema_contract:
        payload["required_top_level_json_shape"] = ROUTER_SCHEMA_CONTRACT
        payload["output_instruction"] = (
            "Return exactly one JSON object using required_top_level_json_shape as the root shape. "
            "Do not copy the key name required_top_level_json_shape into your response."
        )
    return payload


def build_semantic_router_messages(
    *,
    utterance: str,
    context: list[str] | None = None,
    available_domain_profiles: list[dict[str, Any]] | None = None,
    kb_manifest: dict[str, Any] | None = None,
    include_schema_contract: bool = True,
) -> list[dict[str, str]]:
    payload = build_semantic_router_input_payload(
        utterance=utterance,
        context=context,
        available_domain_profiles=available_domain_profiles,
        kb_manifest=kb_manifest,
        include_schema_contract=include_schema_contract,
    )
    return [
        {"role": "system", "content": SEMANTIC_ROUTER_SYSTEM},
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]


def call_semantic_router(
    *,
    utterance: str,
    config: SemanticRouterCallConfig,
    context: list[str] | None = None,
    available_domain_profiles: list[dict[str, Any]] | None = None,
    kb_manifest: dict[str, Any] | None = None,
    include_model_input: bool = False,
) -> dict[str, Any]:
    messages = build_semantic_router_messages(
        utterance=utterance,
        context=context,
        available_domain_profiles=available_domain_profiles,
        kb_manifest=kb_manifest,
        include_schema_contract=True,
    )
    backend = str(config.backend or "lmstudio").strip().lower()
    if backend == "lmstudio":
        result = _call_lmstudio_router(config=config, messages=messages)
    elif backend == "ollama":
        result = _call_ollama_router(config=config, messages=messages)
    else:
        raise RuntimeError(f"semantic_router_v1 backend not supported: {backend}")
    if include_model_input:
        result["model_input"] = {
            "backend": backend,
            "model": config.model,
            "messages": messages,
            "options": {
                "temperature": float(config.temperature),
                "top_p": float(config.top_p),
                "top_k": int(config.top_k),
                "num_ctx": int(config.context_length),
                "max_tokens": int(config.max_tokens),
                "thinking": bool(config.think_enabled),
                "reasoning_effort": str(config.reasoning_effort or ""),
            },
        }
    return result


def parse_semantic_router_json(text: str) -> dict[str, Any] | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if "semantic_router" in parsed and isinstance(parsed.get("semantic_router"), dict):
        parsed = parsed["semantic_router"]
    if str(parsed.get("schema_version", "")).strip() != "semantic_router_v1":
        return None
    if not str(parsed.get("selected_profile_id", "")).strip():
        return None
    return parsed


def _call_ollama_router(*, config: SemanticRouterCallConfig, messages: list[dict[str, str]]) -> dict[str, Any]:
    payload = {
        "model": config.model,
        "stream": False,
        "format": "json",
        "think": bool(config.think_enabled),
        "messages": messages,
        "options": {
            "temperature": float(config.temperature),
            "top_p": float(config.top_p),
            "top_k": int(config.top_k),
            "num_ctx": int(config.context_length),
        },
    }
    req = urllib.request.Request(
        f"{config.base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=int(config.timeout)) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc

    message = raw.get("message", {}) if isinstance(raw, dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": content,
        "parsed": parse_semantic_router_json(content),
    }


def _call_lmstudio_router(*, config: SemanticRouterCallConfig, messages: list[dict[str, str]]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": config.model,
        "messages": messages,
        "temperature": float(config.temperature),
        "top_p": float(config.top_p),
        "max_tokens": int(config.max_tokens),
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "semantic_router_v1",
                "strict": True,
                "schema": SEMANTIC_ROUTER_JSON_SCHEMA,
            },
        },
    }
    if str(config.reasoning_effort or "").strip():
        payload["reasoning_effort"] = str(config.reasoning_effort).strip()
    base_url = config.base_url.rstrip("/")
    endpoint = f"{base_url}/chat/completions" if base_url.endswith("/v1") else f"{base_url}/v1/chat/completions"
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=int(config.timeout)) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc

    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    first = choices[0] if choices and isinstance(choices[0], dict) else {}
    message = first.get("message", {}) if isinstance(first, dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    if not content and isinstance(message, dict):
        content = str(message.get("reasoning_content", "") or "").strip()
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": content,
        "parsed": parse_semantic_router_json(content),
    }
