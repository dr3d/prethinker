#!/usr/bin/env python3
"""Run Silverton as an incremental semantic IR story.

This is different from the guardrail A/B runner. Each turn sends:

- the new utterance as the focused item to process;
- shared Silverton rules;
- the natural-language story so far;
- previously admitted mapper clauses.

Raw model outputs stay under tmp/ because they are local research traces.
"""

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

from scripts.run_semantic_ir_prompt_bakeoff import (  # noqa: E402
    SILVERTON_SCENARIO_IDS,
    WILD_SCENARIOS,
    score_record,
)
from src.semantic_ir import (  # noqa: E402
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
)


DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "silverton_incremental_semantic_ir"

SILVERTON_SHARED_CONTEXT = [
    "Story setting: Elias Silverton was a reclusive clockmaker whose estate is in probate.",
    (
        "Charter rule: the inheritance is split 50/50 between Arthur and Beatrice unless a "
        "beneficiary resided outside the country for more than five consecutive years."
    ),
    (
        "Forfeiture rule: a beneficiary who triggers the outside-country condition forfeits "
        "their share to the Silverton Clock Restoration Fund."
    ),
    (
        "Amendment rule: verbal changes to the Charter are valid only if witnessed by two "
        "non-beneficiaries simultaneously."
    ),
    "Known people: Arthur Silverton, Beatrice Silverton, Alfred Silverton, Silas the gardener.",
    "Known ambiguity: London may mean London, Ontario or London, UK.",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _silverton_scenarios() -> list[dict[str, Any]]:
    by_id = {str(row.get("id", "")): row for row in WILD_SCENARIOS}
    return [by_id[scenario_id] for scenario_id in SILVERTON_SCENARIO_IDS]


def _allowed_predicates(scenarios: list[dict[str, Any]]) -> list[str]:
    values: set[str] = set()
    for scenario in scenarios:
        for item in scenario.get("allowed_predicates", []):
            text = str(item).strip()
            if text:
                values.add(text)
    return sorted(values)


def build_incremental_context(
    *,
    story_so_far: list[str],
    admitted_clauses: list[str],
    scenario_context: list[str],
) -> list[str]:
    context = list(SILVERTON_SHARED_CONTEXT)
    for item in scenario_context:
        text = str(item).strip()
        if text and text not in context:
            context.append(text)
    if story_so_far:
        context.append("Story so far, in order:")
        context.extend([f"{idx + 1}. {line}" for idx, line in enumerate(story_so_far)])
    if admitted_clauses:
        context.append("Previously admitted mapper clauses:")
        context.extend(admitted_clauses[-24:])
    context.append(
        "Focus instruction: process only the new utterance as the proposed update; use story so far only for context."
    )
    return context


def _clause_preview(parsed: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("facts", "rules", "queries", "correction_retract_clauses"):
        values = parsed.get(key, []) if isinstance(parsed, dict) else []
        if not isinstance(values, list):
            continue
        for item in values:
            text = str(item).strip()
            if text:
                out.append(text)
    return out


def _rough_token_count(value: Any) -> int:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return max(1, len(text) // 4)


def run_incremental(
    *,
    backend: str,
    base_url: str,
    model: str,
    timeout: int,
    max_tokens: int,
    context_length: int,
) -> list[dict[str, Any]]:
    config = SemanticIRCallConfig(
        backend=backend,
        base_url=base_url,
        model=model,
        timeout=timeout,
        max_tokens=max_tokens,
        context_length=context_length,
    )
    scenarios = _silverton_scenarios()
    allowed_predicates = _allowed_predicates(scenarios)
    story_so_far: list[str] = []
    admitted_clauses: list[str] = []
    records: list[dict[str, Any]] = []

    for index, scenario in enumerate(scenarios, start=1):
        utterance = str(scenario.get("utterance", "")).strip()
        context = build_incremental_context(
            story_so_far=story_so_far,
            admitted_clauses=admitted_clauses,
            scenario_context=[
                str(item).strip()
                for item in scenario.get("context", [])
                if str(item).strip()
            ],
        )
        prompt_footprint = {
            "context_items": len(context),
            "story_so_far_lines": len(story_so_far),
            "admitted_clause_count": len(admitted_clauses),
            "rough_context_tokens": _rough_token_count(context),
            "rough_utterance_tokens": _rough_token_count(utterance),
            "rough_allowed_predicate_tokens": _rough_token_count(allowed_predicates),
            "configured_context_length": context_length,
        }
        print(f"[{_utc_now()}] step {index}: {scenario['id']}")
        error = ""
        try:
            result = call_semantic_ir(
                utterance=utterance,
                config=config,
                context=context,
                allowed_predicates=allowed_predicates,
                domain="silverton_incremental_probate",
                include_model_input=True,
            )
        except Exception as exc:
            result = {"latency_ms": 0, "content": "", "parsed": None, "raw": {}}
            error = str(exc)
        parsed = result.get("parsed") if isinstance(result, dict) else None
        mapped: dict[str, Any] = {}
        warnings: list[str] = []
        if isinstance(parsed, dict):
            mapped, warnings = semantic_ir_to_legacy_parse(parsed)
            for clause in _clause_preview(mapped):
                if clause not in admitted_clauses:
                    admitted_clauses.append(clause)
        score = score_record(parsed if isinstance(parsed, dict) else None, scenario)
        records.append(
            {
                "step": index,
                "scenario_id": str(scenario.get("id", "")),
                "utterance": utterance,
                "context": context,
                "allowed_predicates": allowed_predicates,
                "latency_ms": int(result.get("latency_ms", 0) or 0),
                "model_input": result.get("model_input", {}),
                "content": str(result.get("content", "")),
                "parsed": parsed if isinstance(parsed, dict) else None,
                "parse_error": error,
                "mapped": mapped,
                "mapper_warnings": warnings,
                "score": score,
                "prompt_footprint": prompt_footprint,
                "story_so_far_size": len(story_so_far),
                "admitted_clause_count": len(admitted_clauses),
            }
        )
        story_so_far.append(utterance)
        admitted_clauses = admitted_clauses[-48:]
    return records


def write_outputs(records: list[dict[str, Any]], jsonl_path: Path) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    decision_ok = sum(1 for row in records if row.get("score", {}).get("decision_ok"))
    schema_ok = sum(1 for row in records if row.get("score", {}).get("schema_ok"))
    avg_score = sum(float(row.get("score", {}).get("rough_score", 0.0)) for row in records) / max(1, len(records))
    avg_latency = sum(int(row.get("latency_ms", 0) or 0) for row in records) / max(1, len(records))
    max_context_tokens = max(
        int((row.get("prompt_footprint", {}) or {}).get("rough_context_tokens", 0) or 0)
        for row in records
    ) if records else 0
    lines = [
        "# Silverton Incremental Semantic IR",
        "",
        f"Generated: {_utc_now()}",
        "",
        "## Aggregate",
        "",
        "| Runs | Schema OK | Decision OK | Avg rough score | Avg latency ms |",
        "|---:|---:|---:|---:|---:|",
        f"| {len(records)} | {schema_ok} | {decision_ok} | {avg_score:.3f} | {avg_latency:.0f} |",
        "",
        f"Max rough context tokens: `{max_context_tokens}`.",
        "",
        "## Cases",
        "",
        "| Step | Scenario | Expected | Actual | Score | Context tokens | Admitted clauses |",
        "|---:|---|---|---|---:|---:|---:|",
    ]
    for record in records:
        score = record.get("score", {})
        mapped = record.get("mapped", {}) if isinstance(record.get("mapped"), dict) else {}
        diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
        lines.append(
            f"| {record['step']} | `{record['scenario_id']}` | "
            f"`{score.get('expected_decision', '')}` | `{score.get('decision', '')}` | "
            f"{float(score.get('rough_score', 0.0)):.2f} | "
            f"{int((record.get('prompt_footprint', {}) or {}).get('rough_context_tokens', 0) or 0)} | "
            f"{int(diagnostics.get('admitted_count', 0) or 0)} |"
        )
    lines.extend(
        [
            "",
            "## Consumption Shape",
            "",
            "Each step sends the current utterance as the focused update, with shared Silverton rules, natural-language story-so-far, and admitted mapper clauses in context.",
            "",
            "## Files",
            "",
            f"- JSONL: `{jsonl_path.name}`",
        ]
    )
    jsonl_path.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["ollama", "lmstudio"], default="lmstudio")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backend = str(args.backend or "lmstudio").strip().lower()
    base_url = str(args.base_url or "").strip()
    if not base_url:
        base_url = "http://127.0.0.1:1234" if backend == "lmstudio" else "http://127.0.0.1:11434"
    model = str(args.model or "").strip()
    if not model:
        model = "qwen/qwen3.6-35b-a3b" if backend == "lmstudio" else "qwen3.6:35b"
    run_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jsonl_path = Path(args.out_dir) / f"silverton_incremental_{run_slug}.jsonl"
    records = run_incremental(
        backend=backend,
        base_url=base_url,
        model=model,
        timeout=int(args.timeout),
        max_tokens=int(args.max_tokens),
        context_length=int(args.num_ctx),
    )
    write_outputs(records, jsonl_path)
    print(f"Wrote {jsonl_path}")
    print(f"Wrote {jsonl_path.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
