#!/usr/bin/env python3
"""Select among existing QA evidence modes without source or answer-key access.

This is a query-surface experiment. It reads existing QA artifacts, strips
reference answers, judge labels, oracle fields, and failure-surface labels, then
asks an LLM to choose which mode has the strongest structured evidence for each
question.

The selector does not read source prose, gold KBs, strategy files, or answer
keys. Python does not derive answers from text; it packages already-executed
query evidence and scores the selected mode against existing judge labels only
after the model selection is complete.
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
        help="Comparison group in the form name:label=path,label=path.",
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
        choices=["direct", "completeness"],
        default="direct",
        help="Selector policy. direct is the stable default; completeness is an experimental broad-support policy.",
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
    group = load_group(args.group)
    rows = build_rows(
        group,
        sample_row_limit=int(args.sample_row_limit),
        include_self_check=bool(args.include_self_check),
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
                selection_policy=str(args.selection_policy),
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
            "artifacts": [{"label": item["label"], "path": display_path(item["path"])} for item in group["artifacts"]],
        },
        "selection_policy": str(args.selection_policy),
        "include_self_check": bool(args.include_self_check),
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
        path = Path(raw_path.strip())
        path = path if path.is_absolute() else REPO_ROOT / path
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        artifacts.append({"label": label.strip(), "path": path, "record": payload})
    return {"name": name.strip(), "artifacts": artifacts, "labels": [item["label"] for item in artifacts]}


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
    messages = [
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
        f"{base_url.rstrip('/')}/chat/completions" if base_url.rstrip("/").endswith("/v1") else f"{base_url.rstrip('/')}/v1/chat/completions",
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
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise RuntimeError("selector returned non-object JSON")
    return parsed


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
    return {
        "row_count": len(rows),
        "selector_error_count": sum(1 for row in rows if row.get("error")),
        "selected_best_count": sum(1 for row in rows if row.get("selected_is_best")),
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
        f"- Selected verdicts: `{summary.get('selected_exact', 0)} exact / {summary.get('selected_partial', 0)} partial / {summary.get('selected_miss', 0)} miss`",
        f"- Perfect selector upper bound: `{summary.get('perfect_selector_counts', {})}`",
        "",
        "## Rows",
        "",
        "| Row | Selected | Selected Verdict | Best | Mode Verdicts | Note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.get("rows", []):
        if not isinstance(row, dict):
            continue
        verdicts = row.get("mode_verdicts", {}) if isinstance(row.get("mode_verdicts"), dict) else {}
        verdict_text = ", ".join(f"{label}:{verdict}" for label, verdict in verdicts.items())
        note = "best" if row.get("selected_is_best") else "missed-best"
        if row.get("error"):
            note = f"error: {row.get('error')}"
        lines.append(
            f"| `{row.get('id', '')}` | `{row.get('selected_mode', '')}` | `{row.get('selected_verdict', '')}` | `{','.join(row.get('best_labels', []))}` | {verdict_text} | {note} |"
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
