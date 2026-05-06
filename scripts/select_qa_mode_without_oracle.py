#!/usr/bin/env python3
"""Select among existing QA evidence modes without source or answer-key access.

This is a query-surface experiment. It reads existing QA artifacts, strips
reference answers, judge labels, oracle fields, and failure-surface labels, then
asks an LLM, or optionally a deterministic structural scorer, to choose which
mode has the strongest structured evidence for each question.

The selector does not read source prose, gold KBs, strategy files, or answer
keys. Python does not derive answers from text; it packages already-executed
query evidence and scores the selected mode against existing judge labels only
after the selection is complete.
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VERDICT_SCORE = {"miss": 0, "partial": 1, "exact": 2}
SCORE_VERDICT = {0: "miss", 1: "partial", 2: "exact"}


SELECTOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "selected_mode",
        "selection_confidence",
        "evidence_quality_by_mode",
        "rationale",
        "risks",
    ],
    "properties": {
        "schema_version": {"type": "string", "enum": ["qa_mode_selector_v1"]},
        "selected_mode": {"type": "string"},
        "selection_confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "evidence_quality_by_mode": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["mode", "quality", "reason"],
                "properties": {
                    "mode": {"type": "string"},
                    "quality": {"type": "string", "enum": ["weak", "partial", "strong"]},
                    "reason": {"type": "string"},
                },
            },
        },
        "rationale": {"type": "string"},
        "risks": {"type": "array", "items": {"type": "string"}},
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--group",
        required=True,
        help=(
            "Comparison group in the form name:label=path,label=path. "
            "A mode can merge QA artifacts with +, e.g. baseline=qa.json+failure.json."
        ),
    )
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument(
        "--sample-row-limit",
        type=int,
        default=12,
        help="Maximum query result rows retained per executed query in selector evidence.",
    )
    parser.add_argument(
        "--selection-policy",
        choices=[
            "direct",
            "completeness",
            "relevance",
            "activation",
            "structural",
            "hybrid",
            "protected",
            "guarded_activation",
        ],
        default="direct",
        help=(
            "Selector policy. direct is the stable default; completeness, relevance, "
            "and activation are experimental LLM calibration policies. structural is "
            "a deterministic query-evidence scorer that does not call the model. "
            "hybrid uses the structural scorer first and calls the LLM selector only "
            "on uncertain rows. protected uses structural by default and calls the "
            "activation selector only for high-volume non-baseline overrides. "
            "guarded_activation uses structural for confident rows and activation+self-check "
            "for uncertain rows."
        ),
    )
    parser.add_argument(
        "--hybrid-llm-policy",
        choices=["direct", "completeness", "relevance", "activation"],
        default="direct",
        help="LLM selector policy used only for uncertain rows when --selection-policy hybrid.",
    )
    parser.add_argument(
        "--hybrid-margin",
        type=float,
        default=1.5,
        help="Minimum structural score gap required to avoid the LLM selector in hybrid mode.",
    )
    parser.add_argument(
        "--hybrid-min-score",
        type=float,
        default=3.0,
        help="Minimum top structural score required to avoid the LLM selector in hybrid mode.",
    )
    parser.add_argument(
        "--include-self-check",
        action="store_true",
        help="Include bounded QA self-check notes in selector evidence. Experimental; default excludes them.",
    )
    parser.add_argument("--row-limit", type=int, default=0)
    parser.add_argument("--only-ids", default="")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selection_policy = str(args.selection_policy)
    guarded_activation = selection_policy == "guarded_activation"
    effective_hybrid_llm_policy = "activation" if guarded_activation else str(args.hybrid_llm_policy)
    effective_hybrid_margin = 1.0 if guarded_activation else float(args.hybrid_margin)
    effective_hybrid_min_score = 4.0 if guarded_activation else float(args.hybrid_min_score)
    effective_include_self_check = bool(args.include_self_check) or guarded_activation
    group = load_group(args.group)
    rows = build_rows(
        group,
        sample_row_limit=int(args.sample_row_limit),
        include_self_check=effective_include_self_check,
    )
    only_ids = {part.strip() for part in str(args.only_ids).split(",") if part.strip()}
    if only_ids:
        rows = [row for row in rows if row["id"] in only_ids]
    if args.row_limit:
        rows = rows[: int(args.row_limit)]

    outputs: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        print(f"[{index}/{len(rows)}] {row['id']}")
        selection_error = ""
        if selection_policy == "structural":
            selection = structural_selector(row=row, mode_labels=group["labels"])
        elif selection_policy in {"hybrid", "guarded_activation"}:
            try:
                selection = hybrid_selector(
                    row=row,
                    mode_labels=group["labels"],
                    margin=effective_hybrid_margin,
                    min_score=effective_hybrid_min_score,
                    fallback_selector=lambda *, row, mode_labels: call_selector(
                        base_url=str(args.base_url),
                        model=str(args.model),
                        timeout=int(args.timeout),
                        temperature=float(args.temperature),
                        top_p=float(args.top_p),
                        max_tokens=int(args.max_tokens),
                        row=row,
                        mode_labels=mode_labels,
                        selection_policy=effective_hybrid_llm_policy,
                    ),
                )
            except Exception as exc:  # pragma: no cover - live harness path
                selection_error = str(exc)
                selection = {}
        elif selection_policy == "protected":
            selection = protected_selector(
                row=row,
                mode_labels=group["labels"],
                fallback_selector=lambda *, row, mode_labels: call_selector(
                    base_url=str(args.base_url),
                    model=str(args.model),
                    timeout=int(args.timeout),
                    temperature=float(args.temperature),
                    top_p=float(args.top_p),
                    max_tokens=int(args.max_tokens),
                    row=row,
                    mode_labels=mode_labels,
                    selection_policy="activation",
                ),
            )
        else:
            try:
                selection = call_selector(
                    base_url=str(args.base_url),
                    model=str(args.model),
                    timeout=int(args.timeout),
                    temperature=float(args.temperature),
                    top_p=float(args.top_p),
                    max_tokens=int(args.max_tokens),
                    row=row,
                    mode_labels=group["labels"],
                    selection_policy=selection_policy,
                )
            except Exception as exc:  # pragma: no cover - live harness path
                selection_error = str(exc)
                selection = {}
        outputs.append(score_selection(row=row, selection=selection, error=selection_error))

    report = {
        "schema_version": "qa_mode_selector_run_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Selector input excludes source prose, reference answers, judge labels, oracle fields, and failure-surface labels.",
            "Selector chooses among already-executed query evidence modes only.",
            "Python packages structured query evidence and computes after-the-fact metrics; it does not interpret source language.",
        ],
        "group": {
            "name": group["name"],
            "labels": group["labels"],
            "artifacts": [
                {"label": item["label"], "paths": [display_path(path) for path in item.get("paths", [])]}
                for item in group["artifacts"]
            ],
        },
        "selection_policy": selection_policy,
        "hybrid_llm_policy": effective_hybrid_llm_policy,
        "hybrid_margin": effective_hybrid_margin,
        "hybrid_min_score": effective_hybrid_min_score,
        "include_self_check": effective_include_self_check,
        "summary": summarize(outputs),
        "rows": outputs,
    }
    out_json = args.out_json if args.out_json.is_absolute() else REPO_ROOT / args.out_json
    out_md = args.out_md if args.out_md.is_absolute() else REPO_ROOT / args.out_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def load_group(spec: str) -> dict[str, Any]:
    name, _, rest = str(spec).partition(":")
    if not name.strip() or not rest.strip():
        raise SystemExit(f"invalid --group {spec!r}")
    artifacts: list[dict[str, Any]] = []
    for part in rest.split(","):
        label, _, raw_path = part.partition("=")
        if not label.strip() or not raw_path.strip():
            raise SystemExit(f"invalid artifact spec {part!r}")
        paths = [_resolve_path(token.strip()) for token in raw_path.split("+") if token.strip()]
        if not paths:
            raise SystemExit(f"invalid artifact path list {raw_path!r}")
        records = [json.loads(path.read_text(encoding="utf-8-sig")) for path in paths]
        artifacts.append({"label": label.strip(), "paths": paths, "record": merge_qa_records(records)})
    return {"name": name.strip(), "artifacts": artifacts, "labels": [item["label"] for item in artifacts]}


def _resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else REPO_ROOT / path


def merge_qa_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge QA rows by id, letting later artifacts add/override row metadata."""
    if not records:
        return {"rows": []}
    merged = dict(records[0])
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for record in records:
        for row in record.get("rows", []) if isinstance(record.get("rows"), list) else []:
            if not isinstance(row, dict):
                continue
            row_id = str(row.get("id", "")).strip()
            if not row_id:
                continue
            if row_id not in by_id:
                order.append(row_id)
                by_id[row_id] = {}
            by_id[row_id].update(row)
    merged["rows"] = [by_id[row_id] for row_id in order]
    return merged


