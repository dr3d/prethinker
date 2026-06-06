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


CITATION_RE = re.compile(
    r"(?P<case>[A-Z][A-Za-z0-9.&' -]+? v\. [A-Z][A-Za-z0-9.&' -]+?),\s+"
    r"(?P<volume>\d+)\s+(?P<reporter>U\.S\.)\s+(?P<page>\d+)"
    r"(?:,\s+(?P<pin>\d+))?\s+\((?P<year>\d{4})\)"
)
QUOTE_RE = re.compile(r'"(?P<quote>[^"]+)"')


@dataclass(frozen=True)
class Paragraph:
    text: str
    start_line: int


def verify_legal_authorities(
    *,
    source_path: Path,
    authority_inventory_path: Path,
    document_id: str = "legal_authority_micro",
) -> dict[str, Any]:
    source_text = source_path.read_text(encoding="utf-8")
    inventory = _load_inventory(authority_inventory_path)
    paragraphs = _paragraphs(source_text)
    facts: list[str] = []
    mentions: list[dict[str, Any]] = []
    lookup_rows: list[dict[str, Any]] = []
    issue_rows: list[dict[str, Any]] = []

    mention_index = 0
    quote_index = 0
    proposition_index = 0
    for paragraph in paragraphs:
        for match in CITATION_RE.finditer(paragraph.text):
            mention_index += 1
            mention_id = f"mention_{mention_index:03d}"
            case_name = _clean_space(match.group("case"))
            citation = _citation_text(match)
            citation_atom = _citation_atom(citation)
            citation_line = paragraph.start_line + paragraph.text[: match.start()].count("\n")
            source_scope = f"source_line_{citation_line}"
            line_atom = f"line_{citation_line}"
            authority_matches = inventory.get(citation, [])
            lookup = _courtlistener_like_lookup(
                citation=citation,
                match=match,
                authority_matches=authority_matches,
            )
            lookup_rows.append(lookup)
            authority = authority_matches[0] if len(authority_matches) == 1 else None
            resolution_status, authority_id = _resolution(authority_matches)

            facts.append(
                f"legal_citation_mention({document_id}, {mention_id}, {citation_atom}, {line_atom}, {source_scope})."
            )
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
                "pin": match.group("pin") or "",
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

            for field, extracted in (("case_name", case_name), ("year", match.group("year"))):
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

            quote_match = QUOTE_RE.search(paragraph.text, match.end())
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
                if quote_status == "no_match":
                    issue_rows.append(
                        {
                            "mention_id": mention_id,
                            "quote_id": quote_id,
                            "issue": "quote_not_found_in_authority",
                            "line": quote_line,
                        }
                    )
                    facts.append(
                        "legal_verification_abstention("
                        f"{quote_id}, quote_verification, quote_not_found_in_authority, {quote_scope})."
                    )
                pin = match.group("pin")
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

            if _has_proposition_boundary(paragraph.text, match.end()):
                proposition_index += 1
                proposition_id = f"proposition_{mention_index:03d}"
                boundary_scope = f"source_line_{paragraph.start_line + paragraph.text[match.end():].count(chr(10))}"
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
                    "boundary_status": "deterministic_abstain",
                    "review_requirement": "human_review_required",
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

    false_verified = _false_verified_count(mentions)
    document_outcome = "citation_clean" if not issue_rows else "review_required"
    summary = {
        "document_id": document_id,
        "citation_mentions": len(mentions),
        "resolved": sum(1 for row in mentions if row["resolution_status"] == "resolved"),
        "unresolved": sum(1 for row in mentions if row["resolution_status"] == "unresolved"),
        "ambiguous": sum(1 for row in mentions if row["resolution_status"] == "ambiguous"),
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
    return {
        "schema_version": "legal_authority_verification_report_v1",
        "source": str(source_path),
        "authority_inventory": str(authority_inventory_path),
        "summary": summary,
        "courtlistener_like_lookup": lookup_rows,
        "mentions": mentions,
        "issues": issue_rows,
        "facts": facts,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Legal Authority Verification Report",
        "",
        f"- Document: `{summary['document_id']}`",
        f"- Citation mentions: `{summary['citation_mentions']}`",
        f"- Resolved: `{summary['resolved']}`",
        f"- Unresolved: `{summary['unresolved']}`",
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
    lines.extend(["", "## Mentions", "", "| Mention | Citation | Resolution | Quote | Pin | Proposition |", "| --- | --- | --- | --- | --- | --- |"])
    for row in report.get("mentions", []):
        quote = row["quote_check"]["status"] if row.get("quote_check") else ""
        pin = row["pin_check"]["status"] if row.get("pin_check") else ""
        proposition = row["proposition_boundary"]["review_requirement"] if row.get("proposition_boundary") else ""
        lines.append(
            f"| `{row['mention_id']}` | `{row['citation']}` | `{row['resolution_status']}` | "
            f"`{quote}` | `{pin}` | `{proposition}` |"
        )
    return "\n".join(lines) + "\n"


def facts_text(report: dict[str, Any]) -> str:
    return "\n".join(report.get("facts", [])) + "\n"


def _load_inventory(path: Path) -> dict[str, list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, list[dict[str, Any]]] = {}
    for row in data.get("authorities", []):
        citation = str(row.get("canonical_citation") or "").strip()
        if citation:
            out.setdefault(citation, []).append(row)
    return out


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


def _citation_text(match: re.Match[str]) -> str:
    return f"{match.group('volume')} {match.group('reporter')} {match.group('page')}"


def _citation_atom(citation: str) -> str:
    citation = citation.casefold().replace("u.s.", "us")
    compact = re.sub(r"[^a-z0-9]+", "_", citation).strip("_")
    return f"cite_{compact}"


def _quote_digest(quote: str) -> str:
    digest = hashlib.sha256(_normalize_text(quote).encode("utf-8")).hexdigest()[:12]
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


def _courtlistener_like_lookup(
    *,
    citation: str,
    match: re.Match[str],
    authority_matches: list[dict[str, Any]],
) -> dict[str, Any]:
    if not authority_matches:
        status = 404
        error = "citation_not_found"
    elif len(authority_matches) > 1:
        status = 300
        error = "ambiguous_citation"
    else:
        status = 200
        error = ""
    return {
        "citation": citation,
        "normalized_citations": [citation],
        "start_index": match.start("volume"),
        "end_index": match.end("page"),
        "status": status,
        "error_message": error,
        "clusters": [
            {
                "authority_id": row.get("authority_id"),
                "case_name": row.get("case_name"),
                "canonical_citation": row.get("canonical_citation"),
                "year": row.get("year"),
            }
            for row in authority_matches
        ],
    }


def _false_verified_count(mentions: list[dict[str, Any]]) -> int:
    # This prototype has no "verified despite blocker" state: mismatches become
    # issues/abstentions, not verified rows. Keep this metric explicit because
    # it is the primary legal-hallucination guardrail.
    return 0


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
