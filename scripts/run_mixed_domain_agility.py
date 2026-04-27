from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_semantic_ir_prompt_bakeoff import (  # noqa: E402
    HARBOR_FRONTIER_SCENARIO_IDS,
    SILVERTON_NOISY_SCENARIO_IDS,
    SILVERTON_SCENARIO_IDS,
    WILD_SCENARIOS,
)
from src.mcp_server import PrologMCPServer  # noqa: E402
from src.semantic_ir import semantic_ir_to_legacy_parse  # noqa: E402


DEFAULT_OUT = REPO_ROOT / "tmp" / "mixed_domain_agility"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a randomized mixed-domain Semantic IR agility stream.")
    parser.add_argument("--count", type=int, default=16)
    parser.add_argument("--seed", type=int, default=2701)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--backend", choices=["lmstudio", "ollama"], default="lmstudio")
    parser.add_argument("--model", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--selector-only", action="store_true", help="Skip model calls and only test auto selection.")
    parser.add_argument("--include-model-input", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rng = random.Random(int(args.seed))
    cases = build_mixed_cases()
    stream = _interleaved_sample(cases, count=max(1, int(args.count)), rng=rng)
    out_path = args.out or _default_out_path(args.seed)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

    backend = str(args.backend or "lmstudio").strip().lower()
    model = str(args.model or "").strip()
    if not model:
        model = "qwen/qwen3.6-35b-a3b" if backend == "lmstudio" else "qwen3.6:35b"
    base_url = str(args.base_url or "").strip()
    if not base_url:
        base_url = "http://127.0.0.1:1234" if backend == "lmstudio" else "http://127.0.0.1:11434"

    server = PrologMCPServer(
        compiler_prompt_enabled=False,
        semantic_ir_enabled=True,
        compiler_backend=backend,
        compiler_base_url=base_url,
        semantic_ir_model=model,
        semantic_ir_context_length=int(args.num_ctx),
        semantic_ir_timeout=int(args.timeout),
        active_profile="auto",
    )
    records: list[dict[str, Any]] = []
    for index, case in enumerate(stream, start=1):
        case_id = str(case.get("id") or f"mixed_{index:04d}")
        expected = str(case.get("expected_profile") or "")
        print(f"[{index}/{len(stream)}] {case_id} expected={expected}", flush=True)
        turn_context = [str(item) for item in case.get("context", []) if str(item).strip()]
        selection = server._semantic_ir_selected_profile_for_utterance(
            str(case.get("utterance") or ""),
            context=turn_context,
        )
        selected = selection or "general"
        record: dict[str, Any] = {
            "ts": _utc_now(),
            "index": index,
            "case_id": case_id,
            "source": case.get("source"),
            "expected_profile": expected,
            "selector_profile": selected,
            "selector_ok": not expected or selected == expected,
            "profile_selection": server._last_semantic_ir_profile_selection,
            "utterance": case.get("utterance"),
            "context": case.get("context", []),
            "parsed_ok": None,
            "model_decision": None,
            "projected_decision": None,
            "admitted_count": 0,
            "skipped_count": 0,
            "error": "",
        }
        if not args.selector_only:
            try:
                ir, error = server._compile_semantic_ir(
                    str(case.get("utterance") or ""),
                    context=turn_context,
                )
                trace = server._last_semantic_ir_trace
                record["selector_profile"] = trace.get("selected_profile")
                record["selector_ok"] = not expected or trace.get("selected_profile") == expected
                record["profile_selection"] = trace.get("profile_selection")
                record["model_input"] = trace.get("model_input") if bool(args.include_model_input) else {}
                record["latency_ms"] = trace.get("latency_ms")
                if error:
                    record["error"] = error
                if isinstance(ir, dict):
                    mapped, warnings = semantic_ir_to_legacy_parse(
                        ir,
                        allowed_predicates=trace.get("model_input", {}).get("allowed_predicates", []),
                        predicate_contracts=trace.get("model_input", {}).get("predicate_contracts", []),
                    )
                    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
                    record.update(
                        {
                            "parsed_ok": True,
                            "model_decision": ir.get("decision"),
                            "projected_decision": diagnostics.get("projected_decision"),
                            "admitted_count": diagnostics.get("admitted_count", 0),
                            "skipped_count": diagnostics.get("skipped_count", 0),
                            "warning_counts": diagnostics.get("warning_counts", {}),
                            "clauses": diagnostics.get("clauses", {}),
                            "mapper_warnings": warnings,
                            "parsed": ir,
                        }
                    )
                else:
                    record["parsed_ok"] = False
            except Exception as exc:
                record["parsed_ok"] = False
                record["error"] = str(exc)
        records.append(record)
        with out_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    _print_summary(records, out_path)
    return 0


def build_mixed_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    cases.extend(_goldilocks_cases())
    cases.extend(_wild_cases("glitch_", "story_world@v0", "glitch"))
    cases.extend(_wild_cases("ledger_", "probate@v0", "ledger"))
    cases.extend(_wild_ids(SILVERTON_SCENARIO_IDS + SILVERTON_NOISY_SCENARIO_IDS, "probate@v0", "silverton"))
    cases.extend(_harbor_cases())
    cases.extend(_dataset_cases(REPO_ROOT / "datasets" / "courtlistener" / "samples" / "legal_seed_synthetic_5.jsonl", "legal_courtlistener@v0", "courtlistener"))
    cases.extend(_dataset_cases(REPO_ROOT / "datasets" / "sec_edgar" / "samples" / "sec_contracts_synthetic_5.jsonl", "sec_contracts@v0", "sec_contracts"))
    cases.extend(_wild_medical_cases())
    return cases


def _wild_cases(prefix: str, expected_profile: str, source: str) -> list[dict[str, Any]]:
    return [
        _case_from_wild(row, expected_profile=expected_profile, source=source)
        for row in WILD_SCENARIOS
        if str(row.get("id", "")).startswith(prefix)
    ]


def _wild_ids(ids: list[str], expected_profile: str, source: str) -> list[dict[str, Any]]:
    wanted = set(ids)
    return [
        _case_from_wild(row, expected_profile=expected_profile, source=source)
        for row in WILD_SCENARIOS
        if str(row.get("id", "")) in wanted
    ]


def _harbor_cases() -> list[dict[str, Any]]:
    wanted = set(HARBOR_FRONTIER_SCENARIO_IDS)
    return [
        _case_from_wild(row, expected_profile=_expected_harbor_profile(row), source="harbor")
        for row in WILD_SCENARIOS
        if str(row.get("id", "")) in wanted
    ]


def _expected_harbor_profile(row: dict[str, Any]) -> str:
    scenario_id = str(row.get("id") or "")
    domain = str(row.get("domain") or "")
    if scenario_id == "harbor_clinical_advice_inside_legal_turn":
        return "medical@v0"
    if domain == "harbor_house_governance":
        return "sec_contracts@v0"
    return "legal_courtlistener@v0"


def _wild_medical_cases() -> list[dict[str, Any]]:
    ids = {
        "vague_pressure_bad",
        "warfarin_hold_tonight",
        "repeat_it_high",
        "spanglish_allergy",
        "metformin_correction",
        "pressure_sugar_weird_add_it",
        "edge_temporal_correction_warfarin",
        "edge_comparative_measurement_direction",
        "edge_scope_negation_allergy",
        "weak_medical_negation_side_effect",
        "weak_medical_negation_intolerance",
    }
    return [
        _case_from_wild(row, expected_profile="medical@v0", source="medical")
        for row in WILD_SCENARIOS
        if str(row.get("id", "")) in ids
    ]


def _case_from_wild(row: dict[str, Any], *, expected_profile: str, source: str) -> dict[str, Any]:
    return {
        "id": str(row.get("id") or ""),
        "source": source,
        "expected_profile": expected_profile,
        "utterance": str(row.get("utterance") or ""),
        "context": [str(item) for item in row.get("context", []) if str(item).strip()]
    }


def _dataset_cases(path: Path, expected_profile: str, source: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "id": str(row.get("id") or ""),
                "source": source,
                "expected_profile": expected_profile,
                "utterance": str(row.get("utterance") or ""),
                "context": [str(item) for item in row.get("context", []) if str(item).strip()],
            }
        )
    return out


def _goldilocks_cases() -> list[dict[str, Any]]:
    path = REPO_ROOT / "stories" / "goldilocks_and_the_three_bears.txt"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    sentences = [item.strip() for item in text.replace("\r", " ").replace("\n", " ").split(".") if item.strip()]
    chunks = [". ".join(sentences[i : i + 3]).strip() + "." for i in range(0, min(len(sentences), 12), 3)]
    return [
        {
            "id": f"goldilocks_chunk_{index:02d}",
            "source": "goldilocks",
            "expected_profile": "story_world@v0",
            "utterance": chunk,
            "context": ["Source: Goldilocks and the Three Bears story-world ingestion stressor."],
        }
        for index, chunk in enumerate(chunks, start=1)
        if chunk.strip()
    ]


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
        available = [src for src in sources if by_source.get(src) and src != last_source]
        if not available:
            available = [src for src in sources if by_source.get(src)]
        src = rng.choice(available)
        stream.append(by_source[src].pop())
        last_source = src
    return stream


def _print_summary(records: list[dict[str, Any]], out_path: Path) -> None:
    total = len(records)
    selector_ok = sum(1 for row in records if bool(row.get("selector_ok")))
    parsed_ok = sum(1 for row in records if bool(row.get("parsed_ok")))
    profiles: dict[str, int] = {}
    sources: dict[str, int] = {}
    for row in records:
        profiles[str(row.get("selector_profile"))] = profiles.get(str(row.get("selector_profile")), 0) + 1
        sources[str(row.get("source"))] = sources.get(str(row.get("source")), 0) + 1
    print(f"Wrote {out_path}")
    print(f"selector_ok={selector_ok}/{total} parsed_ok={parsed_ok}/{total}")
    print(f"profiles={dict(sorted(profiles.items()))}")
    print(f"sources={dict(sorted(sources.items()))}")


def _default_out_path(seed: int) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return DEFAULT_OUT / f"mixed_domain_agility_seed{seed}_{stamp}.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