def build_rows(group: dict[str, Any], *, sample_row_limit: int, include_self_check: bool) -> list[dict[str, Any]]:
    rows_by_label = {
        artifact["label"]: {
            str(row.get("id", "")): row
            for row in artifact["record"].get("rows", [])
            if isinstance(row, dict) and str(row.get("id", "")).strip()
        }
        for artifact in group["artifacts"]
    }
    all_ids = sorted(set().union(*(set(rows) for rows in rows_by_label.values())))
    out: list[dict[str, Any]] = []
    for row_id in all_ids:
        modes = []
        question = ""
        for label in group["labels"]:
            row = rows_by_label[label].get(row_id)
            if not row:
                continue
            question = question or str(row.get("utterance", "")).strip()
            modes.append(
                {
                    "mode": label,
                    "query_evidence": compact_query_evidence(
                        row,
                        sample_row_limit=sample_row_limit,
                        include_self_check=include_self_check,
                    ),
                    "verdict": row_verdict(row),
                }
            )
        out.append({"id": row_id, "question": question, "modes": modes})
    return out


def compact_query_evidence(row: dict[str, Any], *, sample_row_limit: int, include_self_check: bool) -> dict[str, Any]:
    results = []
    for item in row.get("query_results", []) or []:
        if not isinstance(item, dict):
            continue
        result = item.get("result") if isinstance(item.get("result"), dict) else {}
        rows = result.get("rows", []) if isinstance(result.get("rows"), list) else []
        results.append(
            {
                "query": str(item.get("query", "")),
                "status": str(result.get("status", "")),
                "predicate": str(result.get("predicate", "")),
                "num_rows": int(result.get("num_rows", 0) or 0),
                "variables": result.get("variables", []),
                "sample_rows": rows[: max(1, sample_row_limit)],
                "rows_omitted": max(0, len(rows) - max(1, sample_row_limit)),
                "was_relaxed_fallback": bool(item.get("derived_from_queries")),
            }
        )
    evidence = {
        "model_decision": str(row.get("model_decision", "")),
        "projected_decision": str(row.get("projected_decision", "")),
        "planned_queries": row.get("queries", []),
        "executed_results": results,
        "warnings": row.get("warnings", []),
        "parse_error": str(row.get("parse_error", "")),
    }
    if include_self_check:
        evidence["self_check"] = compact_self_check(row)
    return evidence


def compact_self_check(row: dict[str, Any]) -> dict[str, Any]:
    self_check = row.get("self_check") if isinstance(row.get("self_check"), dict) else {}
    notes = self_check.get("notes", []) if isinstance(self_check.get("notes"), list) else []
    missing_slots = self_check.get("missing_slots", []) if isinstance(self_check.get("missing_slots"), list) else []
    return {
        "bad_commit_risk": str(self_check.get("bad_commit_risk", "")),
        "missing_slots": missing_slots[:8],
        "notes": [str(note)[:800] for note in notes[:4]],
    }


def call_selector(
    *,
    base_url: str,
    model: str,
    timeout: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
    row: dict[str, Any],
    mode_labels: list[str],
    selection_policy: str,
) -> dict[str, Any]:
    base_messages = [
        {
            "role": "system",
            "content": selector_system_prompt(selection_policy),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "question_id": row["id"],
                    "question": row["question"],
                    "available_modes": mode_labels,
                    "mode_evidence": [
                        {"mode": mode["mode"], "query_evidence": mode["query_evidence"]}
                        for mode in row["modes"]
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
        },
    ]
    last_parse_error = ""
    for attempt in range(2):
        messages = list(base_messages)
        if attempt:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Retry the previous selector response. Return exactly one valid "
                        "qa_mode_selector_v1 JSON object and no prose."
                    ),
                }
            )
        content = _selector_completion_content(
            base_url=base_url,
            model=model,
            timeout=timeout,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            messages=messages,
        )
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            last_parse_error = str(exc)
            continue
        if not isinstance(parsed, dict):
            last_parse_error = "selector returned non-object JSON"
            continue
        return parsed
    raise RuntimeError(last_parse_error or "selector returned invalid JSON")


def _selector_completion_content(
    *,
    base_url: str,
    model: str,
    timeout: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
    messages: list[dict[str, str]],
) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "reasoning_effort": "none",
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "qa_mode_selector_v1",
                "strict": True,
                "schema": SELECTOR_SCHEMA,
            },
        },
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions"
        if base_url.rstrip("/").endswith("/v1")
        else f"{base_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
    return str(message.get("content", "") if isinstance(message, dict) else "").strip()


def structural_selector(*, row: dict[str, Any], mode_labels: list[str]) -> dict[str, Any]:
    scored = structural_mode_scores(row=row, mode_labels=mode_labels)
    best_score, selected, _best_quality = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0.0
    return {
        "schema_version": "qa_mode_selector_v1",
        "selected_mode": selected,
        "selection_confidence": min(1.0, max(0.0, round(best_score / 10.0, 3))),
        "evidence_quality_by_mode": [
            {
                "mode": label,
                "quality": str(quality.get("quality", "weak")),
                "reason": str(quality.get("reason", "")),
            }
            for _score, label, quality in scored
        ],
        "rationale": f"deterministic structural query-evidence score selected {selected}",
        "risks": [
            "structural selector cannot judge answer meaning",
            "row count can reward irrelevant evidence",
        ],
        "selection_source": "structural",
        "structural_score": round(float(best_score), 3),
        "structural_margin": round(float(best_score - second_score), 3),
    }


