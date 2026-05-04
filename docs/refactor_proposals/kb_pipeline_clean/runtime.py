"""Runtime boundary for the proposed refactor.

The first migration can keep these as thin adapters around the active
`kb_pipeline` implementations. A later migration can move the implementations
here and leave compatibility imports behind.
"""

from __future__ import annotations

from typing import Any

from .contracts import RuntimePort


class LegacyCoreRuntimeAdapter(RuntimePort):
    """Adapter preserving the active `kb_pipeline.CorePrologRuntime` behavior."""

    def __init__(self, *, max_depth: int = 500) -> None:
        from kb_pipeline import CorePrologRuntime

        self._runtime = CorePrologRuntime(max_depth=max_depth)

    @property
    def legacy_runtime(self) -> Any:
        return self._runtime

    def empty_kb(self) -> dict[str, Any]:
        return self._runtime.empty_kb()

    def assert_fact(self, clause: str) -> dict[str, Any]:
        return self._runtime.assert_fact(clause)

    def assert_rule(self, clause: str) -> dict[str, Any]:
        return self._runtime.assert_rule(clause)

    def retract_fact(self, clause: str) -> dict[str, Any]:
        return self._runtime.retract_fact(clause)

    def query_rows(self, query: str) -> dict[str, Any]:
        return self._runtime.query_rows(query)


class LegacyParseOnlyRuntimeAdapter(RuntimePort):
    """Adapter preserving the active parse-only scenario runtime."""

    def __init__(self) -> None:
        from kb_pipeline import ParseOnlyRuntime

        self._runtime = ParseOnlyRuntime()

    @property
    def legacy_runtime(self) -> Any:
        return self._runtime

    def empty_kb(self) -> dict[str, Any]:
        return self._runtime.empty_kb()

    def assert_fact(self, clause: str) -> dict[str, Any]:
        return self._runtime.assert_fact(clause)

    def assert_rule(self, clause: str) -> dict[str, Any]:
        return self._runtime.assert_rule(clause)

    def retract_fact(self, clause: str) -> dict[str, Any]:
        return self._runtime.retract_fact(clause)

    def query_rows(self, query: str) -> dict[str, Any]:
        return self._runtime.query_rows(query)


def normalize_clause(clause: str) -> str:
    """Compatibility wrapper for the active clause normalizer."""

    from kb_pipeline import _normalize_clause

    return _normalize_clause(clause)

