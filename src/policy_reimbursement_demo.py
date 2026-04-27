from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kb_pipeline import CorePrologRuntime


DOMAIN = "policy_reimbursement_demo@v0"

ALLOWED_PREDICATES = [
    "requested_by/2",
    "approved_by/2",
    "manages/2",
    "reimbursement_month/2",
    "self_approval/1",
    "manager_conflict_approval/1",
    "violation/2",
]

PREDICATE_CONTRACTS = [
    {"signature": "requested_by/2", "args": ["reimbursement", "person"]},
    {"signature": "approved_by/2", "args": ["reimbursement", "person"]},
    {"signature": "manages/2", "args": ["manager", "report"]},
    {"signature": "reimbursement_month/2", "args": ["reimbursement", "month"]},
    {"signature": "self_approval/1", "args": ["reimbursement"]},
    {"signature": "manager_conflict_approval/1", "args": ["reimbursement"]},
    {"signature": "violation/2", "args": ["event_or_record", "policy"]},
]

DOMAIN_CONTEXT = [
    "Profile scope: reimbursement approval policy and concrete reimbursement events.",
    "Goal: turn plain-language policy into narrow executable Prolog rules when the rule is simple and explicit.",
    "A rule candidate must include candidate_operations[].clause. Do not emit a rule operation with only predicate/args.",
    "Use operation='rule' only for executable clauses. Use operation='assert' only for direct ground event facts.",
    "For self-approval policy, safe executable form: self_approval(R) :- requested_by(R, P), approved_by(R, P).",
    "For manager-conflict policy, safe executable form: manager_conflict_approval(R) :- requested_by(R, Requester), approved_by(R, Approver), manages(Approver, Requester).",
    "For violation policy, safe executable forms may derive violation(R, reimbursement_policy) from self_approval(R) or manager_conflict_approval(R).",
    "When the utterance says a condition violates policy, include a violation/2 rule path. If operation budget is tight, prefer violation/2 rules over intermediate helper rules.",
    "Good bridge rule examples: violation(R, reimbursement_policy) :- self_approval(R). violation(R, reimbursement_policy) :- manager_conflict_approval(R).",
    "Do not assert violation/2 as a durable fact merely because the rule could derive it. Keep derived violations as query/runtime answers.",
    "Concrete reimbursement events are direct facts: requested_by/2, approved_by/2, manages/2, reimbursement_month/2.",
    "Corrections to prior event facts may use retract/assert when the target prior KB clause is visible and the correction is explicit.",
    "Questions such as 'which reimbursements violated policy?' should become query operations over violation/2, not fact writes.",
]

DEMO_TURNS = [
    {
        "id": "policy_rule_setup",
        "utterance": (
            "Record this reimbursement policy: a reimbursement violates policy if the requester approved it. "
            "A reimbursement also violates policy if the approver manages the requester."
        ),
        "expect": {
            "kind": "rule_setup",
            "query": "violation(R, reimbursement_policy).",
            "expected_rows": [],
        },
    },
    {
        "id": "february_events",
        "utterance": (
            "In February, reimbursement R1 was requested by Maya and approved by Maya. "
            "R2 was requested by Theo and approved by Lena, and Lena manages Theo. "
            "R3 was requested by Priya and approved by Sam."
        ),
        "expect": {
            "kind": "event_ingest",
            "query": "violation(R, reimbursement_policy).",
            "expected_rows": ["r1", "r2"],
        },
    },
    {
        "id": "violation_query",
        "utterance": "Which February reimbursements violated the reimbursement policy, and why?",
        "expect": {
            "kind": "query",
            "query": "violation(R, reimbursement_policy).",
            "expected_rows": ["r1", "r2"],
        },
    },
    {
        "id": "approval_correction",
        "utterance": (
            "Correction: R2 was not approved by Lena after all; R2 was approved by Omar. "
            "Which February reimbursements violate the policy now?"
        ),
        "expect": {
            "kind": "correction_plus_query",
            "query": "violation(R, reimbursement_policy).",
            "expected_rows": ["r1"],
        },
    },
]


@dataclass
class PolicyDemoState:
    runtime: CorePrologRuntime = field(default_factory=CorePrologRuntime)
    facts: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    recent_committed_logic: list[str] = field(default_factory=list)