def hybrid_selector(
    *,
    row: dict[str, Any],
    mode_labels: list[str],
    margin: float,
    min_score: float,
    fallback_selector: Any,
) -> dict[str, Any]:
    scored = structural_mode_scores(row=row, mode_labels=mode_labels)
    best_score, structural_choice, best_quality = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0.0
    score_margin = float(best_score - second_score)
    quality = str(best_quality.get("quality", "weak"))
    direct_rows = int(best_quality.get("direct_rows", 0) or 0)
    parse_error = bool(best_quality.get("parse_error", False))
    warning_count = int(best_quality.get("warning_count", 0) or 0)
    uncertain_reasons: list[str] = []
    if best_score < min_score:
        uncertain_reasons.append(f"top structural score {best_score:.3f} below {min_score:.3f}")
    if score_margin < margin:
        uncertain_reasons.append(f"score margin {score_margin:.3f} below {margin:.3f}")
    if quality != "strong":
        uncertain_reasons.append(f"top evidence quality is {quality}")
    if direct_rows <= 0:
        uncertain_reasons.append("top mode has no direct returned rows")
    if parse_error:
        uncertain_reasons.append("top mode has a parse error")
    if warning_count:
        uncertain_reasons.append("top mode has warnings")
    volume_trap_reason = structural_volume_trap_reason(scored)
    if volume_trap_reason:
        uncertain_reasons.append(volume_trap_reason)
    identity_trap_reason = structural_identity_completeness_trap_reason(row=row, scored=scored)
    if identity_trap_reason:
        uncertain_reasons.append(identity_trap_reason)
    rationale_trap_reason = structural_rationale_contrast_trap_reason(row=row, scored=scored)
    if rationale_trap_reason:
        uncertain_reasons.append(rationale_trap_reason)
    operational_trap_reason = structural_operational_record_status_trap_reason(
        row=row,
        scored=scored,
        mode_labels=mode_labels,
        structural_choice=structural_choice,
    )
    if operational_trap_reason:
        uncertain_reasons.append(operational_trap_reason)
    baseline_guard_reason = structural_baseline_answer_surface_guard_reason(
        row=row,
        scored=scored,
        mode_labels=mode_labels,
        structural_choice=structural_choice,
    )
    if baseline_guard_reason:
        selection = structural_selector(row=row, mode_labels=mode_labels)
        selection["selected_mode"] = mode_labels[0] if mode_labels else structural_choice
        selection["selection_source"] = "hybrid_structural"
        selection["hybrid_decision"] = "structural_baseline_answer_surface_guard"
        selection["structural_candidate"] = structural_choice
        selection["structural_score"] = round(float(best_score), 3)
        selection["structural_margin"] = round(score_margin, 3)
        selection["structural_uncertainty_reasons"] = uncertain_reasons
        selection["baseline_guard_reason"] = baseline_guard_reason
        selection["rationale"] = baseline_guard_reason
        selection.setdefault("risks", []).append(
            "baseline guard overrode a broad or self-check-heavy candidate surface"
        )
        return selection
    specialized_override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=mode_labels,
        structural_choice=structural_choice,
    )
    if specialized_override:
        override_label, override_reason = specialized_override
        selection = structural_selector(row=row, mode_labels=mode_labels)
        selection["selected_mode"] = override_label
        selection["selection_source"] = "hybrid_structural"
        selection["hybrid_decision"] = "structural_specialized_answer_surface_guard"
        selection["structural_candidate"] = structural_choice
        selection["structural_score"] = round(float(best_score), 3)
        selection["structural_margin"] = round(score_margin, 3)
        selection["structural_uncertainty_reasons"] = uncertain_reasons
        selection["specialized_guard_reason"] = override_reason
        selection["rationale"] = override_reason
        selection.setdefault("risks", []).append(
            "specialized answer-surface guard overrode ordinary structural or activation selection"
        )
        return selection
    if not uncertain_reasons:
        selection = structural_selector(row=row, mode_labels=mode_labels)
        selection["selection_source"] = "hybrid_structural"
        selection["hybrid_decision"] = "structural_confident"
        selection["structural_candidate"] = structural_choice
        return selection

    try:
        selection = fallback_selector(row=row, mode_labels=mode_labels)
    except Exception as exc:
        selection = structural_selector(row=row, mode_labels=mode_labels)
        selection["selection_source"] = "hybrid_structural_after_llm_error"
        selection["hybrid_decision"] = "structural_after_llm_error"
        selection["hybrid_llm_error"] = str(exc)
        selection["structural_candidate"] = structural_choice
        selection["structural_uncertainty_reasons"] = uncertain_reasons
        selection.setdefault("risks", []).append("LLM fallback failed; deterministic structural choice used")
        return selection
    if not isinstance(selection, dict):
        selection = {}
    selection["selection_source"] = "hybrid_llm"
    selection["hybrid_decision"] = "llm_due_to_uncertainty"
    selection["structural_candidate"] = structural_choice
    selection["structural_score"] = round(float(best_score), 3)
    selection["structural_margin"] = round(score_margin, 3)
    selection["structural_uncertainty_reasons"] = uncertain_reasons
    return selection


def protected_selector(*, row: dict[str, Any], mode_labels: list[str], fallback_selector: Any) -> dict[str, Any]:
    structural = structural_selector(row=row, mode_labels=mode_labels)
    structural_choice = str(structural.get("selected_mode", ""))
    baseline_label = mode_labels[0] if mode_labels else ""
    scored = structural_mode_scores(row=row, mode_labels=mode_labels)
    top_score, _top_label, top_quality = scored[0]
    baseline_quality = _quality_for_label(scored, baseline_label)
    top_volume = int(top_quality.get("direct_rows", 0) or 0) + int(top_quality.get("relaxed_rows", 0) or 0)
    top_direct = int(top_quality.get("direct_rows", 0) or 0)
    baseline_volume = int(baseline_quality.get("direct_rows", 0) or 0) + int(baseline_quality.get("relaxed_rows", 0) or 0)
    margin = float(structural.get("structural_margin", 0.0) or 0.0)
    reasons: list[str] = []
    if structural_choice == baseline_label:
        reasons.append("structural selected baseline")
    if top_volume < 12 and top_direct <= 2:
        reasons.append("candidate override is compact enough for structural choice")
    if margin < 1.0 and top_direct <= 2:
        reasons.append("candidate override is close and focused; protect structural choice")
    if baseline_volume <= 0:
        reasons.append("baseline has no evidence to protect")
    should_call_activation = (
        structural_choice != baseline_label
        and top_volume >= 12
        and baseline_volume > 0
        and not (margin < 1.0 and top_direct <= 2)
    )
    if not should_call_activation:
        structural["selection_source"] = "protected_structural"
        structural["protected_decision"] = "structural_guard"
        structural["protected_reasons"] = reasons or ["structural evidence not risky enough for activation override"]
        return structural
    try:
        selection = fallback_selector(row=row, mode_labels=mode_labels)
    except Exception as exc:
        structural["selection_source"] = "protected_structural_after_llm_error"
        structural["protected_decision"] = "structural_after_llm_error"
        structural["protected_llm_error"] = str(exc)
        structural["protected_reasons"] = [
            "activation fallback failed; protected selector kept structural choice",
        ]
        structural.setdefault("risks", []).append("activation fallback failed; structural choice used")
        return structural
    if not isinstance(selection, dict):
        selection = {}
    selection["selection_source"] = "protected_llm"
    selection["protected_decision"] = "activation_for_high_volume_override"
    selection["structural_candidate"] = structural_choice
    selection["structural_score"] = round(float(top_score), 3)
    selection["structural_margin"] = round(margin, 3)
    selection["protected_reasons"] = [
        f"structural candidate {structural_choice} overrode {baseline_label}",
        f"candidate_volume={top_volume}",
        f"baseline_volume={baseline_volume}",
    ]
    return selection


