"""Shared governance checks for retained oracle fact clauses.

Expected oracle facts can become positive proposal evidence, so they must obey
the same compact-atom and closed-value discipline as compiled facts. Forbidden
facts are negative sentinels: they may intentionally name off-domain or
prose-shaped bad outputs, but those values should be visible in audit warnings
and must never count as positive support.
"""

from __future__ import annotations

import re
from typing import Any

from scripts.audit_kb_atom_inventory import (
    DEFAULT_MAX_ATOM_CHARS,
    DEFAULT_MAX_ATOM_TOKENS,
    DEFAULT_MAX_PREDICATE_CHARS,
    DEFAULT_MAX_PREDICATE_TOKENS,
    ParsedFact,
    _atom_shape_issues,
)
from src.carrier_contract_registry import carrier_contract


CITATION_PAYLOAD_RE = re.compile(
    r"^(?:cfr_|fdca_|usc_|u_s_c_|us_c_|\d+_cfr_|\d+_usc_)",
    re.IGNORECASE,
)


def audit_oracle_fact_clause(
    *,
    predicate: str,
    args: list[str],
    clause: str,
    line_no: int,
    role: str,
) -> tuple[list[str], list[str]]:
    """Return blocking errors and warnings for one retained oracle fact."""

    expected = role == "expected"
    fact = ParsedFact(predicate=predicate, args=tuple(args), clause=clause.strip())
    shape_messages = _atom_shape_messages(fact=fact, line_no=line_no, prefix=role)
    value_messages = _value_domain_messages(fact=fact, line_no=line_no, prefix=role)
    if expected:
        return shape_messages + value_messages, []
    return [], shape_messages + value_messages


def _atom_shape_messages(*, fact: ParsedFact, line_no: int, prefix: str) -> list[str]:
    messages: list[str] = []
    for index, raw_arg in enumerate(fact.args, start=1):
        if _quoted_atom_contains_whitespace(raw_arg):
            messages.append(f"line_{line_no}:{prefix}_atom_shape:quoted_atom_contains_whitespace:arg{index}")
    for issue in _atom_shape_issues(
        fact,
        max_predicate_chars=DEFAULT_MAX_PREDICATE_CHARS,
        max_predicate_tokens=DEFAULT_MAX_PREDICATE_TOKENS,
        max_atom_chars=DEFAULT_MAX_ATOM_CHARS,
        max_atom_tokens=DEFAULT_MAX_ATOM_TOKENS,
    ):
        issue_type = str(issue.get("issue_type") or "unknown")
        field = str(issue.get("field") or "unknown")
        messages.append(f"line_{line_no}:{prefix}_atom_shape:{issue_type}:{field}")
    return messages


def _value_domain_messages(*, fact: ParsedFact, line_no: int, prefix: str) -> list[str]:
    contract = carrier_contract(fact.signature)
    if not isinstance(contract, dict):
        return []
    arg_names = [str(item).strip() for item in contract.get("args") or []]
    if len(arg_names) != len(fact.args):
        return [
            f"line_{line_no}:{prefix}_carrier_contract_arg_count_mismatch:"
            f"{len(arg_names)}!={len(fact.args)}"
        ]
    domains = contract.get("value_domains")
    value_domains = domains if isinstance(domains, dict) else {}
    messages: list[str] = []
    for index, raw_arg in enumerate(fact.args):
        if _is_variable_arg(raw_arg):
            continue
        arg_name = arg_names[index]
        value = _normalize_arg(raw_arg)
        provenance_issue = _provenance_payload_issue(arg_name, value)
        if provenance_issue:
            messages.append(f"line_{line_no}:{prefix}_value_domain:{arg_name}:{provenance_issue}:{value}")
        allowed_values = {
            str(item).strip()
            for item in value_domains.get(arg_name, [])
            if str(item).strip()
        }
        if allowed_values and value not in allowed_values:
            messages.append(f"line_{line_no}:{prefix}_value_domain:{arg_name}:value_not_allowed:{value}")
    return messages


def _normalize_arg(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        text = text[1:-1]
    return text.strip()


def _is_variable_arg(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(text) and (text.startswith("_") or text[0].isupper())


def _quoted_atom_contains_whitespace(value: Any) -> bool:
    text = str(value or "").strip()
    if len(text) < 2 or text[0] != text[-1] or text[0] not in {"'", '"'}:
        return False
    return bool(re.search(r"\s", text[1:-1]))


def _provenance_payload_issue(arg_name: str, value: str) -> str | None:
    if arg_name != "source_or_scope":
        return None
    if CITATION_PAYLOAD_RE.match(str(value or "").strip()):
        return "citation_payload_in_source_or_scope"
    return None
