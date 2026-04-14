from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_pipeline import (
    _build_extractor_prompt,
    _call_model_prompt,
    _extract_retract_targets,
    _get_api_key,
    _normalize_clarification_fields,
    _parse_model_json,
    _validate_parsed,
)
from src.mcp_server import PrologMCPServer


class RuntimeHooks:
    """Gateway runtime bridge wired to real prethink + deterministic runtime tools."""

    def __init__(self) -> None:
        self._server: PrologMCPServer | None = None
        self._server_signature = ""
        self._prompt_cache: dict[str, str] = {}
        self._kb_path = str((REPO_ROOT / "kb_store" / "ui_gateway_live").resolve())

    def _should_use_external_compiler_prompt(self, config: dict[str, Any]) -> bool:
        mode = str(config.get("compiler_prompt_mode", "auto") or "auto").strip().lower()
        if mode == "always":
            return True
        if mode == "never":
            return False
        model = str(config.get("compiler_model", "") or "").strip().lower()
        # Auto: avoid duplicate SP injection for known baked semantic parser variants.
        return "semparse" not in model

    def _prompt_path_from_config(self, config: dict[str, Any]) -> Path | None:
        if not self._should_use_external_compiler_prompt(config):
            return None
        raw = str(config.get("compiler_prompt_file", "")).strip()
        if not raw:
            return REPO_ROOT / "modelfiles" / "semantic_parser_system_prompt.md"
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = (REPO_ROOT / candidate).resolve()
        return candidate

    def _prompt_text(self, path: Path | None) -> str:
        if path is None:
            return ""
        key = str(path)
        if key in self._prompt_cache:
            return self._prompt_cache[key]
        text = path.read_text(encoding="utf-8")
        self._prompt_cache[key] = text
        return text

    def _server_config_signature(self, config: dict[str, Any]) -> str:
        prompt_path_obj = self._prompt_path_from_config(config)
        prompt_path = str(prompt_path_obj) if prompt_path_obj else ""
        return "|".join(
            [
                str(config.get("compiler_mode", "strict")),
                str(config.get("compiler_prompt_mode", "auto")),
                str(config.get("compiler_backend", "ollama")),
                str(config.get("compiler_base_url", "http://127.0.0.1:11434")),
                str(config.get("compiler_model", "qwen35-semparse:9b")),
                str(int(config.get("compiler_context_length", 8192) or 8192)),
                str(int(config.get("compiler_timeout", 60) or 60)),
                prompt_path,
                str(round(float(config.get("clarification_eagerness", 0.75) or 0.75), 3)),
                str(bool(config.get("require_final_confirmation", True))),
                str(bool(config.get("strict_mode", True))),
            ]
        )

    def _ensure_server(self, config: dict[str, Any]) -> PrologMCPServer:
        signature = self._server_config_signature(config)
        if self._server is not None and signature == self._server_signature:
            return self._server

        compiler_mode = str(config.get("compiler_mode", "strict")).strip().lower()
        if bool(config.get("strict_mode", True)) and compiler_mode == "auto":
            compiler_mode = "strict"

        prompt_path = self._prompt_path_from_config(config)
        prompt_enabled = prompt_path is not None
        self._server = PrologMCPServer(
            kb_path=self._kb_path,
            compiler_mode=compiler_mode,
            compiler_backend=str(config.get("compiler_backend", "ollama") or "ollama"),
            compiler_base_url=str(config.get("compiler_base_url", "http://127.0.0.1:11434") or "http://127.0.0.1:11434"),
            compiler_model=str(config.get("compiler_model", "qwen35-semparse:9b") or "qwen35-semparse:9b"),
            compiler_context_length=max(512, int(config.get("compiler_context_length", 8192) or 8192)),
            compiler_timeout=max(5, int(config.get("compiler_timeout", 60) or 60)),
            compiler_prompt_file=str(prompt_path) if prompt_path is not None else "",
            compiler_prompt_enabled=prompt_enabled,
        )
        self._server.tools_call(
            "set_pre_think_session",
            {
                "enabled": True,
                "all_turns_require_prethink": True,
                "clarification_eagerness": float(config.get("clarification_eagerness", 0.75) or 0.75),
                "require_final_confirmation": bool(config.get("require_final_confirmation", True)),
            },
        )
        self._server_signature = signature
        return self._server

    def inspect_kb(self, *, config: dict[str, Any], limit: int = 80) -> dict[str, Any]:
        server = self._ensure_server(config)
        cap = max(1, min(500, int(limit or 80)))
        clauses: list[str] = []
        seen: set[str] = set()

        runtime = getattr(server, "_runtime", None)
        engine = getattr(runtime, "engine", None) if runtime is not None else None
        raw_clauses = getattr(engine, "clauses", []) if engine is not None else []
        if isinstance(raw_clauses, list):
            for row in raw_clauses:
                text = str(row).strip()
                if not text:
                    continue
                if not text.endswith("."):
                    text = f"{text}."
                if text in seen:
                    continue
                seen.add(text)
                clauses.append(text)

        shown = clauses[-cap:] if len(clauses) > cap else list(clauses)
        return {
            "status": "success",
            "kb_path": str(getattr(server, "_kb_path", "") or self._kb_path),
            "clause_count": len(clauses),
            "clauses": shown,
            "truncated": max(0, len(clauses) - len(shown)),
        }

    def clear_kb(self, *, config: dict[str, Any]) -> dict[str, Any]:
        server = self._ensure_server(config)
        before = self.inspect_kb(config=config, limit=500)
        result = server.empty_kb()
        after = self.inspect_kb(config=config, limit=1)
        before_count = int(before.get("clause_count", 0) or 0)
        after_count = int(after.get("clause_count", 0) or 0)
        return {
            "status": str(result.get("status", "unknown")).strip() or "unknown",
            "result_type": str(result.get("result_type", "runtime_emptied")).strip() or "runtime_emptied",
            "message": str(result.get("message", "KB clear executed.")).strip() or "KB clear executed.",
            "cleared_count": max(0, before_count - after_count),
            "before_count": before_count,
            "after_count": after_count,
            "kb_path": str(before.get("kb_path", "")).strip(),
        }

    def front_door(self, utterance: str, config: dict, session: dict) -> dict:
        server = self._ensure_server(config)
        prethink = server.tools_call("pre_think", {"utterance": utterance})
        if str(prethink.get("status", "")).strip() != "success":
            message = str(prethink.get("message", "pre_think unavailable")).strip()
            return {
                "route": "other",
                "looks_like_query": False,
                "looks_like_write": False,
                "ambiguity_score": 1.0,
                "needs_clarification": True,
                "reasons": [message],
                "clarification_question": "Compiler unavailable. Retry after compiler model is reachable.",
                "front_door_uri": config["front_door_uri"],
                "compiler": {
                    "mode": config.get("compiler_mode", "strict"),
                    "model": config.get("compiler_model", "qwen35-semparse:9b"),
                    "backend": config.get("compiler_backend", "ollama"),
                    "base_url": config.get("compiler_base_url", "http://127.0.0.1:11434"),
                    "strict_mode": config.get("strict_mode", True),
                    "used": False,
                    "error": message,
                },
                "session_snapshot": {
                    "session_id": session["session_id"],
                    "turn_count": len(session["turns"]),
                    "has_pending_clarification": bool(session["pending_clarification"]),
                },
                "prethink": prethink,
            }

        packet = prethink.get("packet", {}) if isinstance(prethink.get("packet"), dict) else {}
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
        needs_clarification = bool(clar.get("required_before_query"))

        return {
            "route": route,
            "compiler_intent": compiler_intent,
            "looks_like_query": route == "query",
            "looks_like_write": route == "write",
            "ambiguity_score": round(ambiguity, 2),
            "needs_clarification": needs_clarification,
            "reasons": [str(clar.get("reason", "")).strip() or "compiler_decision"],
            "clarification_question": str(clar.get("question", "")).strip(),
            "prethink_id": str(packet.get("prethink_id", "")).strip(),
            "front_door_uri": config["front_door_uri"],
            "compiler": {
                "mode": config.get("compiler_mode", "strict"),
                "model": config.get("compiler_model", "qwen35-semparse:9b"),
                "backend": config.get("compiler_backend", "ollama"),
                "base_url": config.get("compiler_base_url", "http://127.0.0.1:11434"),
                "strict_mode": config.get("strict_mode", True),
                "used": bool(compiler.get("used", True)),
                "error": str(compiler.get("error", "")).strip(),
            },
            "session_snapshot": {
                "session_id": session["session_id"],
                "turn_count": len(session["turns"]),
                "has_pending_clarification": bool(session["pending_clarification"]),
            },
            "prethink": prethink,
        }

    def _compile_parse(
        self,
        *,
        utterance: str,
        compiler_intent: str,
        config: dict[str, Any],
        clarification_question: str = "",
        clarification_answer: str = "",
    ) -> tuple[dict[str, Any] | None, str]:
        prompt_path = self._prompt_path_from_config(config)
        try:
            prompt_guide = self._prompt_text(prompt_path)
        except Exception as exc:
            return None, f"Unable to load prompt file: {exc}"

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
            known_predicates=[],
            prompt_guide=prompt_guide,
        )

        api_key = _get_api_key()
        try:
            response = _call_model_prompt(
                backend=str(config.get("compiler_backend", "ollama") or "ollama"),
                base_url=str(config.get("compiler_base_url", "http://127.0.0.1:11434") or "http://127.0.0.1:11434"),
                model=str(config.get("compiler_model", "qwen35-semparse:9b") or "qwen35-semparse:9b"),
                prompt_text=extraction_prompt,
                context_length=max(512, int(config.get("compiler_context_length", 8192) or 8192)),
                timeout=max(5, int(config.get("compiler_timeout", 60) or 60)),
                api_key=api_key,
            )
        except Exception as exc:
            return None, f"Compiler parse call failed: {exc}"

        parsed, _ = _parse_model_json(
            response,
            required_keys=["intent", "logic_string", "components", "confidence"],
        )
        if not isinstance(parsed, dict):
            return None, "Compiler parse payload was not valid JSON."

        parsed = _normalize_clarification_fields(
            parsed,
            utterance=effective,
            route=compiler_intent,
        )
        parsed = self._augment_compound_family_facts(
            parsed=parsed,
            utterance=utterance,
            clarification_answer=clarification_answer,
        )
        ok, errors = _validate_parsed(parsed)
        if not ok:
            return None, "; ".join(errors)
        return parsed, ""

    def _atomize_name(self, raw: str) -> str:
        lowered = str(raw or "").strip().lower()
        if not lowered:
            return ""
        atom = re.sub(r"[^a-z0-9_]+", "_", lowered).strip("_")
        return atom

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

        parent_override_facts: list[str] = []
        owner_from_parent_block = ""
        parent_block = re.search(
            r"\b([a-z][a-z0-9_'-]*?)'?s\s+mom\s+and\s+dad\s+are\s+([a-z][a-z0-9_'-]*)\s+and\s+([a-z][a-z0-9_'-]*)\b",
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
            owner_atom = ""
            if owner_token in {"his", "her", "their"}:
                owner_atom = clar_atom or owner_from_parent_block
            else:
                owner_match = re.match(r"^([a-z][a-z0-9_'-]*?)'?s$", owner_token)
                if owner_match:
                    owner_atom = self._atomize_name(owner_match.group(1))
            if owner_atom and sibling_atom:
                fact = f"brother({sibling_atom}, {owner_atom})."
                if fact not in sibling_override_facts:
                    sibling_override_facts.append(fact)

        if parent_override_facts:
            kept = [fact for fact in normalized_facts if not re.match(r"^parent\s*\(", fact)]
            normalized_facts = kept + parent_override_facts

        if sibling_override_facts:
            kept = [fact for fact in normalized_facts if not re.match(r"^brother\s*\(", fact)]
            normalized_facts = kept + sibling_override_facts

        if normalized_facts == original_facts or not normalized_facts:
            return parsed

        parsed["facts"] = normalized_facts
        parsed["logic_string"] = (
            normalized_facts[0] if len(normalized_facts) == 1 else " ".join(normalized_facts)
        )
        parsed["rules"] = []
        parsed["queries"] = []
        parsed["components"] = self._extract_components_from_facts(normalized_facts)
        rationale = str(parsed.get("rationale", "")).strip()
        suffix = "Compound family statement expansion added deterministic companion facts."
        parsed["rationale"] = f"{rationale} {suffix}".strip() if rationale else suffix
        return parsed

    def _apply_parsed(self, *, parsed: dict[str, Any], prethink_id: str, server: PrologMCPServer) -> dict[str, Any]:
        intent = str(parsed.get("intent", "")).strip()
        operations: list[dict[str, Any]] = []
        writes_applied = 0
        query_result: dict[str, Any] | None = None
        errors: list[str] = []

        if intent == "assert_fact":
            clauses = [str(item).strip() for item in parsed.get("facts", []) if str(item).strip()]
            if not clauses:
                clause = str(parsed.get("logic_string", "")).strip()
                if clause:
                    clauses = [clause]
            for clause in clauses:
                result = server.tools_call(
                    "assert_fact",
                    {"clause": clause, "prethink_id": prethink_id, "confirm": True},
                )
                operations.append({"tool": "assert_fact", "clause": clause, "result": result})
                if str(result.get("status", "")).strip() == "success":
                    writes_applied += 1
                else:
                    errors.append(f"assert_fact failed for {clause}")

        elif intent == "assert_rule":
            clauses = [str(item).strip() for item in parsed.get("rules", []) if str(item).strip()]
            if not clauses:
                clause = str(parsed.get("logic_string", "")).strip()
                if clause:
                    clauses = [clause]
            for clause in clauses:
                result = server.tools_call(
                    "assert_rule",
                    {"clause": clause, "prethink_id": prethink_id, "confirm": True},
                )
                operations.append({"tool": "assert_rule", "clause": clause, "result": result})
                if str(result.get("status", "")).strip() == "success":
                    writes_applied += 1
                else:
                    errors.append(f"assert_rule failed for {clause}")

        elif intent == "retract":
            targets = _extract_retract_targets(
                str(parsed.get("logic_string", "")).strip(),
                [str(item).strip() for item in parsed.get("facts", []) if str(item).strip()],
            )
            for target in targets:
                clause = target if str(target).strip().endswith(".") else f"{target}."
                result = server.tools_call(
                    "retract_fact",
                    {"clause": clause, "prethink_id": prethink_id, "confirm": True},
                )
                operations.append({"tool": "retract_fact", "clause": clause, "result": result})
                if str(result.get("status", "")).strip() == "success":
                    writes_applied += 1
                else:
                    errors.append(f"retract_fact failed for {clause}")

        elif intent == "query":
            queries = [str(item).strip() for item in parsed.get("queries", []) if str(item).strip()]
            query = queries[0] if queries else str(parsed.get("logic_string", "")).strip()
            result = server.tools_call(
                "query_rows",
                {"query": query, "prethink_id": prethink_id},
            )
            query_result = result
            operations.append({"tool": "query_rows", "query": query, "result": result})
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

    def execute_turn(
        self,
        *,
        utterance: str,
        front_door: dict[str, Any],
        config: dict[str, Any],
        clarification_answer: str = "",
    ) -> dict[str, Any]:
        server = self._ensure_server(config)
        prethink_id = str(front_door.get("prethink_id", "")).strip()
        if not prethink_id:
            return {
                "status": "error",
                "intent": "other",
                "writes_applied": 0,
                "operations": [],
                "query_result": None,
                "parse": {},
                "errors": ["Missing prethink_id from front door."],
            }

        if clarification_answer:
            clarified = server.tools_call(
                "record_clarification_answer",
                {
                    "prethink_id": prethink_id,
                    "answer": clarification_answer,
                    "confirmed": True,
                },
            )
            if str(clarified.get("status", "")).strip() != "success":
                return {
                    "status": "error",
                    "intent": "other",
                    "writes_applied": 0,
                    "operations": [{"tool": "record_clarification_answer", "result": clarified}],
                    "query_result": None,
                    "parse": {},
                    "errors": [str(clarified.get("message", "clarification record failed"))],
                }

        compiler_intent = str(front_door.get("compiler_intent", "other")).strip() or "other"
        parsed, error = self._compile_parse(
            utterance=utterance,
            compiler_intent=compiler_intent,
            config=config,
            clarification_question=str(front_door.get("clarification_question", "")).strip(),
            clarification_answer=clarification_answer,
        )
        if not isinstance(parsed, dict):
            return {
                "status": "error",
                "intent": compiler_intent,
                "writes_applied": 0,
                "operations": [],
                "query_result": None,
                "parse": {},
                "errors": [error or "parse failed"],
            }

        return self._apply_parsed(parsed=parsed, prethink_id=prethink_id, server=server)

    def _served_handoff_mode(self, config: dict[str, Any]) -> str:
        mode = str(config.get("served_handoff_mode", "fallback_only") or "fallback_only").strip().lower()
        if mode not in {"never", "fallback_only", "on_other", "always"}:
            mode = "fallback_only"
        return mode

    def _should_handoff_to_served_llm(
        self,
        *,
        execution: dict[str, Any],
        route: str,
        config: dict[str, Any],
    ) -> bool:
        if str(execution.get("status", "")).strip() != "success":
            return False
        mode = self._served_handoff_mode(config)
        if mode == "never":
            return False
        if mode == "always":
            return True
        if mode == "on_other":
            return str(route or "").strip().lower() == "other"

        # fallback_only
        writes_applied = int(execution.get("writes_applied", 0) or 0)
        if writes_applied > 0:
            return False

        query_result = execution.get("query_result")
        if isinstance(query_result, dict):
            status = str(query_result.get("status", "")).strip()
            if status == "success":
                num_rows = int(query_result.get("num_rows", 0) or 0)
                return num_rows <= 0
            if status == "no_results":
                return True
            return True

        # No query payload and no writes means this was effectively a no-op/other turn.
        return True

    def _build_served_prompt(
        self,
        *,
        utterance: str,
        route: str,
        execution: dict[str, Any],
    ) -> str:
        intent = str(execution.get("intent", "")).strip() or "other"
        summary = {
            "intent": intent,
            "writes_applied": int(execution.get("writes_applied", 0) or 0),
            "query_result": execution.get("query_result"),
            "parse": execution.get("parse", {}),
        }
        return (
            "You are the served assistant behind a governed pre-think gateway.\n"
            "Follow these rules:\n"
            "- The deterministic pre-think/runtime result is the source of truth.\n"
            "- If deterministic query returned no rows, say that clearly, then offer a helpful next question.\n"
            "- Do not claim KB mutations unless stated in the deterministic summary.\n"
            "- Keep response concise and plain.\n\n"
            f"ROUTE: {route}\n"
            f"USER_UTTERANCE: {utterance}\n"
            "DETERMINISTIC_SUMMARY_JSON:\n"
            f"{json.dumps(summary, ensure_ascii=True)}\n"
        )

    def _served_handoff_response(
        self,
        *,
        utterance: str,
        route: str,
        execution: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = self._build_served_prompt(utterance=utterance, route=route, execution=execution)
        api_key = _get_api_key()
        backend = str(config.get("served_llm_provider", "ollama") or "ollama")
        model = str(config.get("served_llm_model", "gpt-oss:20b") or "gpt-oss:20b")
        base_url = str(config.get("served_llm_base_url", "http://127.0.0.1:11434") or "http://127.0.0.1:11434")
        try:
            raw = _call_model_prompt(
                backend=backend,
                base_url=base_url,
                model=model,
                prompt_text=prompt,
                context_length=max(512, int(config.get("served_llm_context_length", 16384) or 16384)),
                timeout=max(5, int(config.get("served_llm_timeout", 60) or 60)),
                api_key=api_key,
            )
            message_text = ""
            reasoning_text = ""
            if hasattr(raw, "message"):
                message_text = str(getattr(raw, "message", "") or "").strip()
            if hasattr(raw, "reasoning"):
                reasoning_text = str(getattr(raw, "reasoning", "") or "").strip()
            text = message_text or reasoning_text or str(raw or "").strip()
            if not text:
                text = "Served model returned an empty response."
            return {
                "speaker": "served-llm",
                "text": text,
                "mode": "served_llm_handoff",
                "served_llm": {
                    "provider": backend,
                    "model": model,
                    "base_url": base_url,
                    "handoff_mode": self._served_handoff_mode(config),
                },
            }
        except Exception as exc:
            return {
                "speaker": "prethink-gateway",
                "text": f"Served LLM handoff failed ({backend}:{model}): {exc}",
                "mode": "served_llm_handoff_error",
                "served_llm": {
                    "provider": backend,
                    "model": model,
                    "base_url": base_url,
                    "handoff_mode": self._served_handoff_mode(config),
                    "error": str(exc),
                },
            }

    def answer(
        self,
        *,
        utterance: str,
        route: str,
        execution: dict | None,
        clarification: dict | None,
        config: dict,
    ) -> dict:
        if clarification:
            return {
                "speaker": "prethink-gateway",
                "text": clarification["question"],
                "mode": "clarify",
            }

        if not execution:
            return {
                "speaker": "prethink-gateway",
                "text": "No execution result was produced.",
                "mode": "answer",
            }

        if str(execution.get("status", "")).strip() != "success":
            errors = execution.get("errors", [])
            return {
                "speaker": "prethink-gateway",
                "text": f"Execution blocked: {'; '.join(str(e) for e in errors) if errors else 'unknown error'}",
                "mode": "answer",
            }

        if self._should_handoff_to_served_llm(execution=execution, route=route, config=config):
            return self._served_handoff_response(
                utterance=utterance,
                route=route,
                execution=execution,
                config=config,
            )

        intent = str(execution.get("intent", "")).strip()
        if intent in {"assert_fact", "assert_rule", "retract"}:
            writes = int(execution.get("writes_applied", 0) or 0)
            return {
                "speaker": "prethink-gateway",
                "text": f"Deterministic commit complete: {writes} mutation(s) applied.",
                "mode": "answer",
            }

        if intent == "query":
            query_result = execution.get("query_result")
            if isinstance(query_result, dict):
                status = str(query_result.get("status", "")).strip()
                if status == "success":
                    rows = query_result.get("rows", [])
                    preview = " | ".join(
                        [", ".join(f"{k}={v}" for k, v in row.items()) for row in rows[:5] if isinstance(row, dict)]
                    )
                    return {
                        "speaker": "prethink-gateway",
                        "text": f"Query succeeded with {int(query_result.get('num_rows', len(rows)) or 0)} row(s). {preview}".strip(),
                        "mode": "answer",
                    }
                if status == "no_results":
                    return {
                        "speaker": "prethink-gateway",
                        "text": "Query returned no results.",
                        "mode": "answer",
                    }
            return {
                "speaker": "prethink-gateway",
                "text": "Query executed but result payload was not recognized.",
                "mode": "answer",
            }

        return {
            "speaker": "prethink-gateway",
            "text": (
                "No deterministic mutation was required. "
                f"Served LLM ({config['served_llm_provider']}:{config['served_llm_model']}) handoff can be added next."
            ),
            "mode": "answer",
        }