def _quality_for_label(scored: list[tuple[float, str, dict[str, Any]]], label: str) -> dict[str, Any]:
    for _score, candidate_label, quality in scored:
        if candidate_label == label:
            return quality
    return {}


def structural_baseline_answer_surface_guard_reason(
    *,
    row: dict[str, Any],
    scored: list[tuple[float, str, dict[str, Any]]],
    mode_labels: list[str],
    structural_choice: str,
) -> str:
    """Return a reason to keep baseline when a variant has answer-surface mismatch risk."""
    if len(scored) < 2 or not mode_labels:
        return ""
    baseline_label = mode_labels[0]
    baseline_quality = _quality_for_label(scored, baseline_label)
    if not baseline_quality:
        return ""
    question = str(row.get("question", "")).casefold()
    baseline_predicates = set(baseline_quality.get("predicate_names", []) or [])
    top_quality = _quality_for_label(scored, structural_choice)
    top_predicates = set(top_quality.get("predicate_names", []) or [])
    baseline_direct = int(baseline_quality.get("direct_rows", 0) or 0)
    if baseline_direct <= 0:
        return ""

    identity_markers = ["who is ", "who was ", "who were "]
    identity_predicates = {"alias", "full_name", "name", "person_name", "preferred_name", "registered_as"}
    broad_action_predicates = {"event_actor", "event_occurs"}
    if (
        structural_choice != baseline_label
        and any(marker in question for marker in identity_markers)
        and baseline_predicates.intersection(identity_predicates)
        and top_predicates.intersection(broad_action_predicates)
    ):
        return "identity question has baseline name/role support and candidate is broad action-heavy"

    award_markers = ["who won", "won first", "won second", "first place", "second place", "recognition", "award"]
    if (
        structural_choice != baseline_label
        and any(marker in question for marker in award_markers)
        and "awarded" in baseline_predicates
        and "awarded" not in top_predicates
    ):
        return "award/result question has baseline awarded support and candidate lacks awarded rows"

    status_markers = ["exhibition status", "eligibility", "eligible", "status at closing"]
    direct_status_predicates = {"disqualified_from", "eligible_for", "exhibition_status", "rule_applies_to"}
    if (
        structural_choice == baseline_label
        and any(marker in question for marker in status_markers)
        and baseline_predicates.intersection(direct_status_predicates)
    ):
        return "status question has direct baseline status/rule support"

    direct_application_status_predicates = {
        "application_status",
        "certification_status",
        "event_status",
        "pending_action",
    }
    if (
        "commit" not in question
        and "status" in question
        and baseline_predicates.intersection(direct_application_status_predicates)
        and _competing_mode_is_broad_or_relaxed_heavy(scored=scored, baseline_label=baseline_label)
    ):
        return "status question has direct baseline application/status support and candidate is broad or relaxed-heavy"

    counterfactual_markers = ["if ", "would ", "what would happen", "should the system", "pending", "hold", "commit"]
    counterfactual_support_predicates = {
        "deaccession_threshold",
        "denial_reason",
        "event_occurred",
        "event_status",
        "has_residency_proof",
        "pending_action",
        "rule",
        "rule_condition",
        "species",
    }
    if (
        structural_choice == baseline_label
        and sum(1 for marker in counterfactual_markers if marker in question) >= 2
        and baseline_predicates.intersection(counterfactual_support_predicates)
        and _competing_mode_is_broad_or_relaxed_heavy(scored=scored, baseline_label=baseline_label)
    ):
        return "counterfactual or hold/readiness question has direct baseline rule/status support and candidate is broad or relaxed-heavy"

    return ""


