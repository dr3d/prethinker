#!/usr/bin/env python3
"""Run a broad Semantic IR "lava" sweep across mixed scenario sources.

This is a research harness, not a locked regression suite. It tries to make the
Semantic IR compiler uncomfortable by mixing domains, carrying KB state through
the stream, perturbing utterances, and repeating temperature-0 runs so we can
see when the local model/server is still nondeterministic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_mixed_domain_agility import build_mixed_cases  # noqa: E402
from src.mcp_server import PrologMCPServer  # noqa: E402
from src.semantic_ir import semantic_ir_to_legacy_parse  # noqa: E402


DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "semantic_ir_lava_sweep"
DEFAULT_FRONTIER_PACK_DIR = REPO_ROOT / "docs" / "data" / "frontier_packs"
DEFAULT_DATASET_GLOBS = (
    "datasets/courtlistener/samples/*.jsonl",
    "datasets/courtlistener/generated/*.jsonl",
    "datasets/sec_edgar/samples/*.jsonl",
    "datasets/sec_edgar/generated/*.jsonl",
)
DEFAULT_KB_SCENARIO_GLOBS = (
    "kb_scenarios/story_*.json",
    "kb_scenarios/rung_4*.json",
    "kb_scenarios/stage_00_*.json",
    "kb_scenarios/acid_*.json",
)


@dataclass(frozen=True)
class LavaCase:
    id: str
    source: str
    utterance: str
    context: tuple[str, ...] = ()
    expected_profile: str = ""
    expected_decision: str = ""
    allowed_predicates: tuple[str, ...] = ()
    predicate_contracts: tuple[dict[str, Any], ...] = ()
    expect: dict[str, Any] | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hammer Semantic IR with a broad mixed-domain lava sweep.")
    parser.add_argument("--limit", type=int, default=48, help="Maximum base cases before variants/repeats.")
    parser.add_argument("--repeats", type=int, default=2, help="Repeated temp-0 passes used for variance checks.")
    parser.add_argument("--seed", type=int, default=8675309)
    parser.add_argument("--sample-mode", choices=["balanced", "random"], default="balanced")
    parser.add_argument("--variants", default="original,typo,bad_grammar,context_switch")
    parser.add_argument("--state-mode", choices=["stream", "isolated"], default="stream")
    parser.add_argument("--backend", choices=["lmstudio", "ollama"], default="lmstudio")
    parser.add_argument("--model", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p-values", default="0.82", help="Comma-separated top_p values to run.")
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--thinking", action="store_true")
    parser.add_argument("--selector-only", action="store_true")
    parser.add_argument("--no-apply", action="store_true", help="Compile/map but do not mutate/query the runtime KB.")
    parser.add_argument(
        "--source-filter",
        default="",
        help="Optional case-insensitive substring filter applied to LavaCase.source or id before sampling.",
    )
    parser.add_argument(
        "--execute-queries",
        action="store_true",
        help="Also execute admitted queries. Off by default because recursive toy-Prolog queries can monopolize CPU.",
    )
    parser.add_argument("--include-model-input", action="store_true")
    parser.add_argument("--include-tmp", action="store_true", help="Also mine tmp/scenarios JSON files.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rng = random.Random(int(args.seed))
    variants = [item.strip() for item in str(args.variants).split(",") if item.strip()]
    top_p_values = [float(item.strip()) for item in str(args.top_p_values).split(",") if item.strip()]
    loaded_cases = filter_lava_cases(
        load_lava_cases(include_tmp=bool(args.include_tmp)),
        source_filter=str(args.source_filter or ""),
    )
    if not loaded_cases:
        raise SystemExit(f"No lava cases matched source filter: {args.source_filter!r}")
    base_cases = select_base_cases(loaded_cases, limit=int(args.limit), mode=str(args.sample_mode), rng=rng)
    stream = expand_variants(base_cases, variants=variants, rng=rng)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug_model = _slug(args.model or ("qwen/qwen3.6-35b-a3b" if args.backend == "lmstudio" else "qwen3.6:35b"))
    out_jsonl = out_dir / f"semantic_ir_lava_sweep_{stamp}_{slug_model}.jsonl"
    out_md = out_dir / f"semantic_ir_lava_sweep_{stamp}_{slug_model}.md"

    all_records: list[dict[str, Any]] = []
    for top_p in top_p_values:
        for repeat in range(1, max(1, int(args.repeats)) + 1):
            server = None
            if args.state_mode == "stream":
                server = make_server(args, top_p=top_p)
            order = list(stream)
            # Keep order stable by repeat so variance reflects model/server behavior, not shuffling.
            for index, case in enumerate(order, start=1):
                if args.state_mode == "isolated" or server is None:
                    server = make_server(args, top_p=top_p)
                record = run_case(
                    server,
                    case=case,
                    index=index,
                    repeat=repeat,
                    top_p=top_p,
                    args=args,
                )
                all_records.append(record)
                with out_jsonl.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                print(
                    f"[top_p={top_p} repeat={repeat}/{args.repeats} {index}/{len(order)}] "
                    f"{case.id}#{case.source}/{case.expect and case.expect.get('variant') or 'original'} "
                    f"profile={record.get('selected_profile')} decision={record.get('projected_decision')} "
                    f"admit={record.get('admitted_count')} fuzzy={record.get('fuzzy_edge_count')} "
                    f"stable_key={record.get('signature_hash')[:10]}",
                    flush=True,
                )

    summary = summarize_records(all_records, base_case_count=len(base_cases), variants=variants, args=args)
    out_md.write_text(summary, encoding="utf-8")
    print(f"Wrote {out_jsonl}")
    print(f"Wrote {out_md}")
    print(summary)
    return 0


def make_server(args: argparse.Namespace, *, top_p: float) -> PrologMCPServer:
    backend = str(args.backend or "lmstudio").strip().lower()
    model = str(args.model or "").strip()
    if not model:
        model = "qwen/qwen3.6-35b-a3b" if backend == "lmstudio" else "qwen3.6:35b"
    base_url = str(args.base_url or "").strip()
    if not base_url:
        base_url = "http://127.0.0.1:1234" if backend == "lmstudio" else "http://127.0.0.1:11434"
    return PrologMCPServer(
        compiler_prompt_enabled=False,
        semantic_ir_enabled=True,
        compiler_backend=backend,
        compiler_base_url=base_url,
        semantic_ir_model=model,
        semantic_ir_context_length=int(args.num_ctx),
        semantic_ir_timeout=int(args.timeout),
        semantic_ir_temperature=float(args.temperature),
        semantic_ir_top_p=float(top_p),
        semantic_ir_top_k=int(args.top_k),
        semantic_ir_thinking=bool(args.thinking),
        active_profile="auto",
    )


def run_case(
    server: PrologMCPServer,
    *,
    case: LavaCase,
    index: int,
    repeat: int,
    top_p: float,
    args: argparse.Namespace,
) -> dict[str, Any]:
    started = time.perf_counter()
    selected = server._semantic_ir_selected_profile_for_utterance(case.utterance, context=list(case.context)) or "general"
    allowed_predicates = _merge_ordered_strings(
        server._semantic_ir_allowed_predicates(selected),
        list(case.allowed_predicates),
    )
    predicate_contracts = _merge_contracts(
        server._semantic_ir_predicate_contracts(selected),
        list(case.predicate_contracts),
    )
    record: dict[str, Any] = {
        "ts": _utc_now(),
        "index": index,
        "repeat": repeat,
        "case_id": case.id,
        "source": case.source,
        "variant": (case.expect or {}).get("variant", "original"),
        "top_p": top_p,
        "temperature": float(args.temperature),
        "top_k": int(args.top_k),
        "utterance": case.utterance,
        "context": list(case.context),
        "expected_profile": case.expected_profile,
        "expected_decision": case.expected_decision,
        "selected_profile": selected,
        "selector_ok": (not case.expected_profile) or selected == case.expected_profile,
        "profile_selection": server._last_semantic_ir_profile_selection,
        "parsed_ok": False,
        "model_decision": "",
        "projected_decision": "",
        "admitted_count": 0,
        "skipped_count": 0,
        "fuzzy_edge_count": 0,
        "execution_status": "",
        "writes_applied": 0,
        "errors": [],
        "signature": {},
        "signature_hash": "",
    }
    if bool(args.selector_only):
        record["parsed_ok"] = None
        record["signature"] = signature_for(record)
        record["signature_hash"] = _hash_json(record["signature"])
        return record

    try:
        ir, error = server._compile_semantic_ir(
            case.utterance,
            context=list(case.context),
            allowed_predicates_override=allowed_predicates or None,
            predicate_contracts_override=predicate_contracts or None,
        )
        trace = server._last_semantic_ir_trace if isinstance(server._last_semantic_ir_trace, dict) else {}
        record["selected_profile"] = str(trace.get("selected_profile") or selected or "general")
        record["profile_selection"] = trace.get("profile_selection", record["profile_selection"])
        record["latency_ms"] = int(trace.get("latency_ms", 0) or 0)
        record["raw_message_excerpt"] = str(trace.get("raw_message", ""))[:1000]
        if args.include_model_input:
            record["model_input"] = trace.get("model_input", {})
        else:
            record["model_input_manifest"] = _compact_model_input_manifest(trace.get("model_input", {}))
        if error:
            record["errors"].append(error)
        if not isinstance(ir, dict):
            record["signature"] = signature_for(record)
            record["signature_hash"] = _hash_json(record["signature"])
            return record
        mapped, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=allowed_predicates or trace.get("model_input", {}).get("allowed_predicates", []),
            predicate_contracts=predicate_contracts or trace.get("model_input", {}).get("predicate_contracts", []),
        )
        diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
        clauses = diagnostics.get("clauses", {}) if isinstance(diagnostics.get("clauses"), dict) else {}
        alignment = diagnostics.get("truth_maintenance_alignment", {})
        fuzzy_edges = alignment.get("fuzzy_edges", []) if isinstance(alignment, dict) else []
        epistemic_worlds = diagnostics.get("epistemic_worlds", {})
        record.update(
            {
                "parsed_ok": True,
                "model_decision": str(ir.get("decision", "")),
                "projected_decision": str(diagnostics.get("projected_decision", "")),
                "admitted_count": int(diagnostics.get("admitted_count", 0) or 0),
                "skipped_count": int(diagnostics.get("skipped_count", 0) or 0),
                "warning_counts": diagnostics.get("warning_counts", {}),
                "mapper_warnings": warnings,
                "clauses": clauses,
                "truth_maintenance": ir.get("truth_maintenance", {}),
                "truth_maintenance_alignment": alignment,
                "epistemic_worlds": _compact_epistemic_worlds(epistemic_worlds),
                "fuzzy_edge_count": len(fuzzy_edges),
                "fuzzy_edge_kinds": _fuzzy_edge_kinds(fuzzy_edges),
            }
        )
        if not bool(args.no_apply):
            execution = apply_mapped_directly(server, mapped, execute_queries=bool(args.execute_queries))
            record["execution_status"] = str(execution.get("status", ""))
            record["writes_applied"] = int(execution.get("writes_applied", 0) or 0)
            record["execution_errors"] = execution.get("errors", [])
            record["execution_ops"] = _compact_execution_ops(execution.get("operations", []))
        record["expectation_score"] = score_expectation(case, record, ir=ir)
        record["signature"] = signature_for(record)
        record["signature_hash"] = _hash_json(record["signature"])
    except Exception as exc:
        record["errors"].append(str(exc))
        record["signature"] = signature_for(record)
        record["signature_hash"] = _hash_json(record["signature"])
    finally:
        record["elapsed_ms"] = int((time.perf_counter() - started) * 1000)
    return record


def load_lava_cases(*, include_tmp: bool = False) -> list[LavaCase]:
    cases: list[LavaCase] = []
    for row in build_mixed_cases():
        cases.append(case_from_mapping(row, source=str(row.get("source") or "mixed")))
    cases.extend(load_frontier_pack_cases(DEFAULT_FRONTIER_PACK_DIR))
    for pattern in DEFAULT_DATASET_GLOBS:
        cases.extend(load_jsonl_cases(REPO_ROOT / pattern))
    for pattern in DEFAULT_KB_SCENARIO_GLOBS:
        cases.extend(load_kb_scenario_cases(REPO_ROOT / pattern))
    if include_tmp:
        cases.extend(load_kb_scenario_cases(REPO_ROOT / "tmp" / "scenarios" / "*.json"))
    return dedupe_cases(cases)


def apply_mapped_directly(
    server: PrologMCPServer,
    mapped: dict[str, Any],
    *,
    execute_queries: bool = False,
) -> dict[str, Any]:
    """Apply admitted clauses to this runner's private runtime without front-door gating."""

    intent = str(mapped.get("intent", "")).strip()
    clauses = mapped.get("admission_diagnostics", {}).get("clauses", {})
    if not isinstance(clauses, dict):
        clauses = {}
    facts = [str(item).strip() for item in clauses.get("facts", []) if str(item).strip()]
    rules = [str(item).strip() for item in clauses.get("rules", []) if str(item).strip()]
    retracts = [str(item).strip() for item in clauses.get("retracts", []) if str(item).strip()]
    queries = [str(item).strip() for item in clauses.get("queries", []) if str(item).strip()]
    operations: list[dict[str, Any]] = []
    errors: list[str] = []
    writes_applied = 0

    def remember(tool: str, clause: str = "", query: str = "", result: dict[str, Any] | None = None) -> None:
        nonlocal writes_applied
        row = {"tool": tool, "result": result or {}}
        if clause:
            row["clause"] = clause
        if query:
            row["query"] = query
        operations.append(row)
        status = str((result or {}).get("status", "")).strip()
        if tool in {"assert_fact", "assert_rule", "retract_fact"} and status == "success":
            writes_applied += 1
        if status and status not in {"success", "no_results", "no_result", "skipped"}:
            errors.append(f"{tool} failed for {clause or query}: {status}")

    for clause in retracts:
        normalized = clause if clause.endswith(".") else f"{clause}."
        remember("retract_fact", clause=normalized, result=server.retract_fact(normalized))
    if intent in {"assert_fact", "assert_rule", "retract", "query"}:
        for clause in facts:
            remember("assert_fact", clause=clause, result=server.assert_fact(clause))
        for clause in rules:
            remember("assert_rule", clause=clause, result=server.assert_rule(clause))
        for query in queries[:1]:
            if execute_queries:
                remember("query_rows", query=query, result=server.query_rows(query))
            else:
                remember(
                    "query_rows",
                    query=query,
                    result={
                        "status": "skipped",
                        "result_type": "query_execution_disabled",
                        "message": "Lava sweep recorded the query but did not execute it.",
                    },
                )
    elif not operations:
        operations.append({"tool": "none", "result": {"status": "skipped", "message": f"Intent={intent or 'other'}"}})
    return {
        "status": "success" if not errors else "error",
        "intent": intent,
        "writes_applied": writes_applied,
        "operations": operations,
        "errors": errors,
    }


