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
        (("rule_condition",), ("rule_action", "rule_outcome")),
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
        (".*_threshold", "threshold", "rule_threshold", "limit_rule", "cap_rule"),
        (("threshold_measure", "threshold_subject"), ("threshold_value", "threshold_amount", "threshold_limit")),
    ),
    LensTerm(
        "activation_condition",
        ("activates", "activation", "triggered", "when"),
        3,
        ("activation_condition", "trigger_condition", "applies_when", "rule_activation"),
        (("rule_condition", "trigger_condition", "applies_when"), ("rule_action", "rule_outcome")),
    ),
    LensTerm(
        "eligibility_condition",
        ("eligible", "eligibility", "qualifies", "qualify", "required"),
        3,
        ("eligibility_condition", "qualifies_when", "required_condition", "requirement_condition"),
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
        ("vote_requirement", "required_vote", "approval_vote", "quorum_requirement"),
    ),
    LensTerm(
        "fallback_rule",
        ("fallback", "otherwise", "default"),
        2,
        ("fallback_rule", "otherwise_rule", "default_rule", "fallback_to"),
    ),
)

LENS_TERMS: dict[str, tuple[LensTerm, ...]] = {
    "evidence_provenance": EVIDENCE_PROVENANCE_TERMS,
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
    if term.term == "exception":
        special = _rule_exception_link_contract_rows(direct_rows)
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
    if term.term == "exception":
        special = _partial_rule_exception_link_rows(direct_rows)
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
    effect_rows = _rows_by_anchor(direct_rows, ("rule_action", "rule_outcome", "exception_effect", "waiver_effect"))
    for exception_id, link_fact in links.items():
        if condition_rows.get(exception_id) and effect_rows.get(exception_id):
            return [link_fact, condition_rows[exception_id][0], effect_rows[exception_id][0]]
    return []


def _partial_rule_exception_link_rows(direct_rows: list[dict[str, Any]]) -> list[str]:
    links = _rule_exception_links(direct_rows)
    if not links:
        return []
    condition_rows = _rows_by_anchor(direct_rows, ("rule_condition", "exception_condition", "waiver_condition"))
    effect_rows = _rows_by_anchor(direct_rows, ("rule_action", "rule_outcome", "exception_effect", "waiver_effect"))
    out: list[str] = []
    for exception_id, link_fact in links.items():
        rows = [link_fact, *condition_rows.get(exception_id, [])[:1], *effect_rows.get(exception_id, [])[:1]]
        if 1 <= len(rows) < 3:
            out.extend(rows)
    return out


def _rule_exception_links(direct_rows: list[dict[str, Any]]) -> dict[str, str]:
    links: dict[str, str] = {}
    for row in direct_rows:
        if str(row["predicate"]).lower() != "rule_exception" or len(row["args"]) < 2:
            continue
        links[str(row["args"][1])] = str(row["fact"])
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