def structural_specialized_answer_surface_override(
    *,
    row: dict[str, Any],
    scored: list[tuple[float, str, dict[str, Any]]],
    mode_labels: list[str],
    structural_choice: str,
) -> tuple[str, str] | None:
    """Return a deterministic nonbaseline choice for narrow question-act traps."""
    if len(scored) < 2 or len(mode_labels) < 2:
        return None
    baseline_label = mode_labels[0]
    baseline_quality = _quality_for_label(scored, baseline_label)
    if not baseline_quality:
        return None
    question = str(row.get("question", "")).casefold()
    baseline_predicates = set(baseline_quality.get("predicate_names", []) or [])

    if "who collected" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection({"collector", "lot_collector", "accession_collector"}):
                return (
                    label,
                    "collector identity question needs direct collector predicate surface rather than broad status/note evidence",
                )

    if any(marker in question for marker in ["youngest", "oldest"]) and any(
        marker in question for marker in ["exhibitor", "person", "child", "member"]
    ):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection({"age", "person_age", "person_identity", "registered_age"}):
                return (
                    label,
                    "superlative identity question needs explicit age/identity surface rather than broad role membership rows",
                )

    if any(marker in question for marker in ["who is ", "who was "]) and any(
        marker in question for marker in ["warden", "official", "inspector", "authority"]
    ):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection({"person_name", "name", "canonical_person"}) and predicates.intersection(
                {"role_authority", "role_duty", "ruling_by", "ruling_made_by", "inspected_by", "official_action"}
            ):
                return (
                    label,
                    "official identity question needs role-authority definition surface rather than action volume or title-only rows",
                )

    if "what thread" in question and any(marker in question for marker in ["currently", "current", " in the "]):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection({"device_state", "current_state", "contained_thread", "component_state"}):
                return (
                    label,
                    "current object-component question needs direct current-state/component surface rather than transition history volume",
                )

    if "why" in question and "have" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection({"custody_transfer", "custody_reason", "loaned_to", "transferred_to"}):
                return (
                    label,
                    "why-have question needs custody-transfer surface rather than adjacent action or object-property rows",
                )

    if any(marker in question for marker in ["who won", "won first", "won second", "first place", "second place"]):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection({"award_given", "awarded", "award_result", "placement_awarded"}):
                return (
                    label,
                    "award placement question needs explicit award-result surface rather than nearby device/person rows",
                )

    if "reinstated" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            direct_rows = int(quality.get("direct_rows", 0) or 0)
            relaxed_rows = int(quality.get("relaxed_rows", 0) or 0)
            if "holds_role" in predicates and direct_rows > 0 and relaxed_rows == 0 and len(predicates) <= 2:
                return (
                    label,
                    "reinstatement question needs focused role-history surface rather than broad current-role or rule evidence",
                )

    carry_markers = ["carried", "carry", "carries"]
    if any(marker in question for marker in carry_markers):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "possesses" in predicates:
                return (
                    label,
                    "carry question needs direct possession surface rather than broad title or event evidence",
                )

    possession_markers = [*carry_markers, "possess", "loan", "owns", "own ", "owned", "inherit"]
    if any(marker in question for marker in possession_markers):
        possession_predicates = {"inherits", "owns", "possesses", "transferred_ownership"}
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if len(predicates.intersection(possession_predicates)) >= 2:
                return (
                    label,
                    "possession-versus-ownership question needs inherit/own/possess distinction surface rather than broad event/rule evidence",
                )

    if "legal title" in question or "stronger title" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "claimed_by" in predicates or predicates.intersection({"transferred_ownership", "trust_administered_by"}):
                return (
                    label,
                    "legal-title contest question needs claim/default/transfer surface rather than static ownership rows",
                )

    if "contract" in question and any(marker in question for marker in ["survive", "void", "valid"]):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection({"authority_source", "acting_role_holder"}):
                return (
                    label,
                    "contract-validity question needs explicit acting-authority surface rather than generic rule evidence",
                )
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "rule_condition" in predicates:
                return (
                    label,
                    "contract-validity question needs authority-source surface rather than unrelated ownership or entity rows",
                )

    if question.startswith("did all ") or " did all " in question:
        universal_scope_predicates = {"acknowledgment_received", "deadline_met", "deadline_exceeded"}
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if universal_scope_predicates.issubset(predicates) and "report_submitted" not in predicates:
                return (
                    label,
                    "universal-scope question needs broad set-enumeration surface rather than narrower report-detail joins",
                )

    if "why" in question and "termination" in question and "denied" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"termination_status", "clarification_provided", "unit_count"}):
                return (
                    label,
                    "termination-denial question needs rationale plus quantity-threshold support rather than status text alone",
                )

    if "affected by the recall" in question and "lot" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "lot_affected" in predicates and predicates.intersection({"correction_applied", "unit_count"}):
                return (
                    label,
                    "lot-affected question needs explicit target-lot exclusion/check surface rather than broad affected-lot listing",
                )

    if "had not been reclassified" in question and "deadline" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "deadline_requirement" in predicates and "recall_classification" in predicates:
                return (
                    label,
                    "counterfactual reclassification deadline question needs classification-bound deadline surface",
                )
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "deadline_requirement" in predicates and predicates.intersection(
                {"classification_change"}
            ):
                return (
                    label,
                    "counterfactual reclassification deadline question needs classification-bound deadline surface",
                )

    if "why" in question and "deferred" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"vote_result", "recusal_member", "eligibility_determination", "interpretation_text"}):
                return (
                    label,
                    "deferment-rationale question needs interpreted decision support rather than rule text alone",
                )

    if "component" in question and "problem" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"project_category", "rule_condition"}):
                return (
                    label,
                    "component-problem question needs project-category plus rule-condition surface",
                )

    if (
        "if " in question
        and "what would have been different" in question
        and ("recuse" in question or "recusal" in question)
    ):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset(
                {"recusal_member", "quorum_status", "vote_result", "eligibility_determination"}
            ):
                return (
                    label,
                    "counterfactual-recusal outcome question needs both procedure path and eligibility surface",
                )

    if "recuse" in question or "recusal" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"recusal_member", "vote_result", "rule_text"}) and "eligibility_determination" not in predicates:
                return (
                    label,
                    "recusal-rationale question needs recusal rule surface rather than eligibility determination surface",
                )

    if "couldn" in question and "vote" in question and "recusal" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"recusal_member", "vote_result", "rule_text"}) and "quorum_status" not in predicates:
                return (
                    label,
                    "post-recusal vote question needs recusal/vote/rule surface without misleading quorum-status volume",
                )

    if "3-year window" in question or "three-year window" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"prior_grant_history", "interpretation_text", "rule_condition"}):
                return (
                    label,
                    "window-merit question needs explicit rule-condition plus prior-history surface",
                )
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"prior_grant_history", "interpretation_text"}) and predicates.intersection(
                {"rule_interpreted", "rule_condition"}
            ) and "applicant_id" not in predicates:
                return (
                    label,
                    "window-merit question needs prior-history plus interpretation surface",
                )

    if "recall" in question and ("amendment" in question or "ba-" in question):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"charter_rule", "voting_threshold"}) and predicates.intersection(
                {"reserve_balance", "emergency_declared"}
            ) and "legal_opinion" not in predicates:
                return (
                    label,
                    "amendment-recall question needs recall-authority surface rather than threshold-only legal-opinion rows",
                )

    if "rejected on the merits" in question or "because of absences" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection({"correction_to_record", "clarification_of_record"}) and "derived_status" not in predicates:
                return (
                    label,
                    "rejection-cause question needs correction/clarification surface rather than derived status alone",
                )

    if "if " in question and "reserve status" in question:
        if baseline_predicates.issuperset({"reserve_balance", "minimum_reserve_policy", "expenditure_authorized"}):
            return (
                baseline_label,
                "hypothetical reserve-status question keeps baseline arithmetic inputs over derived rule status",
            )
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"reserve_balance", "minimum_reserve_policy", "expenditure_authorized"}) and "derived_status" not in predicates:
                return (
                    label,
                    "hypothetical reserve-status question needs baseline arithmetic inputs rather than derived rule status",
                )

    if "guardianship" in question and any(marker in question for marker in ["invalid", "valid", "retroactive"]):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "resides_at" in predicates and predicates.intersection({"charter_clause", "rule_condition"}):
                return (
                    label,
                    "guardianship-validity question needs residence/resumption condition surface rather than bare guardianship status",
                )

    if "current operational status" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"has_state", "is_final_state"}):
                return (
                    label,
                    "current operational status question needs explicit final-state surface rather than adjacent event/action evidence",
                )

    if "adjusted" in question and "expiration" in question and "reinstatement" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            direct_rows = int(quality.get("direct_rows", 0) or 0)
            if "permit_current_expiration" in predicates and direct_rows > 0:
                return (
                    label,
                    "adjusted-expiration question needs explicit current-expiration surface rather than extension-label or original-date evidence",
                )

    if "correction" in question and "extension entitlement" in question and any(
        marker in question for marker in ["change", "changed", "affect"]
    ):
        entitlement_predicates = {"deadline_requirement", "rule_threshold_met"}
        extension_predicates = {"extension_approved_on", "extension_duration_days", "extension_granted"}
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection(entitlement_predicates) and predicates.intersection(extension_predicates):
                return (
                    label,
                    "correction-entitlement question needs entitlement rule plus extension effect surface rather than correction/admission rows alone",
                )

    if "evidentiary status" in question and ("report" in question or "source" in question):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "witness_statement" in predicates and predicates.intersection({"allegation_tip", "document_type"}):
                return (
                    label,
                    "evidentiary-status report question needs explicit witness/report surface rather than generic claim-status surface",
                )

    filing_markers = ["filed on time", "request filed", "filed", "request"]
    if (
        "on time" in question
        and "reinstatement" in question
        and any(marker in question for marker in filing_markers)
        and baseline_predicates.intersection({"inspection_completed_on", "business_days_between", "deadline_requirement"})
    ):
        for _score, label, quality in scored:
            if label == baseline_label:
                continue
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"inspection_requested", "permit_reinstated"}) and predicates.intersection(
                {"rule_threshold_met", "next_inspection_scheduling_deadline"}
            ):
                return (
                    label,
                    "request filing timeliness question needs request/reinstatement threshold evidence rather than completion-window evidence",
                )

    if "should the system" in question and "commit" in question:
        process_predicates = {"pending_action", "requires_investigation", "event_defers", "event_reverses"}
        status_value_predicates = {"certification_status", "event_occurred", "has_state"}
        if baseline_predicates.intersection(status_value_predicates):
            for _score, label, quality in scored:
                if label == baseline_label:
                    continue
                predicates = set(quality.get("predicate_names", []) or [])
                if predicates.intersection(process_predicates):
                    return (
                        label,
                        "commit-readiness question needs unresolved process evidence rather than a bare status value",
                    )

    if any(marker in question for marker in ["what caused", "why ", "cause of", "caused the"]):
        rationale_note_predicates = {"inspector_note", "source_detail", "explanation", "reason", "cause", "caused_by"}
        if baseline_predicates.intersection(rationale_note_predicates):
            top_quality = _quality_for_label(scored, structural_choice)
            top_predicates = set(top_quality.get("predicate_names", []) or [])
            broad_record_predicates = {
                "event_occurs",
                "extension_granted",
                "inspection_completed",
                "inspection_requested",
                "observation_by",
                "permit_suspended",
                "record_corrected",
                "stop_work_order",
            }
            if structural_choice != baseline_label and top_predicates.intersection(broad_record_predicates):
                return (
                    baseline_label,
                    "cause question has explicit baseline rationale-note support and candidate is broad record/event surface",
                )

    if "priority" in question:
        for _score, label, quality in scored:
            if label == baseline_label:
                continue
            predicates = set(quality.get("predicate_names", []) or [])
            if any("priority" in predicate for predicate in predicates) and not any(
                "priority" in predicate for predicate in baseline_predicates
            ):
                return (
                    label,
                    "priority question needs explicit priority predicate surface rather than an underlying condition predicate",
                )

    if "decided" in question or "decision" in question:
        for _score, label, quality in scored:
            if label == baseline_label:
                continue
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.intersection({"panel_decision", "decision_reasoning", "final_decision"}) and not baseline_predicates.intersection(
                {"panel_decision", "decision_reasoning", "final_decision"}
            ):
                return (
                    label,
                    "decision-status question needs explicit decision surface rather than adjacent application/status evidence",
                )

    if "ventilation concern" in question and ("board decide" in question or "current position" in question):
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"event_occurred", "action_taken", "concern_raised"}):
                return (
                    label,
                    "board-concern decision question needs event/action concern history rather than bare pending status",
                )

    if "not yet" in question and "viability tested" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "test_status" in predicates and "\\+" not in predicates:
                return (
                    label,
                    "not-yet-tested question needs explicit pending test-status surface rather than broad negation over all lots",
                )

    if "deaccessioned" in question and "yet" in question:
        deaccession_status_predicates = {
            "deaccession_lot",
            "deaccession_status",
            "lot_deaccessioned",
            "scheduled_deaccession",
        }
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            direct_rows = int(quality.get("direct_rows", 0) or 0)
            relaxed_rows = int(quality.get("relaxed_rows", 0) or 0)
            if predicates.intersection(deaccession_status_predicates) and direct_rows > 0 and relaxed_rows == 0:
                return (
                    label,
                    "deaccession-yet question needs explicit scheduled/not-formally-completed status surface rather than broad lot-history volume",
                )

    if "why" in question and "split" in question and "vault" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"note_content", "note_subject"}) and predicates.intersection(
                {"test_germination_rate", "lot_germination_rate", "test_resulting_condition", "lot_condition_after_test"}
            ):
                return (
                    label,
                    "split rationale question needs explicit source-note rationale plus viability context",
                )

        generic_vault_predicates = {"requires_cryogenic", "vault_assignment_rule", "vault_type"}
        if baseline_predicates.intersection(generic_vault_predicates):
            for _score, label, quality in scored:
                if label == baseline_label:
                    continue
                predicates = set(quality.get("predicate_names", []) or [])
                if "lot_vault_split" in predicates and predicates.intersection(
                    {"lot_germination_rate", "lot_condition_after_test", "policy_vault_assignment"}
                ):
                    return (
                        label,
                        "split rationale question needs actual split/lot-condition surface rather than generic vault assignment surface",
                    )

    if "viability concern" in question and "vault 4" in question and "split" in question:
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"note_content", "note_subject"}) and predicates.intersection(
                {"test_germination_rate", "lot_germination_rate", "test_resulting_condition", "lot_condition_after_test"}
            ):
                return (
                    label,
                    "viability-concern question needs explicit source-note contrast plus viability context",
                )

    if "if" in question and "fails viability testing" in question and "germination rate" in question:
        if baseline_predicates.intersection({"deaccession_threshold", "minimum_storage_requirement"}):
            return (
                baseline_label,
                "hypothetical failed-viability question keeps direct baseline threshold/storage support over broader policy-note surfaces",
            )
        for _score, label, quality in scored:
            predicates = set(quality.get("predicate_names", []) or [])
            if "policy_condition_threshold" in predicates and predicates.intersection(
                {"policy_minimum_storage", "lot_deaccessioned", "deaccession_lot", "lot_status"}
            ):
                return (
                    label,
                    "hypothetical failed-viability question needs threshold/action policy surface rather than note surface",
                )

    if "as currently constituted" in question and "apply" in question:
        for _score, label, quality in scored:
            if label == baseline_label:
                continue
            predicates = set(quality.get("predicate_names", []) or [])
            if predicates.issuperset({"applicant_type", "director_interpretation"}):
                return (
                    label,
                    "current-constitution eligibility question needs applicant-type plus controlling interpretation surface",
                )

    if "resubmit" in question and "resident" in question:
        resubmission_resolution_predicates = {
            "applicant",
            "director_interpretation",
            "has_residency_proof",
            "rule",
            "rule_condition",
        }
        if baseline_predicates.intersection(resubmission_resolution_predicates):
            for _score, label, quality in scored:
                if label == baseline_label:
                    continue
                predicates = set(quality.get("predicate_names", []) or [])
                if predicates.intersection({"applicant_type", "residency_status"}) and not predicates.intersection(
                    {"has_residency_proof", "applicant"}
                ):
                    return (
                        baseline_label,
                        "resubmission eligibility question needs proof/rule resolution surface rather than current applicant status surface",
                    )

    return None


