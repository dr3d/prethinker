#!/usr/bin/env python3
"""
Run live random Hacker News ingestion experiments through kb_pipeline.

Goals:
1) sample real HN threads (random from a feed window)
2) build bounded turnsets/scenarios from OP + comments
3) execute pipeline runs with repeatable settings
4) publish per-thread + aggregate telemetry artifacts
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import random
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "kb_pipeline.py"


def _utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")


def _slug(text: str, *, max_len: int = 80) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or ""))
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    cleaned = cleaned.strip("_") or "thread"
    return cleaned[:max_len].strip("_") or "thread"


def _clip_text(text: str, limit: int) -> str:
    if limit <= 0:
        return text
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _sanitize_hn_html(raw: str) -> str:
    text = str(raw or "")
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", text)
    text = re.sub(r"(?i)<\s*/\s*p\s*>", "\n\n", text)
    text = re.sub(r"(?i)<\s*p[^>]*>", "", text)
    text = re.sub(r"(?i)<\s*li[^>]*>", "- ", text)
    text = re.sub(r"(?i)<\s*/\s*li\s*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _http_json(url: str, timeout_seconds: int) -> Any:
    req = urllib.request.Request(
        url=url,
        headers={
            "Accept": "application/json",
            "User-Agent": "prethinker-hn-random-ingest/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=max(5, int(timeout_seconds))) as resp:
        payload = resp.read().decode("utf-8", errors="replace")
    return json.loads(payload)


def _fetch_feed_ids(*, api_base: str, feed: str, timeout_seconds: int) -> list[int]:
    url = f"{api_base.rstrip('/')}/{feed}stories.json"
    payload = _http_json(url, timeout_seconds)
    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected feed payload type from {url}: {type(payload).__name__}")
    out: list[int] = []
    for row in payload:
        try:
            out.append(int(row))
        except (TypeError, ValueError):
            continue
    return out


def _fetch_item(*, api_base: str, item_id: int, timeout_seconds: int) -> dict[str, Any] | None:
    url = f"{api_base.rstrip('/')}/item/{int(item_id)}.json"
    try:
        payload = _http_json(url, timeout_seconds)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None
    if isinstance(payload, dict):
        return payload
    return None


@dataclass
class HNComment:
    item_id: int
    by: str
    unix_time: int
    depth: int
    parent: int
    text: str


@dataclass
class HNThread:
    thread_id: int
    title: str
    by: str
    unix_time: int
    score: int
    descendants: int
    hn_url: str
    source_url: str
    op_text: str
    comments: list[HNComment]


def _collect_comments_bfs(
    *,
    api_base: str,
    root_item: dict[str, Any],
    max_comments: int,
    max_depth: int,
    timeout_seconds: int,
    max_comment_chars: int,
) -> list[HNComment]:
    kids = root_item.get("kids")
    if not isinstance(kids, list):
        return []

    queue: deque[tuple[int, int, int]] = deque()
    root_id = int(root_item.get("id") or 0)
    for kid in kids:
        try:
            queue.append((int(kid), 1, root_id))
        except (TypeError, ValueError):
            continue

    out: list[HNComment] = []
    seen: set[int] = set()
    while queue and len(out) < max(0, int(max_comments)):
        item_id, depth, parent = queue.popleft()
        if item_id in seen:
            continue
        seen.add(item_id)
        if depth > max(1, int(max_depth)):
            continue

        row = _fetch_item(api_base=api_base, item_id=item_id, timeout_seconds=timeout_seconds)
        if not isinstance(row, dict):
            continue
        if row.get("deleted") or row.get("dead"):
            continue
        if str(row.get("type", "")).strip().lower() != "comment":
            continue

        raw_text = _sanitize_hn_html(str(row.get("text", "")))
        if not raw_text:
            continue
        comment = HNComment(
            item_id=item_id,
            by=str(row.get("by") or "unknown").strip() or "unknown",
            unix_time=int(row.get("time") or 0),
            depth=depth,
            parent=int(row.get("parent") or parent),
            text=_clip_text(raw_text, max(0, int(max_comment_chars))),
        )
        out.append(comment)

        if depth < max(1, int(max_depth)):
            child_kids = row.get("kids")
            if isinstance(child_kids, list):
                for child in child_kids:
                    try:
                        queue.append((int(child), depth + 1, item_id))
                    except (TypeError, ValueError):
                        continue

    return out


def _build_turnset(thread: HNThread, *, max_op_chars: int) -> dict[str, Any]:
    utterances: list[dict[str, Any]] = []

    utterances.append(
        {
            "utterance": f"OP (title): {thread.title}",
            "source": "op",
            "source_id": thread.thread_id,
        }
    )
    if thread.source_url:
        utterances.append(
            {
                "utterance": f"Linked article URL: {thread.source_url}",
                "source": "op",
                "source_id": thread.thread_id,
            }
        )
    if thread.op_text:
        utterances.append(
            {
                "utterance": f"OP (text): {_clip_text(thread.op_text, max(0, int(max_op_chars)))}",
                "source": "op",
                "source_id": thread.thread_id,
            }
        )

    for comment in thread.comments:
        utterances.append(
            {
                "utterance": f"{comment.by}: {comment.text}",
                "source": "comment",
                "source_id": comment.item_id,
                "depth": comment.depth,
            }
        )

    label = f"hn_random_{thread.thread_id}_{_slug(thread.title, max_len=40)}"
    return {
        "name": f"{label}_turnset_v1",
        "source_thread_id": thread.thread_id,
        "source_url": thread.hn_url,
        "difficulty": "G3",
        "lane": "hn_random_live",
        "utterances": utterances,
        "notes": "Auto-generated random OP+comment turnset from live Hacker News feed.",
    }


def _build_scenario(thread: HNThread, turnset: dict[str, Any]) -> dict[str, Any]:
    scenario_name = f"hn_random_live_{thread.thread_id}_{_slug(thread.title, max_len=40)}"
    utterances: list[str] = []
    for row in turnset.get("utterances", []):
        if not isinstance(row, dict):
            continue
        text = str(row.get("utterance") or "").strip()
        if text:
            utterances.append(text)
    return {
        "name": scenario_name,
        "ontology_name": scenario_name,
        "utterances": utterances,
        "validations": [],
        "meta": {
            "source_thread_id": thread.thread_id,
            "source_url": thread.hn_url,
            "source_article_url": thread.source_url,
            "sample_lane": "hn_random_live",
        },
    }


def _run_pipeline_for_scenario(
    *,
    scenario_path: Path,
    report_path: Path,
    backend: str,
    base_url: str,
    model: str,
    runtime: str,
    kb_root: str,
    prompt_file: str,
    context_length: int,
    timeout_seconds: int,
    clarification_eagerness: float,
    max_clarification_rounds: int,
    ce_mode: str,
    clarification_answer_model: str,
    clarification_answer_backend: str,
    clarification_answer_base_url: str,
    clarification_answer_context_length: int,
    clarification_answer_min_confidence: float,
    write_corpus_on_fail: bool,
) -> int:
    cmd = [
        sys.executable,
        str(PIPELINE),
        "--scenario",
        str(scenario_path),
        "--backend",
        backend,
        "--base-url",
        base_url,
        "--model",
        model,
        "--runtime",
        runtime,
        "--kb-root",
        kb_root,
        "--context-length",
        str(max(256, int(context_length))),
        "--timeout-seconds",
        str(max(30, int(timeout_seconds))),
        "--clarification-eagerness",
        f"{float(clarification_eagerness):.4f}",
        "--max-clarification-rounds",
        str(max(0, int(max_clarification_rounds))),
        "--out",
        str(report_path),
    ]
    if prompt_file:
        cmd.extend(["--prompt-file", prompt_file])
    if write_corpus_on_fail:
        cmd.append("--write-corpus-on-fail")

    mode = str(ce_mode).strip().lower()
    if mode == "same":
        cmd.extend(
            [
                "--clarification-answer-model",
                model,
                "--clarification-answer-backend",
                backend,
                "--clarification-answer-base-url",
                base_url,
                "--clarification-answer-context-length",
                str(max(256, int(clarification_answer_context_length))),
                "--clarification-answer-min-confidence",
                f"{float(clarification_answer_min_confidence):.4f}",
            ]
        )
    elif mode == "explicit":
        model_id = str(clarification_answer_model).strip()
        if not model_id:
            raise ValueError("ce_mode=explicit requires --clarification-answer-model.")
        ce_backend = str(clarification_answer_backend).strip() or backend
        ce_base_url = str(clarification_answer_base_url).strip() or base_url
        cmd.extend(
            [
                "--clarification-answer-model",
                model_id,
                "--clarification-answer-backend",
                ce_backend,
                "--clarification-answer-base-url",
                ce_base_url,
                "--clarification-answer-context-length",
                str(max(256, int(clarification_answer_context_length))),
                "--clarification-answer-min-confidence",
                f"{float(clarification_answer_min_confidence):.4f}",
            ]
        )

    print("")
    print(f"==> running scenario: {scenario_path.stem}")
    print("    command:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
    return int(proc.returncode)


def _read_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _record_from_report(
    *,
    thread: HNThread,
    scenario_name: str,
    report_path: Path,
    exit_code: int,
) -> dict[str, Any]:
    if not report_path.exists():
        return {
            "thread_id": thread.thread_id,
            "title": thread.title,
            "scenario": scenario_name,
            "status": "missing_report",
            "exit_code": int(exit_code),
            "report_path": str(report_path),
        }

    report = _read_report(report_path)
    turns_total = int(report.get("turns_total", 0) or 0)
    commits = int((report.get("decision_state_counts") or {}).get("commit", 0) or 0)
    apply_failures = int(report.get("turn_apply_failures", 0) or 0)
    parse_failures = int(report.get("turn_parse_failures", 0) or 0)
    clar_requests = int(report.get("turns_clarification_requested", 0) or 0)
    clar_rounds = int(report.get("clarification_rounds_total", 0) or 0)
    clar_answers = int(report.get("clarification_proxy_answers_total", 0) or 0) + int(
        report.get("clarification_served_llm_answers_total", 0) or 0
    )
    return {
        "thread_id": thread.thread_id,
        "title": thread.title,
        "hn_url": thread.hn_url,
        "source_url": thread.source_url,
        "scenario": scenario_name,
        "overall_status": str(report.get("overall_status", "failed")),
        "turns_total": turns_total,
        "turn_parse_failures": parse_failures,
        "turn_apply_failures": apply_failures,
        "clarification_requests": clar_requests,
        "clarification_rounds_total": clar_rounds,
        "clarification_answers_used_total": clar_answers,
        "decision_state_counts": report.get("decision_state_counts", {}),
        "commit_turn_rate": round((commits / turns_total) if turns_total else 0.0, 4),
        "apply_failure_rate": round((apply_failures / turns_total) if turns_total else 0.0, 4),
        "exit_code": int(exit_code),
        "report_path": str(report_path),
        "kb_path": str((report.get("corpus_write") or {}).get("path", "")),
    }


def _write_markdown_summary(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# HN Random Ingest Summary")
    lines.append("")
    lines.append(f"- generated_at_utc: `{payload.get('generated_at_utc', '')}`")
    lines.append(f"- run_dir: `{payload.get('run_dir', '')}`")
    lines.append(f"- stories_requested: `{payload.get('stories_requested', 0)}`")
    lines.append(f"- stories_selected: `{payload.get('stories_selected', 0)}`")
    lines.append(f"- runs_passed: `{payload.get('runs_passed', 0)}/{payload.get('runs_total', 0)}`")
    totals = payload.get("totals", {})
    if isinstance(totals, dict):
        lines.append(f"- turns_total: `{totals.get('turns_total', 0)}`")
        lines.append(f"- apply_failures_total: `{totals.get('apply_failures_total', 0)}`")
        lines.append(f"- clarification_requests_total: `{totals.get('clarification_requests_total', 0)}`")
        lines.append(f"- clarification_answers_total: `{totals.get('clarification_answers_total', 0)}`")
        lines.append(f"- commit_turn_rate_avg: `{totals.get('commit_turn_rate_avg', 0.0)}`")
    lines.append("")
    lines.append("## Per Thread")
    lines.append("")
    lines.append("| thread_id | status | turns | apply_fail | clar_req | commit_rate | title |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | --- |")
    records = payload.get("records", [])
    if isinstance(records, list):
        for row in records:
            if not isinstance(row, dict):
                continue
            lines.append(
                "| {thread_id} | {status} | {turns} | {apply_fail} | {clar_req} | {commit_rate} | {title} |".format(
                    thread_id=row.get("thread_id", ""),
                    status=row.get("overall_status", row.get("status", "")),
                    turns=row.get("turns_total", 0),
                    apply_fail=row.get("turn_apply_failures", 0),
                    clar_req=row.get("clarification_requests", 0),
                    commit_rate=row.get("commit_turn_rate", 0.0),
                    title=str(row.get("title", "")).replace("|", " "),
                )
            )
    lines.append("")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run random live Hacker News ingestion experiments.")
    parser.add_argument("--feed", choices=["top", "new", "best"], default="top")
    parser.add_argument("--sample-size", type=int, default=2)
    parser.add_argument("--seed", type=int, default=54)
    parser.add_argument("--max-candidates", type=int, default=250)
    parser.add_argument("--min-comments", type=int, default=6)
    parser.add_argument("--max-comments", type=int, default=12)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--max-comment-chars", type=int, default=700)
    parser.add_argument("--max-op-chars", type=int, default=1600)
    parser.add_argument("--hn-api-base", default="https://hacker-news.firebaseio.com/v0")
    parser.add_argument("--hn-timeout-seconds", type=int, default=20)

    parser.add_argument("--backend", default="ollama")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument(
        "--model",
        default="qwen3.5:9b",
        help="Parser model id. Default uses bare qwen3.5:9b with runtime prompt file.",
    )
    parser.add_argument("--runtime", default="core")
    parser.add_argument("--prompt-file", default="modelfiles/semantic_parser_system_prompt.md")
    parser.add_argument("--context-length", type=int, default=8192)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--clarification-eagerness", type=float, default=0.35)
    parser.add_argument("--max-clarification-rounds", type=int, default=2)
    parser.add_argument("--ce-mode", choices=["same", "off", "explicit"], default="same")
    parser.add_argument("--clarification-answer-model", default="")
    parser.add_argument("--clarification-answer-backend", default="")
    parser.add_argument("--clarification-answer-base-url", default="")
    parser.add_argument("--clarification-answer-context-length", type=int, default=8192)
    parser.add_argument("--clarification-answer-min-confidence", type=float, default=0.55)
    parser.add_argument("--no-write-corpus-on-fail", action="store_true")

    parser.add_argument(
        "--out-root",
        default="kb_runs/hn_random_ingest",
        help="Run artifact root. Default is repo-local history under kb_runs.",
    )
    parser.add_argument(
        "--kb-root",
        default="kb_store/hn_random_ingest",
        help="KB state root. Default is repo-local kb_store namespace for replay/diff.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run_stamp = _utc_stamp()
    run_label = f"hn_random_{args.feed}_{run_stamp}"

    out_root = (ROOT / args.out_root).resolve()
    run_dir = (out_root / run_label).resolve()
    source_dir = run_dir / "source_threads"
    turnset_dir = run_dir / "turnsets"
    scenario_dir = run_dir / "scenarios"
    report_dir = run_dir / "reports"
    for folder in (source_dir, turnset_dir, scenario_dir, report_dir):
        folder.mkdir(parents=True, exist_ok=True)

    rng = random.Random(int(args.seed))
    feed_ids = _fetch_feed_ids(api_base=args.hn_api_base, feed=args.feed, timeout_seconds=args.hn_timeout_seconds)
    if not feed_ids:
        raise RuntimeError("HN feed returned no ids.")

    candidate_ids = list(feed_ids[: max(1, int(args.max_candidates))])
    rng.shuffle(candidate_ids)

    selected_threads: list[HNThread] = []
    for item_id in candidate_ids:
        if len(selected_threads) >= max(1, int(args.sample_size)):
            break
        item = _fetch_item(api_base=args.hn_api_base, item_id=item_id, timeout_seconds=args.hn_timeout_seconds)
        if not isinstance(item, dict):
            continue
        if item.get("deleted") or item.get("dead"):
            continue
        if str(item.get("type", "")).strip().lower() != "story":
            continue
        title = _sanitize_hn_html(str(item.get("title") or "")).strip()
        if not title:
            continue

        comments = _collect_comments_bfs(
            api_base=args.hn_api_base,
            root_item=item,
            max_comments=max(0, int(args.max_comments)),
            max_depth=max(1, int(args.max_depth)),
            timeout_seconds=args.hn_timeout_seconds,
            max_comment_chars=max(0, int(args.max_comment_chars)),
        )
        if len(comments) < max(0, int(args.min_comments)):
            continue

        thread_id = int(item.get("id") or item_id)
        source_url = str(item.get("url") or "").strip()
        op_text = _sanitize_hn_html(str(item.get("text") or ""))
        thread = HNThread(
            thread_id=thread_id,
            title=title,
            by=str(item.get("by") or "unknown").strip() or "unknown",
            unix_time=int(item.get("time") or 0),
            score=int(item.get("score") or 0),
            descendants=int(item.get("descendants") or 0),
            hn_url=f"https://news.ycombinator.com/item?id={thread_id}",
            source_url=source_url,
            op_text=op_text,
            comments=comments,
        )
        selected_threads.append(thread)

    if not selected_threads:
        raise RuntimeError(
            "No candidate threads met selection criteria. Try lowering --min-comments or increasing --max-candidates."
        )

    records: list[dict[str, Any]] = []
    for index, thread in enumerate(selected_threads, start=1):
        label = f"{index:02d}_{thread.thread_id}_{_slug(thread.title, max_len=40)}"

        source_payload = {
            "thread_id": thread.thread_id,
            "hn_url": thread.hn_url,
            "source_url": thread.source_url,
            "title": thread.title,
            "by": thread.by,
            "unix_time": thread.unix_time,
            "score": thread.score,
            "descendants": thread.descendants,
            "comment_count": len(thread.comments),
            "comments": [
                {
                    "id": c.item_id,
                    "by": c.by,
                    "time": c.unix_time,
                    "depth": c.depth,
                    "parent": c.parent,
                    "text": c.text,
                }
                for c in thread.comments
            ],
        }
        source_path = source_dir / f"{label}.json"
        source_path.write_text(json.dumps(source_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        turnset = _build_turnset(thread, max_op_chars=max(0, int(args.max_op_chars)))
        turnset_path = turnset_dir / f"{label}_turnset.json"
        turnset_path.write_text(json.dumps(turnset, ensure_ascii=False, indent=2), encoding="utf-8")

        scenario = _build_scenario(thread, turnset)
        scenario_path = scenario_dir / f"{scenario['name']}.json"
        scenario_path.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")

        report_path = report_dir / f"{scenario['name']}_run.json"
        exit_code = _run_pipeline_for_scenario(
            scenario_path=scenario_path,
            report_path=report_path,
            backend=str(args.backend),
            base_url=str(args.base_url),
            model=str(args.model),
            runtime=str(args.runtime),
            kb_root=str(args.kb_root),
            prompt_file=str(args.prompt_file),
            context_length=int(args.context_length),
            timeout_seconds=int(args.timeout_seconds),
            clarification_eagerness=float(args.clarification_eagerness),
            max_clarification_rounds=int(args.max_clarification_rounds),
            ce_mode=str(args.ce_mode),
            clarification_answer_model=str(args.clarification_answer_model),
            clarification_answer_backend=str(args.clarification_answer_backend),
            clarification_answer_base_url=str(args.clarification_answer_base_url),
            clarification_answer_context_length=int(args.clarification_answer_context_length),
            clarification_answer_min_confidence=float(args.clarification_answer_min_confidence),
            write_corpus_on_fail=not bool(args.no_write_corpus_on_fail),
        )

        row = _record_from_report(
            thread=thread,
            scenario_name=str(scenario["name"]),
            report_path=report_path,
            exit_code=exit_code,
        )
        row["source_thread_path"] = str(source_path)
        row["turnset_path"] = str(turnset_path)
        row["scenario_path"] = str(scenario_path)
        records.append(row)

    runs_total = len(records)
    runs_passed = sum(1 for r in records if str(r.get("overall_status", "")).strip().lower() == "passed")
    turns_total = sum(int(r.get("turns_total", 0) or 0) for r in records)
    apply_failures_total = sum(int(r.get("turn_apply_failures", 0) or 0) for r in records)
    parse_failures_total = sum(int(r.get("turn_parse_failures", 0) or 0) for r in records)
    clar_requests_total = sum(int(r.get("clarification_requests", 0) or 0) for r in records)
    clar_answers_total = sum(int(r.get("clarification_answers_used_total", 0) or 0) for r in records)
    commit_turn_rate_avg = (
        round(sum(float(r.get("commit_turn_rate", 0.0) or 0.0) for r in records) / runs_total, 4)
        if runs_total
        else 0.0
    )

    summary = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "run_label": run_label,
        "run_dir": str(run_dir),
        "stories_requested": int(args.sample_size),
        "stories_selected": len(selected_threads),
        "runs_total": runs_total,
        "runs_passed": runs_passed,
        "settings": {
            "feed": args.feed,
            "seed": int(args.seed),
            "max_candidates": int(args.max_candidates),
            "min_comments": int(args.min_comments),
            "max_comments": int(args.max_comments),
            "max_depth": int(args.max_depth),
            "backend": args.backend,
            "base_url": args.base_url,
            "model": args.model,
            "runtime": args.runtime,
            "prompt_file": args.prompt_file,
            "context_length": int(args.context_length),
            "timeout_seconds": int(args.timeout_seconds),
            "clarification_eagerness": float(args.clarification_eagerness),
            "max_clarification_rounds": int(args.max_clarification_rounds),
            "ce_mode": args.ce_mode,
            "clarification_answer_model": (
                args.model if args.ce_mode == "same" else str(args.clarification_answer_model).strip()
            ),
            "clarification_answer_context_length": int(args.clarification_answer_context_length),
            "clarification_answer_min_confidence": float(args.clarification_answer_min_confidence),
            "kb_root": str(args.kb_root),
        },
        "totals": {
            "turns_total": turns_total,
            "apply_failures_total": apply_failures_total,
            "parse_failures_total": parse_failures_total,
            "clarification_requests_total": clar_requests_total,
            "clarification_answers_total": clar_answers_total,
            "commit_turn_rate_avg": commit_turn_rate_avg,
        },
        "records": records,
    }

    summary_json = run_dir / "summary.json"
    summary_md = run_dir / "summary.md"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown_summary(summary_md, summary)

    print("")
    print("HN random ingest complete")
    print("note: local-only artifacts written (no cloud push performed)")
    print(f"run_dir: {run_dir}")
    print(f"runs_passed: {runs_passed}/{runs_total}")
    print(f"turns_total: {turns_total}")
    print(f"apply_failures_total: {apply_failures_total}")
    print(f"clarification_requests_total: {clar_requests_total}")
    print(f"summary_json: {summary_json}")
    print(f"summary_md: {summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
