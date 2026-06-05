#!/usr/bin/env python3
"""Union mapper-admitted domain bootstrap compile surfaces.

This utility combines already-admitted facts/rules from one or more
domain-bootstrap source compile JSON artifacts. It deliberately does not read
the original source prose and does not infer new clauses. It only deduplicates
safe mapper outputs and optionally validates that the merged clauses load in
the local Prolog runtime.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_file"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_pipeline import CorePrologRuntime  # noqa: E402
from scripts.run_rule_acquisition_pass import (  # noqa: E402
    _runtime_trial,
    _rule_trial_item_promotion_ready,
)
from scripts.run_domain_bootstrap_file import (  # noqa: E402
    _apply_domain_omission_carrier_signature_reduction,
    _apply_fda_consultant_citation_scope_reduction,
    _apply_fda_correspondence_party_name_reduction,
    _apply_fda_cgmp_violation_item_projection,
    _apply_fda_cgmp_bundle_subject_integrity,
    _apply_fda_date_atom_reduction,
    _apply_fda_facility_identity_atom_reduction,
    _apply_fda_facility_subject_convergence,
    _apply_fda_lot_identifier_atom_reduction,
    _apply_fda_no_fei_omission_reduction,
    _apply_fda_office_atom_reduction,
    _apply_fda_response_assessment_slot_projection,
    _apply_fda_response_assessment_scope_reduction,
    _apply_fda_response_assessment_item_projection,
    _apply_fda_response_documentation_gap_projection,
    _apply_fda_response_investigation_gap_projection,
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
    parser.add_argument("--run-json", action="append", type=Path, required=True, help="Compile run JSON to merge.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--label", default="union", help="Short label used in the output filename.")
    parser.add_argument("--domain-hint", default="", help="Optional domain hint override.")
    parser.add_argument(
        "--trial-backbone-json",
        type=Path,
        default=None,
        help="Optional compile JSON whose admitted facts provide the temporary KB for rule trial.",
    )
    parser.add_argument(
        "--positive-query",
        action="append",
        default=[],
        help="Optional Prolog query expected to return rows after temporary rule loading.",
    )
    parser.add_argument(
        "--negative-query",
        action="append",
        default=[],
        help="Optional Prolog query expected to return no rows after temporary rule loading.",
    )
    parser.add_argument(
        "--drop-non-promotion-ready-rules",
        action="store_true",
        help="When --trial-backbone-json is supplied, keep only rules that pass promotion-readiness diagnostics.",
    )
    parser.add_argument(
        "--no-runtime-validation",
        action="store_true",
        help="Do not validate merged clauses in the local Prolog runtime before writing.",
    )
    parser.add_argument(
        "--apply-domain-reducers",
        action="store_true",
        help="Apply deterministic typed-domain reducers after merging admitted clauses. This reads no source prose.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_paths = [path if path.is_absolute() else (REPO_ROOT / path).resolve() for path in args.run_json]
    records = [json.loads(path.read_text(encoding="utf-8-sig")) for path in run_paths]
    if not records:
        raise SystemExit("no records supplied")

    facts = _ordered_unique(_source_compile_items(records, "facts"))
    rules = _ordered_unique(_source_compile_items(records, "rules"))
    queries = _ordered_unique(_source_compile_items(records, "queries"))
    reducer_reports: dict[str, Any] = {}
    if bool(args.apply_domain_reducers):
        reduced_compile = {"facts": facts, "rules": rules, "queries": queries}
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
            ("fda_no_fei_omission_reduction", _apply_fda_no_fei_omission_reduction),
            ("registered_date_slot_atom_reduction", _apply_registered_date_slot_atom_reduction),
            ("sec_exhibit_number_atom_reduction", _apply_sec_exhibit_number_atom_reduction),
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
            ("fda_violation_detail_value_kind_integrity", _apply_fda_violation_detail_value_kind_integrity),
            ("fda_violation_detail_subject_integrity", _apply_fda_violation_detail_subject_integrity),
            ("fda_violation_detail_slot_projection", _apply_fda_violation_detail_slot_projection),
            ("fda_response_assessment_scope_reduction", _apply_fda_response_assessment_scope_reduction),
            ("fda_response_assessment_item_projection", _apply_fda_response_assessment_item_projection),
            ("fda_response_documentation_gap_projection", _apply_fda_response_documentation_gap_projection),
            ("fda_response_investigation_gap_projection", _apply_fda_response_investigation_gap_projection),
            ("fda_response_assessment_id_canonicalization", _apply_fda_response_assessment_id_canonicalization),
            ("fda_response_assessment_kind_citation_reduction", _apply_fda_response_assessment_kind_citation_reduction),
            ("fda_response_assessment_specificity_reduction", _apply_fda_response_assessment_specificity_reduction),
            ("fda_response_assessment_subject_integrity", _apply_fda_response_assessment_subject_integrity),
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
        ):
            reducer_reports[name] = reducer(reduced_compile)
        facts = _ordered_unique(_compile_items({"source_compile": reduced_compile}, "facts"))
        rules = _ordered_unique(_compile_items({"source_compile": reduced_compile}, "rules"))
        queries = _ordered_unique(_compile_items({"source_compile": reduced_compile}, "queries"))
    runtime_trial: dict[str, Any] = {}
    trial_facts: list[str] = []
    if args.trial_backbone_json is not None:
        trial_backbone_path = args.trial_backbone_json
        if not trial_backbone_path.is_absolute():
            trial_backbone_path = (REPO_ROOT / trial_backbone_path).resolve()
        trial_backbone = json.loads(trial_backbone_path.read_text(encoding="utf-8-sig"))
        trial_facts = _compile_items(trial_backbone, "facts")
        runtime_trial = _runtime_trial(
            facts=trial_facts,
            backbone_rules=[],
            rule_lens_rules=rules,
            positive_queries=[str(item) for item in args.positive_query if str(item).strip()],
            negative_queries=[str(item) for item in args.negative_query if str(item).strip()],
        )
        if bool(args.drop_non_promotion_ready_rules):
            ready_rules = _promotion_ready_rules_from_trial(runtime_trial)
            rules = [rule for rule in rules if rule in ready_rules]
            runtime_trial = _runtime_trial(
                facts=trial_facts,
                backbone_rules=[],
                rule_lens_rules=rules,
                positive_queries=[str(item) for item in args.positive_query if str(item).strip()],
                negative_queries=[str(item) for item in args.negative_query if str(item).strip()],
            )
    load_errors: list[str] = []
    if not bool(args.no_runtime_validation):
        facts, rules, load_errors = _runtime_validated(facts=facts, rules=rules)

    first = dict(records[0])
    first_compile = first.get("source_compile") if isinstance(first.get("source_compile"), dict) else {}
    domain_hint = str(args.domain_hint or first.get("domain_hint") or "")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    source_counts = [
        {
            "run_json": str(path),
            "facts": len(_compile_items(record, "facts")),
            "rules": len(_compile_items(record, "rules")),
            "queries": len(_compile_items(record, "queries")),
        }
        for path, record in zip(run_paths, records)
    ]

    first.update(
        {
            "ts": now,
            "mode": "deterministic_compile_union",
            "domain_hint": domain_hint,
            "source_compile": {
                "ok": not bool(load_errors),
                "mode": "deterministic_compile_union",
                "facts": facts,
                "rules": rules,
                "queries": queries,
                "admitted_count": len(facts) + len(rules),
                "skipped_count": 0,
                "unique_fact_count": len(facts),
                "unique_rule_count": len(rules),
                "unique_query_count": len(queries),
                "source_admitted_counts": source_counts,
                "runtime_load_errors": load_errors,
            },
            "runtime_trial": runtime_trial,
            "union_source_compile": {
                "schema_version": "domain_bootstrap_compile_union_v1",
                "created_at": now,
                "source_runs": [str(path) for path in run_paths],
                "source_counts": source_counts,
                "runtime_validated": not bool(args.no_runtime_validation),
                "runtime_load_errors": load_errors,
                "trial_backbone_json": str(args.trial_backbone_json or ""),
                "trial_fact_count": len(trial_facts),
                "drop_non_promotion_ready_rules": bool(args.drop_non_promotion_ready_rules),
                "domain_reducers_applied": bool(args.apply_domain_reducers),
                "domain_reducer_reports": reducer_reports,
                "positive_queries": [str(item) for item in args.positive_query if str(item).strip()],
                "negative_queries": [str(item) for item in args.negative_query if str(item).strip()],
                "policy": [
                    "No source prose was read.",
                    "No new facts or rules were inferred.",
                    "Only mapper-admitted compile outputs were deduplicated.",
                ],
            },
        }
    )
    if isinstance(first_compile, dict):
        first["union_source_compile"]["first_compile_mode"] = first_compile.get("mode", "")
    first.pop("active_profile_registry_lens", None)
    first["profile_registry_lens"] = ""
    first["profile_registry_lens_note"] = (
        "deterministic_compile_union has no single active lens; source lens artifacts are listed in union_source_compile.source_runs"
    )

    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    # Lens-bundle runs nest union artifacts under already-descriptive Windows
    # paths, so keep filename slugs short enough to avoid MAX_PATH surprises.
    slug = _slug(str(args.label or "union"), limit=48)
    model_slug = _slug(str(first.get("model") or "model"), limit=32)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out_path = out_dir / f"domain_bootstrap_file_{stamp}_{slug}_{model_slug}.json"
    out_path.write_text(json.dumps(first, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(str(out_path))
    print(
        json.dumps(
            {
                "facts": len(facts),
                "rules": len(rules),
                "queries": len(queries),
                "runtime_load_errors": len(load_errors),
                "trial_promotion_ready_rules": runtime_trial.get("promotion_ready_rule_count") if runtime_trial else None,
                "trial_composition_ready_rules": runtime_trial.get("composition_ready_rule_count") if runtime_trial else None,
                "trial_composition_rescued_rules": runtime_trial.get("composition_rescued_rule_count") if runtime_trial else None,
                "trial_positive_probe_passes": runtime_trial.get("positive_probe_pass_count") if runtime_trial else None,
                "trial_negative_probe_passes": runtime_trial.get("negative_probe_pass_count") if runtime_trial else None,
                "trial_probe_adjusted_promotion_ready": runtime_trial.get("probe_adjusted_promotion_ready") if runtime_trial else None,
                "source_runs": len(run_paths),
            },
            sort_keys=True,
        )
    )
    return 0


def _compile_items(record: dict[str, Any], key: str) -> list[str]:
    source_compile = record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {}
    return [str(item).strip() for item in source_compile.get(key, []) if str(item).strip()]


def _promotion_ready_rules_from_trial(runtime_trial: dict[str, Any]) -> set[str]:
    ready_rules: set[str] = set()
    for key in ("derived_head_queries", "composition_head_queries"):
        rows = runtime_trial.get(key, [])
        if not isinstance(rows, list):
            continue
        ready_rules.update(
            str(item.get("rule", "")).strip()
            for item in rows
            if isinstance(item, dict) and _rule_trial_item_promotion_ready(item)
        )
    return {rule for rule in ready_rules if rule}


def _source_compile_items(records: list[dict[str, Any]], key: str) -> list[str]:
    out: list[str] = []
    for record in records:
        out.extend(_compile_items(record, key))
    return out


def _ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _runtime_validated(*, facts: list[str], rules: list[str]) -> tuple[list[str], list[str], list[str]]:
    runtime = CorePrologRuntime(max_depth=500)
    good_facts: list[str] = []
    good_rules: list[str] = []
    errors: list[str] = []
    for fact in facts:
        result = runtime.assert_fact(fact)
        if str(result.get("status", "")) == "success":
            good_facts.append(fact)
        else:
            errors.append(f"fact {fact}: {result.get('message', result)}")
    for rule in rules:
        result = runtime.assert_rule(rule)
        if str(result.get("status", "")) == "success":
            good_rules.append(rule)
        else:
            errors.append(f"rule {rule}: {result.get('message', result)}")
    return good_facts, good_rules, errors


def _slug(value: str, *, limit: int = 80) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "").strip())
    out = "-".join(part for part in out.split("-") if part)
    return out[: max(1, int(limit))] or "union"


if __name__ == "__main__":
    raise SystemExit(main())