def select_base_cases(cases: list[LavaCase], *, limit: int, mode: str, rng: random.Random) -> list[LavaCase]:
    rows = list(cases)
    rng.shuffle(rows)
    if limit <= 0 or limit >= len(rows):
        return rows
    if mode != "balanced":
        return rows[:limit]
    buckets: dict[str, list[LavaCase]] = defaultdict(list)
    for case in rows:
        buckets[source_family(case.source)].append(case)
    for bucket in buckets.values():
        rng.shuffle(bucket)
    families = sorted(buckets)
    rng.shuffle(families)
    picked: list[LavaCase] = []
    while len(picked) < limit and any(buckets.values()):
        for family in list(families):
            if len(picked) >= limit:
                break
            bucket = buckets.get(family) or []
            if bucket:
                picked.append(bucket.pop())
    return picked


def filter_lava_cases(cases: list[LavaCase], *, source_filter: str = "") -> list[LavaCase]:
    needle = str(source_filter or "").strip().lower()
    if not needle:
        return list(cases)
    return [
        case
        for case in cases
        if needle in case.source.lower() or needle in case.id.lower()
    ]


def source_family(source: str) -> str:
    raw = str(source or "unknown")
    if raw.startswith("kb_scenario:"):
        name = raw.split(":", 1)[1]
        if name.startswith("story_"):
            return "kb_story"
        if name.startswith("rung_"):
            return "kb_rung"
        if name.startswith("acid_"):
            return "kb_acid"
        if name.startswith("stage_"):
            return "kb_stage"
        return "kb_scenario"
    if raw.startswith("frontier:"):
        return "frontier_pack"
    if raw.startswith("dataset:"):
        return "dataset"
    return raw


