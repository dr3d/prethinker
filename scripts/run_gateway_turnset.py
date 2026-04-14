#!/usr/bin/env python3
"""
Run a turnset through the product front door (`/api/prethink`) and capture artifacts.

This keeps evaluation on the same path we intend to ship:
language -> strict gateway bouncer -> deterministic runtime phases.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")


def _slug(text: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or ""))
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_") or "gateway_run"


def _normalize_base_url(raw: str) -> str:
    value = str(raw or "").strip()
    if not value:
        return "http://127.0.0.1:8765"
    return value.rstrip("/")


def _detect_turns_format(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".jsonl":
        return "jsonl"
    if ext == ".json":
        return "json"
    return "txt"


def _coerce_turn_entry(raw: Any) -> dict[str, Any]:
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            raise ValueError("Encountered empty turn text.")
        return {"utterance": text}

    if isinstance(raw, dict):
        text = str(raw.get("utterance") or raw.get("text") or raw.get("input") or "").strip()
        if not text:
            raise ValueError(f"Turn object missing utterance text: {raw}")
        row = dict(raw)
        row["utterance"] = text
        return row

    text = str(raw).strip()
    if not text:
        raise ValueError("Encountered empty turn text.")
    return {"utterance": text}


def _load_turns(path: Path, turns_format: str) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8-sig")
    fmt = turns_format if turns_format != "auto" else _detect_turns_format(path)

    turns: list[dict[str, Any]] = []
    if fmt == "txt":
        for line in raw.splitlines():
            text = line.strip()
            if text:
                turns.append(_coerce_turn_entry(text))
        return turns

    if fmt == "jsonl":
        for idx, line in enumerate(raw.splitlines(), start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                payload = text
            try:
                turns.append(_coerce_turn_entry(payload))
            except ValueError as err:
                raise ValueError(f"Invalid jsonl turn at line {idx}: {err}") from err
        return turns

    if fmt == "json":
        payload = json.loads(raw)
        items: list[Any]
        if isinstance(payload, dict):
            if isinstance(payload.get("utterances"), list):
                items = list(payload.get("utterances", []))
            elif isinstance(payload.get("turns"), list):
                items = list(payload.get("turns", []))
            else:
                raise ValueError("JSON input must contain `utterances` or `turns` list.")
        elif isinstance(payload, list):
            items = payload
        else:
            raise ValueError("JSON input must be an object or list.")
        for idx, item in enumerate(items, start=1):
            try:
                turns.append(_coerce_turn_entry(item))
            except ValueError as err:
                raise ValueError(f"Invalid turn at index {idx}: {err}") from err
        return turns

    raise ValueError(f"Unsupported turns format: {fmt}")


def _request_json(
    *,
    base_url: str,
    path: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    url = f"{base_url}{path}"
    body: bytes | None = None
    req_headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url=url, data=body, method=method.upper(), headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=max(5, int(timeout_seconds))) as resp:
            text = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {err.code} for {url}: {raw}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Connection error for {url}: {err}") from err
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Non-JSON response from {url}: {text[:240]}") from err
    if not isinstance(parsed, dict):
        raise RuntimeError(f"Unexpected response type from {url}: {type(parsed).__name__}")
    return parsed


def _phase_status(turn: dict[str, Any], phase_name: str) -> str:
    phases = turn.get("phases", [])
    if not isinstance(phases, list):
        return ""
    for row in phases:
        if not isinstance(row, dict):
            continue
        if str(row.get("phase", "")).strip() == phase_name:
            return str(row.get("status", "")).strip().lower()
    return ""


def _summarize(responses: list[dict[str, Any]]) -> dict[str, Any]:
    route_counts: dict[str, int] = {}
    clarify_required = 0
    clarify_resolved = 0
    commit_applied = 0
    commit_blocked = 0
    commit_failed = 0
    answer_error = 0

    for item in responses:
        turn = item.get("turn", {})
        if not isinstance(turn, dict):
            continue
        route = str(turn.get("route", "other")).strip() or "other"
        route_counts[route] = route_counts.get(route, 0) + 1

        clarify_status = _phase_status(turn, "clarify")
        if clarify_status == "required":
            clarify_required += 1
        if clarify_status == "resolved":
            clarify_resolved += 1

        commit_status = _phase_status(turn, "commit")
        if commit_status == "applied":
            commit_applied += 1
        elif commit_status == "blocked":
            commit_blocked += 1
        elif commit_status in {"failed", "error"}:
            commit_failed += 1

        answer_status = _phase_status(turn, "answer")
        if answer_status in {"error", "failed"}:
            answer_error += 1

    return {
        "turns_total": len(responses),
        "route_counts": route_counts,
        "clarify_required": clarify_required,
        "clarify_resolved": clarify_resolved,
        "commit_applied": commit_applied,
        "commit_blocked": commit_blocked,
        "commit_failed": commit_failed,
        "answer_error": answer_error,
    }


def _strict_lock_payload() -> dict[str, Any]:
    return {
        "strict_mode": True,
        "compiler_mode": "strict",
        "served_handoff_mode": "never",
        "require_final_confirmation": True,
    }


def _write_transcript(path: Path, responses: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    for idx, item in enumerate(responses, start=1):
        utterance = str(item.get("utterance", "")).strip()
        turn = item.get("turn", {}) if isinstance(item.get("turn"), dict) else {}
        route = str(turn.get("route", "other")).strip() or "other"
        answer = turn.get("assistant", {}) if isinstance(turn.get("assistant"), dict) else {}
        answer_text = str(answer.get("text", "")).strip()
        lines.append(f"## Turn {idx}")
        lines.append(f"user: {utterance}")
        lines.append(f"route: {route}")
        lines.append(f"assistant: {answer_text}")
        lines.append("")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a turnset through /api/prethink and save artifacts.")
    parser.add_argument("--turns", required=True, help="Turnset file (.json/.jsonl/.txt).")
    parser.add_argument("--turns-format", default="auto", choices=["auto", "txt", "jsonl", "json"])
    parser.add_argument("--base-url", default="http://127.0.0.1:8765", help="Gateway base URL.")
    parser.add_argument("--session-id", default="", help="Optional existing session id.")
    parser.add_argument("--reset-session", action="store_true", help="Reset gateway session before the run.")
    parser.add_argument("--strict-lock", action="store_true", help="Apply strict bouncer lock before run.")
    parser.add_argument(
        "--config-overrides",
        default="",
        help="Optional JSON object merged into gateway config before run.",
    )
    parser.add_argument("--max-turns", type=int, default=0, help="Optional max turns to run.")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--label", default="", help="Optional run label for artifact folder naming.")
    parser.add_argument("--out-dir", default="tmp/runs/gateway_sessions")
    args = parser.parse_args()

    turns_path = Path(args.turns)
    if not turns_path.is_absolute():
        turns_path = (ROOT / turns_path).resolve()
    if not turns_path.exists():
        raise SystemExit(f"Turns file not found: {turns_path}")

    turns = _load_turns(turns_path, args.turns_format)
    if int(args.max_turns) > 0:
        turns = turns[: int(args.max_turns)]
    if not turns:
        raise SystemExit("No turns to run.")

    base_url = _normalize_base_url(args.base_url)
    timeout_seconds = max(5, int(args.timeout_seconds))

    current_config = _request_json(
        base_url=base_url,
        path="/api/config",
        timeout_seconds=timeout_seconds,
    ).get("config", {})
    if not isinstance(current_config, dict):
        current_config = {}

    overrides: dict[str, Any] = {}
    if args.strict_lock:
        overrides.update(_strict_lock_payload())
    if str(args.config_overrides or "").strip():
        raw = json.loads(str(args.config_overrides))
        if not isinstance(raw, dict):
            raise SystemExit("--config-overrides must be a JSON object.")
        overrides.update(raw)
    if overrides:
        updated = _request_json(
            base_url=base_url,
            path="/api/config",
            method="POST",
            payload=overrides,
            timeout_seconds=timeout_seconds,
        )
        current_config = updated.get("config", current_config)

    session_id = str(args.session_id or "").strip()
    if args.reset_session or not session_id:
        reset_headers = {"X-Session-Id": session_id} if session_id else {}
        reset_payload = _request_json(
            base_url=base_url,
            path="/api/session/reset",
            method="GET",
            headers=reset_headers,
            timeout_seconds=timeout_seconds,
        )
        session_id = str(reset_payload.get("session_id", "")).strip()

    started_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    responses: list[dict[str, Any]] = []
    for idx, row in enumerate(turns, start=1):
        utterance = str(row.get("utterance", "")).strip()
        if not utterance:
            continue
        payload = {"session_id": session_id, "utterance": utterance}
        result = _request_json(
            base_url=base_url,
            path="/api/prethink",
            method="POST",
            payload=payload,
            timeout_seconds=timeout_seconds,
        )
        session_id = str(result.get("session_id", session_id)).strip() or session_id
        responses.append(
            {
                "index": idx,
                "utterance": utterance,
                "response": result,
                "turn": result.get("turn", {}),
            }
        )
        turn = result.get("turn", {}) if isinstance(result.get("turn"), dict) else {}
        route = str(turn.get("route", "other")).strip() or "other"
        print(f"[{idx}/{len(turns)}] route={route} session={session_id}")

    finished_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    run_label = args.label or turns_path.stem
    run_dir = (ROOT / args.out_dir / f"{_utc_stamp()}_{_slug(run_label)}").resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    summary = _summarize(responses)
    summary.update(
        {
            "status": "ok",
            "started_at_utc": started_at,
            "finished_at_utc": finished_at,
            "base_url": base_url,
            "session_id": session_id,
            "turns_file": str(turns_path),
            "config_snapshot": current_config,
            "run_dir": str(run_dir),
        }
    )

    (run_dir / "responses.json").write_text(
        json.dumps(responses, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / "session_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _write_transcript(run_dir / "transcript.md", responses)

    print(f"Saved gateway run artifacts: {run_dir}")
    print(
        "Summary: "
        f"turns={summary['turns_total']} "
        f"commit_applied={summary['commit_applied']} "
        f"clarify_required={summary['clarify_required']} "
        f"commit_failed={summary['commit_failed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
