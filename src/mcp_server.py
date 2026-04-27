#!/usr/bin/env python3
"""
Prethinker MCP server (stdio transport).

This is a lightweight MCP-compatible server for LM Studio manual play:
- deterministic core runtime tools (assert/query/retract)
- pre-think session controls
- pre_think routing packet tool
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_pipeline import (
    _build_classifier_prompt,
    CorePrologRuntime,
    _build_extractor_prompt,
    _call_model_prompt,
    _extract_calls_with_args,
    _extract_retract_targets,
    _get_api_key,
    _load_env_file,
    _normalize_clause,
    _normalize_clarification_fields,
    _parse_model_json,
    _resolve_env_file,
    _synthesize_clarification_question,
    _validate_parsed,
)
from src.domain_profiles import (
    load_domain_profile_catalog,
    load_profile_package,
    profile_package_context,
    profile_package_contracts,
    select_domain_profile,
    thin_profile_roster,
)
from src.medical_profile import (
    bridge_admission_guidance,
    build_medical_profile_guide,
    canonical_predicate_signatures,
    load_profile_concepts,
    load_umls_bridge_facts,
    load_profile_manifest,
    rescue_medical_clarified_lab_result,
    resolve_profile_paths,
    sanitize_medical_parse_for_bridge,
    sanitize_medical_parse_for_clarification,
    semantic_ir_predicate_contracts,
    semantic_ir_profile_context,
)
from src.semantic_ir import (
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
    semantic_ir_to_prethink_payload,
)


FUNCTIONAL_CURRENT_STATE_PREDICATES: set[tuple[str, int]] = {
    ("lives_in", 2),
    ("located_at", 2),
    ("located_in", 2),
    ("scheduled_for", 2),
}

FUNCTIONAL_CURRENT_STATE_PREFIXES: tuple[str, ...] = (
    "current_",
    "latest_",
    "primary_",
)


def _coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on", "enabled"}:
            return True
        if lowered in {"0", "false", "no", "off", "disabled"}:
            return False
    return default


def _clip_01(value: Any, default: float = 0.75) -> float:
    try:
        v = float(value)
    except Exception:
        return default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _clip_temperature(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except Exception:
        return default
    if v < 0.0:
        return 0.0
    if v > 2.0:
        return 2.0
    return v


def _normalize_freethinker_resolution_policy(value: Any, default: str = "off") -> str:
    mode = str(value or default).strip().lower()
    if mode not in {"off", "advisory_only", "grounded_reference", "conservative_contextual"}:
        mode = str(default or "off").strip().lower() or "off"
    return mode


def _normalize_active_profile(value: Any, default: str = "general") -> str:
    aliases = {
        "default": "general",
        "general": "general",
        "auto": "auto",
        "medical": "medical@v0",
        "medical@v0": "medical@v0",
        "legal": "legal_courtlistener@v0",
        "legal_courtlistener": "legal_courtlistener@v0",
        "legal_courtlistener@v0": "legal_courtlistener@v0",
        "courtlistener": "legal_courtlistener@v0",
        "sec": "sec_contracts@v0",
        "sec_contracts": "sec_contracts@v0",
        "sec_contracts@v0": "sec_contracts@v0",
        "contracts": "sec_contracts@v0",
        "story": "story_world@v0",
        "story_world": "story_world@v0",
        "story_world@v0": "story_world@v0",
        "probate": "probate@v0",
        "probate@v0": "probate@v0",
    }
    requested = str(value or default).strip().lower()
    return aliases.get(requested, aliases.get(str(default or "general").strip().lower(), "general"))


def _bootstrap_env_from_local_file(explicit_path: str = "") -> Path | None:
    env_file = _resolve_env_file(str(explicit_path or "").strip(), None)
    if env_file is None:
        return None
    _load_env_file(env_file)
    return env_file


# Keep MCP entrypoints and in-process callers consistent with kb_pipeline
# behavior: auto-load local env keys when available.
_bootstrap_env_from_local_file()


@dataclass
class PreThinkSessionState:
    enabled: bool = True
    all_turns_require_prethink: bool = False
    clarification_eagerness: float = 0.75
    require_final_confirmation: bool = True


class PrologMCPServer:
    SUPPORTED_PROTOCOL_VERSIONS = [
        "2025-11-25",
        "2025-06-18",
        "2025-03-26",
        "2024-11-05",
    ]

    def __init__(
        self,
        kb_path: str = "",
        *,
        active_profile: str = "general",
        compiler_mode: str = "strict",
        compiler_backend: str = "ollama",
        compiler_base_url: str = "http://127.0.0.1:11434",
        compiler_model: str = "qwen3.5:9b",
        compiler_context_length: int = 8192,
        compiler_timeout: int = 60,
        compiler_prompt_file: str = "",
        compiler_prompt_enabled: bool = True,
        freethinker_resolution_policy: str = "off",
        freethinker_backend: str = "ollama",
        freethinker_base_url: str = "http://127.0.0.1:11434",
        freethinker_model: str = "qwen3.5:9b",
        freethinker_context_length: int = 16384,
        freethinker_timeout: int = 60,
        freethinker_prompt_file: str = "",
        freethinker_temperature: float = 0.2,
        freethinker_thinking: bool = False,
        semantic_ir_enabled: bool = False,
        semantic_ir_model: str = "qwen3.6:35b",
        semantic_ir_context_length: int = 16384,
        semantic_ir_timeout: int = 120,
        semantic_ir_temperature: float = 0.0,
        semantic_ir_top_p: float = 0.82,
        semantic_ir_top_k: int = 20,
        semantic_ir_thinking: bool = False,
    ) -> None:
        self._runtime = CorePrologRuntime()
        self._kb_path = str(Path(kb_path).resolve()) if str(kb_path).strip() else ""
        self._session = PreThinkSessionState()
        self._request_id = 1
        self._prethink_counter = 1
        self._pending_prethink: dict[str, Any] | None = None
        self._trace_path = REPO_ROOT / "tmp" / "mcp_trace.log"
        self._active_profile = _normalize_active_profile(active_profile, "general")
        self._compiler_mode = str(compiler_mode or "strict").strip().lower()
        if self._compiler_mode not in {"strict", "auto", "heuristic"}:
            self._compiler_mode = "strict"
        self._compiler_backend = str(compiler_backend or "ollama").strip()
        self._compiler_base_url = str(compiler_base_url or "http://127.0.0.1:11434").strip()
        self._compiler_model = str(compiler_model or "qwen3.5:9b").strip()
        self._compiler_context_length = max(512, int(compiler_context_length))
        self._compiler_timeout = max(5, int(compiler_timeout))
        prompt_candidate = str(compiler_prompt_file or "").strip()
        if not prompt_candidate:
            prompt_candidate = str(REPO_ROOT / "modelfiles" / "semantic_parser_system_prompt.md")
        self._compiler_prompt_path = Path(prompt_candidate)
        self._compiler_prompt_enabled = bool(compiler_prompt_enabled)
        self._compiler_prompt_text = ""
        self._compiler_prompt_loaded = False
        self._compiler_prompt_load_error = ""
        self._compiler_api_key = _get_api_key()
        self._semantic_ir_enabled = bool(semantic_ir_enabled)
        self._semantic_ir_model = str(semantic_ir_model or "qwen3.6:35b").strip()
        self._semantic_ir_context_length = max(512, int(semantic_ir_context_length))
        self._semantic_ir_timeout = max(5, int(semantic_ir_timeout))
        self._semantic_ir_temperature = _clip_temperature(semantic_ir_temperature, 0.0)
        try:
            self._semantic_ir_top_p = float(semantic_ir_top_p)
        except Exception:
            self._semantic_ir_top_p = 0.82
        if self._semantic_ir_top_p < 0.0:
            self._semantic_ir_top_p = 0.0
        if self._semantic_ir_top_p > 1.0:
            self._semantic_ir_top_p = 1.0
        try:
            self._semantic_ir_top_k = max(1, int(semantic_ir_top_k))
        except Exception:
            self._semantic_ir_top_k = 20
        self._semantic_ir_thinking = bool(semantic_ir_thinking)
        self._last_semantic_ir_trace: dict[str, Any] = {}
        self._last_semantic_ir_profile_selection: dict[str, Any] = {}
        self._last_semantic_ir_selected_profile = ""
        self._freethinker_resolution_policy = _normalize_freethinker_resolution_policy(
            freethinker_resolution_policy,
            "off",
        )
        self._freethinker_backend = str(freethinker_backend or "ollama").strip()
        self._freethinker_base_url = str(freethinker_base_url or "http://127.0.0.1:11434").strip()
        self._freethinker_model = str(freethinker_model or "qwen3.5:9b").strip()
        self._freethinker_context_length = max(512, int(freethinker_context_length))
        self._freethinker_timeout = max(5, int(freethinker_timeout))
        self._freethinker_temperature = _clip_temperature(freethinker_temperature, 0.2)
        self._freethinker_thinking = bool(freethinker_thinking)
        freethinker_prompt_candidate = str(freethinker_prompt_file or "").strip()
        if not freethinker_prompt_candidate:
            freethinker_prompt_candidate = str(REPO_ROOT / "modelfiles" / "freethinker_system_prompt.md")
        self._freethinker_prompt_path = Path(freethinker_prompt_candidate)
        self._freethinker_prompt_text = ""
        self._freethinker_prompt_loaded = False
        self._freethinker_prompt_load_error = ""
        self._freethinker_api_key = _get_api_key()
        self._profile_manifest: dict[str, Any] = {}
        self._domain_profile_catalog: dict[str, Any] = {}
        self._domain_profile_roster: list[dict[str, Any]] = []
        self._domain_profile_catalog_error = ""
        self._load_domain_profile_catalog()
        self._profile_paths: dict[str, Path] = {}
        self._profile_prompt_supplement = ""
        self._profile_known_predicates: list[str] = []
        self._profile_predicate_contracts: list[dict[str, Any]] = []
        self._profile_semantic_ir_context: list[str] = []
        self._profile_concepts: list[dict[str, Any]] = []
        self._profile_umls_bridge: dict[str, Any] = {}
        self._profile_load_error = ""
        self._load_profile_assets()
        self._registry_signatures = self._load_registry_signatures()
        self._last_prethink_trace: dict[str, Any] = {}
        self._last_prethink_fallback_trace: dict[str, Any] = {}
        self._last_parse_trace: dict[str, Any] = {}
        self._recent_accepted_turns: list[dict[str, Any]] = []
        self._recent_committed_logic: list[str] = []
        self._load_compiler_prompt()
        self._load_freethinker_prompt()

    def _load_domain_profile_catalog(self) -> None:
        self._domain_profile_catalog = {}
        self._domain_profile_roster = []
        self._domain_profile_catalog_error = ""
        try:
            catalog = load_domain_profile_catalog()
            self._domain_profile_catalog = catalog
            self._domain_profile_roster = thin_profile_roster(catalog)
        except Exception as exc:
            self._domain_profile_catalog_error = str(exc)

    def _default_medical_slice_dir(self) -> Path:
        return (REPO_ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp").resolve()

    def _load_profile_assets(self) -> None:
        self._profile_manifest = {}
        self._profile_paths = {}
        self._profile_prompt_supplement = ""
        self._profile_known_predicates = []
        self._profile_predicate_contracts = []
        self._profile_semantic_ir_context = []
        self._profile_concepts = []
        self._profile_umls_bridge = {}
        self._profile_load_error = ""
        if self._active_profile not in {"medical@v0", "auto"}:
            return
        try:
            manifest = load_profile_manifest()
            profile_paths = resolve_profile_paths()
            supplement_path = profile_paths.get("prompt_supplement", Path())
            supplement = (
                supplement_path.read_text(encoding="utf-8")
                if isinstance(supplement_path, Path) and supplement_path.exists()
                else ""
            )
            slice_dir = self._default_medical_slice_dir()
            concepts = load_profile_concepts(slice_dir) if slice_dir.exists() else []
            bridge_path = profile_paths.get("umls_bridge_facts", Path())
            if not isinstance(bridge_path, Path) or not str(bridge_path).strip():
                bridge_path = slice_dir / "umls_bridge_facts.pl"
            bridge = load_umls_bridge_facts(bridge_path)
            self._profile_manifest = manifest
            self._profile_paths = profile_paths
            self._profile_prompt_supplement = supplement
            self._profile_known_predicates = canonical_predicate_signatures(manifest)
            self._profile_predicate_contracts = semantic_ir_predicate_contracts(manifest)
            self._profile_concepts = concepts
            self._profile_umls_bridge = bridge
            self._profile_semantic_ir_context = semantic_ir_profile_context(
                manifest=manifest,
                concepts=concepts,
                umls_bridge=bridge,
            )
        except Exception as exc:
            self._profile_load_error = str(exc)

    def _compose_profile_prompt_guide(self, base_prompt_text: str) -> str:
        base = str(base_prompt_text or "").strip()
        if self._active_profile != "medical@v0":
            return base
        if not self._profile_manifest:
            return base
        return build_medical_profile_guide(
            shared_prompt=base,
            supplement=self._profile_prompt_supplement,
            concepts=self._profile_concepts,
            umls_bridge=self._profile_umls_bridge,
            known_predicates=self._profile_known_predicates,
        )

    def _apply_active_profile_parse_guard(
        self,
        *,
        parsed: dict[str, Any],
        utterance: str,
        profile_id: str = "",
    ) -> dict[str, Any]:
        effective_profile = str(profile_id or self._active_profile or "").strip()
        if effective_profile == "medical@v0":
            guarded = sanitize_medical_parse_for_clarification(parsed, utterance=utterance)
            guarded = sanitize_medical_parse_for_bridge(
                guarded if isinstance(guarded, dict) else parsed,
                utterance=utterance,
                bridge=self._profile_umls_bridge,
            )
            return guarded if isinstance(guarded, dict) else parsed
        return parsed

    def _load_compiler_prompt(self) -> None:
        if not self._compiler_prompt_enabled:
            self._compiler_prompt_text = self._compose_profile_prompt_guide("")
            self._compiler_prompt_loaded = True
            self._compiler_prompt_load_error = ""
            return
        try:
            base_prompt_text = self._compiler_prompt_path.read_text(encoding="utf-8")
            self._compiler_prompt_text = self._compose_profile_prompt_guide(base_prompt_text)
            self._compiler_prompt_loaded = bool(self._compiler_prompt_text.strip())
            self._compiler_prompt_load_error = ""
        except Exception as exc:
            self._compiler_prompt_text = ""
            self._compiler_prompt_loaded = False
            self._compiler_prompt_load_error = str(exc)

    def _load_freethinker_prompt(self) -> None:
        try:
            self._freethinker_prompt_text = self._freethinker_prompt_path.read_text(encoding="utf-8")
            self._freethinker_prompt_loaded = bool(self._freethinker_prompt_text.strip())
            self._freethinker_prompt_load_error = ""
        except Exception as exc:
            self._freethinker_prompt_text = ""
            self._freethinker_prompt_loaded = False
            self._freethinker_prompt_load_error = str(exc)

    def _load_registry_signatures(self) -> set[tuple[str, int]]:
        path = REPO_ROOT / "modelfiles" / "predicate_registry.json"
        signatures: set[tuple[str, int]] = set()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        rows = payload.get("canonical_predicates", []) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            name = self._atomize_name(row.get("name", ""))
            try:
                arity = int(row.get("arity", -1))
            except Exception:
                arity = -1
            if name and arity >= 0:
                signatures.add((name, arity))
        for signature in self._profile_known_predicates:
            match = re.match(r"^([a-z_][a-z0-9_]*)/(\d+)$", str(signature or "").strip())
            if not match:
                continue
            signatures.add((match.group(1), int(match.group(2))))
        return signatures

    def _clone_trace_payload(self, value: Any) -> Any:
        try:
            return deepcopy(value)
        except Exception:
            return value

    def _trace_step(self, *, name: str, before: Any, after: Any, summary: str) -> dict[str, Any]:
        return {
            "name": name,
            "applied": before != after,
            "summary": summary,
        }

    def _summarize_prethink_trace(self, trace: dict[str, Any]) -> dict[str, Any]:
        source = str(trace.get("source", "unknown")).strip() or "unknown"
        rescues = [
            str(item.get("name", "")).strip()
            for item in trace.get("rescues", [])
            if isinstance(item, dict) and bool(item.get("applied"))
        ]
        if rescues:
            overall = f"prethink={source}; adjusted via {', '.join(rescues)}"
        elif source == "primary":
            overall = "prethink=primary; raw routing packet accepted"
        elif source == "fallback_classifier":
            overall = "prethink=fallback_classifier; compact classifier supplied routing"
        elif source == "heuristic":
            overall = "prethink=heuristic; model compiler was bypassed"
        elif source == "external_or_stubbed":
            overall = "prethink=external_or_stubbed; trace synthesized from final packet"
        elif source == "failed":
            overall = "prethink=failed; compiler did not produce a valid routing packet"
        else:
            overall = f"prethink={source}"
        return {
            "source": source,
            "rescues": rescues,
            "overall": overall,
        }

    def _summarize_parse_trace(self, trace: dict[str, Any]) -> dict[str, Any]:
        rescues = [
            str(item.get("name", "")).strip()
            for item in trace.get("rescues", [])
            if isinstance(item, dict) and bool(item.get("applied"))
        ]
        validation_errors = list(trace.get("validation_errors", []))
        raw_matches_admitted = bool(trace.get("raw_matches_admitted", False))
        if validation_errors:
            overall = "parse=failed validation; see validation_errors"
        elif rescues:
            overall = f"parse adjusted via {', '.join(rescues)}"
        elif raw_matches_admitted:
            overall = "parse raw output admitted unchanged"
        else:
            overall = "parse normalized without additional rescue"
        return {
            "rescues": rescues,
            "raw_matches_admitted": raw_matches_admitted,
            "validation_error_count": len(validation_errors),
            "overall": overall,
        }

    def _build_freethinker_trace(
        self,
        *,
        utterance: str,
        action: str,
        reason: str,
        used: bool = False,
        confidence: float = 0.0,
        grounding: str = "",
        proposed_answer: str = "",
        proposed_question: str = "",
        notes: str = "",
        prompt_text: str = "",
        response_text: str = "",
        parsed: dict[str, Any] | None = None,
        context_pack: dict[str, Any] | None = None,
        error: str = "",
        decision_action: str = "",
    ) -> dict[str, Any]:
        action_clean = str(action or "skipped").strip().lower() or "skipped"
        reason_clean = str(reason or "").strip()
        grounding_clean = str(grounding or "").strip()
        trace = {
            "utterance": utterance,
            "policy": self._freethinker_resolution_policy,
            "used": bool(used),
            "action": action_clean,
            "reason": reason_clean,
            "confidence": _clip_01(confidence, 0.0),
            "grounding": grounding_clean,
            "proposed_answer": str(proposed_answer or "").strip(),
            "proposed_question": str(proposed_question or "").strip(),
            "notes": str(notes or "").strip(),
            "model": self._freethinker_model,
            "backend": self._freethinker_backend,
            "base_url": self._freethinker_base_url,
            "context_length": self._freethinker_context_length,
            "temperature": self._freethinker_temperature,
            "thinking": bool(self._freethinker_thinking),
            "prompt_path": str(self._freethinker_prompt_path),
            "prompt_loaded": bool(self._freethinker_prompt_loaded),
            "prompt_error": str(self._freethinker_prompt_load_error or "").strip(),
            "prompt_text": str(prompt_text or ""),
            "response_text": str(response_text or ""),
            "parsed": self._clone_trace_payload(parsed) if isinstance(parsed, dict) else None,
            "context_pack": self._clone_trace_payload(context_pack) if isinstance(context_pack, dict) else None,
            "error": str(error or "").strip(),
            "decision_action": str(decision_action or "").strip(),
        }
        trace["summary"] = self._summarize_freethinker_trace(trace)
        return trace

    def _summarize_freethinker_trace(self, trace: dict[str, Any]) -> dict[str, Any]:
        policy = _normalize_freethinker_resolution_policy(trace.get("policy"), "off")
        used = bool(trace.get("used", False))
        action = str(trace.get("action", "")).strip().lower() or "skipped"
        reason = str(trace.get("reason", "")).strip()
        grounding = str(trace.get("grounding", "")).strip()
        if policy == "off":
            overall = "freethinker=off"
        elif not used:
            suffix = f" ({reason})" if reason else ""
            overall = f"freethinker=idle{suffix}"
        elif grounding:
            overall = f"freethinker={action} via {grounding}"
        else:
            overall = f"freethinker={action}"
        return {
            "policy": policy,
            "used": used,
            "action": action,
            "grounding": grounding,
            "overall": overall,
        }

    def _summarize_compiler_trace(
        self,
        *,
        prethink_trace: dict[str, Any] | None,
        parse_trace: dict[str, Any] | None,
        freethinker_trace: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        prethink_summary = (
            dict(prethink_trace.get("summary", {}))
            if isinstance(prethink_trace, dict) and isinstance(prethink_trace.get("summary"), dict)
            else {}
        )
        freethinker_summary = (
            dict(freethinker_trace.get("summary", {}))
            if isinstance(freethinker_trace, dict) and isinstance(freethinker_trace.get("summary"), dict)
            else {}
        )
        parse_summary = (
            dict(parse_trace.get("summary", {}))
            if isinstance(parse_trace, dict) and isinstance(parse_trace.get("summary"), dict)
            else {}
        )
        parts = [
            str(prethink_summary.get("overall", "")).strip(),
            str(freethinker_summary.get("overall", "")).strip(),
            str(parse_summary.get("overall", "")).strip(),
        ]
        overall = "; ".join(part for part in parts if part)
        if not overall:
            overall = "No compiler trace captured."
        return {
            "overall": overall,
            "prethink_source": str(prethink_summary.get("source", "")).strip(),
            "freethinker_policy": str(freethinker_summary.get("policy", "")).strip(),
            "freethinker_action": str(freethinker_summary.get("action", "")).strip(),
            "parse_rescues": list(parse_summary.get("rescues", [])),
        }

    def _kb_snapshot_clauses(self, limit: int = 24) -> list[str]:
        runtime = getattr(self, "_runtime", None)
        engine = getattr(runtime, "engine", None) if runtime is not None else None
        raw_clauses = getattr(engine, "clauses", []) if engine is not None else []
        if not isinstance(raw_clauses, list):
            return []
        snapshot: list[str] = []
        seen: set[str] = set()
        for row in reversed(raw_clauses):
            text = str(row).strip()
            if not text:
                continue
            if not text.endswith("."):
                text = f"{text}."
            if text in seen:
                continue
            seen.add(text)
            snapshot.append(text)
            if len(snapshot) >= max(1, int(limit or 24)):
                break
        snapshot.reverse()
        return snapshot

    def _extract_entities_from_parse(self, parsed: dict[str, Any] | None) -> list[str]:
        if not isinstance(parsed, dict):
            return []
        components = parsed.get("components", {}) if isinstance(parsed.get("components"), dict) else {}
        atoms = [str(item).strip() for item in components.get("atoms", []) if str(item).strip()]
        blocked = {"he", "she", "they", "it", "him", "her", "them", "his", "hers", "their", "person", "patient"}
        entities: list[str] = []
        for atom in atoms:
            if atom.lower() in blocked:
                continue
            entities = self._append_unique(entities, atom)
        return entities

    def _remember_turn_outcome(
        self,
        *,
        utterance: str,
        front_door: dict[str, Any],
        execution: dict[str, Any],
    ) -> None:
        status = str(execution.get("status", "")).strip().lower()
        if status not in {"success", "no_results"}:
            return
        parse = execution.get("parse", {}) if isinstance(execution.get("parse"), dict) else {}
        operations = execution.get("operations", []) if isinstance(execution.get("operations"), list) else []
        entities = self._extract_entities_from_parse(parse)
        operation_preview: list[str] = []
        for op in operations:
            if not isinstance(op, dict):
                continue
            tool = str(op.get("tool", "")).strip()
            clause = str(op.get("clause", "") or op.get("query", "")).strip()
            if tool and clause:
                operation_preview.append(f"{tool}: {clause}")
            elif tool:
                operation_preview.append(tool)
            if tool in {"assert_fact", "assert_rule", "retract_fact"}:
                result = op.get("result", {}) if isinstance(op.get("result"), dict) else {}
                if str(result.get("status", "")).strip() == "success" and clause:
                    if clause not in self._recent_committed_logic:
                        self._recent_committed_logic.append(clause)
        self._recent_committed_logic = self._recent_committed_logic[-6:]

        entry = {
            "utterance": utterance,
            "route": str(front_door.get("route", "")).strip(),
            "intent": str(front_door.get("compiler_intent", "")).strip(),
            "entities": entities[:8],
            "name_mentions": self._name_mentions_for_freethinker(utterance=utterance)[:4],
            "operations": operation_preview[:6],
            "query": str(((execution.get("query_result") or {}) if isinstance(execution.get("query_result"), dict) else {}).get("prolog_query", "")).strip(),
        }
        self._recent_accepted_turns.append(entry)
        self._recent_accepted_turns = self._recent_accepted_turns[-4:]

    def _active_entities_for_freethinker(
        self,
        *,
        utterance: str,
        front_door: dict[str, Any],
    ) -> list[str]:
        entities: list[str] = []
        coreference = self._build_coreference_hint(utterance)
        for binding in coreference.get("pronoun_bindings", []):
            if not isinstance(binding, dict):
                continue
            for item in binding.get("effective_entities", []):
                entities = self._append_unique(entities, str(item).strip())
        pending = self._pending_prethink or {}
        for item in pending.get("segments", []):
            if not isinstance(item, dict):
                continue
            for token in self._tokenize_words(str(item.get("text", "")).strip()):
                if self._is_name_token(token):
                    entities = self._append_unique(entities, token)
        for turn in self._recent_accepted_turns[-4:]:
            if not isinstance(turn, dict):
                continue
            for item in turn.get("entities", []):
                entities = self._append_unique(entities, str(item).strip())
        return entities[:8]

    def _name_mentions_for_freethinker(self, *, utterance: str) -> list[str]:
        names: list[str] = []
        for token in self._tokenize_words(utterance):
            if self._is_name_token(token):
                names = self._append_unique(names, token)
        return names

    def _recent_name_candidates_for_freethinker(self, context_pack: dict[str, Any]) -> list[str]:
        if not isinstance(context_pack, dict):
            return []
        names: list[str] = []
        for turn in context_pack.get("recent_accepted_turns", []):
            if not isinstance(turn, dict):
                continue
            for item in turn.get("name_mentions", []):
                names = self._append_unique(names, str(item).strip())
            if not names:
                names = self._append_unique(
                    names,
                    *self._name_mentions_for_freethinker(utterance=str(turn.get("utterance", "")).strip()),
                )
        return names[:4]

    def _build_freethinker_context_pack(
        self,
        *,
        utterance: str,
        front_door: dict[str, Any],
    ) -> dict[str, Any]:
        pending = self._pending_prethink or {}
        recent_turns = [self._clone_trace_payload(turn) for turn in self._recent_accepted_turns[-4:]]
        committed_logic = [str(item).strip() for item in self._recent_committed_logic[-6:] if str(item).strip()]
        clarification_question = str(front_door.get("clarification_question", "")).strip()
        clarification_reason = ""
        reasons = front_door.get("reasons", [])
        if isinstance(reasons, list) and reasons:
            clarification_reason = str(reasons[0]).strip()
        current_parse_signals = {
            "route": str(front_door.get("route", "")).strip(),
            "compiler_intent": str(front_door.get("compiler_intent", "")).strip(),
            "ambiguity_score": float(front_door.get("ambiguity_score", 0.0) or 0.0),
            "looks_like_query": bool(front_door.get("looks_like_query", False)),
            "looks_like_write": bool(front_door.get("looks_like_write", False)),
        }
        pending_transcript = {}
        if pending:
            pending_transcript = {
                "clarification_question": str(pending.get("clarification_question", "")).strip(),
                "clarification_answer": str(pending.get("clarification_answer", "")).strip(),
                "clarification_required_before_query": bool(
                    pending.get("clarification_required_before_query", False)
                ),
            }
        return {
            "prethink_id": str(front_door.get("prethink_id", "")).strip(),
            "resolution_policy": self._freethinker_resolution_policy,
            "current_utterance": utterance,
            "compiler_intent": str(front_door.get("compiler_intent", "")).strip(),
            "compiler_uncertainty_score": float(front_door.get("ambiguity_score", 0.0) or 0.0),
            "clarification_question": clarification_question,
            "clarification_reason": clarification_reason,
            "current_parse_signals": current_parse_signals,
            "pending_clarification_transcript": pending_transcript,
            "recent_accepted_turns": recent_turns,
            "recent_committed_logic": committed_logic,
            "active_entities": self._active_entities_for_freethinker(utterance=utterance, front_door=front_door),
            "small_kb_snapshot": self._kb_snapshot_clauses(limit=24),
            "source_of_truth_note": "Only the deterministic Prolog KB is authoritative. Resolve reference conservatively.",
        }

    def _build_freethinker_prompt(self, *, utterance: str, context_pack: dict[str, Any]) -> str:
        sections = ["/no_think"]
        if self._freethinker_prompt_text.strip():
            sections.append(self._freethinker_prompt_text.strip())
        sections.append(
            "FREETHINKER_CONTEXT_JSON:\n"
            + json.dumps(context_pack, ensure_ascii=True, indent=2)
        )
        sections.append(f"CURRENT_UTTERANCE:\n{utterance}")
        return "\n\n".join(section for section in sections if section.strip())

    def _normalize_freethinker_decision(self, parsed: dict[str, Any]) -> dict[str, Any]:
        allowed_actions = {"resolve_from_context", "ask_user_this", "abstain"}
        allowed_grounding = {
            "pending_clarification",
            "recent_turn",
            "kb_clause",
            "active_entities",
            "multi_source",
            "weak_inference",
            "none",
        }
        action = str(parsed.get("action", "")).strip().lower()
        if action not in allowed_actions:
            action = "abstain"
        grounding = str(parsed.get("grounding", "")).strip().lower()
        if grounding not in allowed_grounding:
            grounding = "none"
        confidence = _clip_01(parsed.get("confidence"), 0.0)
        proposed_answer = str(parsed.get("proposed_answer", "")).strip()
        proposed_question = str(parsed.get("proposed_question", "")).strip()
        notes = str(parsed.get("notes", "")).strip()
        if action != "resolve_from_context":
            proposed_answer = ""
        if action != "ask_user_this":
            proposed_question = ""
        return {
            "action": action,
            "confidence": confidence,
            "grounding": grounding,
            "proposed_answer": proposed_answer,
            "proposed_question": proposed_question,
            "notes": notes,
        }

    def _freethinker_confirmation_question(self, answer: str, fallback: str) -> str:
        proposed = str(answer or "").strip()
        if proposed:
            return f'Do you mean "{proposed}"?'
        return str(fallback or "").strip()

    def _freethinker_specific_question(
        self,
        *,
        utterance: str,
        proposed_question: str,
        context_pack: dict[str, Any] | None,
    ) -> str:
        question = str(proposed_question or "").strip()
        if not question:
            return ""
        lower = question.lower()
        pronoun_match = re.search(r"'(he|she|they|him|her|them)'", question, re.IGNORECASE)
        if not pronoun_match:
            return question
        if not (lower.startswith("who does ") and "refer to" in lower):
            return question
        candidates = self._recent_name_candidates_for_freethinker(context_pack or {})
        if len(candidates) != 1:
            return question
        pronoun = pronoun_match.group(1).lower()
        candidate = candidates[0]
        return f"Do you mean {candidate} when you say '{pronoun}'?"

    def _freethinker_can_auto_resolve(self, *, policy: str, confidence: float, grounding: str) -> bool:
        if grounding in {"weak_inference", "none"}:
            return False
        threshold = 0.9 if policy == "grounded_reference" else 0.78
        return confidence >= threshold

    def _apply_freethinker_front_door(
        self,
        *,
        front_door: dict[str, Any],
        freethinker_trace: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], str]:
        updated = dict(front_door)
        if not isinstance(freethinker_trace, dict):
            return updated, ""
        effective_question = str(freethinker_trace.get("effective_question", "")).strip()
        effective_answer = str(freethinker_trace.get("effective_answer", "")).strip()
        action = str(freethinker_trace.get("action", "")).strip().lower()
        reasons = [str(item).strip() for item in updated.get("reasons", []) if str(item).strip()]

        if effective_question:
            updated["clarification_question"] = effective_question
            reasons = self._append_unique(reasons, "freethinker_question_refined")
        if action == "resolve_from_context" and effective_answer:
            updated["needs_clarification"] = False
            updated["clarification_question"] = ""
            reasons = self._append_unique(reasons, "freethinker_resolved_from_context")
        updated["reasons"] = reasons

        pending = self._pending_prethink
        if pending is not None:
            expected_id = str(pending.get("prethink_id", "")).strip()
            actual_id = str(updated.get("prethink_id", "")).strip()
            if expected_id and actual_id and expected_id == actual_id:
                if effective_question:
                    pending["clarification_question"] = effective_question
                if action == "resolve_from_context" and effective_answer:
                    pending["clarification_required_before_query"] = False
                    pending["clarification_answer"] = effective_answer
        return updated, effective_answer

    def _ensure_prethink_trace(
        self,
        *,
        utterance: str,
        compiled: dict[str, Any] | None,
        compile_error: str,
        packet: dict[str, Any] | None,
    ) -> dict[str, Any]:
        trace = self._clone_trace_payload(self._last_prethink_trace)
        if not isinstance(trace, dict) or str(trace.get("utterance", "")).strip() != utterance:
            if self._compiler_mode == "heuristic" and compiled is None:
                source = "heuristic"
            elif compiled is None:
                source = "failed"
            else:
                source = "external_or_stubbed"
            trace = {
                "utterance": utterance,
                "source": source,
                "compiler_mode": self._compiler_mode,
                "model": self._compiler_model,
                "prompt_path": str(self._compiler_prompt_path) if self._compiler_prompt_enabled else "",
                "primary": {
                    "prompt_text": "",
                    "raw_message": "",
                    "reasoning": "",
                    "parsed": None,
                    "normalized_before_sanitize": None,
                    "final_normalized": self._clone_trace_payload(compiled),
                    "error": str(compile_error or "").strip(),
                },
                "fallback": {
                    "used": False,
                    "prompt_text": "",
                    "raw_message": "",
                    "reasoning": "",
                    "parsed": None,
                    "normalized": None,
                    "error": "",
                },
                "rescues": [],
                "final": self._clone_trace_payload(compiled),
            }
        if isinstance(trace.get("primary"), dict) and not str(trace["primary"].get("prompt_text", "")).strip():
            trace["primary"]["prompt_text"] = self._build_compiler_prompt(utterance)
        trace["packet"] = self._clone_trace_payload(packet) if isinstance(packet, dict) else None
        trace["summary"] = self._summarize_prethink_trace(trace)
        return trace

    def _ensure_parse_trace(
        self,
        *,
        utterance: str,
        compiler_intent: str,
        clarification_answer: str,
        parsed: dict[str, Any] | None,
        error: str,
    ) -> dict[str, Any]:
        trace = self._clone_trace_payload(self._last_parse_trace)
        if not isinstance(trace, dict) or str(trace.get("utterance", "")).strip() != utterance:
            trace = {
                "utterance": utterance,
                "compiler_intent": compiler_intent,
                "clarification_answer": clarification_answer,
                "extractor": {
                    "prompt_text": "",
                    "raw_message": "",
                    "reasoning": "",
                    "parsed": None,
                    "error": str(error or "").strip(),
                },
                "normalized": None,
                "rescues": [],
                "admitted": self._clone_trace_payload(parsed),
                "validation_errors": [str(error or "").strip()] if error else [],
                "raw_matches_admitted": False,
            }
        trace["summary"] = self._summarize_parse_trace(trace)
        return trace

    def _atomize_name(self, raw: str) -> str:
        lowered = str(raw or "").strip().lower()
        if not lowered:
            return ""
        return re.sub(r"[^a-z0-9_]+", "_", lowered).strip("_")

    def _normalize_clarification_answer(
        self,
        *,
        clarification_question: str,
        clarification_answer: str,
    ) -> str:
        answer = str(clarification_answer or "").strip()
        question = str(clarification_question or "").strip()
        if not answer or not question:
            return answer

        owner_choices = re.findall(r"([A-Z][A-Za-z0-9_'-]*)'s brother", question)
        if owner_choices:
            lowered_answer = answer.lower()
            for owner in owner_choices:
                lowered_owner = owner.lower()
                accepted = {
                    lowered_owner,
                    f"{lowered_owner}'s",
                    f"{lowered_owner}s",
                }
                if lowered_answer in accepted:
                    return owner

        return answer

    def _extract_components_from_facts(self, facts: list[str]) -> dict[str, list[str]]:
        atoms: set[str] = set()
        variables: set[str] = set()
        predicates: set[str] = set()

        for clause in facts:
            text = str(clause or "").strip()
            match = re.match(r"^([a-z_][a-z0-9_]*)\((.*)\)\.$", text)
            if not match:
                continue
            predicates.add(match.group(1))
            raw_args = [part.strip() for part in match.group(2).split(",")]
            for arg in raw_args:
                if not arg:
                    continue
                if re.match(r"^[A-Z_][A-Za-z0-9_]*$", arg):
                    variables.add(arg)
                elif re.match(r"^[a-z_][a-z0-9_]*$", arg):
                    atoms.add(arg)

        return {
            "atoms": sorted(atoms),
            "variables": sorted(variables),
            "predicates": sorted(predicates),
        }

    def _split_fact_args(self, raw_args: str) -> list[str]:
        args: list[str] = []
        current: list[str] = []
        depth = 0
        for ch in str(raw_args or ""):
            if ch == "," and depth == 0:
                token = "".join(current).strip()
                if token:
                    args.append(token)
                current = []
                continue
            if ch == "(":
                depth += 1
            elif ch == ")" and depth > 0:
                depth -= 1
            current.append(ch)
        token = "".join(current).strip()
        if token:
            args.append(token)
        return args

    def _canonicalize_subject_prefixed_predicates(self, parsed: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(parsed, dict):
            return parsed
        if str(parsed.get("intent", "")).strip().lower() != "assert_fact":
            return parsed
        if not self._registry_signatures:
            return parsed

        facts = [str(item).strip() for item in parsed.get("facts", []) if str(item).strip()]
        if not facts:
            logic = str(parsed.get("logic_string", "")).strip()
            if logic:
                facts = [logic]
        if not facts:
            return parsed

        rewritten_facts: list[str] = []
        changed = False
        canonical_pairs: list[tuple[str, str]] = []
        for fact in facts:
            clause = fact if fact.endswith(".") else f"{fact}."
            match = re.match(r"^\s*([a-z_][a-z0-9_]*)\((.*)\)\.\s*$", clause)
            if not match:
                rewritten_facts.append(clause)
                continue
            predicate = match.group(1)
            args = self._split_fact_args(match.group(2))
            if not args:
                rewritten_facts.append(clause)
                continue
            first_atom = self._atomize_name(args[0])
            replacement = ""
            rewritten_args = list(args)
            prefix = f"{first_atom}_"
            if first_atom and predicate.startswith(prefix):
                candidate = predicate[len(prefix) :]
                if candidate and (candidate, len(args)) in self._registry_signatures:
                    replacement = candidate
            if not replacement and "_" in predicate:
                candidate, embedded_subject = predicate.rsplit("_", 1)
                embedded_subject = self._atomize_name(embedded_subject)
                if (
                    (predicate, len(args)) not in self._registry_signatures
                    and
                    candidate
                    and embedded_subject
                    and embedded_subject[:1].isalpha()
                    and (candidate, len(args) + 1) in self._registry_signatures
                    and embedded_subject.lower() not in {self._atomize_name(arg).lower() for arg in args if self._atomize_name(arg)}
                ):
                    replacement = candidate
                    rewritten_args = [embedded_subject, *args]
            if replacement:
                rewritten_facts.append(f"{replacement}({', '.join(rewritten_args)}).")
                changed = True
                canonical_pairs.append((predicate, replacement))
            else:
                rewritten_facts.append(clause)

        if not changed:
            return parsed

        parsed["facts"] = rewritten_facts
        parsed["logic_string"] = rewritten_facts[0] if len(rewritten_facts) == 1 else " ".join(rewritten_facts)
        parsed["rules"] = []
        parsed["queries"] = []
        parsed["components"] = self._extract_components_from_facts(rewritten_facts)
        parsed["ambiguities"] = []
        seen: set[str] = set()
        pairs: list[str] = []
        for before, after in canonical_pairs:
            label = f"{before}->{after}"
            if label not in seen:
                seen.add(label)
                pairs.append(label)
        parsed["rationale"] = "Subject-prefixed predicate canonicalized to registry form: " + ", ".join(pairs) + "."
        return parsed

    def _canonicalize_make_with_query(self, parsed: dict[str, Any], *, utterance: str) -> dict[str, Any]:
        if not isinstance(parsed, dict):
            return parsed
        if str(parsed.get("intent", "")).strip().lower() != "query":
            return parsed

        lowered = str(utterance or "").strip().lower()
        if not lowered:
            return parsed
        match = re.match(
            r"^\s*can\s+you\s+make\s+([a-z][a-z0-9_'-]*(?:\s+[a-z][a-z0-9_'-]*){0,3})\s+with\s+([a-z][a-z0-9_'-]*(?:\s+[a-z][a-z0-9_'-]*){0,3})\s*\?\s*$",
            lowered,
        )
        if not match:
            return parsed

        subject_atom = self._atomize_name(match.group(1))
        ingredient_atom = self._atomize_name(match.group(2))
        if not subject_atom or not ingredient_atom:
            return parsed

        query = f"made_with({subject_atom}, {ingredient_atom})."
        parsed["logic_string"] = query
        parsed["queries"] = [query]
        parsed["facts"] = []
        parsed["rules"] = []
        parsed["components"] = {
            "atoms": sorted({subject_atom, ingredient_atom}),
            "variables": [],
            "predicates": ["made_with"],
        }
        parsed["ambiguities"] = []
        parsed["needs_clarification"] = False
        parsed["clarification_question"] = ""
        parsed["clarification_reason"] = ""
        parsed["uncertainty_score"] = 0.05
        parsed["uncertainty_label"] = "low"
        parsed["rationale"] = (
            "Mapped capability wording onto the stored ingredient relation "
            f"made_with({subject_atom}, {ingredient_atom})."
        )
        return parsed

    def _augment_compound_family_facts(
        self,
        *,
        parsed: dict[str, Any],
        utterance: str,
        clarification_answer: str,
    ) -> dict[str, Any]:
        if not isinstance(parsed, dict):
            return parsed
        if str(parsed.get("intent", "")).strip().lower() != "assert_fact":
            return parsed

        facts = [str(item).strip() for item in parsed.get("facts", []) if str(item).strip()]
        if not facts:
            logic = str(parsed.get("logic_string", "")).strip()
            if logic:
                facts = [logic]

        normalized_facts: list[str] = []
        for fact in facts:
            clause = fact if fact.endswith(".") else f"{fact}."
            if clause not in normalized_facts:
                normalized_facts.append(clause)
        original_facts = list(normalized_facts)

        lowered = str(utterance or "").strip().lower()
        if not lowered:
            return parsed
        clar_atom = self._atomize_name(clarification_answer)

        def _resolve_brother_owner(owner_token: str) -> str:
            if owner_token in {"his", "her", "their"}:
                return clar_atom or owner_from_parent_block
            owner_match = re.match(r"^([a-z][a-z0-9_'-]*?)'?s$", owner_token)
            if owner_match:
                return self._atomize_name(owner_match.group(1))
            return ""

        parent_override_facts: list[str] = []
        owner_from_parent_block = ""
        parent_block = re.search(
            r"\b([a-z][a-z0-9_'-]*?)'?s\s+mom\s+and\s+dad\s+(?:is|are)\s+([a-z][a-z0-9_'-]*)\s+and\s+([a-z][a-z0-9_'-]*)\b",
            lowered,
        )
        if parent_block:
            owner_from_parent_block = self._atomize_name(parent_block.group(1))
            mom_atom = self._atomize_name(parent_block.group(2))
            dad_atom = self._atomize_name(parent_block.group(3))
            if owner_from_parent_block and mom_atom:
                fact = f"parent({mom_atom}, {owner_from_parent_block})."
                if fact not in parent_override_facts:
                    parent_override_facts.append(fact)
            if owner_from_parent_block and dad_atom:
                fact = f"parent({dad_atom}, {owner_from_parent_block})."
                if fact not in parent_override_facts:
                    parent_override_facts.append(fact)

        sibling_override_facts: list[str] = []
        sibling_block = re.search(
            r"\b((?:[a-z][a-z0-9_'-]*?)'?s|his|her|their)\s+brother\s+is\s+([a-z][a-z0-9_'-]*)\b",
            lowered,
        )
        if sibling_block:
            owner_token = sibling_block.group(1)
            sibling_atom = self._atomize_name(sibling_block.group(2))
            owner_atom = _resolve_brother_owner(owner_token)
            if owner_atom and sibling_atom:
                fact = f"brother({sibling_atom}, {owner_atom})."
                if fact not in sibling_override_facts:
                    sibling_override_facts.append(fact)

        sibling_location_override_facts: list[str] = []
        sibling_location_rationale = ""
        sibling_location_block = re.match(
            r"^\s*((?:[a-z][a-z0-9_'-]*?)'?s|his|her|their)\s+brother\s+is\s+in\s+([a-z][a-z0-9_'-]*(?:\s+[a-z][a-z0-9_'-]*){0,3})\.?\s*$",
            lowered,
            re.IGNORECASE,
        )
        if sibling_location_block:
            owner_token = str(sibling_location_block.group(1) or "").strip().lower()
            place_atom = self._atomize_name(sibling_location_block.group(2))
            owner_atom = _resolve_brother_owner(owner_token)
            if owner_atom and place_atom:
                sibling_atom = f"brother_of_{owner_atom}"
                sibling_location_override_facts = [
                    f"brother({sibling_atom}, {owner_atom}).",
                    f"lives_in({sibling_atom}, {place_atom}).",
                ]
                sibling_location_rationale = (
                    "Clarification resolved the owner of an unnamed brother, so the statement "
                    f"was normalized into brother({sibling_atom}, {owner_atom}) and "
                    f"lives_in({sibling_atom}, {place_atom})."
                )

        explicit_sibling_name_rationale = ""
        sibling_name_block = re.search(
            r"\b([a-z][a-z0-9_'-]*)\s+has\s+a\s+brother\s+and\s+his\s+brother'?s\s+name\s+is\s+([a-z][a-z0-9_'-]*)\b",
            lowered,
        )
        if sibling_name_block:
            owner_atom = self._atomize_name(sibling_name_block.group(1))
            sibling_atom = self._atomize_name(sibling_name_block.group(2))
            if owner_atom and sibling_atom:
                sibling_override_facts = [f"brother({sibling_atom}, {owner_atom})."]
                explicit_sibling_name_rationale = (
                    "Recognized an explicit sibling naming pattern and normalized it to "
                    f"brother({sibling_atom}, {owner_atom})."
                )

        inverse_possessive_override_facts: list[str] = []
        inverse_possessive_rationale = ""
        inverse_possessive = re.match(
            r"^\s*([a-z][a-z0-9_'-]*)\s+is\s+([a-z][a-z0-9_'-]*)'?s\s+([a-z][a-z0-9_'-]*(?:\s+[a-z][a-z0-9_'-]*){0,3})\.?\s*$",
            lowered,
            re.IGNORECASE,
        )
        if inverse_possessive:
            subject_atom = self._atomize_name(inverse_possessive.group(1))
            owner_atom = self._atomize_name(inverse_possessive.group(2))
            relation_atom = self._atomize_name(inverse_possessive.group(3))
            if subject_atom and owner_atom and relation_atom:
                fact = f"{relation_atom}({subject_atom}, {owner_atom})."
                inverse_possessive_override_facts.append(fact)
                inverse_possessive_rationale = (
                    "Recognized an inverse possessive relation and normalized it to "
                    f"{relation_atom}({subject_atom}, {owner_atom})."
                )

        if parent_override_facts:
            kept = [fact for fact in normalized_facts if not re.match(r"^parent\s*\(", fact)]
            normalized_facts = kept + parent_override_facts

        if sibling_override_facts:
            kept = [fact for fact in normalized_facts if not re.match(r"^brother\s*\(", fact)]
            normalized_facts = kept + sibling_override_facts

        if sibling_location_override_facts:
            normalized_facts = list(sibling_location_override_facts)

        if inverse_possessive_override_facts:
            kept: list[str] = []
            for fact in normalized_facts:
                parsed_name = ""
                match = re.match(r"^\s*([a-z_][a-z0-9_]*)\s*\(", fact)
                if match:
                    parsed_name = match.group(1)
                if parsed_name and fact not in inverse_possessive_override_facts:
                    continue
                kept.append(fact)
            normalized_facts = kept + [
                fact for fact in inverse_possessive_override_facts if fact not in kept
            ]

        if normalized_facts == original_facts or not normalized_facts:
            return parsed

        parsed["facts"] = normalized_facts
        parsed["logic_string"] = (
            normalized_facts[0] if len(normalized_facts) == 1 else " ".join(normalized_facts)
        )
        parsed["rules"] = []
        parsed["queries"] = []
        parsed["components"] = self._extract_components_from_facts(normalized_facts)
        if parent_override_facts and owner_from_parent_block:
            parent_atoms = [fact[len("parent(") : fact.rfind(",")] for fact in parent_override_facts if fact.startswith("parent(")]
            normalized_owner = owner_from_parent_block.replace("_", " ")
            normalized_parents = ", ".join(atom.replace("_", " ") for atom in parent_atoms)
            parsed["ambiguities"] = []
            parsed["rationale"] = (
                f"Recognized an explicit family bundle and normalized it to parent facts for {normalized_owner}: "
                f"{normalized_parents}."
            )
        elif sibling_override_facts and explicit_sibling_name_rationale:
            parsed["ambiguities"] = []
            parsed["rationale"] = explicit_sibling_name_rationale
        elif sibling_location_override_facts and sibling_location_rationale:
            parsed["ambiguities"] = []
            parsed["rationale"] = sibling_location_rationale
        elif inverse_possessive_override_facts and inverse_possessive_rationale:
            parsed["ambiguities"] = []
            parsed["rationale"] = inverse_possessive_rationale
        else:
            rationale = str(parsed.get("rationale", "")).strip()
            suffix = "Compound family statement expansion added deterministic companion facts."
            parsed["rationale"] = f"{rationale} {suffix}".strip() if rationale else suffix
        return parsed

    def _extract_explicit_with_correction(
        self,
        utterance: str,
    ) -> dict[str, str] | None:
        lowered = str(utterance or "").strip()
        if not lowered:
            return None
        match = re.match(
            r"^\s*(?:actually\s+no[, ]+)?(?P<subject>.+?)\s+is\s+with\s+(?P<new_holder>[a-z][a-z0-9_'-]*)\s+not\s+(?P<old_holder>[a-z][a-z0-9_'-]*)[.?!]?\s*$",
            lowered,
            re.IGNORECASE,
        )
        if not match:
            return None
        subject = str(match.group("subject") or "").strip(" ,")
        new_holder = str(match.group("new_holder") or "").strip()
        old_holder = str(match.group("old_holder") or "").strip()
        if not subject or not new_holder or not old_holder:
            return None
        return {
            "subject": subject,
            "new_holder": new_holder,
            "old_holder": old_holder,
        }

    def _extract_explicit_step_sequence(
        self,
        utterance: str,
    ) -> dict[str, Any] | None:
        text = str(utterance or "").strip()
        if not text:
            return None
        match = re.match(
            r"^\s*at\s+step\s+(?P<step>\d+)\s+(?P<entity>[a-z][a-z0-9_'-]*(?:\s+[a-z][a-z0-9_'-]*){0,3})\s+was\s+in\s+(?P<origin>[a-z0-9][a-z0-9_'-]*(?:\s+[a-z0-9][a-z0-9_'-]*){0,5})\s+and\s+later\s+moved\s+to\s+(?P<destination>[a-z0-9][a-z0-9_'-]*(?:\s+[a-z0-9][a-z0-9_'-]*){0,5})[.?!]?\s*$",
            text,
            re.IGNORECASE,
        )
        if not match:
            return None
        try:
            step = int(match.group("step"))
        except Exception:
            return None
        entity_atom = self._atomize_name(match.group("entity"))
        origin_atom = self._atomize_name(match.group("origin"))
        destination_atom = self._atomize_name(match.group("destination"))
        if step < 0 or not entity_atom or not origin_atom or not destination_atom:
            return None
        return {
            "step": step,
            "entity_atom": entity_atom,
            "origin_atom": origin_atom,
            "destination_atom": destination_atom,
        }

    def _extract_fact_clauses(self, parsed: dict[str, Any]) -> list[str]:
        clauses = [str(item).strip() for item in parsed.get("facts", []) if str(item).strip()]
        if not clauses:
            clause = str(parsed.get("logic_string", "")).strip()
            if clause:
                clauses = [clause]
        normalized: list[str] = []
        for clause in clauses:
            cleaned = clause if clause.endswith(".") else f"{clause}."
            if cleaned not in normalized:
                normalized.append(cleaned)
        return normalized

    def _rescue_explicit_with_correction(
        self,
        *,
        parsed: dict[str, Any],
        utterance: str,
        compiler_intent: str,
    ) -> dict[str, Any]:
        if not isinstance(parsed, dict):
            return parsed
        if str(compiler_intent or "").strip().lower() != "assert_fact":
            return parsed
        correction = self._extract_explicit_with_correction(utterance)
        if correction is None:
            return parsed

        subject = correction["subject"]
        new_holder = correction["new_holder"]
        old_holder = correction["old_holder"]
        new_parse, new_error = self._compile_shadow_parse(
            f"{subject} is with {new_holder}.",
            "assert_fact",
        )
        old_parse, old_error = self._compile_shadow_parse(
            f"{subject} is with {old_holder}.",
            "assert_fact",
        )
        if not isinstance(new_parse, dict) or not isinstance(old_parse, dict):
            return parsed
        if new_error or old_error:
            return parsed

        new_facts = self._extract_fact_clauses(new_parse)
        old_facts = self._extract_fact_clauses(old_parse)
        if not new_facts or not old_facts:
            return parsed

        rescued = self._clone_trace_payload(new_parse)
        rescued["correction_retract_clauses"] = old_facts
        rescued["needs_clarification"] = False
        rescued["clarification_question"] = ""
        rescued["clarification_reason"] = ""
        rescued["uncertainty_score"] = min(
            _clip_01(rescued.get("uncertainty_score"), 0.15),
            0.15,
        )
        rescued["uncertainty_label"] = "low"
        rescued["ambiguities"] = []
        rescued["rationale"] = (
            "Recognized an explicit holder correction and converted it into a "
            f"retract-old/assert-new state update for {self._atomize_name(subject)}."
        )
        return rescued

    def _rescue_explicit_step_sequence(
        self,
        *,
        parsed: dict[str, Any],
        utterance: str,
        compiler_intent: str,
    ) -> dict[str, Any]:
        if not isinstance(parsed, dict):
            return parsed
        if str(compiler_intent or "").strip().lower() != "assert_fact":
            return parsed
        sequence = self._extract_explicit_step_sequence(utterance)
        if sequence is None:
            return parsed

        step = int(sequence["step"])
        entity_atom = str(sequence["entity_atom"])
        origin_atom = str(sequence["origin_atom"])
        destination_atom = str(sequence["destination_atom"])
        facts = [
            f"at_step({step}, at({entity_atom}, {origin_atom})).",
            f"at_step({step + 1}, at({entity_atom}, {destination_atom})).",
        ]
        rescued = self._clone_trace_payload(parsed)
        rescued["intent"] = "assert_fact"
        rescued["facts"] = facts
        rescued["logic_string"] = " ".join(facts)
        rescued["rules"] = []
        rescued["queries"] = []
        rescued["components"] = self._extract_components_from_facts(facts)
        rescued["ambiguities"] = []
        rescued["needs_clarification"] = False
        rescued["clarification_question"] = ""
        rescued["clarification_reason"] = ""
        rescued["uncertainty_score"] = min(
            _clip_01(rescued.get("uncertainty_score"), 0.1),
            0.1,
        )
        rescued["uncertainty_label"] = "low"
        rescued["rationale"] = (
            "Recognized an explicit step sequence and normalized it into valid "
            "at_step(Integer, Fact) temporal wrappers."
        )
        return rescued

    def _compile_apply_parse(
        self,
        *,
        utterance: str,
        compiler_intent: str,
        clarification_question: str = "",
        clarification_answer: str = "",
    ) -> tuple[dict[str, Any] | None, str]:
        if self._semantic_ir_enabled:
            return self._compile_apply_parse_with_semantic_ir(
                utterance=utterance,
                compiler_intent=compiler_intent,
                clarification_question=clarification_question,
                clarification_answer=clarification_answer,
            )
        if not self._compiler_prompt_loaded:
            reason = self._compiler_prompt_load_error or "compiler prompt unavailable"
            return None, f"Compiler prompt not loaded: {reason}"
        self._last_parse_trace = {}

        effective = utterance
        if clarification_question or clarification_answer:
            effective = (
                f"{utterance}\n"
                f"Clarification question: {clarification_question}\n"
                f"Clarification answer: {clarification_answer}"
            ).strip()

        extraction_prompt = _build_extractor_prompt(
            effective,
            compiler_intent if compiler_intent in {"assert_fact", "assert_rule", "query", "retract", "other"} else "other",
            known_predicates=self._profile_known_predicates,
            prompt_guide=self._compiler_prompt_text,
        )
        trace = {
            "utterance": utterance,
            "effective_utterance": effective,
            "compiler_intent": compiler_intent,
            "clarification_answer": clarification_answer,
            "model": self._compiler_model,
            "prompt_path": str(self._compiler_prompt_path) if self._compiler_prompt_enabled else "",
            "extractor": {
                "prompt_text": extraction_prompt,
                "raw_message": "",
                "reasoning": "",
                "parsed": None,
                "error": "",
            },
            "normalized": None,
            "rescues": [],
            "admitted": None,
            "validation_errors": [],
            "raw_matches_admitted": False,
        }

        try:
            response = _call_model_prompt(
                backend=self._compiler_backend,
                base_url=self._compiler_base_url,
                model=self._compiler_model,
                prompt_text=extraction_prompt,
                context_length=self._compiler_context_length,
                timeout=self._compiler_timeout,
                api_key=self._compiler_api_key,
            )
        except Exception as exc:
            trace["extractor"]["error"] = f"Compiler parse call failed: {exc}"
            trace["validation_errors"] = [trace["extractor"]["error"]]
            trace["summary"] = self._summarize_parse_trace(trace)
            self._last_parse_trace = trace
            return None, f"Compiler parse call failed: {exc}"
        trace["extractor"]["raw_message"] = str(response.message or "")
        trace["extractor"]["reasoning"] = str(response.reasoning or "")

        parsed, _ = _parse_model_json(
            response,
            required_keys=["intent", "logic_string", "components", "confidence"],
        )
        if not isinstance(parsed, dict):
            trace["extractor"]["error"] = "Compiler parse payload was not valid JSON."
            trace["validation_errors"] = [trace["extractor"]["error"]]
            trace["summary"] = self._summarize_parse_trace(trace)
            self._last_parse_trace = trace
            return None, "Compiler parse payload was not valid JSON."
        raw_parsed = self._clone_trace_payload(parsed)
        trace["extractor"]["parsed"] = raw_parsed

        normalized = _normalize_clarification_fields(
            self._clone_trace_payload(parsed),
            utterance=effective,
            route=compiler_intent,
        )
        trace["normalized"] = self._clone_trace_payload(normalized)
        trace["rescues"].append(
            self._trace_step(
                name="clarification_fields_normalized",
                before=raw_parsed,
                after=normalized,
                summary="Normalized clarification fields onto the parse schema.",
            )
        )
        after_make_with = self._canonicalize_make_with_query(
            self._clone_trace_payload(normalized),
            utterance=utterance,
        )
        trace["rescues"].append(
            self._trace_step(
                name="make_with_query_canonicalization",
                before=normalized,
                after=after_make_with,
                summary="Mapped capability wording onto the stored ingredient relation.",
            )
        )
        family_input = self._clone_trace_payload(after_make_with)
        after_family = self._augment_compound_family_facts(
            parsed=family_input,
            utterance=utterance,
            clarification_answer=clarification_answer,
        )
        trace["rescues"].append(
            self._trace_step(
                name="compound_family_augmentation",
                before=after_make_with,
                after=after_family,
                summary="Expanded or corrected explicit family bundle statements.",
            )
        )
        correction_input = self._clone_trace_payload(after_family)
        after_correction = self._rescue_explicit_with_correction(
            parsed=correction_input,
            utterance=utterance,
            compiler_intent=compiler_intent,
        )
        trace["rescues"].append(
            self._trace_step(
                name="explicit_with_correction_rescue",
                before=after_family,
                after=after_correction,
                summary="Recovered explicit holder corrections into retract-old/assert-new updates.",
            )
        )
        step_sequence_input = self._clone_trace_payload(after_correction)
        after_step_sequence = self._rescue_explicit_step_sequence(
            parsed=step_sequence_input,
            utterance=utterance,
            compiler_intent=compiler_intent,
        )
        trace["rescues"].append(
            self._trace_step(
                name="explicit_step_sequence_rescue",
                before=after_correction,
                after=after_step_sequence,
                summary="Recovered explicit step-sequence narration into valid temporal wrappers.",
            )
        )
        subject_prefix_input = self._clone_trace_payload(after_step_sequence)
        after_subject_prefix = self._canonicalize_subject_prefixed_predicates(subject_prefix_input)
        trace["rescues"].append(
            self._trace_step(
                name="subject_prefixed_predicate_canonicalization",
                before=after_step_sequence,
                after=after_subject_prefix,
                summary="Canonicalized subject-prefixed predicates into registry form.",
            )
        )
        profile_guard_input = self._clone_trace_payload(after_subject_prefix)
        after_medical_clarification_rescue = profile_guard_input
        if self._active_profile == "medical@v0":
            after_medical_clarification_rescue = rescue_medical_clarified_lab_result(
                profile_guard_input,
                utterance=utterance,
                clarification_answer=clarification_answer,
            )
        trace["rescues"].append(
            self._trace_step(
                name="medical_clarified_lab_result_rescue",
                before=profile_guard_input,
                after=after_medical_clarification_rescue,
                summary="Recovered clarified medical lab-result restatements into bounded profile facts.",
            )
        )
        admitted = self._apply_active_profile_parse_guard(
            parsed=after_medical_clarification_rescue,
            utterance=effective,
        )
        trace["rescues"].append(
            self._trace_step(
                name="active_profile_parse_guard",
                before=after_medical_clarification_rescue,
                after=admitted,
                summary="Applied active profile clarification and argument guardrails.",
            )
        )
        trace["admitted"] = self._clone_trace_payload(admitted)
        trace["raw_matches_admitted"] = raw_parsed == admitted
        ok, errors = _validate_parsed(admitted)
        trace["validation_errors"] = list(errors)
        trace["summary"] = self._summarize_parse_trace(trace)
        self._last_parse_trace = trace
        if not ok:
            return None, "; ".join(errors)
        return admitted, ""

    def _semantic_ir_call_config(self) -> SemanticIRCallConfig:
        return SemanticIRCallConfig(
            backend=self._compiler_backend,
            base_url=self._compiler_base_url,
            model=self._semantic_ir_model,
            context_length=self._semantic_ir_context_length,
            timeout=self._semantic_ir_timeout,
            temperature=self._semantic_ir_temperature,
            top_p=self._semantic_ir_top_p,
            top_k=self._semantic_ir_top_k,
            think_enabled=self._semantic_ir_thinking,
        )

    def _semantic_ir_selected_profile_for_utterance(
        self,
        utterance: str,
        *,
        context: list[str] | None = None,
    ) -> str:
        if self._active_profile == "auto":
            selection = select_domain_profile(
                utterance,
                context=self._semantic_ir_context(context),
                catalog=self._domain_profile_catalog,
            )
            self._last_semantic_ir_profile_selection = self._clone_trace_payload(selection)
            selected = str(selection.get("profile_id", "general")).strip() if isinstance(selection, dict) else "general"
            self._last_semantic_ir_selected_profile = "" if selected == "general" else selected
            return self._last_semantic_ir_selected_profile
        self._last_semantic_ir_profile_selection = {
            "profile_id": self._active_profile,
            "score": None,
            "runner_up_score": None,
            "reasons": ["active_profile explicitly configured"],
        }
        self._last_semantic_ir_selected_profile = "" if self._active_profile == "general" else self._active_profile
        return self._last_semantic_ir_selected_profile

    def _profile_contracts_for(self, profile_id: str) -> list[dict[str, Any]]:
        if profile_id == "medical@v0":
            return self._clone_trace_payload(self._profile_predicate_contracts)
        profile = load_profile_package(profile_id, self._domain_profile_catalog)
        return profile_package_contracts(profile) if profile else []

    def _profile_context_for(self, profile_id: str) -> list[str]:
        if profile_id == "medical@v0":
            return [str(item).strip() for item in self._profile_semantic_ir_context if str(item).strip()]
        profile = load_profile_package(profile_id, self._domain_profile_catalog)
        return profile_package_context(profile) if profile else []

    def _semantic_ir_allowed_predicates(self, profile_id: str = "") -> list[str]:
        profile_contracts = self._profile_contracts_for(profile_id) if profile_id else []
        if profile_contracts:
            signatures = [str(row.get("signature", "")).strip() for row in profile_contracts if str(row.get("signature", "")).strip()]
            if signatures:
                return signatures
        signatures = sorted(self._registry_signatures)
        return [f"{name}/{arity}" for name, arity in signatures]

    def _semantic_ir_predicate_contracts(self, profile_id: str = "") -> list[dict[str, Any]]:
        return self._profile_contracts_for(profile_id) if profile_id else []

    def _semantic_ir_domain_context(self, profile_id: str = "") -> list[str]:
        return self._profile_context_for(profile_id) if profile_id else []

    def _semantic_ir_available_domain_profiles(self) -> list[dict[str, Any]]:
        return self._clone_trace_payload(self._domain_profile_roster)

    def _semantic_ir_context(self, extra_context: list[str] | None = None) -> list[str]:
        context: list[str] = []
        for item in extra_context or []:
            text = str(item).strip()
            if text:
                context.append(text)
        for clause in self._recent_committed_logic[-16:]:
            text = str(clause).strip()
            if text:
                context.append(text)
        pending = self._pending_prethink or {}
        pending_utterance = str(pending.get("utterance", "")).strip()
        if pending_utterance:
            context.append(f"pending_utterance: {pending_utterance}")
        return context

    def _semantic_ir_context_terms(self, *, utterance: str, context: list[str]) -> set[str]:
        terms: set[str] = set()
        for raw in [utterance, *context]:
            for token in self._tokenize_words(str(raw)):
                normalized = re.sub(r"[^a-z0-9_]+", "_", token.strip().lower()).strip("_")
                if len(normalized) >= 2:
                    terms.add(normalized)
                    terms.update(part for part in normalized.split("_") if len(part) >= 2)
        return terms

    @staticmethod
    def _clause_terms(predicate: str, args: list[str]) -> set[str]:
        terms: set[str] = {str(predicate).strip().lower()}
        for arg in args:
            normalized = re.sub(r"[^a-z0-9_]+", "_", str(arg).strip().lower()).strip("_")
            if not normalized:
                continue
            terms.add(normalized)
            terms.update(part for part in normalized.split("_") if len(part) >= 2)
        return terms

    def _semantic_ir_kb_context_pack(
        self,
        *,
        utterance: str,
        semantic_context: list[str],
        selected_profile: str,
        allowed_predicates: list[str],
    ) -> dict[str, Any]:
        fact_rows: list[dict[str, Any]] = []
        for clause in self._runtime_direct_fact_clauses():
            parsed = self._single_fact_call(clause)
            if parsed is None:
                continue
            predicate, args, normalized = parsed
            fact_rows.append(
                {
                    "clause": normalized,
                    "predicate": predicate,
                    "arity": len(args),
                    "args": args,
                    "terms": sorted(self._clause_terms(predicate, args)),
                }
            )
        terms = self._semantic_ir_context_terms(utterance=utterance, context=semantic_context)
        allowed_names = {
            str(item).split("/", 1)[0].strip().lower()
            for item in allowed_predicates
            if str(item).strip()
        }
        relevant: list[dict[str, Any]] = []
        for row in fact_rows:
            row_terms = set(row.get("terms", []))
            predicate = str(row.get("predicate", "")).strip().lower()
            if (row_terms & terms) or (predicate in allowed_names and predicate in terms):
                relevant.append(row)
        if not relevant and fact_rows:
            relevant = fact_rows[-8:]
        relevant = relevant[-24:]
        recent = [str(item).strip() for item in self._recent_committed_logic[-12:] if str(item).strip()]
        snapshot = self._kb_snapshot_clauses(limit=12)
        entity_candidates: list[str] = []
        for row in relevant:
            for arg in row.get("args", []):
                text = str(arg).strip()
                if text and text not in entity_candidates:
                    entity_candidates.append(text)
        current_state_candidates = [
            row["clause"]
            for row in relevant
            if self._is_likely_functional_current_state_predicate(
                str(row.get("predicate", "")),
                int(row.get("arity", 0) or 0),
            )
        ][:12]
        current_state_subject_candidates: list[dict[str, Any]] = []
        for row in relevant:
            predicate = str(row.get("predicate", "")).strip()
            arity = int(row.get("arity", 0) or 0)
            args = row.get("args", []) if isinstance(row.get("args"), list) else []
            if not args or not self._is_likely_functional_current_state_predicate(predicate, arity):
                continue
            subject = str(args[0]).strip()
            if not subject:
                continue
            candidate = {
                "entity": subject,
                "role": "current_state_subject",
                "predicate": f"{predicate}/{arity}",
                "source_clause": str(row.get("clause", "")).strip(),
            }
            if candidate not in current_state_subject_candidates:
                current_state_subject_candidates.append(candidate)
        return {
            "version": "semantic_ir_context_pack_v1",
            "authority": "context_only_runtime_kb_remains_authoritative",
            "active_profile": selected_profile or "general",
            "manifest": {
                "total_direct_fact_clauses": len(fact_rows),
                "relevant_clause_count": len(relevant),
                "recent_commit_count": len(recent),
                "snapshot_count": len(snapshot),
                "retrieval_terms": sorted(terms)[:48],
                "context_budget_note": "Compact symbolic retrieval for 16K context; not a full KB dump.",
            },
            "relevant_clauses": [row["clause"] for row in relevant],
            "current_state_candidates": current_state_candidates,
            "current_state_subject_candidates": current_state_subject_candidates[:16],
            "entity_candidates": entity_candidates[:32],
            "recent_committed_logic": recent,
            "small_kb_snapshot": snapshot,
            "instructions": [
                "Use exact KB clauses to resolve references, corrections, and conflict pressure.",
                "Do not copy KB clauses into candidate_operations unless the current utterance explicitly changes them.",
                "Use truth_maintenance.support_links/conflicts/retraction_plan to cite KB context.",
            ],
        }

    def _compile_semantic_ir(
        self,
        utterance: str,
        *,
        context: list[str] | None = None,
        allowed_predicates_override: list[str] | None = None,
        predicate_contracts_override: list[dict[str, Any]] | None = None,
    ) -> tuple[dict[str, Any] | None, str]:
        selected_profile = self._semantic_ir_selected_profile_for_utterance(utterance, context=context)
        domain = selected_profile or "runtime"
        semantic_context = self._semantic_ir_context(context)
        domain_context = self._semantic_ir_domain_context(selected_profile)
        allowed_predicates = (
            list(allowed_predicates_override)
            if allowed_predicates_override is not None
            else self._semantic_ir_allowed_predicates(selected_profile)
        )
        predicate_contracts = (
            list(predicate_contracts_override)
            if predicate_contracts_override is not None
            else self._semantic_ir_predicate_contracts(selected_profile)
        )
        kb_context_pack = self._semantic_ir_kb_context_pack(
            utterance=utterance,
            semantic_context=semantic_context,
            selected_profile=selected_profile,
            allowed_predicates=allowed_predicates,
        )
        trace = {
            "enabled": True,
            "utterance": utterance,
            "model": self._semantic_ir_model,
            "backend": self._compiler_backend,
            "base_url": self._compiler_base_url,
            "active_profile": self._active_profile,
            "selected_profile": selected_profile or "general",
            "profile_selection": self._clone_trace_payload(self._last_semantic_ir_profile_selection),
            "model_input": {
                "domain": domain,
                "utterance": utterance,
                "context": semantic_context,
                "available_domain_profiles": self._semantic_ir_available_domain_profiles(),
                "domain_context": domain_context,
                "allowed_predicates": allowed_predicates,
                "predicate_contracts": predicate_contracts,
                "kb_context_pack": kb_context_pack,
                "options": {
                    "temperature": self._semantic_ir_temperature,
                    "top_p": self._semantic_ir_top_p,
                    "top_k": self._semantic_ir_top_k,
                    "num_ctx": self._semantic_ir_context_length,
                    "thinking": bool(self._semantic_ir_thinking),
                },
                "note": "Exact system/schema prompt is logged by research runners; gateway traces keep a compact input view.",
            },
            "parsed": None,
            "raw_message": "",
            "latency_ms": 0,
            "error": "",
        }
        try:
            result = call_semantic_ir(
                utterance=utterance,
                config=self._semantic_ir_call_config(),
                context=semantic_context,
                domain_context=domain_context,
                available_domain_profiles=self._semantic_ir_available_domain_profiles(),
                allowed_predicates=allowed_predicates,
                predicate_contracts=predicate_contracts,
                kb_context_pack=kb_context_pack,
                domain=domain,
            )
        except Exception as exc:
            trace["error"] = str(exc)
            self._last_semantic_ir_trace = trace
            return None, str(exc)
        trace["raw_message"] = str(result.get("content", "")).strip()
        trace["latency_ms"] = int(result.get("latency_ms", 0) or 0)
        parsed = result.get("parsed")
        if not isinstance(parsed, dict):
            trace["error"] = "semantic_ir_v1 payload was not valid JSON."
            self._last_semantic_ir_trace = trace
            return None, trace["error"]
        trace["parsed"] = self._clone_trace_payload(parsed)
        self._last_semantic_ir_trace = trace
        return parsed, ""

    def _compile_apply_parse_with_semantic_ir(
        self,
        *,
        utterance: str,
        compiler_intent: str,
        clarification_question: str = "",
        clarification_answer: str = "",
    ) -> tuple[dict[str, Any] | None, str]:
        self._last_parse_trace = {}
        effective = utterance
        if clarification_question or clarification_answer:
            effective = (
                f"{utterance}\n"
                f"Clarification question: {clarification_question}\n"
                f"Clarification answer: {clarification_answer}"
            ).strip()

        cached_trace = self._last_semantic_ir_trace if isinstance(self._last_semantic_ir_trace, dict) else {}
        cached_ir = cached_trace.get("parsed") if str(cached_trace.get("utterance", "")).strip() == effective else None
        if isinstance(cached_ir, dict):
            ir, error = self._clone_trace_payload(cached_ir), ""
        else:
            ir, error = self._compile_semantic_ir(effective)
        trace = {
            "utterance": utterance,
            "effective_utterance": effective,
            "compiler_intent": compiler_intent,
            "clarification_answer": clarification_answer,
            "model": self._semantic_ir_model,
            "semantic_ir_enabled": True,
            "semantic_ir": self._clone_trace_payload(self._last_semantic_ir_trace),
            "normalized": None,
            "rescues": [],
            "admitted": None,
            "validation_errors": [],
            "raw_matches_admitted": True,
        }
        if not isinstance(ir, dict):
            trace["validation_errors"] = [error or "semantic_ir_v1 failed"]
            trace["summary"] = self._summarize_parse_trace(trace)
            self._last_parse_trace = trace
            return None, error or "semantic_ir_v1 failed"

        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=self._semantic_ir_allowed_predicates(self._last_semantic_ir_selected_profile),
            predicate_contracts=self._semantic_ir_predicate_contracts(self._last_semantic_ir_selected_profile),
        )
        trace["normalized"] = self._clone_trace_payload(parsed)
        trace["rescues"].append(
            {
                "name": "semantic_ir_mapper",
                "applied": True,
                "summary": "Mapped safe semantic_ir_v1 operations directly to runtime parse without English rescue passes.",
                "warnings": list(warnings),
                "admission_diagnostics": self._clone_trace_payload(
                    parsed.get("admission_diagnostics", {})
                    if isinstance(parsed.get("admission_diagnostics"), dict)
                    else {}
                ),
            }
        )
        admitted = self._apply_active_profile_parse_guard(
            parsed=parsed,
            utterance=effective,
            profile_id=self._last_semantic_ir_selected_profile,
        )
        trace["admitted"] = self._clone_trace_payload(admitted)
        ok, errors = _validate_parsed(admitted)
        trace["validation_errors"] = list(errors)
        trace["summary"] = self._summarize_parse_trace(trace)
        self._last_parse_trace = trace
        if not ok:
            return None, "; ".join(errors)
        return admitted, ""

    def _runtime_direct_fact_clauses(self) -> list[str]:
        clauses: list[str] = []
        engine = getattr(self._runtime, "engine", None)
        if engine is not None:
            for row in getattr(engine, "clauses", []) or []:
                if getattr(row, "body", None):
                    continue
                text = _normalize_clause(str(row))
                if text:
                    clauses.append(text)
        raw_clauses = getattr(self._runtime, "_clauses", None)
        if isinstance(raw_clauses, set):
            for row in sorted(raw_clauses):
                text = _normalize_clause(str(row))
                if text and ":-" not in text:
                    clauses.append(text)
        deduped: list[str] = []
        seen: set[str] = set()
        for clause in clauses:
            if clause in seen:
                continue
            seen.add(clause)
            deduped.append(clause)
        return deduped

    @staticmethod
    def _single_fact_call(clause: str) -> tuple[str, list[str], str] | None:
        normalized = _normalize_clause(clause)
        if not normalized or ":-" in normalized:
            return None
        expr = normalized[:-1] if normalized.endswith(".") else normalized
        calls = _extract_calls_with_args(expr)
        if len(calls) != 1:
            return None
        predicate, args = calls[0]
        if not predicate:
            return None
        return predicate, [str(arg).strip() for arg in args], normalized

    @staticmethod
    def _is_likely_functional_current_state_predicate(predicate: str, arity: int) -> bool:
        name = str(predicate).strip().lower()
        if (name, int(arity)) in FUNCTIONAL_CURRENT_STATE_PREDICATES:
            return True
        return int(arity) >= 2 and any(name.startswith(prefix) for prefix in FUNCTIONAL_CURRENT_STATE_PREFIXES)

    @staticmethod
    def _opposing_modal_predicates(predicate: str) -> list[str]:
        name = str(predicate).strip().lower()
        for prefix in ("cannot_", "cant_"):
            if name.startswith(prefix) and len(name) > len(prefix):
                stem = name[len(prefix) :]
                return [f"may_{stem}", f"can_{stem}"]
        for prefix in ("may_", "can_"):
            if name.startswith(prefix) and len(name) > len(prefix):
                stem = name[len(prefix) :]
                return [f"cannot_{stem}", f"cant_{stem}"]
        return []

    @staticmethod
    def _compact_numbered_atom_aliases(args: list[str]) -> list[list[str]]:
        variants = [list(args)]
        compacted = [re.sub(r"(?<=[a-z])_(?=\d)", "", str(arg).strip()) for arg in args]
        if compacted != args:
            variants.append(compacted)
        return variants

    def _stored_logic_conflicts_for_facts(
        self,
        *,
        fact_clauses: list[str],
        correction_retracts: list[str],
    ) -> list[dict[str, Any]]:
        correction_targets = {
            _normalize_clause(clause)
            for clause in correction_retracts
            if _normalize_clause(str(clause))
        }
        existing_facts: list[tuple[str, list[str], str]] = []
        for clause in self._runtime_direct_fact_clauses():
            parsed = self._single_fact_call(clause)
            if parsed is None:
                continue
            existing_facts.append(parsed)

        conflicts: list[dict[str, Any]] = []
        for raw_clause in fact_clauses:
            parsed_new = self._single_fact_call(raw_clause)
            if parsed_new is None:
                continue
            predicate, args, normalized = parsed_new
            arity = len(args)
            if self._is_likely_functional_current_state_predicate(predicate, arity) and args:
                subject = args[0]
                for existing_predicate, existing_args, existing_clause in existing_facts:
                    if existing_clause in correction_targets:
                        continue
                    if existing_clause == normalized:
                        continue
                    if existing_predicate != predicate or len(existing_args) != arity:
                        continue
                    if existing_args and existing_args[0] == subject and existing_args != args:
                        conflicts.append(
                            {
                                "kind": "functional_current_state_conflict",
                                "candidate": normalized,
                                "existing": existing_clause,
                                "predicate": f"{predicate}/{arity}",
                                "subject": subject,
                                "reason": "candidate changes a likely functional current-state value without an explicit retract/correction",
                            }
                        )

            for opposite in self._opposing_modal_predicates(predicate):
                for query_args in self._compact_numbered_atom_aliases(args):
                    opposite_query = f"{opposite}({', '.join(query_args)})."
                    result = self.query_rows(opposite_query)
                    if str(result.get("status", "")).strip() != "success":
                        continue
                    conflicts.append(
                        {
                            "kind": "rule_derived_modal_conflict",
                            "candidate": normalized,
                            "opposing_query": opposite_query,
                            "predicate": f"{predicate}/{arity}",
                            "reason": "candidate contradicts an opposite modal predicate derivable from current KB state",
                            "query_rows": result.get("rows", []),
                        }
                    )
                    break
        return conflicts

    def _apply_compiled_parse(self, *, parsed: dict[str, Any], prethink_id: str) -> dict[str, Any]:
        intent = str(parsed.get("intent", "")).strip()
        operations: list[dict[str, Any]] = []
        writes_applied = 0
        query_result: dict[str, Any] | None = None
        errors: list[str] = []
        clause_supports = parsed.get("clause_supports", {}) if isinstance(parsed.get("clause_supports"), dict) else {}

        def support_for(effect: str, clause: str) -> dict[str, Any]:
            rows = clause_supports.get(effect, []) if isinstance(clause_supports, dict) else []
            normalized_clause = _normalize_clause(str(clause))
            if not isinstance(rows, list):
                return {}
            for row in rows:
                if not isinstance(row, dict):
                    continue
                if _normalize_clause(str(row.get("clause", ""))) == normalized_clause:
                    return self._clone_trace_payload(row)
            return {}

        if intent in {"assert_fact", "assert_rule"}:
            correction_retracts = [
                str(item).strip()
                for item in parsed.get("correction_retract_clauses", [])
                if str(item).strip()
            ]
            for clause in correction_retracts:
                normalized_clause = clause if clause.endswith(".") else f"{clause}."
                result = self.tools_call(
                    "retract_fact",
                    {"clause": normalized_clause, "prethink_id": prethink_id, "confirm": True},
                )
                operations.append(
                    {
                        "tool": "retract_fact",
                        "clause": normalized_clause,
                        "support": support_for("retracts", normalized_clause),
                        "result": result,
                    }
                )
                status = str(result.get("status", "")).strip()
                if status == "success":
                    writes_applied += 1
                elif status not in {"no_results", "no_result"}:
                    errors.append(f"retract_fact failed for {normalized_clause}")

            fact_clauses = [str(item).strip() for item in parsed.get("facts", []) if str(item).strip()]
            rule_clauses = [str(item).strip() for item in parsed.get("rules", []) if str(item).strip()]

            if intent == "assert_fact" and not fact_clauses:
                clause = str(parsed.get("logic_string", "")).strip()
                if clause:
                    fact_clauses = [clause]
            if intent == "assert_rule" and not rule_clauses:
                clause = str(parsed.get("logic_string", "")).strip()
                if clause:
                    rule_clauses = [clause]

            conflicts = self._stored_logic_conflicts_for_facts(
                fact_clauses=fact_clauses,
                correction_retracts=correction_retracts,
            )
            if conflicts:
                errors.append("stored logic conflict blocked fact assertion")
                operations.append(
                    {
                        "tool": "stored_logic_conflict_guard",
                        "result": {
                            "status": "blocked",
                            "result_type": "stored_logic_conflict",
                            "conflicts": conflicts,
                        },
                    }
                )
                return {
                    "status": "error",
                    "intent": intent,
                    "writes_applied": writes_applied,
                    "operations": operations,
                    "query_result": query_result,
                    "parse": parsed,
                    "errors": errors,
                }

            for clause in fact_clauses:
                result = self.tools_call(
                    "assert_fact",
                    {"clause": clause, "prethink_id": prethink_id, "confirm": True},
                )
                operations.append(
                    {
                        "tool": "assert_fact",
                        "clause": clause,
                        "support": support_for("facts", clause),
                        "result": result,
                    }
                )
                if str(result.get("status", "")).strip() == "success":
                    writes_applied += 1
                else:
                    errors.append(f"assert_fact failed for {clause}")

            for clause in rule_clauses:
                result = self.tools_call(
                    "assert_rule",
                    {"clause": clause, "prethink_id": prethink_id, "confirm": True},
                )
                operations.append(
                    {
                        "tool": "assert_rule",
                        "clause": clause,
                        "support": support_for("rules", clause),
                        "result": result,
                    }
                )
                if str(result.get("status", "")).strip() == "success":
                    writes_applied += 1
                else:
                    errors.append(f"assert_rule failed for {clause}")

            queries = [str(item).strip() for item in parsed.get("queries", []) if str(item).strip()]
            if queries:
                query = queries[0]
                result = self.tools_call(
                    "query_rows",
                    {"query": query, "prethink_id": prethink_id},
                )
                query_result = result
                operations.append(
                    {
                        "tool": "query_rows",
                        "query": query,
                        "support": support_for("queries", query),
                        "result": result,
                    }
                )
                status = str(result.get("status", "")).strip()
                if status not in {"success", "no_results"}:
                    errors.append(f"query_rows failed for {query}")

        elif intent == "retract":
            targets = _extract_retract_targets(
                str(parsed.get("logic_string", "")).strip(),
                [str(item).strip() for item in parsed.get("facts", []) if str(item).strip()],
            )
            for target in targets:
                clause = target if str(target).strip().endswith(".") else f"{target}."
                result = self.tools_call(
                    "retract_fact",
                    {"clause": clause, "prethink_id": prethink_id, "confirm": True},
                )
                operations.append(
                    {
                        "tool": "retract_fact",
                        "clause": clause,
                        "support": support_for("retracts", clause),
                        "result": result,
                    }
                )
                status = str(result.get("status", "")).strip()
                if status == "success":
                    writes_applied += 1
                elif status not in {"no_results", "no_result"}:
                    errors.append(f"retract_fact failed for {clause}")

        elif intent == "query":
            queries = [str(item).strip() for item in parsed.get("queries", []) if str(item).strip()]
            query = queries[0] if queries else str(parsed.get("logic_string", "")).strip()
            result = self.tools_call(
                "query_rows",
                {"query": query, "prethink_id": prethink_id},
            )
            query_result = result
            operations.append(
                {
                    "tool": "query_rows",
                    "query": query,
                    "support": support_for("queries", query),
                    "result": result,
                }
            )
            status = str(result.get("status", "")).strip()
            if status not in {"success", "no_results"}:
                errors.append(f"query_rows failed for {query}")

        else:
            operations.append({"tool": "none", "result": {"status": "skipped", "message": "Intent=other"}})

        return {
            "status": "success" if not errors else "error",
            "intent": intent,
            "writes_applied": writes_applied,
            "operations": operations,
            "query_result": query_result,
            "parse": parsed,
            "errors": errors,
        }

    def _front_door_from_packet(
        self,
        *,
        packet: dict[str, Any],
        prethink: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        signals = packet.get("signals", {}) if isinstance(packet.get("signals"), dict) else {}
        compiler = packet.get("compiler", {}) if isinstance(packet.get("compiler"), dict) else {}
        clar = packet.get("clarification", {}) if isinstance(packet.get("clarification"), dict) else {}
        compiler_intent = str(
            signals.get("compiler_intent") or compiler.get("intent") or "other"
        ).strip()
        route = "query" if compiler_intent == "query" else (
            "write" if compiler_intent in {"assert_fact", "assert_rule", "retract"} else "other"
        )
        ambiguity = float(signals.get("compiler_uncertainty_score") or 0.0)
        reason = str(clar.get("reason", "")).strip() or "compiler_decision"
        return {
            "route": route,
            "compiler_intent": compiler_intent,
            "looks_like_query": route == "query",
            "looks_like_write": route == "write",
            "ambiguity_score": round(ambiguity, 2),
            "needs_clarification": bool(clar.get("required_before_query")),
            "reasons": [reason],
            "clarification_question": str(clar.get("question", "")).strip(),
            "prethink_id": str(packet.get("prethink_id", "")).strip(),
            "compiler": {
                "mode": self._compiler_mode,
                "model": str(compiler.get("model", "")).strip()
                or (self._semantic_ir_model if self._semantic_ir_enabled else self._compiler_model),
                "backend": self._compiler_backend,
                "base_url": self._compiler_base_url,
                "strict_mode": self._compiler_mode == "strict",
                "used": bool(compiler.get("used", True)),
                "error": str(compiler.get("error", "")).strip(),
                "semantic_ir_enabled": bool(compiler.get("semantic_ir_enabled", self._semantic_ir_enabled)),
            },
            "session_snapshot": {
                "pending_prethink": self._pending_prethink_summary(),
            },
            "prethink": prethink or {"status": "success", "result_type": "pre_think_packet", "packet": packet},
        }

    def _front_door_from_pending(self) -> dict[str, Any]:
        pending = self._pending_prethink or {}
        packet = {
            "prethink_id": str(pending.get("prethink_id", "")).strip(),
            "signals": {
                "compiler_intent": str(pending.get("compiler_intent", "other")).strip() or "other",
                "compiler_uncertainty_score": float(pending.get("compiler_uncertainty_score", 0.0) or 0.0),
            },
            "compiler": {
                "mode": self._compiler_mode,
                "backend": self._compiler_backend,
                "base_url": self._compiler_base_url,
                "model": self._semantic_ir_model if self._semantic_ir_enabled else self._compiler_model,
                "used": self._compiler_mode != "heuristic",
                "error": "",
                "intent": str(pending.get("compiler_intent", "other")).strip() or "other",
                "semantic_ir_enabled": bool(self._semantic_ir_enabled),
            },
            "clarification": {
                "required_before_query": bool(pending.get("clarification_required_before_query", False)),
                "question": str(pending.get("clarification_question", "")).strip(),
                "reason": str(pending.get("clarification_reason", "")).strip(),
            },
        }
        return self._front_door_from_packet(packet=packet)

    # Direct runtime methods used by kb_pipeline with --runtime mcp
    def empty_kb(self) -> dict[str, Any]:
        result = self._runtime.empty_kb()
        if self._kb_path:
            result["knowledge_base_path"] = self._kb_path
        return result

    def reset_conversation_state(self, *, clear_kb: bool = True) -> dict[str, Any]:
        kb_result: dict[str, Any] | None = None
        if clear_kb:
            kb_result = self.empty_kb()
        self._pending_prethink = None
        self._recent_accepted_turns.clear()
        self._recent_committed_logic.clear()
        self._last_prethink_trace = {}
        self._last_prethink_fallback_trace = {}
        self._last_parse_trace = {}
        self._last_semantic_ir_trace = {}
        self._prethink_counter = 1
        return {
            "status": "success",
            "result_type": "conversation_state_reset",
            "kb_cleared": bool(clear_kb),
            "kb_result": kb_result,
            "state": self._serialize_state(),
        }

    def assert_fact(self, clause: str) -> dict[str, Any]:
        result = self._runtime.assert_fact(clause)
        if self._kb_path:
            result["knowledge_base_path"] = self._kb_path
        return result

    def assert_rule(self, clause: str) -> dict[str, Any]:
        result = self._runtime.assert_rule(clause)
        if self._kb_path:
            result["knowledge_base_path"] = self._kb_path
        return result

    def retract_fact(self, clause: str) -> dict[str, Any]:
        result = self._runtime.retract_fact(clause)
        if self._kb_path:
            result["knowledge_base_path"] = self._kb_path
        return result

    def query_rows(self, query: str) -> dict[str, Any]:
        result = self._runtime.query_rows(query)
        if self._kb_path:
            result["knowledge_base_path"] = self._kb_path
        return result

    def tools_list(self) -> dict[str, Any]:
        return {
            "status": "success",
            "tools": [
                {
                    "name": "pre_think",
                    "description": "Generate pre-think decision packet for an utterance.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"utterance": {"type": "string"}},
                        "required": ["utterance"],
                    },
                },
                {
                    "name": "set_pre_think_session",
                    "description": "Toggle session-level pre-think settings.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "enabled": {"type": "boolean"},
                            "all_turns_require_prethink": {"type": "boolean"},
                            "clarification_eagerness": {"type": "number"},
                            "require_final_confirmation": {"type": "boolean"},
                        },
                    },
                },
                {
                    "name": "show_pre_think_state",
                    "description": "Show current pre-think session state.",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": "record_clarification_answer",
                    "description": "Record clarification answer for the active pre-think turn.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prethink_id": {"type": "string"},
                            "answer": {"type": "string"},
                            "confirmed": {"type": "boolean"},
                        },
                        "required": ["prethink_id", "answer"],
                    },
                },
                {
                    "name": "process_utterance",
                    "description": "Canonical Prethinker utterance entryway: pre-think, clarify if needed, parse, and deterministically execute.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "utterance": {"type": "string"},
                            "clarification_answer": {"type": "string"},
                            "prethink_id": {"type": "string"},
                        },
                        "required": ["utterance"],
                    },
                },
                {
                    "name": "query_rows",
                    "description": "Run deterministic Prolog query_rows.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "prethink_id": {"type": "string"},
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "assert_fact",
                    "description": "Assert deterministic fact clause.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "clause": {"type": "string"},
                            "prethink_id": {"type": "string"},
                            "confirm": {"type": "boolean"},
                        },
                        "required": ["clause"],
                    },
                },
                {
                    "name": "assert_rule",
                    "description": "Assert deterministic rule clause.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "clause": {"type": "string"},
                            "prethink_id": {"type": "string"},
                            "confirm": {"type": "boolean"},
                        },
                        "required": ["clause"],
                    },
                },
                {
                    "name": "retract_fact",
                    "description": "Retract deterministic fact clause.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "clause": {"type": "string"},
                            "prethink_id": {"type": "string"},
                            "confirm": {"type": "boolean"},
                        },
                        "required": ["clause"],
                    },
                },
            ],
        }

    def get_tools(self) -> list[dict[str, Any]]:
        return list(self.tools_list().get("tools", []))

    def list_tools(self) -> dict[str, Any]:
        return self.tools_list()

    def tools_call(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        tool = str(name or "").strip()
        if not tool:
            return {"status": "validation_error", "message": "Tool name is required."}
        self._trace("tools_call_start", {"tool": tool, "arguments": args})

        if tool == "pre_think":
            result = self.pre_think(args)
            self._trace("tools_call_end", {"tool": tool, "result": result})
            return result
        if tool == "set_pre_think_session":
            result = self.set_pre_think_session(args)
            self._trace("tools_call_end", {"tool": tool, "result": result})
            return result
        if tool == "show_pre_think_state":
            result = self.show_pre_think_state()
            self._trace("tools_call_end", {"tool": tool, "result": result})
            return result
        if tool == "record_clarification_answer":
            result = self.record_clarification_answer(args)
            self._trace("tools_call_end", {"tool": tool, "result": result})
            return result
        if tool == "process_utterance":
            result = self.process_utterance(args)
            self._trace("tools_call_end", {"tool": tool, "result": result})
            return result
        if tool == "query_rows":
            blocked = self._check_prethink_gate(tool, args)
            if blocked is not None:
                self._trace("tools_call_end", {"tool": tool, "result": blocked})
                return blocked
            result = self._query_rows_with_fallback(str(args.get("query", "")))
            self._consume_prethink_after_call(tool, result)
            self._trace("tools_call_end", {"tool": tool, "result": result})
            return result
        if tool == "assert_fact":
            blocked = self._check_prethink_gate(tool, args)
            if blocked is not None:
                self._trace("tools_call_end", {"tool": tool, "result": blocked})
                return blocked
            result = self.assert_fact(str(args.get("clause", "")))
            self._consume_prethink_after_call(tool, result)
            self._trace("tools_call_end", {"tool": tool, "result": result})
            return result
        if tool == "assert_rule":
            blocked = self._check_prethink_gate(tool, args)
            if blocked is not None:
                self._trace("tools_call_end", {"tool": tool, "result": blocked})
                return blocked
            result = self.assert_rule(str(args.get("clause", "")))
            self._consume_prethink_after_call(tool, result)
            self._trace("tools_call_end", {"tool": tool, "result": result})
            return result
        if tool == "retract_fact":
            blocked = self._check_prethink_gate(tool, args)
            if blocked is not None:
                self._trace("tools_call_end", {"tool": tool, "result": blocked})
                return blocked
            result = self.retract_fact(str(args.get("clause", "")))
            self._consume_prethink_after_call(tool, result)
            self._trace("tools_call_end", {"tool": tool, "result": result})
            return result

        result = {"status": "not_found", "message": f"Unknown tool: {tool}"}
        self._trace("tools_call_end", {"tool": tool, "result": result})
        return result

    def handle_tool_call(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.tools_call(name=name, arguments=arguments)

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.tools_call(name=name, arguments=arguments)

    def set_pre_think_session(self, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        self._session.enabled = _coerce_bool(args.get("enabled"), self._session.enabled)
        self._session.all_turns_require_prethink = _coerce_bool(
            args.get("all_turns_require_prethink"),
            self._session.all_turns_require_prethink,
        )
        self._session.require_final_confirmation = _coerce_bool(
            args.get("require_final_confirmation"),
            self._session.require_final_confirmation,
        )
        if "clarification_eagerness" in args:
            self._session.clarification_eagerness = _clip_01(
                args.get("clarification_eagerness"),
                self._session.clarification_eagerness,
            )
        return {
            "status": "success",
            "result_type": "session_updated",
            "state": self._serialize_state(),
        }

    def show_pre_think_state(self) -> dict[str, Any]:
        return {"status": "success", "result_type": "session_state", "state": self._serialize_state()}

    def _build_compiler_prompt(self, utterance: str) -> str:
        prompt_section = self._compiler_prompt_text.strip()
        return (
            "/no_think\n"
            f"{prompt_section}\n\n"
            "You are compiling a PRE-THINK routing packet.\n"
            "Return minified JSON only with keys:\n"
            "intent,needs_clarification,uncertainty_score,clarification_question,clarification_reason,rationale\n"
            "Rules:\n"
            "- intent must be one of: assert_fact,assert_rule,query,retract,other\n"
            "- needs_clarification must be boolean\n"
            "- uncertainty_score must be numeric in [0,1]\n"
            "- clarification_question must be empty string unless clarification is needed\n"
            "- clarification_reason must be empty string unless clarification is needed\n"
            "- rationale must be one short sentence (<=16 words)\n"
            "- do not explain alternatives or deliberate\n"
            "- no markdown, no prose wrappers\n"
            f"USER_UTTERANCE:\n{utterance}\n"
        )

    def _coerce_prethink_compiler_payload_base(
        self,
        parsed: dict[str, Any],
    ) -> tuple[dict[str, Any] | None, str]:
        if not isinstance(parsed, dict):
            return None, "Compiler returned non-parseable JSON payload."

        intent_raw = str(parsed.get("intent", "")).strip().lower()
        intent_aliases = {
            "informative": "assert_fact",
            "information": "assert_fact",
            "statement": "assert_fact",
            "fact": "assert_fact",
            "question": "query",
            "ask": "query",
            "remove": "retract",
            "delete": "retract",
        }
        intent = intent_aliases.get(intent_raw, intent_raw)
        if intent not in {"assert_fact", "assert_rule", "query", "retract", "other"}:
            return None, f"Compiler returned invalid intent: {intent_raw or intent}"

        out = dict(parsed)
        out["intent"] = intent
        out["needs_clarification"] = _coerce_bool(out.get("needs_clarification"), False)
        out["uncertainty_score"] = _clip_01(out.get("uncertainty_score"), 0.0)
        out["clarification_question"] = str(out.get("clarification_question") or "").strip()
        out["clarification_reason"] = str(out.get("clarification_reason") or "").strip()
        out["rationale"] = str(out.get("rationale") or "").strip()
        if not out["needs_clarification"]:
            out["clarification_question"] = ""
            out["clarification_reason"] = ""
        return out, ""

    def _normalize_prethink_compiler_payload(
        self,
        parsed: dict[str, Any],
        *,
        utterance: str,
    ) -> tuple[dict[str, Any] | None, str]:
        out, error = self._coerce_prethink_compiler_payload_base(parsed)
        if out is None:
            return None, error
        out = self._sanitize_compiler_clarification(
            utterance=utterance,
            compiled=out,
        )
        return out, ""

    def _compile_prethink_classifier_fallback(self, utterance: str) -> tuple[dict[str, Any] | None, str]:
        self._last_prethink_fallback_trace = {
            "used": False,
            "prompt_text": "",
            "raw_message": "",
            "reasoning": "",
            "parsed": None,
            "normalized": None,
            "error": "",
        }
        prompt = _build_classifier_prompt(utterance)
        self._last_prethink_fallback_trace["prompt_text"] = prompt
        try:
            response = _call_model_prompt(
                backend=self._compiler_backend,
                base_url=self._compiler_base_url,
                model=self._compiler_model,
                prompt_text=prompt,
                context_length=max(512, min(self._compiler_context_length, 4096)),
                timeout=self._compiler_timeout,
                api_key=self._compiler_api_key,
            )
            self._last_prethink_fallback_trace["raw_message"] = str(response.message or "")
            self._last_prethink_fallback_trace["reasoning"] = str(response.reasoning or "")
            parsed, _ = _parse_model_json(
                response,
                required_keys=["route", "needs_clarification", "ambiguity_risk", "reason"],
            )
        except Exception as exc:
            self._last_prethink_fallback_trace["error"] = str(exc)
            return None, str(exc)
        if not isinstance(parsed, dict):
            self._last_prethink_fallback_trace["error"] = "Fallback classifier returned non-parseable JSON payload."
            return None, "Fallback classifier returned non-parseable JSON payload."
        self._last_prethink_fallback_trace["parsed"] = self._clone_trace_payload(parsed)

        route_raw = str(parsed.get("route", "")).strip().lower()
        route_aliases = {
            "informative": "assert_fact",
            "information": "assert_fact",
            "statement": "assert_fact",
            "fact": "assert_fact",
            "question": "query",
            "ask": "query",
            "delete": "retract",
            "remove": "retract",
        }
        route = route_aliases.get(route_raw, route_raw)
        if route not in {"assert_fact", "assert_rule", "query", "retract", "other"}:
            self._last_prethink_fallback_trace["error"] = (
                f"Fallback classifier returned invalid route: {route_raw or route}"
            )
            return None, f"Fallback classifier returned invalid route: {route_raw or route}"

        risk = str(parsed.get("ambiguity_risk", "")).strip().lower()
        score_map = {"low": 0.15, "medium": 0.55, "high": 0.85}
        uncertainty = score_map.get(risk, 0.55)
        needs_clarification = _coerce_bool(parsed.get("needs_clarification"), False)
        reason = str(parsed.get("reason") or "").strip()
        question = (
            _synthesize_clarification_question(
                utterance=utterance,
                route=route,
                ambiguities=[],
                reason=reason or "Needs clarification",
            )
            if needs_clarification
            else ""
        )
        fallback_payload = {
            "intent": route,
            "needs_clarification": needs_clarification,
            "uncertainty_score": uncertainty,
            "clarification_question": question,
            "clarification_reason": reason if needs_clarification else "",
            "rationale": f"Fallback classifier routed utterance as {route}.",
        }
        normalized, error = self._normalize_prethink_compiler_payload(
            fallback_payload,
            utterance=utterance,
        )
        self._last_prethink_fallback_trace["used"] = normalized is not None
        self._last_prethink_fallback_trace["normalized"] = self._clone_trace_payload(normalized)
        self._last_prethink_fallback_trace["error"] = str(error or "").strip()
        return normalized, error

    def _compile_shadow_parse(self, utterance: str, route: str) -> tuple[dict[str, Any] | None, str]:
        if not self._compiler_prompt_loaded:
            reason = self._compiler_prompt_load_error or "compiler prompt unavailable"
            return None, f"Compiler prompt not loaded: {reason}"
        effective_route = str(route or "other").strip().lower()
        if effective_route not in {"assert_fact", "assert_rule", "query", "retract", "other"}:
            effective_route = "other"
        extraction_prompt = _build_extractor_prompt(
            utterance,
            effective_route,
            known_predicates=self._profile_known_predicates,
            prompt_guide=self._compiler_prompt_text,
        )
        try:
            response = _call_model_prompt(
                backend=self._compiler_backend,
                base_url=self._compiler_base_url,
                model=self._compiler_model,
                prompt_text=extraction_prompt,
                context_length=self._compiler_context_length,
                timeout=self._compiler_timeout,
                api_key=self._compiler_api_key,
            )
            parsed, _ = _parse_model_json(
                response,
                required_keys=["intent", "logic_string", "components", "confidence"],
            )
        except Exception as exc:
            return None, str(exc)
        if not isinstance(parsed, dict):
            return None, "Shadow parse returned non-parseable JSON payload."
        normalized = _normalize_clarification_fields(
            parsed,
            utterance=utterance,
            route=effective_route,
        )
        normalized = self._apply_active_profile_parse_guard(
            parsed=normalized,
            utterance=utterance,
        )
        ok, errors = _validate_parsed(normalized)
        if not ok:
            return None, "; ".join(errors)
        return normalized, ""

    def _clarification_family_relation_drift(
        self,
        *,
        utterance: str,
        question: str,
        reason: str,
    ) -> bool:
        utterance_terms = set(re.findall(r"[a-z][a-z0-9_'-]*", str(utterance or "").lower()))
        clarification_terms = set(
            re.findall(r"[a-z][a-z0-9_'-]*", f"{question} {reason}".lower())
        )
        family_terms = {
            "parent",
            "parents",
            "mother",
            "father",
            "mom",
            "dad",
            "child",
            "children",
            "son",
            "sons",
            "daughter",
            "daughters",
            "ancestor",
            "ancestors",
            "guardian",
            "guardians",
        }
        return bool(clarification_terms & family_terms) and not bool(utterance_terms & family_terms)

    def _utterance_has_explicit_family_bundle(self, utterance: str) -> bool:
        lowered = str(utterance or "").strip().lower()
        if not lowered:
            return False
        patterns = [
            r"\b([a-z][a-z0-9_'-]*?)'?s\s+mom\s+and\s+dad\s+(?:is|are)\s+[a-z][a-z0-9_'-]*\s+and\s+[a-z][a-z0-9_'-]*\b",
            r"\b([a-z][a-z0-9_'-]*?)'?s\s+mother\s+and\s+father\s+(?:is|are)\s+[a-z][a-z0-9_'-]*\s+and\s+[a-z][a-z0-9_'-]*\b",
            r"\b[a-z][a-z0-9_'-]*\s+has\s+a\s+brother\s+and\s+his\s+brother'?s\s+name\s+is\s+[a-z][a-z0-9_'-]*\b",
        ]
        return any(re.search(pattern, lowered) for pattern in patterns)

    def _is_internal_predicate_mapping_clarification(
        self,
        *,
        question: str,
        reason: str,
    ) -> bool:
        text = f"{question} {reason}".strip().lower()
        if not text:
            return False
        signals = (
            "intended prolog predicate",
            "canonical predicate mapping",
            "predicate mapping",
            "canonical predicate",
            "what is the intended prolog predicate",
            "what specific facts about",
            "facts to assert",
            "lacks explicit predicates or facts to assert",
        )
        return any(token in text for token in signals)

    def _medical_vague_surface_clarification(self, utterance: str) -> dict[str, str]:
        if self._active_profile != "medical@v0":
            return {}
        guidance = bridge_admission_guidance(utterance, self._profile_umls_bridge)
        if not guidance.get("needs_clarification"):
            return {}
        surfaces = [
            str(row.get("surface", "")).strip()
            for row in guidance.get("vague_surfaces", [])
            if isinstance(row, dict) and str(row.get("surface", "")).strip()
        ]
        if not surfaces:
            return {}
        surface = surfaces[0]
        patient = ""
        patient_match = re.search(
            rf"\b([A-Z][A-Za-z0-9_-]*)'?s\s+{re.escape(surface)}\b",
            str(utterance or ""),
        )
        if patient_match:
            patient = patient_match.group(1)
        patient_phrase = f" for {patient}" if patient else ""
        if surface == "pressure":
            question = (
                f"Which medical meaning of 'pressure' is bad{patient_phrase}: "
                "blood pressure reading, chest pressure symptom, stress, or something else?"
            )
        elif surface == "sugar":
            question = (
                f"Which medical meaning of 'sugar' is bad{patient_phrase}: "
                "blood glucose result, diabetes, diet, or something else?"
            )
        elif surface in {"kidney", "kidneys"}:
            question = (
                f"Which kidney-related meaning should be stored{patient_phrase}: "
                "condition, symptom, lab result, or procedure?"
            )
        else:
            question = f"Which medical meaning of '{surface}' should be stored{patient_phrase}?"
        reasons = [
            str(row.get("reason", "")).strip()
            for row in guidance.get("vague_surfaces", [])
            if isinstance(row, dict) and str(row.get("reason", "")).strip()
        ]
        return {
            "question": question,
            "reason": reasons[0] if reasons else f"Vague medical surface: {surface}.",
        }

    def _sanitize_compiler_clarification(
        self,
        *,
        utterance: str,
        compiled: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(compiled, dict):
            return compiled
        out = dict(compiled)
        intent = str(out.get("intent", "")).strip().lower()
        if intent not in {"assert_fact", "assert_rule", "query", "retract", "other"}:
            return out
        out = _normalize_clarification_fields(out, utterance=utterance, route=intent)
        medical_vague = self._medical_vague_surface_clarification(utterance)
        if medical_vague:
            lowered = str(utterance or "").strip().lower()
            if not (
                str(out.get("intent", "")).strip().lower() == "query"
                and (
                    str(utterance or "").strip().endswith("?")
                    or lowered.startswith(("is ", "are ", "does ", "do "))
                )
            ):
                out["intent"] = "assert_fact"
            out["needs_clarification"] = True
            out["clarification_question"] = medical_vague["question"]
            out["clarification_reason"] = medical_vague["reason"]
            out["uncertainty_score"] = max(_clip_01(out.get("uncertainty_score"), 0.0), 0.85)
            out["uncertainty_label"] = "high"
            out["rationale"] = "Medical profile held a vague surface form before extraction."
            return out
        explicit_with_correction = self._extract_explicit_with_correction(utterance)
        if explicit_with_correction is not None and intent in {"assert_fact", "retract"}:
            out["intent"] = "assert_fact"
            out["needs_clarification"] = False
            out["clarification_question"] = ""
            out["clarification_reason"] = ""
            out["uncertainty_score"] = min(
                _clip_01(out.get("uncertainty_score"), 0.15),
                0.15,
            )
            out["uncertainty_label"] = "low"
            out["rationale"] = (
                "Recognized an explicit holder correction and normalized it to an assert_fact "
                "state update."
            )
            return out
        explicit_step_sequence = self._extract_explicit_step_sequence(utterance)
        if explicit_step_sequence is not None and intent == "assert_fact":
            out["needs_clarification"] = False
            out["clarification_question"] = ""
            out["clarification_reason"] = ""
            out["uncertainty_score"] = min(
                _clip_01(out.get("uncertainty_score"), 0.15),
                0.15,
            )
            out["uncertainty_label"] = "low"
            out["rationale"] = (
                "Recognized an explicit step sequence and deferred canonical temporal "
                "normalization to the parse layer."
            )
            return out
        question = str(out.get("clarification_question", "")).strip()
        reason = str(out.get("clarification_reason", "")).strip()
        if not bool(out.get("needs_clarification", False)):
            return out
        family_drift = self._clarification_family_relation_drift(
            utterance=utterance,
            question=question,
            reason=reason,
        )
        explicit_family_bundle = self._utterance_has_explicit_family_bundle(utterance)
        internal_predicate_mapping = self._is_internal_predicate_mapping_clarification(
            question=question,
            reason=reason,
        )
        if not family_drift and not explicit_family_bundle and not internal_predicate_mapping:
            return out

        shadow_parse, _shadow_error = self._compile_shadow_parse(utterance, intent)
        if isinstance(shadow_parse, dict):
            shadow_intent = str(shadow_parse.get("intent", "")).strip().lower()
            shadow_uncertainty = _clip_01(shadow_parse.get("uncertainty_score"), default=1.0)
            same_family = shadow_intent == intent or (
                intent in {"assert_fact", "assert_rule", "retract"}
                and shadow_intent in {"assert_fact", "assert_rule", "retract"}
            )
            if same_family and not bool(shadow_parse.get("needs_clarification", False)) and shadow_uncertainty <= 0.35:
                out["needs_clarification"] = False
                out["clarification_question"] = ""
                out["clarification_reason"] = ""
                out["uncertainty_score"] = shadow_uncertainty
                out["uncertainty_label"] = str(shadow_parse.get("uncertainty_label", "low")).strip() or "low"
                rationale = str(shadow_parse.get("rationale", "")).strip()
                if rationale:
                    out["rationale"] = rationale
                return out

        if family_drift or internal_predicate_mapping:
            out["clarification_question"] = _synthesize_clarification_question(
                utterance=utterance,
                route=intent,
                ambiguities=[],
                reason="Action or relation needs clarification",
            )
            out["clarification_reason"] = "Action or relation needs clarification"
        return out

    def _compile_prethink_semantics(self, utterance: str) -> tuple[dict[str, Any] | None, str]:
        if self._semantic_ir_enabled:
            return self._compile_prethink_semantics_with_semantic_ir(utterance)
        if not self._compiler_prompt_loaded:
            reason = self._compiler_prompt_load_error or "compiler prompt unavailable"
            return None, f"Compiler prompt not loaded: {reason}"
        self._last_prethink_trace = {}
        self._last_prethink_fallback_trace = {}
        prompt = self._build_compiler_prompt(utterance)
        trace = {
            "utterance": utterance,
            "source": "primary",
            "compiler_mode": self._compiler_mode,
            "model": self._compiler_model,
            "prompt_path": str(self._compiler_prompt_path) if self._compiler_prompt_enabled else "",
            "primary": {
                "prompt_text": prompt,
                "raw_message": "",
                "reasoning": "",
                "parsed": None,
                "normalized_before_sanitize": None,
                "final_normalized": None,
                "error": "",
            },
            "fallback": {
                "used": False,
                "prompt_text": "",
                "raw_message": "",
                "reasoning": "",
                "parsed": None,
                "normalized": None,
                "error": "",
            },
            "rescues": [],
            "final": None,
        }
        try:
            response = _call_model_prompt(
                backend=self._compiler_backend,
                base_url=self._compiler_base_url,
                model=self._compiler_model,
                prompt_text=prompt,
                context_length=self._compiler_context_length,
                timeout=self._compiler_timeout,
                api_key=self._compiler_api_key,
            )
            trace["primary"]["raw_message"] = str(response.message or "")
            trace["primary"]["reasoning"] = str(response.reasoning or "")
            parsed, _ = _parse_model_json(
                response,
                required_keys=["intent", "needs_clarification", "uncertainty_score"],
            )
            trace["primary"]["parsed"] = self._clone_trace_payload(parsed)
            normalized_before_sanitize, normalize_error = self._coerce_prethink_compiler_payload_base(
                parsed,
            )
            trace["primary"]["normalized_before_sanitize"] = self._clone_trace_payload(
                normalized_before_sanitize
            )
            if normalized_before_sanitize is not None:
                normalized = self._sanitize_compiler_clarification(
                    utterance=utterance,
                    compiled=self._clone_trace_payload(normalized_before_sanitize),
                )
                clarification_changed = (
                    (
                        bool(normalized_before_sanitize.get("needs_clarification", False))
                        or bool(normalized.get("needs_clarification", False))
                    )
                    and (
                        bool(normalized_before_sanitize.get("needs_clarification", False))
                        != bool(normalized.get("needs_clarification", False))
                        or str(normalized_before_sanitize.get("clarification_question", "")).strip()
                        != str(normalized.get("clarification_question", "")).strip()
                        or str(normalized_before_sanitize.get("clarification_reason", "")).strip()
                        != str(normalized.get("clarification_reason", "")).strip()
                        or _clip_01(normalized_before_sanitize.get("uncertainty_score"), 0.0)
                        != _clip_01(normalized.get("uncertainty_score"), 0.0)
                    )
                )
                trace["primary"]["final_normalized"] = self._clone_trace_payload(normalized)
                trace["primary"]["error"] = ""
                trace["rescues"].append(
                    {
                        "name": "clarification_sanitized",
                        "applied": clarification_changed,
                        "summary": "Suppressed or tightened unsafe clarification behavior.",
                    }
                )
                trace["final"] = self._clone_trace_payload(normalized)
                trace["summary"] = self._summarize_prethink_trace(trace)
                self._last_prethink_trace = trace
                return normalized, ""
            trace["primary"]["error"] = str(normalize_error or "").strip()
            fallback, fallback_error = self._compile_prethink_classifier_fallback(utterance)
            trace["fallback"] = self._clone_trace_payload(self._last_prethink_fallback_trace)
            if fallback is not None:
                trace["source"] = "fallback_classifier"
                trace["rescues"].append(
                    {
                        "name": "fallback_classifier",
                        "applied": True,
                        "summary": "Primary routing packet failed; compact classifier supplied the route.",
                    }
                )
                trace["final"] = self._clone_trace_payload(fallback)
                trace["summary"] = self._summarize_prethink_trace(trace)
                self._last_prethink_trace = trace
                return fallback, ""
            trace["source"] = "failed"
            trace["summary"] = self._summarize_prethink_trace(trace)
            self._last_prethink_trace = trace
            return None, f"{normalize_error} | Fallback classifier failed: {fallback_error}"
        except Exception as exc:
            fallback, fallback_error = self._compile_prethink_classifier_fallback(utterance)
            trace["primary"]["error"] = str(exc)
            trace["fallback"] = self._clone_trace_payload(self._last_prethink_fallback_trace)
            if fallback is not None:
                trace["source"] = "fallback_classifier"
                trace["rescues"].append(
                    {
                        "name": "fallback_classifier",
                        "applied": True,
                        "summary": "Primary routing packet failed; compact classifier supplied the route.",
                    }
                )
                trace["final"] = self._clone_trace_payload(fallback)
                trace["summary"] = self._summarize_prethink_trace(trace)
                self._last_prethink_trace = trace
                return fallback, ""
            trace["source"] = "failed"
            trace["summary"] = self._summarize_prethink_trace(trace)
            self._last_prethink_trace = trace
            return None, f"{exc} | Fallback classifier failed: {fallback_error}"

    def _compile_prethink_semantics_with_semantic_ir(self, utterance: str) -> tuple[dict[str, Any] | None, str]:
        self._last_prethink_trace = {}
        self._last_prethink_fallback_trace = {}
        ir, error = self._compile_semantic_ir(utterance)
        trace = {
            "utterance": utterance,
            "source": "semantic_ir_v1",
            "compiler_mode": self._compiler_mode,
            "model": self._semantic_ir_model,
            "semantic_ir": self._clone_trace_payload(self._last_semantic_ir_trace),
            "rescues": [],
            "final": None,
        }
        if not isinstance(ir, dict):
            trace["source"] = "failed"
            trace["summary"] = self._summarize_prethink_trace(trace)
            self._last_prethink_trace = trace
            return None, error or "semantic_ir_v1 failed"
        compiled = semantic_ir_to_prethink_payload(ir)
        trace["final"] = self._clone_trace_payload(compiled)
        trace["rescues"].append(
            {
                "name": "semantic_ir_prethink_projection",
                "applied": True,
                "summary": "Projected semantic_ir_v1 decision into the pre-think routing packet.",
            }
        )
        trace["summary"] = self._summarize_prethink_trace(trace)
        self._last_prethink_trace = trace
        return compiled, ""

    def _freethinker_trace_for_front_door(
        self,
        *,
        utterance: str,
        front_door: dict[str, Any] | None,
    ) -> dict[str, Any]:
        needs_clarification = bool((front_door or {}).get("needs_clarification", False))
        if self._freethinker_resolution_policy == "off":
            return self._build_freethinker_trace(
                utterance=utterance,
                action="skipped",
                reason="policy_off",
                used=False,
            )
        if not needs_clarification:
            return self._build_freethinker_trace(
                utterance=utterance,
                action="skipped",
                reason="not_needed",
                used=False,
            )
        if not self._freethinker_prompt_loaded or not self._freethinker_prompt_text.strip():
            return self._build_freethinker_trace(
                utterance=utterance,
                action="skipped",
                reason="prompt_unavailable",
                used=False,
                error=str(self._freethinker_prompt_load_error or "").strip(),
            )

        context_pack = self._build_freethinker_context_pack(
            utterance=utterance,
            front_door=front_door or {},
        )
        prompt_text = self._build_freethinker_prompt(
            utterance=utterance,
            context_pack=context_pack,
        )
        required_keys = [
            "action",
            "confidence",
            "grounding",
            "proposed_answer",
            "proposed_question",
            "notes",
        ]
        try:
            response = _call_model_prompt(
                backend=self._freethinker_backend,
                base_url=self._freethinker_base_url,
                model=self._freethinker_model,
                prompt_text=prompt_text,
                context_length=self._freethinker_context_length,
                timeout=self._freethinker_timeout,
                api_key=self._freethinker_api_key,
                response_format="json",
                temperature=self._freethinker_temperature,
                think_enabled=self._freethinker_thinking,
            )
        except Exception as exc:
            return self._build_freethinker_trace(
                utterance=utterance,
                action="error",
                reason="model_call_failed",
                used=True,
                prompt_text=prompt_text,
                context_pack=context_pack,
                error=str(exc),
            )

        parsed, _ = _parse_model_json(response, required_keys)
        response_text = str((response.message or "").strip() or (response.reasoning or "").strip())
        if not isinstance(parsed, dict):
            return self._build_freethinker_trace(
                utterance=utterance,
                action="abstain",
                reason="invalid_json",
                used=True,
                prompt_text=prompt_text,
                response_text=response_text,
                context_pack=context_pack,
                error="Freethinker did not return a valid JSON decision object.",
            )

        decision = self._normalize_freethinker_decision(parsed)
        policy = self._freethinker_resolution_policy
        raw_action = decision["action"]
        effective_action = raw_action
        effective_question = ""
        effective_answer = ""
        reason = "decision_applied"
        specific_question = self._freethinker_specific_question(
            utterance=utterance,
            proposed_question=str(decision["proposed_question"]).strip(),
            context_pack=context_pack,
        )

        if raw_action == "ask_user_this":
            effective_question = specific_question or decision["proposed_question"]
            if not effective_question:
                effective_action = "abstain"
                reason = "empty_question"
        elif raw_action == "resolve_from_context":
            proposed_answer = decision["proposed_answer"]
            if policy == "advisory_only":
                effective_question = self._freethinker_confirmation_question(
                    proposed_answer,
                    str((front_door or {}).get("clarification_question", "")).strip(),
                )
                if effective_question:
                    effective_action = "ask_user_this"
                    reason = "confirmation_required_by_policy"
                else:
                    effective_action = "abstain"
                    reason = "confirmation_question_unavailable"
            elif proposed_answer and self._freethinker_can_auto_resolve(
                policy=policy,
                confidence=float(decision["confidence"]),
                grounding=str(decision["grounding"]).strip(),
            ):
                effective_answer = proposed_answer
                effective_action = "resolve_from_context"
                reason = "resolved_from_context"
            elif decision["proposed_question"]:
                effective_question = specific_question or decision["proposed_question"]
                effective_action = "ask_user_this"
                reason = "resolution_below_threshold"
            else:
                effective_action = "abstain"
                reason = "resolution_below_threshold"
        else:
            reason = "abstained"

        trace = self._build_freethinker_trace(
            utterance=utterance,
            action=effective_action,
            reason=reason,
            used=True,
            confidence=float(decision["confidence"]),
            grounding=str(decision["grounding"]).strip(),
            proposed_answer=str(decision["proposed_answer"]).strip(),
            proposed_question=effective_question or str(decision["proposed_question"]).strip(),
            notes=str(decision["notes"]).strip(),
            prompt_text=prompt_text,
            response_text=response_text,
            parsed=parsed,
            context_pack=context_pack,
            decision_action=raw_action,
        )
        trace["effective_question"] = effective_question
        trace["effective_answer"] = effective_answer
        return trace

    def pre_think(self, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        utterance = str(args.get("utterance", "")).strip()
        if not utterance:
            return {"status": "validation_error", "message": "utterance is required"}

        compiled: dict[str, Any] | None = None
        compile_error = ""
        if self._compiler_mode != "heuristic":
            compiled, compile_error = self._compile_prethink_semantics(utterance)
            if compiled is None and self._compiler_mode == "strict":
                failure_trace = self._ensure_prethink_trace(
                    utterance=utterance,
                    compiled=compiled,
                    compile_error=compile_error,
                    packet=None,
                )
                return {
                    "status": "blocked",
                    "result_type": "compiler_failed",
                    "message": (
                        "Pre-think compiler failed in strict mode. "
                        f"Fix the compiler response or switch compiler_mode."
                    ),
                    "details": {
                        "compiler_mode": self._compiler_mode,
                        "compiler_backend": self._compiler_backend,
                        "compiler_base_url": self._compiler_base_url,
                        "compiler_model": self._compiler_model,
                        "compiler_prompt_path": str(self._compiler_prompt_path),
                        "error": compile_error,
                    },
                    "trace": failure_trace,
                }

        lower = utterance.lower()
        looks_like_query = utterance.endswith("?") or lower.startswith(
            ("who ", "what ", "when ", "where ", "why ", "how ", "is ", "are ", "does ", "do ")
        )
        looks_like_write = any(
            token in lower
            for token in (" is ", " are ", " was ", " were ", " if ", " then ", " retract ", " remove ")
        )

        compiler_intent = str((compiled or {}).get("intent", "")).strip()
        intent = compiler_intent or ("query" if looks_like_query else ("assert_fact" if looks_like_write else "other"))
        uncertainty = _clip_01((compiled or {}).get("uncertainty_score"), 0.0)
        compiler_needs_clarification = _coerce_bool((compiled or {}).get("needs_clarification"), False)
        compiler_clarification_question = str((compiled or {}).get("clarification_question", "")).strip()
        compiler_clarification_reason = str((compiled or {}).get("clarification_reason", "")).strip()

        if not self._session.enabled:
            mode = "forward_with_facts"
            note = "pre-think disabled for this session; forwarding without gating."
        elif intent == "query":
            mode = "short_circuit"
            note = "query-like utterance from compiler."
        elif intent in {"assert_fact", "assert_rule", "retract"}:
            mode = "block_or_clarify"
            note = "write-like utterance from compiler; apply gates before mutation."
        else:
            mode = "forward_with_facts"
            note = "other/mixed utterance from compiler."

        coreference = self._build_coreference_hint(utterance)
        segments = self._build_turn_segments(utterance)
        ce_threshold = max(0.0, 1.0 - float(self._session.clarification_eagerness))
        coreference_requires_clarification = bool(coreference.get("clarification_recommended"))
        if (
            self._semantic_ir_enabled
            and not compiler_needs_clarification
            and uncertainty < ce_threshold
        ):
            coreference_requires_clarification = False
            coreference["clarification_override"] = "semantic_ir_confident_commit"
        coreference["clarification_applied"] = bool(coreference_requires_clarification)
        clarification_required = bool(
            compiler_needs_clarification
            or coreference_requires_clarification
            or (uncertainty >= ce_threshold and self._session.enabled)
        )
        clarification_question = compiler_clarification_question or str(
            coreference.get("clarification_question", "")
        ).strip()
        if clarification_required and not clarification_question:
            clarification_question = "Please clarify the intended fact or referent before I continue."
        if not clarification_required:
            clarification_question = ""
        packet = {
            "prethink_id": self._next_prethink_id(),
            "utterance": utterance,
            "mode": mode,
            "signals": {
                "looks_like_query": intent == "query",
                "looks_like_write": intent in {"assert_fact", "assert_rule", "retract"},
                "compiler_intent": intent,
                "compiler_uncertainty_score": uncertainty,
            },
            "coreference": coreference,
            "compiler": {
                "mode": self._compiler_mode,
                "backend": self._compiler_backend,
                "base_url": self._compiler_base_url,
                "model": self._semantic_ir_model if self._semantic_ir_enabled else self._compiler_model,
                "context_length": self._semantic_ir_context_length if self._semantic_ir_enabled else self._compiler_context_length,
                "prompt_enabled": bool(self._compiler_prompt_enabled),
                "prompt_path": str(self._compiler_prompt_path) if self._compiler_prompt_enabled else "",
                "used": compiled is not None,
                "source": "",
                "error": compile_error,
                "intent": intent,
                "needs_clarification": compiler_needs_clarification,
                "clarification_reason": compiler_clarification_reason,
                "semantic_ir_enabled": bool(self._semantic_ir_enabled),
            },
            "execution_protocol": {
                "strategy": "segment_checkpoint_pipeline",
                "steps": [
                    "segment_utterance",
                    "ingest_until_query_boundary",
                    "clarify_if_needed_before_query",
                    "commit_ingest",
                    "run_query",
                    "resume_next_segment",
                ],
                "segments": segments,
                "query_gate_requires_clarification_resolution": clarification_required,
            },
            "clarification": {
                "required_before_query": clarification_required,
                "question": clarification_question,
                "reason": compiler_clarification_reason,
            },
            "requires_user_confirmation": bool(self._session.require_final_confirmation),
            "clarification_eagerness": float(self._session.clarification_eagerness),
            "source_of_truth": "prolog_kb",
            "note": note,
        }
        prethink_trace = self._ensure_prethink_trace(
            utterance=utterance,
            compiled=compiled,
            compile_error=compile_error,
            packet=packet,
        )
        packet["compiler"]["source"] = str(
            ((prethink_trace.get("summary", {}) if isinstance(prethink_trace, dict) else {}) or {}).get("source", "")
        ).strip()
        self._pending_prethink = {
            "prethink_id": packet["prethink_id"],
            "mode": packet["mode"],
            "utterance": utterance,
            "clarification_required_before_query": clarification_required,
            "clarification_question": clarification_question,
            "clarification_reason": compiler_clarification_reason,
            "compiler_intent": intent,
            "compiler_uncertainty_score": uncertainty,
            "clarification_answer": "",
            "segments": segments,
            "writes_applied": 0,
            "queries_executed": 0,
            "query_attempts": 0,
            "query_no_results": 0,
            "no_result_streak": 0,
            "last_query": "",
            "last_query_status": "",
            "compiler_trace": self._clone_trace_payload(prethink_trace),
        }
        return {
            "status": "success",
            "result_type": "pre_think_packet",
            "packet": packet,
            "trace": prethink_trace,
            "state": self._serialize_state(),
        }

    def record_clarification_answer(self, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        pending = self._pending_prethink
        if pending is None:
            return {
                "status": "blocked",
                "result_type": "pre_think_required",
                "message": "No active pre-think turn. Call pre_think first.",
            }
        provided_id = str(args.get("prethink_id", "")).strip()
        expected_id = str(pending.get("prethink_id", "")).strip()
        if not provided_id or provided_id != expected_id:
            return {
                "status": "blocked",
                "result_type": "pre_think_id_mismatch",
                "message": "Provided prethink_id does not match active turn.",
                "required": {"prethink_id": expected_id},
            }
        answer = str(args.get("answer", "")).strip()
        if not answer:
            return {
                "status": "validation_error",
                "message": "answer is required",
            }
        confirmed = _coerce_bool(args.get("confirmed"), True)
        if not confirmed:
            return {
                "status": "blocked",
                "result_type": "clarification_not_confirmed",
                "message": "Clarification was not confirmed; query gate remains active.",
                "pending_prethink": self._pending_prethink_summary(),
            }
        pending["clarification_answer"] = answer
        pending["clarification_required_before_query"] = False
        return {
            "status": "success",
            "result_type": "clarification_recorded",
            "prethink_id": expected_id,
            "answer": answer,
            "state": self._serialize_state(),
        }

    def process_utterance(self, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        utterance = str(args.get("utterance", "")).strip()
        clarification_answer = str(args.get("clarification_answer", "")).strip()
        effective_clarification_answer = clarification_answer
        provided_prethink_id = str(args.get("prethink_id", "")).strip()
        if not utterance:
            return {"status": "validation_error", "message": "utterance is required"}

        prethink: dict[str, Any] | None = None
        prethink_trace: dict[str, Any] | None = None
        freethinker_trace: dict[str, Any] | None = None
        if clarification_answer:
            pending = self._pending_prethink
            if pending is None:
                return {
                    "status": "blocked",
                    "result_type": "pre_think_required",
                    "message": "No active pre-think turn. Call process_utterance without clarification first.",
                    "state": self._serialize_state(),
                }
            expected_id = str(pending.get("prethink_id", "")).strip()
            pending_question = str(pending.get("clarification_question", "")).strip()
            effective_clarification_answer = self._normalize_clarification_answer(
                clarification_question=pending_question,
                clarification_answer=clarification_answer,
            )
            if provided_prethink_id and provided_prethink_id != expected_id:
                return {
                    "status": "blocked",
                    "result_type": "pre_think_id_mismatch",
                    "message": "Provided prethink_id does not match active turn.",
                    "required": {"prethink_id": expected_id},
                    "state": self._serialize_state(),
                }
            clarified = self.record_clarification_answer(
                {
                    "prethink_id": expected_id,
                    "answer": effective_clarification_answer,
                    "confirmed": True,
                }
            )
            if str(clarified.get("status", "")).strip() != "success":
                return clarified
            front_door = self._front_door_from_pending()
            front_door["needs_clarification"] = False
            front_door["clarification_question"] = ""
            front_door["reasons"] = ["clarification_resolved"]
            prethink_trace = self._clone_trace_payload(pending.get("compiler_trace", {}))
            freethinker_trace = self._freethinker_trace_for_front_door(
                utterance=utterance,
                front_door=front_door,
            )
            front_door, freethinker_answer = self._apply_freethinker_front_door(
                front_door=front_door,
                freethinker_trace=freethinker_trace,
            )
            if freethinker_answer:
                effective_clarification_answer = freethinker_answer
        else:
            prethink = self.pre_think({"utterance": utterance})
            if str(prethink.get("status", "")).strip() != "success":
                prethink_message = str(prethink.get("message", "pre_think failed")).strip() or "pre_think failed"
                failure_prethink_trace = self._clone_trace_payload(prethink.get("trace", {}))
                freethinker_trace = self._build_freethinker_trace(
                    utterance=utterance,
                    action="skipped",
                    reason="prethink_failed",
                    used=False,
                )
                compiler_trace = {
                    "prethink": failure_prethink_trace,
                    "freethinker": freethinker_trace,
                    "summary": self._summarize_compiler_trace(
                        prethink_trace=failure_prethink_trace if isinstance(failure_prethink_trace, dict) else None,
                        parse_trace=None,
                        freethinker_trace=freethinker_trace,
                    ),
                }
                return {
                    "status": str(prethink.get("status", "")).strip() or "error",
                    "result_type": str(prethink.get("result_type", "prethink_failed")).strip() or "prethink_failed",
                    "message": prethink_message,
                    "front_door": {
                        "route": "other",
                        "compiler_intent": "other",
                        "looks_like_query": False,
                        "looks_like_write": False,
                        "ambiguity_score": 1.0,
                        "needs_clarification": True,
                        "reasons": [prethink_message],
                        "clarification_question": "Compiler failed to produce a valid routing packet. Retry or inspect the compiler error.",
                        "prethink_id": "",
                        "compiler": {
                            "mode": self._compiler_mode,
                            "model": self._compiler_model,
                            "backend": self._compiler_backend,
                            "base_url": self._compiler_base_url,
                            "strict_mode": self._compiler_mode == "strict",
                            "used": False,
                            "error": prethink_message,
                        },
                        "session_snapshot": {
                            "pending_prethink": self._pending_prethink_summary(),
                        },
                        "prethink": prethink,
                    },
                    "execution": None,
                    "compiler_trace": compiler_trace,
                    "state": self._serialize_state(),
                }
            packet = prethink.get("packet", {}) if isinstance(prethink.get("packet"), dict) else {}
            prethink_trace = self._clone_trace_payload(prethink.get("trace", {}))
            front_door = self._front_door_from_packet(packet=packet, prethink=prethink)
            freethinker_trace = self._freethinker_trace_for_front_door(
                utterance=utterance,
                front_door=front_door,
            )
            front_door, freethinker_answer = self._apply_freethinker_front_door(
                front_door=front_door,
                freethinker_trace=freethinker_trace,
            )
            if freethinker_answer:
                effective_clarification_answer = freethinker_answer
            if bool(front_door.get("needs_clarification")):
                compiler_trace = {
                    "prethink": prethink_trace,
                    "freethinker": freethinker_trace,
                    "summary": self._summarize_compiler_trace(
                        prethink_trace=prethink_trace if isinstance(prethink_trace, dict) else None,
                        parse_trace=None,
                        freethinker_trace=freethinker_trace,
                    ),
                }
                return {
                    "status": "clarification_required",
                    "result_type": "clarification_required",
                    "front_door": front_door,
                    "clarification": {
                        "question": str(front_door.get("clarification_question", "")).strip(),
                        "reasons": list(front_door.get("reasons", [])),
                    },
                    "execution": None,
                    "compiler_trace": compiler_trace,
                    "state": self._serialize_state(),
                }

        prethink_id = str(front_door.get("prethink_id", "")).strip() or str(
            (self._pending_prethink or {}).get("prethink_id", "")
        ).strip()
        compiler_intent = str(front_door.get("compiler_intent", "other")).strip() or "other"
        parsed, error = self._compile_apply_parse(
            utterance=utterance,
            compiler_intent=compiler_intent,
            clarification_question=str(front_door.get("clarification_question", "")).strip(),
            clarification_answer=effective_clarification_answer,
        )
        parse_trace = self._ensure_parse_trace(
            utterance=utterance,
            compiler_intent=compiler_intent,
            clarification_answer=effective_clarification_answer,
            parsed=parsed if isinstance(parsed, dict) else None,
            error=error,
        )
        compiler_trace = {
            "prethink": prethink_trace if isinstance(prethink_trace, dict) else None,
            "freethinker": freethinker_trace,
            "parse": parse_trace,
            "summary": self._summarize_compiler_trace(
                prethink_trace=prethink_trace if isinstance(prethink_trace, dict) else None,
                parse_trace=parse_trace,
                freethinker_trace=freethinker_trace,
            ),
        }
        if not isinstance(parsed, dict):
            execution = {
                "status": "error",
                "intent": compiler_intent,
                "writes_applied": 0,
                "operations": [],
                "query_result": None,
                "parse": {},
                "errors": [error or "parse failed"],
            }
            return {
                "status": "error",
                "result_type": "parse_failed",
                "front_door": front_door,
                "execution": execution,
                "compiler_trace": compiler_trace,
                "state": self._serialize_state(),
            }

        execution = self._apply_compiled_parse(parsed=parsed, prethink_id=prethink_id)
        self._remember_turn_outcome(
            utterance=utterance,
            front_door=front_door,
            execution=execution,
        )
        return {
            "status": str(execution.get("status", "")).strip() or "success",
            "result_type": "utterance_processed",
            "front_door": front_door,
            "execution": execution,
            "compiler_trace": compiler_trace,
            "state": self._serialize_state(),
        }

    def _build_coreference_hint(self, utterance: str) -> dict[str, Any]:
        clauses = self._split_clauses(utterance)
        people_seen: list[str] = []
        speaker_name = ""
        anchor_name = ""
        spouse_name = ""
        child_names: list[str] = []
        active_group: list[str] = []
        has_they = False
        except_names: list[str] = []

        for clause in clauses:
            tokens = self._tokenize_words(clause)
            lower_tokens = [token.lower() for token in tokens]
            if not tokens:
                continue

            intro_name = self._name_after_sequence(tokens, ("i", "am"))
            if intro_name:
                speaker_name = intro_name
                people_seen = self._append_unique(people_seen, intro_name)
                active_group = self._append_unique(active_group, intro_name)

            for relation in ("brother", "sister", "mother", "father", "wife", "husband"):
                rel_name = self._name_after_relation(tokens, relation)
                if rel_name:
                    people_seen = self._append_unique(people_seen, rel_name)
                    if relation in {"brother", "father", "husband"}:
                        anchor_name = rel_name
                    if relation in {"wife", "husband"}:
                        spouse_name = rel_name
                    if speaker_name and relation in {"brother", "sister", "mother", "father"}:
                        active_group = self._append_unique([speaker_name], rel_name)
                    elif relation in {"wife", "husband"} and anchor_name:
                        active_group = self._append_unique([anchor_name], rel_name)

            if "he" in lower_tokens and anchor_name:
                active_group = self._append_unique(active_group, anchor_name)
            if "she" in lower_tokens and spouse_name:
                active_group = self._append_unique(active_group, spouse_name)

            plural_children = self._names_after_plural_relation(tokens, "sons")
            plural_children += self._names_after_plural_relation(tokens, "daughters")
            if plural_children:
                for child in plural_children:
                    people_seen = self._append_unique(people_seen, child)
                    child_names = self._append_unique(child_names, child)
                family_group: list[str] = []
                if anchor_name:
                    family_group = self._append_unique(family_group, anchor_name)
                if spouse_name:
                    family_group = self._append_unique(family_group, spouse_name)
                for child in child_names:
                    family_group = self._append_unique(family_group, child)
                if family_group:
                    active_group = family_group

            if "they" in lower_tokens:
                has_they = True
                if not active_group:
                    active_group = people_seen[-4:]

            if "except" in lower_tokens:
                except_names = self._append_unique(
                    except_names,
                    *self._names_after_keyword(tokens, "except"),
                )

        pronoun_bindings: list[dict[str, Any]] = []
        clarification_recommended = False
        clarification_question = ""

        if has_they:
            resolved = list(active_group)
            if not resolved:
                resolved = list(people_seen[-3:])
            excluded = [name for name in except_names if name in resolved]
            effective = [name for name in resolved if name not in excluded]

            confidence = 0.65
            if resolved and (anchor_name or spouse_name):
                confidence = 0.83
            if excluded:
                confidence = min(0.93, confidence + 0.08)
            if len(resolved) <= 1:
                confidence = min(confidence, 0.55)

            clarification_recommended = confidence < 0.8 or len(effective) <= 1
            if clarification_recommended:
                if effective:
                    joined = ", ".join(effective)
                    clarification_question = (
                        "When you said 'they', should I apply this to: "
                        f"{joined}?"
                    )
                else:
                    clarification_question = (
                        "When you said 'they', who exactly should receive this fact?"
                    )

            pronoun_bindings.append(
                {
                    "pronoun": "they",
                    "resolved_entities": resolved,
                    "excluded_entities": excluded,
                    "effective_entities": effective,
                    "confidence": round(confidence, 2),
                    "resolution_basis": "discourse-group",
                }
            )

        return {
            "pronoun_bindings": pronoun_bindings,
            "clarification_recommended": clarification_recommended,
            "clarification_question": clarification_question,
        }

    def _build_turn_segments(self, utterance: str) -> list[dict[str, Any]]:
        clauses = self._split_clauses(utterance)
        segments: list[dict[str, Any]] = []
        for index, clause in enumerate(clauses, start=1):
            text = clause.strip()
            lower = text.lower()
            is_query = text.endswith("?") or lower.startswith(
                ("who ", "what ", "when ", "where ", "why ", "how ", "is ", "are ", "does ", "do ")
            )
            is_ingest = any(
                token in f" {lower} "
                for token in (" is ", " are ", " was ", " were ", " has ", " have ", " had ", " if ", " then ")
            ) and not is_query
            if is_query:
                phase = "query"
            elif is_ingest:
                phase = "ingest"
            else:
                phase = "context"
            segments.append(
                {
                    "index": index,
                    "phase": phase,
                    "text": text,
                    "checkpoint": "pending",
                }
            )
        return segments

    def _query_rows_with_fallback(self, query: str) -> dict[str, Any]:
        primary = self.query_rows(query)
        if str(primary.get("status", "")).strip() != "no_results":
            return primary
        entities = self._pending_where_live_entities()
        if len(entities) < 2:
            return primary
        fallback = self._lookup_lives_in_entities(entities)
        if str(fallback.get("status", "")).strip() != "success":
            return primary
        merged = dict(fallback)
        merged["fallback_applied"] = True
        merged["fallback_reason"] = "query_shape_repaired_from_pending_utterance"
        merged["original_query"] = str(query).strip()
        merged["fallback_query"] = self._format_entities_lives_query(entities)
        return merged

    def _pending_where_live_entities(self) -> list[str]:
        pending = self._pending_prethink
        if pending is None:
            return []
        utterance = str(pending.get("utterance", "")).strip()
        if not utterance:
            return []
        return self._extract_where_live_entities(utterance)

    def _format_entities_lives_query(self, entities: list[str]) -> str:
        clauses: list[str] = []
        for index, entity in enumerate(entities):
            atom = self._to_prolog_atom(entity)
            var_name = self._entity_place_variable(entity, index)
            clauses.append(f"lives_in({atom}, {var_name})")
        return ", ".join(clauses) + "."

    def _lookup_lives_in_entities(self, entities: list[str]) -> dict[str, Any]:
        rows: list[dict[str, Any]] = [{}]
        variables: list[str] = []
        subqueries: list[str] = []
        for index, entity in enumerate(entities):
            atom = self._to_prolog_atom(entity)
            var_name = self._entity_place_variable(entity, index)
            variables.append(var_name)
            subquery = f"lives_in({atom}, {var_name})."
            subqueries.append(subquery)
            result = self.query_rows(subquery)
            if str(result.get("status", "")).strip() != "success":
                return {
                    "status": "no_results",
                    "result_type": "no_result",
                    "predicate": "lives_in",
                    "prolog_query": self._format_entities_lives_query(entities),
                    "variables": variables,
                    "rows": [],
                    "num_rows": 0,
                    "missing_entity": atom,
                    "subqueries": subqueries,
                    "reasoning_basis": {"kind": "core-local"},
                }
            values: list[str] = []
            for row in result.get("rows", []):
                value = str(row.get(var_name, "")).strip()
                if value:
                    values.append(value)
            if not values:
                return {
                    "status": "no_results",
                    "result_type": "no_result",
                    "predicate": "lives_in",
                    "prolog_query": self._format_entities_lives_query(entities),
                    "variables": variables,
                    "rows": [],
                    "num_rows": 0,
                    "missing_entity": atom,
                    "subqueries": subqueries,
                    "reasoning_basis": {"kind": "core-local"},
                }
            expanded_rows: list[dict[str, Any]] = []
            for base in rows:
                for value in values:
                    merged = dict(base)
                    merged[var_name] = value
                    expanded_rows.append(merged)
            rows = expanded_rows

        return {
            "status": "success",
            "result_type": "table",
            "predicate": "lives_in",
            "prolog_query": self._format_entities_lives_query(entities),
            "variables": variables,
            "rows": rows,
            "num_rows": len(rows),
            "subqueries": subqueries,
            "reasoning_basis": {"kind": "core-local"},
        }

    def _extract_where_live_entities(self, utterance: str) -> list[str]:
        tokens = self._tokenize_words(utterance)
        lower_tokens = [token.lower() for token in tokens]
        if "where" not in lower_tokens:
            return []
        if "live" not in lower_tokens and "lives" not in lower_tokens:
            return []

        where_index = lower_tokens.index("where")
        live_index = -1
        for index in range(where_index + 1, len(lower_tokens)):
            if lower_tokens[index] in {"live", "lives"}:
                live_index = index
                break
        if live_index <= where_index:
            return []

        between = lower_tokens[where_index + 1 : live_index]
        stopwords = {
            "does",
            "do",
            "is",
            "are",
            "the",
            "a",
            "an",
            "in",
            "at",
            "to",
            "for",
            "of",
            "and",
            "or",
        }
        entities: list[str] = []
        for token in between:
            cleaned = token.strip()
            if not cleaned or cleaned in stopwords:
                continue
            if cleaned.isalpha():
                entities = self._append_unique(entities, cleaned)
        return entities

    def _to_prolog_atom(self, value: str) -> str:
        chars: list[str] = []
        for ch in value.lower():
            if ch.isalnum():
                chars.append(ch)
            else:
                chars.append("_")
        atom = "".join(chars).strip("_")
        while "__" in atom:
            atom = atom.replace("__", "_")
        return atom or "unknown"

    def _entity_place_variable(self, entity: str, index: int) -> str:
        letters: list[str] = []
        for ch in entity:
            if ch.isalpha():
                letters.append(ch)
        base = "".join(letters)
        if not base:
            base = f"Entity{index + 1}"
        label = base[0].upper() + base[1:]
        return f"{label}Place"

    def _split_clauses(self, text: str) -> list[str]:
        provisional = text.replace(";", ".").replace(" - ", ".").replace(" -", ".").replace("- ", ".")
        clauses: list[str] = []
        for piece in provisional.split("."):
            chunk = piece.strip()
            if chunk:
                clauses.append(chunk)
        return clauses

    def _tokenize_words(self, text: str) -> list[str]:
        tokens: list[str] = []
        normalized = text.replace(",", " ").replace(":", " ").replace("!", " ").replace("?", " ")
        normalized = normalized.replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " ")
        normalized = normalized.replace("{", " ").replace("}", " ").replace("/", " ")
        for raw in normalized.split():
            cleaned = raw.strip(" .;\"'`")
            if cleaned:
                tokens.append(cleaned)
        return tokens

    def _is_name_token(self, token: str) -> bool:
        if not token:
            return False
        lower = token.lower()
        blocked = {
            "i",
            "my",
            "his",
            "her",
            "their",
            "they",
            "he",
            "she",
            "it",
            "we",
            "you",
            "and",
            "or",
            "in",
            "on",
            "at",
            "to",
            "from",
            "is",
            "are",
            "was",
            "were",
            "has",
            "have",
            "had",
            "except",
            "if",
            "then",
            "who",
            "what",
            "where",
            "when",
            "why",
            "how",
        }
        if lower in blocked:
            return False
        if not token[0].isalpha():
            return False
        return token[0].isupper()

    def _append_unique(self, items: list[str], *names: str) -> list[str]:
        out = list(items)
        seen = {name.lower() for name in out}
        for name in names:
            clean = str(name).strip()
            if not clean:
                continue
            key = clean.lower()
            if key not in seen:
                out.append(clean)
                seen.add(key)
        return out

    def _name_after_sequence(self, tokens: list[str], sequence: tuple[str, ...]) -> str:
        lower_tokens = [token.lower() for token in tokens]
        if len(tokens) < len(sequence) + 1:
            return ""
        for index in range(len(tokens) - len(sequence)):
            matched = True
            for offset, piece in enumerate(sequence):
                if lower_tokens[index + offset] != piece:
                    matched = False
                    break
            if not matched:
                continue
            next_index = index + len(sequence)
            if next_index < len(tokens) and self._is_name_token(tokens[next_index]):
                return tokens[next_index]
        return ""

    def _name_after_relation(self, tokens: list[str], relation: str) -> str:
        lower_tokens = [token.lower() for token in tokens]
        for index, token in enumerate(lower_tokens):
            if token != relation:
                continue
            for cursor in range(index + 1, min(index + 6, len(tokens))):
                if lower_tokens[cursor] == "is":
                    for next_index in range(cursor + 1, min(cursor + 4, len(tokens))):
                        if self._is_name_token(tokens[next_index]):
                            return tokens[next_index]
        return ""

    def _names_after_plural_relation(self, tokens: list[str], relation: str) -> list[str]:
        lower_tokens = [token.lower() for token in tokens]
        names: list[str] = []
        for index, token in enumerate(lower_tokens):
            if token != relation:
                continue
            for cursor in range(index + 1, len(tokens)):
                lower_value = lower_tokens[cursor]
                if lower_value in {"and", "two", "2", "three", "3"}:
                    continue
                if lower_value in {"who", "that", "which", "live", "lives", "in", "except"}:
                    break
                if self._is_name_token(tokens[cursor]):
                    names = self._append_unique(names, tokens[cursor])
                elif names:
                    break
        return names

    def _names_after_keyword(self, tokens: list[str], keyword: str) -> list[str]:
        lower_tokens = [token.lower() for token in tokens]
        names: list[str] = []
        for index, token in enumerate(lower_tokens):
            if token != keyword:
                continue
            for cursor in range(index + 1, len(tokens)):
                lower_value = lower_tokens[cursor]
                if lower_value in {"and"}:
                    continue
                if lower_value in {"he", "she", "they", "who", "that"}:
                    break
                if self._is_name_token(tokens[cursor]):
                    names = self._append_unique(names, tokens[cursor])
                elif names:
                    break
        return names

    def _next_prethink_id(self) -> str:
        token = f"pt-{self._prethink_counter:06d}"
        self._prethink_counter += 1
        return token

    def _pending_prethink_summary(self) -> dict[str, Any]:
        if self._pending_prethink is None:
            return {}
        return {
            "prethink_id": str(self._pending_prethink.get("prethink_id", "")),
            "mode": str(self._pending_prethink.get("mode", "")),
            "utterance": str(self._pending_prethink.get("utterance", "")),
            "compiler_intent": str(self._pending_prethink.get("compiler_intent", "")),
            "compiler_uncertainty_score": float(self._pending_prethink.get("compiler_uncertainty_score", 0.0)),
            "clarification_required_before_query": bool(
                self._pending_prethink.get("clarification_required_before_query", False)
            ),
            "clarification_question": str(self._pending_prethink.get("clarification_question", "")),
            "writes_applied": int(self._pending_prethink.get("writes_applied", 0)),
            "queries_executed": int(self._pending_prethink.get("queries_executed", 0)),
            "query_attempts": int(self._pending_prethink.get("query_attempts", 0)),
            "query_no_results": int(self._pending_prethink.get("query_no_results", 0)),
            "no_result_streak": int(self._pending_prethink.get("no_result_streak", 0)),
        }

    def _tool_requires_prethink(self, tool: str) -> bool:
        if tool in {"assert_fact", "assert_rule", "retract_fact"}:
            return bool(self._session.enabled)
        if tool == "query_rows":
            return bool(self._session.enabled and self._session.all_turns_require_prethink)
        return False

    def _check_prethink_gate(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any] | None:
        pending = self._pending_prethink
        provided_id = str(arguments.get("prethink_id", "")).strip()
        gate_required = self._tool_requires_prethink(tool)
        # Even when query pre-think is not globally required, honor gate logic if
        # caller provides prethink_id for an active turn (LM Studio manual flow).
        if tool == "query_rows" and provided_id and pending is not None:
            gate_required = True
        if not gate_required:
            return None

        if pending is None:
            return {
                "status": "blocked",
                "result_type": "pre_think_required",
                "message": (
                    "Call pre_think first for this turn and pass returned prethink_id to this tool."
                ),
                "required": {
                    "tool": tool,
                    "call_pre_think": True,
                    "confirm_required": bool(
                        tool in {"assert_fact", "assert_rule", "retract_fact"}
                        and self._session.require_final_confirmation
                    ),
                },
                "state": self._serialize_state(),
            }

        expected_id = str(pending.get("prethink_id", "")).strip()
        if not provided_id or provided_id != expected_id:
            return {
                "status": "blocked",
                "result_type": "pre_think_id_mismatch",
                "message": (
                    "This tool call must include the active prethink_id from the latest pre_think packet."
                ),
                "required": {"tool": tool, "prethink_id": expected_id},
                "pending_prethink": self._pending_prethink_summary(),
                "state": self._serialize_state(),
            }

        if tool in {"assert_fact", "assert_rule", "retract_fact"}:
            if self._session.require_final_confirmation and not _coerce_bool(
                arguments.get("confirm"),
                False,
            ):
                return {
                    "status": "blocked",
                    "result_type": "confirmation_required",
                    "message": (
                        "Write intents require explicit confirmation. Re-issue with confirm=true."
                    ),
                    "required": {"tool": tool, "prethink_id": expected_id, "confirm": True},
                    "pending_prethink": self._pending_prethink_summary(),
                    "state": self._serialize_state(),
                }
        if tool == "query_rows" and bool(pending.get("clarification_required_before_query", False)):
            return {
                "status": "blocked",
                "result_type": "clarification_required_before_query",
                "message": (
                    "Resolve clarification before running query for this turn."
                ),
                "required": {
                    "tool": "record_clarification_answer",
                    "prethink_id": expected_id,
                    "answer_required": True,
                },
                "clarification_question": str(pending.get("clarification_question", "")).strip(),
                "pending_prethink": self._pending_prethink_summary(),
                "state": self._serialize_state(),
            }

        if tool == "query_rows":
            no_result_streak = int(pending.get("no_result_streak", 0))
            query_attempts = int(pending.get("query_attempts", 0))
            writes_applied = int(pending.get("writes_applied", 0))
            if no_result_streak >= 2 and writes_applied == 0:
                return {
                    "status": "blocked",
                    "result_type": "query_loop_guard",
                    "message": (
                        "Repeated no-result queries detected for this pre-think turn. "
                        "Stop query retries and issue a fresh pre_think with a concrete user utterance."
                    ),
                    "required": {
                        "action": "call_pre_think_with_new_user_utterance",
                        "reason": "repeated_no_result_streak",
                    },
                    "pending_prethink": self._pending_prethink_summary(),
                    "state": self._serialize_state(),
                }
            if query_attempts >= 6 and writes_applied == 0:
                return {
                    "status": "blocked",
                    "result_type": "query_loop_guard",
                    "message": (
                        "Query attempt limit reached with no committed context updates for this turn. "
                        "Start a new pre_think turn."
                    ),
                    "required": {
                        "action": "call_pre_think_with_new_user_utterance",
                        "reason": "query_attempt_limit",
                    },
                    "pending_prethink": self._pending_prethink_summary(),
                    "state": self._serialize_state(),
                }

        return None

    def _consume_prethink_after_call(self, tool: str, result: dict[str, Any]) -> None:
        # Keep prethink authorization alive for the full utterance turn so
        # mixed sequences can run with one packet:
        # ingest -> query -> ingest -> query.
        # A new `pre_think` call opens the next turn and replaces this state.
        pending = self._pending_prethink
        if pending is None:
            return
        status = str(result.get("status", "")).strip()
        if tool in {"assert_fact", "assert_rule", "retract_fact"}:
            if status != "success":
                return
            pending["writes_applied"] = int(pending.get("writes_applied", 0)) + 1
        if tool == "query_rows":
            pending["query_attempts"] = int(pending.get("query_attempts", 0)) + 1
            query_text = str(result.get("prolog_query", "")).strip().lower()
            last_query = str(pending.get("last_query", "")).strip().lower()
            last_status = str(pending.get("last_query_status", "")).strip()
            if status == "success":
                pending["queries_executed"] = int(pending.get("queries_executed", 0)) + 1
                pending["no_result_streak"] = 0
            elif status == "no_results":
                pending["query_no_results"] = int(pending.get("query_no_results", 0)) + 1
                if query_text and query_text == last_query and last_status == "no_results":
                    pending["no_result_streak"] = int(pending.get("no_result_streak", 0)) + 1
                else:
                    pending["no_result_streak"] = 1
            else:
                pending["no_result_streak"] = 0
            pending["last_query"] = query_text
            pending["last_query_status"] = status
        return

    def _serialize_state(self) -> dict[str, Any]:
        state = {
            "enabled": bool(self._session.enabled),
            "all_turns_require_prethink": bool(self._session.all_turns_require_prethink),
            "clarification_eagerness": round(float(self._session.clarification_eagerness), 4),
            "require_final_confirmation": bool(self._session.require_final_confirmation),
            "compiler_mode": self._compiler_mode,
            "compiler_backend": self._compiler_backend,
            "compiler_base_url": self._compiler_base_url,
            "compiler_model": self._compiler_model,
            "compiler_context_length": self._compiler_context_length,
            "compiler_prompt_path": str(self._compiler_prompt_path),
            "compiler_prompt_loaded": bool(self._compiler_prompt_loaded),
            "semantic_ir_enabled": bool(self._semantic_ir_enabled),
            "semantic_ir_model": self._semantic_ir_model,
            "semantic_ir_context_length": self._semantic_ir_context_length,
            "semantic_ir_timeout": self._semantic_ir_timeout,
            "semantic_ir_temperature": self._semantic_ir_temperature,
            "semantic_ir_top_p": self._semantic_ir_top_p,
            "semantic_ir_top_k": self._semantic_ir_top_k,
            "semantic_ir_thinking": bool(self._semantic_ir_thinking),
            "active_profile": self._active_profile,
            "profile_known_predicates": list(self._profile_known_predicates),
            "profile_umls_bridge_loaded": bool(self._profile_umls_bridge.get("loaded")),
            "profile_umls_bridge_concepts": len(self._profile_umls_bridge.get("concepts", {}) or {}),
            "profile_load_error": str(self._profile_load_error or "").strip(),
            "freethinker_resolution_policy": self._freethinker_resolution_policy,
            "freethinker_backend": self._freethinker_backend,
            "freethinker_base_url": self._freethinker_base_url,
            "freethinker_model": self._freethinker_model,
            "freethinker_context_length": self._freethinker_context_length,
            "freethinker_timeout": self._freethinker_timeout,
            "freethinker_temperature": self._freethinker_temperature,
            "freethinker_thinking": bool(self._freethinker_thinking),
            "freethinker_prompt_path": str(self._freethinker_prompt_path),
            "freethinker_prompt_loaded": bool(self._freethinker_prompt_loaded),
            "pending_prethink": self._pending_prethink_summary(),
        }
        if self._kb_path:
            state["knowledge_base_path"] = self._kb_path
        return state

    def _trace(self, event: str, payload: dict[str, Any]) -> None:
        try:
            self._trace_path.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "event": event,
                "payload": self._json_safe(payload),
            }
            with self._trace_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            # Logging must never break request handling.
            return

    def _json_safe(self, value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, dict):
            return {str(key): self._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._json_safe(item) for item in value]
        return str(value)

    def _format_row_inline(self, row: dict[str, Any]) -> str:
        if not isinstance(row, dict) or not row:
            return "(empty)"
        items = [f"{key}={value}" for key, value in row.items()]
        return ", ".join(items)

    def _human_tool_text(self, result: dict[str, Any]) -> str:
        status = str(result.get("status", "")).strip() or "unknown"
        result_type = str(result.get("result_type", "")).strip()
        message = str(result.get("message", "")).strip()

        if result_type == "table":
            query = str(result.get("prolog_query", "")).strip()
            rows = result.get("rows", [])
            if not isinstance(rows, list):
                rows = []
            preview_rows = [self._format_row_inline(row) for row in rows[:8] if isinstance(row, dict)]
            preview = " | ".join(preview_rows) if preview_rows else "(no rows)"
            num_rows = int(result.get("num_rows", len(rows)) or 0)
            return f"query={query}; status={status}; rows={num_rows}; preview={preview}"

        if result_type == "no_result":
            query = str(result.get("prolog_query", "")).strip()
            return f"query={query}; status=no_results"

        if result_type == "fact_asserted":
            return f"fact_asserted={str(result.get('fact', '')).strip()}"

        if result_type == "rule_asserted":
            return f"rule_asserted={str(result.get('rule', '')).strip()}"

        if result_type == "fact_retracted":
            return f"fact_retracted={str(result.get('fact', '')).strip()}"

        if result_type == "session_updated":
            state = result.get("state", {})
            if isinstance(state, dict):
                enabled = state.get("enabled")
                eagerness = state.get("clarification_eagerness")
                require_confirm = state.get("require_final_confirmation")
                return (
                    "session_updated;"
                    f" enabled={enabled};"
                    f" clarification_eagerness={eagerness};"
                    f" require_final_confirmation={require_confirm}"
                )
            return "session_updated"

        if result_type == "session_state":
            state = result.get("state", {})
            if isinstance(state, dict):
                enabled = state.get("enabled")
                pending = bool(state.get("pending_prethink"))
                return f"session_state; enabled={enabled}; pending_prethink={pending}"
            return "session_state"

        if result_type == "pre_think_packet":
            packet = result.get("packet", {})
            if isinstance(packet, dict):
                mode = packet.get("mode")
                prethink_id = packet.get("prethink_id")
                clar = packet.get("clarification", {})
                clar_required = bool(clar.get("required_before_query")) if isinstance(clar, dict) else False
                return (
                    "pre_think_packet;"
                    f" id={prethink_id};"
                    f" mode={mode};"
                    f" clarification_required_before_query={clar_required}"
                )
            return "pre_think_packet"

        if result_type == "clarification_recorded":
            return f"clarification_recorded; prethink_id={str(result.get('prethink_id', '')).strip()}"

        if message:
            return f"status={status}; message={message}"
        return f"status={status}"

    def _format_tool_result(self, result: dict[str, Any]) -> dict[str, Any]:
        sanitized = self._json_safe(result)
        is_error = str(sanitized.get("status", "")).strip() in {
            "error",
            "validation_error",
            "not_found",
            "blocked",
        }
        text = self._human_tool_text(sanitized)
        return {
            "content": [{"type": "text", "text": text}],
            "structuredContent": sanitized,
            "isError": is_error,
        }

    def _negotiate_protocol_version(self, requested: str | None) -> str:
        if requested in self.SUPPORTED_PROTOCOL_VERSIONS:
            return str(requested)
        return self.SUPPORTED_PROTOCOL_VERSIONS[0]

    def process_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", self._request_id)
        try:
            self._request_id = int(request_id) + 1
        except Exception:
            self._request_id += 1

        if method == "initialize":
            requested_protocol = params.get("protocolVersion") if isinstance(params, dict) else None
            negotiated = self._negotiate_protocol_version(str(requested_protocol) if requested_protocol else None)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": negotiated,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "prethinker", "version": "0.1"},
                    "instructions": (
                        "Use pre_think and deterministic runtime tools; pre_think is compiler-bound in strict mode."
                    ),
                },
            }

        if method == "notifications/initialized":
            return None

        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}

        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": self.get_tools()}}

        if method == "tools/call":
            tool_name = ""
            tool_args: dict[str, Any] = {}
            if isinstance(params, dict):
                tool_name = str(params.get("name", "")).strip()
                raw_args = params.get("arguments", {})
                if isinstance(raw_args, dict):
                    tool_args = raw_args
            result = self.handle_tool_call(tool_name, tool_args)
            return {"jsonrpc": "2.0", "id": request_id, "result": self._format_tool_result(result)}

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prethinker MCP Server")
    parser.add_argument("--kb-path", default="", help="Optional KB path label for metadata.")
    parser.add_argument("--stdio", action="store_true", help="Use stdio transport (for LM Studio).")
    parser.add_argument("--test", action="store_true", help="Print available tools and exit.")
    parser.add_argument(
        "--env-file",
        default="",
        help="Optional env file for API keys. Defaults to local .env.local when present.",
    )
    parser.add_argument(
        "--compiler-mode",
        choices=["strict", "auto", "heuristic"],
        default="strict",
        help="Pre-think compiler mode: strict binds to compiler model, auto falls back to heuristics, heuristic skips compiler.",
    )
    parser.add_argument("--compiler-backend", default="ollama", help="Compiler backend (ollama or lmstudio).")
    parser.add_argument("--compiler-base-url", default="http://127.0.0.1:11434", help="Compiler backend base URL.")
    parser.add_argument("--compiler-model", default="qwen3.5:9b", help="Compiler model tag.")
    parser.add_argument("--compiler-context-length", type=int, default=8192, help="Compiler context length.")
    parser.add_argument("--compiler-timeout", type=int, default=60, help="Compiler timeout in seconds.")
    parser.add_argument(
        "--compiler-prompt-file",
        default=str(REPO_ROOT / "modelfiles" / "semantic_parser_system_prompt.md"),
        help="System prompt file used by compiler model.",
    )
    args = parser.parse_args()
    _bootstrap_env_from_local_file(args.env_file)

    server = PrologMCPServer(
        kb_path=args.kb_path,
        compiler_mode=args.compiler_mode,
        compiler_backend=args.compiler_backend,
        compiler_base_url=args.compiler_base_url,
        compiler_model=args.compiler_model,
        compiler_context_length=args.compiler_context_length,
        compiler_timeout=args.compiler_timeout,
        compiler_prompt_file=args.compiler_prompt_file,
    )

    if args.test:
        print("Prethinker MCP server initialized\n")
        for tool in server.get_tools():
            print(f"- {tool['name']}: {tool['description']}")
        return 0

    if args.stdio:
        print("Prethinker MCP server ready (stdio)", file=sys.stderr)
        try:
            for line in sys.stdin:
                text = line.strip()
                if not text:
                    continue
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    print(json.dumps({"error": "Invalid JSON", "received": text}))
                    sys.stdout.flush()
                    continue

                if isinstance(payload, list):
                    responses: list[dict[str, Any]] = []
                    for req in payload:
                        if not isinstance(req, dict):
                            continue
                        resp = server.process_request(req)
                        if resp is not None:
                            responses.append(resp)
                    if responses:
                        print(json.dumps(responses))
                        sys.stdout.flush()
                elif isinstance(payload, dict):
                    resp = server.process_request(payload)
                    if resp is not None:
                        print(json.dumps(resp))
                        sys.stdout.flush()
        except KeyboardInterrupt:
            return 0
        return 0

    print("Interactive mode is not implemented; run with --stdio or --test.")
    return 0


_POSSESSIVE_FAMILY_ROLE_STEM_RE = re.compile(
    r"\b(?P<owner>[A-Za-z][A-Za-z0-9_-]*?)(?:'s|s)\s+"
    r"(?P<role>mom and dad|mom|dad|mother|father|parents?|brother|sister|wife|husband|friend)\b",
    re.IGNORECASE,
)

_BARE_OWNER_FRIEND_RE = re.compile(
    r"\b(?P<owner>[A-Za-z][A-Za-z0-9_-]*)\s+friend\b(?=\s+is\b)",
    re.IGNORECASE,
)


def _normalize_possessive_family_bundle_utterance(utterance: str) -> str:
    if not isinstance(utterance, str) or not utterance:
        return utterance

    # Keep this lane intentionally narrow: true possessive stems like
    # "scotts mom"/"brians sister" plus the obvious missing-marked social phrase
    # "scott friend is brian". Do not reinterpret pronoun phrases like "his wife".
    blocked_owners = {"hi", "his", "it", "its", "her", "their", "your", "our", "my", "whose"}

    def _rewrite_stem(match: re.Match[str]) -> str:
        owner = match.group("owner")
        role = match.group("role")
        if owner.lower() in blocked_owners:
            return match.group(0)
        return f"{owner}'s {role}"

    normalized = _POSSESSIVE_FAMILY_ROLE_STEM_RE.sub(_rewrite_stem, utterance)

    def _rewrite_bare_friend(match: re.Match[str]) -> str:
        owner = match.group("owner")
        if owner.lower() in blocked_owners:
            return match.group(0)
        return f"{owner}'s friend"

    return _BARE_OWNER_FRIEND_RE.sub(_rewrite_bare_friend, normalized)


_ORIGINAL_PROCESS_UTTERANCE = PrologMCPServer.process_utterance


def _process_utterance_with_possessive_family_bundle_normalization(self, payload):
    if isinstance(payload, dict):
        utterance = payload.get("utterance")
        normalized = _normalize_possessive_family_bundle_utterance(utterance)
        if normalized != utterance:
            payload = dict(payload)
            payload["utterance"] = normalized
    return _ORIGINAL_PROCESS_UTTERANCE(self, payload)


PrologMCPServer.process_utterance = _process_utterance_with_possessive_family_bundle_normalization


_SAME_CLAUSE_SPOUSE_PHRASE_RE = re.compile(
    r"\b(?P<subject>[A-Za-z][A-Za-z0-9_-]*)\s+"
    r"(?P<verb>is|was|were|lives|live|lived|works|work|worked|stays|stay|stayed|"
    r"resides|reside|resided|moved|move|migrate|migrated)\b"
    r"(?P<middle>(?:(?!\band\b).){0,80}?)"
    r"\bwith\s+(?P<pronoun>his|her)\s+(?P<role>wife|husband)\s+(?P<spouse>[A-Za-z][A-Za-z0-9_-]*)\b",
    re.IGNORECASE,
)


def _normalize_same_clause_spouse_phrase_utterance(utterance: str) -> str:
    if not utterance:
        return utterance

    def _rewrite(match: re.Match[str]) -> str:
        pronoun = match.group("pronoun").lower()
        role = match.group("role").lower()
        if (pronoun, role) not in {("his", "wife"), ("her", "husband")}:
            return match.group(0)
        subject = match.group("subject")
        verb = match.group("verb")
        middle = (match.group("middle") or "").rstrip()
        spouse = match.group("spouse")
        return f"{subject} {verb}{middle} with {subject}'s {role} {spouse}"

    return _SAME_CLAUSE_SPOUSE_PHRASE_RE.sub(_rewrite, utterance)


_PROCESS_UTTERANCE_WITH_FAMILY_NORMALIZATION = PrologMCPServer.process_utterance


def _process_utterance_with_same_clause_spouse_normalization(
    self: PrologMCPServer, payload: Dict[str, Any]
) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return _PROCESS_UTTERANCE_WITH_FAMILY_NORMALIZATION(self, payload)
    request = dict(payload)
    utterance = request.get("utterance")
    if isinstance(utterance, str):
        normalized_utterance = _normalize_same_clause_spouse_phrase_utterance(utterance)
        if normalized_utterance != utterance:
            request["utterance"] = normalized_utterance
    return _PROCESS_UTTERANCE_WITH_FAMILY_NORMALIZATION(self, request)


PrologMCPServer.process_utterance = (
    _process_utterance_with_same_clause_spouse_normalization
)


_SAME_UTTERANCE_FAMILY_ANCHOR_PRONOUN_RE = re.compile(
    r"\b(?P<owner>[A-Za-z][A-Za-z0-9_-]*)(?:'s|s)\s+"
    r"(?P<anchor_role>mom and dad|mom|dad|mother|father|parents?|brother|sister)\b"
    r"(?P<middle>[^.?!;]{0,160}?)"
    r"\s*\band\s+(?P<pronoun>his|her)\s+"
    r"(?P<role>brother|sister|mom|dad|mother|father)\b",
    re.IGNORECASE,
)


def _normalize_same_utterance_family_anchor_pronouns(utterance: str) -> str:
    if not isinstance(utterance, str) or not utterance:
        return utterance

    blocked_owners = {"hi", "his", "her", "their", "our", "your", "my", "whose"}

    def _rewrite(match: re.Match[str]) -> str:
        owner = match.group("owner")
        if owner.lower() in blocked_owners:
            return match.group(0)
        anchor_role = match.group("anchor_role")
        middle = (match.group("middle") or "").rstrip()
        role = match.group("role")
        return f"{owner}'s {anchor_role}{middle} and {owner}'s {role}"

    return _SAME_UTTERANCE_FAMILY_ANCHOR_PRONOUN_RE.sub(_rewrite, utterance)


_PROCESS_UTTERANCE_WITH_FAMILY_ANCHOR_PRONOUN_BASE = PrologMCPServer.process_utterance


def _process_utterance_with_family_anchor_pronoun_normalization(self, payload):
    if isinstance(payload, dict):
        utterance = payload.get("utterance")
        normalized = _normalize_same_utterance_family_anchor_pronouns(utterance)
        if normalized != utterance:
            payload = dict(payload)
            payload["utterance"] = normalized
    return _PROCESS_UTTERANCE_WITH_FAMILY_ANCHOR_PRONOUN_BASE(self, payload)


PrologMCPServer.process_utterance = _process_utterance_with_family_anchor_pronoun_normalization


if __name__ == "__main__":
    raise SystemExit(main())