def _competing_mode_is_broad_or_relaxed_heavy(
    *,
    scored: list[tuple[float, str, dict[str, Any]]],
    baseline_label: str,
) -> bool:
    for _score, label, quality in scored:
        if label == baseline_label:
            continue
        direct_rows = int(quality.get("direct_rows", 0) or 0)
        relaxed_rows = int(quality.get("relaxed_rows", 0) or 0)
        predicate_count = int(quality.get("non_empty_predicates", 0) or 0)
        if direct_rows <= 0 and relaxed_rows >= 6:
            return True
        if relaxed_rows >= 12 and relaxed_rows >= max(1, direct_rows) * 3:
            return True
        if direct_rows >= 6 and relaxed_rows >= 12 and predicate_count >= 5:
            return True
    return False


def structural_mode_scores(*, row: dict[str, Any], mode_labels: list[str]) -> list[tuple[float, str, dict[str, Any]]]:
    scored: list[tuple[float, str, dict[str, Any]]] = []
    for mode in row.get("modes", []):
        if not isinstance(mode, dict):
            continue
        label = str(mode.get("mode", "")).strip()
        evidence = mode.get("query_evidence") if isinstance(mode.get("query_evidence"), dict) else {}
        quality = structural_evidence_quality(evidence)
        scored.append((float(quality["score"]), label, quality))
    if not scored:
        selected = mode_labels[0] if mode_labels else ""
        scored = [(0.0, selected, {"quality": "weak", "reason": "no mode evidence"})]
    scored.sort(
        key=lambda item: (
            item[0],
            -mode_labels.index(item[1]) if item[1] in mode_labels else 0,
        ),
        reverse=True,
    )
    return scored


