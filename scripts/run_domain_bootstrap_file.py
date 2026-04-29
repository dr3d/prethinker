#!/usr/bin/env python3
"""Bootstrap a draft domain profile from one raw text file.

This runner is intentionally small and literal: Python reads the file and hands
the raw text to the LLM profile-bootstrap pass. It does not derive predicates,
split the text semantically, rewrite phrases, or inspect the language. The model
proposes the candidate predicate surface; deterministic code only validates,
scores, and optionally uses that draft surface in the ordinary Semantic IR path.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_file"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.profile_bootstrap import (  # noqa: E402
    PROFILE_BOOTSTRAP_JSON_SCHEMA,
    build_profile_bootstrap_messages,
    parse_profile_bootstrap_json,
    profile_bootstrap_allowed_predicates,
    profile_bootstrap_domain_context,
    profile_bootstrap_predicate_contracts,
    profile_bootstrap_score,
)
from src.semantic_ir import (  # noqa: E402
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLM-owned profile bootstrap over a raw text file.")
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument("--domain-hint", default="")
    parser.add_argument("--backend", choices=["lmstudio"], default="lmstudio")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument(
        "--compile-source",
        action="store_true",
        help="After profile bootstrap, run the same raw source through Semantic IR using the draft profile.",
    )
    parser.add_argument("--include-model-input", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text_path = args.text_file if args.text_file.is_absolute() else (REPO_ROOT / args.text_file).resolve()
    source_text = text_path.read_text(encoding="utf-8-sig")
    sample = {
        "id": text_path.stem,
        "source": str(text_path),
        "domain_hint": str(args.domain_hint or "").strip(),
        "text": source_text,
        "context": [
            "Raw source file. Python has not segmented, summarized, or derived predicates from this text.",
            "The LLM bootstrap pass must propose the candidate predicate/entity surface.",
        ],
    }
    messages = build_profile_bootstrap_messages(samples=[sample], domain_hint=str(args.domain_hint or ""))
    started = time.perf_counter()
    response = _call_lmstudio_json_schema(
        base_url=str(args.base_url),
        model=str(args.model),
        messages=messages,
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        max_tokens=int(args.max_tokens),
    )
    parsed, error = parse_profile_bootstrap_json(str(response.get("content", "")))
    score = profile_bootstrap_score(parsed)
    record: dict[str, Any] = {
        "ts": _utc_now(),
        "text_file": str(text_path),
        "domain_hint": str(args.domain_hint or ""),
        "backend": str(args.backend),
        "model": str(args.model),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parsed_ok": isinstance(parsed, dict),
        "parse_error": error,
        "score": score,
        "parsed": parsed or {},
        "raw_content": str(response.get("content", ""))[:20000],
    }
    if args.include_model_input:
        record["model_input"] = {"messages": messages}
    if bool(args.compile_source) and isinstance(parsed, dict):
        record["source_compile"] = _compile_source_with_draft_profile(
            source_text=source_text,
            parsed_profile=parsed,
            args=args,
        )

    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(text_path.stem)}_{_slug(str(args.model))}"
    json_path = out_dir / f"domain_bootstrap_file_{slug}.json"
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(record, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(
        json.dumps(
            {
                "parsed_ok": record["parsed_ok"],
                "score": score,
                "candidate_predicates": score.get("predicate_count", 0),
                "compile_admitted": (record.get("source_compile") or {}).get("admitted_count"),
                "compile_skipped": (record.get("source_compile") or {}).get("skipped_count"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _compile_source_with_draft_profile(*, source_text: str, parsed_profile: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    allowed_predicates = profile_bootstrap_allowed_predicates(parsed_profile)
    predicate_contracts = profile_bootstrap_predicate_contracts(parsed_profile)
    domain_context = profile_bootstrap_domain_context(parsed_profile)
    config = SemanticIRCallConfig(
        backend="lmstudio",
        base_url=str(args.base_url),
        model=str(args.model),
        context_length=int(args.num_ctx),
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        top_k=int(args.top_k),
        max_tokens=int(args.max_tokens),
        think_enabled=False,
        reasoning_effort="none",
    )
    try:
        result = call_semantic_ir(
            utterance=source_text,
            config=config,
            context=[
                "Compile the raw source text using the draft profile proposed by profile_bootstrap_v1.",
                "Do not add facts not present in the source text.",
                "If the whole source contains more safe facts than fit, preserve the highest-signal source-grounded facts and note segment_required_for_complete_ingestion.",
            ],
            domain_context=domain_context,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
            kb_context_pack={},
            domain=f"profile_bootstrap:{parsed_profile.get('domain_guess', 'unknown')}",
            include_model_input=False,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    ir = result.get("parsed") if isinstance(result, dict) else None
    if not isinstance(ir, dict):
        return {
            "ok": False,
            "error": str(result.get("parse_error", "semantic_ir_parse_failed")) if isinstance(result, dict) else "semantic_ir_failed",
            "raw_content": str((result or {}).get("content", ""))[:4000] if isinstance(result, dict) else "",
        }
    mapped, warnings = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    return {
        "ok": True,
        "model_decision": ir.get("decision", ""),
        "projected_decision": diagnostics.get("projected_decision", ""),
        "admitted_count": int(diagnostics.get("admitted_count", 0) or 0),
        "skipped_count": int(diagnostics.get("skipped_count", 0) or 0),
        "warnings": warnings,
        "facts": mapped.get("facts", []),
        "rules": mapped.get("rules", []),
        "queries": mapped.get("queries", []),
        "self_check": ir.get("self_check", {}),
    }


def _call_lmstudio_json_schema(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
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
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "profile_bootstrap_v1",
                "strict": True,
                "schema": PROFILE_BOOTSTRAP_JSON_SCHEMA,
            },
        },
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc
    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    reasoning_content = str(message.get("reasoning_content", "") if isinstance(message, dict) else "").strip()
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": content or reasoning_content,
    }


def _write_summary(record: dict[str, Any], path: Path) -> None:
    parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
    score = record.get("score") if isinstance(record.get("score"), dict) else {}
    compile_record = record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {}
    lines = [
        "# Domain Bootstrap File Run",
        "",
        f"- Source file: `{record.get('text_file', '')}`",
        f"- Backend/model: `{record.get('backend', '')}` / `{record.get('model', '')}`",
        f"- Parsed: `{record.get('parsed_ok', False)}`",
        f"- Rough score: `{score.get('rough_score', 0.0)}`",
        f"- Entity types: `{score.get('entity_type_count', 0)}`",
        f"- Candidate predicates: `{score.get('predicate_count', 0)}`",
        f"- Generic predicates: `{score.get('generic_predicate_count', 0)}`",
        f"- Frontier unknown positive predicate refs: `{score.get('frontier_unknown_positive_predicate_refs', [])}`",
        "",
        "## Candidate Predicates",
        "",
    ]
    for item in parsed.get("candidate_predicates", []) if isinstance(parsed.get("candidate_predicates"), list) else []:
        if isinstance(item, dict):
            lines.append(f"- `{item.get('signature', '')}` args={item.get('args', [])}: {item.get('description', '')}")
    if not lines[-1].startswith("- `"):
        lines.append("- none")
    lines.extend(["", "## Admission Risks", ""])
    risks = [str(item).strip() for item in parsed.get("admission_risks", []) if str(item).strip()] if isinstance(parsed.get("admission_risks"), list) else []
    lines.extend([f"- {item}" for item in risks] or ["- none"])
    if compile_record:
        lines.extend(
            [
                "",
                "## Source Compile",
                "",
                f"- OK: `{compile_record.get('ok', False)}`",
                f"- Model decision: `{compile_record.get('model_decision', '')}`",
                f"- Projected decision: `{compile_record.get('projected_decision', '')}`",
                f"- Admitted: `{compile_record.get('admitted_count', 0)}`",
                f"- Skipped: `{compile_record.get('skipped_count', 0)}`",
                "",
                "### Facts",
                "",
                "```prolog",
                *[str(item) for item in compile_record.get("facts", [])],
                "```",
                "",
                "### Rules",
                "",
                "```prolog",
                *[str(item) for item in compile_record.get("rules", [])],
                "```",
            ]
        )
    lines.extend(["", "## Full Profile JSON", "", "```json", json.dumps(parsed, ensure_ascii=False, indent=2, sort_keys=True), "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(value: str) -> str:
    import re

    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip()).strip("-").lower()
    return text[:60] or "run"


if __name__ == "__main__":
    raise SystemExit(main())
