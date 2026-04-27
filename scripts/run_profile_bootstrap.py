#!/usr/bin/env python3
"""Ask a local model to propose a draft domain profile from sample text.

Artifacts stay under tmp/ because profile bootstrapping is research material:
the model proposes a vocabulary, but nothing becomes an approved profile until
reviewed and tested.
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
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "profile_bootstrap"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.profile_bootstrap import (  # noqa: E402
    PROFILE_BOOTSTRAP_JSON_SCHEMA,
    build_profile_bootstrap_messages,
    parse_profile_bootstrap_json,
    profile_bootstrap_score,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(value: str) -> str:
    import re

    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip()).strip("-").lower()
    return text[:60] or "run"


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _load_jsonl(path: Path, *, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(_sample_from_row(parsed))
            if limit > 0 and len(rows) >= limit:
                break
    return rows


def _sample_from_row(row: dict[str, Any]) -> dict[str, Any]:
    text = str(row.get("text") or row.get("utterance") or row.get("excerpt") or "").strip()
    context = row.get("context") if isinstance(row.get("context"), list) else []
    source = str(row.get("source") or row.get("id") or row.get("provenance_url") or "").strip()
    return {
        "id": str(row.get("id") or source or f"sample_{abs(hash(text))}"),
        "source": source,
        "domain_hint": str(row.get("domain_hint") or row.get("domain") or "").strip(),
        "text": text,
        "context": [str(item) for item in context],
    }


def _call_lmstudio(
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
        "content_channel": "content" if content else ("reasoning_content" if reasoning_content else ""),
    }


def _call_ollama(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    timeout: int,
    temperature: float,
    top_p: float,
    top_k: int,
    num_ctx: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "think": False,
        "messages": messages,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "num_ctx": num_ctx,
        },
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
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
    message = raw.get("message", {}) if isinstance(raw, dict) else {}
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": str(message.get("content", "")).strip(),
        "content_channel": "content",
    }


def write_summary(record: dict[str, Any], path: Path) -> None:
    parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
    score = record.get("score") if isinstance(record.get("score"), dict) else {}
    predicates = parsed.get("candidate_predicates", []) if isinstance(parsed, dict) else []
    risks = parsed.get("admission_risks", []) if isinstance(parsed, dict) else []
    frontier = parsed.get("starter_frontier_cases", []) if isinstance(parsed, dict) else []
    lines = [
        "# Profile Bootstrap Run",
        "",
        f"Generated: {_utc_now()}",
        "",
        f"- Dataset: `{record.get('dataset', '')}`",
        f"- Backend/model: `{record.get('backend', '')}` / `{record.get('model', '')}`",
        f"- Domain hint: `{record.get('domain_hint', '')}`",
        f"- Parsed: `{record.get('parsed_ok', False)}`",
        f"- Score: `{score.get('rough_score', 0.0)}`",
        f"- Entity types: `{score.get('entity_type_count', 0)}`",
        f"- Candidate predicates: `{score.get('predicate_count', 0)}`",
        f"- Generic predicate count: `{score.get('generic_predicate_count', 0)}`",
        f"- Frontier unknown positive predicate count: `{score.get('frontier_unknown_positive_predicate_count', 0)}`",
        f"- Frontier unknown positive predicate refs: `{score.get('frontier_unknown_positive_predicate_refs', [])}`",
        f"- Admission risks: `{score.get('risk_count', 0)}`",
        f"- Starter frontier cases: `{score.get('frontier_case_count', 0)}`",
        "",
        "## Candidate Predicates",
        "",
    ]
    if predicates:
        for item in predicates:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- `{item.get('signature', '')}` args={item.get('args', [])}: {item.get('description', '')}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Admission Risks", ""])
    lines.extend([f"- {risk}" for risk in risks] or ["- none"])
    lines.extend(["", "## Starter Frontier Cases", ""])
    if frontier:
        for item in frontier:
            if not isinstance(item, dict):
                continue
            lines.append(f"- {item.get('expected_boundary', '')}: {item.get('utterance', '')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Full Parsed JSON", "", "```json", _json_dumps(parsed), "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run profile_bootstrap_v1 over a small sample dataset.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--domain-hint", default="")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--backend", choices=["lmstudio", "ollama"], default="lmstudio")
    parser.add_argument("--model", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--max-tokens", type=int, default=4096)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dataset = args.dataset
    if not dataset.is_absolute():
        dataset = (REPO_ROOT / dataset).resolve()
    samples = _load_jsonl(dataset, limit=max(1, int(args.limit)))
    backend = str(args.backend or "lmstudio").strip().lower()
    model = str(args.model or "").strip()
    if not model:
        model = "qwen/qwen3.6-35b-a3b" if backend == "lmstudio" else "qwen3.6:35b"
    base_url = str(args.base_url or "").strip()
    if not base_url:
        base_url = "http://127.0.0.1:1234" if backend == "lmstudio" else "http://127.0.0.1:11434"
    messages = build_profile_bootstrap_messages(samples=samples, domain_hint=str(args.domain_hint or ""))
    if backend == "lmstudio":
        response = _call_lmstudio(
            base_url=base_url,
            model=model,
            messages=messages,
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=int(args.max_tokens),
        )
    else:
        response = _call_ollama(
            base_url=base_url,
            model=model,
            messages=messages,
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            top_k=int(args.top_k),
            num_ctx=int(args.num_ctx),
        )
    parsed, parse_error = parse_profile_bootstrap_json(response.get("content", ""))
    score = profile_bootstrap_score(parsed)
    out_dir = args.out_dir
    if not out_dir.is_absolute():
        out_dir = (REPO_ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    slug = f"{slug}_{_slug(args.domain_hint or dataset.stem)}_{_slug(model)}"
    json_path = out_dir / f"profile_bootstrap_{slug}.json"
    md_path = json_path.with_suffix(".md")
    record = {
        "ts": _utc_now(),
        "dataset": str(dataset),
        "domain_hint": str(args.domain_hint or ""),
        "backend": backend,
        "model": model,
        "options": {
            "temperature": float(args.temperature),
            "top_p": float(args.top_p),
            "top_k": int(args.top_k),
            "num_ctx": int(args.num_ctx),
            "max_tokens": int(args.max_tokens),
        },
        "model_input": {"messages": messages, "samples": samples},
        "latency_ms": response.get("latency_ms", 0),
        "content": response.get("content", ""),
        "content_channel": response.get("content_channel", ""),
        "parsed": parsed,
        "parsed_ok": parsed is not None,
        "parse_error": parse_error,
        "score": score,
    }
    json_path.write_text(_json_dumps(record), encoding="utf-8")
    write_summary(record, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(json.dumps({"parsed_ok": record["parsed_ok"], "score": score}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
