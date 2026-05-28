#!/usr/bin/env python3
"""Populate and score an ACH stress payload without mutating KB state."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from typing import Any
import urllib.error
import urllib.request


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.ach_overlay import analyze_ach_overlay  # noqa: E402
from src.model_path import (  # noqa: E402
    apply_openrouter_provider_env,
    is_openrouter_base_url,
    openrouter_api_key,
    openrouter_generation_metadata,
    openrouter_metadata_headers,
    openrouter_provider_routing_from_env,
    provider_family,
)
from src.semantic_ir import bootstrap_env_local  # noqa: E402


DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "ach_payload_proposer_runs"
VALID_ASSESSMENTS = {"consistent", "inconsistent", "neutral", "not_applicable"}
VALID_DIAGNOSTICITY = {"low", "medium", "high", "critical"}


PROPOSER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["evidence_diagnosticity", "judgments"],
    "properties": {
        "evidence_diagnosticity": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["evidence_id", "diagnosticity", "rationale"],
                "properties": {
                    "evidence_id": {"type": "string"},
                    "diagnosticity": {"type": "string", "enum": sorted(VALID_DIAGNOSTICITY)},
                    "rationale": {"type": "string", "maxLength": 360},
                },
            },
        },
        "judgments": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["evidence_id", "hypothesis_id", "assessment", "rationale"],
                "properties": {
                    "evidence_id": {"type": "string"},
                    "hypothesis_id": {"type": "string"},
                    "assessment": {"type": "string", "enum": sorted(VALID_ASSESSMENTS)},
                    "rationale": {"type": "string", "maxLength": 360},
                },
            },
        },
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, required=True, help="ACH stress payload JSON.")
    parser.add_argument("--source", type=Path, default=None, help="Optional source.md for local excerpt context.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--model", default=os.environ.get("PRETHINKER_MODEL", "qwen/qwen3.6-35b-a3b"))
    parser.add_argument("--base-url", default=os.environ.get("PRETHINKER_BASE_URL", "https://openrouter.ai/api/v1"))
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--openrouter-provider-order", default="")
    parser.add_argument("--openrouter-provider-only", default="")
    parser.add_argument("--openrouter-provider-ignore", default="")
    parser.add_argument("--openrouter-quantizations", default="")
    parser.add_argument("--openrouter-allow-fallbacks", choices=["", "true", "false"], default="")
    parser.add_argument("--openrouter-require-parameters", choices=["", "true", "false"], default="")
    return parser.parse_args()


def main() -> int:
    bootstrap_env_local()
    args = parse_args()
    apply_openrouter_provider_env(
        order=args.openrouter_provider_order,
        only=args.openrouter_provider_only,
        ignore=args.openrouter_provider_ignore,
        quantizations=args.openrouter_quantizations,
        allow_fallbacks=args.openrouter_allow_fallbacks,
        require_parameters=args.openrouter_require_parameters,
    )
    payload_path = _resolve(args.payload)
    payload = json.loads(payload_path.read_text(encoding="utf-8-sig"))
    source_path = _resolve(args.source) if args.source else payload_path.parent / "source.md"
    source_text = source_path.read_text(encoding="utf-8-sig", errors="replace") if source_path.exists() else ""

    messages = build_messages(payload=payload, source_text=source_text)
    call = call_json_schema(
        base_url=str(args.base_url),
        model=str(args.model),
        messages=messages,
        schema=PROPOSER_SCHEMA,
        schema_name="ach_judgment_proposal_v1",
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        max_tokens=int(args.max_tokens),
    )
    proposal = json.loads(call["content"])
    scorer_payload = build_scorer_payload(payload, proposal)
    ach_report = analyze_ach_overlay(scorer_payload)
    report = build_report(
        payload=payload,
        payload_path=payload_path,
        source_path=source_path,
        scorer_payload=scorer_payload,
        proposal=proposal,
        ach_report=ach_report,
        call=call,
        model=str(args.model),
        base_url=str(args.base_url),
    )

    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(payload.get("fixture_id") or payload_path.parent.name or payload_path.stem))
    out_json = _resolve(args.out_json) if args.out_json else out_dir / f"{slug}_ach_payload_proposal.json"
    out_md = _resolve(args.out_md) if args.out_md else out_dir / f"{slug}_ach_payload_proposal.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_messages(*, payload: dict[str, Any], source_text: str) -> list[dict[str, str]]:
    prompt_payload = public_prompt_payload(payload)
    source = str(source_text or "")
    if len(source) > 36000:
        source = source[:36000] + "\n[TRUNCATED]"
    return [
        {
            "role": "system",
            "content": (
                "/no_think\n"
                "You populate an Analysis of Competing Hypotheses matrix. "
                "Use only the supplied source text, hypotheses, and evidence anchors. "
                "Do not decide by counting supportive rows; mark each evidence row against each hypothesis. "
                "Assessments must be one of consistent, inconsistent, neutral, or not_applicable. "
                "Diagnosticity describes how much the evidence discriminates among hypotheses."
            ),
        },
        {
            "role": "user",
            "content": (
                "ACH task payload, with fixture oracle fields intentionally omitted:\n"
                + json.dumps(prompt_payload, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n\nSOURCE TEXT:\n"
                + source
            ),
        },
    ]


def public_prompt_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": payload.get("fixture_id", ""),
        "ach_question": payload.get("ach_question", ""),
        "hypotheses": [
            {
                "id": item.get("id", ""),
                "label": item.get("label", ""),
                "claim": item.get("claim", ""),
            }
            for item in payload.get("hypotheses", [])
            if isinstance(item, dict)
        ],
        "evidence_rows": [
            {
                "id": item.get("id", ""),
                "label": item.get("label", ""),
                "source_coords": item.get("source_coords", ""),
                "text_anchor": item.get("text_anchor", ""),
            }
            for item in payload.get("evidence_rows", [])
            if isinstance(item, dict)
        ],
    }


def build_scorer_payload(payload: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
    diagnosticity_by_id = {
        str(item.get("evidence_id") or "").strip(): str(item.get("diagnosticity") or "medium").strip().casefold()
        for item in proposal.get("evidence_diagnosticity", [])
        if isinstance(item, dict)
    }
    evidence = []
    for item in payload.get("evidence_rows", []) or []:
        if not isinstance(item, dict):
            continue
        evidence_id = str(item.get("id") or "").strip()
        diagnosticity = diagnosticity_by_id.get(evidence_id, "medium")
        if diagnosticity not in VALID_DIAGNOSTICITY:
            diagnosticity = "medium"
        evidence.append(
            {
                "id": evidence_id,
                "label": str(item.get("label") or evidence_id),
                "diagnosticity": diagnosticity,
                "source_coords": str(item.get("source_coords") or ""),
                "text_anchor": str(item.get("text_anchor") or ""),
            }
        )
    hypothesis_ids = {str(item.get("id") or "").strip() for item in payload.get("hypotheses", []) if isinstance(item, dict)}
    evidence_ids = {item["id"] for item in evidence}
    judgments = []
    seen: set[tuple[str, str]] = set()
    for item in proposal.get("judgments", []) or []:
        if not isinstance(item, dict):
            continue
        evidence_id = str(item.get("evidence_id") or "").strip()
        hypothesis_id = str(item.get("hypothesis_id") or "").strip()
        key = (evidence_id, hypothesis_id)
        if evidence_id not in evidence_ids or hypothesis_id not in hypothesis_ids or key in seen:
            continue
        assessment = str(item.get("assessment") or "").strip().casefold()
        if assessment not in VALID_ASSESSMENTS:
            continue
        seen.add(key)
        judgments.append(
            {
                "evidence_id": evidence_id,
                "hypothesis_id": hypothesis_id,
                "assessment": assessment,
                "rationale": str(item.get("rationale") or "").strip()[:360],
            }
        )
    return {
        "schema_version": "ach_overlay_payload_v1",
        "hypotheses": [
            {"id": str(item.get("id") or ""), "label": str(item.get("label") or ""), "claim": str(item.get("claim") or "")}
            for item in payload.get("hypotheses", [])
            if isinstance(item, dict)
        ],
        "evidence": evidence,
        "judgments": judgments,
    }


def build_report(
    *,
    payload: dict[str, Any],
    payload_path: Path,
    source_path: Path,
    scorer_payload: dict[str, Any],
    proposal: dict[str, Any],
    ach_report: dict[str, Any],
    call: dict[str, Any],
    model: str,
    base_url: str,
) -> dict[str, Any]:
    top = [
        item["hypothesis_id"]
        for item in ach_report.get("hypothesis_scores", []) or []
        if isinstance(item, dict) and item.get("rank") == 1
    ]
    expected = payload.get("expected_read") if isinstance(payload.get("expected_read"), dict) else {}
    expected_best = str(expected.get("best_hypothesis") or "").strip()
    sensitivity = ach_report.get("sensitivity", []) if isinstance(ach_report.get("sensitivity"), list) else []
    pivotal = str(expected.get("pivotal_evidence") or "").strip()
    return {
        "schema_version": "ach_payload_proposal_run_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "payload_path": _display_path(payload_path),
        "source_path": _display_path(source_path),
        "policy": [
            "The LLM proposes ACH judgments only; it does not write KB facts or mutate QA verdicts.",
            "The prompt omits expected_read and expected_relevance fields to avoid oracle leakage.",
            "The deterministic scorer ranks hypotheses by least disconfirmation and computes single-row sensitivity.",
        ],
        "model_serving_path": {
            "provider_family": provider_family(backend="lmstudio", base_url=base_url),
            "model": model,
            "base_url": base_url,
            "provider_routing": openrouter_provider_routing_from_env() if is_openrouter_base_url(base_url) else {},
        },
        "openrouter_generation_metadata": call.get("openrouter_generation_metadata", {}),
        "summary": {
            "fixture_id": str(payload.get("fixture_id") or ""),
            "matrix_complete": bool(ach_report.get("matrix_complete")),
            "warning_count": len(ach_report.get("warnings", []) or []),
            "hypothesis_count": int(ach_report.get("hypothesis_count", 0) or 0),
            "evidence_count": int(ach_report.get("evidence_count", 0) or 0),
            "judgment_count": int(ach_report.get("judgment_count", 0) or 0),
            "top_hypotheses": top,
            "expected_best_hypothesis": expected_best,
            "best_matches_expected": bool(expected_best and top == [expected_best]),
            "sensitivity_count": len(sensitivity),
            "sensitivity_evidence_ids": [str(item.get("evidence_id") or "") for item in sensitivity if isinstance(item, dict)],
            "expected_sensitivity": str(expected.get("sensitivity_expectation") or ""),
            "expected_pivotal_evidence": pivotal,
            "pivotal_found_in_sensitivity": bool(pivotal and any(item.get("evidence_id") == pivotal for item in sensitivity if isinstance(item, dict))),
            "latency_ms": int(call.get("latency_ms", 0) or 0),
        },
        "scorer_payload": scorer_payload,
        "proposal": proposal,
        "ach_report": ach_report,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# ACH Payload Proposal Run",
        "",
        f"Generated: `{report.get('generated_at', '')}`",
        f"Payload: `{report.get('payload_path', '')}`",
        f"Source: `{report.get('source_path', '')}`",
        "",
        "## Summary",
        "",
        f"- Fixture: `{summary.get('fixture_id', '')}`",
        f"- Matrix complete: `{summary.get('matrix_complete', False)}`",
        f"- Hypotheses / evidence / judgments: `{summary.get('hypothesis_count', 0)} / {summary.get('evidence_count', 0)} / {summary.get('judgment_count', 0)}`",
        f"- Warnings: `{summary.get('warning_count', 0)}`",
        f"- Top hypotheses: `{summary.get('top_hypotheses', [])}`",
        f"- Expected best: `{summary.get('expected_best_hypothesis', '')}`",
        f"- Best matches expected: `{summary.get('best_matches_expected', False)}`",
        f"- Sensitivity rows: `{summary.get('sensitivity_count', 0)}`",
        f"- Sensitivity evidence ids: `{summary.get('sensitivity_evidence_ids', [])}`",
        f"- Expected sensitivity: `{summary.get('expected_sensitivity', '')}`",
        f"- Expected pivotal evidence: `{summary.get('expected_pivotal_evidence', '')}`",
        f"- Pivotal found in sensitivity: `{summary.get('pivotal_found_in_sensitivity', False)}`",
        "",
        "## Hypothesis Scores",
        "",
        "| Rank | Hypothesis | Inconsistency | Consistency | Missing |",
        "| ---: | --- | ---: | ---: | ---: |",
    ]
    ach_report = report.get("ach_report", {}) if isinstance(report.get("ach_report"), dict) else {}
    for row in ach_report.get("hypothesis_scores", []) or []:
        if not isinstance(row, dict):
            continue
        label = str(row.get("label", row.get("hypothesis_id", ""))).replace("|", "/")
        lines.append(
            f"| {row.get('rank', '')} | `{row.get('hypothesis_id', '')}` {label} | "
            f"{row.get('inconsistency_weight', 0)} | {row.get('consistency_weight', 0)} | "
            f"{row.get('missing_judgment_count', 0)} |"
        )
    sensitivity = ach_report.get("sensitivity", []) if isinstance(ach_report.get("sensitivity"), list) else []
    if sensitivity:
        lines.extend(["", "## Sensitivity", "", "| Evidence | Baseline Top | Top Without Evidence |", "| --- | --- | --- |"])
        for row in sensitivity:
            if not isinstance(row, dict):
                continue
            label = str(row.get("label", row.get("evidence_id", ""))).replace("|", "/")
            lines.append(
                f"| `{row.get('evidence_id', '')}` {label} | `{row.get('baseline_top', [])}` | "
                f"`{row.get('top_without_evidence', [])}` |"
            )
    lines.append("")
    return "\n".join(lines)


def call_json_schema(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    schema: dict[str, Any],
    schema_name: str,
    timeout: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "think": False,
        "thinking": False,
        "reasoning": {"effort": "none", "exclude": True},
        "include_reasoning": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
    }
    if is_openrouter_base_url(base_url):
        provider_routing = openrouter_provider_routing_from_env()
        if provider_routing:
            payload["provider"] = provider_routing
    started = time.perf_counter()
    request = urllib.request.Request(
        _chat_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers=_headers(base_url),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=int(timeout)) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    if not content:
        content = str(message.get("reasoning_content", "") if isinstance(message, dict) else "").strip()
    if not content:
        raise RuntimeError("model returned empty ACH proposal content")
    metadata = openrouter_generation_metadata(
        raw_response=raw,
        request_payload=payload,
        base_url=base_url,
        timeout=min(int(timeout), 30),
        call_role=schema_name,
    )
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "content": content,
        "raw": raw,
        "openrouter_generation_metadata": metadata,
    }


def _headers(base_url: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if is_openrouter_base_url(base_url):
        key = openrouter_api_key()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        headers.update(openrouter_metadata_headers(base_url))
        headers["HTTP-Referer"] = "https://github.com/dr3d/prethinker"
        headers["X-Title"] = "ach-payload-proposer"
        headers["X-OpenRouter-Title"] = "ach-payload-proposer"
    else:
        key = str(os.environ.get("PRETHINKER_API_KEY") or "").strip()
        if key:
            headers["Authorization"] = f"Bearer {key}"
    return headers


def _chat_url(base_url: str) -> str:
    base = str(base_url or "").rstrip("/")
    return f"{base}/chat/completions" if base.endswith("/v1") else f"{base}/v1/chat/completions"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return ""
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


def _slug(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or ""))
    out = "-".join(part for part in out.split("-") if part)
    return out or "ach-payload-proposal"


if __name__ == "__main__":
    raise SystemExit(main())
