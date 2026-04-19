from __future__ import annotations

import time
from typing import Any

from gateway.runtime_hooks import RuntimeHooks
from gateway.session_store import SessionState


def _phase(name: str, status: str, summary: str, data: dict) -> dict:
    return {
        "phase": name,
        "status": status,
        "summary": summary,
        "data": data,
    }


def process_turn(
    utterance: str,
    session: SessionState,
    config: dict,
    runtime: RuntimeHooks,
    config_store: Any | None = None,
) -> dict:
    started_at = time.time()
    phases: list[dict] = []
    execution: dict | None = None
    clarification: dict | None = None
    compiler_trace: dict | None = None
    route = "other"

    slash_result = _handle_slash_command(
        utterance=utterance,
        session=session,
        config=config,
        runtime=runtime,
        config_store=config_store,
    )
    if slash_result is not None:
        phases.append(
            _phase(
                "ingest",
                "ok",
                "Slash command accepted.",
                {
                    "front_door_uri": config["front_door_uri"],
                    "command": slash_result["command"],
                },
            )
        )
        phases.append(
            _phase(
                "clarify",
                "skipped",
                "Slash command bypassed clarification gate.",
                {"reason": "operator_command"},
            )
        )
        phases.append(
            _phase(
                "commit",
                "skipped",
                "Slash command bypassed deterministic commit pipeline.",
                {"reason": "operator_command"},
            )
        )
        phases.append(
            _phase(
                "answer",
                "ok",
                "Prepared slash command response.",
                slash_result["answer"],
            )
        )

        turn = {
            "turn_index": len(session.turns) + 1,
            "timestamp": started_at,
            "utterance": utterance,
            "route": "command",
            "phases": phases,
            "assistant": slash_result["answer"],
            "trace": None,
        }
        session.turns.append(turn)
        return {
            "status": "ok",
            "front_door_uri": config["front_door_uri"],
            "session_id": session.session_id,
            "turn": turn,
            "pending_clarification": session.pending_clarification,
        }

    if session.pending_clarification:
        pending = session.pending_clarification
        lowered = utterance.strip().lower()
        phases.append(
            _phase(
                "ingest",
                "ok",
                "Received clarification follow-up.",
                {
                    "front_door_uri": config["front_door_uri"],
                    "pending_question": pending["question"],
                    "original_utterance": pending["original_utterance"],
                },
            )
        )
        if lowered in {"no", "cancel", "stop"}:
            phases.append(
                _phase(
                    "clarify",
                    "cancelled",
                    "User cancelled the staged write.",
                    {"resolution": "cancelled"},
                )
            )
            phases.append(
                _phase(
                    "commit",
                    "skipped",
                    "No commit produced after cancellation.",
                    {"reason": "user_cancelled"},
                )
            )
            execution = {
                "status": "error",
                "intent": "other",
                "errors": ["User cancelled staged write."],
            }
            route = "write"
            session.pending_clarification = None
        else:
            resolution = "confirmed" if lowered in {"yes", "y", "confirm", "go ahead", "commit it"} else "reframed"
            phases.append(
                _phase(
                    "clarify",
                    "resolved",
                    f"Clarification resolved via {resolution}.",
                    {
                        "resolution": resolution,
                        "follow_up": utterance,
                    },
                )
            )
            process_result = runtime.process_utterance(
                utterance=str(pending.get("original_utterance", "")).strip(),
                config=config,
                session={
                    "session_id": session.session_id,
                    "turns": session.turns,
                    "pending_clarification": session.pending_clarification,
                },
                clarification_answer=utterance,
                prethink_id=str(pending.get("prethink_id", "")).strip(),
            )
            compiler_trace = (
                process_result.get("compiler_trace")
                if isinstance(process_result.get("compiler_trace"), dict)
                else None
            )
            front_door = process_result.get("front_door") if isinstance(process_result.get("front_door"), dict) else {}
            route = str(front_door.get("route", "other")).strip() or "other"
            execution = process_result.get("execution") if isinstance(process_result.get("execution"), dict) else {
                "status": "error",
                "intent": "other",
                "errors": [str(process_result.get("message", "utterance processing failed")).strip() or "utterance processing failed"],
            }
            phases.append(
                _phase(
                    "commit",
                    "applied" if str(execution.get("status", "")).strip() == "success" else "failed",
                    "Deterministic execution completed after clarification."
                    if str(execution.get("status", "")).strip() == "success"
                    else "Deterministic execution failed after clarification.",
                    execution,
                )
            )
            session.pending_clarification = None
    else:
        process_result = runtime.process_utterance(
            utterance=utterance,
            config=config,
            session={
                "session_id": session.session_id,
                "turns": session.turns,
                "pending_clarification": session.pending_clarification,
            },
        )
        compiler_trace = (
            process_result.get("compiler_trace")
            if isinstance(process_result.get("compiler_trace"), dict)
            else None
        )
        front_door = process_result.get("front_door") if isinstance(process_result.get("front_door"), dict) else {
            "route": "other",
            "reasons": [str(process_result.get("message", "utterance processing failed")).strip() or "utterance processing failed"],
            "clarification_question": "",
            "needs_clarification": False,
        }
        route = front_door["route"]
        phases.append(
            _phase(
                "ingest",
                "ok",
                "prethink:// front door classified the utterance.",
                front_door,
            )
        )
        if str(process_result.get("status", "")).strip() == "clarification_required" and front_door["needs_clarification"]:
            question = _clarification_question(front_door, utterance)
            clarification = {
                "question": question,
                "reasons": front_door["reasons"],
            }
            phases.append(
                _phase(
                    "clarify",
                    "required",
                    "Strict gateway is holding the turn for clarification.",
                    clarification,
                )
            )
            phases.append(
                _phase(
                    "commit",
                    "blocked",
                    "Commit blocked until clarification resolves.",
                    {"reason": "needs_clarification"},
                )
            )
            session.pending_clarification = {
                "question": question,
                "original_utterance": utterance,
                "front_door": front_door,
                "prethink_id": str(front_door.get("prethink_id", "")).strip(),
            }
        else:
            phases.append(
                _phase(
                    "clarify",
                    "skipped",
                    "No clarification needed for this turn.",
                    {"reason": "confidence_above_threshold"},
                )
            )
            execution = process_result.get("execution") if isinstance(process_result.get("execution"), dict) else {
                "status": "error",
                "intent": str(front_door.get("compiler_intent", "other")).strip() or "other",
                "errors": [str(process_result.get("message", "utterance processing failed")).strip() or "utterance processing failed"],
            }
            if route == "write":
                phases.append(
                    _phase(
                        "commit",
                        "applied" if str(execution.get("status", "")).strip() == "success" else "failed",
                        "Deterministic commit attempted."
                        if str(execution.get("status", "")).strip() == "success"
                        else "Deterministic commit failed.",
                        execution,
                    )
                )
            else:
                phases.append(
                    _phase(
                        "commit",
                        "skipped",
                        "No mutation commit needed for this route; deterministic query/no-op executed.",
                        execution,
                    )
                )

    answer = runtime.answer(
        utterance=utterance,
        route=route,
        execution=execution,
        clarification=clarification,
        config=config,
    )
    phases.append(
        _phase(
            "answer",
            "ok",
            "Prepared final response envelope.",
            answer,
        )
    )

    turn = {
        "turn_index": len(session.turns) + 1,
        "timestamp": started_at,
        "utterance": utterance,
        "route": route,
        "phases": phases,
        "assistant": answer,
        "trace": compiler_trace,
    }
    session.turns.append(turn)
    return {
        "status": "ok",
        "front_door_uri": config["front_door_uri"],
        "session_id": session.session_id,
        "turn": turn,
        "pending_clarification": session.pending_clarification,
    }


