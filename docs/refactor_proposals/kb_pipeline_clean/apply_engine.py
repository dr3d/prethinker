"""Deterministic apply boundary for the proposed refactor."""

from __future__ import annotations

from typing import Any

from .contracts import ApplyOptions, RuntimePort


class LegacyScenarioApplyEngine:
    """Wraps active `_apply_to_kb` behavior for scenario parity."""

    def __init__(self, options: ApplyOptions | None = None) -> None:
        self.options = options or ApplyOptions()

    def apply(
        self,
        runtime: RuntimePort,
        parsed: dict[str, Any],
        *,
        corpus_clauses: set[str] | None = None,
    ) -> dict[str, Any]:
        from kb_pipeline import _apply_to_kb

        return _apply_to_kb(
            runtime,
            parsed,
            corpus_clauses=corpus_clauses,
            registry_signatures=set(self.options.registry_signatures),
            strict_registry=self.options.strict_registry,
            type_schema=dict(self.options.type_schema or {"entities": {}, "predicates": {}}),
            strict_types=self.options.strict_types,
            turn_index=self.options.turn_index,
            temporal_dual_write=self.options.temporal_dual_write,
            temporal_predicate=self.options.temporal_predicate,
        )


class ToolApplyEngine:
    """Small MCP-style apply engine for already-normalized legacy parses."""

    def apply(self, runtime: RuntimePort, parsed: dict[str, Any]) -> dict[str, Any]:
        intent = str(parsed.get("intent", "other")).strip()
        if intent == "assert_fact":
            clauses = [str(item).strip() for item in parsed.get("facts", []) if str(item).strip()]
            if not clauses and str(parsed.get("logic_string", "")).strip():
                clauses = [str(parsed.get("logic_string", "")).strip()]
            return self._apply_many(runtime.assert_fact, "assert_fact", clauses)
        if intent == "assert_rule":
            clauses = [str(item).strip() for item in parsed.get("rules", []) if str(item).strip()]
            if not clauses and str(parsed.get("logic_string", "")).strip():
                clauses = [str(parsed.get("logic_string", "")).strip()]
            return self._apply_many(runtime.assert_rule, "assert_rule", clauses)
        if intent == "retract":
            clauses = [str(item).strip() for item in parsed.get("facts", []) if str(item).strip()]
            return self._apply_many(runtime.retract_fact, "retract_fact", clauses)
        if intent == "query":
            queries = [str(item).strip() for item in parsed.get("queries", []) if str(item).strip()]
            query = queries[0] if queries else str(parsed.get("logic_string", "")).strip()
            return {"tool": "query_rows", "input": query, "result": runtime.query_rows(query)}
        return {
            "tool": "none",
            "input": None,
            "result": {"status": "skipped", "message": "Intent=other; no operation applied."},
        }

    @staticmethod
    def _apply_many(method: Any, tool: str, clauses: list[str]) -> dict[str, Any]:
        if not clauses:
            return {
                "tool": tool,
                "input": None,
                "result": {"status": "validation_error", "message": "No clauses were provided."},
            }
        rows = [{"clause": clause, "result": method(clause)} for clause in clauses]
        if len(rows) == 1:
            return {"tool": tool, "input": rows[0]["clause"], "result": rows[0]["result"]}
        status = "success" if all(row["result"].get("status") == "success" for row in rows) else "partial"
        return {
            "tool": f"{tool}_batch",
            "input": clauses,
            "result": {"status": status, "result_type": "batch", "operations": rows},
        }

