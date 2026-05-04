"""Compiler boundary for pre-think and parse compilation."""

from __future__ import annotations

from typing import Any


class LegacyMCPCompilerFacade:
    """Facade over the active `PrologMCPServer` compiler methods.

    This keeps migration low risk: callers can exercise the new orchestration
    seam while the actual compiler, prompt, rescue, and trace behavior remains
    in the current MCP server.
    """

    def __init__(self, server: Any) -> None:
        self._server = server

    def compile_prethink(
        self,
        utterance: str,
        *,
        context: list[str] | None = None,
    ) -> tuple[dict[str, Any] | None, str, dict[str, Any]]:
        compiled, error = self._server._compile_prethink_semantics(
            utterance,
            context=context or None,
        )
        return compiled, error, dict(getattr(self._server, "_last_prethink_trace", {}) or {})

    def compile_parse(
        self,
        utterance: str,
        *,
        compiler_intent: str,
        clarification_question: str = "",
        clarification_answer: str = "",
        context: list[str] | None = None,
    ) -> tuple[dict[str, Any] | None, str, dict[str, Any]]:
        parsed, error = self._server._compile_apply_parse(
            utterance=utterance,
            compiler_intent=compiler_intent,
            clarification_question=clarification_question,
            clarification_answer=clarification_answer,
            context=context or None,
        )
        return parsed, error, dict(getattr(self._server, "_last_parse_trace", {}) or {})


class PromptBuilderInventory:
    """Names the prompt helpers that should move out of `kb_pipeline.py`."""

    prethink_prompt = "_build_compiler_prompt"
    classifier_prompt = "_build_classifier_prompt"
    extractor_prompt = "_build_extractor_prompt"
    logic_only_extractor_prompt = "_build_logic_only_extractor_prompt"
    repair_prompt = "_build_repair_prompt"