def _clarification_question(front_door: dict, utterance: str) -> str:
    compiler_question = str(front_door.get("clarification_question", "")).strip()
    if compiler_question:
        return compiler_question
    if front_door["route"] == "write":
        return (
            "Clarify before commit: name the concrete subject, predicate, and object "
            f"for '{utterance}'."
        )
    return (
        "I could not confidently route that turn. Should I treat it as a query, a write, "
        "or a no-op?"
    )


def _format_config_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _coerce_bool_token(raw: str) -> bool | None:
    value = str(raw or "").strip().lower()
    if value in {"1", "true", "yes", "on", "enabled"}:
        return True
    if value in {"0", "false", "no", "off", "disabled"}:
        return False
    return None


def _coerce_config_value(key: str, raw_value: str, current_value: Any) -> tuple[bool, Any, str]:
    text = str(raw_value or "").strip()
    if text == "":
        return False, None, f"Value required for '{key}'."

    if isinstance(current_value, bool):
        parsed = _coerce_bool_token(text)
        if parsed is None:
            return False, None, f"'{key}' expects boolean (true/false)."
        return True, parsed, ""
    if isinstance(current_value, int):
        try:
            return True, int(text), ""
        except ValueError:
            return False, None, f"'{key}' expects integer."
    if isinstance(current_value, float):
        try:
            return True, float(text), ""
        except ValueError:
            return False, None, f"'{key}' expects number."
    return True, text, ""


