from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_semantic_router_agility import (  # noqa: E402
    _compiler_context_from_router,
    _evaluate_router,
    _known_profile_or_general,
)
from src.domain_profiles import (  # noqa: E402
    load_domain_profile_catalog,
    load_profile_package,
    profile_package_context,
    profile_package_contracts,
    thin_profile_roster,
)
from src.semantic_ir import SemanticIRCallConfig, call_semantic_ir, semantic_ir_to_legacy_parse  # noqa: E402
from src.semantic_router import SemanticRouterCallConfig, call_semantic_router  # noqa: E402


DEFAULT_OUT = REPO_ROOT / "tmp" / "multilingual_semantic_ir"


MULTILINGUAL_CASES: list[dict[str, Any]] = [
    {
        "id": "es_medication_state_update",
        "language": "es",
        "expected_profile": "medical@v0",
        "utterance": "Priya toma warfarina desde marzo; no es una recomendacion, solo un registro.",
        "context": ["Known patient: Priya.", "This is bounded clinical memory, not treatment advice."],
        "expected_pressure": "commit medication fact, no advice",
    },
    {
        "id": "es_vague_lab_clarification",
        "language": "es",
        "expected_profile": "medical@v0",
        "utterance": "La presion de Mara salio mala otra vez.",
        "context": ["Known patient: Mara."],
        "expected_pressure": "clarify which pressure/measurement is meant",
    },
    {
        "id": "fr_legal_claim_not_finding",
        "language": "fr",
        "expected_profile": "legal_courtlistener@v0",
        "utterance": "Dans Doe c. Acme, la plainte alleguait qu'Acme avait viole le bail, mais le tribunal a seulement constate que la plainte etait deposee a temps.",
        "context": ["Known case: Doe v. Acme.", "Complaints contain party allegations; court findings are separate."],
        "expected_pressure": "preserve allegation versus court finding",
    },
    {
        "id": "de_contract_obligation_exception",
        "language": "de",
        "expected_profile": "sec_contracts@v0",
        "utterance": "Jeder Premiumkunde muss vorrangigen Support erhalten, ausser wenn eine unbezahlte Rechnung aelter als zehn Tage ist.",
        "context": ["Policy intake. Obligations and exceptions are rules, not completed facts."],
        "expected_pressure": "rule/obligation semantics, not customer fact",
    },
    {
        "id": "pt_story_source_fidelity",
        "language": "pt",
        "expected_profile": "story_world@v0",
        "utterance": "Tres lontras moravam numa casa pequena perto do rio. A pequena lontra tinha uma caneca azul, a lontra media tinha botas verdes, e a grande lontra tinha um barco vermelho.",
        "context": ["Story-world source fidelity test. Preserve text-local names and colors."],
        "expected_pressure": "story facts with text-local entity names",
    },
    {
        "id": "ja_contract_conditional_right",
        "language": "ja",
        "expected_profile": "sec_contracts@v0",
        "utterance": "契約では、借り手が期限までに支払わない場合、貸し手は返済を加速できる。",
        "context": ["Contract clause intake. Conditional rights are not present-day events."],
        "expected_pressure": "conditional right, not repayment fact",
    },
    {
        "id": "it_probate_witness_rule",
        "language": "it",
        "expected_profile": "probate@v0",
        "utterance": "Arthur dice che il padre cambio il testamento in officina, ma erano presenti solo Arthur e il padre.",
        "context": [
            "Silverton probate setting.",
            "A verbal charter amendment requires two simultaneous non-beneficiary witnesses.",
        ],
        "expected_pressure": "probate amendment validity and witness insufficiency",
    },
    {
        "id": "spanglish_medical_side_effect",
        "language": "mixed",
        "expected_profile": "medical@v0",
        "utterance": "Priya no es alergica a metformin; solo le dio stomach upset, like nausea.",
        "context": ["Known patient: Priya.", "Existing KB may contain allergy(priya, metformin)."],
        "expected_pressure": "allergy versus side-effect correction",
    },
    {
        "id": "fr_legal_medical_source_conflict",
        "language": "fr",
        "expected_profile": "legal_courtlistener@v0",
        "utterance": "Le dossier de pharmacie montre que Priya a retire la warfarine lundi, mais le temoin affirme qu'elle ne l'a jamais prise.",
        "context": [
            "Legal evidence intake.",
            "Pharmacy logs are source records; witness statements are claims.",
            "Medical profile may normalize warfarin but should not own the legal provenance issue.",
        ],
        "expected_pressure": "legal source conflict with medical advisory terms",
    },
    {
        "id": "de_meeting_commitment_query",
        "language": "de",
        "expected_profile": "sec_contracts@v0",
        "utterance": "Maya versprach den Entwurf bis Freitag. Der Start haengt von der Freigabe durch Legal ab. Was blockiert den Start?",
        "context": ["Meeting-to-commitment demo. Commitments and dependencies are policy/obligation-like state."],
        "expected_pressure": "mixed direct commitments plus query",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run multilingual raw-language Semantic Router -> Semantic IR probes."
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--backend", choices=["lmstudio", "ollama"], default="lmstudio")
    parser.add_argument("--model", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--router-only", action="store_true")
    parser.add_argument("--include-model-input", action="store_true")
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
    out_path = args.out or _default_out_path()
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

    for index, case in enumerate(MULTILINGUAL_CASES, start=1):
        case_id = str(case["id"])
        expected = str(case["expected_profile"])
        utterance = str(case["utterance"])
        context = [str(item) for item in case.get("context", []) if str(item).strip()]
        print(f"[{index}/{len(MULTILINGUAL_CASES)}] {case_id} lang={case['language']} expected={expected}", flush=True)
        record: dict[str, Any] = {
            "ts": _utc_now(),
            "index": index,
            "case_id": case_id,
            "language": case.get("language"),
            "expected_profile": expected,
            "expected_pressure": case.get("expected_pressure"),
            "utterance": utterance,
            "context": context,
            "router_ok": False,
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
                kb_manifest={"note": "no live KB; multilingual raw utterance probe"},
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

            router_profile = str(router.get("selected_profile_id") or "general").strip() or "general"
            effective_profile = _known_profile_or_general(router_profile, catalog)
            record["router_profile"] = router_profile
            record["effective_profile"] = effective_profile
            router_eval = _evaluate_router(
                router,
                expected_profile=expected,
                effective_profile=effective_profile,
                catalog=catalog,
            )
            record["router_eval"] = router_eval
            record["router_ok"] = bool(router_eval.get("strict_ok"))

            if args.router_only:
                _write_record(out_path, record)
                records.append(record)
                continue

            profile = load_profile_package(effective_profile, catalog) if effective_profile != "general" else {}
            domain_context = profile_package_context(profile) if profile else []
            predicate_contracts = profile_package_contracts(profile) if profile else []
            allowed_predicates = [
                str(row.get("signature", "")).strip()
                for row in predicate_contracts
                if isinstance(row, dict) and str(row.get("signature", "")).strip()
            ]
            compiler_context = _compiler_context_from_router(router, context)
            compiler_context.append(
                "Multilingual probe: preserve source fidelity while normalizing entity atoms into safe Prolog-style identifiers."
            )
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


def _write_record(out_path: Path, record: dict[str, Any]) -> None:
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _print_summary(records: list[dict[str, Any]], out_path: Path) -> None:
    total = len(records)
    router_ok = sum(1 for row in records if bool(row.get("router_ok")))
    parsed_ok = sum(1 for row in records if bool(row.get("compiler_parsed_ok")))
    profiles: dict[str, int] = {}
    languages: dict[str, int] = {}
    for row in records:
        profiles[str(row.get("effective_profile"))] = profiles.get(str(row.get("effective_profile")), 0) + 1
        languages[str(row.get("language"))] = languages.get(str(row.get("language")), 0) + 1
    scores = [
        float((row.get("router_eval") if isinstance(row.get("router_eval"), dict) else {}).get("score", 0.0) or 0.0)
        for row in records
    ]
    avg_score = (sum(scores) / len(scores)) if scores else 0.0
    print(f"Wrote {out_path}")
    print(
        f"router_ok={router_ok}/{total} router_score_avg={avg_score:.3f} "
        f"compiler_parsed_ok={parsed_ok}/{total}"
    )
    print(f"profiles={dict(sorted(profiles.items()))}")
    print(f"languages={dict(sorted(languages.items()))}")


def _default_out_path() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return DEFAULT_OUT / f"multilingual_semantic_ir_{stamp}.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
