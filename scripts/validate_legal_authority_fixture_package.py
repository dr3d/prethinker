#!/usr/bin/env python3
"""Validate returned legal-authority verification fixture packages.

This is an intake gate for clean public legal filing batches. It reads package
control/oracle files, local authority inventories, and the deterministic legal
authority verifier output. It does not call an LLM or live legal resolver.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.carrier_contract_registry import carrier_contract  # noqa: E402
from src.legal_authority_verification import facts_text, verify_legal_authorities  # noqa: E402


FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
COMPACT_ATOM_RE = re.compile(r"^[a-z][a-z0-9_]*$")
REQUIRED_FIXTURE_FILES = {
    "source.md",
    "source_metadata.json",
    "authority_inventory.json",
    "expected_facts.pl",
    "forbidden_facts.pl",
    "manifest.json",
    "review_notes.md",
}
REQUIRED_AUTHORITY_FIELDS = {
    "authority_id",
    "canonical_citation",
    "case_name",
    "court",
    "year",
    "reporter",
    "volume",
    "page",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Returned fixture package directory or zip.")
    parser.add_argument("--fixture-class", default="clean_public_filings")
    parser.add_argument("--expected-fixture-count", type=int, default=3)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        package_path=args.package,
        fixture_class=args.fixture_class,
        expected_fixture_count=args.expected_fixture_count,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    failed = report["summary"]["blocking_errors"] > 0
    return 0 if args.exit_zero or not failed else 1


def build_report(
    *,
    package_path: Path,
    fixture_class: str = "clean_public_filings",
    expected_fixture_count: int = 3,
) -> dict[str, Any]:
    package_path = _resolve(package_path)
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    errors: list[str] = []
    try:
        if package_path.is_file() and package_path.suffix.casefold() == ".zip":
            temp_dir = tempfile.TemporaryDirectory(prefix="prethinker_legal_fixture_pkg_")
            extract_root = Path(temp_dir.name)
            errors.extend(_extract_zip_safely(package_path, extract_root))
            root = _payload_root(extract_root)
        else:
            root = _payload_root(package_path)
        fixture_dirs = _fixture_dirs(root)
        rows = [_audit_fixture(path, fixture_class=fixture_class) for path in fixture_dirs]
        if expected_fixture_count and len(rows) != expected_fixture_count:
            errors.append(f"fixture_count_expected_{expected_fixture_count}_got_{len(rows)}")
        blocking_rows = [row for row in rows if row["errors"]]
        summary = _aggregate(rows)
        summary.update(
            {
                "package": _display_path(package_path),
                "payload_root": _display_path(root),
                "fixture_class": fixture_class,
                "expected_fixture_count": expected_fixture_count,
                "fixture_count": len(rows),
                "package_errors": len(errors),
                "fixture_rows_with_errors": len(blocking_rows),
                "blocking_errors": len(errors) + len(blocking_rows),
                "status": "pass" if not errors and not blocking_rows else "fail",
            }
        )
        return {
            "schema": "prethinker.legal_authority_fixture_package_validation.v1",
            "summary": summary,
            "package_errors": errors,
            "fixtures": rows,
        }
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def _audit_fixture(path: Path, *, fixture_class: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    fixture_id = path.name
    present = {item.name for item in path.iterdir()} if path.exists() and path.is_dir() else set()
    missing = sorted(REQUIRED_FIXTURE_FILES - present)
    errors.extend(f"missing_{name}" for name in missing)

    manifest = _load_json(path / "manifest.json") if (path / "manifest.json").exists() else {}
    metadata = _load_json(path / "source_metadata.json") if (path / "source_metadata.json").exists() else {}
    inventory = _load_json(path / "authority_inventory.json") if (path / "authority_inventory.json").exists() else {}
    expected_facts = _load_fact_lines(path / "expected_facts.pl")
    forbidden_facts = _load_fact_lines(path / "forbidden_facts.pl")

    errors.extend(_manifest_errors(manifest, fixture_id=fixture_id, fixture_class=fixture_class))
    errors.extend(_metadata_errors(metadata, fixture_id=fixture_id))
    errors.extend(_inventory_errors(inventory))
    errors.extend(_fact_errors(expected_facts, label="expected_facts.pl"))
    errors.extend(_fact_errors(forbidden_facts, label="forbidden_facts.pl"))
    if fixture_class == "clean_public_filings":
        errors.extend(_clean_public_expected_fact_policy_errors(expected_facts))

    verifier_summary: dict[str, Any] = {}
    ledger_query_summary: dict[str, Any] = {}
    missing_expected: list[str] = []
    matched_forbidden: list[str] = []
    if not missing and (path / "source.md").exists() and (path / "authority_inventory.json").exists():
        report = verify_legal_authorities(
            source_path=path / "source.md",
            authority_inventory_path=path / "authority_inventory.json",
            document_id=fixture_id,
        )
        emitted = {line.strip() for line in facts_text(report).splitlines() if line.strip()}
        missing_expected = sorted(set(expected_facts) - emitted)
        matched_forbidden = sorted(set(forbidden_facts) & emitted)
        verifier_summary = dict(report.get("summary") or {})
        ledger_query_summary = _ledger_query_summary(dict(report.get("ledger_queries") or {}))
        if missing_expected:
            errors.append(f"missing_expected_facts:{len(missing_expected)}")
        if matched_forbidden:
            errors.append(f"matched_forbidden_facts:{len(matched_forbidden)}")
        if int(verifier_summary.get("false_verified", 0) or 0):
            errors.append(f"false_verified:{verifier_summary.get('false_verified')}")
        citation_mentions = int(verifier_summary.get("citation_mentions", 0) or 0)
        if citation_mentions < 3 or citation_mentions > 6:
            errors.append(f"citation_mentions_expected_3_to_6_got_{citation_mentions}")
        if int(verifier_summary.get("invalid_reporter", 0) or 0):
            errors.append(f"clean_public_fixture_has_invalid_reporter:{verifier_summary.get('invalid_reporter')}")
        quote_claims = int(verifier_summary.get("quote_claims", 0) or 0)
        if quote_claims < 1:
            errors.append("missing_quote_claim")
        mentions = list(report.get("mentions") or [])
        if not any(row.get("quote_check") and str(row.get("pin") or "").strip() for row in mentions):
            errors.append("missing_quoted_pin_cite")
        if not any(not row.get("quote_check") for row in mentions):
            errors.append("missing_no_quote_citation")
        if int(verifier_summary.get("review_required_mentions", 0) or 0):
            warnings.append("clean_public_fixture_contains_proposition_review_boundary")

    return {
        "fixture_id": fixture_id,
        "path": _display_path(path),
        "expected_fact_count": len(expected_facts),
        "missing_expected_facts": missing_expected,
        "forbidden_fact_count": len(forbidden_facts),
        "matched_forbidden_facts": matched_forbidden,
        "verifier_summary": verifier_summary,
        "ledger_query_summary": ledger_query_summary,
        "errors": errors,
        "warnings": warnings,
    }


def _manifest_errors(manifest: dict[str, Any], *, fixture_id: str, fixture_class: str) -> list[str]:
    errors: list[str] = []
    if str(manifest.get("fixture_id") or "").strip() != fixture_id:
        errors.append("manifest_fixture_id_mismatch")
    if str(manifest.get("domain_profile") or "").strip() != "legal_authority_verification_v1":
        errors.append("manifest_domain_profile_not_legal_authority_verification_v1")
    if fixture_class == "clean_public_filings" and str(manifest.get("source_kind") or "").strip() != "public_legal_filing_excerpt":
        errors.append("manifest_source_kind_not_public_legal_filing_excerpt")
    if str(manifest.get("claim_status") or "").strip() != "research_fixture_not_legal_advice":
        errors.append("manifest_claim_status_not_research_fixture_not_legal_advice")
    return errors


def _metadata_errors(metadata: dict[str, Any], *, fixture_id: str) -> list[str]:
    errors: list[str] = []
    if str(metadata.get("fixture_id") or "").strip() != fixture_id:
        errors.append("source_metadata_fixture_id_mismatch")
    for key in ("source_title", "source_url", "excerpt_method"):
        if not str(metadata.get(key) or "").strip():
            errors.append(f"source_metadata_missing_{key}")
    independence = metadata.get("oracle_independence")
    if not isinstance(independence, dict):
        errors.append("source_metadata_missing_oracle_independence")
    else:
        if bool(independence.get("used_model_output")):
            errors.append("oracle_independence_used_model_output_true")
        if str(independence.get("review_basis") or "").strip() != "source_and_authority_inventory_only":
            errors.append("oracle_independence_review_basis_not_source_and_authority_inventory_only")
    authority_sources = metadata.get("authority_sources")
    if not isinstance(authority_sources, list) or not authority_sources:
        errors.append("source_metadata_missing_authority_sources")
    return errors


def _inventory_errors(inventory: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if str(inventory.get("schema_version") or "").strip() != "legal_authority_inventory_v1":
        errors.append("authority_inventory_schema_version_not_legal_authority_inventory_v1")
    authorities = inventory.get("authorities")
    if not isinstance(authorities, list) or not authorities:
        return [*errors, "authority_inventory_missing_authorities"]
    seen_ids: set[str] = set()
    seen_citations: set[str] = set()
    for index, row in enumerate(authorities, start=1):
        if not isinstance(row, dict):
            errors.append(f"authority_{index}:not_object")
            continue
        missing = sorted(field for field in REQUIRED_AUTHORITY_FIELDS if not str(row.get(field) or "").strip())
        errors.extend(f"authority_{index}:missing_{field}" for field in missing)
        authority_id = str(row.get("authority_id") or "").strip()
        if authority_id and not COMPACT_ATOM_RE.match(authority_id):
            errors.append(f"authority_{index}:authority_id_not_compact")
        if authority_id in seen_ids:
            errors.append(f"authority_{index}:duplicate_authority_id:{authority_id}")
        seen_ids.add(authority_id)
        citation = str(row.get("canonical_citation") or "").strip()
        if citation in seen_citations:
            errors.append(f"authority_{index}:duplicate_canonical_citation:{citation}")
        seen_citations.add(citation)
        if str(row.get("reporter") or "").strip() != "U.S.":
            errors.append(f"authority_{index}:reporter_not_us")
        expected_citation = f"{row.get('volume', '')} {row.get('reporter', '')} {row.get('page', '')}".strip()
        if citation and citation != expected_citation:
            errors.append(f"authority_{index}:canonical_citation_slot_mismatch")
        pages = row.get("pages")
        if pages is not None and not isinstance(pages, dict):
            errors.append(f"authority_{index}:pages_not_object")
    return errors


def _fact_errors(facts: list[str], *, label: str) -> list[str]:
    errors: list[str] = []
    for line_number, fact in enumerate(facts, start=1):
        parsed = _parse_fact(fact)
        if parsed is None:
            errors.append(f"{label}:line_{line_number}:invalid_fact")
            continue
        signature = f"{parsed['predicate']}/{len(parsed['args'])}"
        if carrier_contract(signature) is None:
            errors.append(f"{label}:line_{line_number}:unregistered_signature:{signature}")
    return errors


def _clean_public_expected_fact_policy_errors(facts: list[str]) -> list[str]:
    errors: list[str] = []
    allowed_proposition_claim_status = {"detected_unreviewed", "human_review_required"}
    allowed_source_span_status = {
        "authority_unavailable",
        "human_review_required",
        "no_deterministic_span",
        "not_applicable",
    }
    for line_number, fact in enumerate(facts, start=1):
        parsed = _parse_fact(fact)
        if parsed is None:
            continue
        signature = f"{parsed['predicate']}/{len(parsed['args'])}"
        args = [str(arg).strip() for arg in parsed["args"]]
        if signature == "legal_support_assessment/5":
            errors.append(
                f"expected_facts.pl:line_{line_number}:tier2_support_assessment_not_allowed_clean_public"
            )
        elif signature == "legal_proposition_claim/5":
            review_status = args[4] if len(args) > 4 else ""
            if review_status not in allowed_proposition_claim_status:
                errors.append(
                    f"expected_facts.pl:line_{line_number}:proposition_claim_must_be_review_required_clean_public"
                )
        elif signature == "legal_proposition_source_span/5":
            span_status = args[3] if len(args) > 3 else ""
            if span_status not in allowed_source_span_status:
                errors.append(
                    f"expected_facts.pl:line_{line_number}:proposition_span_must_be_review_only_clean_public"
                )
        elif signature == "legal_proposition_support_boundary/5":
            boundary_status = args[2] if len(args) > 2 else ""
            review_requirement = args[3] if len(args) > 3 else ""
            if boundary_status != "deterministic_abstain" or review_requirement != "human_review_required":
                errors.append(
                    f"expected_facts.pl:line_{line_number}:proposition_boundary_must_abstain_clean_public"
                )
    return errors


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, int]:
    totals = {
        "expected_fact_count": 0,
        "matched_expected_fact_count": 0,
        "forbidden_fact_count": 0,
        "matched_forbidden_fact_count": 0,
        "citation_mentions": 0,
        "verified_mentions": 0,
        "blocked_mentions": 0,
        "review_required_mentions": 0,
        "quote_claims": 0,
        "quote_mismatch": 0,
        "pin_mismatch": 0,
        "authority_text_sources": 0,
        "authority_text_available_sources": 0,
        "authority_text_unavailable_sources": 0,
        "false_verified": 0,
    }
    for row in rows:
        expected = int(row.get("expected_fact_count", 0) or 0)
        missing = len(row.get("missing_expected_facts") or [])
        totals["expected_fact_count"] += expected
        totals["matched_expected_fact_count"] += expected - missing
        totals["forbidden_fact_count"] += int(row.get("forbidden_fact_count", 0) or 0)
        totals["matched_forbidden_fact_count"] += len(row.get("matched_forbidden_facts") or [])
        summary = row.get("verifier_summary") or {}
        for key in (
            "citation_mentions",
            "verified_mentions",
            "blocked_mentions",
            "review_required_mentions",
            "quote_claims",
            "quote_mismatch",
            "pin_mismatch",
            "authority_text_sources",
            "authority_text_available_sources",
            "authority_text_unavailable_sources",
            "false_verified",
        ):
            totals[key] += int(summary.get(key, 0) or 0)
    return totals


def _ledger_query_summary(queries: dict[str, Any]) -> dict[str, Any]:
    clean = queries.get("can_this_filing_be_certified_citation_clean") or {}
    return {
        "certification_answer": clean.get("answer", ""),
        "citation_clean": bool(clean.get("citation_clean", False)),
        "blocking_issue_count": int(clean.get("blocking_issue_count", 0) or 0),
        "review_required_count": int(clean.get("review_required_count", 0) or 0),
        "authority_text_sources": len(queries.get("which_authority_text_sources_were_used") or []),
        "authority_text_unavailable": len(queries.get("which_authority_text_is_unavailable") or []),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Legal Authority Fixture Package Validation",
        "",
        f"- Package: `{summary['package']}`",
        f"- Payload root: `{summary['payload_root']}`",
        f"- Fixture class: `{summary['fixture_class']}`",
        f"- Fixtures: `{summary['fixture_count']} / expected {summary['expected_fixture_count']}`",
        f"- Expected facts: `{summary['matched_expected_fact_count']} / {summary['expected_fact_count']}`",
        f"- Matched forbidden facts: `{summary['matched_forbidden_fact_count']} / {summary['forbidden_fact_count']}`",
        f"- Citation mentions: `{summary['citation_mentions']}`",
        f"- Verified / blocked / review-required mentions: `{summary['verified_mentions']} / {summary['blocked_mentions']} / {summary['review_required_mentions']}`",
        f"- Quote claims / quote mismatches: `{summary['quote_claims']} / {summary['quote_mismatch']}`",
        f"- Pin mismatches: `{summary['pin_mismatch']}`",
        f"- Authority text sources: `{summary['authority_text_sources']}`",
        f"- Authority text available / unavailable sources: `{summary['authority_text_available_sources']} / {summary['authority_text_unavailable_sources']}`",
        f"- False verified: `{summary['false_verified']}`",
        f"- Blocking errors: `{summary['blocking_errors']}`",
        f"- Status: `{summary['status']}`",
        "",
        "## Fixtures",
        "",
        "| Fixture | Expected | Forbidden matched | False verified | Certification | Errors | Warnings |",
        "| --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in report.get("fixtures", []):
        verifier = row.get("verifier_summary") or {}
        query = row.get("ledger_query_summary") or {}
        expected = int(row.get("expected_fact_count", 0) or 0)
        missing = len(row.get("missing_expected_facts") or [])
        lines.append(
            "| `{}` | {}/{} | {} | {} | `{}` | `{}` | `{}` |".format(
                row.get("fixture_id", ""),
                expected - missing,
                expected,
                len(row.get("matched_forbidden_facts") or []),
                verifier.get("false_verified", 0),
                query.get("certification_answer", ""),
                row.get("errors", []),
                row.get("warnings", []),
            )
        )
    if report.get("package_errors"):
        lines.extend(["", "## Package Errors", ""])
        lines.extend(f"- `{error}`" for error in report["package_errors"])
    return "\n".join(lines) + "\n"


def _extract_zip_safely(zip_path: Path, dest: Path) -> list[str]:
    errors: list[str] = []
    try:
        with zipfile.ZipFile(zip_path) as archive:
            for entry in archive.infolist():
                name = entry.filename.replace("\\", "/")
                if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
                    errors.append(f"unsafe_zip_entry_absolute:{entry.filename}")
                    continue
                parts = [part for part in name.split("/") if part]
                if ".." in parts:
                    errors.append(f"unsafe_zip_entry_traversal:{entry.filename}")
                    continue
                target = (dest / name).resolve()
                if not str(target).startswith(str(dest.resolve())):
                    errors.append(f"unsafe_zip_entry_escape:{entry.filename}")
                    continue
                if entry.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(entry) as source, target.open("wb") as sink:
                        shutil.copyfileobj(source, sink)
    except zipfile.BadZipFile:
        errors.append("zip_read_error:bad_zip_file")
    return errors


def _payload_root(path: Path) -> Path:
    if not path.exists() or not path.is_dir():
        return path
    if _fixture_dirs(path):
        return path
    children = [child for child in path.iterdir() if child.is_dir()]
    if len(children) == 1:
        return children[0]
    return path


def _fixture_dirs(path: Path) -> list[Path]:
    if not path.exists() or not path.is_dir():
        return []
    return sorted(
        child
        for child in path.iterdir()
        if child.is_dir() and (child / "source.md").exists() and (child / "manifest.json").exists()
    )


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


def _parse_fact(fact: str) -> dict[str, Any] | None:
    match = FACT_RE.match(fact)
    if not match:
        return None
    return {"predicate": match.group(1), "args": _split_args(match.group(2))}


def _split_args(text: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        if char in "([":
            depth += 1
        elif char in ")]" and depth:
            depth -= 1
        current.append(char)
    if current or text.strip():
        args.append("".join(current).strip())
    return args


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
