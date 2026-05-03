#!/usr/bin/env python3
"""Audit admitted Prolog surfaces for right-shaped/wrong-meaning risks.

This script is intentionally structural. It reads already-produced Prolog
clauses or JSON compile artifacts and inspects clause shapes, predicate names,
variable binding, and helper usage. It does not read raw source prose to infer
meaning, and it does not authorize or mutate KB state.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

CLAUSE_KEYS = {
    "clause",
    "fact",
    "rule",
    "query",
    "prolog_clause",
    "asserted_clause",
    "admitted_clause",
}

BROAD_UNARY_PREDICATES = {
    "actor",
    "authority",
    "cargo",
    "character",
    "claimant",
    "committee",
    "document",
    "entity",
    "food",
    "group",
    "institution",
    "object",
    "organization",
    "person",
    "place",
    "proposal",
    "role",
    "source",
    "vessel",
}

CLAIM_SOURCE_PREDICATES = {
    "advisory_opinion",
    "allegation",
    "claim",
    "claim_made",
    "disclosure",
    "reported_event",
    "said",
    "source_claim",
    "statement_detail",
    "witness_claim",
    "witness_statement",
}

ADOPTION_OR_AUTHORITY_PREDICATES = {
    "adopted_as_finding",
    "authorized_action",
    "certified_log",
    "confirmed_by",
    "finding",
    "formal_interpretation",
    "governing_bylaw",
    "official_record",
    "review_finding",
}

ASSERTIVE_HEAD_PREDICATES = {
    "approved",
    "eligible",
    "finding",
    "violation",
    "derived_authorization",
    "derived_clearance_status",
    "derived_condition",
    "derived_obligation",
    "derived_permission",
    "derived_reward_status",
    "derived_status",
    "derived_tax_status",
}

ENTITY_FIRST_HELPERS = {"value_greater_than", "value_at_most"}
NUMBER_HELPERS = {"number_greater_than", "number_at_most"}
PERCENT_HELPERS = {"percent_at_least", "percent_below"}
AGGREGATION_HELPERS = {"support_count_at_least"}
TEMPORAL_HELPERS = {"hours_at_least", "elapsed_hours", "elapsed_days", "within_hours"}
HELPER_PREDICATES = ENTITY_FIRST_HELPERS | NUMBER_HELPERS | PERCENT_HELPERS | AGGREGATION_HELPERS | TEMPORAL_HELPERS


@dataclass(frozen=True)
class Goal:
    predicate: str
    args: tuple[str, ...]
    text: str

    @property
    def signature(self) -> str:
        return f"{self.predicate}/{len(self.args)}"


@dataclass(frozen=True)
class ParsedClause:
    clause: str
    head: Goal | None
    body: tuple[Goal, ...]
    fragments: tuple[str, ...]
    body_text: str = ""

    @property
    def is_rule(self) -> bool:
        return ":-" in self.clause


@dataclass(frozen=True)
class ShortcutFinding:
    risk: str
    severity: str
    clause: str
    detail: str


def main() -> int:
    args = parse_args()
    paths = resolve_paths(args.artifact, args.artifact_glob)
    if not paths:
        print("No artifacts matched.", file=sys.stderr)
        return 2

    all_clauses: list[str] = []
    per_file_counts: dict[str, int] = {}
    for path in paths:
        clauses = load_clauses(path)
        per_file_counts[str(path)] = len(clauses)
        all_clauses.extend(clauses)

    findings = audit_clauses(all_clauses)
    summary = summarize(findings, clause_count=len(all_clauses), per_file_counts=per_file_counts)
    output = {
        "summary": summary,
        "findings": [asdict(item) for item in findings],
    }
    if args.out_json:
        out_path = args.out_json if args.out_json.is_absolute() else (REPO_ROOT / args.out_json).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote {out_path}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if args.fail_on_findings and findings else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, action="append", default=[], help="JSON or .pl artifact to audit.")
    parser.add_argument("--artifact-glob", default="", help="Optional glob relative to repo root.")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--fail-on-findings", action="store_true")
    return parser.parse_args()


def resolve_paths(paths: list[Path], artifact_glob: str) -> list[Path]:
    resolved: list[Path] = []
    for path in paths:
        full = path if path.is_absolute() else (REPO_ROOT / path).resolve()
        if full.exists():
            resolved.append(full)
    if artifact_glob:
        resolved.extend(sorted(REPO_ROOT.glob(artifact_glob)))
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in resolved:
        if path.is_file() and path not in seen:
            seen.add(path)
            deduped.append(path)
    return deduped


def load_clauses(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        try:
            return collect_json_clauses(json.loads(text))
        except json.JSONDecodeError:
            return []
    return extract_prolog_clauses(text)


def collect_json_clauses(value: Any, parent_key: str = "") -> list[str]:
    clauses: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if isinstance(child, str) and key_text in CLAUSE_KEYS and looks_like_clause(child):
                clauses.append(normalize_clause(child))
            else:
                clauses.extend(collect_json_clauses(child, key_text))
    elif isinstance(value, list):
        for child in value:
            if isinstance(child, str) and parent_key in {"facts", "rules", "clauses", "admitted_clauses"} and looks_like_clause(child):
                clauses.append(normalize_clause(child))
            else:
                clauses.extend(collect_json_clauses(child, parent_key))
    return dedupe_preserve_order(clauses)


def extract_prolog_clauses(text: str) -> list[str]:
    clauses: list[str] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.split("%", 1)[0].strip()
        if not line or line.startswith(":-"):
            continue
        current.append(line)
        joined = " ".join(current).strip()
        if joined.endswith("."):
            if looks_like_clause(joined):
                clauses.append(normalize_clause(joined))
            current = []
    return dedupe_preserve_order(clauses)


def looks_like_clause(text: str) -> bool:
    clean = str(text or "").strip()
    if not clean:
        return False
    clean = normalize_clause(clean)
    return bool(re.match(r"^[a-z_][a-z0-9_]*\s*\(", clean))


def normalize_clause(text: str) -> str:
    clean = re.sub(r"\s+", " ", str(text or "").strip())
    if clean and not clean.endswith("."):
        clean += "."
    return clean


def dedupe_preserve_order(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def audit_clauses(clauses: list[str]) -> list[ShortcutFinding]:
    parsed = [parse_clause(clause) for clause in dedupe_preserve_order([normalize_clause(c) for c in clauses if looks_like_clause(c)])]
    findings: list[ShortcutFinding] = []
    for item in parsed:
        findings.extend(audit_clause(item))
    findings.extend(audit_sibling_heads(parsed))
    return findings


def audit_clause(item: ParsedClause) -> list[ShortcutFinding]:
    findings: list[ShortcutFinding] = []
    if not item.head:
        return findings
    if not item.is_rule:
        return findings

    head_vars = variables_in_text(item.head.text)
    body_vars = variables_in_text(item.body_text)
    unbound = sorted(var for var in head_vars if var not in body_vars)
    if unbound:
        findings.append(
            ShortcutFinding(
                risk="unbound_head_variable",
                severity="high",
                clause=item.clause,
                detail=f"Head variables are absent from the body: {', '.join(unbound)}.",
            )
        )

    if any(
        fragment in {";", "!", "\\+"}
        or "\\+" in fragment
        or fragment.startswith("not(")
        or " is " in f" {fragment} "
        or re.search(r"(>=|=<|>|<)", fragment)
        for fragment in item.fragments
    ):
        findings.append(
            ShortcutFinding(
                risk="unsupported_control_construct",
                severity="medium",
                clause=item.clause,
                detail="Body contains control, negation, or non-Horn fragments that require explicit helper substrate.",
            )
        )

    findings.extend(audit_helper_usage(item))
    findings.extend(audit_class_fanout(item))
    findings.extend(audit_claim_fact_collapse(item))
    findings.extend(audit_aggregation_overclaim(item))
    return findings


def audit_helper_usage(item: ParsedClause) -> list[ShortcutFinding]:
    findings: list[ShortcutFinding] = []
    for goal in item.body:
        if goal.predicate in ENTITY_FIRST_HELPERS and len(goal.args) == 2:
            entity, threshold = goal.args
            if is_numeric_literal(entity):
                findings.append(
                    ShortcutFinding(
                        risk="helper_argument_misuse",
                        severity="high",
                        clause=item.clause,
                        detail=f"{goal.text} uses a numeric literal where an entity argument is required.",
                    )
                )
            if not is_literal_threshold(threshold):
                findings.append(
                    ShortcutFinding(
                        risk="helper_threshold_not_literal",
                        severity="medium",
                        clause=item.clause,
                        detail=f"{goal.text} uses a non-literal threshold.",
                    )
                )
        if goal.predicate in NUMBER_HELPERS and len(goal.args) == 2:
            value, threshold = goal.args
            earlier = body_vars_before(item, goal)
            if not is_variable(value) or value not in earlier:
                findings.append(
                    ShortcutFinding(
                        risk="helper_argument_misuse",
                        severity="high",
                        clause=item.clause,
                        detail=f"{goal.text} uses a numeric variable before it is bound by a prior body goal.",
                    )
                )
            if not is_literal_threshold(threshold):
                findings.append(
                    ShortcutFinding(
                        risk="helper_threshold_not_literal",
                        severity="medium",
                        clause=item.clause,
                        detail=f"{goal.text} uses a non-literal threshold.",
                    )
                )
        if goal.predicate in PERCENT_HELPERS and len(goal.args) == 3:
            part, whole, threshold = goal.args
            earlier = body_vars_before(item, goal)
            if not is_variable(part) or not is_variable(whole) or part not in earlier or whole not in earlier:
                findings.append(
                    ShortcutFinding(
                        risk="helper_argument_misuse",
                        severity="high",
                        clause=item.clause,
                        detail=f"{goal.text} uses percent inputs before prior body goals bind both numeric variables.",
                    )
                )
            if not is_literal_threshold(threshold):
                findings.append(
                    ShortcutFinding(
                        risk="helper_threshold_not_literal",
                        severity="medium",
                        clause=item.clause,
                        detail=f"{goal.text} uses a non-literal percentage threshold.",
                    )
                )
    return findings


def audit_class_fanout(item: ParsedClause) -> list[ShortcutFinding]:
    if not item.head or not item.head.predicate.startswith("derived_"):
        return []
    head_vars = variables_in_text(item.head.text)
    if not head_vars:
        return []
    relational_binders = [
        goal
        for goal in item.body
        if len(goal.args) >= 2
        and (goal.predicate not in HELPER_PREDICATES or goal.predicate in ENTITY_FIRST_HELPERS or goal.predicate in AGGREGATION_HELPERS)
        and variables_in_text(goal.text).intersection(head_vars)
    ]
    if not relational_binders:
        return [
            ShortcutFinding(
                risk="broad_class_fanout_risk",
                severity="medium",
                clause=item.clause,
                detail="Derived head variables are not anchored by a relation-bearing body goal.",
            )
        ]
    return []


def audit_claim_fact_collapse(item: ParsedClause) -> list[ShortcutFinding]:
    if not item.head:
        return []
    body_preds = {goal.predicate for goal in item.body}
    if item.head.predicate not in ASSERTIVE_HEAD_PREDICATES:
        return []
    if not body_preds.intersection(CLAIM_SOURCE_PREDICATES):
        return []
    if body_preds.intersection(ADOPTION_OR_AUTHORITY_PREDICATES):
        return []
    return [
        ShortcutFinding(
            risk="claim_to_fact_shortcut_risk",
            severity="high",
            clause=item.clause,
            detail="Assertive derived head depends on claim/source predicates without an adoption or authority predicate.",
        )
    ]


def audit_aggregation_overclaim(item: ParsedClause) -> list[ShortcutFinding]:
    if not item.head:
        return []
    body_preds = {goal.predicate for goal in item.body}
    if "support_count_at_least" not in body_preds:
        return []
    head_text = item.head.text.lower()
    final_words = {"approved", "passed", "valid", "eligible", "adopted", "authorized"}
    if not any(word in head_text for word in final_words):
        return []
    if any("veto" in goal.text.lower() or "override" in goal.text.lower() or "exception" in goal.text.lower() for goal in item.body):
        return []
    return [
        ShortcutFinding(
            risk="aggregation_final_outcome_overclaim",
            severity="medium",
            clause=item.clause,
            detail="Vote/support threshold is used to derive a final outcome without an explicit veto/override/exception check.",
        )
    ]


def audit_sibling_heads(parsed: list[ParsedClause]) -> list[ShortcutFinding]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for item in parsed:
        if not item.head or not item.is_rule or not item.head.predicate.startswith("derived_"):
            continue
        key = f"{item.head.predicate}/{len(item.head.args)}:{','.join(arg if not is_variable(arg) else '_' for arg in item.head.args)}"
        buckets[key].append(item.clause)
    findings: list[ShortcutFinding] = []
    for key, clauses in buckets.items():
        if len(clauses) <= 1:
            continue
        for clause in clauses:
            findings.append(
                ShortcutFinding(
                    risk="sibling_rule_masking_risk",
                    severity="low",
                    clause=clause,
                    detail=f"{len(clauses)} sibling rules share derived head shape {key}; require isolated trial before crediting firing.",
                )
            )
    return findings


def parse_clause(clause: str) -> ParsedClause:
    clean = normalize_clause(clause).rstrip(".").strip()
    if ":-" in clean:
        head_text, body_text = clean.split(":-", 1)
        body_text = body_text.strip()
        body_parts = split_top_level(body_text, ",")
    else:
        head_text, body_parts = clean, []
    head = parse_goal(head_text.strip())
    body = tuple(goal for part in body_parts if (goal := parse_goal(part.strip())))
    remainder = body_text if ":-" in clean else ""
    for goal in body:
        remainder = remainder.replace(goal.text, " ", 1)
    fragments = tuple(fragment.strip() for fragment in re.split(r"\s*,\s*", remainder) if fragment.strip())
    return ParsedClause(clause=normalize_clause(clause), head=head, body=body, fragments=fragments, body_text=body_text if ":-" in clean else "")


def parse_goal(text: str) -> Goal | None:
    clean = str(text or "").strip().rstrip(".")
    match = re.match(r"^([a-z_][a-z0-9_]*)\s*\((.*)\)$", clean)
    if not match:
        return None
    predicate = match.group(1)
    args = tuple(part.strip() for part in split_top_level(match.group(2), ","))
    return Goal(predicate=predicate, args=args, text=f"{predicate}({', '.join(args)})")


def split_top_level(text: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    bracket_depth = 0
    for ch in str(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == "[":
            bracket_depth += 1
        elif ch == "]":
            bracket_depth = max(0, bracket_depth - 1)
        if ch == delimiter and depth == 0 and bracket_depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(ch)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def body_vars_before(item: ParsedClause, target_goal: Goal) -> set[str]:
    variables: set[str] = set()
    for goal in item.body:
        if goal == target_goal:
            return variables
        variables.update(variables_in_text(goal.text))
    return variables


def variables_in_text(text: str) -> set[str]:
    return set(re.findall(r"\b[A-Z_][A-Za-z0-9_]*\b", str(text or "")))


def is_variable(value: str) -> bool:
    return bool(re.match(r"^[A-Z_][A-Za-z0-9_]*$", str(value or "").strip()))


def is_numeric_literal(value: str) -> bool:
    return bool(re.match(r"^-?\d+(?:\.\d+)?$", str(value or "").strip()))


def is_literal_threshold(value: str) -> bool:
    text = str(value or "").strip()
    return is_numeric_literal(text) or bool(re.match(r"^[a-z][a-z0-9_]*$", text))


def summarize(findings: list[ShortcutFinding], *, clause_count: int, per_file_counts: dict[str, int]) -> dict[str, Any]:
    by_risk = Counter(item.risk for item in findings)
    by_severity = Counter(item.severity for item in findings)
    return {
        "audited_clause_count": clause_count,
        "finding_count": len(findings),
        "risk_counts": dict(sorted(by_risk.items())),
        "severity_counts": dict(sorted(by_severity.items())),
        "per_file_clause_counts": per_file_counts,
    }


if __name__ == "__main__":
    raise SystemExit(main())
