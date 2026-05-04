"""Semantic IR boundary for the proposed refactor."""

from __future__ import annotations

from typing import Any


class ActiveSemanticIRMapper:
    """Thin wrapper around the active Semantic IR mapper functions."""

    def to_prethink_payload(self, ir: dict[str, Any]) -> dict[str, Any]:
        from src.semantic_ir import semantic_ir_to_prethink_payload

        return semantic_ir_to_prethink_payload(ir)

    def to_legacy_parse(
        self,
        ir: dict[str, Any],
        *,
        allowed_predicates: list[str] | None = None,
        predicate_contracts: list[dict[str, Any]] | None = None,
    ) -> tuple[dict[str, Any], list[str]]:
        from src.semantic_ir import semantic_ir_to_legacy_parse

        return semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
        )

    def admission_diagnostics(
        self,
        ir: dict[str, Any],
        *,
        allowed_predicates: list[str] | None = None,
        predicate_contracts: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        from src.semantic_ir import semantic_ir_admission_diagnostics

        return semantic_ir_admission_diagnostics(
            ir,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
        )


SEMANTIC_MAPPER_BOUNDARY = {
    "authority": "mapper_controls_admission",
    "router_context": "advisory_only",
    "input_contracts": [
        "semantic_ir_v1",
        "allowed_predicates",
        "predicate_contracts",
        "kb_context_pack",
    ],
    "output_contracts": [
        "legacy_parse",
        "mapper_warnings",
        "admission_diagnostics",
    ],
}

