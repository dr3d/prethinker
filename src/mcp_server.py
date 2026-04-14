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
import sys
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_pipeline import (
    CorePrologRuntime,
    _call_model_prompt,
    _get_api_key,
    _load_env_file,
    _parse_model_json,
    _resolve_env_file,
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
        compiler_mode: str = "strict",
        compiler_backend: str = "ollama",
        compiler_base_url: str = "http://127.0.0.1:11434",
        compiler_model: str = "qwen35-semparse:9b",
        compiler_context_length: int = 8192,
        compiler_timeout: int = 60,
        compiler_prompt_file: str = "",
        compiler_prompt_enabled: bool = True,
    ) -> None:
        self._runtime = CorePrologRuntime()
        self._kb_path = str(Path(kb_path).resolve()) if str(kb_path).strip() else ""
        self._session = PreThinkSessionState()
        self._request_id = 1
        self._prethink_counter = 1
        self._pending_prethink: dict[str, Any] | None = None
        self._trace_path = REPO_ROOT / "tmp" / "mcp_trace.log"
        self._compiler_mode = str(compiler_mode or "strict").strip().lower()
        if self._compiler_mode not in {"strict", "auto", "heuristic"}:
            self._compiler_mode = "strict"
        self._compiler_backend = str(compiler_backend or "ollama").strip()
        self._compiler_base_url = str(compiler_base_url or "http://127.0.0.1:11434").strip()
        self._compiler_model = str(compiler_model or "qwen35-semparse:9b").strip()
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
        self._load_compiler_prompt()

    def _load_compiler_prompt(self) -> None:
        if not self._compiler_prompt_enabled:
            self._compiler_prompt_text = ""
            self._compiler_prompt_loaded = True
            self._compiler_prompt_load_error = ""
            return
        try:
            self._compiler_prompt_text = self._compiler_prompt_path.read_text(encoding="utf-8")
            self._compiler_prompt_loaded = bool(self._compiler_prompt_text.strip())
            self._compiler_prompt_load_error = ""
        except Exception as exc:
            self._compiler_prompt_text = ""
            self._compiler_prompt_loaded = False
            self._compiler_prompt_load_error = str(exc)

    # Direct runtime methods used by kb_pipeline with --runtime mcp
    def empty_kb(self) -> dict[str, Any]:
        result = self._runtime.empty_kb()
        if self._kb_path:
            result["knowledge_base_path"] = self._kb_path
        return result

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
            "- clarification_question may be empty string if not needed\n"
            "- clarification_reason should be short and concrete\n"
            "- no markdown, no prose wrappers\n"
            f"USER_UTTERANCE:\n{utterance}\n"
        )

    def _compile_prethink_semantics(self, utterance: str) -> tuple[dict[str, Any] | None, str]:
        if not self._compiler_prompt_loaded:
            reason = self._compiler_prompt_load_error or "compiler prompt unavailable"
            return None, f"Compiler prompt not loaded: {reason}"
        prompt = self._build_compiler_prompt(utterance)
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
            parsed, _ = _parse_model_json(
                response,
                required_keys=["intent", "needs_clarification", "uncertainty_score"],
            )
            if not isinstance(parsed, dict):
                return None, "Compiler returned non-parseable JSON payload."
            intent = str(parsed.get("intent", "")).strip()
            if intent not in {"assert_fact", "assert_rule", "query", "retract", "other"}:
                return None, f"Compiler returned invalid intent: {intent}"
            return parsed, ""
        except Exception as exc:
            return None, str(exc)

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
                return {
                    "status": "blocked",
                    "result_type": "compiler_unavailable",
                    "message": (
                        "Pre-think compiler is strict-bound and unavailable. "
                        f"Configure {self._compiler_model} or switch compiler_mode."
                    ),
                    "details": {
                        "compiler_mode": self._compiler_mode,
                        "compiler_backend": self._compiler_backend,
                        "compiler_base_url": self._compiler_base_url,
                        "compiler_model": self._compiler_model,
                        "compiler_prompt_path": str(self._compiler_prompt_path),
                        "error": compile_error,
                    },
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
        clarification_required = bool(
            compiler_needs_clarification
            or bool(coreference.get("clarification_recommended"))
            or (uncertainty >= ce_threshold and self._session.enabled)
        )
        clarification_question = compiler_clarification_question or str(
            coreference.get("clarification_question", "")
        ).strip()
        if clarification_required and not clarification_question:
            clarification_question = "Please clarify the intended fact or referent before I continue."
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
                "model": self._compiler_model,
                "context_length": self._compiler_context_length,
                "prompt_enabled": bool(self._compiler_prompt_enabled),
                "prompt_path": str(self._compiler_prompt_path) if self._compiler_prompt_enabled else "",
                "used": compiled is not None,
                "error": compile_error,
                "intent": intent,
                "needs_clarification": compiler_needs_clarification,
                "clarification_reason": compiler_clarification_reason,
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
        self._pending_prethink = {
            "prethink_id": packet["prethink_id"],
            "mode": packet["mode"],
            "utterance": utterance,
            "clarification_required_before_query": clarification_required,
            "clarification_question": clarification_question,
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
        }
        return {
            "status": "success",
            "result_type": "pre_think_packet",
            "packet": packet,
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
    parser.add_argument("--compiler-model", default="qwen35-semparse:9b", help="Compiler model tag.")
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


if __name__ == "__main__":
    raise SystemExit(main())
