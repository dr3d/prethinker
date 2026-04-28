from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_mixed_domain_agility import build_mixed_cases  # noqa: E402
from scripts.run_semantic_ir_lava_sweep import load_frontier_pack_cases  # noqa: E402
from src.domain_profiles import (  # noqa: E402
    load_domain_profile_catalog,
    load_profile_package,
    profile_package_context,
    profile_package_contracts,
    thin_profile_roster,
)
from src.semantic_ir import SemanticIRCallConfig, call_semantic_ir, semantic_ir_to_legacy_parse  # noqa: E402
from src.semantic_router import SemanticRouterCallConfig, call_semantic_router  # noqa: E402


DEFAULT_OUT = REPO_ROOT / "tmp" / "semantic_router_agility"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a two-pass LLM-router -> Semantic IR compiler mixed-domain agility experiment."
    )
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--seed", type=int, default=4107)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--backend", choices=["lmstudio", "ollama"], default="lmstudio")
    parser.add_argument("--model", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--router-only", action="store_true", help="Skip second compiler pass.")
    parser.add_argument("--include-model-input", action="store_true")
    parser.add_argument(
        "--frontier-pack",
        type=Path,
        default=None,
        help="Optional frontier pack JSON to use instead of the built-in mixed-domain agility cases.",
    )
    parser.add_argument(
        "--source-filter",
        default="",
        help="Optional case-insensitive substring filter over frontier case id/source.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backend = str(args.backend or "lmstudio").strip().lower()
    model = str(args.model or "").strip()
    if not model:
        model = "qwen/qwen3.6-35b-a3b" if backend == "lmstudio" else "qwen3.6:35b"
    base_url = str(args.base_url or "").strip()
    if not base_url:
        base_url = "http://127.0.0.1:1234" if backend == "lmstudio" else "http://127.0.0.1:11434"

    catalog = load_domain_profile_catalog()
    roster = thin_profile_roster(catalog)
    predicate_index = _profile_predicate_index(catalog)
    rng = random.Random(int(args.seed))
    cases = _load_requested_cases(args)
    stream = _interleaved_sample(cases, count=max(1, int(args.count)), rng=rng)
    out_path = args.out or _default_out_path(args.seed)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

    ir_config = SemanticIRCallConfig(
        backend=backend,
        base_url=base_url,
        model=model,
        context_length=int(args.num_ctx),
        timeout=int(args.timeout),
        max_tokens=12000,
    )
    router_config = SemanticRouterCallConfig.from_semantic_ir_config(ir_config)
    records: list[dict[str, Any]] = []

    for index, case in enumerate(stream, start=1):
        case_id = str(case.get("id") or f"router_{index:04d}")
        expected = str(case.get("expected_profile") or "")
        context = [str(item).strip() for item in case.get("context", []) if str(item).strip()]
        utterance = str(case.get("utterance") or "").strip()
        print(f"[{index}/{len(stream)}] {case_id} expected={expected}", flush=True)

        record: dict[str, Any] = {
            "ts": _utc_now(),
            "index": index,
            "case_id": case_id,
            "source": case.get("source"),
            "expected_profile": expected,
            "utterance": utterance,
            "context": context,
            "router_ok": False,
            "router_eval": {},
            "router_profile": "",
            "effective_profile": "general",
            "compiler_parsed_ok": None,
            "model_decision": None,
            "projected_decision": None,
            "admitted_count": 0,
            "skipped_count": 0,
            "error": "",
        }

        try:
            router_response = call_semantic_router(
                utterance=utterance,
                config=router_config,
                context=context,
                available_domain_profiles=roster,
                kb_manifest={"note": "no live KB in offline router agility harness"},
                include_model_input=bool(args.include_model_input),
            )
            router = router_response.get("parsed")
            record["router_latency_ms"] = router_response.get("latency_ms")
            record["router"] = router
            record["router_model_input"] = router_response.get("model_input") if bool(args.include_model_input) else {}
            if not isinstance(router, dict):
                record["error"] = "router did not return semantic_router_v1 JSON"
                _write_record(out_path, record)
                records.append(record)
                continue

            router_profile = str(router.get("selected_profile_id") or "general").strip()
            effective_profile = _known_profile_or_general(router_profile, catalog)
            record["router_profile"] = router_profile
            record["effective_profile"] = effective_profile
            router_eval = _evaluate_router(router, expected_profile=expected, effective_profile=effective_profile, catalog=catalog)
            record["router_eval"] = router_eval
            record["router_ok"] = bool(router_eval.get("strict_ok"))

            if args.router_only:
                record["context_audit"] = _context_audit_record(
                    router=router,
                    effective_profile=effective_profile,
                    domain_context=[],
                    predicate_contracts=[],
                    allowed_predicates=[],
                )
                _write_record(out_path, record)
                records.append(record)
                continue

            bootstrap_review_only = _router_requests_bootstrap(router)
            profile = load_profile_package(effective_profile, catalog) if effective_profile != "general" else {}
            domain_context = profile_package_context(profile) if profile else []
            predicate_contracts = profile_package_contracts(profile) if profile else []
            if bootstrap_review_only:
                domain_context = [
                    "bootstrap_review_policy: no approved domain profile or predicate palette exists for this turn.",
                    "bootstrap_review_policy: semantic_ir_v1 may describe candidate meanings, risks, and clarification needs, but durable candidate_operations are review-only and will not be admitted.",
                    "bootstrap_review_policy: prefer clarify, quarantine, query, or mixed over commit when a new domain vocabulary would be required.",
                ]
                predicate_contracts = [{"signature": "bootstrap_review_only/0", "arguments": []}]
            allowed_predicates = [
                str(row.get("signature", "")).strip()
                for row in predicate_contracts
                if isinstance(row, dict) and str(row.get("signature", "")).strip()
            ]
            record["context_audit"] = _context_audit_record(
                router=router,
                effective_profile=effective_profile,
                domain_context=domain_context,
                predicate_contracts=predicate_contracts,
                allowed_predicates=allowed_predicates,
            )
            compiler_context = _compiler_context_from_router(router, context)
            response = call_semantic_ir(
                utterance=utterance,
                config=ir_config,
                context=compiler_context,
                domain_context=domain_context,
                available_domain_profiles=roster,
                allowed_predicates=allowed_predicates,
                predicate_contracts=predicate_contracts,
                domain=effective_profile if effective_profile != "general" else "runtime",
                include_model_input=bool(args.include_model_input),
            )
            parsed = response.get("parsed")
            record["compiler_latency_ms"] = response.get("latency_ms")
            record["compiler_model_input"] = response.get("model_input") if bool(args.include_model_input) else {}
            if isinstance(parsed, dict):
                mapped, warnings = semantic_ir_to_legacy_parse(
                    parsed,
                    allowed_predicates=allowed_predicates,
                    predicate_contracts=predicate_contracts,
                )
                diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
                anti_coupling = _anti_coupling_diagnostics(
                    router=router,
                    router_eval=router_eval,
                    effective_profile=effective_profile,
                    expected_profile=expected,
                    diagnostics=diagnostics,
                    predicate_index=predicate_index,
                )
                router_diagnostics = _router_diagnostics(
                    router=router,
                    effective_profile=effective_profile,
                    diagnostics=diagnostics,
                    predicate_index=predicate_index,
                )
                record.update(
                    {
                        "compiler_parsed_ok": True,
                        "parsed": parsed,
                        "mapped": mapped,
                        "mapper_warnings": warnings,
                        "model_decision": parsed.get("decision"),
                        "projected_decision": diagnostics.get("projected_decision"),
                        "admitted_count": diagnostics.get("admitted_count", 0),
                        "skipped_count": diagnostics.get("skipped_count", 0),
                        "warning_counts": diagnostics.get("warning_counts", {}),
                        "clauses": diagnostics.get("clauses", {}),
                        "anti_coupling": anti_coupling,
                        "router_diagnostics": router_diagnostics,
                        "bootstrap_review_only": bootstrap_review_only,
                    }
                )
            else:
                record["compiler_parsed_ok"] = False
                record["error"] = "compiler did not return semantic_ir_v1 JSON"
        except Exception as exc:
            record["error"] = str(exc)
            if record.get("compiler_parsed_ok") is None:
                record["compiler_parsed_ok"] = False

        _write_record(out_path, record)
        records.append(record)

    _print_summary(records, out_path)
    return 0


def _compiler_context_from_router(router: dict[str, Any], base_context: list[str]) -> list[str]:
    lines = list(base_context)
    router_summary = {
        "selected_profile_id": router.get("selected_profile_id"),
        "candidate_profile_ids": router.get("candidate_profile_ids", []),
        "turn_shape": router.get("turn_shape"),
        "should_segment": router.get("should_segment"),
        "guidance_modules": router.get("guidance_modules", []),
        "retrieval_hints": router.get("retrieval_hints", {}),
        "risk_flags": router.get("risk_flags", []),
        "context_audit": router.get("context_audit", {}),
        "bootstrap_request": router.get("bootstrap_request", {}),
    }
    lines.append(
        "semantic_router_v1 authority: advisory context engineering only; do not treat router notes as facts."
    )
    lines.append("semantic_router_v1 decision: " + json.dumps(router_summary, ensure_ascii=False, sort_keys=True))
    segments = router.get("segments") if isinstance(router.get("segments"), list) else []
    if segments:
        compact_segments = [
            {
                "span_id": row.get("span_id"),
                "purpose": row.get("purpose"),
                "text": row.get("text"),
            }
            for row in segments
            if isinstance(row, dict)
        ][:8]
        lines.append("semantic_router_v1 segments: " + json.dumps(compact_segments, ensure_ascii=False))
    return lines


def _context_audit_record(
    *,
    router: dict[str, Any],
    effective_profile: str,
    domain_context: list[str],
    predicate_contracts: list[dict[str, Any]],
    allowed_predicates: list[str],
) -> dict[str, Any]:
    audit = router.get("context_audit") if isinstance(router.get("context_audit"), dict) else {}
    return {
        "version": "context_audit_v1",
        "authority": "diagnostic_only_router_controls_context_mapper_controls_admission",
        "selected_profile_id": router.get("selected_profile_id"),
        "effective_profile_id": effective_profile,
        "routing_confidence": router.get("routing_confidence"),
        "why_this_profile": audit.get("why_this_profile", ""),
        "selected_context_sources": audit.get("selected_context_sources", []),
        "secondary_profiles_considered": audit.get("secondary_profiles_considered", []),
        "why_not_secondary": audit.get("why_not_secondary", []),
        "guidance_modules": router.get("guidance_modules", []),
        "risk_flags": router.get("risk_flags", []),
        "retrieval_hints": router.get("retrieval_hints", {}),
        "loaded_domain_context_count": len(domain_context),
        "loaded_predicate_contract_count": len(predicate_contracts),
        "loaded_allowed_predicate_count": len(allowed_predicates),
        "loaded_allowed_predicate_sample": list(allowed_predicates)[:12],
    }


def _router_requests_bootstrap(router: dict[str, Any]) -> bool:
    selected_profile = str(router.get("selected_profile_id") or "").strip()
    bootstrap_request = router.get("bootstrap_request") if isinstance(router.get("bootstrap_request"), dict) else {}
    return selected_profile == "bootstrap" or bool(bootstrap_request.get("needed"))


def _load_requested_cases(args: argparse.Namespace) -> list[dict[str, Any]]:
    if not args.frontier_pack:
        return build_mixed_cases()
    path = Path(args.frontier_pack)
    cases = [
        _router_case_from_lava(case)
        for case in load_frontier_pack_cases(path.parent)
        if case.source.endswith(path.stem)
    ]
    needle = str(args.source_filter or "").strip().lower()
    if needle:
        cases = [
            case
            for case in cases
            if needle in str(case.get("id", "")).lower()
            or needle in str(case.get("source", "")).lower()
        ]
    if not cases:
        raise SystemExit(f"No router cases loaded from frontier pack: {path}")
    return cases


def _router_case_from_lava(case: Any) -> dict[str, Any]:
    return {
        "id": str(case.id),
        "source": str(case.source),
        "expected_profile": str(case.expected_profile or ""),
        "utterance": str(case.utterance),
        "context": [str(item) for item in case.context if str(item).strip()],
    }


def _evaluate_router(
    router: dict[str, Any],
    *,
    expected_profile: str,
    effective_profile: str,
    catalog: dict[str, Any],
) -> dict[str, Any]:
    selected = str(router.get("selected_profile_id") or "general").strip() or "general"
    candidates = [str(item).strip() for item in router.get("candidate_profile_ids", []) if str(item).strip()]
    available_candidates = [item for item in candidates if _known_profile_or_general(item, catalog) == item]
    confidence = _coerce_float(router.get("routing_confidence"), 0.0)
    bootstrap = router.get("bootstrap_request") if isinstance(router.get("bootstrap_request"), dict) else {}
    expected = str(expected_profile or "").strip()
    if expected == "bootstrap":
        strict_ok = selected == "bootstrap" or bool(bootstrap.get("needed"))
    else:
        strict_ok = not expected or effective_profile == expected
    expected_in_candidates = bool(expected and expected in candidates)
    selected_available = selected in {"general", "bootstrap"} or _known_profile_or_general(selected, catalog) == selected
    low_confidence = confidence < 0.7
    semantic_near_miss = bool(expected and expected_in_candidates and not strict_ok)
    unavailable_near_miss = selected not in {"general", "bootstrap"} and not selected_available
    return {
        "strict_ok": strict_ok,
        "expected_profile": expected,
        "selected_profile": selected,
        "effective_profile": effective_profile,
        "candidate_profile_ids": candidates,
        "available_candidate_profile_ids": available_candidates,
        "expected_in_candidates": expected_in_candidates,
        "semantic_near_miss": semantic_near_miss,
        "selected_available": selected_available,
        "unavailable_near_miss": unavailable_near_miss,
        "low_confidence": low_confidence,
        "bootstrap_requested": bool(bootstrap.get("needed")),
        "routing_confidence": confidence,
        "score": _router_score(
            strict_ok=strict_ok,
            semantic_near_miss=semantic_near_miss,
            unavailable_near_miss=unavailable_near_miss,
            low_confidence=low_confidence,
        ),
    }


def _router_score(
    *,
    strict_ok: bool,
    semantic_near_miss: bool,
    unavailable_near_miss: bool,
    low_confidence: bool,
) -> float:
    if strict_ok:
        return 1.0 if not low_confidence else 0.85
    if semantic_near_miss:
        return 0.75
    if unavailable_near_miss:
        return 0.55
    return 0.0 if not low_confidence else 0.25


def _anti_coupling_diagnostics(
    *,
    router: dict[str, Any],
    router_eval: dict[str, Any],
    effective_profile: str,
    expected_profile: str,
    diagnostics: dict[str, Any],
    predicate_index: dict[str, set[str]],
) -> dict[str, Any]:
    """Detect structural signs that the router's context choice harmed admission.

    This intentionally avoids reading or classifying the raw utterance. It only
    compares the router control-plane object with mapper/admission outcomes.
    """

    operations = diagnostics.get("operations", []) if isinstance(diagnostics, dict) else []
    if not isinstance(operations, list):
        operations = []
    clauses = diagnostics.get("clauses", {}) if isinstance(diagnostics.get("clauses"), dict) else {}
    warning_counts = diagnostics.get("warning_counts", {}) if isinstance(diagnostics.get("warning_counts"), dict) else {}
    admitted_count = int(diagnostics.get("admitted_count", 0) or 0)
    skipped_count = int(diagnostics.get("skipped_count", 0) or 0)
    operation_count = int(diagnostics.get("operation_count", len(operations)) or 0)
    projected_decision = str(diagnostics.get("projected_decision") or "").strip()
    routing_confidence = _coerce_float(router.get("routing_confidence"), 0.0)
    selected_profile = str(router.get("selected_profile_id") or router_eval.get("selected_profile") or "").strip()
    candidates = [str(item).strip() for item in router.get("candidate_profile_ids", []) if str(item).strip()]
    bootstrap_request = router.get("bootstrap_request") if isinstance(router.get("bootstrap_request"), dict) else {}
    bootstrap_requested = bool(bootstrap_request.get("needed")) or selected_profile == "bootstrap"
    bootstrap_expected_ok = expected_profile == "bootstrap" and (
        bootstrap_requested or bool(router_eval.get("bootstrap_requested"))
    )
    flags: list[dict[str, Any]] = []

    def flag(kind: str, severity: str, detail: str, **extra: Any) -> None:
        row: dict[str, Any] = {"kind": kind, "severity": severity, "detail": detail}
        row.update({key: value for key, value in extra.items() if value not in (None, "", [], {})})
        flags.append(row)

    if bool(router_eval.get("low_confidence")) and admitted_count:
        flag(
            "low_confidence_router_with_admissions",
            "watch",
            "Router confidence is low but mapper admitted operations.",
            routing_confidence=routing_confidence,
            admitted_count=admitted_count,
        )
    if projected_decision in {"commit", "mixed"} and admitted_count and bool(router_eval.get("semantic_near_miss")):
        flag(
            "semantic_near_miss_with_admissions",
            "review",
            "Router chose a defensible-but-nonexpected profile and the compiler admitted writes.",
            expected_profile=expected_profile,
            effective_profile=effective_profile,
            admitted_count=admitted_count,
        )
    if (
        expected_profile
        and effective_profile != expected_profile
        and not bootstrap_expected_ok
        and not bool(router_eval.get("semantic_near_miss"))
        and admitted_count
    ):
        flag(
            "strict_profile_miss_with_admissions",
            "risk",
            "Router selected a nonexpected profile and mapper admitted operations.",
            expected_profile=expected_profile,
            effective_profile=effective_profile,
            admitted_count=admitted_count,
        )
    if (
        effective_profile == "general"
        and not bootstrap_requested
        and any(item not in {"general", "bootstrap"} for item in candidates)
    ):
        flag(
            "general_effective_profile_with_domain_candidates",
            "watch",
            "Router fell back to general while retaining domain candidates.",
            candidate_profile_ids=candidates,
        )
    if bool(router_eval.get("unavailable_near_miss")):
        flag(
            "selected_unavailable_profile",
            "risk",
            "Router selected a profile whose thick context is unavailable.",
            selected_profile=router_eval.get("selected_profile"),
            effective_profile=effective_profile,
        )

    skip_reasons: dict[str, int] = {}
    skipped_predicates: list[str] = []
    for op in operations:
        if not isinstance(op, dict) or bool(op.get("admitted")):
            continue
        reason = str(op.get("skip_reason") or "").strip()
        if reason:
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
        predicate = str(op.get("predicate") or "").strip()
        if predicate:
            skipped_predicates.append(predicate)
    profile_context_skip_reasons = {
        "predicate_not_in_allowed_palette",
        "predicate_contract_role_mismatch",
        "contract_policy_gate",
    }
    profile_context_skips = {
        reason: count
        for reason, count in skip_reasons.items()
        if reason in profile_context_skip_reasons
    }
    if profile_context_skips and bootstrap_requested and effective_profile == "general":
        flag(
            "bootstrap_review_only_skips",
            "info",
            "Bootstrap mode skipped unapproved candidate operations because no durable predicate palette exists yet.",
            skip_reasons=profile_context_skips,
            skipped_predicates=sorted(set(skipped_predicates))[:12],
        )
    elif profile_context_skips:
        flag(
            "mapper_skips_tied_to_profile_context",
            "review",
            "Mapper skipped operations for predicate palette or profile contract reasons.",
            skip_reasons=profile_context_skips,
            skipped_predicates=sorted(set(skipped_predicates))[:12],
        )
    outside_palette_warnings = {
        warning: count
        for warning, count in warning_counts.items()
        if "outside allowed predicate palette" in str(warning)
    }
    existing_flag_kinds = {row["kind"] for row in flags}
    if outside_palette_warnings and not (
        "mapper_skips_tied_to_profile_context" in existing_flag_kinds
        or "bootstrap_review_only_skips" in existing_flag_kinds
    ):
        flag(
            "out_of_palette_warning",
            "review",
            "Mapper warnings indicate profile/palette mismatch pressure.",
            warning_counts=outside_palette_warnings,
        )
    if operation_count >= 4 and skipped_count > admitted_count:
        flag(
            "high_mapper_skip_ratio",
            "watch",
            "More candidate operations were skipped than admitted.",
            admitted_count=admitted_count,
            skipped_count=skipped_count,
            operation_count=operation_count,
        )

    admitted_predicates = _admitted_predicates_from_clauses(clauses)
    if admitted_predicates:
        profile_hits = _profile_hits_for_predicates(admitted_predicates, predicate_index)
        selected_hits = profile_hits.get(effective_profile, 0)
        better_profiles = [
            {"profile_id": profile, "hits": hits}
            for profile, hits in sorted(profile_hits.items(), key=lambda item: (-item[1], item[0]))
            if profile != effective_profile and hits > selected_hits
        ]
        if better_profiles:
            flag(
                "admitted_predicates_fit_other_profile_better",
                "review",
                "Admitted predicates match another profile palette more strongly than the selected profile.",
                effective_profile=effective_profile,
                admitted_predicates=sorted(admitted_predicates),
                better_profiles=better_profiles[:3],
            )

    return {
        "version": "anti_coupling_diagnostics_v1",
        "authority": "diagnostic_only_router_and_mapper_remain_authoritative",
        "flag_count": len(flags),
        "flags": flags,
        "summary": {
            "routing_confidence": routing_confidence,
            "expected_profile": expected_profile,
            "effective_profile": effective_profile,
            "candidate_profile_ids": candidates,
            "projected_decision": projected_decision,
            "admitted_count": admitted_count,
            "skipped_count": skipped_count,
            "skip_reasons": skip_reasons,
            "admitted_predicates": sorted(admitted_predicates),
        },
    }


def _router_diagnostics(
    *,
    router: dict[str, Any],
    effective_profile: str,
    diagnostics: dict[str, Any],
    predicate_index: dict[str, set[str]],
) -> dict[str, Any]:
    """Formal router/ compiler alignment diagnostics.

    This does not inspect raw language. It compares the router control-plane
    plan with the compiler/mapper predicate surface.
    """

    operations = diagnostics.get("operations", []) if isinstance(diagnostics, dict) else []
    if not isinstance(operations, list):
        operations = []
    emitted_predicates = {
        str(op.get("predicate") or "").strip()
        for op in operations
        if isinstance(op, dict) and str(op.get("predicate") or "").strip()
    }
    admitted_predicates = _admitted_predicates_from_clauses(
        diagnostics.get("clauses", {}) if isinstance(diagnostics, dict) else {}
    )
    selected_palette = predicate_index.get(effective_profile, set())
    candidate_profiles = [
        str(item).strip()
        for item in router.get("candidate_profile_ids", [])
        if str(item).strip()
    ]
    flags: list[dict[str, Any]] = []

    def flag(kind: str, severity: str, detail: str, **extra: Any) -> None:
        row: dict[str, Any] = {"kind": kind, "severity": severity, "detail": detail}
        row.update({key: value for key, value in extra.items() if value not in (None, "", [], {})})
        flags.append(row)

    emitted_outside_selected = sorted(emitted_predicates - selected_palette) if selected_palette else []
    if emitted_outside_selected and effective_profile not in {"general", "bootstrap"}:
        flag(
            "compiler_emitted_predicates_outside_selected_profile",
            "review",
            "Compiler proposed predicates outside the router-selected profile palette.",
            effective_profile=effective_profile,
            predicates=emitted_outside_selected[:16],
        )

    for profile, palette in sorted(predicate_index.items()):
        if profile == effective_profile or profile not in candidate_profiles:
            continue
        overlap = sorted(emitted_predicates & palette)
        selected_overlap = len(emitted_predicates & selected_palette) if selected_palette else 0
        if overlap and len(overlap) > selected_overlap:
            flag(
                "compiler_predicates_fit_secondary_profile_better",
                "review",
                "Compiler predicate surface fits a router secondary profile better than the selected profile.",
                secondary_profile=profile,
                effective_profile=effective_profile,
                predicates=overlap[:16],
            )

    return {
        "version": "router_diagnostics_v1",
        "authority": "diagnostic_only_router_compiler_mapper_remain_separate",
        "flag_count": len(flags),
        "flags": flags,
        "summary": {
            "selected_profile_id": router.get("selected_profile_id"),
            "effective_profile_id": effective_profile,
            "candidate_profile_ids": candidate_profiles,
            "emitted_predicates": sorted(emitted_predicates),
            "admitted_predicates": sorted(admitted_predicates),
            "selected_profile_palette_overlap": sorted(emitted_predicates & selected_palette),
        },
    }


def _profile_predicate_index(catalog: dict[str, Any]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    profiles = catalog.get("profiles", []) if isinstance(catalog, dict) else []
    for row in profiles if isinstance(profiles, list) else []:
        if not isinstance(row, dict):
            continue
        profile_id = str(row.get("profile_id", "")).strip()
        if not profile_id:
            continue
        package = load_profile_package(profile_id, catalog)
        predicates: set[str] = set()
        for contract in profile_package_contracts(package):
            signature = str(contract.get("signature", "")).strip()
            name = signature.split("/", 1)[0].strip()
            if name:
                predicates.add(name)
        index[profile_id] = predicates
    return index


def _admitted_predicates_from_clauses(clauses: dict[str, Any]) -> set[str]:
    predicates: set[str] = set()
    if not isinstance(clauses, dict):
        return predicates
    for bucket in ("facts", "queries", "retracts"):
        rows = clauses.get(bucket, [])
        if not isinstance(rows, list):
            continue
        for clause in rows:
            name = _predicate_name_from_clause(str(clause))
            if name:
                predicates.add(name)
    for clause in clauses.get("rules", []) if isinstance(clauses.get("rules"), list) else []:
        predicates.update(_predicate_names_from_rule_clause(str(clause)))
    return predicates


def _predicate_name_from_clause(clause: str) -> str:
    text = str(clause or "").strip()
    match = re.match(r"\s*([a-zA-Z_][A-Za-z0-9_]*)\s*\(", text)
    return match.group(1) if match else ""


def _predicate_names_from_rule_clause(clause: str) -> set[str]:
    text = str(clause or "")
    names = {
        match.group(1)
        for match in re.finditer(r"\b([a-zA-Z_][A-Za-z0-9_]*)\s*\(", text)
    }
    return names


def _profile_hits_for_predicates(predicates: set[str], predicate_index: dict[str, set[str]]) -> dict[str, int]:
    hits: dict[str, int] = {}
    for profile_id, profile_predicates in predicate_index.items():
        count = len(predicates & profile_predicates)
        if count:
            hits[profile_id] = count
    return hits


def _known_profile_or_general(profile_id: str, catalog: dict[str, Any]) -> str:
    wanted = str(profile_id or "").strip()
    if wanted in {"", "general", "bootstrap"}:
        return "general"
    profiles = catalog.get("profiles", []) if isinstance(catalog, dict) else []
    for row in profiles if isinstance(profiles, list) else []:
        if not isinstance(row, dict):
            continue
        source = str(row.get("thick_context_source", "")).strip()
        if str(row.get("profile_id", "")).strip() == wanted and source and not source.startswith("future "):
            return wanted
    return "general"


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _interleaved_sample(cases: list[dict[str, Any]], *, count: int, rng: random.Random) -> list[dict[str, Any]]:
    by_source: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        by_source.setdefault(str(case.get("source") or "unknown"), []).append(case)
    for rows in by_source.values():
        rng.shuffle(rows)
    sources = sorted(by_source)
    rng.shuffle(sources)
    stream: list[dict[str, Any]] = []
    last_source = ""
    while len(stream) < count and any(by_source.values()):
        available = [source for source in sources if by_source.get(source) and source != last_source]
        if not available:
            available = [source for source in sources if by_source.get(source)]
        source = rng.choice(available)
        stream.append(by_source[source].pop())
        last_source = source
    return stream


def _write_record(out_path: Path, record: dict[str, Any]) -> None:
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _print_summary(records: list[dict[str, Any]], out_path: Path) -> None:
    total = len(records)
    router_ok = sum(1 for row in records if bool(row.get("router_ok")))
    parsed_ok = sum(1 for row in records if bool(row.get("compiler_parsed_ok")))
    router_scores = [
        float((row.get("router_eval") if isinstance(row.get("router_eval"), dict) else {}).get("score", 0.0) or 0.0)
        for row in records
    ]
    profiles: dict[str, int] = {}
    sources: dict[str, int] = {}
    anti_coupling_flags: dict[str, int] = {}
    for row in records:
        profiles[str(row.get("effective_profile"))] = profiles.get(str(row.get("effective_profile")), 0) + 1
        sources[str(row.get("source"))] = sources.get(str(row.get("source")), 0) + 1
        anti = row.get("anti_coupling") if isinstance(row.get("anti_coupling"), dict) else {}
        flags = anti.get("flags", []) if isinstance(anti, dict) else []
        for flag in flags if isinstance(flags, list) else []:
            if not isinstance(flag, dict):
                continue
            kind = str(flag.get("kind") or "unknown").strip()
            if kind:
                anti_coupling_flags[kind] = anti_coupling_flags.get(kind, 0) + 1
    print(f"Wrote {out_path}")
    average_router_score = (sum(router_scores) / len(router_scores)) if router_scores else 0.0
    print(
        f"router_ok={router_ok}/{total} router_score_avg={average_router_score:.3f} "
        f"compiler_parsed_ok={parsed_ok}/{total}"
    )
    print(f"profiles={dict(sorted(profiles.items()))}")
    print(f"sources={dict(sorted(sources.items()))}")
    if anti_coupling_flags:
        print(f"anti_coupling_flags={dict(sorted(anti_coupling_flags.items()))}")


def _default_out_path(seed: int) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return DEFAULT_OUT / f"semantic_router_agility_seed{seed}_{stamp}.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
