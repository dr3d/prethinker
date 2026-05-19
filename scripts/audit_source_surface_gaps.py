#!/usr/bin/env python3
"""Audit whether direct-surface QA misses have answer evidence in source surfaces.

This is a diagnostic tool, not a repair. It reads QA scorecard artifacts and
their compile JSONs, then checks whether reference-answer tokens are present in
deterministic ``source_record_*`` rows and/or direct admitted predicates.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
WORD_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "about",
    "according",
    "all",
    "an",
    "and",
    "answer",
    "are",
    "as",
    "associated",
    "at",
    "be",
    "by",
    "did",
    "does",
    "during",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "if",
    "in",
    "is",
    "it",
    "its",
    "list",
    "model",
    "number",
    "of",
    "on",
    "or",
    "per",
    "same",
    "section",
    "status",
    "that",
    "the",
    "this",
    "to",
    "under",
    "was",
    "were",
    "what",
    "when",
    "which",
    "who",
    "with",
    "would",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorecard-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument(
        "--surface",
        action="append",
        default=[],
        help="Optional failure surface filter. Repeatable.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scorecard_path = _resolve(args.scorecard_json)
    report = audit_scorecard(
        json.loads(scorecard_path.read_text(encoding="utf-8-sig")),
        scorecard_path=scorecard_path,
        surfaces=set(args.surface or []),
    )
    out_json = _resolve(args.out_json) if args.out_json else scorecard_path.with_name("source_surface_gap_audit.json")
    out_md = _resolve(args.out_md) if args.out_md else scorecard_path.with_name("source_surface_gap_audit.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def audit_scorecard(
    scorecard: dict[str, Any],
    *,
    scorecard_path: Path | None = None,
    surfaces: set[str] | None = None,
) -> dict[str, Any]:
    surfaces = surfaces or set()
    rows: list[dict[str, Any]] = []
    fixture_rows = _scorecard_fixture_rows(scorecard)
    for artifact in fixture_rows:
        if not isinstance(artifact, dict):
            continue
        fixture = str(artifact.get("label") or artifact.get("fixture") or "")
        qa_path = _path_from_artifact(artifact.get("path"))
        run_path = _path_from_artifact(artifact.get("run_json"))
        if not qa_path or not qa_path.exists() or not run_path or not run_path.exists():
            continue
        qa = json.loads(qa_path.read_text(encoding="utf-8-sig"))
        qa_rows = {str(row.get("id", "")): row for row in qa.get("rows", []) if isinstance(row, dict)}
        compile_payload = json.loads(run_path.read_text(encoding="utf-8-sig"))
        compile_index = _compile_index(compile_payload)
        for row in artifact.get("non_exact_rows", []) if isinstance(artifact.get("non_exact_rows"), list) else []:
            if not isinstance(row, dict):
                continue
            surface = str(row.get("failure_surface", "") or "")
            if surfaces and surface not in surfaces:
                continue
            qa_row = qa_rows.get(str(row.get("id", "")), {})
            rows.append(
                _audit_row(
                    fixture=fixture,
                    scorecard_row=row,
                    qa_row=qa_row,
                    compile_index=compile_index,
                )
            )

    evidence_counts = Counter(str(row.get("evidence_class", "")) for row in rows)
    coordinate_counts = Counter(str(row.get("coordinate_class", "")) for row in rows)
    coordinate_detail_counts = Counter(
        str(row.get("coordinate_detail_class", ""))
        for row in rows
        if str(row.get("coordinate_detail_class", ""))
    )
    surface_counts = Counter(str(row.get("failure_surface", "")) for row in rows)
    return {
        "schema_version": "source_surface_gap_audit_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Diagnostic only: may inspect reference answers to classify misses, but does not change architecture.",
            "Treats source_record_* rows as source-addressability evidence, not semantic truth.",
            "Use results to choose generic compile-surface or query-planning repairs; do not promote fixture terms.",
        ],
        "artifacts": {"scorecard_json": _display_path(scorecard_path)},
        "summary": {
            "row_count": len(rows),
            "failure_surface_counts": dict(sorted(surface_counts.items())),
            "evidence_class_counts": dict(sorted(evidence_counts.items())),
            "coordinate_class_counts": dict(sorted(coordinate_counts.items())),
            "coordinate_detail_class_counts": dict(sorted(coordinate_detail_counts.items())),
            "answer_in_source_record_rows": sum(
                1 for row in rows if row["answer_evidence"]["source_record_strong_match_count"]
            ),
            "answer_in_direct_rows": sum(1 for row in rows if row["answer_evidence"]["direct_strong_match_count"]),
            "question_terms_in_source_record_rows": sum(
                1 for row in rows if row["question_evidence"]["source_record_match_count"]
            ),
        },
        "rows": rows,
    }


def _audit_row(
    *,
    fixture: str,
    scorecard_row: dict[str, Any],
    qa_row: dict[str, Any],
    compile_index: dict[str, Any],
) -> dict[str, Any]:
    question = str(scorecard_row.get("question") or qa_row.get("utterance") or "")
    answer = str(qa_row.get("reference_answer") or "")
    answer_tokens = _salient_tokens(answer)
    question_tokens = _salient_tokens(question)
    answer_evidence = _evidence(tokens=answer_tokens, compile_index=compile_index)
    question_evidence = _evidence(tokens=question_tokens, compile_index=compile_index, min_overlap=2)
    direct_predicates = sorted({predicate for query in scorecard_row.get("queries", []) for predicate in _query_predicates(query)})
    evidence_class = _evidence_class(answer_evidence=answer_evidence, question_evidence=question_evidence)
    coordinate_class = _coordinate_class(
        question=question,
        reference_answer=answer,
        predicate_hints=direct_predicates,
        answer_tokens=answer_tokens,
        question_tokens=question_tokens,
    )
    coordinate_detail_class = _coordinate_detail_class(
        coordinate_class=coordinate_class,
        question=question,
        reference_answer=answer,
        predicate_hints=direct_predicates,
        answer_tokens=answer_tokens,
        question_tokens=question_tokens,
    )
    return {
        "fixture": fixture,
        "id": str(scorecard_row.get("id", "")),
        "verdict": str(scorecard_row.get("verdict", "")),
        "failure_surface": str(scorecard_row.get("failure_surface", "")),
        "question": question,
        "reference_answer": answer,
        "predicate_hints": direct_predicates,
        "evidence_class": evidence_class,
        "coordinate_class": coordinate_class,
        "coordinate_detail_class": coordinate_detail_class,
        "answer_tokens": sorted(answer_tokens),
        "question_tokens": sorted(question_tokens),
        "answer_evidence": answer_evidence,
        "question_evidence": question_evidence,
    }


def _evidence(tokens: set[str], compile_index: dict[str, Any], *, min_overlap: int = 1) -> dict[str, Any]:
    if not tokens:
        return {
            "source_record_match_count": 0,
            "direct_match_count": 0,
            "source_record_strong_match_count": 0,
            "direct_strong_match_count": 0,
            "source_record_best_coverage": 0.0,
            "direct_best_coverage": 0.0,
            "source_record_matches": [],
            "direct_matches": [],
        }
    source_matches = _matching_rows(tokens, compile_index["source_rows"], min_overlap=min_overlap)
    direct_matches = _matching_rows(tokens, compile_index["direct_rows"], min_overlap=min_overlap)
    return {
        "source_record_match_count": len(source_matches),
        "direct_match_count": len(direct_matches),
        "source_record_strong_match_count": sum(1 for match in source_matches if _is_strong_match(match, tokens)),
        "direct_strong_match_count": sum(1 for match in direct_matches if _is_strong_match(match, tokens)),
        "source_record_best_coverage": _best_coverage(source_matches, tokens),
        "direct_best_coverage": _best_coverage(direct_matches, tokens),
        "source_record_matches": source_matches[:5],
        "direct_matches": direct_matches[:5],
    }


def _evidence_class(*, answer_evidence: dict[str, Any], question_evidence: dict[str, Any]) -> str:
    answer_source = int(answer_evidence.get("source_record_strong_match_count", 0) or 0)
    answer_direct = int(answer_evidence.get("direct_strong_match_count", 0) or 0)
    answer_source_weak = int(answer_evidence.get("source_record_match_count", 0) or 0)
    answer_direct_weak = int(answer_evidence.get("direct_match_count", 0) or 0)
    question_source = int(question_evidence.get("source_record_match_count", 0) or 0)
    if answer_source and not answer_direct:
        return "answer_stranded_in_source_record"
    if answer_source and answer_direct:
        return "answer_present_in_direct_and_source"
    if answer_direct:
        return "answer_present_in_direct_only"
    if answer_source_weak and not answer_direct_weak:
        return "weak_answer_trace_in_source_record"
    if answer_source_weak:
        return "weak_answer_trace_in_source_and_direct"
    if question_source:
        return "question_surface_present_without_answer_match"
    return "no_obvious_source_match"


def _coordinate_class(
    *,
    question: str,
    reference_answer: str,
    predicate_hints: list[str],
    answer_tokens: set[str],
    question_tokens: set[str],
) -> str:
    """Classify the answer-bearing shape without naming fixture content."""

    semantic_hints = [
        hint for hint in predicate_hints if hint != "memberchk" and not hint.startswith("source_record")
    ]
    text = " ".join([question, reference_answer, *semantic_hints]).lower().replace("_", " ")
    question_text = str(question or "").lower().replace("_", " ")
    answer_text = str(reference_answer or "").lower().replace("_", " ")
    tokens = set(question_tokens) | set(answer_tokens) | set(WORD_RE.findall(" ".join(semantic_hints).lower()))
    if _has_any(
        question_text,
        (
            "how many",
            "how long",
            "what percentage",
            "what percent",
            "what rate",
            "assessment rate",
            "what amount",
            "what would the reserve",
            "what would the balance",
            "total additional",
            "total harvest",
            "what seal numbers",
            "license number",
            "motion number",
            "timely",
            "deadline",
            "duration",
            "on time",
        ),
    ):
        return "quantity_or_duration"
    if (question_tokens & {"reserve", "balance", "budget", "fund", "funds"}) and (
        bool(answer_tokens & {"000", "dollars", "minimum", "minus", "starting", "unchanged"})
        or bool(re.search(r"[$£€]|\b\d+(?:,\d{3})+\b", answer_text))
    ):
        return "quantity_or_duration"
    if _has_any(
        question_text,
        (
            "status",
            "current",
            "condition",
            "classification",
            "result",
            "active",
            "pending",
            "closed",
            "resolved",
            "unresolved",
            "authorized",
            "approved",
            "denied",
            "decided",
            "deaccessioned",
            "filed",
            "issued",
            "rescinded",
        ),
    ):
        return "status_or_state"
    if _has_any(question_text, ("can ", "could ", "may ", "must", "should", "required", "valid", "merit", "authority", "determine", "controls", "rule")):
        return "rule_or_authority_application"
    if _is_temporal_question(question_text):
        return "date_time_or_interval"
    if _has_any(question_text, ("where", "located", "location", "custody", "retained", "stored", "cabinet", "vault", "room")):
        return "location_or_custody"
    if _has_any(question_text, ("who", "whose", "by whom", "owner", "director", "judge", "supervisor", "assigned", "role", "retains", "holds", "what type", "management entity")):
        return "identity_or_role"
    if _has_any(question_text, ("list all", "list the", "chronological", "chronology", "rank order")):
        return "set_or_list_membership"
    if _is_source_reference_question(question_text):
        return "source_reference"
    if _has_any(
        " ".join([question_text, answer_text]),
        ("how many", "how long", "elapsed", "total", "count", "number", "minutes", "hours", "amount", "rate", "percentage"),
    ):
        return "quantity_or_duration"
    if _has_any(question_text, ("why", "reason", "basis", "because", "rationale", "explain", "waive", "exception", "ambiguity")):
        return "rationale_or_exception"
    if tokens & {"list", "all", "which"}:
        return "set_or_list_membership"
    return "other_answer_bearing_detail"


def _coordinate_detail_class(
    *,
    coordinate_class: str,
    question: str,
    reference_answer: str,
    predicate_hints: list[str],
    answer_tokens: set[str],
    question_tokens: set[str],
) -> str:
    """Split broad coordinate classes into repair-relevant subshapes."""

    qa_text = " ".join([question, reference_answer]).lower().replace("_", " ")
    qa_tokens = set(question_tokens) | set(answer_tokens)
    if coordinate_class == "status_or_state":
        if _has_any(
            qa_text,
            (
                "as of",
                " on january",
                " on february",
                " on march",
                " on april",
                " on may",
                " on june",
                " on july",
                " on august",
                " on september",
                " on october",
                " on november",
                " on december",
                "on 202",
                "status on",
                "state on",
                "condition on",
            ),
        ):
            return "point_in_time_status"
        if _has_any(
            qa_text,
            (
                "reclassified",
                "changed status",
                "status changed",
                "elevated from",
                "moved from",
                "from active",
                "from pending",
                "superseded",
                "replaced",
                "voided",
                "prior superseded",
                "current authoritative",
            ),
        ):
            return "status_transition_or_supersession"
        if _has_any(
            qa_text,
            (
                "list all",
                "which items",
                "which applications",
                "which lots",
                "all protected",
                "all in-scope",
                "any further",
                "any outdoor",
                "population",
            ),
        ):
            return "partial_population_state"
        if qa_tokens & {"pending", "undetermined", "unresolved", "decided", "determined", "clarification", "commit"}:
            return "pending_or_resolution_state"
        if qa_tokens & {"current", "currently", "condition", "classification", "result", "available", "active", "approved", "denied", "cleared", "suspect"}:
            return "current_condition_or_availability"
        return "other_status_or_state"

    if coordinate_class == "identity_or_role":
        if _has_any(
            qa_text,
            (
                "owner",
                "owned",
                "ownership",
                "possession",
                "possessor",
                "retains",
                "held",
                "holds",
                "custodian",
                "custody",
                "administered",
            ),
        ):
            return "ownership_or_custody_identity"
        if _has_any(
            qa_text,
            (
                "director",
                "keeper",
                "captain",
                "captained",
                "mechanic",
                "manager",
                "managed",
                "mayor",
                "quality",
                "role",
                "supervised",
                "supervisor",
                "assigned",
            ),
        ):
            return "official_or_staff_role_identity"
        if _has_any(
            qa_text,
            (
                "according to whose",
                "whose statement",
                "by whom",
                "who exposed",
                "who discovered",
                "who reported",
                "who prepared",
                "who authored",
            ),
        ):
            return "source_actor_or_discoverer_identity"
        if qa_tokens & {"brother", "sister", "parent", "child", "children", "spouse", "heir", "beneficiary"}:
            return "family_or_legal_relationship_identity"
        return "other_identity_or_role"

    if coordinate_class == "source_reference":
        if _has_any(
            qa_text,
            (
                "opinion rather than",
                "applicant's opinion",
                "asserted",
                "claim or characterization",
                "staff finding",
                "established facts",
            ),
        ):
            return "claim_or_opinion_attribution"
        if _has_any(
            qa_text,
            (
                "source within",
                "source for",
                "which section",
                "what section",
                "where in",
                "packet",
                "register",
                "appendix",
                "schedule",
                "exhibit",
                "§",
            ),
        ):
            return "source_location_or_section"
        if _has_any(qa_text, ("list all unresolved", "open questions", "remaining open", "open items")):
            return "open_item_source_list"
        if _has_any(qa_text, ("according to", "per ", "whose", "by whom", "prepared by", "authored by")):
            return "source_actor_or_authority"
        return "other_source_reference"

    if coordinate_class == "other_answer_bearing_detail":
        if _is_participant_statement_detail(qa_text):
            return "participant_statement_detail"
        if _has_any(qa_text, ("deny", "denied", "acknowledged", "disputed", "conceded", "admitted")):
            return "claim_status_detail"
        if _has_any(
            qa_text,
            (
                "decision",
                "outcome",
                "approved",
                "denied",
                "rejected",
                "determined",
                "finding",
            ),
        ):
            return "decision_or_finding_detail"
        if _is_compact_identifier_detail(question=question, reference_answer=reference_answer, qa_tokens=qa_tokens):
            return "compact_identifier_detail"
        if _has_any(
            qa_text,
            (
                "eligible",
                "eligibility",
                "category",
                "categories",
                "priority",
                "voting rights",
                "full voting",
                "scope",
            ),
        ):
            return "eligibility_scope_or_category"
        if _has_any(
            qa_text,
            (
                "consequence",
                "penalty",
                "effect",
                "inherit",
                "inherited",
                "veto",
                "visited",
                "observed",
                "measured",
                "retains",
                "notebook",
                "disposition",
            ),
        ):
            return "source_stated_factual_detail"
        if _has_any(qa_text, ("list all", "which ", "what are the", "all claims", "all items")):
            return "set_or_list_detail"
        return "other_answer_detail"

    if coordinate_class != "quantity_or_duration":
        return ""
    has_number = bool(re.search(r"(?:^|[^a-z])(?:\d+|\$|£|€|%)(?:[^a-z]|$)", qa_text))
    if _has_any(qa_text, ("seal", "serial", "range", "through")) and (
        "number" in qa_tokens or "numbers" in qa_tokens or has_number
    ):
        return "identifier_range_or_sequence"
    if _has_any(qa_text, ("license number", "motion number", "case number", "file number")):
        return "identifier_range_or_sequence"
    if _has_any(qa_text, ("how many", "number of")) and not (qa_tokens & {"minutes", "minute", "hours", "hour"}):
        return "count_or_total"
    deadline_tokens = {
        "timely",
        "deadline",
        "elapsed",
        "window",
        "duration",
        "hours",
        "hour",
        "minutes",
        "minute",
        "late",
    }
    if qa_tokens & deadline_tokens or _has_any(qa_text, ("how long", "on time", "past 22:00", "days before", "days after")):
        return "deadline_or_duration_arithmetic"
    monetary_tokens = {
        "amount",
        "budget",
        "revenue",
        "rate",
        "assessment",
        "cost",
        "fund",
        "funds",
        "funding",
        "percent",
        "percentage",
        "dollars",
        "unit",
    }
    if re.search(r"[$£€]|\b\d+(?:\.\d+)?\s*%", qa_text) or qa_tokens & monetary_tokens or "per unit" in qa_text:
        return "monetary_rate_or_amount"
    if _has_any(qa_text, ("change", "changed", "increase", "decrease", "difference", "delta", "same total")):
        return "quantity_comparison_or_delta"
    if _has_any(qa_text, ("how many", "count", "number of", "total", "different", "awarded", "violations", "members")):
        return "count_or_total"
    if not has_number:
        return "scoped_availability_or_permission"
    return "other_quantity_or_duration"


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _is_source_reference_question(question_text: str) -> bool:
    if _has_any(
        question_text,
        (
            "according to",
            "per ",
            "source within",
            "source for",
            "which document",
            "what document",
            "which source",
            "what source",
            "which section",
            "what section",
            "where in",
            "document recorded",
            "document that recorded",
        ),
    ):
        return True
    return bool(
        re.search(r"\b(?:document|packet|report|memo|order|section|exhibit|appendix)\b", question_text)
        and re.search(r"\b(?:which|what|where|source|according|per|recorded|authority|binding)\b", question_text)
    )


def _is_temporal_question(question_text: str) -> bool:
    return bool(
        _has_any(question_text, ("when", "what date", "deadline", "scheduled", "window", "as of", "on what date"))
        or re.search(r"\bdate\b", question_text)
    )


def _is_compact_identifier_detail(*, question: str, reference_answer: str, qa_tokens: set[str]) -> bool:
    """Detect questions whose requested answer is a compact identifier/code.

    Keep this deliberately question-led. Reference answers often carry bracketed
    QA labels or local document codes, and those labels should not turn an
    ordinary statement-detail miss into an identifier-surface gap.
    """

    question_text = str(question).lower().replace("_", " ")
    if _has_any(
        question_text,
        (
            "asset tag",
            "barcode",
            "bar code",
            "case number",
            "device id",
            "device identifier",
            "file number",
            "identifier",
            "license number",
            "locker code",
            "locker codes",
            "maintenance ticket",
            "motion number",
            "permit number",
            "serial number",
            "ticket number",
        ),
    ):
        return True
    if re.search(
        r"\b(?:what|which)\b.{0,80}\b(?:id|ids|code|codes|tag|tags|serial|serials|ticket|tickets|barcode|barcodes|identifier|identifiers)\b",
        question_text,
    ):
        return True
    if re.search(r"\bwhat\s+(?:is|are)\s+the\b.{0,60}\blabels?\b", question_text):
        return True
    return bool(qa_tokens & {"identifier", "identifiers", "serial", "serials", "barcode", "barcodes"})


def _is_participant_statement_detail(text: str) -> bool:
    return bool(
        re.search(
            r"\bwhat\b.{0,80}\b(?:said|say|suggest|suggested|state|stated|testify|testified|claim|claimed|comment|commented|object|objected)\b",
            text,
        )
        or re.search(r"\b(?:statement|comment|testimony|suggestion|objection|concern)s?\b", text)
    )


def _compile_index(payload: dict[str, Any]) -> dict[str, Any]:
    facts = _facts_from_compile(payload)
    source_rows: list[dict[str, Any]] = []
    direct_rows: list[dict[str, Any]] = []
    for fact in facts:
        parsed = _parse_fact(fact)
        if not parsed:
            continue
        predicate, args = parsed
        row = {
            "fact": fact,
            "predicate": predicate,
            "args": args,
            "tokens": _salient_tokens(" ".join([predicate, *args])),
        }
        if predicate.startswith("source_record"):
            source_rows.append(row)
        else:
            direct_rows.append(row)
    return {"source_rows": source_rows, "direct_rows": direct_rows}


def _matching_rows(tokens: set[str], rows: list[dict[str, Any]], *, min_overlap: int) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for row in rows:
        overlap = tokens & set(row["tokens"])
        if len(overlap) < min_overlap:
            continue
        matches.append(
            {
                "predicate": row["predicate"],
                "overlap": sorted(overlap),
                "coverage": round(len(overlap) / max(1, len(tokens)), 3),
                "fact": row["fact"],
            }
        )
    matches.sort(key=lambda item: (-float(item["coverage"]), -len(item["overlap"]), item["predicate"], item["fact"]))
    return matches


def _is_strong_match(match: dict[str, Any], tokens: set[str]) -> bool:
    overlap_count = len(match.get("overlap", []))
    coverage = float(match.get("coverage", 0.0) or 0.0)
    if len(tokens) <= 2:
        return overlap_count == len(tokens)
    if len(tokens) <= 4:
        return overlap_count >= len(tokens) - 1 and coverage >= 0.75
    return overlap_count >= 3 and coverage >= 0.6


def _best_coverage(matches: list[dict[str, Any]], tokens: set[str]) -> float:
    if not matches or not tokens:
        return 0.0
    return round(max(float(match.get("coverage", 0.0) or 0.0) for match in matches), 3)


def _facts_from_compile(payload: dict[str, Any]) -> list[str]:
    source_compile = payload.get("source_compile") if isinstance(payload.get("source_compile"), dict) else {}
    facts = source_compile.get("facts")
    if isinstance(facts, list):
        return [str(fact).strip() for fact in facts if str(fact).strip()]
    parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
    parsed_facts = parsed.get("facts")
    if isinstance(parsed_facts, list):
        return [str(fact).strip() for fact in parsed_facts if str(fact).strip()]
    return []


def _parse_fact(fact: str) -> tuple[str, list[str]] | None:
    match = FACT_RE.match(str(fact).strip())
    if not match:
        return None
    return match.group(1), [part.strip().strip("'\"") for part in _split_args(match.group(2))]


def _split_args(raw: str) -> list[str]:
    # Current compiled facts use atom arguments; this small splitter avoids
    # corrupting quoted commas if future ledgers contain quoted values.
    args: list[str] = []
    current: list[str] = []
    quote = ""
    for char in raw:
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == ",":
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current or raw:
        args.append("".join(current).strip())
    return args


def _query_predicates(query: Any) -> list[str]:
    return [match.group(1) for match in re.finditer(r"\b([a-z][A-Za-z0-9_]*)\s*\(", str(query))]


def _salient_tokens(text: str) -> set[str]:
    tokens = set()
    for token in WORD_RE.findall(str(text).lower().replace("_", " ")):
        if token in STOPWORDS:
            continue
        if len(token) == 1 and not token.isdigit():
            continue
        tokens.add(token)
    return tokens


def _scorecard_fixture_rows(scorecard: dict[str, Any]) -> list[Any]:
    fixtures = scorecard.get("fixtures")
    if isinstance(fixtures, list):
        return fixtures
    artifacts = scorecard.get("artifacts")
    if isinstance(artifacts, list):
        return artifacts
    return []


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Source-Surface Gap Audit",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "## Policy",
        "",
    ]
    for rule in report.get("policy", []):
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Rows audited: `{summary.get('row_count', 0)}`",
            f"- Failure surfaces: `{summary.get('failure_surface_counts', {})}`",
            f"- Evidence classes: `{summary.get('evidence_class_counts', {})}`",
            f"- Coordinate classes: `{summary.get('coordinate_class_counts', {})}`",
            f"- Coordinate detail classes: `{summary.get('coordinate_detail_class_counts', {})}`",
            f"- Answer present in source_record rows: `{summary.get('answer_in_source_record_rows', 0)}`",
            f"- Answer present in direct rows: `{summary.get('answer_in_direct_rows', 0)}`",
            f"- Question terms present in source_record rows: `{summary.get('question_terms_in_source_record_rows', 0)}`",
            "",
            "## Rows",
            "",
            "| Fixture | Row | Verdict | Surface | Evidence Class | Coordinate | Detail | Source Answer Matches | Direct Answer Matches | Question |",
            "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in report.get("rows", []):
        answer = row.get("answer_evidence", {}) if isinstance(row.get("answer_evidence"), dict) else {}
        question = str(row.get("question", "")).replace("|", "/")
        lines.append(
            f"| `{row.get('fixture', '')}` | `{row.get('id', '')}` | `{row.get('verdict', '')}` | "
            f"`{row.get('failure_surface', '')}` | `{row.get('evidence_class', '')}` | "
            f"`{row.get('coordinate_class', '')}` | "
            f"`{row.get('coordinate_detail_class', '')}` | "
            f"`{answer.get('source_record_strong_match_count', 0)}` | "
            f"`{answer.get('direct_strong_match_count', 0)}` | {question} |"
        )
    lines.append("")
    lines.extend(["## Top Stranded Examples", ""])
    stranded = [row for row in report.get("rows", []) if row.get("evidence_class") == "answer_stranded_in_source_record"]
    for row in stranded[:12]:
        matches = row.get("answer_evidence", {}).get("source_record_matches", [])
        lines.append(f"### `{row.get('fixture')}` `{row.get('id')}`")
        lines.append("")
        lines.append(f"- Question: {row.get('question', '')}")
        lines.append(f"- Reference answer: `{row.get('reference_answer', '')}`")
        for match in matches[:2]:
            fact = str(match.get("fact", "")).replace("|", "/")
            overlap = ", ".join(match.get("overlap", []))
            lines.append(f"- Source match ({overlap}): `{fact}`")
        lines.append("")
    return "\n".join(lines)


def _path_from_artifact(value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    return path if path.is_absolute() else REPO_ROOT / path


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return ""
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