def _apply_config_updates(*, config: dict[str, Any], config_store: Any | None, updates: dict[str, Any]) -> dict[str, Any]:
    if config_store is not None and hasattr(config_store, "update"):
        updated = config_store.update(updates)
        if hasattr(updated, "to_dict"):
            return dict(updated.to_dict())
    merged = dict(config)
    merged.update(updates)
    return merged


def _format_config_snapshot(config: dict[str, Any]) -> str:
    lines = ["gateway dials:"]
    for key in sorted(config.keys()):
        lines.append(f"{key}={_format_config_value(config.get(key))}")
    return "\n".join(lines)


def _kb_list_text(runtime: RuntimeHooks, config: dict[str, Any], limit: int) -> str:
    snapshot = runtime.inspect_kb(config=config, limit=limit)
    clauses = snapshot.get("clauses", [])
    if not isinstance(clauses, list):
        clauses = []
    total = int(snapshot.get("clause_count", len(clauses)) or len(clauses))
    truncated = int(snapshot.get("truncated", 0) or 0)
    kb_path = str(snapshot.get("kb_path", "")).strip()
    if not clauses:
        return (
            f"KB clauses: 0 (path: {kb_path or 'in-memory'})\n"
            "No clauses currently loaded."
        )
    lines = [f"KB clauses shown: {len(clauses)} / total {total} (path: {kb_path or 'in-memory'})"]
    for idx, clause in enumerate(clauses, start=1):
        lines.append(f"{idx}. {clause}")
    if truncated > 0:
        lines.append(f"... {truncated} older clause(s) not shown.")
    return "\n".join(lines)


def _normalize_slash_input(raw: str) -> str:
    text = str(raw or "")
    # Remove common invisible characters that can break command detection.
    for token in ("\ufeff", "\u200b", "\u200c", "\u200d", "\u2060"):
        text = text.replace(token, "")
    text = text.strip()
    if text.startswith("／"):  # full-width slash
        text = "/" + text[1:]
    return text