def case_from_mapping(row: dict[str, Any], *, source: str = "") -> LavaCase:
    expect = row.get("expect") if isinstance(row.get("expect"), dict) else {}
    expected_decision = str(row.get("expected_decision") or expect.get("decision") or "")
    return LavaCase(
        id=str(row.get("id") or _short_hash(str(row.get("utterance") or ""))),
        source=source or str(row.get("source") or row.get("domain") or "unknown"),
        utterance=str(row.get("utterance") or ""),
        context=tuple(str(item) for item in row.get("context", []) if str(item).strip()),
        expected_profile=str(row.get("expected_profile") or ""),
        expected_decision=expected_decision,
        allowed_predicates=tuple(str(item) for item in row.get("allowed_predicates", []) if str(item).strip()),
        predicate_contracts=tuple(item for item in row.get("predicate_contracts", []) if isinstance(item, dict)),
        expect=expect or None,
    )


def load_frontier_pack_cases(root: Path) -> list[LavaCase]:
    out: list[LavaCase] = []
    if not root.exists():
        return out
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = data.get("cases", []) if isinstance(data, dict) else []
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            profile = profile_for_domain(str(row.get("domain") or ""))
            enriched = dict(row)
            enriched["expected_profile"] = profile
            out.append(case_from_mapping(enriched, source=f"frontier:{path.stem}"))
    return out


