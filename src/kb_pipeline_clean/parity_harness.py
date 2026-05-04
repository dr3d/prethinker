"""Structural parity harness for the clean KB pipeline proposal.

The functions here compare compiler/gate/apply shapes. They intentionally do
not interpret source prose or decide whether an answer is semantically better.
"""

from __future__ import annotations

import importlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .parse_normalization import NORMALIZER_PIPELINE


MISSING = "<missing>"
FIXTURE_NAMING_TOKENS = ("three_bears", "goldilocks", "story_world")


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    return [str(item).strip() for item in _as_list(value) if str(item).strip()]


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except Exception:
        return None


def _optional_float(value: Any, *, digits: int = 4) -> float | None:
    try:
        return round(float(value), digits)
    except Exception:
        return None


def _sorted_rows(rows: Any) -> list[dict[str, Any]]:
    normalized = [dict(row) for row in _as_list(rows) if isinstance(row, dict)]
    return sorted(normalized, key=_stable_json)


def canonical_query_result(result: Any) -> dict[str, Any]:
    """Return stable query result fields used by parity fixtures."""

    payload = _as_dict(result)
    rows = _sorted_rows(payload.get("rows", []))
    return {
        "status": str(payload.get("status", "")).strip(),
        "result_type": str(payload.get("result_type", "")).strip(),
        "prolog_query": str(payload.get("prolog_query", payload.get("query", ""))).strip(),
        "num_rows": _optional_int(payload.get("num_rows", len(rows))),
        "rows": rows,
    }


def canonical_operation(operation: Any) -> dict[str, Any]:
    """Return stable operation fields without re-judging the operation."""

    payload = _as_dict(operation)
    result = _as_dict(payload.get("result"))
    query_result = canonical_query_result(result) if payload.get("tool") == "query_rows" else {}
    return {
        "tool": str(payload.get("tool", "")).strip(),
        "clause": str(payload.get("clause", "")).strip(),
        "query": str(payload.get("query", payload.get("input", ""))).strip(),
        "status": str(result.get("status", "")).strip(),
        "result_type": str(result.get("result_type", "")).strip(),
        "query_result": query_result,
        "support": _as_dict(payload.get("support")),
    }


def canonical_execution_result(execution: Any) -> dict[str, Any]:
    """Return the apply/execution signature for result-shape parity."""

    payload = _as_dict(execution)
    operations = [canonical_operation(item) for item in _as_list(payload.get("operations"))]
    return {
        "status": str(payload.get("status", "")).strip(),
        "intent": str(payload.get("intent", "")).strip(),
        "writes_applied": _optional_int(payload.get("writes_applied")),
        "operation_tools": [item.get("tool", "") for item in operations],
        "operations": operations,
        "query_result": canonical_query_result(payload.get("query_result")),
        "errors": _string_list(payload.get("errors")),
    }


def canonical_parse_result(parsed: Any) -> dict[str, Any]:
    """Return deterministic compiler parse fields for parity snapshots."""

    payload = _as_dict(parsed)
    confidence = _as_dict(payload.get("confidence"))
    components = _as_dict(payload.get("components"))
    return {
        "intent": str(payload.get("intent", "")).strip(),
        "logic_string": str(payload.get("logic_string", "")).strip(),
        "facts": _string_list(payload.get("facts")),
        "rules": _string_list(payload.get("rules")),
        "queries": _string_list(payload.get("queries")),
        "retracts": _string_list(payload.get("retracts")),
        "correction_retract_clauses": _string_list(payload.get("correction_retract_clauses")),
        "needs_clarification": bool(payload.get("needs_clarification", False)),
        "clarification_question": str(payload.get("clarification_question", "")).strip(),
        "clarification_reason": str(payload.get("clarification_reason", "")).strip(),
        "uncertainty_score": _optional_float(payload.get("uncertainty_score")),
        "uncertainty_label": str(payload.get("uncertainty_label", "")).strip(),
        "confidence": {
            "overall": _optional_float(confidence.get("overall")),
            "intent": _optional_float(confidence.get("intent")),
            "logic": _optional_float(confidence.get("logic")),
        },
        "components": {
            "atoms": sorted(_string_list(components.get("atoms"))),
            "variables": sorted(_string_list(components.get("variables"))),
            "predicates": sorted(_string_list(components.get("predicates"))),
        },
    }


def canonical_compiler_trace(trace: Any) -> dict[str, Any]:
    """Return stable trace fields that matter to extraction parity."""

    payload = _as_dict(trace)
    summary = _as_dict(payload.get("summary"))
    parse_trace = _as_dict(payload.get("parse"))
    prethink_trace = _as_dict(payload.get("prethink"))
    semantic_ir = _first_dict(
        payload.get("semantic_ir"),
        parse_trace.get("semantic_ir"),
        parse_trace.get("ir"),
        prethink_trace.get("semantic_ir"),
    )
    prethink = _as_dict(payload.get("prethink"))
    return {
        "summary": {
            "route": str(summary.get("route", "")).strip(),
            "compiler_intent": str(summary.get("compiler_intent", "")).strip(),
            "needs_clarification": bool(summary.get("needs_clarification", False)),
            "prethink_source": str(summary.get("prethink_source", "")).strip(),
        },
        "semantic_ir_present": bool(semantic_ir),
        "semantic_ir_schema": _semantic_ir_schema(semantic_ir),
        "prethink_present": bool(prethink),
        "parse_rescues": _string_list(payload.get("parse_rescues")),
        "validation_errors": _string_list(payload.get("validation_errors")),
    }


