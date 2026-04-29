from __future__ import annotations

from typing import Any


TEMPORAL_KERNEL_PREDICATE_CONTRACTS: list[dict[str, Any]] = [
    {
        "signature": "event_on/2",
        "arguments": ["event", "date_or_time_anchor"],
        "notes": "Explicit date/time anchor for an event.",
    },
    {
        "signature": "interval_start/2",
        "arguments": ["interval", "date_or_time_anchor"],
        "notes": "Start anchor for an explicitly stated interval.",
    },
    {
        "signature": "interval_end/2",
        "arguments": ["interval", "date_or_time_anchor"],
        "notes": "End anchor for an explicitly stated interval.",
    },
    {
        "signature": "before/2",
        "arguments": ["earlier_event_or_anchor", "later_event_or_anchor"],
        "notes": "Directly admitted ordering relation.",
    },
    {
        "signature": "after/2",
        "arguments": ["later_event_or_anchor", "earlier_event_or_anchor"],
        "notes": "Derived inverse of before/2.",
    },
    {
        "signature": "precedes/2",
        "arguments": ["earlier_event_or_anchor", "later_event_or_anchor"],
        "notes": "Transitive temporal ordering over admitted before/2 facts.",
    },
    {
        "signature": "follows/2",
        "arguments": ["later_event_or_anchor", "earlier_event_or_anchor"],
        "notes": "Derived inverse of precedes/2.",
    },
    {
        "signature": "during/2",
        "arguments": ["event", "interval"],
        "notes": "Event is explicitly scoped to an interval.",
    },
    {
        "signature": "overlaps/2",
        "arguments": ["interval_or_event", "interval_or_event"],
        "notes": "Direct overlap relation admitted from source language.",
    },
    {
        "signature": "same_time/2",
        "arguments": ["event_or_anchor", "event_or_anchor"],
        "notes": "Direct same-time relation admitted from source language.",
    },
    {
        "signature": "concurrent/2",
        "arguments": ["event_or_interval", "event_or_interval"],
        "notes": "Derived coarse concurrence from same_time/2 or overlaps/2.",
    },
    {
        "signature": "supersedes/2",
        "arguments": ["new_temporal_record", "old_temporal_record"],
        "notes": "Direct correction/supersession relation between temporal records.",
    },
    {
        "signature": "corrected_temporal_value/4",
        "arguments": ["record", "field", "new_value", "old_value"],
        "notes": "Explicit temporal correction record.",
    },
]


TEMPORAL_KERNEL_RULES: list[str] = [
    "after(Later, Earlier) :- before(Earlier, Later).",
    "precedes(Earlier, Later) :- before(Earlier, Later).",
    "precedes(Earlier, Later) :- before(Earlier, Middle), precedes(Middle, Later).",
    "follows(Later, Earlier) :- precedes(Earlier, Later).",
    "concurrent(A, B) :- same_time(A, B).",
    "concurrent(A, B) :- overlaps(A, B).",
]


TEMPORAL_KERNEL_SIGNATURES: set[str] = {
    str(row["signature"]) for row in TEMPORAL_KERNEL_PREDICATE_CONTRACTS
}


def install_temporal_kernel(runtime: Any) -> dict[str, Any]:
    """Install deterministic temporal rules into a Prolog-like runtime.

    This is deliberately not a language parser. It only adds rules that reason
    over already-admitted temporal predicates.
    """

    results: list[dict[str, Any]] = []
    for rule in TEMPORAL_KERNEL_RULES:
        assert_rule = getattr(runtime, "assert_rule", None)
        if not callable(assert_rule):
            results.append(
                {
                    "status": "error",
                    "rule": rule,
                    "message": "Runtime does not expose assert_rule.",
                }
            )
            continue
        result = assert_rule(rule)
        if isinstance(result, dict):
            row = dict(result)
            row["rule"] = rule
            results.append(row)
        else:
            results.append({"status": "unknown", "rule": rule, "raw": result})
    ok = all(str(row.get("status", "")).strip() == "success" for row in results)
    return {
        "status": "success" if ok else "partial_failure",
        "rule_count": len(TEMPORAL_KERNEL_RULES),
        "rules": results,
    }
