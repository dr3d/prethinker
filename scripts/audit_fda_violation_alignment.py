#!/usr/bin/env python3
"""Audit FDA violation/category/citation alignment without mutating facts."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_domain_bootstrap_file import _parse_fact_clause


CITATION_CATEGORY = {
    "cfr_21_211_68_b": "data_integrity",
    "cfr_21_211_113_b": "contamination_control",
    "cfr_21_211_42_c_10_iv": "facility_equipment_control",
    "cfr_21_211_192": "investigation_failure",
    "cfr_21_211_100_a": "process_validation",
    "cfr_21_211_110_a": "process_validation",
}
ALLOWED_CGMP_CITATIONS = {
    *CITATION_CATEGORY.keys(),
    "cfr_21_211_42_c_10_v",
}


def _is_numbered_violation_atom(value: str) -> bool:
    prefix = "violation_"
    if not value.startswith(prefix):
        return False
    tail = value[len(prefix) :]
    return bool(tail) and tail.isdigit()


def _numbered_violation_index(value: str) -> int | None:
    if not _is_numbered_violation_atom(value):
        return None
    try:
        return int(value.split("_", 1)[1])
    except (IndexError, ValueError):
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-json", action="append", type=Path, default=[])
    parser.add_argument("--compile-root", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--expect-md", type=Path)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def _compile_paths(args: argparse.Namespace) -> list[Path]:
    paths = [path for path in args.compile_json if path]
    if args.compile_root:
        paths.extend(sorted(args.compile_root.rglob("domain_bootstrap_file_*.json")))
        paths.extend(sorted(args.compile_root.rglob("union.json")))
    return sorted({path.resolve() for path in paths if path.exists()})


def _facts_from_payload(payload: dict[str, Any]) -> list[str]:
    source_compile = payload.get("source_compile")
    if isinstance(source_compile, dict):
        return [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    return []


def _fixture_id(path: Path, payload: dict[str, Any]) -> str:
    text_file = str(payload.get("text_file") or "").replace("\\", "/").rstrip("/")
    if text_file:
        text_path = Path(text_file)
        if text_path.name == "source.md":
            return text_path.parent.name
        return text_path.name
    return path.parent.name


def audit_facts(*, facts: list[str], fixture: str, path: str = "") -> dict[str, Any]:
    violations: dict[str, list[dict[str, str]]] = defaultdict(list)
    citations: dict[str, list[dict[str, str]]] = defaultdict(list)
    authority_citations: dict[str, list[dict[str, str]]] = defaultdict(list)
    bundles: dict[str, list[dict[str, str]]] = defaultdict(list)
    response_assessments: dict[str, list[dict[str, str]]] = defaultdict(list)
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate == "fda_cgmp_violation_item" and len(args) == 5:
            bundles[args[0]].append(
                {
                    "fact": fact,
                    "violation_id": args[0],
                    "letter_id": args[1],
                    "violation_number": args[2],
                    "citation": args[3],
                }
            )
        elif predicate == "fda_violation" and len(args) == 5:
            violations[args[0]].append(
                {
                    "fact": fact,
                    "violation_id": args[0],
                    "letter_id": args[1],
                    "violation_number": args[2],
                    "violation_category": args[3],
                }
            )
        elif predicate == "fda_violation_citation" and len(args) == 4 and args[2] == "cgmps_requirement":
            citations[args[0]].append(
                {
                    "fact": fact,
                    "violation_id": args[0],
                    "citation": args[1],
                    "expected_category": CITATION_CATEGORY.get(args[1], ""),
                }
            )
        elif (
            predicate == "fda_violation_citation"
            and len(args) == 4
            and args[2] == "adulteration_authority"
            and args[1] in {"fdca_501_a_2_a", "fdca_501_a_2_b"}
        ):
            authority_citations[args[0]].append(
                {
                    "fact": fact,
                    "subject_id": args[0],
                    "citation": args[1],
                }
            )
        elif predicate == "fda_response_assessment" and len(args) == 5:
            response_assessments[args[1]].append(
                {
                    "fact": fact,
                    "assessment_id": args[0],
                    "violation_id": args[1],
                    "assessment_kind": args[2],
                    "assessment_scope": args[3],
                }
            )

    findings: list[dict[str, str]] = []
    unstable_violation_ids: set[str] = set()

    numbered_subjects = {
        value
        for value in [*violations.keys(), *citations.keys(), *bundles.keys()]
        if _is_numbered_violation_atom(value)
    }
    numbered_indexes = sorted(
        index for index in (_numbered_violation_index(value) for value in numbered_subjects) if index is not None
    )
    if numbered_indexes and numbered_indexes[0] != 1:
        findings.append(
            {
                "fixture": fixture,
                "issue": "numbered_violation_sequence_does_not_start_at_one",
                "violation_id": ", ".join(sorted(numbered_subjects)),
                "detail": f"lowest_numbered_violation={numbered_indexes[0]}",
            }
        )
    if numbered_indexes:
        expected_indexes = set(range(numbered_indexes[0], numbered_indexes[-1] + 1))
        missing_indexes = sorted(expected_indexes - set(numbered_indexes))
        if missing_indexes:
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "numbered_violation_sequence_gap",
                    "violation_id": ", ".join(sorted(numbered_subjects)),
                    "detail": "missing=" + ", ".join(f"violation_{item}" for item in missing_indexes),
                }
            )

    for violation_id, rows in sorted(bundles.items()):
        citation_values = sorted({row["citation"] for row in rows})
        if not _is_numbered_violation_atom(violation_id) or {row["violation_number"] for row in rows} != {violation_id}:
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "cgmp_bundle_key_mismatch",
                    "violation_id": violation_id,
                    "facts": " | ".join(row["fact"] for row in rows[:5]),
                }
            )
        if len(citation_values) > 1:
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "cgmp_bundle_ambiguous_citations",
                    "violation_id": violation_id,
                    "citation": ", ".join(citation_values),
                    "facts": " | ".join(row["fact"] for row in rows[:5]),
                }
            )
        for row in rows:
            if row["citation"] not in ALLOWED_CGMP_CITATIONS:
                findings.append(
                    {
                        "fixture": fixture,
                        "issue": "cgmp_bundle_unmapped_citation",
                        "violation_id": violation_id,
                        "citation": row["citation"],
                        "fact": row["fact"],
                    }
                )

    for violation_id, rows in sorted(violations.items()):
        numbered_rows = [row for row in rows if _is_numbered_violation_atom(row["violation_number"])]
        numbered_values = sorted({row["violation_number"] for row in numbered_rows})
        if len(numbered_values) > 1:
            unstable_violation_ids.add(violation_id)
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "duplicate_violation_id_multiple_numbers",
                    "violation_id": violation_id,
                    "violation_numbers": ", ".join(numbered_values),
                    "facts": " | ".join(item["fact"] for item in numbered_rows[:5]),
                }
            )
        for row in numbered_rows:
            if row["violation_id"] != row["violation_number"]:
                unstable_violation_ids.add(row["violation_id"])
                findings.append(
                    {
                        "fixture": fixture,
                        "issue": "violation_id_not_numbered_key",
                        "violation_id": row["violation_id"],
                        "expected_violation_id": row["violation_number"],
                        "fact": row["fact"],
                    }
                )

    for violation_id, rows in sorted(violations.items()):
        linked_citations = citations.get(violation_id, [])
        mapped = [item for item in linked_citations if item["expected_category"]]
        mapped_categories = sorted({item["expected_category"] for item in mapped})
        if violation_id in unstable_violation_ids:
            continue
        if len(mapped_categories) > 1:
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "merged_citation_category_families",
                    "violation_id": violation_id,
                    "expected_categories": ", ".join(mapped_categories),
                    "facts": " | ".join(item["fact"] for item in mapped[:5]),
                }
            )
        for row in rows:
            for citation in mapped:
                if row["violation_category"] != citation["expected_category"]:
                    findings.append(
                        {
                            "fixture": fixture,
                            "issue": "category_citation_mismatch",
                            "violation_id": violation_id,
                            "violation_category": row["violation_category"],
                            "citation": citation["citation"],
                            "expected_category": citation["expected_category"],
                            "fact": row["fact"],
                        }
                    )
        if not linked_citations:
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "violation_without_specific_cgmp_citation",
                    "violation_id": violation_id,
                    "facts": " | ".join(item["fact"] for item in rows[:5]),
                }
            )

    for violation_id, linked_citations in sorted(citations.items()):
        if not _is_numbered_violation_atom(violation_id):
            unstable_violation_ids.add(violation_id)
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "cgmps_citation_subject_not_numbered_key",
                    "violation_id": violation_id,
                    "facts": " | ".join(item["fact"] for item in linked_citations[:5]),
                }
            )
        if violation_id not in violations:
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "citation_without_matching_violation_id",
                    "violation_id": violation_id,
                    "facts": " | ".join(item["fact"] for item in linked_citations[:5]),
                }
            )

    numbered_subjects_by_citation: dict[str, list[str]] = defaultdict(list)
    for violation_id, linked_citations in citations.items():
        if not _is_numbered_violation_atom(violation_id):
            continue
        for citation in linked_citations:
            numbered_subjects_by_citation[citation["citation"]].append(violation_id)
    for citation, subject_ids in sorted(numbered_subjects_by_citation.items()):
        unique_subjects = sorted(set(subject_ids))
        if len(unique_subjects) > 1:
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "cgmps_citation_reused_across_numbered_violations",
                    "violation_id": ", ".join(unique_subjects),
                    "citation": citation,
                }
            )
    bundle_subjects_by_citation: dict[str, list[str]] = defaultdict(list)
    for violation_id, rows in bundles.items():
        if not _is_numbered_violation_atom(violation_id):
            continue
        for row in rows:
            if row["citation"] in ALLOWED_CGMP_CITATIONS:
                bundle_subjects_by_citation[row["citation"]].append(violation_id)
    for citation, subject_ids in sorted(bundle_subjects_by_citation.items()):
        unique_subjects = sorted(set(subject_ids))
        if len(unique_subjects) > 1:
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "cgmp_bundle_citation_reused_across_numbered_violations",
                    "violation_id": ", ".join(unique_subjects),
                    "citation": citation,
                }
            )

    for subject_id, linked_citations in sorted(authority_citations.items()):
        if _is_numbered_violation_atom(subject_id):
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "adulteration_authority_attached_to_numbered_violation",
                    "violation_id": subject_id,
                    "facts": " | ".join(item["fact"] for item in linked_citations[:5]),
                }
            )

    for violation_id, rows in sorted(response_assessments.items()):
        if not _is_numbered_violation_atom(violation_id):
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "response_assessment_subject_not_numbered_key",
                    "violation_id": violation_id,
                    "facts": " | ".join(row["fact"] for row in rows[:5]),
                }
            )
        if violation_id not in bundles:
            findings.append(
                {
                    "fixture": fixture,
                    "issue": "response_assessment_without_matching_cgmp_bundle",
                    "violation_id": violation_id,
                    "facts": " | ".join(row["fact"] for row in rows[:5]),
                }
            )

    return {
        "fixture": fixture,
        "path": path,
        "facts": len(facts),
        "violation_ids": len(violations),
        "citation_subjects": len(citations),
        "finding_count": len(findings),
        "findings": findings,
    }


def audit_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return audit_facts(
        facts=_facts_from_payload(payload),
        fixture=_fixture_id(path, payload),
        path=str(path),
    )


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# FDA Violation Alignment Audit",
        "",
        f"- Compile artifacts: `{report['compile_count']}`",
        f"- Findings: `{report['finding_count']}`",
        f"- Status: `{'pass' if report['finding_count'] == 0 else 'hold'}`",
        "",
        "| Fixture | Issue | Violation | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["findings"]:
        detail = (
            item.get("detail")
            or item.get("citation")
            or item.get("expected_categories")
            or item.get("facts")
            or item.get("fact")
            or ""
        )
        lines.append(
            f"| `{item.get('fixture', '')}` | `{item.get('issue', '')}` | "
            f"`{item.get('violation_id', '')}` | `{detail}` |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    paths = _compile_paths(args)
    audits = [audit_payload(path) for path in paths]
    findings = [finding for audit in audits for finding in audit["findings"]]
    report = {
        "schema_version": "fda_violation_alignment_audit_v1",
        "policy": {
            "mutates_facts": False,
            "reads_source_prose": False,
            "reads_query_text": False,
            "description": (
                "Checks typed fda_violation/5 rows against typed fda_violation_citation/4 rows. "
                "It does not infer or repair facts."
            ),
        },
        "compile_count": len(audits),
        "finding_count": len(findings),
        "audits": audits,
        "findings": findings,
    }
    md = _markdown(report)
    expected_md_match = None
    if args.expect_md:
        expected_md_match = args.expect_md.exists() and args.expect_md.read_text(encoding="utf-8") == md
        report["expected_md_match"] = expected_md_match
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(md, encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.expect_md:
        return 0 if expected_md_match else 1
    return 0 if args.exit_zero or not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
