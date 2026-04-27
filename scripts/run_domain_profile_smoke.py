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

from src.domain_profiles import (
    load_domain_profile_catalog,
    load_profile_package,
    profile_package_context,
    profile_package_contracts,
    thin_profile_roster,
)
from src.semantic_ir import SemanticIRCallConfig, call_semantic_ir, semantic_ir_to_legacy_parse


DEFAULT_OUT = Path("tmp") / "domain_profile_smoke"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run profile-backed Semantic IR smoke traces over JSONL cases.")
    parser.add_argument("--dataset", action="append", required=True, help="JSONL harness dataset. Repeatable.")
    parser.add_argument("--profile-id", required=True, help="Domain profile package id, e.g. legal_courtlistener@v0.")
    parser.add_argument("--domain", default="", help="Domain label to send in the semantic IR input.")
    parser.add_argument("--limit-per-dataset", type=int, default=0)
    parser.add_argument("--backend", choices=["ollama", "lmstudio"], default="lmstudio")
    parser.add_argument("--model", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--out", type=Path, default=None)
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

    profile_id = str(args.profile_id or "").strip()
    catalog = load_domain_profile_catalog()
    profile = load_profile_package(profile_id, catalog)
    if not profile:
        raise SystemExit(f"profile not found or has no package: {profile_id}")
    domain_context = profile_package_context(profile)
    profile_contracts = profile_package_contracts(profile)
    roster = thin_profile_roster(catalog)

    cases = _load_cases([Path(item) for item in args.dataset], limit_per_dataset=max(0, args.limit_per_dataset))
    if not cases:
        raise SystemExit("no cases loaded")

    out_path = args.out or _default_out_path(profile_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

    config = SemanticIRCallConfig(
        backend=backend,
        base_url=base_url,
        model=model,
        context_length=int(args.num_ctx),
        timeout=int(args.timeout),
        max_tokens=int(args.max_tokens),
    )
    domain = str(args.domain or "").strip() or _domain_from_profile_id(profile_id)
    summaries: list[dict[str, Any]] = []

    for index, case in enumerate(cases, start=1):
        case_id = str(case.get("id") or f"case_{index:04d}")
        print(f"[{index}/{len(cases)}] {case_id}", flush=True)
        allowed_predicates = _string_list(case.get("allowed_predicates"))
        predicate_contracts = case.get("predicate_contracts")
        if not isinstance(predicate_contracts, list) or not predicate_contracts:
            predicate_contracts = profile_contracts
        context = _string_list(case.get("context"))
        utterance = str(case.get("utterance") or "").strip()
        record: dict[str, Any] = {
            "ts": _utc_now(),
            "case_id": case_id,
            "domain": str(case.get("domain") or domain),
            "profile_id": profile_id,
            "backend": backend,
            "model": model,
            "source_dataset": str(case.get("_source_dataset") or ""),
            "expected_decision": case.get("expected_decision"),
            "admission_expectations": case.get("admission_expectations", {}),
            "utterance": utterance,
        }
        try:
            response = call_semantic_ir(
                utterance=utterance,
                config=config,
                context=context,
                domain_context=domain_context,
                available_domain_profiles=roster,
                allowed_predicates=allowed_predicates,
                predicate_contracts=predicate_contracts,
                domain=str(case.get("domain") or domain),
                include_model_input=bool(args.include_model_input),
            )
            parsed = response.get("parsed")
            mapped: dict[str, Any] = {}
            warnings: list[str] = []
            if isinstance(parsed, dict):
                mapped, warnings = semantic_ir_to_legacy_parse(parsed, allowed_predicates=allowed_predicates)
            diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
            record.update(
                {
                    "latency_ms": response.get("latency_ms"),
                    "parsed_ok": isinstance(parsed, dict),
                    "parsed": parsed,
                    "mapped": mapped,
                    "mapper_warnings": warnings,
                    "model_input": response.get("model_input"),
                    "summary": _summarize_record(parsed, mapped),
                    "admission_diagnostics": diagnostics,
                }
            )
        except Exception as exc:
            record.update({"parsed_ok": False, "error": str(exc), "summary": {"error": str(exc)}})
        summaries.append(record["summary"])
        with out_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    _print_summary(summaries, out_path)
    return 0


def _load_cases(paths: list[Path], *, limit_per_dataset: int) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in paths:
        rows: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if isinstance(row, dict):
                row["_source_dataset"] = str(path)
                rows.append(row)
        if limit_per_dataset:
            rows = rows[:limit_per_dataset]
        cases.extend(rows)
    return cases


def _summarize_record(parsed: Any, mapped: dict[str, Any]) -> dict[str, Any]:
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    clauses = diagnostics.get("clauses", {}) if isinstance(diagnostics, dict) else {}
    features = diagnostics.get("features", {}) if isinstance(diagnostics, dict) else {}
    return {
        "model_decision": parsed.get("decision") if isinstance(parsed, dict) else None,
        "projected_decision": diagnostics.get("projected_decision") if isinstance(diagnostics, dict) else None,
        "admitted_count": diagnostics.get("admitted_count") if isinstance(diagnostics, dict) else 0,
        "skipped_count": diagnostics.get("skipped_count") if isinstance(diagnostics, dict) else 0,
        "facts": clauses.get("facts", []) if isinstance(clauses, dict) else [],
        "rules": clauses.get("rules", []) if isinstance(clauses, dict) else [],
        "queries": clauses.get("queries", []) if isinstance(clauses, dict) else [],
        "warning_counts": diagnostics.get("warning_counts", {}) if isinstance(diagnostics, dict) else {},
        "features": features,
    }


def _print_summary(summaries: list[dict[str, Any]], out_path: Path) -> None:
    total = len(summaries)
    parsed = sum(1 for row in summaries if "error" not in row)
    admitted = sum(int(row.get("admitted_count") or 0) for row in summaries)
    skipped = sum(int(row.get("skipped_count") or 0) for row in summaries)
    decisions: dict[str, int] = {}
    projected: dict[str, int] = {}
    for row in summaries:
        decisions[str(row.get("model_decision"))] = decisions.get(str(row.get("model_decision")), 0) + 1
        projected[str(row.get("projected_decision"))] = projected.get(str(row.get("projected_decision")), 0) + 1
    print(f"Wrote {out_path}")
    print(f"parsed={parsed}/{total} admitted={admitted} skipped={skipped}")
    print(f"model_decisions={dict(sorted(decisions.items()))}")
    print(f"projected_decisions={dict(sorted(projected.items()))}")


def _default_out_path(profile_id: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_profile = profile_id.replace("@", "_").replace("/", "_")
    return DEFAULT_OUT / f"{safe_profile}_{stamp}.jsonl"


def _domain_from_profile_id(profile_id: str) -> str:
    return profile_id.split("@", 1)[0] if profile_id else "runtime"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