def _handle_slash_command(
    *,
    utterance: str,
    session: SessionState,
    config: dict,
    runtime: RuntimeHooks,
    config_store: Any | None = None,
) -> dict | None:
    text = _normalize_slash_input(utterance)
    if not text.startswith("/"):
        return None

    parts = text.split(maxsplit=1)
    command = str(parts[0]).strip().lower()
    argument = str(parts[1]).strip() if len(parts) > 1 else ""
    active_config = dict(config)
    known_keys = sorted(active_config.keys())
    pending = bool(session.pending_clarification)
    answer_text = ""

    if command == "/help":
        answer_text = (
            "Slash commands:\n"
            "/help - show this command list\n"
            "/dials - list all tunable gateway settings\n"
            "/show <key> - show one dial value\n"
            "/set <key> <value> - update a dial (persisted)\n"
            "/ce <0..1> - set clarification_eagerness\n"
            "/kb [limit] - list KB clauses (default 80)\n"
            "/kb clear - empty runtime KB\n"
            "/state - show session state and pending clarification status\n"
            "/cancel - cancel current pending clarification"
        )
    elif command in {"/config", "/dials"}:
        answer_text = _format_config_snapshot(active_config)
    elif command == "/show":
        key = argument.strip()
        if not key:
            answer_text = _format_config_snapshot(active_config)
        elif key not in active_config:
            answer_text = (
                f"Unknown dial: {key}\n"
                f"Available keys: {', '.join(known_keys)}"
            )
        else:
            answer_text = f"{key}={_format_config_value(active_config.get(key))}"
    elif command == "/set":
        set_parts = text.split(maxsplit=2)
        if len(set_parts) < 3:
            answer_text = "Usage: /set <key> <value>"
        else:
            key = str(set_parts[1]).strip()
            raw_value = str(set_parts[2]).strip()
            if key not in active_config:
                answer_text = (
                    f"Unknown dial: {key}\n"
                    f"Available keys: {', '.join(known_keys)}"
                )
            else:
                ok, parsed_value, error = _coerce_config_value(key, raw_value, active_config.get(key))
                if not ok:
                    answer_text = error
                else:
                    updated_config = _apply_config_updates(
                        config=active_config,
                        config_store=config_store,
                        updates={key: parsed_value},
                    )
                    applied = updated_config.get(key)
                    answer_text = f"Updated {key}={_format_config_value(applied)}."
                    if _format_config_value(applied) != _format_config_value(parsed_value):
                        answer_text += (
                            f"\nRequested {key}={_format_config_value(parsed_value)} "
                            f"but invariant/sanitizer applied {key}={_format_config_value(applied)}."
                        )
                    if key == "strict_mode" and bool(applied):
                        answer_text += (
                            "\nStrict mode invariants active: compiler_mode=strict, "
                            "served_handoff_mode=never, require_final_confirmation=true."
                        )
    elif command == "/ce":
        if not argument:
            answer_text = "Usage: /ce <0..1>"
        else:
            ok, parsed_value, error = _coerce_config_value(
                "clarification_eagerness",
                argument,
                active_config.get("clarification_eagerness", 0.75),
            )
            if not ok:
                answer_text = error
            else:
                updated_config = _apply_config_updates(
                    config=active_config,
                    config_store=config_store,
                    updates={"clarification_eagerness": parsed_value},
                )
                answer_text = (
                    "Updated clarification_eagerness="
                    f"{_format_config_value(updated_config.get('clarification_eagerness'))}."
                )
    elif command in {"/kb", "/emptykb"}:
        kb_parts = argument.split()
        kb_action = kb_parts[0].lower() if kb_parts else "list"
        if command == "/emptykb":
            kb_action = "clear"

        if kb_action in {"clear", "empty", "reset"}:
            clear_result = runtime.clear_kb(config=active_config)
            answer_text = (
                f"KB cleared: {int(clear_result.get('cleared_count', 0) or 0)} clause(s) removed.\n"
                f"before={int(clear_result.get('before_count', 0) or 0)} "
                f"after={int(clear_result.get('after_count', 0) or 0)}\n"
                f"path={str(clear_result.get('kb_path', '')).strip() or 'in-memory'}"
            )
        elif kb_action in {"list", "ls", "show"} or kb_action.isdigit():
            limit = 80
            if kb_action.isdigit():
                limit = max(1, min(500, int(kb_action)))
            elif len(kb_parts) > 1:
                try:
                    limit = max(1, min(500, int(kb_parts[1])))
                except ValueError:
                    limit = 80
            answer_text = _kb_list_text(runtime, active_config, limit)
        elif not kb_action:
            answer_text = _kb_list_text(runtime, active_config, 80)
        else:
            answer_text = "Usage: /kb [limit] | /kb clear"
    elif command == "/state":
        answer_text = (
            f"session_id={session.session_id}\n"
            f"turn_count={len(session.turns)}\n"
            f"pending_clarification={pending}\n"
            f"front_door_uri={active_config.get('front_door_uri', '')}"
        )
    elif command == "/cancel":
        if session.pending_clarification:
            session.pending_clarification = None
            answer_text = "Pending clarification cancelled."
        else:
            answer_text = "No pending clarification to cancel."
    else:
        answer_text = (
            f"Unknown slash command: {command}\n"
            "Use /help to see available commands."
        )

    return {
        "command": command,
        "answer": {
            "speaker": "prethink-gateway",
            "text": answer_text,
            "mode": "slash_command",
        },
    }
