"""Deterministic legal authority verification prototype.

This module is intentionally narrow. It extracts citation-shaped mentions from
a filing, resolves them against a declared authority inventory, checks quoted
language and pin-cite locality when authority text is available, and emits a
governed fact/report bundle. It does not decide whether an authority is good
law or whether the authority legally supports a proposition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.legal_authority_resolvers import LocalAuthorityInventoryResolver, unsupported_reporter_lookup_row


CASE_WORD_RE = r"(?:[A-Z][A-Za-z0-9.&']*|of|the|and|for|in|on|to|ex|rel\.|&)"
CASE_PARTY_RE = rf"{CASE_WORD_RE}(?:\s+{CASE_WORD_RE}){{0,8}}"
CITATION_RE = re.compile(
    rf"(?P<case>{CASE_PARTY_RE} v\. {CASE_PARTY_RE}),\s+"
    r"(?P<volume>\d+)\s+(?P<reporter>U\.S\.|F\. ?(?:2d|3d|4th)|F\. ?Supp\. ?(?:2d|3d)?|S\. ?Ct\.)\s+(?P<page>\d+)"
    r"(?:,\s+(?P<pin>\d+))?\s+\((?P<year>\d{4})\)"
)
BARE_CITATION_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(?P<volume>\d+)\s+(?P<reporter>U\.S\.|F\. ?(?:2d|3d|4th)|F\. ?Supp\. ?(?:2d|3d)?|S\. ?Ct\.)\s+"
    r"(?P<page>\d+)"
    r"(?:,\s+(?P<pin_comma>\d+)|\s+at\s+(?P<pin_at>\d+))?"
    r"(?:\s+\((?P<year>\d{4})\))?"
)
QUOTE_RE = re.compile(r'"(?P<quote>[^"]+)"')


@dataclass(frozen=True)
class Paragraph:
    text: str
    start_line: int


@dataclass(frozen=True)
class CitationExtract:
    case_name: str
    citation: str
    reporter: str
    pin: str
    year: str
    start: int
    end: int
    lookup_start: int
    lookup_end: int


def verify_legal_authorities(
    *,
    source_path: Path,
    authority_inventory_path: Path,
    document_id: str = "legal_authority_micro",
) -> dict[str, Any]:
    source_text = source_path.read_text(encoding="utf-8")
    resolver = LocalAuthorityInventoryResolver.from_path(authority_inventory_path)
    paragraphs = _paragraphs(source_text)
    facts: list[str] = []
    mentions: list[dict[str, Any]] = []
    lookup_rows: list[dict[str, Any]] = []
    issue_rows: list[dict[str, Any]] = []

    mention_index = 0
    quote_index = 0
    proposition_index = 0
    for paragraph in paragraphs:
        for citation_extract in _citation_extracts(paragraph.text):
            mention_index += 1
            mention_id = f"mention_{mention_index:03d}"
            case_name = citation_extract.case_name
            citation = citation_extract.citation
            citation_atom = _citation_atom(citation)
            citation_line = paragraph.start_line + paragraph.text[: citation_extract.start].count("\n")
            source_scope = f"source_line_{citation_line}"
            line_atom = f"line_{citation_line}"
            facts.append(
                f"legal_citation_mention({document_id}, {mention_id}, {citation_atom}, {line_atom}, {source_scope})."
            )
            if not _supported_reporter(citation_extract.reporter):
                lookup = unsupported_reporter_lookup_row(
                    citation=citation,
                    start_index=citation_extract.lookup_start,
                    end_index=citation_extract.lookup_end,
                )
                lookup_rows.append(lookup)
                resolution_status, authority_id = "invalid_reporter", "invalid_authority"
                facts.append(
                    "legal_authority_resolution("
                    f"{mention_id}, {citation_atom}, {resolution_status}, {authority_id}, {source_scope})."
                )
                facts.append(
                    "legal_verification_abstention("
                    f"{mention_id}, authority_resolution, unsupported_reporter, {source_scope})."
                )
                issue_rows.append(
                    {
                        "mention_id": mention_id,
                        "issue": resolution_status,
                        "reason": "unsupported_reporter",
                        "line": citation_line,
                    }
                )
                mentions.append(
                    {
                        "mention_id": mention_id,
                        "case_name": case_name,
                        "citation": citation,
                        "normalized_citation": citation_atom,
                        "line": citation_line,
                        "pin": citation_extract.pin,
                        "resolution_status": resolution_status,
                        "authority_id": authority_id,
                        "metadata_checks": [],
                        "quote_check": None,
                        "pin_check": None,
                        "proposition_boundary": None,
                    }
                )
                continue

            resolution = resolver.lookup_citation(
                citation=citation,
                start_index=citation_extract.lookup_start,
                end_index=citation_extract.lookup_end,
            )
            authority_matches = resolution.authority_matches
            lookup = resolution.lookup_row
            lookup_rows.append(lookup)
            authority = authority_matches[0] if len(authority_matches) == 1 else None
            resolution_status, authority_id = _resolution(authority_matches)

            facts.append(
                "legal_authority_resolution("
                f"{mention_id}, {citation_atom}, {resolution_status}, {authority_id}, {source_scope})."
            )
            mention_report: dict[str, Any] = {
                "mention_id": mention_id,
                "case_name": case_name,
                "citation": citation,
                "normalized_citation": citation_atom,
                "line": citation_line,
                "pin": citation_extract.pin,
                "resolution_status": resolution_status,
                "authority_id": authority_id,
                "metadata_checks": [],
                "quote_check": None,
                "pin_check": None,
                "proposition_boundary": None,
            }

            if authority is None:
                issue_rows.append(
                    {
                        "mention_id": mention_id,
                        "issue": resolution_status,
                        "reason": _resolution_reason(resolution_status),
                        "line": citation_line,
                    }
                )
                abstention_reason = "ambiguous_authority" if resolution_status == "ambiguous" else "citation_not_found"
                facts.append(
                    "legal_verification_abstention("
                    f"{mention_id}, authority_resolution, {abstention_reason}, {source_scope})."
                )
                mentions.append(mention_report)
                continue

            metadata_candidates = []
            if case_name:
                metadata_candidates.append(("case_name", case_name))
            if citation_extract.year:
                metadata_candidates.append(("year", citation_extract.year))
            for field, extracted in metadata_candidates:
                status = "match" if _metadata_matches(field, extracted, authority) else "mismatch"
                mention_report["metadata_checks"].append(
                    {
                        "field": field,
                        "extracted": extracted,
                        "authority_value": str(authority.get(field) or ""),
                        "status": status,
                    }
                )
                facts.append(
                    "legal_authority_metadata_check("
                    f"{mention_id}, {authority['authority_id']}, {field}, {status}, {source_scope})."
                )
                if status == "mismatch":
                    issue_rows.append(
                        {
                            "mention_id": mention_id,
                            "issue": "metadata_mismatch",
                            "field": field,
                            "line": citation_line,
                        }
                    )

            quote_match = QUOTE_RE.search(paragraph.text, citation_extract.end)
            if quote_match:
                quote_index += 1
                quote_id = f"quote_{quote_index:03d}"
                quote = _clean_space(quote_match.group("quote"))
                quote_line = paragraph.start_line + paragraph.text[: quote_match.start()].count("\n")
                quote_scope = f"source_line_{quote_line}"
                quote_location = f"filing_line_{quote_line}"
                digest = _quote_digest(quote)
                facts.append(
                    f"legal_quote_claim({mention_id}, {quote_id}, {digest}, {quote_location}, {quote_scope})."
                )
                quote_status, matched_location = _quote_span_match(quote, authority)
                facts.append(
                    "legal_quote_span_match("
                    f"{quote_id}, {authority['authority_id']}, {quote_status}, {matched_location}, authority_inventory)."
                )
                mention_report["quote_check"] = {
                    "quote_id": quote_id,
                    "quote_digest": digest,
                    "line": quote_line,
                    "status": quote_status,
                    "matched_location": matched_location,
                }
                if quote_status in {"no_match", "authority_unavailable"}:
                    issue_name = (
                        "authority_text_unavailable"
                        if quote_status == "authority_unavailable"
                        else "quote_not_found_in_authority"
                    )
                    abstention_reason = (
                        "authority_text_unavailable"
                        if quote_status == "authority_unavailable"
                        else "quote_not_found_in_authority"
                    )
                    issue_rows.append(
                        {
                            "mention_id": mention_id,
                            "quote_id": quote_id,
                            "issue": issue_name,
                            "line": quote_line,
                        }
                    )
                    facts.append(
                        "legal_verification_abstention("
                        f"{quote_id}, quote_verification, {abstention_reason}, {quote_scope})."
                    )
                pin = citation_extract.pin
                pin_status, pin_atom = _pin_status(pin=pin, quote_status=quote_status, matched_location=matched_location, authority=authority)
                if pin_status != "not_applicable":
                    facts.append(
                        "legal_pin_cite_check("
                        f"{mention_id}, {authority['authority_id']}, {pin_atom}, {pin_status}, {source_scope})."
                    )
                    mention_report["pin_check"] = {
                        "pin": pin_atom,
                        "status": pin_status,
                    }
                    if pin_status == "quote_outside_pin":
                        issue_rows.append(
                            {
                                "mention_id": mention_id,
                                "issue": "quote_outside_cited_pin",
                                "pin": pin_atom,
                                "line": citation_line,
                            }
                        )
                        facts.append(
                            "legal_verification_abstention("
                            f"{mention_id}, pin_cite_verification, quote_outside_cited_pin, {source_scope})."
                        )

            if _has_proposition_boundary(paragraph.text, citation_extract.end):
                proposition_index += 1
                proposition_id = f"proposition_{mention_index:03d}"
                boundary_scope = f"source_line_{paragraph.start_line + paragraph.text[citation_extract.end:].count(chr(10))}"
                proposition_digest = _proposition_digest(paragraph.text[citation_extract.end:])
                claim_location = f"filing_line_{citation_line}"
                facts.append(
                    "legal_proposition_claim("
                    f"{mention_id}, {proposition_id}, {proposition_digest}, {claim_location}, human_review_required)."
                )
                facts.append(
                    "legal_proposition_source_span("
                    f"{proposition_id}, {authority['authority_id']}, span_not_selected, no_deterministic_span, {boundary_scope})."
                )
                facts.append(
                    "legal_support_assessment("
                    f"{proposition_id}, {authority['authority_id']}, deterministic_abstain, no_independent_review, {boundary_scope})."
                )
                facts.append(
                    "legal_proposition_support_boundary("
                    f"{mention_id}, {proposition_id}, deterministic_abstain, human_review_required, {boundary_scope})."
                )
                facts.append(
                    "legal_verification_abstention("
                    f"{proposition_id}, proposition_support, requires_human_legal_review, {boundary_scope})."
                )
                mention_report["proposition_boundary"] = {
                    "proposition_id": proposition_id,
                    "proposition_digest": proposition_digest,
                    "boundary_status": "deterministic_abstain",
                    "review_requirement": "human_review_required",
                    "candidate_span_status": "no_deterministic_span",
                    "support_assessment": "deterministic_abstain",
                }
                issue_rows.append(
                    {
                        "mention_id": mention_id,
                        "proposition_id": proposition_id,
                        "issue": "proposition_support_requires_human_review",
                        "line": citation_line,
                    }
                )
            mentions.append(mention_report)

    for mention in mentions:
        mention["verification_status"] = _mention_verification_status(mention)

    false_verified = _false_verified_count(mentions)
    document_outcome = "citation_clean" if not issue_rows else "review_required"
    summary = {
        "document_id": document_id,
        "citation_mentions": len(mentions),
        "verified_mentions": sum(1 for row in mentions if row.get("verification_status") == "verified"),
        "blocked_mentions": sum(1 for row in mentions if row.get("verification_status") == "blocked"),
        "review_required_mentions": sum(1 for row in mentions if row.get("verification_status") == "review_required"),
        "resolved": sum(1 for row in mentions if row["resolution_status"] == "resolved"),
        "unresolved": sum(1 for row in mentions if row["resolution_status"] == "unresolved"),
        "ambiguous": sum(1 for row in mentions if row["resolution_status"] == "ambiguous"),
        "invalid_reporter": sum(1 for row in mentions if row["resolution_status"] == "invalid_reporter"),
        "quote_claims": sum(1 for row in mentions if row.get("quote_check")),
        "quote_exact_or_normalized_match": sum(
            1
            for row in mentions
            if row.get("quote_check")
            and row["quote_check"]["status"] in {"exact_match", "normalized_match"}
        ),
        "quote_mismatch": sum(
            1 for row in mentions if row.get("quote_check") and row["quote_check"]["status"] == "no_match"
        ),
        "pin_mismatch": sum(
            1 for row in mentions if row.get("pin_check") and row["pin_check"]["status"] == "quote_outside_pin"
        ),
        "proposition_boundaries": sum(1 for row in mentions if row.get("proposition_boundary")),
        "false_verified": false_verified,
        "document_outcome": document_outcome,
        "status": "pass" if false_verified == 0 else "fail",
    }
    report = {
        "schema_version": "legal_authority_verification_report_v1",
        "source": str(source_path),
        "authority_inventory": str(authority_inventory_path),
        "summary": summary,
        "courtlistener_like_lookup": lookup_rows,
        "mentions": mentions,
        "issues": issue_rows,
        "facts": facts,
    }
    report["ledger_queries"] = build_ledger_queries(report)
    return report


def build_ledger_queries(report: dict[str, Any]) -> dict[str, Any]:
    """Return practical query answers derived only from structured ledger rows."""

    mentions = list(report.get("mentions") or [])
    issues = list(report.get("issues") or [])
    unresolved = [
        _mention_brief(row)
        for row in mentions
        if row.get("resolution_status") in {"unresolved", "ambiguous", "invalid_reporter", "unavailable"}
    ]
    metadata_mismatches = [
        {
            "mention_id": row["mention_id"],
            "citation": row["citation"],
            "field": check["field"],
            "status": check["status"],
        }
        for row in mentions
        for check in row.get("metadata_checks", [])
        if check.get("status") == "mismatch"
    ]
    quote_mismatches = [
        {
            "mention_id": row["mention_id"],
            "citation": row["citation"],
            "quote_id": row["quote_check"]["quote_id"],
            "status": row["quote_check"]["status"],
        }
        for row in mentions
        if row.get("quote_check") and row["quote_check"].get("status") == "no_match"
    ]
    unavailable_authority_text = [
        {
            "mention_id": row["mention_id"],
            "citation": row["citation"],
            "quote_id": row["quote_check"]["quote_id"],
            "status": row["quote_check"]["status"],
        }
        for row in mentions
        if row.get("quote_check") and row["quote_check"].get("status") == "authority_unavailable"
    ]
    pin_mismatches = [
        {
            "mention_id": row["mention_id"],
            "citation": row["citation"],
            "pin": row["pin_check"]["pin"],
            "status": row["pin_check"]["status"],
        }
        for row in mentions
        if row.get("pin_check") and row["pin_check"].get("status") == "quote_outside_pin"
    ]
    proposition_review = [
        {
            "mention_id": row["mention_id"],
            "citation": row["citation"],
            "proposition_id": row["proposition_boundary"]["proposition_id"],
            "review_requirement": row["proposition_boundary"]["review_requirement"],
            "support_assessment": row["proposition_boundary"].get("support_assessment", ""),
        }
        for row in mentions
        if row.get("proposition_boundary")
    ]
    blocking_issues = [
        row
        for row in issues
        if row.get("issue")
        in {
            "unresolved",
            "ambiguous",
            "invalid_reporter",
            "metadata_mismatch",
            "authority_text_unavailable",
            "quote_not_found_in_authority",
            "quote_outside_cited_pin",
        }
    ]
    return {
        "which_citations_do_not_resolve": unresolved,
        "which_cases_have_metadata_mismatches": metadata_mismatches,
        "which_quotes_cannot_be_found": quote_mismatches,
        "which_authority_text_is_unavailable": unavailable_authority_text,
        "which_pin_cites_do_not_contain_the_quote": pin_mismatches,
        "which_propositions_require_human_review": proposition_review,
        "can_this_filing_be_certified_citation_clean": {
            "citation_clean": not blocking_issues,
            "blocking_issue_count": len(blocking_issues),
            "review_required_count": len(proposition_review),
            "answer": "yes" if not blocking_issues and not proposition_review else "no",
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Legal Authority Verification Report",
        "",
        f"- Document: `{summary['document_id']}`",
        f"- Citation mentions: `{summary['citation_mentions']}`",
        f"- Verified mentions: `{summary['verified_mentions']}`",
        f"- Blocked mentions: `{summary['blocked_mentions']}`",
        f"- Review-required mentions: `{summary['review_required_mentions']}`",
        f"- Resolved: `{summary['resolved']}`",
        f"- Unresolved: `{summary['unresolved']}`",
        f"- Invalid reporter: `{summary['invalid_reporter']}`",
        f"- Quote claims: `{summary['quote_claims']}`",
        f"- Quote mismatches: `{summary['quote_mismatch']}`",
        f"- Pin mismatches: `{summary['pin_mismatch']}`",
        f"- Proposition support boundaries: `{summary['proposition_boundaries']}`",
        f"- False verified: `{summary['false_verified']}`",
        f"- Document outcome: `{summary['document_outcome']}`",
        f"- Status: `{summary['status']}`",
        "",
        "## Issues",
        "",
    ]
    if report.get("issues"):
        lines.extend(["| Mention | Issue | Detail |", "| --- | --- | --- |"])
        for issue in report["issues"]:
            detail = ", ".join(f"{key}={value}" for key, value in issue.items() if key not in {"mention_id", "issue"})
            lines.append(f"| `{issue.get('mention_id', '')}` | `{issue.get('issue', '')}` | {detail} |")
    else:
        lines.append("_No issues._")
    lines.extend(
        [
            "",
            "## Mentions",
            "",
            "| Mention | Citation | Status | Resolution | Quote | Pin | Proposition |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.get("mentions", []):
        quote = row["quote_check"]["status"] if row.get("quote_check") else ""
        pin = row["pin_check"]["status"] if row.get("pin_check") else ""
        proposition = row["proposition_boundary"]["review_requirement"] if row.get("proposition_boundary") else ""
        lines.append(
            f"| `{row['mention_id']}` | `{row['citation']}` | `{row.get('verification_status', '')}` | `{row['resolution_status']}` | "
            f"`{quote}` | `{pin}` | `{proposition}` |"
        )
    queries = report.get("ledger_queries") or {}
    if queries:
        clean = queries.get("can_this_filing_be_certified_citation_clean") or {}
        lines.extend(
            [
                "",
                "## Ledger Query Answers",
                "",
                f"- Certification answer: `{clean.get('answer', '')}`",
                f"- Citation clean: `{clean.get('citation_clean', False)}`",
                f"- Blocking issues: `{clean.get('blocking_issue_count', 0)}`",
                f"- Review-required propositions: `{clean.get('review_required_count', 0)}`",
                f"- Unresolved citations: `{len(queries.get('which_citations_do_not_resolve') or [])}`",
                f"- Unavailable authority text: `{len(queries.get('which_authority_text_is_unavailable') or [])}`",
                f"- Quote mismatches: `{len(queries.get('which_quotes_cannot_be_found') or [])}`",
                f"- Pin-cite mismatches: `{len(queries.get('which_pin_cites_do_not_contain_the_quote') or [])}`",
            ]
        )
    return "\n".join(lines) + "\n"


def facts_text(report: dict[str, Any]) -> str:
    return "\n".join(report.get("facts", [])) + "\n"


def _mention_brief(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "mention_id": row.get("mention_id", ""),
        "citation": row.get("citation", ""),
        "resolution_status": row.get("resolution_status", ""),
        "authority_id": row.get("authority_id", ""),
        "line": row.get("line", ""),
    }


def _paragraphs(text: str) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    start_line = 1
    buffer: list[str] = []
    buffer_start = 1
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            if buffer:
                paragraphs.append(Paragraph(text="\n".join(buffer), start_line=buffer_start))
                buffer = []
            start_line = line_number + 1
            continue
        if not buffer:
            buffer_start = line_number
        buffer.append(line)
        start_line = line_number + 1
    if buffer:
        paragraphs.append(Paragraph(text="\n".join(buffer), start_line=buffer_start))
    return paragraphs


def _citation_extracts(text: str) -> list[CitationExtract]:
    full_matches = [
        CitationExtract(
            case_name=_clean_space(match.group("case")),
            citation=_citation_text(
                volume=match.group("volume"),
                reporter=match.group("reporter"),
                page=match.group("page"),
            ),
            reporter=match.group("reporter"),
            pin=match.group("pin") or "",
            year=match.group("year") or "",
            start=match.start(),
            end=match.end(),
            lookup_start=match.start("volume"),
            lookup_end=match.end("page"),
        )
        for match in CITATION_RE.finditer(text)
    ]
    occupied = [(row.start, row.end) for row in full_matches]
    bare_matches: list[CitationExtract] = []
    for match in BARE_CITATION_RE.finditer(text):
        if any(_spans_overlap(match.span(), span) for span in occupied):
            continue
        bare_matches.append(
            CitationExtract(
                case_name="",
                citation=_citation_text(
                    volume=match.group("volume"),
                    reporter=match.group("reporter"),
                    page=match.group("page"),
                ),
                reporter=match.group("reporter"),
                pin=match.group("pin_comma") or match.group("pin_at") or "",
                year=match.group("year") or "",
                start=match.start(),
                end=match.end(),
                lookup_start=match.start("volume"),
                lookup_end=match.end("page"),
            )
        )
    return sorted([*full_matches, *bare_matches], key=lambda row: (row.start, row.end))


def _spans_overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def _citation_text(*, volume: str, reporter: str, page: str) -> str:
    return f"{volume} {_clean_space(reporter)} {page}"


def _citation_atom(citation: str) -> str:
    citation = citation.casefold().replace("u.s.", "us")
    compact = re.sub(r"[^a-z0-9]+", "_", citation).strip("_")
    return f"cite_{compact}"


def _quote_digest(quote: str) -> str:
    digest = hashlib.sha256(_normalize_text(quote).encode("utf-8")).hexdigest()[:12]
    return f"sha256_{digest}"


def _proposition_digest(proposition_tail: str) -> str:
    digest = hashlib.sha256(_normalize_text(proposition_tail).encode("utf-8")).hexdigest()[:12]
    return f"sha256_{digest}"


def _resolution(matches: list[dict[str, Any]]) -> tuple[str, str]:
    if not matches:
        return "unresolved", "authority_not_found"
    if len(matches) > 1:
        return "ambiguous", "ambiguous_authority"
    return "resolved", str(matches[0]["authority_id"])


def _resolution_reason(status: str) -> str:
    return {
        "unresolved": "citation_not_found",
        "ambiguous": "ambiguous_authority",
        "invalid_reporter": "unsupported_reporter",
        "unavailable": "authority_lookup_unavailable",
    }.get(status, status)


def _supported_reporter(reporter: str) -> bool:
    return _clean_space(reporter) == "U.S."


def _metadata_matches(field: str, extracted: str, authority: dict[str, Any]) -> bool:
    expected = str(authority.get(field) or "")
    if field == "case_name":
        return _normalize_name(extracted) == _normalize_name(expected)
    return extracted.strip() == expected.strip()


def _quote_span_match(quote: str, authority: dict[str, Any]) -> tuple[str, str]:
    normalized_quote = _normalize_text(quote)
    pages = authority.get("pages") if isinstance(authority.get("pages"), dict) else {}
    for page, text in pages.items():
        if normalized_quote and normalized_quote in _normalize_text(str(text)):
            return "exact_match", f"page_{page}"
    if not pages:
        return "authority_unavailable", "authority_unavailable"
    return "no_match", "no_match"


def _pin_status(
    *,
    pin: str | None,
    quote_status: str,
    matched_location: str,
    authority: dict[str, Any],
) -> tuple[str, str]:
    if not pin:
        return "no_pin_stated", "no_pin_stated"
    pin_atom = f"page_{pin}"
    if quote_status not in {"exact_match", "normalized_match"}:
        return "not_applicable", pin_atom
    pages = authority.get("pages") if isinstance(authority.get("pages"), dict) else {}
    if pin not in pages:
        return "pin_unavailable", pin_atom
    if matched_location == pin_atom:
        return "pin_contains_quote", pin_atom
    return "quote_outside_pin", pin_atom


def _has_proposition_boundary(paragraph: str, citation_end: int) -> bool:
    tail = paragraph[citation_end:].casefold()
    return "proposition" in tail


def _mention_verification_status(mention: dict[str, Any]) -> str:
    if _mention_blocking_reasons(mention):
        return "blocked"
    if mention.get("proposition_boundary"):
        return "review_required"
    return "verified"


def _mention_blocking_reasons(mention: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if mention.get("resolution_status") != "resolved":
        reasons.append(str(mention.get("resolution_status") or "authority_resolution"))
    for check in mention.get("metadata_checks", []):
        if check.get("status") == "mismatch":
            reasons.append(f"metadata_mismatch:{check.get('field', '')}")
    quote_check = mention.get("quote_check")
    if quote_check and quote_check.get("status") in {"no_match", "authority_unavailable"}:
        reasons.append(str(quote_check.get("status")))
    pin_check = mention.get("pin_check")
    if pin_check and pin_check.get("status") == "quote_outside_pin":
        reasons.append("quote_outside_pin")
    return reasons


def _false_verified_count(mentions: list[dict[str, Any]]) -> int:
    return sum(
        1
        for mention in mentions
        if mention.get("verification_status") == "verified" and _mention_blocking_reasons(mention)
    )


def _normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _normalize_text(value: str) -> str:
    return _clean_space(value).casefold()


def _clean_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic legal authority verification.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--authority-inventory", type=Path, required=True)
    parser.add_argument("--document-id", default="legal_authority_micro")
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--out-facts", type=Path)
    args = parser.parse_args(argv)

    report = verify_legal_authorities(
        source_path=args.source,
        authority_inventory_path=args.authority_inventory,
        document_id=args.document_id,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if args.out_facts:
        args.out_facts.parent.mkdir(parents=True, exist_ok=True)
        args.out_facts.write_text(facts_text(report), encoding="utf-8")
    if not args.out_json and not args.out_md and not args.out_facts:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["summary"]["status"] == "pass" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
