#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kb_pipeline import _call_model_prompt, _parse_model_json  # noqa: E402
from src import umls_mvp  # noqa: E402


DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3.5:9b"
DEFAULT_CONTEXT = 32768
DEFAULT_TIMEOUT = 180
DEFAULT_TEMPERATURE = 0.2
DEFAULT_BATCH_SIZE = 8
DEFAULT_PROMPT = ROOT / "modelfiles" / "medical_ontology_prospector_prompt.md"
DEFAULT_CORPUS = ROOT / "docs" / "data" / "medical_ontology_prospector_corpus.json"
DEFAULT_SLICE_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp"
DEFAULT_OUT_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp" / "ontology_prospector_latest"

EXISTING_PALETTE = [
    "taking/2",
    "has_condition/2",
    "has_symptom/2",
    "has_allergy/2",
    "underwent_lab_test/2",
    "lab_result_high/2",
    "lab_result_rising/2",
    "lab_result_abnormal/2",
    "pregnant/1",
]


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _chunked(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    chunk_size = max(1, int(size))
    return [items[index : index + chunk_size] for index in range(0, len(items), chunk_size)]


def _render_case(case: dict[str, Any]) -> str:
    lines = [
        f"CASE_ID: {str(case.get('case_id', '')).strip()}",
        f"SOURCE: {str(case.get('source', '')).strip()}",
        f"UTTERANCE: {str(case.get('utterance', '')).strip()}",
    ]
    clarification = str(case.get("clarification_answer", "")).strip()
    if clarification:
        lines.append(f"CLARIFICATION_ANSWER: {clarification}")
    return "\n".join(lines)


def _render_concept_hints(batch: list[dict[str, Any]], alias_records: list[dict[str, Any]], concept_rows: list[dict[str, Any]]) -> str:
    by_seed_id = {str(row.get("seed_id", "")).strip(): row for row in concept_rows}
    matched_seed_ids: list[str] = []
    for case in batch:
        text = " ".join(
            part
            for part in [
                str(case.get("utterance", "")).strip(),
                str(case.get("clarification_answer", "")).strip(),
            ]
            if part
        )
        for match in umls_mvp.extract_grounded_mentions(text, alias_records):
            seed_id = str(match.get("seed_id", "")).strip()
            if seed_id and seed_id not in matched_seed_ids:
                matched_seed_ids.append(seed_id)
    if not matched_seed_ids:
        return "RELEVANT_CONCEPT_HINTS:\n- none"
    lines = ["RELEVANT_CONCEPT_HINTS:"]
    for seed_id in matched_seed_ids[:24]:
        row = by_seed_id.get(seed_id, {})
        preferred_name = str(row.get("preferred_name", "")).strip()
        semantic_types = ", ".join(
            sorted(
                {
                    str(item.get("sty", "")).strip()
                    for item in row.get("semantic_types", []) or []
                    if str(item.get("sty", "")).strip()
                }
            )
        )
        aliases = ", ".join(
            sorted(
                {
                    str(item.get("text", "")).strip()
                    for item in row.get("aliases", []) or []
                    if str(item.get("text", "")).strip()
                }
            )[:6]
        )
        lines.append(
            f"- {seed_id}: preferred='{preferred_name}'"
            + (f"; semantic_types={semantic_types}" if semantic_types else "")
            + (f"; aliases={aliases}" if aliases else "")
        )
    return "\n".join(lines)


def _build_prompt(base_prompt: str, batch: list[dict[str, Any]], alias_records: list[dict[str, Any]], concept_rows: list[dict[str, Any]]) -> str:
    case_lines = ["BATCH_CASES:"]
    for case in batch:
        case_lines.append(_render_case(case))
        case_lines.append("---")
    return (
        base_prompt.strip()
        + "\n\n"
        + "EXISTING_CANONICAL_PALETTE:\n"
        + "\n".join(f"- {item}" for item in EXISTING_PALETTE)
        + "\n\n"
        + _render_concept_hints(batch, alias_records, concept_rows)
        + "\n\n"
        + "\n".join(case_lines).strip()
        + "\n"
    )


def _normalize_string_list(values: Any, *, atomize_items: bool = False, limit: int = 12) -> list[str]:
    results: list[str] = []
    if not isinstance(values, list):
        return results
    for item in values:
        text = str(item or "").strip()
        if not text:
            continue
        normalized = umls_mvp.atomize(text) if atomize_items else text
        if normalized not in results:
            results.append(normalized)
        if len(results) >= limit:
            break
    return results


def _normalize_candidate(candidate: dict[str, Any]) -> dict[str, Any] | None:
    name = umls_mvp.atomize(candidate.get("name", ""))
    if not name:
        return None
    try:
        arity = int(candidate.get("arity", 0))
    except Exception:
        arity = 0
    if arity <= 0:
        return None
    decision = str(candidate.get("decision", "add_new")).strip() or "add_new"
    merge_target = umls_mvp.atomize(candidate.get("merge_target", "")) if decision == "merge_into_existing" else ""
    try:
        confidence = float(candidate.get("confidence", 0.0))
    except Exception:
        confidence = 0.0
    if confidence < 0.0:
        confidence = 0.0
    if confidence > 1.0:
        confidence = 1.0
    return {
        "name": name,
        "arity": arity,
        "arguments": _normalize_string_list(candidate.get("arguments", []), atomize_items=True),
        "semantic_types": _normalize_string_list(candidate.get("semantic_types", []), atomize_items=False),
        "surface_forms": _normalize_string_list(candidate.get("surface_forms", []), atomize_items=False),
        "example_case_ids": _normalize_string_list(candidate.get("example_case_ids", []), atomize_items=False),
        "decision": decision,
        "merge_target": merge_target,
        "confidence": round(confidence, 4),
        "rationale": str(candidate.get("rationale", "")).strip(),
    }


def _run_batch(
    *,
    prompt_text: str,
    base_url: str,
    model: str,
    context_length: int,
    timeout: int,
    temperature: float,
    think_enabled: bool,
) -> tuple[dict[str, Any] | None, str]:
    response = _call_model_prompt(
        backend="ollama",
        base_url=base_url,
        model=model,
        prompt_text=prompt_text,
        context_length=context_length,
        timeout=timeout,
        api_key=None,
        response_format="json",
        temperature=temperature,
        think_enabled=think_enabled,
    )
    return _parse_model_json(response, ["candidate_predicates", "rejected_patterns"])


def _aggregate_batches(batch_summaries: list[dict[str, Any]], total_cases: int) -> dict[str, Any]:
    by_key: dict[tuple[str, int], dict[str, Any]] = {}
    rejected_counter: Counter[tuple[str, str]] = Counter()
    coverage_notes: list[str] = []

    for batch in batch_summaries:
        parsed = batch.get("parsed") or {}
        coverage_notes.extend(str(note).strip() for note in parsed.get("coverage_notes", []) or [] if str(note).strip())
        for rejected in parsed.get("rejected_patterns", []) or []:
            pattern = str(rejected.get("pattern", "")).strip()
            reason = str(rejected.get("reason", "")).strip()
            if pattern:
                rejected_counter[(pattern, reason)] += 1
        for raw_candidate in parsed.get("candidate_predicates", []) or []:
            normalized = _normalize_candidate(raw_candidate)
            if not normalized:
                continue
            key = (normalized["name"], normalized["arity"])
            entry = by_key.setdefault(
                key,
                {
                    "name": normalized["name"],
                    "arity": normalized["arity"],
                    "support_case_ids": set(),
                    "arguments": Counter(),
                    "semantic_types": Counter(),
                    "surface_forms": Counter(),
                    "decisions": Counter(),
                    "merge_targets": Counter(),
                    "confidence_total": 0.0,
                    "confidence_count": 0,
                    "rationale_samples": [],
                },
            )
            entry["support_case_ids"].update(normalized["example_case_ids"])
            entry["arguments"][tuple(normalized["arguments"])] += 1
            for item in normalized["semantic_types"]:
                entry["semantic_types"][item] += 1
            for item in normalized["surface_forms"]:
                entry["surface_forms"][item] += 1
            entry["decisions"][normalized["decision"]] += 1
            if normalized["merge_target"]:
                entry["merge_targets"][normalized["merge_target"]] += 1
            entry["confidence_total"] += normalized["confidence"]
            entry["confidence_count"] += 1
            if normalized["rationale"] and normalized["rationale"] not in entry["rationale_samples"]:
                entry["rationale_samples"].append(normalized["rationale"])

    candidates: list[dict[str, Any]] = []
    for entry in by_key.values():
        support_case_ids = sorted(str(item) for item in entry["support_case_ids"])
        predominant_arguments = list(entry["arguments"].most_common(1)[0][0]) if entry["arguments"] else []
        candidates.append(
            {
                "name": entry["name"],
                "arity": entry["arity"],
                "signature": f"{entry['name']}/{entry['arity']}",
                "support_case_ids": support_case_ids,
                "support_count": len(support_case_ids),
                "arguments": predominant_arguments,
                "semantic_types": [item for item, _ in entry["semantic_types"].most_common(8)],
                "surface_forms": [item for item, _ in entry["surface_forms"].most_common(12)],
                "decision_counts": dict(entry["decisions"]),
                "merge_targets": dict(entry["merge_targets"]),
                "average_confidence": round(
                    entry["confidence_total"] / float(entry["confidence_count"] or 1),
                    4,
                ),
                "rationale_samples": entry["rationale_samples"][:3],
                "existing_palette": f"{entry['name']}/{entry['arity']}" in EXISTING_PALETTE,
            }
        )

    candidates.sort(key=lambda row: (-row["support_count"], -row["average_confidence"], row["signature"]))

    rejected_patterns = [
        {"pattern": pattern, "reason": reason, "count": count}
        for (pattern, reason), count in rejected_counter.most_common()
    ]

    convergence = {
        "total_cases": total_cases,
        "unique_candidate_predicates": len(candidates),
        "predicate_case_ratio": round(len(candidates) / float(total_cases or 1), 4),
        "multi_case_predicates": sum(1 for row in candidates if row["support_count"] >= 2),
        "single_case_predicates": sum(1 for row in candidates if row["support_count"] == 1),
        "existing_palette_hits": sum(1 for row in candidates if row["existing_palette"]),
    }

    return {
        "candidate_predicates": candidates,
        "rejected_patterns": rejected_patterns,
        "coverage_notes": coverage_notes,
        "convergence": convergence,
    }


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Medical Ontology Prospector",
        "",
        f"- generated_at_utc: `{summary['generated_at_utc']}`",
        f"- model: `{summary['model']}`",
        f"- corpus cases: `{summary['counts']['cases']}`",
        f"- batches: `{summary['counts']['batches']}`",
        f"- unique candidate predicates: `{summary['aggregate']['convergence']['unique_candidate_predicates']}`",
        f"- predicate/case ratio: `{summary['aggregate']['convergence']['predicate_case_ratio']}`",
        f"- multi-case predicates: `{summary['aggregate']['convergence']['multi_case_predicates']}`",
        f"- single-case predicates: `{summary['aggregate']['convergence']['single_case_predicates']}`",
        f"- existing palette hits: `{summary['aggregate']['convergence']['existing_palette_hits']}`",
        "",
        "## Candidate Predicates",
        "",
    ]
    for row in summary["aggregate"]["candidate_predicates"]:
        lines.append(
            f"- `{row['signature']}` support=`{row['support_count']}` avg_conf=`{row['average_confidence']}` "
            f"existing_palette=`{row['existing_palette']}`"
        )
        lines.append(f"  - cases: `{', '.join(row['support_case_ids'])}`")
        if row["arguments"]:
            lines.append(f"  - args: `{', '.join(row['arguments'])}`")
        if row["surface_forms"]:
            lines.append(f"  - surface forms: `{', '.join(row['surface_forms'][:8])}`")
        if row["decision_counts"]:
            lines.append(f"  - decisions: `{json.dumps(row['decision_counts'], sort_keys=True)}`")
        if row["merge_targets"]:
            lines.append(f"  - merge targets: `{json.dumps(row['merge_targets'], sort_keys=True)}`")
    if summary["aggregate"]["rejected_patterns"]:
        lines.extend(["", "## Rejected Patterns", ""])
        for row in summary["aggregate"]["rejected_patterns"][:20]:
            lines.append(f"- `{row['pattern']}` x{row['count']}: {row['reason']}")
    if summary["aggregate"]["coverage_notes"]:
        lines.extend(["", "## Coverage Notes", ""])
        for note in summary["aggregate"]["coverage_notes"][:20]:
            lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def run_prospector(
    *,
    base_url: str,
    model: str,
    context_length: int,
    timeout: int,
    temperature: float,
    think_enabled: bool,
    prompt_path: Path,
    corpus_path: Path,
    slice_dir: Path | None,
    batch_size: int,
    out_dir: Path,
) -> dict[str, Any]:
    base_prompt = prompt_path.read_text(encoding="utf-8")
    corpus = umls_mvp.load_json(corpus_path)
    cases = list(corpus.get("cases", []) or [])

    alias_records: list[dict[str, Any]] = []
    concept_rows: list[dict[str, Any]] = []
    if slice_dir and (slice_dir / "manifest.json").exists() and (slice_dir / "concepts.jsonl").exists():
        manifest = umls_mvp.load_json(slice_dir / "manifest.json")
        concept_rows = _load_jsonl(slice_dir / "concepts.jsonl")
        alias_records = umls_mvp.build_alias_records(manifest, concept_rows)

    batch_summaries: list[dict[str, Any]] = []
    for index, batch in enumerate(_chunked(cases, batch_size), start=1):
        prompt_text = _build_prompt(base_prompt, batch, alias_records, concept_rows)
        parsed, raw_json = _run_batch(
            prompt_text=prompt_text,
            base_url=base_url,
            model=model,
            context_length=context_length,
            timeout=timeout,
            temperature=temperature,
            think_enabled=think_enabled,
        )
        batch_summaries.append(
            {
                "batch_index": index,
                "case_ids": [str(case.get("case_id", "")).strip() for case in batch],
                "prompt_text": prompt_text,
                "parsed": parsed or {"candidate_predicates": [], "rejected_patterns": [], "coverage_notes": []},
                "raw_json": raw_json,
            }
        )

    aggregate = _aggregate_batches(batch_summaries, total_cases=len(cases))
    summary = {
        "generated_at_utc": _utc_now(),
        "model": model,
        "base_url": base_url,
        "context_length": context_length,
        "timeout": timeout,
        "temperature": temperature,
        "think_enabled": think_enabled,
        "prompt_path": str(prompt_path),
        "corpus_path": str(corpus_path),
        "slice_dir": str(slice_dir) if slice_dir else "",
        "counts": {
            "cases": len(cases),
            "batches": len(batch_summaries),
        },
        "aggregate": aggregate,
        "batches": batch_summaries,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    umls_mvp.write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(_render_summary_md(summary), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local-only medical ontology prospector against a local model.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--context-length", type=int, default=DEFAULT_CONTEXT)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--think-enabled", action="store_true")
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--slice-dir", type=Path, default=DEFAULT_SLICE_DIR)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    summary = run_prospector(
        base_url=args.base_url,
        model=args.model,
        context_length=args.context_length,
        timeout=args.timeout,
        temperature=args.temperature,
        think_enabled=args.think_enabled,
        prompt_path=args.prompt,
        corpus_path=args.corpus,
        slice_dir=args.slice_dir,
        batch_size=args.batch_size,
        out_dir=args.out_dir,
    )
    print(json.dumps(summary["aggregate"]["convergence"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
