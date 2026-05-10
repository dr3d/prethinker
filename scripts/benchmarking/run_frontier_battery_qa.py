#!/usr/bin/env python3
"""Run one-source/full-question-battery QA for frontier models.

This lane is closer to Prethinker's compile-once test shape than direct row QA:
the model sees the source once, then answers the whole question battery in one
call. The output is expanded back into row-level JSONL so the common scorer can
be reused unchanged.
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
DEFAULT_PLAN = REPO_ROOT / "tmp" / "public_benchmark" / "axis2_probe" / "axis2_context_probe_plan.json"
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "public_benchmark" / "battery_outputs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-json", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--model", required=True)
    parser.add_argument("--provider", default="openai_compatible")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--runs-per-model", type=int, default=None)
    parser.add_argument("--fixture", action="append", default=[], help="Fixture name to include; may be repeated.")
    parser.add_argument("--limit-fixtures", type=int, default=0)
    parser.add_argument("--limit-questions", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan_path = _resolve(args.plan_json)
    plan = _read_json(plan_path)
    battery_jobs = build_battery_jobs(
        plan,
        model=str(args.model),
        provider=str(args.provider),
        runs_per_model=int(args.runs_per_model or plan.get("run_settings", {}).get("runs_per_model", 1)),
        fixture_names=set(str(item) for item in args.fixture),
        limit_fixtures=int(args.limit_fixtures),
        limit_questions=int(args.limit_questions),
        dry_run=bool(args.dry_run),
    )
    if not args.dry_run:
        api_key = str(args.api_key or os.environ.get(str(args.api_key_env), "") or "").strip()
        battery_jobs = answer_battery_jobs(
            battery_jobs,
            base_url=str(args.base_url),
            api_key=api_key,
            timeout=int(args.timeout),
            max_tokens=int(args.max_tokens),
            workers=int(args.workers),
        )
    rows = expand_jobs_to_rows(battery_jobs)
    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(args.model))
    out_jsonl = out_dir / f"frontier_battery_qa_{slug}.jsonl"
    out_json = out_dir / f"frontier_battery_qa_{slug}.json"
    out_jsonl.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    payload = {
        "schema_version": "frontier_battery_qa_run_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "plan_json": str(plan_path),
        "model": str(args.model),
        "provider": str(args.provider),
        "dry_run": bool(args.dry_run),
        "battery_call_count": len(battery_jobs),
        "row_count": len(rows),
        "jobs": battery_jobs,
        "rows": rows,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"battery_calls": len(battery_jobs), "rows": len(rows), "json": str(out_json), "jsonl": str(out_jsonl)}, indent=2))
    return 0


def build_battery_jobs(
    plan: dict[str, Any],
    *,
    model: str,
    provider: str,
    runs_per_model: int,
    fixture_names: set[str],
    limit_fixtures: int,
    limit_questions: int,
    dry_run: bool,
) -> list[dict[str, Any]]:
    fixtures = plan.get("fixtures") if isinstance(plan.get("fixtures"), list) else []
    if fixture_names:
        fixtures = [fixture for fixture in fixtures if str(fixture.get("fixture", "")) in fixture_names]
    if limit_fixtures > 0:
        fixtures = fixtures[:limit_fixtures]
    jobs: list[dict[str, Any]] = []
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
        if limit_questions > 0:
            planned = min(planned, limit_questions)
        questions = questions[:planned]
        for run_index in range(1, max(1, runs_per_model) + 1):
            messages = build_battery_messages(source=source, questions=questions)
            jobs.append(
                {
                    "schema_version": "frontier_battery_qa_job_v1",
                    "fixture": fixture.get("fixture", ""),
                    "bucket": fixture.get("bucket", ""),
                    "run_index": run_index,
                    "provider": provider,
                    "model": model,
                    "source_file": str(source_path),
                    "question_file": str(question_path),
                    "questions": questions,
                    "messages": messages if dry_run else [],
                    "answers": {},
                    "status": "dry_run" if dry_run else "pending",
                    "error": "",
                }
            )
    return jobs


def build_battery_messages(*, source: str, questions: list[dict[str, str]]) -> list[dict[str, str]]:
    question_lines = "\n".join(f"- {item['id']}: {item['question']}" for item in questions)
    user = (
        "SOURCE DOCUMENT:\n"
        f"{source}\n\n"
        "QUESTION BATTERY:\n"
        f"{question_lines}\n\n"
        "Answer every question using only the source document. Return JSON only with this shape:\n"
        '{"answers":[{"question_id":"q001","answer":"concise answer with source evidence in plain language"}]}\n'
        "Use each provided question_id exactly once. Do not include oracle/reference answers."
    )
    return [
        {
            "role": "system",
            "content": "Answer only from the provided source document. If unsupported, say what is unresolved or not stated. Return JSON only.",
        },
        {"role": "user", "content": user},
    ]


def answer_battery_jobs(
    jobs: list[dict[str, Any]],
    *,
    base_url: str,
    api_key: str,
    timeout: int,
    max_tokens: int,
    workers: int,
) -> list[dict[str, Any]]:
    if workers <= 1:
        return [_answer_job(job, base_url=base_url, api_key=api_key, timeout=timeout, max_tokens=max_tokens) for job in jobs]
    answered: list[dict[str, Any] | None] = [None] * len(jobs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        future_map = {
            pool.submit(_answer_job, job, base_url=base_url, api_key=api_key, timeout=timeout, max_tokens=max_tokens): index
            for index, job in enumerate(jobs)
        }
        for future in concurrent.futures.as_completed(future_map):
            answered[future_map[future]] = future.result()
    return [job for job in answered if isinstance(job, dict)]


def expand_jobs_to_rows(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for job in jobs:
        answers = job.get("answers") if isinstance(job.get("answers"), dict) else {}
        for question in job.get("questions", []):
            qid = str(question.get("id", ""))
            answer = str(answers.get(qid, "") or "").strip()
            rows.append(
                {
                    "schema_version": "frontier_battery_qa_row_v1",
                    "fixture": job.get("fixture", ""),
                    "bucket": job.get("bucket", ""),
                    "question_id": qid,
                    "category": question.get("category", ""),
                    "run_index": job.get("run_index", 0),
                    "provider": job.get("provider", ""),
                    "model": job.get("model", ""),
                    "source_file": job.get("source_file", ""),
                    "question_file": job.get("question_file", ""),
                    "question": question.get("question", ""),
                    "answer": answer,
                    "status": "ok" if answer and job.get("status") == "ok" else str(job.get("status", "")),
                    "error": "" if answer else str(job.get("error", "") or "missing answer for question_id"),
                    "battery_call_status": job.get("status", ""),
                    "raw_response": job.get("raw_response", {}),
                }
            )
    return rows


def _answer_job(
    job: dict[str, Any],
    *,
    base_url: str,
    api_key: str,
    timeout: int,
    max_tokens: int,
) -> dict[str, Any]:
    source = Path(str(job.get("source_file", ""))).read_text(encoding="utf-8")
    messages = build_battery_messages(source=source, questions=job.get("questions", []))
    request = {
        "model": job.get("model", ""),
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    try:
        response = _post_chat(base_url=base_url, api_key=api_key, payload=request, timeout=timeout)
        content = _extract_answer(response)
        answers = _parse_answers(content)
        missing = [item["id"] for item in job.get("questions", []) if item["id"] not in answers]
        status = "ok" if not missing else "partial"
        error = "" if not missing else f"missing answers for: {', '.join(missing)}"
        return {**job, "answers": answers, "status": status, "error": error, "raw_text": content, "raw_response": response}
    except Exception as exc:
        return {**job, "answers": {}, "status": "error", "error": str(exc), "raw_text": "", "raw_response": {}}


def _parse_answers(content: str) -> dict[str, str]:
    text = _strip_code_fence(content)
    data = json.loads(text)
    items = data.get("answers") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("answer JSON did not contain an answers list")
    answers: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        qid = str(item.get("question_id") or item.get("id") or "").strip()
        answer = str(item.get("answer") or "").strip()
        if qid and answer:
            answers[qid] = answer
    return answers


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else stripped


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
    return [_normalize_question(json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _normalize_question(row: dict[str, Any]) -> dict[str, str]:
    return {
        "id": str(row.get("id") or row.get("source_id") or "").strip(),
        "question": str(row.get("question") or row.get("prompt") or "").strip(),
        "category": str(row.get("category", "") or "").strip(),
    }


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-").lower() or "model"


if __name__ == "__main__":
    raise SystemExit(main())