def apply_mapped_to_policy_runtime(mapped: dict[str, Any], state: PolicyDemoState) -> dict[str, Any]:
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    clauses = diagnostics.get("clauses", {}) if isinstance(diagnostics, dict) else {}
    result: dict[str, Any] = {
        "asserted_facts": [],
        "asserted_rules": [],
        "retracted_facts": [],
        "queries": list(clauses.get("queries", []) if isinstance(clauses, dict) else []),
        "apply_errors": [],
    }
    for clause in _string_list(clauses.get("retracts", []) if isinstance(clauses, dict) else []):
        target = _normalize_clause(_strip_retract_wrapper(clause))
        outcome = state.runtime.retract_fact(target)
        if outcome.get("status") in {"success", "no_results"}:
            state.facts = [item for item in state.facts if _normalize_clause(item) != target]
            result["retracted_facts"].append(target)
            state.recent_committed_logic.append(f"retract_fact :: {target}")
        else:
            result["apply_errors"].append({"clause": clause, "result": outcome})
    for clause in _string_list(clauses.get("facts", []) if isinstance(clauses, dict) else []):
        normalized = _normalize_clause(clause)
        outcome = state.runtime.assert_fact(normalized)
        if outcome.get("status") == "success":
            if normalized not in state.facts:
                state.facts.append(normalized)
            result["asserted_facts"].append(normalized)
            state.recent_committed_logic.append(f"assert_fact :: {normalized}")
        else:
            result["apply_errors"].append({"clause": normalized, "result": outcome})
    for clause in _string_list(clauses.get("rules", []) if isinstance(clauses, dict) else []):
        normalized = _normalize_clause(clause)
        outcome = state.runtime.assert_rule(normalized)
        if outcome.get("status") == "success":
            if normalized not in state.rules:
                state.rules.append(normalized)
            result["asserted_rules"].append(normalized)
            state.recent_committed_logic.append(f"assert_rule :: {normalized}")
        else:
            result["apply_errors"].append({"clause": normalized, "result": outcome})
    state.recent_committed_logic = state.recent_committed_logic[-24:]
    return result


def query_policy_runtime(state: PolicyDemoState, query: str) -> dict[str, Any]:
    normalized = _normalize_clause(query)
    outcome = state.runtime.query_rows(normalized)
    rows = outcome.get("rows", []) if isinstance(outcome, dict) else []
    values = sorted(
        {
            str(row.get("R", "")).strip()
            for row in rows
            if isinstance(row, dict) and str(row.get("R", "")).strip()
        }
    )
    return {"query": normalized, "result": outcome, "r_values": values}


def build_policy_kb_context_pack(state: PolicyDemoState, *, utterance: str, turn_id: str) -> dict[str, Any]:
    terms = _token_terms(utterance)
    relevant = [clause for clause in [*state.facts, *state.rules] if _clause_terms(clause) & terms]
    if not relevant:
        relevant = [*state.facts[-12:], *state.rules[-8:]]
    entity_candidates: list[str] = []
    for clause in relevant:
        for arg in _flat_clause_args(clause):
            if arg and arg not in entity_candidates and not _is_variable(arg):
                entity_candidates.append(arg)
    return {
        "version": "semantic_ir_context_pack_v1",
        "authority": "context_only_runtime_kb_remains_authoritative",
        "active_profile": DOMAIN,
        "turn_id": turn_id,
        "manifest": {
            "total_committed_facts": len(state.facts),
            "total_committed_rules": len(state.rules),
            "relevant_clause_count": len(relevant),
            "retrieval_terms": sorted(terms)[:48],
            "context_budget_note": "Compact symbolic retrieval for the policy demo; not a full KB dump.",
        },
        "relevant_clauses": relevant[-24:],
        "current_state_candidates": state.facts[-24:],
        "current_state_subject_candidates": _current_subject_candidates(state.facts[-24:]),
        "entity_candidates": entity_candidates[:32],
        "recent_committed_logic": state.recent_committed_logic[-16:],
        "small_kb_snapshot": [*state.facts[-12:], *state.rules[-8:]],
        "instructions": [
            "Use exact KB clauses to resolve references, corrections, and conflict pressure.",
            "Do not copy KB clauses into candidate_operations unless the current utterance explicitly changes them.",
            "For query turns, use existing KB rules/facts as support and emit query operations instead of derived writes.",
        ],
    }


def summarize_policy_demo_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    parsed_ok = sum(1 for row in rows if row.get("parsed_ok"))
    apply_error_free = sum(1 for row in rows if not row.get("runtime_apply", {}).get("apply_errors"))
    expected_match = sum(1 for row in rows if row.get("expected_match"))
    derived_not_written = sum(1 for row in rows if not row.get("derived_violation_write_leak"))
    return {
        "turns": total,
        "parsed_ok": parsed_ok,
        "apply_error_free": apply_error_free,
        "expected_query_matches": expected_match,
        "no_derived_violation_write_leak": derived_not_written,
        "rough_score": round(
            (
                _fraction(parsed_ok, total)
                + _fraction(apply_error_free, total)
                + _fraction(expected_match, total)
                + _fraction(derived_not_written, total)
            )
            / 4,
            3,
        ),
    }


