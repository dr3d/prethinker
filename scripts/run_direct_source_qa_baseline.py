#!/usr/bin/env python3
"""Run a no-Prethinker direct-source QA baseline.

This control answers each QA prompt directly from source.md, without compiling
the document into a KB or using query surfaces. The oracle is used only after the
answer is produced, by a separate structured judge.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURES_ROOT = REPO_ROOT / "datasets" / "real_world_transfer" / "fresh_ugly_public_20260524_01"
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "direct_source_qa_baseline"
DEFAULT_CACHE_DIR = REPO_ROOT / "tmp" / "direct_source_qa_baseline_cache"
CACHE_SCHEMA_VERSION = "direct_source_qa_baseline_cache_v1"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_domain_bootstrap_qa import (  # noqa: E402
    QA_JUDGE_SCHEMA,
    SemanticIRCallConfig,
    _configure_openrouter_title,
    call_lmstudio_json_schema,
    hash_text,
    load_oracle,
    parse_numbered_markdown_questions,
)


DIRECT_SOURCE_ANSWER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "answer", "support", "uncertainty"],
    "properties": {
        "schema_version": {"type": "string", "const": "direct_source_answer_v1"},
        "answer": {"type": "string", "maxLength": 1200},
        "support": {"type": "string", "maxLength": 1200},
        "uncertainty": {"type": "string", "maxLength": 500},
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run direct source.md QA baseline without Prethinker compilation.")
    parser.add_argument("--fixtures-root", type=Path, default=DEFAULT_FIXTURES_ROOT)
    parser.add_argument("--fixture", action="append", default=[], help="Fixture directory name to include.")
    parser.add_argument("--only-ids", default="", help="Comma-separated QA ids to run within each selected fixture.")
    parser.add_argument("--limit", type=int, default=0, help="Optional total row limit after fixture/id filtering.")
    parser.add_argument("--lanes", type=int, default=6, help="Concurrent OpenAI-compatible calls.")
    parser.add_argument("--backend", choices=["lmstudio"], default="lmstudio")
    parser.add_argument("--model", default=os.environ.get("PRETHINKER_MODEL", "qwen/qwen3.6-35b-a3b"))
    parser.add_argument("--base-url", default=os.environ.get("PRETHINKER_BASE_URL", "http://127.0.0.1:1234"))
    parser.add_argument(
        "--api-key",
        default="",
        help="Optional OpenAI-compatible API key. Local LM Studio does not require one.",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--include-model-input", action="store_true")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=32768)
    parser.add_argument("--max-answer-tokens", type=int, default=900)
    parser.add_argument("--max-judge-tokens", type=int, default=900)
    return parser.parse_args()


def load_env_local(path: Path = REPO_ROOT / ".env.local") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and value and key not in os.environ:
            os.environ[key] = value


def selected_fixture_dirs(root: Path, fixture_names: list[str]) -> list[Path]:
    resolved = root if root.is_absolute() else (REPO_ROOT / root).resolve()
    if fixture_names:
        return [resolved / name for name in fixture_names]
    return sorted(
        path
        for path in resolved.iterdir()
        if path.is_dir() and (path / "source.md").exists() and (path / "qa.md").exists() and (path / "oracle.jsonl").exists()
    )


def load_jobs(fixtures_root: Path, fixture_names: list[str], only_ids: set[str], limit: int) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for fixture_dir in selected_fixture_dirs(fixtures_root, fixture_names):
        qa_path = fixture_dir / "qa.md"
        source_path = fixture_dir / "source.md"
        oracle_path = fixture_dir / "oracle.jsonl"
        source_text = source_path.read_text(encoding="utf-8-sig")
        oracle = load_oracle(oracle_path)
        for question in parse_numbered_markdown_questions(qa_path.read_text(encoding="utf-8-sig")):
            qid = str(question.get("id", "")).strip()
            if only_ids and qid not in only_ids:
                continue
            jobs.append(
                {
                    "fixture": fixture_dir.name,
                    "fixture_dir": str(fixture_dir),
                    "source_path": str(source_path),
                    "qa_path": str(qa_path),
                    "oracle_path": str(oracle_path),
                    "source_hash": hash_text(source_text),
                    "source_text": source_text,
                    "id": qid,
                    "number": int(question.get("number", 0) or 0),
                    "phase": str(question.get("phase", "") or ""),
                    "utterance": str(question.get("utterance", "") or ""),
                    "reference_answer": str((oracle.get(qid, {}) or {}).get("reference_answer", "") or "").strip(),
                }
            )
    jobs.sort(key=lambda item: (str(item["fixture"]), int(item["number"])))
    if limit > 0:
        return jobs[:limit]
    return jobs


def cache_key_for_job(job: dict[str, Any], *, model: str, base_url: str, answer_prompt_version: str, judge_prompt_version: str) -> str:
    payload = {
        "schema": CACHE_SCHEMA_VERSION,
        "fixture": job.get("fixture", ""),
        "source_hash": job.get("source_hash", ""),
        "id": job.get("id", ""),
        "utterance": job.get("utterance", ""),
        "reference_answer": job.get("reference_answer", ""),
        "model": model,
        "base_url": base_url,
        "answer_prompt_version": answer_prompt_version,
        "judge_prompt_version": judge_prompt_version,
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def read_cache(cache_dir: Path, key: str) -> dict[str, Any] | None:
    path = cache_dir / f"{key}.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(payload, dict) and payload.get("schema_version") == CACHE_SCHEMA_VERSION:
        row = payload.get("row")
        if isinstance(row, dict):
            return row
    return None


def write_cache(cache_dir: Path, key: str, row: dict[str, Any]) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "cache_key": key,
        "cached_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "row": row,
    }
    (cache_dir / f"{key}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def answer_directly_from_source(*, job: dict[str, Any], config: SemanticIRCallConfig, max_tokens: int) -> dict[str, Any]:
    payload = {
        "task": "Answer one question using only the provided source document.",
        "source_document": job["source_text"],
        "question_id": job["id"],
        "question": job["utterance"],
        "answer_policy": [
            "Use only the source_document. Do not use outside knowledge.",
            "Give the shortest answer that fully answers the question.",
            "Preserve identifiers, dates, names, amounts, redaction labels, and source-stated uncertainty exactly when relevant.",
            "If the source document does not state the answer, say that it is not stated.",
            "The support field should name or quote the compact source phrase that justifies the answer.",
        ],
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You are a direct document QA baseline. Return direct_source_answer_v1 JSON only. "
                "Do not compile, infer a KB, or use outside knowledge."
            ),
        },
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]
    return call_lmstudio_json_schema(
        config=config,
        messages=messages,
        schema_name="direct_source_answer_v1",
        schema=DIRECT_SOURCE_ANSWER_SCHEMA,
        max_tokens=max_tokens,
    )


def judge_direct_answer(*, job: dict[str, Any], answer: dict[str, Any], config: SemanticIRCallConfig, max_tokens: int) -> dict[str, Any]:
    reference = str(job.get("reference_answer", "") or "").strip()
    if not reference:
        return {
            "schema_version": "qa_judge_v1",
            "verdict": "not_judged",
            "answer_supported": False,
            "concise_answer": "",
            "issues": ["no reference answer supplied"],
        }
    payload = {
        "task": "Compare a direct source-model answer with a human reference answer.",
        "authority": "You are a scorer only. Judge semantic equivalence to the reference answer; do not use outside knowledge.",
        "question_id": job.get("id", ""),
        "question": job.get("utterance", ""),
        "reference_answer": reference,
        "model_answer": answer.get("answer", ""),
        "model_support": answer.get("support", ""),
        "model_uncertainty": answer.get("uncertainty", ""),
        "verdict_policy": [
            "exact: the model answer contains all material information in the reference answer, allowing harmless formatting or wording differences.",
            "partial: the model answer is relevant but omits material reference content, is too broad, or mixes correct content with unresolved noise.",
            "miss: the model answer is wrong, unsupported by the reference, contradicts the reference, or says not stated when the reference gives an answer.",
            "not_judged: malformed/no reference or model answer.",
            "For identifiers, dates, amounts, names, status labels, and counts, require the same material value even if punctuation/case differs harmlessly.",
            "Do not reward outside facts. The answer is judged only against the supplied reference answer.",
        ],
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict QA judge for a no-Prethinker direct-source baseline. "
                "Return qa_judge_v1 JSON only, with no chain-of-thought."
            ),
        },
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]
    return call_lmstudio_json_schema(
        config=config,
        messages=messages,
        schema_name="qa_judge_v1",
        schema=QA_JUDGE_SCHEMA,
        max_tokens=max_tokens,
    )


def run_job(
    job: dict[str, Any],
    *,
    config: SemanticIRCallConfig,
    cache_dir: Path,
    cache_enabled: bool,
    include_model_input: bool,
    max_answer_tokens: int,
    max_judge_tokens: int,
    answer_prompt_version: str,
    judge_prompt_version: str,
) -> dict[str, Any]:
    key = cache_key_for_job(
        job,
        model=config.model,
        base_url=config.base_url,
        answer_prompt_version=answer_prompt_version,
        judge_prompt_version=judge_prompt_version,
    )
    cached = read_cache(cache_dir, key) if cache_enabled else None
    if cached is not None:
        cached["cache_hit"] = True
        cached["cache_key"] = key
        return cached

    row: dict[str, Any] = {
        "fixture": job["fixture"],
        "id": job["id"],
        "number": job["number"],
        "phase": job["phase"],
        "utterance": job["utterance"],
        "reference_answer": job["reference_answer"],
        "source_path": job["source_path"],
        "ok": False,
        "error": "",
        "direct_answer": {},
        "reference_judge": {},
        "cache_hit": False,
        "cache_key": key,
    }
    started = time.perf_counter()
    if include_model_input:
        row["model_input"] = {
            "source_hash": job["source_hash"],
            "question": job["utterance"],
        }
    try:
        answer = answer_directly_from_source(job=job, config=config, max_tokens=max_answer_tokens)
        row["direct_answer"] = answer
        row["reference_judge"] = judge_direct_answer(
            job=job,
            answer=answer,
            config=config,
            max_tokens=max_judge_tokens,
        )
        row["ok"] = True
    except Exception as exc:
        row["error"] = str(exc)[:1200]
    row["elapsed_ms"] = int((time.perf_counter() - started) * 1000)
    if cache_enabled and row["ok"]:
        write_cache(cache_dir, key, row)
    return row


def summarize(rows: list[dict[str, Any]], *, elapsed_ms: int) -> dict[str, Any]:
    verdicts = Counter(str((row.get("reference_judge") or {}).get("verdict", "not_judged") or "not_judged") for row in rows)
    by_fixture: dict[str, dict[str, int]] = {}
    for row in rows:
        fixture = str(row.get("fixture", "") or "unknown")
        bucket = by_fixture.setdefault(fixture, {"question_count": 0, "exact": 0, "partial": 0, "miss": 0, "not_judged": 0, "errors": 0})
        bucket["question_count"] += 1
        verdict = str((row.get("reference_judge") or {}).get("verdict", "not_judged") or "not_judged")
        bucket[verdict if verdict in {"exact", "partial", "miss", "not_judged"} else "not_judged"] += 1
        if row.get("error"):
            bucket["errors"] += 1
    total = max(1, len(rows))
    return {
        "question_count": len(rows),
        "ok_rows": sum(1 for row in rows if row.get("ok")),
        "error_rows": sum(1 for row in rows if row.get("error")),
        "judge_exact": int(verdicts.get("exact", 0)),
        "judge_partial": int(verdicts.get("partial", 0)),
        "judge_miss": int(verdicts.get("miss", 0)),
        "judge_not_judged": int(verdicts.get("not_judged", 0)),
        "exact_rate": round(float(verdicts.get("exact", 0)) / total, 4),
        "by_fixture": dict(sorted(by_fixture.items())),
        "elapsed_ms": elapsed_ms,
    }


def write_summary(record: dict[str, Any], path: Path) -> None:
    summary = record["summary"]
    lines = [
        "# Direct Source QA Baseline",
        "",
        "No-Prethinker control: each question is answered directly from `source.md`; `oracle.jsonl` is used only by the after-the-fact judge.",
        "",
        f"- Fixtures root: `{record.get('fixtures_root', '')}`",
        f"- Model: `{record.get('model', '')}`",
        f"- Base URL: `{record.get('base_url', '')}`",
        f"- Questions: `{summary.get('question_count', 0)}`",
        f"- OK/error rows: `{summary.get('ok_rows', 0)}` / `{summary.get('error_rows', 0)}`",
        f"- Reference judge: exact=`{summary.get('judge_exact', 0)}` partial=`{summary.get('judge_partial', 0)}` miss=`{summary.get('judge_miss', 0)}` not_judged=`{summary.get('judge_not_judged', 0)}`",
        f"- Exact rate: `{summary.get('exact_rate', 0.0):.2%}`",
        f"- Cache: enabled=`{record.get('cache', {}).get('enabled', False)}` hits=`{record.get('cache', {}).get('hits', 0)}` misses=`{record.get('cache', {}).get('misses', 0)}`",
        "",
        "## By Fixture",
        "",
        "| Fixture | Exact | Partial | Miss | Not judged | Errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for fixture, item in summary.get("by_fixture", {}).items():
        lines.append(
            f"| `{fixture}` | {item.get('exact', 0)} | {item.get('partial', 0)} | {item.get('miss', 0)} | {item.get('not_judged', 0)} | {item.get('errors', 0)} |"
        )
    lines.extend(["", "## Rows", ""])
    for row in record["rows"]:
        judge = row.get("reference_judge") or {}
        answer = row.get("direct_answer") or {}
        lines.extend(
            [
                f"### {row.get('fixture', '')} {row.get('id', '')}",
                "",
                f"- Question: {row.get('utterance', '')}",
                f"- Reference answer: {row.get('reference_answer', '') or '-'}",
                f"- Direct answer: {answer.get('answer', '') or '-'}",
                f"- Support: {answer.get('support', '') or '-'}",
                f"- Judge: `{judge.get('verdict', 'not_judged')}`",
                f"- Judge note: {judge.get('concise_answer', '') or '-'}",
            ]
        )
        if row.get("error"):
            lines.append(f"- Error: `{row.get('error', '')}`")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", str(value or "").strip()).strip("-").lower()[:80] or "run"


def main() -> int:
    args = parse_args()
    load_env_local()
    if str(args.api_key or "").strip():
        os.environ["PRETHINKER_API_KEY"] = str(args.api_key).strip()
    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    cache_dir = args.cache_dir if args.cache_dir.is_absolute() else (REPO_ROOT / args.cache_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    _configure_openrouter_title(out_dir)

    only_ids = {item.strip() for item in str(args.only_ids or "").split(",") if item.strip()}
    jobs = load_jobs(args.fixtures_root, [str(item) for item in args.fixture], only_ids, int(args.limit or 0))
    if not jobs:
        raise SystemExit("no jobs selected")

    config = SemanticIRCallConfig(
        backend=str(args.backend),
        base_url=str(args.base_url),
        model=str(args.model),
        context_length=int(args.num_ctx),
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        top_k=int(args.top_k),
        max_tokens=max(int(args.max_answer_tokens), int(args.max_judge_tokens)),
        think_enabled=False,
        reasoning_effort="none",
        api_key=str(args.api_key or ""),
    )
    answer_prompt_version = "direct_source_answer_prompt_v1"
    judge_prompt_version = "direct_source_judge_prompt_v1"
    cache_enabled = not bool(args.no_cache)
    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, int(args.lanes or 1))) as pool:
        futures = [
            pool.submit(
                run_job,
                job,
                config=config,
                cache_dir=cache_dir,
                cache_enabled=cache_enabled,
                include_model_input=bool(args.include_model_input),
                max_answer_tokens=int(args.max_answer_tokens),
                max_judge_tokens=int(args.max_judge_tokens),
                answer_prompt_version=answer_prompt_version,
                judge_prompt_version=judge_prompt_version,
            )
            for job in jobs
        ]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            row = future.result()
            rows.append(row)
            verdict = (row.get("reference_judge") or {}).get("verdict", "not_judged")
            print(f"[{index}/{len(jobs)}] {row.get('fixture')} {row.get('id')} {verdict}")
    rows.sort(key=lambda item: (str(item.get("fixture", "")), int(item.get("number", 0) or 0)))
    summary = summarize(rows, elapsed_ms=int((time.perf_counter() - started) * 1000))
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "schema_version": "direct_source_qa_baseline_run_v1",
        "fixtures_root": str((args.fixtures_root if args.fixtures_root.is_absolute() else (REPO_ROOT / args.fixtures_root).resolve())),
        "model": str(args.model),
        "base_url": str(args.base_url),
        "lanes": int(args.lanes),
        "answer_prompt_version": answer_prompt_version,
        "judge_prompt_version": judge_prompt_version,
        "cache": {
            "enabled": cache_enabled,
            "schema_version": CACHE_SCHEMA_VERSION,
            "dir": str(cache_dir),
            "hits": sum(1 for row in rows if row.get("cache_hit")),
            "misses": sum(1 for row in rows if not row.get("cache_hit")),
        },
        "summary": summary,
        "rows": rows,
    }
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(str(args.model))}"
    json_path = out_dir / f"direct_source_qa_baseline_{slug}.json"
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    write_summary(record, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
