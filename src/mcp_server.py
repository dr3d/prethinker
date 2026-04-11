"""
Local MCP-style server shim for prethinker.

This module is intentionally lightweight:
- exposes a small MCP-like tool interface (`tools_list` + `tools_call`)
- keeps deterministic KB operations local via CorePrologRuntime
- provides session toggles for pre-think interposition experiments

It is not a full MCP transport server. Host UIs/runtimes can wrap this class.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kb_pipeline import CorePrologRuntime


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


@dataclass
class PreThinkSessionState:
    enabled: bool = True
    all_turns_require_prethink: bool = False
    clarification_eagerness: float = 0.75
    require_final_confirmation: bool = True


class PrologMCPServer:
    """
    Minimal local MCP-compatible façade.

    Methods used by kb_pipeline runtime path:
    - empty_kb
    - assert_fact
    - assert_rule
    - retract_fact
    - query_rows

    MCP-style helper methods for control-plane experiments:
    - tools_list
    - tools_call
    """

    def __init__(self, kb_path: str = "") -> None:
        self._runtime = CorePrologRuntime()
        self._kb_path = str(Path(kb_path).resolve()) if str(kb_path).strip() else ""
        self._session = PreThinkSessionState()

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

    # MCP-style tools
    def tools_list(self) -> dict[str, Any]:
        return {
            "status": "success",
            "tools": [
                {
                    "name": "pre_think",
                    "description": "Generate pre-think decision packet for an utterance.",
                },
                {
                    "name": "set_pre_think_session",
                    "description": "Toggle session-level pre-think settings.",
                },
                {
                    "name": "show_pre_think_state",
                    "description": "Show current pre-think session state.",
                },
                {"name": "query_rows", "description": "Run deterministic Prolog query_rows."},
                {"name": "assert_fact", "description": "Assert deterministic fact clause."},
                {"name": "assert_rule", "description": "Assert deterministic rule clause."},
                {"name": "retract_fact", "description": "Retract deterministic fact clause."},
            ],
        }

    def list_tools(self) -> dict[str, Any]:
        return self.tools_list()

    def tools_call(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        tool = str(name or "").strip()
        if not tool:
            return {"status": "validation_error", "message": "Tool name is required."}

        if tool == "pre_think":
            return self.pre_think(args)
        if tool == "set_pre_think_session":
            return self.set_pre_think_session(args)
        if tool == "show_pre_think_state":
            return self.show_pre_think_state()
        if tool == "query_rows":
            return self.query_rows(str(args.get("query", "")))
        if tool == "assert_fact":
            return self.assert_fact(str(args.get("clause", "")))
        if tool == "assert_rule":
            return self.assert_rule(str(args.get("clause", "")))
        if tool == "retract_fact":
            return self.retract_fact(str(args.get("clause", "")))

        return {"status": "not_found", "message": f"Unknown tool: {tool}"}

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.tools_call(name=name, arguments=arguments)

    # Pre-think controls
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

    def pre_think(self, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        utterance = str(args.get("utterance", "")).strip()
        if not utterance:
            return {"status": "validation_error", "message": "utterance is required"}

        lower = utterance.lower()
        looks_like_query = utterance.endswith("?") or lower.startswith(
            ("who ", "what ", "when ", "where ", "why ", "how ", "is ", "are ", "does ", "do ")
        )
        looks_like_write = any(
            token in lower
            for token in (" is ", " are ", " was ", " were ", " if ", " then ", " retract ", " remove ")
        )

        if not self._session.enabled:
            mode = "forward_with_facts"
            note = "pre-think disabled for this session; forwarding without gating."
        elif looks_like_query:
            mode = "short_circuit"
            note = "query-like utterance; candidate for deterministic short-circuit."
        elif looks_like_write:
            mode = "block_or_clarify"
            note = "write-like utterance; apply validation and clarification gates before mutation."
        else:
            mode = "forward_with_facts"
            note = "mixed/unclear utterance; forward with deterministic evidence packet."

        packet = {
            "utterance": utterance,
            "mode": mode,
            "signals": {
                "looks_like_query": looks_like_query,
                "looks_like_write": looks_like_write,
            },
            "requires_user_confirmation": bool(self._session.require_final_confirmation),
            "clarification_eagerness": float(self._session.clarification_eagerness),
            "source_of_truth": "prolog_kb",
            "note": note,
        }
        return {
            "status": "success",
            "result_type": "pre_think_packet",
            "packet": packet,
            "state": self._serialize_state(),
        }

    def _serialize_state(self) -> dict[str, Any]:
        state = {
            "enabled": bool(self._session.enabled),
            "all_turns_require_prethink": bool(self._session.all_turns_require_prethink),
            "clarification_eagerness": round(float(self._session.clarification_eagerness), 4),
            "require_final_confirmation": bool(self._session.require_final_confirmation),
        }
        if self._kb_path:
            state["knowledge_base_path"] = self._kb_path
        return state