def structural_volume_trap_reason(scored: list[tuple[float, str, dict[str, Any]]]) -> str:
    """Return an uncertainty reason when structural score is row-volume heavy."""
    if len(scored) < 2:
        return ""
    _best_score, _best_label, best_quality = scored[0]
    _second_score, _second_label, second_quality = scored[1]
    direct_rows = int(best_quality.get("direct_rows", 0) or 0)
    relaxed_rows = int(best_quality.get("relaxed_rows", 0) or 0)
    top_volume = direct_rows + relaxed_rows
    second_volume = int(second_quality.get("direct_rows", 0) or 0) + int(second_quality.get("relaxed_rows", 0) or 0)
    if direct_rows > 0 and relaxed_rows >= 5 and relaxed_rows >= direct_rows * 3:
        return "top structural score is dominated by relaxed fallback volume"
    if top_volume >= 12 and second_volume > 0 and top_volume >= second_volume * 4:
        return "top structural score is dominated by broad row-volume advantage"
    return ""


def structural_identity_completeness_trap_reason(
    *,
    row: dict[str, Any],
    scored: list[tuple[float, str, dict[str, Any]]],
) -> str:
    """Return uncertainty when identity rows outrank explicit name support."""
    if len(scored) < 2:
        return ""
    question = str(row.get("question", "")).casefold()
    if not any(marker in question for marker in ["who is ", "who was ", "who were "]):
        return ""
    _best_score, _best_label, best_quality = scored[0]
    best_predicates = set(best_quality.get("predicate_names", []) or [])
    name_predicates = {"alias", "full_name", "name", "person_name", "preferred_name"}
    if best_predicates.intersection(name_predicates):
        return ""
    for _score, _label, quality in scored[1:]:
        predicates = set(quality.get("predicate_names", []) or [])
        if predicates.intersection(name_predicates):
            return "identity question has competing mode with explicit name support"
    return ""


def structural_rationale_contrast_trap_reason(
    *,
    row: dict[str, Any],
    scored: list[tuple[float, str, dict[str, Any]]],
) -> str:
    """Return uncertainty when why/contrast rows have competing reason support."""
    if len(scored) < 2:
        return ""
    question = str(row.get("question", "")).casefold()
    if not any(marker in question for marker in ["why ", "why can't", "why cannot", "difference between", "contrast"]):
        return ""
    _best_score, _best_label, best_quality = scored[0]
    best_predicates = set(best_quality.get("predicate_names", []) or [])
    rationale_predicates = {
        "award_reason",
        "awarded",
        "cause",
        "caused_by",
        "disqualified_from",
        "explanation",
        "reason",
        "result_reason",
        "rule_applies_to",
        "source_detail",
    }
    if best_predicates.intersection(rationale_predicates):
        return ""
    for _score, _label, quality in scored[1:]:
        predicates = set(quality.get("predicate_names", []) or [])
        if predicates.intersection(rationale_predicates):
            return "why or contrast question has competing mode with explicit rationale support"
    return ""


def structural_operational_record_status_trap_reason(
    *,
    row: dict[str, Any],
    scored: list[tuple[float, str, dict[str, Any]]],
    mode_labels: list[str],
    structural_choice: str,
) -> str:
    """Return uncertainty when an operational/status lens may carry the answer surface."""
    if len(scored) < 2 or len(mode_labels) < 2:
        return ""
    baseline_label = mode_labels[0]
    if structural_choice != baseline_label:
        return ""
    question = str(row.get("question", "")).casefold()
    operational_markers = [
        "how long",
        "period",
        "deadline",
        "on time",
        "status",
        "current",
        "decide",
        "decision",
        "remedy",
        "unresolved",
        "threshold",
        "trigger",
        "priority",
        "correction",
        "corrected",
        "reinstatement",
        "reinstated",
        "isolated",
    ]
    if not any(marker in question for marker in operational_markers):
        return ""
    operational_predicates = {
        "asset_hierarchy",
        "community_impact_priority",
        "decision_reasoning",
        "director_interpretation",
        "event_corrects",
        "event_date",
        "event_defers",
        "event_reverses",
        "has_state",
        "initiated_action",
        "is_final_state",
        "panel_decision",
        "pending_action",
        "permit_reinstated",
        "permit_suspended",
        "policy_condition_threshold",
        "policy_vault_assignment",
        "record_corrected",
        "requires_investigation",
        "rule_threshold_met",
        "tolling_period",
    }
    for _score, label, quality in scored:
        if label == baseline_label:
            continue
        predicates = set(quality.get("predicate_names", []) or [])
        if predicates.intersection(operational_predicates):
            return "operational/status question has competing mode with specialized record-state evidence"
    return ""


def structural_evidence_quality(evidence: dict[str, Any]) -> dict[str, Any]:
    results = evidence.get("executed_results", []) if isinstance(evidence.get("executed_results"), list) else []
    row_total = 0
    direct_row_total = 0
    relaxed_row_total = 0
    success_count = 0
    non_empty_predicates: set[str] = set()
    for result in results:
        if not isinstance(result, dict):
            continue
        rows = int(result.get("num_rows", 0) or 0)
        row_total += rows
        if str(result.get("status", "")) == "success":
            success_count += 1
        predicate = str(result.get("predicate", "")).strip()
        if rows > 0 and predicate:
            non_empty_predicates.add(predicate)
        if bool(result.get("was_relaxed_fallback")):
            relaxed_row_total += rows
        else:
            direct_row_total += rows
    warning_count = len(evidence.get("warnings", [])) if isinstance(evidence.get("warnings"), list) else 0
    parse_error = bool(str(evidence.get("parse_error", "")).strip())
    score = 0.0
    score += min(6, direct_row_total) * 1.0
    score += min(6, relaxed_row_total) * 0.35
    score += min(4, success_count) * 0.25
    score += min(4, len(non_empty_predicates)) * 0.25
    score -= min(3, warning_count) * 0.2
    if parse_error:
        score -= 2.0
    if row_total == 0:
        quality = "weak"
    elif direct_row_total > 0 and score >= 3:
        quality = "strong"
    else:
        quality = "partial"
    return {
        "score": round(score, 3),
        "quality": quality,
        "direct_rows": direct_row_total,
        "relaxed_rows": relaxed_row_total,
        "success_results": success_count,
        "non_empty_predicates": len(non_empty_predicates),
        "predicate_names": sorted(non_empty_predicates),
        "warning_count": warning_count,
        "parse_error": parse_error,
        "reason": (
            f"direct_rows={direct_row_total}; relaxed_rows={relaxed_row_total}; "
            f"success_results={success_count}; non_empty_predicates={len(non_empty_predicates)}; "
            f"warnings={warning_count}"
        ),
    }