def write_policy_demo_markdown(record: dict[str, Any], path: Path) -> None:
    summary = record.get("summary", {})
    lines = [
        "# Policy Reimbursement Demo Trace",
        "",
        f"Generated: {_utc_now()}",
        "",
        f"- Backend/model: `{record.get('backend', '')}` / `{record.get('model', '')}`",
        f"- Domain: `{DOMAIN}`",
        f"- Turns: `{summary.get('turns', 0)}`",
        f"- Parsed OK: `{summary.get('parsed_ok', 0)}`",
        f"- Apply error free: `{summary.get('apply_error_free', 0)}`",
        f"- Expected query matches: `{summary.get('expected_query_matches', 0)}`",
        f"- No derived violation write leak: `{summary.get('no_derived_violation_write_leak', 0)}`",
        f"- Rough score: `{summary.get('rough_score', 0.0)}`",
        "",
        "This demo tests whether plain English can install narrow policy rules, ingest concrete events, answer derived violation queries, and handle an explicit correction without writing derived violations as durable facts.",
        "",
        "## Turn Results",
        "",
    ]
    for row in record.get("rows", []):
        runtime_query = row.get("runtime_query", {})
        lines.extend(
            [
                f"### {row.get('index', '')}. {row.get('turn_id', '')}",
                "",
                f"- Utterance: {row.get('utterance', '')}",
                f"- Decision: model `{row.get('model_decision', '')}`, projected `{row.get('projected_decision', '')}`",
                f"- Admission: `{row.get('admitted_count', 0)}` admitted, `{row.get('skipped_count', 0)}` skipped",
                f"- Expected query rows: `{row.get('expected_rows', [])}`",
                f"- Runtime query rows: `{runtime_query.get('r_values', [])}`",
                f"- Expected match: `{row.get('expected_match', False)}`",
                f"- Derived violation write leak: `{row.get('derived_violation_write_leak', False)}`",
                "",
                "Committed this turn:",
                "",
            ]
        )
        apply_result = row.get("runtime_apply", {})
        for label, key in (
            ("facts", "asserted_facts"),
            ("rules", "asserted_rules"),
            ("retracts", "retracted_facts"),
        ):
            values = apply_result.get(key, []) if isinstance(apply_result, dict) else []
            if values:
                lines.append(f"- {label}:")
                lines.extend([f"  - `{value}`" for value in values])
        if not any(apply_result.get(key) for key in ("asserted_facts", "asserted_rules", "retracted_facts")):
            lines.append("- none")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_policy_demo_html(record: dict[str, Any], path: Path) -> None:
    summary = record.get("summary", {})
    rows_html = []
    for row in record.get("rows", []):
        apply_result = row.get("runtime_apply", {})
        runtime_query = row.get("runtime_query", {})
        facts = _code_list(apply_result.get("asserted_facts", []))
        rules = _code_list(apply_result.get("asserted_rules", []))
        retracts = _code_list(apply_result.get("retracted_facts", []))
        rows_html.append(
            f"""
<details class="turn" open>
  <summary>
    <span class="index">{html.escape(str(row.get('index', '')))}.</span>
    <code>{html.escape(str(row.get('turn_id', '')))}</code>
    <span class="meta">decision={html.escape(str(row.get('projected_decision', '')))} | admitted={html.escape(str(row.get('admitted_count', 0)))} | query={html.escape(str(runtime_query.get('r_values', [])))}</span>
  </summary>
  <section class="utterance">{html.escape(str(row.get('utterance', '')))}</section>
  <div class="grid">
    <div><h3>Committed Facts</h3>{facts}</div>
    <div><h3>Committed Rules</h3>{rules}</div>
    <div><h3>Retracts</h3>{retracts}</div>
    <div><h3>Runtime Query</h3><pre>{html.escape(json.dumps(runtime_query, indent=2, ensure_ascii=False))}</pre></div>
  </div>
  <details>
    <summary>Semantic IR JSON</summary>
    <pre class="json">{html.escape(json.dumps(row.get('parsed', {}), indent=2, ensure_ascii=False))}</pre>
  </details>
  <details>
    <summary>Mapper Diagnostics JSON</summary>
    <pre class="json">{html.escape(json.dumps(row.get('admission_diagnostics', {}), indent=2, ensure_ascii=False))}</pre>
  </details>
</details>
"""
        )
    body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Policy Reimbursement Demo Trace</title>
