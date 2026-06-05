#!/usr/bin/env python3
"""Summarize typed micro-fixture support across repeated compile artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_typed_micro_fixtures import (  # noqa: E402
    DEFAULT_ROOT,
    _parse_fact,
    _facts_from_compile_json,
    _load_fact_lines,
    _match_expected_facts,
)
from scripts.run_domain_bootstrap_file import (  # noqa: E402
    _apply_active_lens_scope_integrity,
    _apply_domain_omission_carrier_signature_reduction,
    _apply_fda_adulteration_basis_authority_reduction,
    _apply_fda_consultant_citation_scope_reduction,
    _apply_fda_correspondence_party_name_reduction,
    _apply_fda_correspondence_party_role_integrity,
    _apply_fda_cgmp_violation_item_projection,
    _apply_fda_cgmp_bundle_subject_integrity,
    _apply_fda_date_atom_reduction,
    _apply_fda_facility_identity_atom_reduction,
    _apply_fda_facility_subject_convergence,
    _apply_fda_lot_identifier_atom_reduction,
    _apply_fda_no_fei_omission_reduction,
    _apply_fda_office_atom_reduction,
    _apply_fda_insanitary_adulteration_basis_support_integrity,
    _apply_fda_response_assessment_slot_projection,
    _apply_fda_response_assessment_scope_reduction,
    _apply_fda_response_documentation_gap_projection,
    _apply_fda_response_investigation_gap_projection,
    _apply_fda_response_assessment_item_projection,
    _apply_fda_response_assessment_id_canonicalization,
    _apply_fda_response_assessment_kind_citation_reduction,
    _apply_fda_response_assessment_specificity_reduction,
    _apply_fda_response_assessment_subject_integrity,
    _apply_fda_violation_detail_atom_reduction,
    _apply_fda_violation_detail_value_kind_integrity,
    _apply_fda_violation_detail_slot_projection,
    _apply_fda_violation_detail_subject_integrity,
    _apply_fda_violation_category_from_unique_citation_reduction,
    _apply_fda_violation_number_atom_reduction,
    _apply_fda_warning_letter_subject_convergence,
    _apply_ntsb_actor_id_atom_reduction,
    _apply_ntsb_condition_atom_reduction,
    _apply_ntsb_injury_count_scope_specificity,
    _apply_ntsb_report_omission_contradiction_integrity,
    _apply_ntsb_timestamp_atom_reduction,
    _apply_osha_accident_omission_contradiction_integrity,
    _apply_osha_inspection_omission_contradiction_integrity,
    _apply_registered_date_slot_atom_reduction,
    _apply_sec_exhibit_number_atom_reduction,
    _apply_sec_exhibit_treatment_specificity_integrity,
    _apply_sec_filing_id_atom_reduction,
    _apply_sec_identifier_value_atom_reduction,
    _apply_sec_signature_omission_contradiction_integrity,
    _apply_sec_typed_slot_prefix_reduction,
    _apply_state_ag_typed_atom_reduction,
    _apply_atom_shape_integrity,
    _apply_carrier_value_domain_integrity,
    _apply_domain_omission_registry_value_integrity,
    _apply_source_scope_payload_integrity,
    _enforce_fda_correspondence_party_placeholder_contract,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, help="Micro-fixture id under datasets/compile_micro_fixtures.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--compile-json", action="append", default=[], type=Path, required=True)
    parser.add_argument("--support-threshold", type=int, default=2)
    parser.add_argument(
        "--expected-signature",
        action="append",
        default=[],
        help=(
            "Restrict expected/forbidden facts to one or more predicate signatures such as "
            "fda_violation/5. May be repeated or comma-separated."
        ),
    )
    parser.add_argument(
        "--matcher",
        choices=("unification", "constant_slot"),
        default="unification",
        help=(
            "Support matcher. unification preserves the normal variable-binding "
            "matcher; constant_slot treats expected variables as floating IDs/source "
            "coordinates and requires only same-position expected constants."
        ),
    )
    parser.add_argument(
        "--apply-domain-reducers",
        action="store_true",
        help="Apply deterministic typed-domain reducers to each compile before measuring support.",
    )
    parser.add_argument(
        "--enforce-supported",
        action="store_true",
        help="Fail when any expected fact does not meet the support threshold.",
    )
    parser.add_argument(
        "--enforce-no-forbidden",
        action="store_true",
        help="Fail when any forbidden fact is supported by one or more compiles.",
    )
    parser.add_argument(
        "--report-unexpected",
        action="store_true",
        help=(
            "Report emitted facts in the selected signatures that match neither expected nor forbidden facts. "
            "This is a precision diagnostic, not a source-truth adjudication."
        ),
    )
    parser.add_argument(
        "--enforce-no-unexpected",
        action="store_true",
        help="Fail when --report-unexpected finds emitted same-signature facts outside the fixture oracle.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        fixture_id=str(args.fixture),
        root=args.root,
        compile_paths=[path.resolve() for path in args.compile_json],
        support_threshold=int(args.support_threshold),
        matcher=str(args.matcher),
        apply_domain_reducers=bool(args.apply_domain_reducers),
        expected_signatures=_parse_signature_filter(args.expected_signature),
        report_unexpected=bool(args.report_unexpected or args.enforce_no_unexpected),
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.exit_zero:
        return 0
    if not report["summary"]["compile_count"]:
        return 1
    if args.enforce_supported and report["summary"]["unsupported_fact_count"]:
        return 1
    if args.enforce_no_forbidden and report["summary"]["supported_forbidden_fact_count"]:
        return 1
    if args.enforce_no_unexpected and (report["summary"].get("unexpected_fact_count") or 0):
        return 1
    return 0


def build_report(
    *,
    fixture_id: str,
    root: Path = DEFAULT_ROOT,
    compile_paths: list[Path],
    support_threshold: int = 2,
    matcher: str = "unification",
    apply_domain_reducers: bool = False,
    expected_signatures: set[str] | None = None,
    report_unexpected: bool = False,
) -> dict[str, Any]:
    fixture_dir = root / fixture_id
    expected_path = fixture_dir / "expected_facts.pl"
    forbidden_path = fixture_dir / "forbidden_facts.pl"
    expected_facts = _load_fact_lines(expected_path)
    forbidden_facts = _load_fact_lines(forbidden_path) if forbidden_path.exists() else []
    signature_filter = {str(item).strip() for item in (expected_signatures or set()) if str(item).strip()}
    if signature_filter:
        expected_facts = [
            fact for fact in expected_facts if _fact_matches_expected_signature_filter(fact, signature_filter)
        ]
        forbidden_facts = [
            fact for fact in forbidden_facts if _fact_matches_expected_signature_filter(fact, signature_filter)
        ]
    runs: list[dict[str, Any]] = []
    support: dict[str, list[str]] = {fact: [] for fact in expected_facts}
    variants: dict[str, dict[str, list[str]]] = {fact: {} for fact in expected_facts}
    forbidden_support: dict[str, list[str]] = {fact: [] for fact in forbidden_facts}
    unexpected_support: dict[str, list[str]] = {}
    for index, path in enumerate(compile_paths, start=1):
        run_id = path.parent.name or f"run_{index}"
        compile_facts = _facts_from_compile_json(path)
        reducer_report: dict[str, Any] = {}
        if apply_domain_reducers:
            reduced_compile = {"facts": compile_facts, "rules": [], "queries": []}
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                payload = {}
            if isinstance(payload, dict):
                mode = str(payload.get("mode", "")).strip()
                if mode:
                    reduced_compile["mode"] = mode
                if isinstance(payload.get("union_source_compile"), dict):
                    reduced_compile["union_source_compile"] = payload["union_source_compile"]
            if isinstance(payload, dict) and isinstance(payload.get("active_profile_registry_lens"), dict):
                reduced_compile["active_profile_registry_lens"] = payload["active_profile_registry_lens"]
            reducer_report = _apply_domain_reducers(reduced_compile)
            compile_facts = [str(item).strip() for item in reduced_compile.get("facts", []) if str(item).strip()]
        if matcher == "constant_slot":
            missing = {fact for fact in expected_facts if not _constant_slot_supported(fact, compile_facts)}
        else:
            match_report = _match_expected_facts(expected_facts, compile_facts)
            missing = set(match_report["missing_expected_facts"])
        matched = [fact for fact in expected_facts if fact not in missing]
        for fact in matched:
            support.setdefault(fact, []).append(run_id)
        for fact in forbidden_facts:
            if _fact_supported(fact, compile_facts, matcher=matcher):
                forbidden_support.setdefault(fact, []).append(run_id)
        if report_unexpected:
            for fact in sorted(set(compile_facts)):
                if not _fact_in_signature_filter(fact, signature_filter):
                    continue
                if any(_fact_supported(expected_fact, [fact], matcher=matcher) for expected_fact in expected_facts):
                    continue
                if any(_fact_supported(forbidden_fact, [fact], matcher=matcher) for forbidden_fact in forbidden_facts):
                    continue
                unexpected_support.setdefault(fact, []).append(run_id)
        for fact in missing:
            for variant in _same_predicate_variants(fact, compile_facts):
                variants.setdefault(fact, {}).setdefault(variant["fact"], []).append(run_id)
        runs.append(
            {
                "run_id": run_id,
                "compile_json": str(path),
                "matched_fact_count": len(matched),
                "expected_fact_count": len(expected_facts),
                "missing_fact_count": len(missing),
                "forbidden_match_count": sum(
                    1 for fact in forbidden_facts if run_id in forbidden_support.get(fact, [])
                ),
                "domain_reducer_reports": reducer_report,
            }
        )
    rows = [
        {
            "expected_fact": fact,
            "support_count": len(run_ids),
            "support_runs": run_ids,
            "meets_threshold": len(run_ids) >= support_threshold,
            "same_predicate_variants": [
                {"fact": variant, "runs": sorted(set(variant_runs)), "run_count": len(set(variant_runs))}
                for variant, variant_runs in sorted(
                    variants.get(fact, {}).items(),
                    key=lambda item: (-len(set(item[1])), item[0]),
                )
            ],
        }
        for fact, run_ids in support.items()
    ]
    rows.sort(key=lambda item: (not bool(item["meets_threshold"]), -int(item["support_count"]), item["expected_fact"]))
    supported = [row for row in rows if row["meets_threshold"]]
    forbidden_rows = [
        {
            "forbidden_fact": fact,
            "support_count": len(run_ids),
            "support_runs": run_ids,
            "supported": bool(run_ids),
        }
        for fact, run_ids in forbidden_support.items()
    ]
    forbidden_rows.sort(key=lambda item: (not bool(item["supported"]), -int(item["support_count"]), item["forbidden_fact"]))
    supported_forbidden = [row for row in forbidden_rows if row["supported"]]
    unexpected_rows = [
        {
            "fact": fact,
            "support_count": len(run_ids),
            "support_runs": run_ids,
        }
        for fact, run_ids in unexpected_support.items()
    ]
    unexpected_rows.sort(key=lambda item: (-int(item["support_count"]), item["fact"]))
    unexpected_signature_rows = _summarize_unexpected_by_signature(
        unexpected_rows,
        support_threshold=support_threshold,
    )
    return {
        "schema_version": "typed_micro_series_summary_v1",
        "fixture_id": fixture_id,
        "expected_facts": str(expected_path),
        "forbidden_facts": str(forbidden_path) if forbidden_path.exists() else "",
        "support_threshold": support_threshold,
        "matcher": matcher,
        "domain_reducers_applied": bool(apply_domain_reducers),
        "expected_signature_filter": sorted(signature_filter),
        "summary": {
            "compile_count": len(compile_paths),
            "expected_fact_count": len(expected_facts),
            "supported_fact_count": len(supported),
            "unsupported_fact_count": len(rows) - len(supported),
            "forbidden_fact_count": len(forbidden_facts),
            "supported_forbidden_fact_count": len(supported_forbidden),
            "unexpected_fact_count": len(unexpected_rows) if report_unexpected else None,
        },
        "runs": runs,
        "rows": rows,
        "forbidden_rows": forbidden_rows,
        "unexpected_rows": unexpected_rows,
        "unexpected_signature_rows": unexpected_signature_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Typed Micro-Series Summary",
        "",
        f"- Fixture: `{report['fixture_id']}`",
        f"- Compiles: `{summary['compile_count']}`",
        f"- Expected facts: `{summary['expected_fact_count']}`",
        f"- Support threshold: `{report['support_threshold']}`",
        f"- Matcher: `{report.get('matcher', 'unification')}`",
        f"- Expected signature filter: `{', '.join(report.get('expected_signature_filter') or []) or 'none'}`",
        f"- Domain reducers applied: `{report.get('domain_reducers_applied', False)}`",
        f"- Supported facts: `{summary['supported_fact_count']}`",
        f"- Unsupported facts: `{summary['unsupported_fact_count']}`",
        f"- Forbidden facts: `{summary.get('forbidden_fact_count', 0)}`",
        f"- Supported forbidden facts: `{summary.get('supported_forbidden_fact_count', 0)}`",
        (
            f"- Unexpected facts: `{summary.get('unexpected_fact_count')}`"
            if summary.get("unexpected_fact_count") is not None
            else "- Unexpected facts: `not reported`"
        ),
        "",
        "| Support | Meets | Expected fact |",
        "| ---: | --- | --- |",
    ]
    for row in report.get("rows", []):
        meets = "yes" if row.get("meets_threshold") else "no"
        lines.append(
            "| {} | {} | `{}` |".format(
                row.get("support_count", 0),
                meets,
                str(row.get("expected_fact", "")).replace("|", "/"),
            )
        )
    unsupported_with_variants = [
        row for row in report.get("rows", []) if not row.get("meets_threshold") and row.get("same_predicate_variants")
    ]
    if unsupported_with_variants:
        lines.extend(["", "## Unsupported Same-Predicate Variants", ""])
        for row in unsupported_with_variants:
            lines.append(f"- Expected: `{row.get('expected_fact')}`")
            for variant in row.get("same_predicate_variants", [])[:8]:
                runs = ", ".join(variant.get("runs", []))
                lines.append(f"  - {variant.get('run_count', 0)} run(s): `{variant.get('fact')}` [{runs}]")
    supported_forbidden = [row for row in report.get("forbidden_rows", []) if row.get("supported")]
    if supported_forbidden:
        lines.extend(["", "## Supported Forbidden Facts", ""])
        for row in supported_forbidden:
            runs = ", ".join(row.get("support_runs", []))
            lines.append(f"- {row.get('support_count', 0)} run(s): `{row.get('forbidden_fact')}` [{runs}]")
    unexpected_rows = report.get("unexpected_rows", [])
    if unexpected_rows:
        signature_rows = report.get("unexpected_signature_rows", [])
        if signature_rows:
            lines.extend(["", "## Unexpected Same-Signature Buckets", ""])
            lines.append(
                "| Signature | Facts | Support>=threshold | Max support | Support distribution |"
            )
            lines.append("| --- | ---: | ---: | ---: | --- |")
            for row in signature_rows:
                distribution = ", ".join(
                    f"{support}:{count}"
                    for support, count in sorted(
                        (row.get("support_distribution") or {}).items(),
                        key=lambda item: int(item[0]),
                    )
                )
                lines.append(
                    "| `{}` | {} | {} | {} | `{}` |".format(
                        row.get("signature") or "unparsed",
                        row.get("fact_count", 0),
                        row.get("support_ge_threshold_fact_count", 0),
                        row.get("max_support", 0),
                        distribution,
                    )
                )
        lines.extend(["", "## Unexpected Same-Signature Facts", ""])
        lines.append(
            "These facts were emitted in the selected signatures but matched neither expected nor forbidden facts. "
            "They are precision/adjudication targets, not automatic errors."
        )
        lines.append("")
        for row in unexpected_rows:
            runs = ", ".join(row.get("support_runs", []))
            lines.append(f"- {row.get('support_count', 0)} run(s): `{row.get('fact')}` [{runs}]")
    return "\n".join(lines) + "\n"


def _parse_signature_filter(values: list[str]) -> set[str]:
    signatures: set[str] = set()
    for value in values or []:
        for item in str(value or "").split(","):
            signature = item.strip()
            if signature:
                signatures.add(signature)
    return signatures


def _fact_signature(fact: str) -> str:
    parsed = _parse_fact(fact)
    if parsed is None:
        return ""
    predicate = str(parsed.get("predicate") or "").strip()
    args = parsed.get("args") or []
    if not predicate or not isinstance(args, list):
        return ""
    return f"{predicate}/{len(args)}"


def _summarize_unexpected_by_signature(
    unexpected_rows: list[dict[str, Any]],
    *,
    support_threshold: int,
) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for row in unexpected_rows:
        fact = str(row.get("fact") or "")
        signature = _fact_signature(fact) or "unparsed"
        support_count = int(row.get("support_count") or 0)
        bucket = buckets.setdefault(
            signature,
            {
                "signature": signature,
                "fact_count": 0,
                "support_ge_threshold_fact_count": 0,
                "total_support": 0,
                "max_support": 0,
                "support_distribution": {},
            },
        )
        bucket["fact_count"] += 1
        bucket["total_support"] += support_count
        bucket["max_support"] = max(int(bucket.get("max_support") or 0), support_count)
        if support_count >= support_threshold:
            bucket["support_ge_threshold_fact_count"] += 1
        distribution = bucket.setdefault("support_distribution", {})
        key = str(support_count)
        distribution[key] = int(distribution.get(key) or 0) + 1
    rows = list(buckets.values())
    rows.sort(
        key=lambda item: (
            -int(item.get("support_ge_threshold_fact_count") or 0),
            -int(item.get("fact_count") or 0),
            str(item.get("signature") or ""),
        )
    )
    return rows


def _fact_matches_expected_signature_filter(fact: str, signature_filter: set[str]) -> bool:
    signature = _fact_signature(fact)
    if signature not in signature_filter:
        return False
    if signature != "domain_omission/5":
        return True
    carrier_signatures = {item for item in signature_filter if item != "domain_omission/5"}
    if not carrier_signatures:
        return True
    carrier_signature = _domain_omission_carrier_signature(fact)
    return bool(carrier_signature and carrier_signature in carrier_signatures)


def _domain_omission_carrier_signature(fact: str) -> str:
    parsed = _parse_fact(fact)
    if parsed is None:
        return ""
    if str(parsed.get("predicate") or "") != "domain_omission":
        return ""
    args = parsed.get("args") or []
    if len(args) != 5:
        return ""
    raw = str(args[1] or "").strip().strip("'\"")
    if "/" in raw:
        return raw
    if raw.endswith("_5"):
        return raw[:-2] + "/5"
    if raw.endswith("_4"):
        return raw[:-2] + "/4"
    if raw.endswith("_6"):
        return raw[:-2] + "/6"
    return raw


def _fact_in_signature_filter(fact: str, signature_filter: set[str]) -> bool:
    if not signature_filter:
        return True
    return _fact_matches_expected_signature_filter(fact, signature_filter)


def _same_predicate_variants(expected_fact: str, compile_facts: list[str]) -> list[dict[str, Any]]:
    expected = _parse_fact(expected_fact)
    if expected is None:
        return []
    predicate = str(expected.get("predicate") or "")
    expected_args = [str(arg).strip() for arg in expected.get("args") or []]
    arity = len(expected_args)
    variants: list[dict[str, Any]] = []
    seen: set[str] = set()
    for fact in compile_facts:
        parsed = _parse_fact(fact)
        if parsed is None:
            continue
        if str(parsed.get("predicate") or "") != predicate:
            continue
        if len(parsed.get("args") or []) != arity:
            continue
        if fact == expected_fact:
            continue
        candidate_args = [str(arg).strip() for arg in parsed.get("args") or []]
        overlap = _same_position_constant_overlap(expected_args, candidate_args)
        if overlap <= 0:
            continue
        if fact not in seen:
            variants.append({"fact": fact, "overlap": overlap})
            seen.add(fact)
    variants.sort(key=lambda item: (-int(item["overlap"]), str(item["fact"])))
    return variants


def _constant_slot_supported(expected_fact: str, compile_facts: list[str]) -> bool:
    expected = _parse_fact(expected_fact)
    if expected is None:
        return False
    predicate = str(expected.get("predicate") or "")
    expected_args = [str(arg).strip() for arg in expected.get("args") or []]
    arity = len(expected_args)
    for fact in compile_facts:
        parsed = _parse_fact(fact)
        if parsed is None:
            continue
        if str(parsed.get("predicate") or "") != predicate:
            continue
        candidate_args = [str(arg).strip() for arg in parsed.get("args") or []]
        if len(candidate_args) != arity:
            continue
        if all(
            _is_expected_variable(expected_arg) or expected_arg == candidate_arg
            for expected_arg, candidate_arg in zip(expected_args, candidate_args)
        ):
            return True
    return False


def _fact_supported(fact: str, compile_facts: list[str], *, matcher: str) -> bool:
    if matcher == "constant_slot":
        return _constant_slot_supported(fact, compile_facts)
    return fact not in set(_match_expected_facts([fact], compile_facts)["missing_expected_facts"])


def _same_position_constant_overlap(expected_args: list[str], candidate_args: list[str]) -> int:
    count = 0
    for expected, candidate in zip(expected_args, candidate_args):
        if _is_expected_variable(expected):
            continue
        if expected == candidate:
            count += 1
    return count


def _is_expected_variable(value: str) -> bool:
    text = str(value or "").strip()
    return bool(text) and (text[0].isupper() or text.startswith("_"))


def _apply_domain_reducers(source_compile: dict[str, Any]) -> dict[str, Any]:
    reports: dict[str, Any] = {}
    for name, reducer in (
        ("fda_warning_letter_subject_convergence", _apply_fda_warning_letter_subject_convergence),
        ("fda_date_atom_reduction", _apply_fda_date_atom_reduction),
        ("fda_facility_subject_convergence", _apply_fda_facility_subject_convergence),
        ("fda_lot_identifier_atom_reduction", _apply_fda_lot_identifier_atom_reduction),
        ("fda_violation_detail_atom_reduction", _apply_fda_violation_detail_atom_reduction),
        ("fda_facility_identity_atom_reduction", _apply_fda_facility_identity_atom_reduction),
        ("fda_consultant_citation_scope_reduction", _apply_fda_consultant_citation_scope_reduction),
        ("fda_office_atom_reduction", _apply_fda_office_atom_reduction),
        ("fda_correspondence_party_name_reduction", _apply_fda_correspondence_party_name_reduction),
        ("fda_correspondence_party_role_integrity", _apply_fda_correspondence_party_role_integrity),
        ("fda_no_fei_omission_reduction", _apply_fda_no_fei_omission_reduction),
        ("fda_adulteration_basis_authority_reduction", _apply_fda_adulteration_basis_authority_reduction),
        (
            "fda_insanitary_adulteration_basis_support_integrity",
            _apply_fda_insanitary_adulteration_basis_support_integrity,
        ),
        ("registered_date_slot_atom_reduction", _apply_registered_date_slot_atom_reduction),
        ("sec_exhibit_number_atom_reduction", _apply_sec_exhibit_number_atom_reduction),
        ("sec_exhibit_treatment_specificity_integrity", _apply_sec_exhibit_treatment_specificity_integrity),
        ("sec_filing_id_atom_reduction", _apply_sec_filing_id_atom_reduction),
        ("sec_typed_slot_prefix_reduction", _apply_sec_typed_slot_prefix_reduction),
        ("sec_identifier_value_atom_reduction", _apply_sec_identifier_value_atom_reduction),
        ("state_ag_typed_atom_reduction", _apply_state_ag_typed_atom_reduction),
        ("ntsb_timestamp_atom_reduction", _apply_ntsb_timestamp_atom_reduction),
        ("ntsb_actor_id_atom_reduction", _apply_ntsb_actor_id_atom_reduction),
        ("ntsb_condition_atom_reduction", _apply_ntsb_condition_atom_reduction),
        ("ntsb_injury_count_scope_specificity", _apply_ntsb_injury_count_scope_specificity),
        ("fda_violation_number_atom_reduction", _apply_fda_violation_number_atom_reduction),
        ("fda_cgmp_violation_item_projection", _apply_fda_cgmp_violation_item_projection),
        ("fda_violation_category_from_unique_citation_reduction", _apply_fda_violation_category_from_unique_citation_reduction),
        ("fda_cgmp_bundle_subject_integrity", _apply_fda_cgmp_bundle_subject_integrity),
        ("fda_response_assessment_scope_reduction", _apply_fda_response_assessment_scope_reduction),
        ("fda_response_assessment_item_projection", _apply_fda_response_assessment_item_projection),
        ("fda_response_documentation_gap_projection", _apply_fda_response_documentation_gap_projection),
        ("fda_response_investigation_gap_projection", _apply_fda_response_investigation_gap_projection),
        ("fda_response_assessment_id_canonicalization", _apply_fda_response_assessment_id_canonicalization),
        ("fda_response_assessment_kind_citation_reduction", _apply_fda_response_assessment_kind_citation_reduction),
        ("fda_response_assessment_specificity_reduction", _apply_fda_response_assessment_specificity_reduction),
        ("fda_response_assessment_subject_integrity", _apply_fda_response_assessment_subject_integrity),
        ("fda_violation_detail_value_kind_integrity", _apply_fda_violation_detail_value_kind_integrity),
        ("fda_violation_detail_subject_integrity", _apply_fda_violation_detail_subject_integrity),
        ("fda_violation_detail_slot_projection", _apply_fda_violation_detail_slot_projection),
        ("fda_response_assessment_slot_projection", _apply_fda_response_assessment_slot_projection),
        ("source_scope_payload_integrity", _apply_source_scope_payload_integrity),
        ("carrier_value_domain_integrity", _apply_carrier_value_domain_integrity),
        ("atom_shape_integrity", _apply_atom_shape_integrity),
        ("fda_correspondence_party_placeholder_contract", _enforce_fda_correspondence_party_placeholder_contract),
        ("domain_omission_carrier_signature_reduction", _apply_domain_omission_carrier_signature_reduction),
        ("domain_omission_registry_value_integrity", _apply_domain_omission_registry_value_integrity),
        ("sec_signature_omission_contradiction_integrity", _apply_sec_signature_omission_contradiction_integrity),
        ("osha_accident_omission_contradiction_integrity", _apply_osha_accident_omission_contradiction_integrity),
        ("osha_inspection_omission_contradiction_integrity", _apply_osha_inspection_omission_contradiction_integrity),
        ("ntsb_report_omission_contradiction_integrity", _apply_ntsb_report_omission_contradiction_integrity),
        ("active_lens_scope_integrity", _apply_active_lens_scope_integrity),
    ):
        reports[name] = reducer(source_compile)
    return reports


if __name__ == "__main__":
    raise SystemExit(main())