def selector_system_prompt(selection_policy: str) -> str:
    base = (
        "You are a query-surface selector for Prethinker. Choose which existing evidence mode "
        "best supports answering the user's question. You must not infer from outside knowledge. "
        "Use only the structured query results provided. Do not ask for writes or new facts. "
        "Return strict JSON only. "
    )
    if selection_policy == "completeness":
        return (
            base
            + "Score evidence completeness before evidence directness: a direct-looking row is weak if it covers only one "
            "subpart of the question, the wrong role, or the wrong scope. Prefer a broader or relaxed evidence bundle "
            "when its returned rows cover more of the entities, statuses, contrasts, conditions, timestamps, or rule "
            "consequences named by the question. If a mode retrieves an exact phrase but misses the question's decision, "
            "status, exception, or counter-evidence, mark it partial rather than strong. If two modes are equally complete, "
            "then prefer direct, specific, non-empty evidence over broad relaxed fallbacks."
        )
    if selection_policy == "relevance":
        return (
            base
            + "Score entity and scope relevance before evidence directness. Evidence is weak when it is centered on a "
            "different named person, organization, rule, event, deadline, correction, or decision than the question asks "
            "about, even if that evidence is non-empty or direct. Prefer a mode whose returned rows mention or bind the "
            "question's main subject, requested status, rule, or decision. If relevance and completeness are similar, "
            "then prefer direct, specific, non-empty evidence over broad relaxed fallbacks."
        )
    if selection_policy == "activation":
        return (
            base
            + "Select the mode most likely to produce the answer-bearing support bundle for this exact question. "
            "Direct non-empty rows are useful, but do not reward directness by itself. Prefer a focused, rule-union, "
            "or relaxed-fallback mode when its returned rows and self-check notes cover the question's requested "
            "why/how/counterfactual decision more completely than a narrower direct mode. Treat extra direct rows as "
            "a risk when they introduce a conflicting status, neighboring date, wrong subject, or irrelevant rule. "
            "For rule and counterfactual questions, prefer the mode that contains both the governing rule surface and "
            "the instance facts needed to apply it; if a mode has the rule text but lacks the named applicant/member/"
            "date outcome, mark it partial. Do not assume baseline is safest merely because it is direct; choose "
            "baseline only when its support is at least as answer-bearing and less contradictory than the alternatives. "
            "For requirement questions, a count-only or status-only row is often partial when another mode returns "
            "answer-bearing requirement details such as spacing, interval, threshold, scope, exception, condition, "
            "duration, unit, or authority. Prefer the mode that covers the full requested requirement bundle, not "
            "merely the mode whose document id or predicate name looks closest. For who-is identity questions, "
            "authority or action rows are useful but not sufficient by themselves when another mode includes explicit "
            "name/identity support plus role or authority evidence. For why, cannot, and difference/contrast "
            "questions, adjacent status/action rows are often partial when another mode returns explicit rationale, "
            "rule-application, disqualification, award-reason, cause/result, or contrast evidence tied to the asked "
            "capability or decision. For capability-failure questions, a generic restriction, seal, permission, or "
            "status row is often weaker than evidence that names the affected function, mechanism, component, award "
            "reason, or source-stated reason the capability cannot be demonstrated."
        )
    return (
        base
        + "If two modes are close, prefer the mode with direct, specific, non-empty evidence over broad relaxed fallbacks."
    )


def score_selection(row: dict[str, Any], selection: dict[str, Any], error: str) -> dict[str, Any]:
    verdicts = {mode["mode"]: mode["verdict"] for mode in row["modes"]}
    scores = {label: VERDICT_SCORE.get(verdict, -1) for label, verdict in verdicts.items()}
    best_score = max(scores.values()) if scores else -1
    best_labels = [label for label, score in scores.items() if score == best_score]
    selected = str(selection.get("selected_mode", "")).strip()
    selected_verdict = verdicts.get(selected, "unknown")
    return {
        "id": row["id"],
        "question": row["question"],
        "selected_mode": selected,
        "selected_verdict": selected_verdict,
        "selected_is_best": selected in best_labels,
        "best_verdict": SCORE_VERDICT.get(best_score, "unknown"),
        "best_labels": best_labels,
        "mode_verdicts": verdicts,
        "selection_confidence": selection.get("selection_confidence"),
        "selection_source": selection.get("selection_source", "") or ("llm" if selected else ""),
        "hybrid_decision": selection.get("hybrid_decision", ""),
        "structural_candidate": selection.get("structural_candidate", ""),
        "structural_score": selection.get("structural_score"),
        "structural_margin": selection.get("structural_margin"),
        "structural_uncertainty_reasons": selection.get("structural_uncertainty_reasons", []),
        "baseline_guard_reason": selection.get("baseline_guard_reason", ""),
        "specialized_guard_reason": selection.get("specialized_guard_reason", ""),
        "hybrid_llm_error": selection.get("hybrid_llm_error", ""),
        "evidence_quality_by_mode": selection.get("evidence_quality_by_mode", []),
        "rationale": selection.get("rationale", ""),
        "risks": selection.get("risks", []),
        "error": error,
    }


def row_verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    return str(judge.get("verdict", "")).strip() or "unknown"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    verdict_counts = Counter(str(row.get("selected_verdict", "unknown")) for row in rows)
    source_counts = Counter(str(row.get("selection_source", "") or "unknown") for row in rows)
    return {
        "row_count": len(rows),
        "selector_error_count": sum(1 for row in rows if row.get("error")),
        "selected_best_count": sum(1 for row in rows if row.get("selected_is_best")),
        "selection_source_counts": dict(source_counts),
        "selected_verdict_counts": dict(verdict_counts),
        "selected_exact": int(verdict_counts.get("exact", 0)),
        "selected_partial": int(verdict_counts.get("partial", 0)),
        "selected_miss": int(verdict_counts.get("miss", 0)),
        "perfect_selector_counts": dict(Counter(str(row.get("best_verdict", "unknown")) for row in rows)),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# QA Mode Selector Without Oracle",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "This report asks an LLM selector to choose among existing query-evidence modes.",
        "The selector does not receive source prose, answer keys, judge labels, or failure labels.",
        "",
        "## Summary",
        "",
        f"- Rows: `{summary.get('row_count', 0)}`",
        f"- Selector errors: `{summary.get('selector_error_count', 0)}`",
        f"- Selected best available mode: `{summary.get('selected_best_count', 0)}`",
        f"- Selection sources: `{summary.get('selection_source_counts', {})}`",
        f"- Selected verdicts: `{summary.get('selected_exact', 0)} exact / {summary.get('selected_partial', 0)} partial / {summary.get('selected_miss', 0)} miss`",
        f"- Perfect selector upper bound: `{summary.get('perfect_selector_counts', {})}`",
        "",
        "## Rows",
        "",
        "| Row | Source | Selected | Selected Verdict | Best | Mode Verdicts | Note | Guard |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.get("rows", []):
        if not isinstance(row, dict):
            continue
        verdicts = row.get("mode_verdicts", {}) if isinstance(row.get("mode_verdicts"), dict) else {}
        verdict_text = ", ".join(f"{label}:{verdict}" for label, verdict in verdicts.items())
        note = "best" if row.get("selected_is_best") else "missed-best"
        if row.get("error"):
            note = f"error: {row.get('error')}"
        source = str(row.get("selection_source", "") or "")
        guard = str(row.get("baseline_guard_reason", "") or row.get("specialized_guard_reason", "") or "")
        lines.append(
            f"| `{row.get('id', '')}` | `{source}` | `{row.get('selected_mode', '')}` | "
            f"`{row.get('selected_verdict', '')}` | `{','.join(row.get('best_labels', []))}` | "
            f"{verdict_text} | {note} | {guard} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def display_path(value: Any) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
