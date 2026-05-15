"""Audit whether lens vocabulary terms surface on unlike compile artifacts.

This is a compile-artifact audit, not a QA score. It compares a vocabulary of
structural lens terms against admitted direct facts and source-record facts. A
term is "structural" when it appears in direct predicates or arguments, "source
only" when it appears only in source-record ledger text, and "absent" when the
source itself did not expose that term family.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class LensTerm:
    term: str
    tokens: tuple[str, ...]
    min_arity: int = 2
    predicate_patterns: tuple[str, ...] = ()
    contract_groups: tuple[tuple[str, ...], ...] = ()
    contract_anchor: int = 0


EVIDENCE_PROVENANCE_TERMS: tuple[LensTerm, ...] = (
    LensTerm(
        "prepared",
        ("prepared", "preparer", "drafted", "wrote", "written"),
        2,
        ("prepared_by", "report_prepared_by", "created_by", "written_by", "drafted_by", "authored_by"),
    ),
    LensTerm(
        "presented",
        ("presented", "submitted", "filed", "introduced"),
        3,
        ("presented_by", "presented_to", "submitted_by", "submitted_to", "filed_by", "filed_with", "introduced_by", "read_aloud"),
    ),
    LensTerm("dated", ("dated", "date"), 2, (".*_date", "dated")),
    LensTerm("admitted", ("admitted", "entered"), 2, ("admitted_into", "admitted_by", "entered_into", "entered_by")),
    LensTerm("relied_on", ("relied", "relies", "basis", "cited"), 2, ("relied_on", "basis_for", "cited_by", "cited_in", "used_as_basis")),
    LensTerm("commissioned", ("commissioned", "requested", "ordered"), 3, ("commissioned_by", "commissioned_test", "requested_by", "ordered_by")),
    LensTerm("corrected", ("corrected", "correction", "revised", "amended"), 2, ("corrected_by", "correction_.*", "revised_by", "amended_.*")),
    LensTerm("located", ("located", "found", "stored", "held"), 2, ("located_in", "found_in", "stored_in", "held_in")),
)

RULE_COMPOSITION_TERMS: tuple[LensTerm, ...] = (
    LensTerm(
        "base_rule",
        ("base", "default", "standard", "normal"),
        2,
        ("base_rule", "default_rule", "standard_rule", "rule_text", "rule_scope"),
        (("rule_condition",), ("rule_action", "rule_outcome", "rule_consequence")),
    ),
    LensTerm(
        "exception",
        ("exception", "except", "unless", "waiver", "exempt"),
        3,
        ("exception_rule", "rule_exception", "exception_applies", "waiver_rule", "exemption_rule"),
        (("exception_condition", "waiver_condition", "exemption_condition"), ("exception_effect", "waiver_effect", "exemption_effect")),
    ),
    LensTerm(
        "threshold",
        ("threshold", "minimum", "maximum", "cap", "limit"),
        3,
        (".*_threshold", "threshold", "rule_threshold", "limit_rule", "cap_rule", "requires_count"),
        (("threshold_measure", "threshold_subject"), ("threshold_value", "threshold_amount", "threshold_limit")),
    ),
    LensTerm(
        "activation_condition",
        ("activates", "activation", "triggered", "when"),
        3,
        ("activation_condition", "trigger_condition", "applies_when", "rule_activation"),
        (("rule_condition", "trigger_condition", "applies_when"), ("rule_action", "rule_outcome", "rule_consequence")),
    ),
    LensTerm(
        "eligibility_condition",
        ("eligible", "eligibility", "qualifies", "qualify", "required"),
        3,
        ("eligibility_condition", "qualifies_when", "required_condition", "requirement_condition", "rule_condition"),
    ),
    LensTerm(
        "override",
        ("override", "overrides", "supersede", "supersedes"),
        3,
        ("override", "overrides", "rule_override", "supersedes", "rule_precedence"),
    ),
    LensTerm(
        "precedence",
        ("precedence", "priority", "prior", "before"),
        3,
        ("precedence", "rule_precedence", "priority_order", "takes_precedence"),
    ),
    LensTerm(
        "expiration",
        ("expires", "expiration", "sunset", "valid"),
        2,
        ("expiration", "expires_on", "sunset_date", "valid_until"),
    ),
    LensTerm(
        "vote_requirement",
        ("vote", "votes", "majority", "quorum"),
        3,
        ("vote_requirement", "required_vote", "approval_vote", "quorum_requirement", "requires_vote"),
    ),
    LensTerm(
        "fallback_rule",
        ("fallback", "otherwise", "default"),
        2,
        ("fallback_rule", "otherwise_rule", "default_rule", "fallback_to"),
    ),
)

AUTHORITY_CUSTODY_TERMS: tuple[LensTerm, ...] = (
    LensTerm(
        "court_order",
        ("court", "order", "injunction", "judgment"),
        3,
        ("court_order", "court_.*order", "order_issued_by", "legal_order", "injunction_order"),
    ),
    LensTerm(
        "governing_rule",
        ("governing", "rule", "policy", "bylaw", "ordinance"),
        3,
        ("governing_rule", "rule_governs", "applicable_rule", "policy_rule", "ordinance_rule"),
    ),
    LensTerm(
        "board_vote",
        ("board", "vote", "voted", "decision"),
        3,
        ("board_vote", "body_vote", "vote_decision", "board_decision", "approved_by_vote"),
    ),
    LensTerm(
        "official_record",
        ("official", "record", "registry", "register", "filed"),
        3,
        ("official_record", "record_status", "registry_record", "filed_record", "register_entry"),
    ),
    LensTerm(
        "staff_note",
        ("staff", "note", "memo"),
        3,
        ("staff_note", "staff_memo", "memo_by", "note_by", "staff_record"),
    ),
    LensTerm(
        "draft_recommendation",
        ("draft", "recommendation", "recommended", "proposed"),
        3,
        ("draft_recommendation", "recommendation_status", "recommended_by", "proposed_by", "draft_proposal"),
    ),
    LensTerm(
        "controlling_finding",
        ("controlling", "finding", "binding", "final"),
        3,
        ("controlling_finding", "binding_finding", "final_finding", "controlling_source", "effective_authority"),
    ),
    LensTerm(
        "noncontrolling_source",
        ("noncontrolling", "advisory", "copied", "superseded", "rejected"),
        3,
        ("noncontrolling_source", "advisory_source", "superseded_source", "rejected_source"),
    ),
    LensTerm(
        "custody_holder",
        ("custody", "custodian", "holder", "held"),
        2,
        ("custody_holder", "custodian_for", "held_by", "custody_of", "custody_assignment"),
    ),
    LensTerm(
        "access_control",
        ("access", "permission", "release", "unlock"),
        2,
        ("access_control", "access_controller", "access_permission", "release_authority", "permission_source", "unlock_authority"),
    ),
)

OPERATIONAL_RECORD_STATUS_TERMS: tuple[LensTerm, ...] = (
    LensTerm("received", ("received", "intake", "submitted"), 3, ("received_by", "received_at", "intake_received", "submission_received")),
    LensTerm("filed", ("filed", "logged", "entered"), 3, ("filed_by", "filed_record", "logged_by", "record_entry", "entered_by")),
    LensTerm("assigned", ("assigned", "routed", "referred"), 3, ("assigned_to", "routed_to", "referred_to", "owner_assigned")),
    LensTerm("approved", ("approved", "granted", "accepted"), 3, ("approved_by", "approval_decision", "decision_approved", "granted_by")),
    LensTerm("denied", ("denied", "rejected", "refused"), 3, ("denied_by", "denial_decision", "decision_denied", "rejected_by")),
    LensTerm("withdrawn", ("withdrawn", "retracted", "cancelled"), 3, ("withdrawn_by", "withdrawn_on", "status_withdrawn", "retracted_by")),
    LensTerm("pending", ("pending", "unresolved", "deferred"), 2, ("pending_item", "unresolved_item", "deferred_item", "current_status")),
    LensTerm("corrected", ("corrected", "amended", "revised"), 3, ("corrected_by", "correction_.*", "amended_by", "revised_by")),
    LensTerm("superseded", ("superseded", "replaced", "overridden"), 2, ("superseded_by", "replaced_by", "overridden_by")),
    LensTerm("reopened", ("reopened", "reinstated", "resumed"), 3, ("reopened_by", "reinstated_by", "status_reopened", "resumed_on")),
    LensTerm("closed", ("closed", "completed", "final"), 3, ("closed_by", "completed_by", "final_status", "closure_record")),
    LensTerm("current_status", ("current", "final", "active"), 2, ("current_status", "final_status", "active_status", "status_at")),
    LensTerm("status_transition", ("transition", "before", "after"), 4, ("status_transition", "status_changed", "state_transition", "status_before_after")),
)

LENS_TERMS: dict[str, tuple[LensTerm, ...]] = {
    "authority_custody": AUTHORITY_CUSTODY_TERMS,
    "evidence_provenance": EVIDENCE_PROVENANCE_TERMS,
    "operational_record_status": OPERATIONAL_RECORD_STATUS_TERMS,
    "rule_composition": RULE_COMPOSITION_TERMS,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lens", choices=sorted(LENS_TERMS), required=True)
    parser.add_argument(
        "--compile-json",
        action="append",
        type=Path,
        default=[],
        help="Compile JSON file or directory containing domain_bootstrap_file_*.json. Repeatable.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = _expand_compile_paths(args.compile_json)
    if not paths:
        raise SystemExit("No compile JSON files found.")
    terms = LENS_TERMS[args.lens]
    reports = [audit_compile(path, lens=args.lens, terms=terms) for path in paths]
    payload = {
        "schema": "lens_vocabulary_transfer_audit_v1",
        "lens": args.lens,
        "compile_count": len(reports),
        "summary": summarize_reports(reports, terms),
        "reports": reports,
    }
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(payload), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _expand_compile_paths(inputs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for item in inputs:
        if item.is_dir():
            matches = sorted(item.glob("domain_bootstrap_file_*.json"))
            if matches:
                out.append(matches[-1])
                continue
            out.extend(sorted(item.glob("*/domain_bootstrap_file_*.json")))
        elif item.is_file():
            out.append(item)
    return sorted(dict.fromkeys(path.resolve() for path in out))


def audit_compile(path: Path, *, lens: str, terms: tuple[LensTerm, ...]) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    facts = _facts_from_compile(data)
    source_facts = [fact for fact in facts if _predicate_name(fact).startswith("source_record")]
    direct_facts = [fact for fact in facts if not _predicate_name(fact).startswith("source_record")]
    direct_rows = _fact_rows(direct_facts)
    source_tokens = _tokens_for_facts(source_facts)
    direct_tokens = _tokens_for_facts(direct_facts)
    term_rows = [
        _audit_term(term, source_tokens=source_tokens, direct_tokens=direct_tokens, direct_rows=direct_rows)
        for term in terms
    ]
    return {
        "lens": lens,
        "compile_json": str(path),
        "run": path.parent.parent.name if path.parent.parent != path.parent else "",
        "fixture": path.parent.name,
        "parsed_ok": bool(data.get("parsed_ok")),
        "direct_fact_count": len(direct_facts),
        "source_record_fact_count": len(source_facts),
        "terms": term_rows,
        "summary": _summarize_terms(term_rows),
    }


def _audit_term(
    term: LensTerm,
    *,
    source_tokens: set[str],
    direct_tokens: set[str],
    direct_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    source_hits = [token for token in term.tokens if token in source_tokens]
    direct_hits = [token for token in term.tokens if token in direct_tokens]
    slot_rows = _slot_rows_for_term(term, direct_rows)
    shallow_rows = _shallow_rows_for_term(term, direct_rows)
    contract_rows = _contract_rows_for_term(term, direct_rows)
    partial_contract_rows = _partial_contract_rows_for_term(term, direct_rows)
    if contract_rows:
        slot_rows = [*slot_rows, *contract_rows]
    if partial_contract_rows:
        shallow_rows = [*shallow_rows, *partial_contract_rows]
    if slot_rows:
        status = "structural"
    elif direct_hits or shallow_rows:
        status = "shallow_structural"
    elif source_hits:
        status = "source_only"
    else:
        status = "not_applicable"
    return {
        "term": term.term,
        "status": status,
        "min_arity": term.min_arity,
        "source_hits": source_hits,
        "direct_hits": direct_hits,
        "slot_rows": slot_rows[:5],
        "shallow_rows": shallow_rows[:5],
    }


def _facts_from_compile(data: dict[str, Any]) -> list[str]:
    source_compile = data.get("source_compile") if isinstance(data.get("source_compile"), dict) else {}
    facts = source_compile.get("facts")
    if isinstance(facts, list):
        return [str(fact).strip() for fact in facts if str(fact).strip()]
    parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
    parsed_facts = parsed.get("facts")
    if isinstance(parsed_facts, list):
        return [str(fact).strip() for fact in parsed_facts if str(fact).strip()]
    return []


def _predicate_name(fact: str) -> str:
    match = FACT_RE.match(str(fact))
    return match.group(1) if match else ""


def _fact_rows(facts: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact in facts:
        match = FACT_RE.match(fact)
        if not match:
            continue
        rows.append({"predicate": match.group(1), "args": _split_fact_args(match.group(2)), "fact": fact})
    return rows


def _split_fact_args(raw_args: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    in_quote = False
    escape = False
    depth = 0
    for char in raw_args:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            current.append(char)
            escape = True
            continue
        if char == '"':
            current.append(char)
            in_quote = not in_quote
            continue
        if not in_quote and char == "(":
            depth += 1
        elif not in_quote and char == ")" and depth:
            depth -= 1
        if char == "," and not in_quote and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current or raw_args.strip():
        args.append("".join(current).strip())
    return args


def _slot_rows_for_term(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        predicate_tokens = set(TOKEN_RE.findall(predicate))
        arg_count = len(row["args"])
        if arg_count < term.min_arity:
            continue
        if _predicate_matches(term, predicate, predicate_tokens):
            out.append(str(row["fact"]))
    return out


def _shallow_rows_for_term(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        predicate_tokens = set(TOKEN_RE.findall(predicate))
        if len(row["args"]) >= term.min_arity:
            continue
        if _predicate_matches(term, predicate, predicate_tokens):
            out.append(str(row["fact"]))
    return out


def _contract_rows_for_term(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    if term.term == "noncontrolling_source":
        special = _noncontrolling_source_contract_rows(direct_rows)
        if special:
            return special
    if term.term in AUTHORITY_CUSTODY_TERM_NAMES:
        special = _authority_record_contract_rows(term, direct_rows)
        if special:
            return special
    if term.term in OPERATIONAL_RECORD_TERM_NAMES:
        special = _operational_record_contract_rows(term, direct_rows)
        if special:
            return special
    if term.term == "exception":
        special = _rule_exception_link_contract_rows(direct_rows)
        if special:
            return special
    if term.term == "override":
        special = _rule_override_link_contract_rows(direct_rows)
        if special:
            return special
    if not term.contract_groups:
        return []
    grouped = _matching_contract_rows(term, direct_rows)
    for group_rows in grouped.values():
        if all(any(group_index == index for group_index, _ in group_rows) for index in range(len(term.contract_groups))):
            return [fact for _, fact in group_rows]
    return []


def _partial_contract_rows_for_term(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    if term.term == "noncontrolling_source":
        special = _partial_noncontrolling_source_rows(direct_rows)
        if special:
            return special
    if term.term in AUTHORITY_CUSTODY_TERM_NAMES:
        special = _partial_authority_record_rows(term, direct_rows)
        if special:
            return special
    if term.term in OPERATIONAL_RECORD_TERM_NAMES:
        special = _partial_operational_record_rows(term, direct_rows)
        if special:
            return special
    if term.term == "exception":
        special = _partial_rule_exception_link_rows(direct_rows)
        if special:
            return special
    if term.term == "override":
        special = _partial_rule_override_link_rows(direct_rows)
        if special:
            return special
    if not term.contract_groups:
        return []
    grouped = _matching_contract_rows(term, direct_rows)
    out: list[str] = []
    for group_rows in grouped.values():
        covered = {group_index for group_index, _ in group_rows}
        if covered and len(covered) < len(term.contract_groups):
            out.extend(fact for _, fact in group_rows)
    return out


def _matching_contract_rows(term: LensTerm, direct_rows: list[dict[str, Any]]) -> dict[str, list[tuple[int, str]]]:
    grouped: dict[str, list[tuple[int, str]]] = {}
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if len(row["args"]) <= term.contract_anchor:
            continue
        for index, patterns in enumerate(term.contract_groups):
            if any(re.fullmatch(pattern, predicate) for pattern in patterns):
                anchor = str(row["args"][term.contract_anchor])
                grouped.setdefault(anchor, []).append((index, str(row["fact"])))
    return grouped


def _rule_exception_link_contract_rows(direct_rows: list[dict[str, Any]]) -> list[str]:
    links = _rule_exception_links(direct_rows)
    condition_rows = _rows_by_anchor(direct_rows, ("rule_condition", "exception_condition", "waiver_condition"))
    effect_rows = _rows_by_anchor(direct_rows, ("rule_action", "rule_outcome", "rule_consequence", "exception_effect", "waiver_effect"))
    for exception_id, link_fact in links.items():
        if condition_rows.get(exception_id) and effect_rows.get(exception_id):
            return [link_fact, condition_rows[exception_id][0], effect_rows[exception_id][0]]
    return []


def _partial_rule_exception_link_rows(direct_rows: list[dict[str, Any]]) -> list[str]:
    links = _rule_exception_links(direct_rows)
    if not links:
        return []
    condition_rows = _rows_by_anchor(direct_rows, ("rule_condition", "exception_condition", "waiver_condition"))
    effect_rows = _rows_by_anchor(direct_rows, ("rule_action", "rule_outcome", "rule_consequence", "exception_effect", "waiver_effect"))
    out: list[str] = []
    for exception_id, link_fact in links.items():
        rows = [link_fact, *condition_rows.get(exception_id, [])[:1], *effect_rows.get(exception_id, [])[:1]]
        if 1 <= len(rows) < 3:
            out.extend(rows)
    return out


def _rule_exception_links(direct_rows: list[dict[str, Any]]) -> dict[str, str]:
    links: dict[str, str] = {}
    for row in direct_rows:
        if str(row["predicate"]).lower() not in {"rule_exception", "exception_for"} or len(row["args"]) < 2:
            continue
        exception_arg = 1 if str(row["predicate"]).lower() == "rule_exception" else 0
        links[str(row["args"][exception_arg])] = str(row["fact"])
    return links


def _rule_override_link_contract_rows(direct_rows: list[dict[str, Any]]) -> list[str]:
    links = _rule_override_links(direct_rows)
    condition_rows = _rows_by_anchor(direct_rows, ("rule_condition", "override_condition", "trigger_condition"))
    effect_rows = _rows_by_anchor(direct_rows, ("rule_action", "rule_outcome", "rule_consequence", "override_effect"))
    for higher_rule, link_fact in links.items():
        if condition_rows.get(higher_rule) and effect_rows.get(higher_rule):
            return [link_fact, condition_rows[higher_rule][0], effect_rows[higher_rule][0]]
    return []


def _partial_rule_override_link_rows(direct_rows: list[dict[str, Any]]) -> list[str]:
    links = _rule_override_links(direct_rows)
    if not links:
        return []
    condition_rows = _rows_by_anchor(direct_rows, ("rule_condition", "override_condition", "trigger_condition"))
    effect_rows = _rows_by_anchor(direct_rows, ("rule_action", "rule_outcome", "rule_consequence", "override_effect"))
    out: list[str] = []
    for higher_rule, link_fact in links.items():
        rows = [link_fact, *condition_rows.get(higher_rule, [])[:1], *effect_rows.get(higher_rule, [])[:1]]
        if 1 <= len(rows) < 3:
            out.extend(rows)
    return out


def _rule_override_links(direct_rows: list[dict[str, Any]]) -> dict[str, str]:
    links: dict[str, str] = {}
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if predicate not in {"rule_precedence", "override_rule", "rule_override", "overrides"} or len(row["args"]) < 2:
            continue
        if len(row["args"]) >= 3:
            continue
        links[str(row["args"][0])] = str(row["fact"])
    return links


def _rows_by_anchor(direct_rows: list[dict[str, Any]], predicates: tuple[str, ...]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    predicate_set = set(predicates)
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if predicate not in predicate_set or not row["args"]:
            continue
        out.setdefault(str(row["args"][0]), []).append(str(row["fact"]))
    return out


NONCONTROLLING_TOKENS = {"noncontrolling", "non_controlling", "advisory", "copied", "superseded", "rejected"}
AUTHORITY_CUSTODY_TERM_NAMES = {term.term for term in AUTHORITY_CUSTODY_TERMS}
AUTHORITY_TYPE_TOKENS: dict[str, set[str]] = {
    "court_order": {"court_order", "order", "injunction", "judgment"},
    "governing_rule": {"governing_rule", "rule", "bylaw", "policy", "ordinance", "machine_rule"},
    "board_vote": {"board_vote", "vote", "committee_vote", "council_vote"},
    "official_record": {"official_record", "official_equipment_register", "official_tool_register", "official_register", "register", "registry", "chain_of_custody"},
    "staff_note": {"staff_note", "note", "memo"},
    "draft_recommendation": {"draft_recommendation", "draft", "proposal", "recommendation"},
    "controlling_finding": {"controlling_finding", "finding", "final_finding"},
}
AUTHORITY_SUPPORT_PREDICATES = {
    "access_condition",
    "access_denied",
    "access_granted",
    "access_granted_to",
    "authorization_denied",
    "conflict_resolved_by",
    "controls_action",
    "denies_access",
    "denies_authority",
    "document_content",
    "event_outcome",
    "grants_access",
    "permits_access",
    "prohibits_access",
    "record_provision",
    "restricts_access",
    "record_detail",
    "register_entry",
    "rule_condition",
    "rule_effect",
    "rule_governs",
    "rule_governs_action",
    "rule_consequence",
    "source_declares",
    "source_grants_no_authorization",
    "vote_result",
    "vote_outcome",
}
AUTHORITY_METADATA_PREDICATES = {
    "authority_level",
    "document_author",
    "document_date",
    "document_status",
    "document_type",
    "event_date",
    "event_occurred",
    "event_occurred_on",
    "event_type",
    "epistemic_status",
    "is_controlling",
    "record_status",
    "record_type",
    "record_entry",
    "source_author",
    "source_date",
    "source_document",
    "source_epistemic_label",
}


def _noncontrolling_source_contract_rows(direct_rows: list[dict[str, Any]]) -> list[str]:
    reason_rows = _rows_by_anchor(
        direct_rows,
        (
            "noncontrolling_reason",
            "non_controlling_reason",
            "source_reason",
            "authority_reason",
            "status_reason",
        ),
    )
    record_detail_reasons = _record_detail_rows_by_field(
        direct_rows,
        {"reason_noncontrolling", "reason_non_controlling", "source_of", "source_of_copy"},
    )
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if predicate in {"noncontrolling_source", "non_controlling_source", "advisory_source", "superseded_source", "rejected_source"}:
            if len(row["args"]) >= 3:
                return [str(row["fact"])]
            if row["args"] and reason_rows.get(str(row["args"][0])):
                return [str(row["fact"]), reason_rows[str(row["args"][0])][0]]
        if predicate == "is_noncontrolling" and row["args"]:
            anchor = str(row["args"][0])
            if record_detail_reasons.get(anchor):
                return [str(row["fact"]), record_detail_reasons[anchor][0]]
            continue
        if predicate not in {"source_status", "authority_status", "source_authority_status", "record_status", "document_status", "epistemic_status"}:
            continue
        if not _row_mentions_noncontrolling_status(row):
            continue
        if len(row["args"]) >= 3:
            return [str(row["fact"])]
        if row["args"] and reason_rows.get(str(row["args"][0])):
            return [str(row["fact"]), reason_rows[str(row["args"][0])][0]]
        if row["args"] and record_detail_reasons.get(str(row["args"][0])):
            return [str(row["fact"]), record_detail_reasons[str(row["args"][0])][0]]
    return []


def _partial_noncontrolling_source_rows(direct_rows: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if predicate in {"noncontrolling_source", "non_controlling_source", "advisory_source", "superseded_source", "rejected_source"} and len(row["args"]) < 3:
            out.append(str(row["fact"]))
        elif predicate == "is_noncontrolling" and row["args"]:
            out.append(str(row["fact"]))
        elif predicate in {"source_status", "authority_status", "source_authority_status", "record_status", "document_status", "epistemic_status"} and _row_mentions_noncontrolling_status(row) and len(row["args"]) < 3:
            out.append(str(row["fact"]))
    return out


def _row_mentions_noncontrolling_status(row: dict[str, Any]) -> bool:
    tokens = set(TOKEN_RE.findall(" ".join(str(arg).lower() for arg in row.get("args", []))))
    return bool(tokens & NONCONTROLLING_TOKENS)


def _authority_record_contract_rows(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    if term.term not in AUTHORITY_TYPE_TOKENS:
        return []
    for anchor, typed_row in _authority_typed_records(term, direct_rows):
        support_rows = _authority_support_rows(anchor, direct_rows)
        if not support_rows:
            continue
        if term.term == "court_order" and not _anchor_has_court_status(anchor, typed_row, direct_rows):
            continue
        return [typed_row, *support_rows[:3]]
    return []


def _partial_authority_record_rows(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    if term.term not in AUTHORITY_TYPE_TOKENS:
        return []
    out: list[str] = []
    for anchor, typed_row in _authority_typed_records(term, direct_rows):
        support_rows = _authority_support_rows(anchor, direct_rows)
        if support_rows:
            continue
        out.append(typed_row)
    return out


def _authority_typed_records(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    target_tokens = AUTHORITY_TYPE_TOKENS.get(term.term, set())
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        args = [str(arg).lower() for arg in row["args"]]
        if predicate == "document_type" and len(args) >= 2 and _value_has_any_token(args[1], target_tokens):
            out.append((str(row["args"][0]), str(row["fact"])))
        elif predicate == "record_entry" and len(args) >= 2 and _value_has_any_token(args[1], target_tokens):
            out.append((str(row["args"][0]), str(row["fact"])))
        elif predicate in {"record_type", "source_document", "event_type"} and len(args) >= 2 and _value_has_any_token(args[1], target_tokens):
            out.append((str(row["args"][0]), str(row["fact"])))
        elif term.term == "draft_recommendation" and predicate in {"source_document", "document_type", "record_type"} and len(args) >= 2 and _value_has_any_token(args[1], {"recommendation"}) and _anchor_has_label(str(row["args"][0]), {"draft"}, direct_rows):
            out.append((str(row["args"][0]), str(row["fact"])))
        elif term.term == "controlling_finding" and predicate == "controlling_finding" and row["args"]:
            out.append((str(row["args"][0]), str(row["fact"])))
        elif term.term == "noncontrolling_source" and predicate in {"non_controlling_record", "noncontrolling_record", "noncontrolling_source", "non_controlling_source"} and row["args"]:
            out.append((str(row["args"][0]), str(row["fact"])))
    return out


def _authority_support_rows(anchor: str, direct_rows: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if predicate in AUTHORITY_METADATA_PREDICATES:
            continue
        if predicate not in AUTHORITY_SUPPORT_PREDICATES:
            continue
        if row["args"] and str(row["args"][0]) == anchor:
            out.append(str(row["fact"]))
    return out


def _anchor_has_court_status(anchor: str, typed_row: str, direct_rows: list[dict[str, Any]]) -> bool:
    if "court" in typed_row.lower():
        return True
    for row in direct_rows:
        if not row["args"] or str(row["args"][0]) != anchor:
            continue
        if "court" in " ".join(str(arg).lower() for arg in row["args"]):
            return True
    return False


def _anchor_has_label(anchor: str, labels: set[str], direct_rows: list[dict[str, Any]]) -> bool:
    for row in direct_rows:
        if not row["args"] or str(row["args"][0]) != anchor:
            continue
        if _row_has_any_token(row, labels):
            return True
    return False


def _record_detail_rows_by_field(direct_rows: list[dict[str, Any]], fields: set[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in direct_rows:
        if str(row["predicate"]).lower() != "record_detail" or len(row["args"]) < 2:
            continue
        if str(row["args"][1]).lower() in fields:
            out.setdefault(str(row["args"][0]), []).append(str(row["fact"]))
    return out


def _value_has_any_token(value: str, tokens: set[str]) -> bool:
    normalized = str(value).lower()
    value_tokens = set(TOKEN_RE.findall(normalized))
    return normalized in tokens or bool(value_tokens & tokens)


OPERATIONAL_RECORD_TERM_NAMES = {term.term for term in OPERATIONAL_RECORD_STATUS_TERMS}
OPERATIONAL_RECORD_PREDICATES = {"record_entry", "event_record", "docket_entry", "log_entry", "case_entry"}
OPERATIONAL_DETAIL_PREDICATES = {"record_detail", "event_detail", "status_detail", "docket_detail", "log_detail"}
OPERATIONAL_STATUS_PREDICATES = {
    "status",
    "record_status",
    "current_status",
    "final_status",
    "status_at",
    "event_status",
    "decision_status",
    "application_status",
    "item_status",
}


def _operational_record_contract_rows(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    detail_rows = _operational_detail_rows_for_term(term, direct_rows)
    if detail_rows:
        return detail_rows[:3]
    status_rows = _operational_status_rows_for_term(term, direct_rows)
    if status_rows:
        return status_rows[:3]
    return []


def _partial_operational_record_rows(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    record_anchors = _operational_record_anchors(direct_rows)
    term_tokens = set(term.tokens)
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if predicate not in OPERATIONAL_RECORD_PREDICATES or not row["args"]:
            continue
        if not _row_has_any_token(row, term_tokens):
            continue
        anchor = str(row["args"][0])
        if anchor in record_anchors:
            out.append(str(row["fact"]))
    return out


def _operational_detail_rows_for_term(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    record_anchors = _operational_record_anchors(direct_rows)
    term_tokens = set(term.tokens)
    out: list[str] = []
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if predicate not in OPERATIONAL_DETAIL_PREDICATES or len(row["args"]) < 3:
            continue
        anchor = str(row["args"][0])
        if anchor not in record_anchors:
            continue
        if _row_has_any_token(row, term_tokens):
            out.append(str(row["fact"]))
    return out


def _operational_status_rows_for_term(term: LensTerm, direct_rows: list[dict[str, Any]]) -> list[str]:
    term_tokens = set(term.tokens)
    out: list[str] = []
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if predicate not in OPERATIONAL_STATUS_PREDICATES:
            continue
        if len(row["args"]) < term.min_arity:
            continue
        if _row_has_any_token(row, term_tokens):
            out.append(str(row["fact"]))
    return out


def _operational_record_anchors(direct_rows: list[dict[str, Any]]) -> set[str]:
    anchors: set[str] = set()
    for row in direct_rows:
        if str(row["predicate"]).lower() in OPERATIONAL_RECORD_PREDICATES and row["args"]:
            anchors.add(str(row["args"][0]))
    return anchors


def _row_has_any_token(row: dict[str, Any], tokens: set[str]) -> bool:
    row_tokens = set(TOKEN_RE.findall(str(row.get("fact", "")).lower()))
    return bool(row_tokens & tokens)


def _predicate_matches(term: LensTerm, predicate: str, predicate_tokens: set[str]) -> bool:
    if any(re.fullmatch(pattern, predicate) for pattern in term.predicate_patterns):
        return True
    return any(token in predicate_tokens for token in term.tokens)


def _tokens_for_facts(facts: list[str]) -> set[str]:
    return set(TOKEN_RE.findall(" ".join(facts).lower()))


def _summarize_terms(term_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in term_rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def summarize_reports(reports: list[dict[str, Any]], terms: tuple[LensTerm, ...]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_term: dict[str, dict[str, int]] = {term.term: {} for term in terms}
    for report in reports:
        for row in report["terms"]:
            status = str(row["status"])
            by_status[status] = by_status.get(status, 0) + 1
            bucket = by_term.setdefault(str(row["term"]), {})
            bucket[status] = bucket.get(status, 0) + 1
    return {
        "status_counts": dict(sorted(by_status.items())),
        "term_status_counts": {key: dict(sorted(value.items())) for key, value in sorted(by_term.items())},
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Lens Vocabulary Transfer Audit",
        "",
        f"- Schema: `{payload['schema']}`",
        f"- Lens: `{payload['lens']}`",
        f"- Compiles: `{payload['compile_count']}`",
        f"- Status counts: `{payload['summary']['status_counts']}`",
        "",
        "## Term Summary",
        "",
        "| Term | Structural | Shallow | Source-only | N/A |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for term, counts in payload["summary"]["term_status_counts"].items():
        lines.append(
            f"| `{term}` | {counts.get('structural', 0)} | {counts.get('shallow_structural', 0)} | {counts.get('source_only', 0)} | {counts.get('not_applicable', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Fixture Summary",
            "",
            "| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for report in payload["reports"]:
        summary = report["summary"]
        lines.append(
            "| {run} | {fixture} | {direct} | {source} | {structural} | {shallow} | {source_only} | {na} |".format(
                run=f"`{report['run']}`",
                fixture=f"`{report['fixture']}`",
                direct=report["direct_fact_count"],
                source=report["source_record_fact_count"],
                structural=summary.get("structural", 0),
                shallow=summary.get("shallow_structural", 0),
                source_only=summary.get("source_only", 0),
                na=summary.get("not_applicable", 0),
            )
        )
    lines.extend(["", "## Shallow Or Source-Only Terms", ""])
    for report in payload["reports"]:
        shallow = [row["term"] for row in report["terms"] if row["status"] == "shallow_structural"]
        source_only = [row["term"] for row in report["terms"] if row["status"] == "source_only"]
        if shallow:
            lines.append(f"- `{report['fixture']}` shallow: {', '.join(f'`{term}`' for term in shallow)}")
        if source_only:
            lines.append(f"- `{report['fixture']}` source-only: {', '.join(f'`{term}`' for term in source_only)}")
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