def _first_dict(*values: Any) -> dict[str, Any]:
    for value in values:
        payload = _as_dict(value)
        if payload:
            return payload
    return {}


def _semantic_ir_schema(semantic_ir: dict[str, Any]) -> str:
    direct = str(semantic_ir.get("schema_version", "")).strip()
    if direct:
        return direct
    parsed = _as_dict(semantic_ir.get("parsed"))
    return str(parsed.get("schema_version", "")).strip()


def canonical_process_result(result: Any) -> dict[str, Any]:
    """Return the process_utterance front-door signature."""

    payload = _as_dict(result)
    front_door = _as_dict(payload.get("front_door"))
    return {
        "status": str(payload.get("status", "")).strip(),
        "result_type": str(payload.get("result_type", "")).strip(),
        "front_door": {
            "route": str(front_door.get("route", "")).strip(),
            "compiler_intent": str(front_door.get("compiler_intent", "")).strip(),
            "needs_clarification": bool(front_door.get("needs_clarification", False)),
            "clarification_question": str(front_door.get("clarification_question", "")).strip(),
            "clarification_reason": str(front_door.get("clarification_reason", "")).strip(),
            "ambiguity_score": _optional_float(front_door.get("ambiguity_score")),
        },
        "execution": canonical_execution_result(payload.get("execution")),
        "compiler_trace": canonical_compiler_trace(payload.get("compiler_trace")),
    }


def signature_from_payload(kind: str, payload: Any) -> dict[str, Any]:
    """Canonicalize a known harness payload kind."""

    normalized_kind = str(kind).strip().lower()
    if normalized_kind in {"process", "process_result", "process_utterance"}:
        return canonical_process_result(payload)
    if normalized_kind in {"execution", "apply", "apply_result"}:
        return canonical_execution_result(payload)
    if normalized_kind in {"parse", "parse_result", "compiler_parse"}:
        return canonical_parse_result(payload)
    if normalized_kind in {"trace", "compiler_trace"}:
        return canonical_compiler_trace(payload)
    if normalized_kind in {"query", "query_result"}:
        return canonical_query_result(payload)
    raise ValueError(f"Unknown parity payload kind: {kind}")


def compare_signatures(
    baseline: Any,
    candidate: Any,
    *,
    ignore_paths: set[str] | None = None,
) -> dict[str, Any]:
    """Compare two canonical signatures and return path-oriented diffs."""

    ignored = ignore_paths or set()
    diffs: list[dict[str, Any]] = []

    def walk(path: str, left: Any, right: Any) -> None:
        if path in ignored:
            return
        if isinstance(left, dict) and isinstance(right, dict):
            keys = sorted(set(left) | set(right))
            for key in keys:
                next_path = f"{path}.{key}" if path else str(key)
                walk(next_path, left.get(key, MISSING), right.get(key, MISSING))
            return
        if isinstance(left, list) and isinstance(right, list):
            max_len = max(len(left), len(right))
            for index in range(max_len):
                next_path = f"{path}[{index}]"
                walk(
                    next_path,
                    left[index] if index < len(left) else MISSING,
                    right[index] if index < len(right) else MISSING,
                )
            return
        if left != right:
            diffs.append({"path": path, "baseline": left, "candidate": right})

    walk("", baseline, candidate)
    return {
        "status": "pass" if not diffs else "fail",
        "diff_count": len(diffs),
        "diffs": diffs,
    }


def normalizer_inventory_audit(module_name: str = "kb_pipeline") -> dict[str, Any]:
    """Check that the proposal's normalizer inventory maps to live symbols."""

    module = importlib.import_module(module_name)
    symbols: list[str] = []
    for spec in NORMALIZER_PIPELINE:
        symbols.extend(spec.legacy_symbols)
    counts = Counter(symbols)
    duplicate_symbols = sorted(symbol for symbol, count in counts.items() if count > 1)
    missing_symbols = sorted(symbol for symbol in symbols if not hasattr(module, symbol))
    fixture_named_specs = sorted(
        {
            spec.new_name
            for spec in NORMALIZER_PIPELINE
            if any(
                token in " ".join([spec.phase, spec.new_name, spec.trace_event]).lower()
                for token in FIXTURE_NAMING_TOKENS
            )
        }
    )
    return {
        "status": "pass" if not missing_symbols and not duplicate_symbols and not fixture_named_specs else "fail",
        "module": module_name,
        "normalizer_count": len(NORMALIZER_PIPELINE),
        "legacy_symbol_count": len(symbols),
        "missing_legacy_symbols": missing_symbols,
        "duplicate_legacy_symbols": duplicate_symbols,
        "fixture_named_new_specs": fixture_named_specs,
        "trace_events": [spec.trace_event for spec in NORMALIZER_PIPELINE],
    }


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
