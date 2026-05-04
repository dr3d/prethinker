"""Shared contracts for the proposed clean KB pipeline split.

These contracts are intentionally structural. They describe the seams needed to
port the existing behavior without moving production code yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


Intent = str


@dataclass(frozen=True)
class CompilerConfig:
    backend: str = "lmstudio"
    base_url: str = "http://127.0.0.1:1234"
    model: str = "qwen/qwen3.6-35b-a3b"
    context_length: int = 16384
    timeout: int = 120
    prompt_path: str = ""
    semantic_ir_enabled: bool = False


@dataclass
class PreThinkSessionConfig:
    enabled: bool = True
    all_turns_require_prethink: bool = False
    clarification_eagerness: float = 0.75
    require_final_confirmation: bool = True


@dataclass
class PendingPreThink:
    prethink_id: str
    mode: str
    utterance: str
    compiler_intent: Intent
    compiler_uncertainty_score: float = 0.0
    clarification_required_before_query: bool = False
    clarification_question: str = ""
    clarification_reason: str = ""
    clarification_answer: str = ""
    writes_applied: int = 0
    queries_executed: int = 0
    query_attempts: int = 0
    query_no_results: int = 0
    no_result_streak: int = 0
    last_query: str = ""
    last_query_status: str = ""
    compiler_trace: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizationEvent:
    kind: str
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ApplyOptions:
    registry_signatures: set[str] = field(default_factory=set)
    strict_registry: bool = False
    type_schema: dict[str, Any] = field(default_factory=dict)
    strict_types: bool = False
    turn_index: int | None = None
    temporal_dual_write: bool = False
    temporal_predicate: str = "at_step"


class RuntimePort(Protocol):
    def empty_kb(self) -> dict[str, Any]: ...

    def assert_fact(self, clause: str) -> dict[str, Any]: ...

    def assert_rule(self, clause: str) -> dict[str, Any]: ...

    def retract_fact(self, clause: str) -> dict[str, Any]: ...

    def query_rows(self, query: str) -> dict[str, Any]: ...


class CompilerClient(Protocol):
    def compile_prethink(
        self,
        utterance: str,
        *,
        context: list[str] | None = None,
    ) -> tuple[dict[str, Any] | None, str, dict[str, Any]]:
        ...

    def compile_parse(
        self,
        utterance: str,
        *,
        compiler_intent: str,
        clarification_question: str = "",
        clarification_answer: str = "",
        context: list[str] | None = None,
    ) -> tuple[dict[str, Any] | None, str, dict[str, Any]]:
        ...


class SemanticMapperPort(Protocol):
    def to_prethink_payload(self, ir: dict[str, Any]) -> dict[str, Any]: ...

    def to_legacy_parse(
        self,
        ir: dict[str, Any],
        *,
        allowed_predicates: list[str] | None = None,
        predicate_contracts: list[dict[str, Any]] | None = None,
    ) -> tuple[dict[str, Any], list[str]]:
        ...


class ApplyEnginePort(Protocol):
    def apply(self, runtime: RuntimePort, parsed: dict[str, Any]) -> dict[str, Any]: ...