def load_jsonl_cases(pattern: Path) -> list[LavaCase]:
    out: list[LavaCase] = []
    for path in sorted(pattern.parent.glob(pattern.name)):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if isinstance(row, dict) and str(row.get("utterance") or "").strip():
                row = dict(row)
                row["expected_profile"] = row.get("expected_profile") or profile_for_domain(str(row.get("domain") or ""))
                out.append(case_from_mapping(row, source=f"dataset:{path.stem}"))
    return out


def load_kb_scenario_cases(pattern: Path) -> list[LavaCase]:
    out: list[LavaCase] = []
    for path in sorted(pattern.parent.glob(pattern.name)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        utterances = data.get("utterances", [])
        if not isinstance(utterances, list):
            continue
        rolling_context: list[str] = []
        for idx, item in enumerate(utterances, start=1):
            utterance = str(item.get("utterance") if isinstance(item, dict) else item).strip()
            if not utterance:
                continue
            if len(utterance) > 1800:
                # Full stories are useful, but for lava sweeps the long-form path
                # belongs in dedicated full-story runners.
                utterance = utterance[:1800].rsplit(" ", 1)[0] + " ..."
            case_id = f"{path.stem}_turn_{idx:03d}"
            profile = profile_for_scenario_name(path.stem, utterance)
            out.append(
                LavaCase(
                    id=case_id,
                    source=f"kb_scenario:{path.stem}",
                    utterance=utterance,
                    context=tuple(rolling_context[-5:]),
                    expected_profile=profile,
                )
            )
            if len(rolling_context) < 12:
                rolling_context.append(utterance)
    return out


def expand_variants(cases: list[LavaCase], *, variants: list[str], rng: random.Random) -> list[LavaCase]:
    out: list[LavaCase] = []
    for case in cases:
        for variant in variants:
            out.append(variant_case(case, variant=variant, rng=rng))
    return out


def variant_case(case: LavaCase, *, variant: str, rng: random.Random) -> LavaCase:
    variant = variant.strip().lower() or "original"
    if variant == "original":
        utterance = case.utterance
        context = list(case.context)
    elif variant == "typo":
        utterance = inject_typos(case.utterance)
        context = list(case.context)
    elif variant == "bad_grammar":
        utterance = degrade_grammar(case.utterance)
        context = list(case.context)
    elif variant == "context_switch":
        distractor = rng.choice(
            [
                "Previous unrelated thread: Priya takes warfarin and asked a medical dosing question.",
                "Previous unrelated thread: Doe v. Acme has a complaint allegation and a separate court finding.",
                "Previous unrelated thread: A borrower default clause was discussed in a credit agreement.",
                "Previous unrelated thread: Goldilocks entered a house in the woods.",
            ]
        )
        utterance = case.utterance
        context = [distractor, *case.context]
    else:
        utterance = case.utterance
        context = list(case.context)
    expect = dict(case.expect or {})
    expect["variant"] = variant
    return LavaCase(
        id=f"{case.id}__{variant}",
        source=case.source,
        utterance=utterance,
        context=tuple(context),
        expected_profile=case.expected_profile,
        expected_decision=case.expected_decision,
        allowed_predicates=case.allowed_predicates,
        predicate_contracts=case.predicate_contracts,
        expect=expect,
    )


TYPO_REPLACEMENTS = {
    "the": "teh",
    "their": "thier",
    "patient": "patint",
    "pressure": "presure",
    "correction": "corection",
    "actually": "actualy",
    "alleged": "aleged",
    "complaint": "complant",
    "default": "defalt",
    "borrower": "borower",
    "agreement": "agrement",
    "unless": "unles",
    "because": "becuz",
    "London": "Londn",
    "medical": "medcal",
    "shares": "shars",
}


def inject_typos(text: str) -> str:
    out = str(text)
    for src, dst in TYPO_REPLACEMENTS.items():
        out = re.sub(rf"\b{re.escape(src)}\b", dst, out, flags=re.IGNORECASE if src.islower() else 0)
    return out


def degrade_grammar(text: str) -> str:
    out = str(text).lower()
    out = re.sub(r"[,;:.!?]+", " ", out)
    out = re.sub(r"\s+", " ", out).strip()
    out = out.replace(" is ", " be ").replace(" are ", " be ").replace(" was ", " were ")
    return "uh " + out if out else out


def profile_for_domain(domain: str) -> str:
    lower = domain.lower()
    if "bootstrap" in lower or "unexpected" in lower:
        return "bootstrap"
    if "medical" in lower or "umls" in lower:
        return "medical@v0"
    if "courtlistener" in lower or "legal_courtlistener" in lower:
        return "legal_courtlistener@v0"
    if "sec" in lower or "contract" in lower or "financial" in lower:
        return "sec_contracts@v0"
    if "probate" in lower or "estate" in lower:
        return "probate@v0"
    if "story" in lower or "glitch" in lower or "goldilocks" in lower:
        return "story_world@v0"
    return ""


def profile_for_scenario_name(name: str, utterance: str) -> str:
    text = f"{name} {utterance}".lower()
    if "glitch" in text or "goldilocks" in text or "story" in text:
        return "story_world@v0"
    if "medical" in text or "warfarin" in text or "creatinine" in text:
        return "medical@v0"
    if "lease" in text or "court" in text or "appeal" in text or "probate" in text:
        return "legal_courtlistener@v0"
    if "contract" in text or "borrower" in text or "sec" in text:
        return "sec_contracts@v0"
    return ""


def dedupe_cases(cases: Iterable[LavaCase]) -> list[LavaCase]:
    out: list[LavaCase] = []
    seen: set[str] = set()
    for case in cases:
        if not case.utterance.strip():
            continue
        key = _hash_json({"u": case.utterance, "c": list(case.context), "p": case.expected_profile})
        if key in seen:
            continue
        seen.add(key)
        out.append(case)
    return out


def score_expectation(case: LavaCase, record: dict[str, Any], *, ir: dict[str, Any]) -> dict[str, Any]:
    expect = case.expect or {}
    diagnostic_text = json.dumps(
        {
            "ir": ir,
            "clauses": record.get("clauses", {}),
            "warnings": record.get("mapper_warnings", []),
            "fuzzy": record.get("fuzzy_edge_kinds", []),
        },
        ensure_ascii=False,
        sort_keys=True,
    ).lower()
    clauses = record.get("clauses", {}) if isinstance(record.get("clauses"), dict) else {}
    asserted_clauses = {
        "facts": clauses.get("facts", []),
        "rules": clauses.get("rules", []),
    }
    retract_clauses = {"retracts": clauses.get("retracts", [])}
    query_clauses = {"queries": clauses.get("queries", [])}
    asserted_text = json.dumps(asserted_clauses, ensure_ascii=False, sort_keys=True).lower()
    retract_text = json.dumps(retract_clauses, ensure_ascii=False, sort_keys=True).lower()
    query_text = json.dumps(query_clauses, ensure_ascii=False, sort_keys=True).lower()
    diagnostic_surfaces = _expectation_surfaces(diagnostic_text)
    asserted_surfaces = _expectation_surfaces(asserted_text)
    retract_surfaces = _expectation_surfaces(retract_text)
    query_surfaces = _expectation_surfaces(query_text)
    must = [str(item).lower() for item in expect.get("must", []) if str(item).strip()]
    avoid = [str(item).lower() for item in expect.get("avoid", []) if str(item).strip()]
    must_hits = [item for item in must if _expectation_contains(diagnostic_surfaces, item)]
    missing_must = [item for item in must if not _expectation_contains(diagnostic_surfaces, item)]
    avoid_hits = [item for item in avoid if _expectation_contains(diagnostic_surfaces, item)]
    avoid_asserted_hits = [item for item in avoid if _expectation_contains(asserted_surfaces, item)]
    avoid_retract_hits = [item for item in avoid if _expectation_contains(retract_surfaces, item)]
    avoid_query_hits = [item for item in avoid if _expectation_contains(query_surfaces, item)]
    expected_decision = case.expected_decision
    decision_ok = not expected_decision or str(record.get("projected_decision", "")) == expected_decision
    must_ok = len(must_hits) == len(must)
    semantic_clean = not avoid_hits
    admission_safe = not avoid_asserted_hits
    return {
        "decision_ok": decision_ok,
        "must_hits": len(must_hits),
        "must_total": len(must),
        "missing_must": missing_must,
        "avoid_hits": avoid_hits,
        "avoid_asserted_hits": avoid_asserted_hits,
        "avoid_retract_hits": avoid_retract_hits,
        # Backward-compatible alias: in expectation scoring, durable unsafe hits
        # mean forbidden asserted facts/rules, not retractions that remove them.
        "avoid_durable_hits": avoid_asserted_hits,
        "avoid_query_hits": avoid_query_hits,
        # Backward-compatible alias for older ad hoc analysis scripts.
        "avoid_admitted_hits": avoid_asserted_hits,
        "semantic_clean": semantic_clean,
        "admission_safe": admission_safe,
        "ok": bool(decision_ok and must_ok and admission_safe),
    }


def _expectation_surfaces(text: str) -> set[str]:
    raw = str(text or "").lower()
    underscored = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    compact = re.sub(r"[^a-z0-9]+", "", raw)
    colon_time = re.sub(r"\b(\d{1,2})[:_](\d{2})\b", r"\1_\2", raw)
    return {raw, underscored, compact, colon_time}


def _expectation_contains(surfaces: set[str], needle: str) -> bool:
    raw = str(needle or "").lower().strip()
    if not raw:
        return False
    variants = _expectation_surfaces(raw)
    return any(
        variant and any(variant in surface for surface in surfaces)
        for variant in variants
    )


def signature_for(record: dict[str, Any]) -> dict[str, Any]:
    clauses = record.get("clauses", {}) if isinstance(record.get("clauses"), dict) else {}
    worlds = record.get("epistemic_worlds", {}) if isinstance(record.get("epistemic_worlds"), dict) else {}
    return {
        "selected_profile": record.get("selected_profile", ""),
        "model_decision": record.get("model_decision", ""),
        "projected_decision": record.get("projected_decision", ""),
        "facts": sorted(str(item) for item in clauses.get("facts", []) if str(item).strip()),
        "retracts": sorted(str(item) for item in clauses.get("retracts", []) if str(item).strip()),
        "rules": sorted(str(item) for item in clauses.get("rules", []) if str(item).strip()),
        "queries": sorted(str(item) for item in clauses.get("queries", []) if str(item).strip()),
        "world_clauses": sorted(str(item) for item in worlds.get("clauses", []) if str(item).strip()),
        "fuzzy": sorted(str(item) for item in record.get("fuzzy_edge_kinds", []) if str(item).strip()),
        "error": "; ".join(str(item) for item in record.get("errors", [])),
    }


def _merge_ordered_strings(*groups: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group or []:
            text = str(item).strip()
            key = text.lower()
            if text and key not in seen:
                out.append(text)
                seen.add(key)
    return out


def _merge_contracts(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for group in groups:
        for item in group or []:
            if not isinstance(item, dict):
                continue
            signature = str(item.get("signature") or "").strip()
            key = signature.lower() if signature else json.dumps(item, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                out.append(dict(item))
                seen.add(key)
    return out


def summarize_records(
    records: list[dict[str, Any]],
    *,
    base_case_count: int,
    variants: list[str],
    args: argparse.Namespace,
) -> str:
    total = len(records)
    parsed_ok = sum(1 for row in records if row.get("parsed_ok") is True)
    selector_checked = [row for row in records if row.get("expected_profile")]
    selector_ok = sum(1 for row in selector_checked if row.get("selector_ok"))
    expectation_rows = [
        row
        for row in records
        if isinstance(row.get("expectation_score"), dict)
        and row.get("expectation_score", {}).get("must_total", 0) > 0
    ]
    expectation_ok = sum(1 for row in expectation_rows if row.get("expectation_score", {}).get("ok"))
    semantic_clean = sum(1 for row in expectation_rows if row.get("expectation_score", {}).get("semantic_clean"))
    admission_safe = sum(1 for row in expectation_rows if row.get("expectation_score", {}).get("admission_safe"))
    expectation_misses = [
        row for row in expectation_rows if not row.get("expectation_score", {}).get("ok")
    ][:12]
    projected = Counter(str(row.get("projected_decision") or "none") for row in records)
    profiles = Counter(str(row.get("selected_profile") or "none") for row in records)
    sources = Counter(source_family(str(row.get("source") or "none")) for row in records)
    world_rows = [
        row
        for row in records
        if isinstance(row.get("epistemic_worlds"), dict)
        and int(row.get("epistemic_worlds", {}).get("operation_count", 0) or 0) > 0
    ]
    world_operation_count = sum(
        int(row.get("epistemic_worlds", {}).get("operation_count", 0) or 0)
        for row in world_rows
    )
    fuzzy = Counter()
    for row in records:
        fuzzy.update(str(item) for item in row.get("fuzzy_edge_kinds", []) if str(item).strip())
    variance_groups: dict[tuple[Any, ...], set[str]] = defaultdict(set)
    for row in records:
        key = (row.get("case_id"), row.get("top_p"), row.get("variant"))
        variance_groups[key].add(str(row.get("signature_hash") or ""))
    unstable = {key: hashes for key, hashes in variance_groups.items() if len(hashes) > 1}
    worst_fuzzy = sorted(
        records,
        key=lambda row: (int(row.get("fuzzy_edge_count", 0) or 0), int(row.get("skipped_count", 0) or 0)),
        reverse=True,
    )[:12]
    unstable_examples = list(unstable.items())[:12]
    lines = [
        "# Semantic IR Lava Sweep",
        "",
        f"- Generated: {_utc_now()}",
        f"- Base cases: {base_case_count}",
        f"- Variants: {', '.join(variants)}",
        f"- Attempts: {total}",
        f"- Backend/model: {args.backend} / {args.model or ('qwen/qwen3.6-35b-a3b' if args.backend == 'lmstudio' else 'qwen3.6:35b')}",
        f"- Temperature/top_p/top_k: {args.temperature} / {args.top_p_values} / {args.top_k}",
        f"- State mode: {args.state_mode}",
        "",
        "## Headline",
        "",
        f"- Parsed JSON: {parsed_ok}/{total}",
        f"- Domain selector: {selector_ok}/{len(selector_checked)} checked",
        f"- Expectation score: {expectation_ok}/{len(expectation_rows)} checked",
        f"- Expectation semantic-clean: {semantic_clean}/{len(expectation_rows)} checked",
        f"- Expectation admission-safe: {admission_safe}/{len(expectation_rows)} checked",
        f"- Epistemic scoped-memory records: {len(world_rows)}/{total} records, {world_operation_count} scoped operation(s)",
        f"- Temp-0 variance groups: {len(unstable)}/{len(variance_groups)} unstable",
        "",
        "## Expectation Miss Examples",
        "",
    ]
    if expectation_misses:
        for row in expectation_misses:
            score = row.get("expectation_score", {})
            missing = ", ".join(str(item) for item in score.get("missing_must", [])[:4]) or "none"
            durable = ", ".join(str(item) for item in score.get("avoid_durable_hits", [])[:4]) or "none"
            query = ", ".join(str(item) for item in score.get("avoid_query_hits", [])[:4]) or "none"
            lines.append(
                f"- `{row.get('case_id')}` variant={row.get('variant')} "
                f"decision={row.get('projected_decision')}/{row.get('expected_decision')} "
                f"must={score.get('must_hits')}/{score.get('must_total')} "
                f"missing=[{missing}] durable_avoid=[{durable}] query_avoid=[{query}]"
            )
    else:
        lines.append("- None.")
    lines.extend([
        "",
        "## Decision Mix",
        "",
        json.dumps(dict(projected.most_common()), indent=2, sort_keys=True),
        "",
        "## Profile Mix",
        "",
        json.dumps(dict(profiles.most_common()), indent=2, sort_keys=True),
        "",
        "## Source Mix",
        "",
        json.dumps(dict(sources.most_common()), indent=2, sort_keys=True),
        "",
        "## Fuzzy Edge Kinds",
        "",
        json.dumps(dict(fuzzy.most_common(20)), indent=2, sort_keys=True),
        "",
        "## Highest Fuzzy/Skipped Records",
        "",
    ])
    if worst_fuzzy:
        for row in worst_fuzzy:
            lines.append(
                f"- `{row.get('case_id')}` repeat={row.get('repeat')} variant={row.get('variant')} "
                f"profile={row.get('selected_profile')} decision={row.get('projected_decision')} "
                f"fuzzy={row.get('fuzzy_edge_count')} skipped={row.get('skipped_count')}"
            )
    else:
        lines.append("- None.")
    lines.extend(["", "## Temp-0 Variance Examples", ""])
    if unstable_examples:
        for (case_id, top_p, variant), hashes in unstable_examples:
            lines.append(f"- `{case_id}` top_p={top_p} variant={variant}: {len(hashes)} signatures")
    else:
        lines.append("- No signature variance detected in repeated groups.")
    lines.append("")
    return "\n".join(lines)


def _compact_model_input_manifest(model_input: Any) -> dict[str, Any]:
    if not isinstance(model_input, dict):
        return {}
    kb_pack = model_input.get("kb_context_pack", {}) if isinstance(model_input.get("kb_context_pack"), dict) else {}
    manifest = kb_pack.get("manifest", {}) if isinstance(kb_pack.get("manifest"), dict) else {}
    return {
        "domain": model_input.get("domain"),
        "context_count": len(model_input.get("context", []) or []),
        "domain_context_count": len(model_input.get("domain_context", []) or []),
        "allowed_predicate_count": len(model_input.get("allowed_predicates", []) or []),
        "predicate_contract_count": len(model_input.get("predicate_contracts", []) or []),
        "kb_context_manifest": manifest,
        "options": model_input.get("options", {}),
    }


def _compact_epistemic_worlds(worlds: Any) -> dict[str, Any]:
    if not isinstance(worlds, dict):
        return {}
    compact_worlds: list[dict[str, Any]] = []
    raw_worlds = worlds.get("worlds", [])
    if isinstance(raw_worlds, list):
        for world in raw_worlds:
            if not isinstance(world, dict):
                continue
            compact_worlds.append(
                {
                    "world_id": world.get("world_id"),
                    "world_type": world.get("world_type"),
                    "operation_count": len(world.get("operations", []) or []),
                }
            )
    return {
        "version": worlds.get("version"),
        "authority": worlds.get("authority"),
        "world_count": int(worlds.get("world_count", 0) or 0),
        "operation_count": int(worlds.get("operation_count", 0) or 0),
        "clauses": [str(item) for item in worlds.get("clauses", []) if str(item).strip()],
        "worlds": compact_worlds,
    }


def _compact_execution_ops(operations: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(operations, list):
        return out
    for op in operations:
        if not isinstance(op, dict):
            continue
        result = op.get("result", {}) if isinstance(op.get("result"), dict) else {}
        out.append(
            {
                "tool": op.get("tool"),
                "clause": op.get("clause"),
                "query": op.get("query"),
                "status": result.get("status"),
                "result_type": result.get("result_type"),
            }
        )
    return out


def _fuzzy_edge_kinds(edges: Any) -> list[str]:
    kinds: list[str] = []
    if not isinstance(edges, list):
        return kinds
    for edge in edges:
        if isinstance(edge, dict):
            kinds.append(str(edge.get("kind") or edge.get("reason") or edge.get("label") or "fuzzy_edge"))
        else:
            kinds.append(str(edge))
    return kinds


def _hash_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _short_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8", errors="replace")).hexdigest()[:12]


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(value)).strip("-")[:80] or "model"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
