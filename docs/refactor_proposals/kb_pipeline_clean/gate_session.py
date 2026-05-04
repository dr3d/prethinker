"""Pre-think session and authorization gate proposal."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .contracts import PendingPreThink, PreThinkSessionConfig


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
        number = float(value)
    except Exception:
        return default
    return max(0.0, min(1.0, number))


class PreThinkGate:
    """Stateful pre-think gate extracted from the MCP server."""

    def __init__(self, config: PreThinkSessionConfig | None = None) -> None:
        self.config = config or PreThinkSessionConfig()
        self.pending: PendingPreThink | None = None
        self._counter = 1

    def next_prethink_id(self) -> str:
        token = f"pt-{self._counter:06d}"
        self._counter += 1
        return token

    def update_session(self, args: dict[str, Any]) -> dict[str, Any]:
        config = self.config
        if "enabled" in args:
            config = replace(config, enabled=_coerce_bool(args.get("enabled"), config.enabled))
        if "all_turns_require_prethink" in args:
            config = replace(
                config,
                all_turns_require_prethink=_coerce_bool(
                    args.get("all_turns_require_prethink"),
                    config.all_turns_require_prethink,
                ),
            )
        if "clarification_eagerness" in args:
            config = replace(
                config,
                clarification_eagerness=_clip_01(
                    args.get("clarification_eagerness"),
                    config.clarification_eagerness,
                ),
            )
        if "require_final_confirmation" in args:
            config = replace(
                config,
                require_final_confirmation=_coerce_bool(
                    args.get("require_final_confirmation"),
                    config.require_final_confirmation,
                ),
            )
        self.config = config
        return {"status": "success", "result_type": "session_updated", "state": self.serialize()}

    def open_turn(
        self,
        *,
        utterance: str,
        mode: str,
        compiler_intent: str,
        compiler_uncertainty_score: float,
        clarification_required_before_query: bool,
        clarification_question: str = "",
        clarification_reason: str = "",
        compiler_trace: dict[str, Any] | None = None,
    ) -> PendingPreThink:
        self.pending = PendingPreThink(
            prethink_id=self.next_prethink_id(),
            mode=mode,
            utterance=utterance,
            compiler_intent=compiler_intent,
            compiler_uncertainty_score=_clip_01(compiler_uncertainty_score, 0.0),
            clarification_required_before_query=bool(clarification_required_before_query),
            clarification_question=str(clarification_question or "").strip(),
            clarification_reason=str(clarification_reason or "").strip(),
            compiler_trace=dict(compiler_trace or {}),
        )
        return self.pending

    def record_clarification_answer(self, args: dict[str, Any]) -> dict[str, Any]:
        if self.pending is None:
            return {
                "status": "blocked",
                "result_type": "pre_think_required",
                "message": "No active pre-think turn. Call pre_think first.",
            }
        expected_id = self.pending.prethink_id
        provided_id = str(args.get("prethink_id", "")).strip()
        if not provided_id or provided_id != expected_id:
            return {
                "status": "blocked",
                "result_type": "pre_think_id_mismatch",
                "message": "Provided prethink_id does not match active turn.",
                "required": {"prethink_id": expected_id},
            }
        answer = str(args.get("answer", "")).strip()
        if not answer:
            return {"status": "validation_error", "message": "answer is required"}
        if not _coerce_bool(args.get("confirmed"), True):
            return {
                "status": "blocked",
                "result_type": "clarification_not_confirmed",
                "message": "Clarification was not confirmed; query gate remains active.",
                "pending_prethink": self.pending_summary(),
            }
        self.pending.clarification_answer = answer
        self.pending.clarification_required_before_query = False
        return {
            "status": "success",
            "result_type": "clarification_recorded",
            "prethink_id": expected_id,
            "answer": answer,
            "state": self.serialize(),
        }

    def tool_requires_prethink(self, tool: str) -> bool:
        if tool in {"assert_fact", "assert_rule", "retract_fact"}:
            return bool(self.config.enabled)
        if tool == "query_rows":
            return bool(self.config.enabled and self.config.all_turns_require_prethink)
        return False

    def check_tool_call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any] | None:
        pending = self.pending
        provided_id = str(arguments.get("prethink_id", "")).strip()
        gate_required = self.tool_requires_prethink(tool)
        if tool == "query_rows" and provided_id and pending is not None:
            gate_required = True
        if not gate_required:
            return None
        if pending is None:
            return {
                "status": "blocked",
                "result_type": "pre_think_required",
                "message": "Call pre_think first for this turn and pass returned prethink_id.",
                "required": {
                    "tool": tool,
                    "call_pre_think": True,
                    "confirm_required": bool(
                        tool in {"assert_fact", "assert_rule", "retract_fact"}
                        and self.config.require_final_confirmation
                    ),
                },
                "state": self.serialize(),
            }
        expected_id = pending.prethink_id
        if not provided_id or provided_id != expected_id:
            return {
                "status": "blocked",
                "result_type": "pre_think_id_mismatch",
                "message": "Tool call must include the active prethink_id.",
                "required": {"tool": tool, "prethink_id": expected_id},
                "pending_prethink": self.pending_summary(),
                "state": self.serialize(),
            }
        if tool in {"assert_fact", "assert_rule", "retract_fact"}:
            if self.config.require_final_confirmation and not _coerce_bool(arguments.get("confirm"), False):
                return {
                    "status": "blocked",
                    "result_type": "confirmation_required",
                    "message": "Write intents require explicit confirmation.",
                    "required": {"tool": tool, "prethink_id": expected_id, "confirm": True},
                    "pending_prethink": self.pending_summary(),
                    "state": self.serialize(),
                }
        if tool == "query_rows" and pending.clarification_required_before_query:
            return {
                "status": "blocked",
                "result_type": "clarification_required_before_query",
                "message": "Resolve clarification before running query for this turn.",
                "required": {
                    "tool": "record_clarification_answer",
                    "prethink_id": expected_id,
                    "answer_required": True,
                },
                "clarification_question": pending.clarification_question,
                "pending_prethink": self.pending_summary(),
                "state": self.serialize(),
            }
        if tool == "query_rows":
            if pending.no_result_streak >= 2 and pending.writes_applied == 0:
                return self._query_loop_guard("repeated_no_result_streak")
            if pending.query_attempts >= 6 and pending.writes_applied == 0:
                return self._query_loop_guard("query_attempt_limit")
        return None

    def consume_tool_result(self, tool: str, result: dict[str, Any]) -> None:
        pending = self.pending
        if pending is None:
            return
        status = str(result.get("status", "")).strip()
        if tool in {"assert_fact", "assert_rule", "retract_fact"} and status == "success":
            pending.writes_applied += 1
        if tool != "query_rows":
            return
        pending.query_attempts += 1
        query_text = str(result.get("prolog_query", "")).strip().lower()
        if status == "success":
            pending.queries_executed += 1
            pending.no_result_streak = 0
        elif status == "no_results":
            pending.query_no_results += 1
            if query_text and query_text == pending.last_query and pending.last_query_status == "no_results":
                pending.no_result_streak += 1
            else:
                pending.no_result_streak = 1
        else:
            pending.no_result_streak = 0
        pending.last_query = query_text
        pending.last_query_status = status

    def pending_summary(self) -> dict[str, Any]:
        if self.pending is None:
            return {}
        return {
            "prethink_id": self.pending.prethink_id,
            "mode": self.pending.mode,
            "utterance": self.pending.utterance,
            "compiler_intent": self.pending.compiler_intent,
            "compiler_uncertainty_score": self.pending.compiler_uncertainty_score,
            "clarification_required_before_query": self.pending.clarification_required_before_query,
            "clarification_question": self.pending.clarification_question,
            "writes_applied": self.pending.writes_applied,
            "queries_executed": self.pending.queries_executed,
            "query_attempts": self.pending.query_attempts,
            "query_no_results": self.pending.query_no_results,
            "no_result_streak": self.pending.no_result_streak,
        }

    def serialize(self) -> dict[str, Any]:
        return {
            "enabled": self.config.enabled,
            "all_turns_require_prethink": self.config.all_turns_require_prethink,
            "clarification_eagerness": round(float(self.config.clarification_eagerness), 4),
            "require_final_confirmation": self.config.require_final_confirmation,
            "pending_prethink": self.pending_summary(),
        }

    def _query_loop_guard(self, reason: str) -> dict[str, Any]:
        return {
            "status": "blocked",
            "result_type": "query_loop_guard",
            "message": "Query loop guard blocked repeated no-result queries for this turn.",
            "required": {
                "action": "call_pre_think_with_new_user_utterance",
                "reason": reason,
            },
            "pending_prethink": self.pending_summary(),
            "state": self.serialize(),
        }

