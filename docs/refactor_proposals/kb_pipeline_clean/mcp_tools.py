"""MCP tool surface proposal."""

from __future__ import annotations

from typing import Any


TOOL_NAMES = (
    "pre_think",
    "set_pre_think_session",
    "show_pre_think_state",
    "record_clarification_answer",
    "process_utterance",
    "query_rows",
    "assert_fact",
    "assert_rule",
    "retract_fact",
)


def tool_surface() -> list[dict[str, Any]]:
    return [{"name": name} for name in TOOL_NAMES]


class ProcessUtteranceService:
    """Orchestration seam for the future MCP server.

    Production can migrate `src.mcp_server.PrologMCPServer.process_utterance`
    here after gate, compiler, mapper, and apply components have parity tests.
    """

    def __init__(self, *, gate: Any, compiler: Any, apply_engine: Any, runtime: Any) -> None:
        self.gate = gate
        self.compiler = compiler
        self.apply_engine = apply_engine
        self.runtime = runtime

    def process_utterance(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(
            "Proposal seam only. Port active process_utterance after parity fixtures exist."
        )

