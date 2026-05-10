#!/usr/bin/env python3
"""Run direct source-plus-question QA for frontier model pilot rows.

This runner is intentionally not a Prethinker QA artifact runner. It gives each
model the same source document and question prompt, records every run-level
answer, and leaves scoring to a separate common-judge step.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_pilot_plan.json"
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_direct_outputs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-json", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--model", required=True, help="Concrete provider model id.")
    parser.add_argument("--provider", default="openai_compatible")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--runs-per-model", type=int, default=None)
    parser.add_argument("--limit-fixtures", type=int, default=0)
    parser.add_argument("--limit-rows", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan_path = _resolve(args.plan_json)
    plan = _read_json(plan_path)
    rows = build_direct_rows(
        plan,
        model=str(args.model),
        provider=str(args.provider),
        runs_per_model=int(args.runs_per_model or plan.get("run_settings", {}).get("runs_per_model", 1)),
        limit_fixtures=int(args.limit_fixtures),
        limit_rows=int(args.limit_rows),
        dry_run=bool(args.dry_run),
    )
    if not args.dry_run:
        api_key = str(args.api_key or os.environ.get(str(args.api_key_env), "") or "").strip()
        rows = _answer_rows(
            rows,
            base_url=str(args.base_url),
            api_key=api_key,
            timeout=int(args.timeout),
            max_tokens=int(args.max_tokens),
            workers=int(args.workers),
        )
    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(args.model))
    out_jsonl = out_dir / f"frontier_direct_qa_{slug}.jsonl"
    out_json = out_dir / f"frontier_direct_qa_{slug}.json"
    out_jsonl.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    payload = {
        "schema_version": "frontier_direct_qa_run_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "plan_json": str(plan_path),
        "model": str(args.model),
        "provider": str(args.provider),
        "dry_run": bool(args.dry_run),
        "row_count": len(rows),
        "rows": rows,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "json": str(out_json), "jsonl": str(out_jsonl)}, indent=2))
    return 0


def build_direct_rows(
    plan: dict[str, Any],
    *,
    model: str,
    provider: str,
    runs_per_model: int,
    limit_fixtures: int,
    limit_rows: int,
    dry_run: bool,
) -> list[dict[str, Any]]:
    fixtures = plan.get("fixtures") if isinstance(plan.get("fixtures"), list) else []
    if limit_fixtures > 0:
        fixtures = fixtures[:limit_fixtures]
    prompt_contract = plan.get("prompt_contract") if isinstance(plan.get("prompt_contract"), dict) else {}
    rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            continue
        fixture_root = Path(str(fixture.get("dataset_path", "")))
        if not fixture_root.is_absolute():
            fixture_root = REPO_ROOT / fixture_root
        source_path = fixture_root / str(fixture.get("source_file") or "source.md")
        question_path = fixture_root / str(fixture.get("question_file") or "qa_questions.jsonl")
        source = source_path.read_text(encoding="utf-8")
        questions = _load_questions(question_path)
        planned = int(fixture.get("planned_rows", len(questions)) or len(questions))
        if limit_rows > 0:
            planned = min(planned, limit_rows)
        for question in questions[:planned]:
            for run_index in range(1, max(1, runs_per_model) + 1):
                messages = build_messages(
                    source=source,
                    question=str(question.get("question", "")),
                    prompt_contract=prompt_contract,
                )
                rows.append(
                    {
                        "schema_version": "frontier_direct_qa_row_v1",
                        "fixture": fixture.get("fixture", ""),
                        "bucket": fixture.get("bucket", ""),
                        "question_id": question.get("id", ""),
                        "category": question.get("category", ""),
                        "run_index": run_index,
                        "provider": provider,
                        "model": model,
                        "source_file": str(source_path),
                        "question_file": str(question_path),
                        "question": question.get("question", ""),
                        "messages": messages if dry_run else [],
                        "answer": "",
                        "status": "dry_run" if dry_run else "pending",
                        "error": "",
                    }
                )
    return rows


def _answer_rows(
    rows: list[dict[str, Any]],
    *,
    base_url: str,
    api_key: str,
    timeout: int,
    max_tokens: int,
    workers: int,
) -> list[dict[str, Any]]:
    if workers <= 1:
        return [
            _answer_row(row, base_url=base_url, api_key=api_key, timeout=timeout, max_tokens=max_tokens)
            for row in rows
        ]
    answered: list[dict[str, Any] | None] = [None] * len(rows)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        future_map = {
            pool.submit(
                _answer_row,
                row,
                base_url=base_url,
                api_key=api_key,
                timeout=timeout,
                max_tokens=max_tokens,
            ): index
            for index, row in enumerate(rows)
        }
        for future in concurrent.futures.as_completed(future_map):
            answered[future_map[future]] = future.result()
    return [row for row in answered if isinstance(row, dict)]


def build_messages(*, source: str, question: str, prompt_contract: dict[str, Any]) -> list[dict[str, str]]:
    system = str(prompt_contract.get("system") or "").strip()
    template = str(prompt_contract.get("user_template") or "").strip()
    if not template:
        template = "SOURCE DOCUMENT:\n{source}\n\nQUESTION:\n{question}\n\nAnswer only from the source."
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": template.format(source=source, question=question)})
    return messages


def _answer_row(
    row: dict[str, Any],
    *,
    base_url: str,
    api_key: str,
    timeout: int,
    max_tokens: int,
) -> dict[str, Any]:
    source = Path(str(row.get("source_file", ""))).read_text(encoding="utf-8")
    messages = build_messages(
        source=source,
        question=str(row.get("question", "")),
        prompt_contract={
            "system": "Answer only from the provided source document. If the source does not support an answer, say what is unresolved or not stated.",
            "user_template": "SOURCE DOCUMENT:\n{source}\n\nQUESTION:\n{question}\n\nReturn a concise answer and cite the source evidence in plain language.",
        },
    )
    request = {
        "model": row.get("model", ""),
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    try:
        response = _post_chat(base_url=base_url, api_key=api_key, payload=request, timeout=timeout)
        answer = _extract_answer(response)
        return {**row, "answer": answer, "status": "ok", "error": "", "raw_response": response}
    except Exception as exc:
        return {**row, "answer": "", "status": "error", "error": str(exc), "raw_response": {}}


def _post_chat(*, base_url: str, api_key: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    endpoint = _chat_url(base_url)
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8", errors="replace"))
                if isinstance(data, dict) and data.get("error"):
                    raise RuntimeError(f"provider error: {json.dumps(data.get('error'), ensure_ascii=False)[:500]}")
                return data
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(1)
                continue
    raise RuntimeError(f"chat completion failed: {last_error}")


def _chat_url(base_url: str) -> str:
    stripped = str(base_url or "").rstrip("/")
    if stripped.endswith("/chat/completions"):
        return stripped
    if stripped.endswith("/v1"):
        return f"{stripped}/chat/completions"
    return f"{stripped}/v1/chat/completions"


def _extract_answer(response: dict[str, Any]) -> str:
    choices = response.get("choices") if isinstance(response.get("choices"), list) else []
    if not choices:
        return ""
    message = choices[0].get("message") if isinstance(choices[0], dict) else {}
    if isinstance(message, dict):
        return str(message.get("content") or "").strip()
    return ""


def _load_questions(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".jsonl":
        return [_normalize_question(json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, list):
            return [_normalize_question(item) for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            for key in ("questions", "items", "rows", "cases"):
                items = value.get(key)
                if isinstance(items, list):
                    return [_normalize_question(item) for item in items if isinstance(item, dict)]
    return _load_markdown_questions(path)


def _normalize_question(row: dict[str, Any]) -> dict[str, str]:
    qid = str(row.get("id") or row.get("source_id") or "").strip()
    question = str(row.get("question") or row.get("prompt") or row.get("utterance") or "").strip()
    return {"id": qid, "question": question, "category": str(row.get("category", "") or "").strip()}


def _load_markdown_questions(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(r"^(?:[-*]\s*)?(q\d{3})[:.)\-\s]+(.+)$", stripped, flags=re.IGNORECASE)
        if match:
            rows.append({"id": match.group(1).lower(), "question": match.group(2).strip(), "category": ""})
        elif stripped.startswith(("- ", "* ")):
            rows.append({"id": f"q{len(rows)+1:03d}", "question": stripped[2:].strip(), "category": ""})
    return rows


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-").lower() or "model"


if __name__ == "__main__":
    raise SystemExit(main())