<style>
body {{ margin: 0; padding: 32px; background: #0d171f; color: #f4eadb; font: 18px/1.5 system-ui, sans-serif; }}
h1 {{ margin-top: 0; }}
code, pre {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 18px 0 26px; }}
.card {{ background: #1f2b34; border: 1px solid #41515b; border-radius: 8px; padding: 14px; }}
.card b {{ display: block; font-size: 28px; }}
.turn {{ background: #1c2831; border: 1px solid #42515a; border-radius: 10px; margin: 18px 0; padding: 16px; }}
.turn > summary {{ cursor: pointer; display: flex; gap: 12px; align-items: baseline; flex-wrap: wrap; font-size: 22px; font-weight: 700; }}
.index {{ color: #ffa45f; }}
.meta {{ font-size: 15px; opacity: .85; }}
.utterance {{ margin: 14px 0; padding: 14px; background: #382920; border: 1px solid #665243; border-radius: 8px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; }}
h3 {{ margin: 8px 0; font-size: 16px; color: #ffce99; text-transform: uppercase; letter-spacing: .04em; }}
ul {{ margin-top: 0; padding-left: 22px; }}
pre {{ white-space: pre-wrap; overflow: auto; max-height: 280px; background: #121c24; border: 1px solid #33434e; border-radius: 8px; padding: 12px; }}
pre.json {{ max-height: 520px; }}
</style>
</head>
<body>
<h1>Policy Reimbursement Demo Trace</h1>
<p>Plain English installs policy rules, event facts arrive later, the runtime answers derived violation queries, and derived violations are kept out of durable writes.</p>
<div class="cards">
  <div class="card"><span>Turns</span><b>{html.escape(str(summary.get('turns', 0)))}</b></div>
  <div class="card"><span>Parsed OK</span><b>{html.escape(str(summary.get('parsed_ok', 0)))}</b></div>
  <div class="card"><span>Expected Matches</span><b>{html.escape(str(summary.get('expected_query_matches', 0)))}</b></div>
  <div class="card"><span>Rough Score</span><b>{html.escape(str(summary.get('rough_score', 0.0)))}</b></div>
</div>
{''.join(rows_html)}
</body>
</html>
"""
    path.write_text(body, encoding="utf-8")


def _code_list(values: Any) -> str:
    items = _string_list(values)
    if not items:
        return "<p>- none</p>"
    return "<ul>" + "".join(f"<li><code>{html.escape(item)}</code></li>" for item in items) + "</ul>"


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _normalize_clause(clause: str) -> str:
    text = str(clause or "").strip()
    if not text:
        return ""
    return text if text.endswith(".") else f"{text}."


def _strip_retract_wrapper(clause: str) -> str:
    text = str(clause or "").strip()
    if text.endswith("."):
        text = text[:-1].strip()
    match = re.fullmatch(r"retract\s*\((.*)\)", text)
    return match.group(1).strip() if match else text


def _flat_clause_args(clause: str) -> list[str]:
    match = re.search(r"\b[a-z][a-z0-9_]*\s*\((.*)\)", str(clause or ""))
    if not match:
        return []
    return [part.strip().strip(".") for part in _split_top_level(match.group(1), ",")]


def _clause_terms(clause: str) -> set[str]:
    return _token_terms(clause)


def _token_terms(text: str) -> set[str]:
    terms: set[str] = set()
    for token in re.findall(r"[A-Za-z][A-Za-z0-9_'-]*", str(text or "")):
        normalized = re.sub(r"[^a-z0-9_]+", "_", token.casefold()).strip("_")
        if normalized:
            terms.add(normalized)
            terms.update(part for part in normalized.split("_") if len(part) >= 2)
    return terms


def _current_subject_candidates(facts: list[str]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for clause in facts:
        match = re.match(r"\s*([a-z][a-z0-9_]*)\s*\(", clause)
        if not match:
            continue
        args = _flat_clause_args(clause)
        if not args:
            continue
        item = {
            "entity": args[0],
            "role": "current_state_subject",
            "predicate": f"{match.group(1)}/{len(args)}",
            "source_clause": _normalize_clause(clause),
        }
        if item not in candidates:
            candidates.append(item)
    return candidates[:16]


def _split_top_level(text: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in str(text or ""):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char == delimiter and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _is_variable(value: str) -> bool:
    text = str(value or "").strip()
    return bool(text) and (text[0].isupper() or text.startswith("_"))


def _fraction(value: int, total: int) -> float:
    return 0.0 if total <= 0 else float(value) / float(total)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
