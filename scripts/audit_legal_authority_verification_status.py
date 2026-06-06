#!/usr/bin/env python3
"""Audit legal-authority verification fixtures and metrics.

This check is deterministic: it reads only fixture files, local authority
inventories, and expected/forbidden fact oracles. It does not call an LLM or a
live legal resolver. The primary gate is false_verified=0, with expected facts
present and forbidden facts absent for every runnable fixture.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.report_freshness import apply_markdown_freshness_check  # noqa: E402
from src.legal_authority_verification import facts_text, verify_legal_authorities  # noqa: E402


DEFAULT_MANIFEST = REPO_ROOT / "datasets" / "legal_authority_verification" / "fixture_corpus_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--expect-md", type=Path)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(manifest_path=args.manifest)
    rendered_md = render_markdown(report)
    if args.expect_md:
        apply_markdown_freshness_check(report=report, expected_path=args.expect_md, rendered_md=rendered_md)
        rendered_md = render_markdown(report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(rendered_md, encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    failed = report["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not failed else 1


def build_report(*, manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    manifest_path = _resolve(manifest_path)
    manifest = _load_json(manifest_path)
    rows: list[dict[str, Any]] = []
    class_rows: list[dict[str, Any]] = []
    for fixture_class in manifest.get("fixture_classes", []):
        if not isinstance(fixture_class, dict):
            continue
        class_id = str(fixture_class.get("id") or "").strip()
        fixtures = [str(item).strip() for item in fixture_class.get("fixtures", []) if str(item).strip()]
        class_rows.append(
            {
                "id": class_id,
                "status": str(fixture_class.get("status") or "").strip(),
                "fixture_count": len(fixtures),
            }
        )
        for fixture_path_text in fixtures:
            rows.append(_audit_fixture(class_id=class_id, fixture_path=_resolve(Path(fixture_path_text))))

    totals = _aggregate_rows(rows)
    blocking_rows = [row for row in rows if row["errors"]]
    return {
        "schema": "prethinker.legal_authority_verification_status.v1",
        "manifest": _display_path(manifest_path),
        "claim_boundary": manifest.get("claim_boundary", {}),
        "fixture_classes": class_rows,
        "next_external_work_order_needed": manifest.get("next_external_work_order_needed", {}),
        "summary": {
            **totals,
            "blocking_rows": len(blocking_rows),
            "status": "pass" if not blocking_rows else "fail",
            "blocking_reasons": [error for row in rows for error in row["errors"]],
        },
        "fixtures": rows,
    }


def _audit_fixture(*, class_id: str, fixture_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    fixture_manifest_path = fixture_path / "manifest.json"
    fixture_manifest = _load_json(fixture_manifest_path) if fixture_manifest_path.exists() else {}
    fixture_id = str(fixture_manifest.get("fixture_id") or fixture_path.name).strip()
    source_path = fixture_path / _manifest_file(fixture_manifest, "source", default="source.md")
    inventory_path = fixture_path / "authority_inventory.json"
    expected_path = fixture_path / _manifest_file(fixture_manifest, "expected_facts", default="expected_facts.pl")
    forbidden_path = fixture_path / _manifest_file(fixture_manifest, "forbidden_facts", default="forbidden_facts.pl")

    for label, path in (
        ("manifest", fixture_manifest_path),
        ("source", source_path),
        ("authority_inventory", inventory_path),
        ("expected_facts", expected_path),
        ("forbidden_facts", forbidden_path),
    ):
        if not path.exists():
            errors.append(f"{fixture_id}:missing_{label}:{_display_path(path)}")

    expected_facts = _load_fact_lines(expected_path)
    forbidden_facts = _load_fact_lines(forbidden_path)
    document_id = str(fixture_manifest.get("document_id") or "").strip()
    if not document_id:
        document_id = _document_id_from_expected(expected_facts) or fixture_id
    emitted_facts: set[str] = set()
    verifier_summary: dict[str, Any] = {}
    ledger_queries: dict[str, Any] = {}
    if not errors:
        report = verify_legal_authorities(
            source_path=source_path,
            authority_inventory_path=inventory_path,
            document_id=document_id,
        )
        emitted_facts = {line.strip() for line in facts_text(report).splitlines() if line.strip()}
        verifier_summary = dict(report.get("summary") or {})
        ledger_queries = dict(report.get("ledger_queries") or {})

    matched_expected = sorted(set(expected_facts) & emitted_facts)
    missing_expected = sorted(set(expected_facts) - emitted_facts)
    matched_forbidden = sorted(set(forbidden_facts) & emitted_facts)
    if missing_expected:
        errors.append(f"{fixture_id}:missing_expected_facts:{len(missing_expected)}")
    if matched_forbidden:
        errors.append(f"{fixture_id}:matched_forbidden_facts:{len(matched_forbidden)}")
    if int(verifier_summary.get("false_verified", 0) or 0):
        errors.append(f"{fixture_id}:false_verified:{verifier_summary.get('false_verified')}")

    return {
        "class_id": class_id,
        "fixture_id": fixture_id,
        "document_id": document_id,
        "path": _display_path(fixture_path),
        "expected_fact_count": len(expected_facts),
        "matched_expected_fact_count": len(expected_facts) - len(missing_expected),
        "missing_expected_facts": missing_expected,
        "forbidden_fact_count": len(forbidden_facts),
        "matched_forbidden_facts": matched_forbidden,
        "fact_signature_summary": _fact_signature_summary(
            expected_facts=expected_facts,
            matched_expected_facts=matched_expected,
            forbidden_facts=forbidden_facts,
            matched_forbidden_facts=matched_forbidden,
        ),
        "verifier_summary": verifier_summary,
        "ledger_query_summary": _ledger_query_summary(ledger_queries),
        "errors": errors,
    }


def _aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {
        "fixture_count": len(rows),
        "expected_fact_count": 0,
        "matched_expected_fact_count": 0,
        "forbidden_fact_count": 0,
        "matched_forbidden_fact_count": 0,
        "citation_mentions": 0,
        "verified_mentions": 0,
        "blocked_mentions": 0,
        "review_required_mentions": 0,
        "resolved": 0,
        "unresolved": 0,
        "ambiguous": 0,
        "invalid_reporter": 0,
        "metadata_checks": 0,
        "metadata_match": 0,
        "metadata_mismatch": 0,
        "quote_claims": 0,
        "quote_exact_or_normalized_match": 0,
        "quote_mismatch": 0,
        "pin_mismatch": 0,
        "authority_text_sources": 0,
        "authority_text_available_sources": 0,
        "authority_text_unavailable_sources": 0,
        "short_form_citations": 0,
        "proposition_boundaries": 0,
        "verification_abstentions": 0,
        "false_verified": 0,
    }
    signature_totals: dict[str, dict[str, int]] = {}
    for row in rows:
        totals["expected_fact_count"] += int(row.get("expected_fact_count", 0))
        totals["matched_expected_fact_count"] += int(row.get("matched_expected_fact_count", 0))
        totals["forbidden_fact_count"] += int(row.get("forbidden_fact_count", 0))
        totals["matched_forbidden_fact_count"] += len(row.get("matched_forbidden_facts") or [])
        summary = row.get("verifier_summary") or {}
        for signature_row in row.get("fact_signature_summary") or []:
            signature = str(signature_row.get("signature") or "").strip()
            if not signature:
                continue
            bucket = signature_totals.setdefault(
                signature,
                {
                    "expected": 0,
                    "matched_expected": 0,
                    "forbidden": 0,
                    "matched_forbidden": 0,
                },
            )
            for key in ("expected", "matched_expected", "forbidden", "matched_forbidden"):
                bucket[key] += int(signature_row.get(key, 0) or 0)
        for key in (
            "citation_mentions",
            "verified_mentions",
            "blocked_mentions",
            "review_required_mentions",
            "resolved",
            "unresolved",
            "ambiguous",
            "invalid_reporter",
            "metadata_checks",
            "metadata_match",
            "metadata_mismatch",
            "quote_claims",
            "quote_exact_or_normalized_match",
            "quote_mismatch",
            "pin_mismatch",
            "authority_text_sources",
            "authority_text_available_sources",
            "authority_text_unavailable_sources",
            "short_form_citations",
            "proposition_boundaries",
            "verification_abstentions",
            "false_verified",
        ):
            totals[key] += int(summary.get(key, 0) or 0)
    totals["fact_signature_summary"] = [
        {"signature": signature, **counts}
        for signature, counts in sorted(signature_totals.items())
    ]
    return totals


def _ledger_query_summary(ledger_queries: dict[str, Any]) -> dict[str, Any]:
    clean = ledger_queries.get("can_this_filing_be_certified_citation_clean") or {}
    return {
        "certification_answer": clean.get("answer", ""),
        "citation_clean": bool(clean.get("citation_clean", False)),
        "blocking_issue_count": int(clean.get("blocking_issue_count", 0) or 0),
        "review_required_count": int(clean.get("review_required_count", 0) or 0),
        "unresolved_or_ambiguous": len(ledger_queries.get("which_citations_do_not_resolve") or []),
        "metadata_mismatches": len(ledger_queries.get("which_cases_have_metadata_mismatches") or []),
        "quote_mismatches": len(ledger_queries.get("which_quotes_cannot_be_found") or []),
        "authority_text_unavailable": len(ledger_queries.get("which_authority_text_is_unavailable") or []),
        "authority_text_sources": len(ledger_queries.get("which_authority_text_sources_were_used") or []),
        "short_form_context_required": len(ledger_queries.get("which_citations_require_context") or []),
        "pin_mismatches": len(ledger_queries.get("which_pin_cites_do_not_contain_the_quote") or []),
        "propositions_requiring_review": len(ledger_queries.get("which_propositions_require_human_review") or []),
        "proposition_authority_links": len(ledger_queries.get("which_authorities_are_attached_to_propositions") or []),
    }


def _fact_signature_summary(
    *,
    expected_facts: list[str],
    matched_expected_facts: list[str],
    forbidden_facts: list[str],
    matched_forbidden_facts: list[str],
) -> list[dict[str, Any]]:
    expected = _signature_counts(expected_facts)
    matched_expected = _signature_counts(matched_expected_facts)
    forbidden = _signature_counts(forbidden_facts)
    matched_forbidden = _signature_counts(matched_forbidden_facts)
    signatures = sorted(set(expected) | set(matched_expected) | set(forbidden) | set(matched_forbidden))
    return [
        {
            "signature": signature,
            "expected": expected.get(signature, 0),
            "matched_expected": matched_expected.get(signature, 0),
            "forbidden": forbidden.get(signature, 0),
            "matched_forbidden": matched_forbidden.get(signature, 0),
        }
        for signature in signatures
    ]


def _signature_counts(facts: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for fact in facts:
        signature = _fact_signature(fact)
        if signature:
            counts[signature] = counts.get(signature, 0) + 1
    return counts


def _fact_signature(fact: str) -> str:
    head, open_paren, rest = fact.partition("(")
    if not open_paren:
        return ""
    args_text = rest.rsplit(")", 1)[0]
    arity = 0 if not args_text.strip() else len([arg for arg in args_text.split(",")])
    return f"{head.strip()}/{arity}"


def _document_id_from_expected(expected_facts: list[str]) -> str:
    for fact in expected_facts:
        prefix = "legal_citation_mention("
        if not fact.startswith(prefix):
            continue
        args = fact[len(prefix) :].split(")", 1)[0].split(",")
        if args:
            return args[0].strip()
    return ""


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Legal Authority Verification Status",
        "",
        "This generated report runs the deterministic legal-authority verifier over fixture-manifest entries.",
        "It reads local fixture files and authority inventories only; it does not call an LLM or live legal resolver.",
        "",
        f"- Manifest: `{report.get('manifest', '')}`",
        f"- Fixtures: `{summary['fixture_count']}`",
        f"- Expected facts: `{summary['matched_expected_fact_count']} / {summary['expected_fact_count']}`",
        f"- Matched forbidden facts: `{summary['matched_forbidden_fact_count']} / {summary['forbidden_fact_count']}`",
        f"- Citation mentions: `{summary['citation_mentions']}`",
        f"- Verified / blocked / review-required mentions: `{summary['verified_mentions']} / {summary['blocked_mentions']} / {summary['review_required_mentions']}`",
        f"- Resolved / unresolved / ambiguous / invalid reporter: `{summary['resolved']} / {summary['unresolved']} / {summary['ambiguous']} / {summary['invalid_reporter']}`",
        f"- Metadata checks / matches / mismatches: `{summary['metadata_checks']} / {summary['metadata_match']} / {summary['metadata_mismatch']}`",
        f"- Quote claims / quote matches / quote mismatches: `{summary['quote_claims']} / {summary['quote_exact_or_normalized_match']} / {summary['quote_mismatch']}`",
        f"- Pin mismatches: `{summary['pin_mismatch']}`",
        f"- Authority text sources: `{summary['authority_text_sources']}`",
        f"- Authority text available / unavailable sources: `{summary['authority_text_available_sources']} / {summary['authority_text_unavailable_sources']}`",
        f"- Short-form citations requiring context: `{summary['short_form_citations']}`",
        f"- Proposition boundaries: `{summary['proposition_boundaries']}`",
        f"- Verification abstentions: `{summary['verification_abstentions']}`",
        f"- False verified: `{summary['false_verified']}`",
        f"- Blocking rows: `{summary['blocking_rows']}`",
        f"- Status: `{summary['status']}`",
        "",
        "## Fact Signature Coverage",
        "",
        "| Signature | Expected matched/total | Forbidden matched/total |",
        "| --- | ---: | ---: |",
    ]
    for row in summary.get("fact_signature_summary") or []:
        lines.append(
            "| `{}` | {}/{} | {}/{} |".format(
                row.get("signature", ""),
                row.get("matched_expected", 0),
                row.get("expected", 0),
                row.get("matched_forbidden", 0),
                row.get("forbidden", 0),
            )
        )
    lines.extend(
        [
            "",
        "## Fixture Classes",
        "",
        "| Class | Status | Fixtures |",
        "| --- | --- | ---: |",
    ]
    )
    for row in report.get("fixture_classes", []):
        lines.append(f"| `{row['id']}` | `{row['status']}` | {row['fixture_count']} |")
    lines.extend(
        [
            "",
            "## Fixture Results",
            "",
            "| Fixture | Class | Expected | Forbidden matched | False verified | Mentions verified/blocked/review | Certification | Errors |",
            "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in report.get("fixtures", []):
        verifier = row.get("verifier_summary") or {}
        query = row.get("ledger_query_summary") or {}
        mentions = "{}/{}/{}".format(
            verifier.get("verified_mentions", 0),
            verifier.get("blocked_mentions", 0),
            verifier.get("review_required_mentions", 0),
        )
        lines.append(
            "| `{}` | `{}` | {}/{} | {} | {} | `{}` | `{}` | `{}` |".format(
                row.get("fixture_id", ""),
                row.get("class_id", ""),
                row.get("matched_expected_fact_count", 0),
                row.get("expected_fact_count", 0),
                len(row.get("matched_forbidden_facts") or []),
                verifier.get("false_verified", 0),
                mentions,
                query.get("certification_answer", ""),
                row.get("errors", []),
            )
        )
    work_order = report.get("next_external_work_order_needed") or {}
    if work_order:
        lines.extend(
            [
                "",
                "## Next External Work Order",
                "",
                f"- Needed now: `{work_order.get('needed_now', '')}`",
                f"- Reason: {work_order.get('reason', '')}",
            ]
        )
    return "\n".join(lines) + "\n"


def _manifest_file(manifest: dict[str, Any], key: str, *, default: str) -> str:
    value = manifest.get(key)
    if str(value or "").strip():
        return str(value).strip()
    files = manifest.get("files")
    if isinstance(files, dict) and str(files.get(key) or "").strip():
        return str(files[key]).strip()
    return default


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _load_fact_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("%")]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
