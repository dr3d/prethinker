#!/usr/bin/env python3
"""Score direct frontier QA outputs against fixture oracles.

The scorer reads run-level raw answers from run_frontier_direct_qa.py and judges
them with a shared exact/partial/miss policy. It does not call or inspect
Prethinker compile artifacts.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_direct_scored"

DIRECT_QA_JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "verdict", "answer_supported", "concise_rationale", "issues"],
    "properties": {
        "schema_version": {"type": "string", "const": "direct_qa_judge_v1"},
        "verdict": {"type": "string", "enum": ["exact", "partial", "miss", "not_judged"]},
        "answer_supported": {"type": "boolean"},
        "concise_rationale": {"type": "string", "maxLength": 600},
        "issues": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 300}},
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Direct QA JSON or JSONL artifact.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--judge-model", required=True)
    parser.add_argument("--judge-base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--judge-api-key", default="")
    parser.add_argument("--judge-api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--response-format",
        choices=["json_schema", "plain_json"],
        default="json_schema",
        help="Use plain_json for local endpoints that do not support OpenAI JSON schema response_format.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = _resolve(Path(args.input))
    rows = _load_direct_rows(input_path)
    api_key = str(args.judge_api_key or os.environ.get(str(args.judge_api_key_env), "") or "").strip()
    scored = score_rows(
        rows,
        judge_model=str(args.judge_model),
        judge_base_url=str(args.judge_base_url),
        judge_api_key=api_key,
        timeout=int(args.timeout),
        max_tokens=int(args.max_tokens),
        dry_run=bool(args.dry_run),
        workers=int(args.workers),
        response_format=str(args.response_format),
    )
    summary = _summarize(scored)
    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem
    out_json = out_dir / f"{stem}_scored.json"
    out_jsonl = out_dir / f"{stem}_scored.jsonl"
    payload = {
        "schema_version": "frontier_direct_qa_scored_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "input": str(input_path),
        "judge_model": str(args.judge_model),
        "dry_run": bool(args.dry_run),
        "summary": summary,
        "rows": scored,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_jsonl.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in scored), encoding="utf-8")
    print(json.dumps({"rows": len(scored), "summary": summary, "json": str(out_json), "jsonl": str(out_jsonl)}, indent=2))
    return 0


def score_rows(
    rows: list[dict[str, Any]],
    *,
    judge_model: str,
    judge_base_url: str,
    judge_api_key: str,
    timeout: int,
    max_tokens: int,
    dry_run: bool,
    workers: int,
    response_format: str = "json_schema",
) -> list[dict[str, Any]]:
    if workers <= 1:
        return [
            score_row(
                row,
                judge_model=judge_model,
                judge_base_url=judge_base_url,
                judge_api_key=judge_api_key,
                timeout=timeout,
                max_tokens=max_tokens,
                dry_run=dry_run,
                response_format=response_format,
            )
            for row in rows
        ]
    scored: list[dict[str, Any] | None] = [None] * len(rows)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        future_map = {
            pool.submit(
                score_row,
                row,
                judge_model=judge_model,
                judge_base_url=judge_base_url,
                judge_api_key=judge_api_key,
                timeout=timeout,
                max_tokens=max_tokens,
                dry_run=dry_run,
                response_format=response_format,
            ): index
            for index, row in enumerate(rows)
        }
        for future in concurrent.futures.as_completed(future_map):
            scored[future_map[future]] = future.result()
    return [row for row in scored if isinstance(row, dict)]


def score_row(
    row: dict[str, Any],
    *,
    judge_model: str,
    judge_base_url: str,
    judge_api_key: str,
    timeout: int,
    max_tokens: int,
    dry_run: bool,
    response_format: str = "json_schema",
) -> dict[str, Any]:
    oracle = _load_oracle_for_row(row)
    payload = build_judge_payload(row=row, oracle=oracle)
    if dry_run:
        judge = {
            "schema_version": "direct_qa_judge_v1",
            "verdict": "not_judged",
            "answer_supported": False,
            "concise_rationale": "dry run",
            "issues": [],
            "judge_payload": payload,
        }
        return {**row, "reference_answer": oracle.get("reference_answer", ""), "reference_judge": judge}
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict benchmark scorer. Return direct_qa_judge_v1 JSON only. "
                "Judge the model answer against the reference answer and question; do not use outside knowledge."
            ),
        },
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]
    try:
        if response_format == "plain_json":
            judge = _call_plain_json(
                model=judge_model,
                base_url=judge_base_url,
                api_key=judge_api_key,
                messages=messages,
                timeout=timeout,
                max_tokens=max_tokens,
            )
        else:
            judge = _call_json_schema(
                model=judge_model,
                base_url=judge_base_url,
                api_key=judge_api_key,
                messages=messages,
                schema=DIRECT_QA_JUDGE_SCHEMA,
                schema_name="direct_qa_judge_v1",
                timeout=timeout,
                max_tokens=max_tokens,
            )
    except Exception as exc:
        judge = {
            "schema_version": "direct_qa_judge_v1",
            "verdict": "not_judged",
            "answer_supported": False,
            "concise_rationale": "",
            "issues": [f"judge error: {exc}"],
        }
    return {**row, "reference_answer": oracle.get("reference_answer", ""), "reference_judge": judge}


def _call_plain_json(
    *,
    model: str,
    base_url: str,
    api_key: str,
    messages: list[dict[str, str]],
    timeout: int,
    max_tokens: int,
) -> dict[str, Any]:
    plain_messages = [
        {
            "role": "system",
            "content": (
                "You are a strict benchmark scorer. Return only one JSON object with keys: "
                "schema_version, verdict, answer_supported, concise_rationale, issues. "
                "verdict must be exact, partial, miss, or not_judged."
            ),
        },
        *messages[1:],
    ]
    payload = {
        "model": model,
        "messages": plain_messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        _chat_url(base_url),
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8", errors="replace"))
            content = str(data["choices"][0]["message"]["content"]).strip()
            return _normalize_judge_json(_extract_first_json_object(content))
        except (KeyError, IndexError, TypeError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(1)
                continue
    raise RuntimeError(f"plain judge call failed: {last_error}")


def build_judge_payload(*, row: dict[str, Any], oracle: dict[str, Any]) -> dict[str, Any]:
    return {
        "task": "Judge a direct source-plus-question model answer against a reference answer.",
        "question_id": row.get("question_id", ""),
        "fixture": row.get("fixture", ""),
        "category": row.get("category") or oracle.get("category", ""),
        "question": row.get("question", ""),
        "reference_answer": oracle.get("reference_answer", ""),
        "model_answer": row.get("answer", ""),
        "verdict_policy": [
            "exact: the answer gives the materially correct reference answer, including needed scope, date, authority, status, or unresolved-state qualifiers.",
            "partial: the answer is substantially relevant but loses an important qualifier, source boundary, temporal/status distinction, count, identifier, or uncertainty.",
            "miss: the answer is wrong, unsupported, contradicts the reference, invents an answer where the source is unresolved/silent, or fails to answer.",
            "not_judged: missing reference answer, missing model answer, or malformed row.",
            "Do not reward fluent unsupported completion. Supported restraint can be exact when the reference answer is unresolved or not stated.",
        ],
    }


def _load_direct_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("rows"), list):
        return [row for row in data["rows"] if isinstance(row, dict)]
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    return []


def _load_oracle_for_row(row: dict[str, Any]) -> dict[str, Any]:
    source_file = Path(str(row.get("source_file", "")))
    if not source_file.is_absolute():
        source_file = REPO_ROOT / source_file
    oracle_path = source_file.parent / "oracle.jsonl"
    qid = str(row.get("question_id", "")).strip()
    if not oracle_path.exists() or not qid:
        return {}
    for line in oracle_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict) and str(value.get("id", value.get("source_id", ""))).strip() == qid:
            return value
    return {}


def _call_json_schema(
    *,
    model: str,
    base_url: str,
    api_key: str,
    messages: list[dict[str, str]],
    schema: dict[str, Any],
    schema_name: str,
    timeout: int,
    max_tokens: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema,
            },
        },
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        _chat_url(base_url),
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8", errors="replace"))
            content = str(data["choices"][0]["message"]["content"]).strip()
            return _normalize_judge_json(json.loads(content))
        except (KeyError, IndexError, TypeError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(1)
                continue
    raise RuntimeError(f"judge call failed: {last_error}")


def _extract_first_json_object(text: str) -> dict[str, Any]:
    stripped = str(text or "").strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        stripped = fence.group(1).strip()
    try:
        data = json.loads(stripped)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    if start < 0:
        raise ValueError("no JSON object found")
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(stripped)):
        char = stripped[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                data = json.loads(stripped[start : index + 1])
                if isinstance(data, dict):
                    return data
                break
    raise ValueError("no complete JSON object found")


def _normalize_judge_json(data: dict[str, Any]) -> dict[str, Any]:
    verdict = str(data.get("verdict") or "not_judged").strip().lower()
    if verdict not in {"exact", "partial", "miss", "not_judged"}:
        verdict = "not_judged"
    issues = data.get("issues") if isinstance(data.get("issues"), list) else []
    return {
        "schema_version": "direct_qa_judge_v1",
        "verdict": verdict,
        "answer_supported": bool(data.get("answer_supported", verdict == "exact")),
        "concise_rationale": str(data.get("concise_rationale") or data.get("rationale") or "")[:600],
        "issues": [str(item)[:300] for item in issues[:8]],
    }


def _chat_url(base_url: str) -> str:
    stripped = str(base_url or "").rstrip("/")
    if stripped.endswith("/chat/completions"):
        return stripped
    if stripped.endswith("/v1"):
        return f"{stripped}/chat/completions"
    return f"{stripped}/v1/chat/completions"


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    for row in rows:
        judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
        verdict = str(judge.get("verdict") or "not_judged")
        counts.update([verdict])
    total = len(rows)
    exact = int(counts.get("exact", 0))
    return {
        "rows": total,
        "verdict_counts": dict(sorted(counts.items())),
        "exact_rate": round(exact / total, 4) if total else 0.0,
    }


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
