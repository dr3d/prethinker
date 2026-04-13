#!/usr/bin/env python3
"""
Turn-by-turn MITM session runner for prethinker.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "kb_pipeline.py"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import kb_pipeline as kp  # noqa: E402

DEFAULT_BASE_URLS = {
    "ollama": "http://127.0.0.1:11434",
    "lmstudio": "http://127.0.0.1:1234",
}


def _utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")


def _slug(text: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or ""))
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_") or "session"


def _clip_01(value: Any, fallback: float = 0.5) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return max(0.0, min(1.0, parsed))


def _tail_lines(text: str, limit: int = 16) -> list[str]:
    rows = str(text or "").splitlines()
    if len(rows) <= limit:
        return rows
    return rows[-limit:]


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


def _build_pipeline_command(
    *,
    scenario_path: Path,
    out_path: Path,
    args: argparse.Namespace,
    force_empty_kb: bool,
) -> list[str]:
    cmd = [
        sys.executable,
        str(PIPELINE),
        "--scenario",
        str(scenario_path),
        "--out",
        str(out_path),
        "--backend",
        args.backend,
        "--base-url",
        args.base_url,
        "--model",
        args.model,
        "--runtime",
        args.runtime,
        "--kb-name",
        args.kb_name,
        "--kb-root",
        args.kb_root,
        "--prompt-file",
        args.prompt_file,
        "--sp-conflict-policy",
        args.sp_conflict_policy,
        "--context-length",
        str(int(args.context_length)),
        "--clarification-eagerness",
        str(float(args.clarification_eagerness)),
        "--max-clarification-rounds",
        str(int(args.max_clarification_rounds)),
        "--timeout-seconds",
        str(int(args.timeout_seconds)),
    ]
    if force_empty_kb:
        cmd.append("--force-empty-kb")
    if args.require_final_confirmation:
        cmd.append("--require-final-confirmation")
    if args.strict_registry:
        cmd.append("--strict-registry")
    if args.predicate_registry:
        cmd.extend(["--predicate-registry", args.predicate_registry])
    if args.type_schema:
        cmd.extend(["--type-schema", args.type_schema])
    if args.strict_types:
        cmd.append("--strict-types")
    if args.env_file:
        cmd.extend(["--env-file", args.env_file])
    if args.served_llm_model:
        cmd.extend(["--served-llm-model", args.served_llm_model])
    if args.served_llm_backend:
        cmd.extend(["--served-llm-backend", args.served_llm_backend])
    if args.served_llm_base_url:
        cmd.extend(["--served-llm-base-url", args.served_llm_base_url])
    if int(args.served_llm_context_length) > 0:
        cmd.extend(["--served-llm-context-length", str(int(args.served_llm_context_length))])
    if args.clarification_answer_model:
        cmd.extend(["--clarification-answer-model", args.clarification_answer_model])
    if args.clarification_answer_backend:
        cmd.extend(["--clarification-answer-backend", args.clarification_answer_backend])
    if args.clarification_answer_base_url:
        cmd.extend(["--clarification-answer-base-url", args.clarification_answer_base_url])
    if int(args.clarification_answer_context_length) > 0:
        cmd.extend(
            [
                "--clarification-answer-context-length",
                str(int(args.clarification_answer_context_length)),
            ]
        )
    if int(args.clarification_answer_history_turns) >= 0:
        cmd.extend(
            [
                "--clarification-answer-history-turns",
                str(int(args.clarification_answer_history_turns)),
            ]
        )
    if int(args.clarification_answer_kb_clause_limit) >= 0:
        cmd.extend(
            [
                "--clarification-answer-kb-clause-limit",
                str(int(args.clarification_answer_kb_clause_limit)),
            ]
        )
    if int(args.clarification_answer_kb_char_budget) >= 0:
        cmd.extend(
            [
                "--clarification-answer-kb-char-budget",
                str(int(args.clarification_answer_kb_char_budget)),
            ]
        )
    if float(args.clarification_answer_min_confidence) >= 0:
        cmd.extend(
            [
                "--clarification-answer-min-confidence",
                str(float(args.clarification_answer_min_confidence)),
            ]
        )
    return cmd


def _run_pipeline_once(
    *,
    scenario_payload: dict[str, Any],
    scenario_path: Path,
    report_path: Path,
    args: argparse.Namespace,
    force_empty_kb: bool,
) -> dict[str, Any]:
    scenario_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_path.write_text(
        json.dumps(scenario_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    cmd = _build_pipeline_command(
        scenario_path=scenario_path,
        out_path=report_path,
        args=args,
        force_empty_kb=force_empty_kb,
    )
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    report: dict[str, Any] = {}
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8-sig"))
            if not isinstance(report, dict):
                report = {}
        except json.JSONDecodeError:
            report = {}
    return {
        "cmd": cmd,
        "return_code": int(proc.returncode),
        "stdout_tail": _tail_lines(proc.stdout, limit=20),
        "stderr_tail": _tail_lines(proc.stderr, limit=20),
        "report_path": str(report_path),
        "report": report,
    }


def _extract_turn_row(report: dict[str, Any]) -> dict[str, Any]:
    rows = report.get("turns", [])
    if isinstance(rows, list):
        for row in reversed(rows):
            if isinstance(row, dict):
                return row
    return {}


def _is_pending(turn: dict[str, Any]) -> bool:
    apply_status = str(turn.get("apply_status", "")).strip().lower()
    if apply_status in {"clarification_requested", "confirmation_requested"}:
        return True
    return bool(turn.get("clarification_pending", False))


def _is_committed(turn: dict[str, Any]) -> bool:
    if _is_pending(turn):
        return False
    status = str(turn.get("apply_status", "")).strip().lower()
    return status in {"success", "skipped", "no_results"}


def _compact_turn_snapshot(turn: dict[str, Any]) -> dict[str, Any]:
    parsed = turn.get("parsed", {}) if isinstance(turn.get("parsed"), dict) else {}
    return {
        "turn_index": int(turn.get("turn_index", 0) or 0),
        "utterance": str(turn.get("utterance_original") or turn.get("utterance") or "").strip(),
        "route": str(turn.get("route", "")).strip(),
        "route_source": str(turn.get("route_source", "")).strip(),
        "apply_status": str(turn.get("apply_status", "")).strip(),
        "decision_state": str(turn.get("decision_state", "")).strip(),
        "clarification_pending": bool(turn.get("clarification_pending", False)),
        "clarification_question": str(turn.get("clarification_question", "")).strip(),
        "clarification_pending_reason": str(turn.get("clarification_pending_reason", "")).strip(),
        "logic_string": str(parsed.get("logic_string", "")).strip(),
        "intent": str(parsed.get("intent", "")).strip(),
    }


def _collect_recent_context(records: list[dict[str, Any]], limit: int) -> list[str]:
    rows: list[str] = []
    for row in records[-max(0, limit) :]:
        snap = row.get("final_turn_snapshot", {})
        if not isinstance(snap, dict):
            continue
        utterance = str(snap.get("utterance", "")).strip()
        logic = str(snap.get("logic_string", "")).strip()
        status = str(snap.get("apply_status", "")).strip()
        if utterance:
            line = f"U: {utterance} | apply={status}"
            if logic:
                line += f" | logic={logic}"
            rows.append(line)
    return rows


def _read_kb_tail(report: dict[str, Any], max_clauses: int) -> list[str]:
    kb_namespace = report.get("kb_namespace", {})
    if not isinstance(kb_namespace, dict):
        return []
    corpus = str(kb_namespace.get("corpus_path", "")).strip()
    if not corpus:
        return []
    path = Path(corpus)
    if not path.exists():
        return []
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        clause = raw.strip()
        if not clause or clause.startswith("%"):
            continue
        lines.append(clause)
    if max_clauses <= 0:
        return lines
    return lines[-max_clauses:]


def _build_sidecar_fallback_prompt(
    *,
    utterance: str,
    clarification_question: str,
    parsed: dict[str, Any],
    recent_context: list[str],
    kb_tail: list[str],
) -> str:
    parsed_view = {
        "intent": parsed.get("intent"),
        "logic_string": parsed.get("logic_string"),
        "ambiguities": parsed.get("ambiguities", []),
        "clarification_reason": parsed.get("clarification_reason", ""),
        "uncertainty_score": parsed.get("uncertainty_score"),
    }
    recent_text = "\n".join(f"- {row}" for row in recent_context) if recent_context else "(none)"
    kb_text = "\n".join(f"- {row}" for row in kb_tail) if kb_tail else "(none)"
    return (
        "/no_think\n"
        "You are a sidecar clarification resolver for a semantic parser MITM loop.\n"
        "Return minified JSON only with keys: answer,confidence,assumption\n"
        "Rules:\n"
        "- answer must directly answer the clarification question in <=18 words\n"
        "- if uncertain, answer must be exactly 'unknown'\n"
        "- confidence must be numeric in [0,1]\n"
        "- assumption must be <=12 words\n"
        "Do not output markdown or extra keys.\n"
        f"Original utterance:\n{utterance}\n"
        f"Clarification question:\n{clarification_question}\n"
        f"Current parse draft:\n{json.dumps(parsed_view, ensure_ascii=False)}\n"
        f"Recent accepted context:\n{recent_text}\n"
        f"Current KB tail:\n{kb_text}\n"
    )


def _generate_sidecar_answer(
    *,
    backend: str,
    base_url: str,
    model: str,
    context_length: int,
    timeout_seconds: int,
    utterance: str,
    clarification_question: str,
    parsed: dict[str, Any],
    recent_context: list[str],
    kb_tail: list[str],
) -> tuple[str, dict[str, Any]]:
    prompt = _build_sidecar_fallback_prompt(
        utterance=utterance,
        clarification_question=clarification_question,
        parsed=parsed,
        recent_context=recent_context,
        kb_tail=kb_tail,
    )
    api_key = kp._get_api_key() if hasattr(kp, "_get_api_key") else None
    response = kp._call_model_prompt(
        backend=backend,
        base_url=base_url,
        model=model,
        prompt_text=prompt,
        context_length=max(512, int(context_length)),
        timeout=max(10, int(timeout_seconds)),
        api_key=api_key,
    )
    parsed_json, _ = kp._parse_model_json(response, required_keys=["answer"])
    if isinstance(parsed_json, dict):
        answer = kp._coerce_synthetic_answer_text(parsed_json.get("answer", ""))
        confidence = _clip_01(parsed_json.get("confidence"), fallback=0.5)
        if answer:
            return answer, {
                "answer_source": "sidecar_model",
                "answer_confidence": confidence,
                "answer_assumption": str(parsed_json.get("assumption", "")).strip(),
            }

    fallback = kp._coerce_synthetic_answer_text(getattr(response, "message", ""))
    if fallback:
        return fallback, {
            "answer_source": "sidecar_fallback",
            "answer_confidence": 0.3,
            "answer_assumption": "fallback from raw response message",
        }
    return "", {
        "answer_source": "sidecar_failed",
        "answer_confidence": 0.0,
        "answer_assumption": "no parseable answer",
    }


def _readiness_grade(*, commit_rate: float, unresolved_rate: float, fallback_resolution_rate: float) -> str:
    score = (0.6 * commit_rate) + (0.25 * (1.0 - unresolved_rate)) + (0.15 * fallback_resolution_rate)
    if score >= 0.95:
        return "A"
    if score >= 0.88:
        return "B"
    if score >= 0.76:
        return "C"
    if score >= 0.62:
        return "D"
    return "F"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Turn-by-turn MITM session runner with optional sidecar clarification fallback."
    )
    p.add_argument("--turns-file", required=True, help="Path to session turns (.txt, .jsonl, or .json).")
    p.add_argument("--turns-format", choices=["auto", "txt", "jsonl", "json"], default="auto")
    p.add_argument("--max-turns", type=int, default=0, help="Optional cap; 0 means all turns.")
    p.add_argument("--session-name", default="", help="Human-readable session name for output folder/report.")

    p.add_argument("--backend", choices=["ollama", "lmstudio"], default="ollama")
    p.add_argument("--base-url", default=DEFAULT_BASE_URLS["ollama"])
    p.add_argument("--model", default="qwen3.5:9b")
    p.add_argument("--runtime", choices=["core", "none", "mcp"], default="core")
    p.add_argument("--kb-name", default="mitm_live_session")
    p.add_argument("--kb-root", default="tmp/kb_store")
    p.add_argument("--reset-kb", action="store_true", help="Force empty KB before first turn.")

    p.add_argument("--prompt-file", default="modelfiles/semantic_parser_system_prompt.md")
    p.add_argument("--sp-conflict-policy", choices=["error", "warn", "off"], default="error")
    p.add_argument("--env-file", default="")
    p.add_argument("--timeout-seconds", type=int, default=120)
    p.add_argument("--context-length", type=int, default=8192)

    p.add_argument("--clarification-eagerness", type=float, default=0.8)
    p.add_argument("--max-clarification-rounds", type=int, default=2)
    p.add_argument("--require-final-confirmation", action="store_true")

    p.add_argument("--served-llm-model", default="")
    p.add_argument("--served-llm-backend", choices=["", "ollama", "lmstudio"], default="")
    p.add_argument("--served-llm-base-url", default="")
    p.add_argument("--served-llm-context-length", type=int, default=8192)

    p.add_argument("--clarification-answer-model", default="")
    p.add_argument("--clarification-answer-backend", choices=["", "ollama", "lmstudio"], default="")
    p.add_argument("--clarification-answer-base-url", default="")
    p.add_argument("--clarification-answer-context-length", type=int, default=16384)
    p.add_argument("--clarification-answer-history-turns", type=int, default=8)
    p.add_argument("--clarification-answer-kb-clause-limit", type=int, default=80)
    p.add_argument("--clarification-answer-kb-char-budget", type=int, default=5000)
    p.add_argument("--clarification-answer-min-confidence", type=float, default=0.55)

    p.add_argument("--strict-registry", action="store_true")
    p.add_argument("--predicate-registry", default="modelfiles/predicate_registry.json")
    p.add_argument("--type-schema", default="")
    p.add_argument("--strict-types", action="store_true")

    p.add_argument("--fallback-sidecar-model", default="", help="Secondary sidecar model for clarification replay.")
    p.add_argument("--fallback-sidecar-backend", choices=["", "ollama", "lmstudio"], default="")
    p.add_argument("--fallback-sidecar-base-url", default="")
    p.add_argument("--fallback-sidecar-context-length", type=int, default=8192)
    p.add_argument("--fallback-sidecar-min-confidence", type=float, default=0.45)
    p.add_argument("--fallback-sidecar-max-retries", type=int, default=1)
    p.add_argument("--fallback-sidecar-recent-turns", type=int, default=8)
    p.add_argument("--fallback-sidecar-kb-clauses", type=int, default=80)

    p.add_argument("--out-dir", default="tmp/runs/mitm_sessions")
    p.add_argument("--summary-out", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    turns_path = Path(args.turns_file).resolve()
    if not turns_path.exists():
        print(f"Turns file not found: {turns_path}")
        return 2

    turns = _load_turns(turns_path, args.turns_format)
    if not turns:
        print("No turns found in input.")
        return 2
    if int(args.max_turns) > 0:
        turns = turns[: int(args.max_turns)]

    if not args.served_llm_base_url and args.served_llm_backend:
        args.served_llm_base_url = DEFAULT_BASE_URLS[args.served_llm_backend]
    if not args.clarification_answer_base_url and args.clarification_answer_backend:
        args.clarification_answer_base_url = DEFAULT_BASE_URLS[args.clarification_answer_backend]
    if not args.fallback_sidecar_base_url and args.fallback_sidecar_backend:
        args.fallback_sidecar_base_url = DEFAULT_BASE_URLS[args.fallback_sidecar_backend]

    stamp = _utc_stamp()
    session_name = args.session_name.strip() or turns_path.stem
    session_id = f"{stamp}_{_slug(session_name)}"
    out_dir = (ROOT / args.out_dir).resolve()
    session_dir = out_dir / session_id
    scenario_dir = session_dir / "scenarios"
    report_dir = session_dir / "reports"
    scenario_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    transcript_path = session_dir / "session_transcript.jsonl"
    summary_out = (
        Path(args.summary_out).resolve()
        if str(args.summary_out).strip()
        else session_dir / "session_summary.json"
    )

    print(f"Session: {session_name}")
    print(f"Session id: {session_id}")
    print(f"Turns: {len(turns)}")
    print(f"KB: {args.kb_name} @ {args.kb_root}")
    print(f"Parser: {args.backend}/{args.model}")
    if args.served_llm_model:
        print(
            "Served loop: "
            f"{args.served_llm_backend or args.backend}/{args.served_llm_model} "
            f"@ {args.served_llm_base_url or DEFAULT_BASE_URLS[args.served_llm_backend or args.backend]}"
        )
    elif args.clarification_answer_model:
        print(
            "Clarification proxy: "
            f"{args.clarification_answer_backend or args.backend}/{args.clarification_answer_model} "
            f"@ {args.clarification_answer_base_url or DEFAULT_BASE_URLS[args.clarification_answer_backend or args.backend]}"
        )
    else:
        print("Clarification auto-answer: disabled")
    if args.fallback_sidecar_model:
        print(
            "Fallback sidecar: "
            f"{args.fallback_sidecar_backend or args.backend}/{args.fallback_sidecar_model} "
            f"@ {args.fallback_sidecar_base_url or DEFAULT_BASE_URLS[args.fallback_sidecar_backend or args.backend]}"
        )

    records: list[dict[str, Any]] = []
    fallback_attempts_total = 0
    fallback_resolution_total = 0

    for idx, turn_entry in enumerate(turns, start=1):
        utterance = str(turn_entry.get("utterance", "")).strip()
        scenario_payload = {
            "name": f"{_slug(session_name)}_turn_{idx:03d}",
            "ontology_name": args.kb_name,
            "utterances": [turn_entry],
            "validations": [],
        }
        scenario_path = scenario_dir / f"turn_{idx:03d}.json"
        report_path = report_dir / f"turn_{idx:03d}.json"
        force_empty = bool(args.reset_kb and idx == 1)

        run = _run_pipeline_once(
            scenario_payload=scenario_payload,
            scenario_path=scenario_path,
            report_path=report_path,
            args=args,
            force_empty_kb=force_empty,
        )
        report = run.get("report", {})
        if not isinstance(report, dict):
            report = {}
        turn = _extract_turn_row(report)
        final_turn = turn
        fallback_rows: list[dict[str, Any]] = []

        pending = _is_pending(turn)
        if pending and args.fallback_sidecar_model:
            recent_context = _collect_recent_context(records, limit=max(0, int(args.fallback_sidecar_recent_turns)))
            kb_tail = _read_kb_tail(report, max_clauses=max(0, int(args.fallback_sidecar_kb_clauses)))
            clarification_question = str(turn.get("clarification_question", "")).strip()
            parsed = turn.get("parsed", {}) if isinstance(turn.get("parsed"), dict) else {}
            for attempt in range(1, max(0, int(args.fallback_sidecar_max_retries)) + 1):
                fallback_attempts_total += 1
                answer, answer_meta = _generate_sidecar_answer(
                    backend=args.fallback_sidecar_backend or args.backend,
                    base_url=(
                        args.fallback_sidecar_base_url
                        or DEFAULT_BASE_URLS[args.fallback_sidecar_backend or args.backend]
                    ),
                    model=args.fallback_sidecar_model,
                    context_length=max(512, int(args.fallback_sidecar_context_length)),
                    timeout_seconds=max(10, int(args.timeout_seconds)),
                    utterance=utterance,
                    clarification_question=clarification_question,
                    parsed=parsed,
                    recent_context=recent_context,
                    kb_tail=kb_tail,
                )
                accepted_answer = (
                    bool(answer)
                    and not kp._is_non_informative_clarification_answer(answer)
                    and _clip_01(answer_meta.get("answer_confidence"), fallback=0.0)
                    >= _clip_01(args.fallback_sidecar_min_confidence, fallback=0.45)
                )
                replay_status = "skipped"
                replay_turn_snapshot: dict[str, Any] = {}
                replay_report_path = ""
                if accepted_answer:
                    replay_entry = dict(turn_entry)
                    existing_answers = replay_entry.get("clarification_answers", [])
                    scripted_answers: list[str] = []
                    if isinstance(existing_answers, list):
                        scripted_answers = [str(item).strip() for item in existing_answers if str(item).strip()]
                    replay_entry["clarification_answers"] = scripted_answers + [answer]
                    if "max_clarification_rounds" not in replay_entry:
                        replay_entry["max_clarification_rounds"] = 1

                    replay_payload = {
                        "name": f"{_slug(session_name)}_turn_{idx:03d}_replay_{attempt:02d}",
                        "ontology_name": args.kb_name,
                        "utterances": [replay_entry],
                        "validations": [],
                    }
                    replay_scenario_path = scenario_dir / f"turn_{idx:03d}_replay_{attempt:02d}.json"
                    replay_out_path = report_dir / f"turn_{idx:03d}_replay_{attempt:02d}.json"
                    replay_run = _run_pipeline_once(
                        scenario_payload=replay_payload,
                        scenario_path=replay_scenario_path,
                        report_path=replay_out_path,
                        args=args,
                        force_empty_kb=False,
                    )
                    replay_report = replay_run.get("report", {})
                    if not isinstance(replay_report, dict):
                        replay_report = {}
                    replay_turn = _extract_turn_row(replay_report)
                    replay_turn_snapshot = _compact_turn_snapshot(replay_turn)
                    replay_report_path = str(replay_out_path)
                    if _is_pending(replay_turn):
                        replay_status = "still_pending"
                    else:
                        replay_status = "resolved"
                        final_turn = replay_turn
                        report = replay_report
                        fallback_resolution_total += 1
                        fallback_rows.append(
                            {
                                "attempt": attempt,
                                "answer": answer,
                                "answer_meta": answer_meta,
                                "accepted_answer": True,
                                "replay_status": replay_status,
                                "replay_report_path": replay_report_path,
                                "replay_turn_snapshot": replay_turn_snapshot,
                            }
                        )
                        break

                fallback_rows.append(
                    {
                        "attempt": attempt,
                        "answer": answer,
                        "answer_meta": answer_meta,
                        "accepted_answer": accepted_answer,
                        "replay_status": replay_status,
                        "replay_report_path": replay_report_path,
                        "replay_turn_snapshot": replay_turn_snapshot,
                    }
                )

        final_snapshot = _compact_turn_snapshot(final_turn)
        record = {
            "turn_number": idx,
            "utterance": utterance,
            "initial_report_path": run.get("report_path", ""),
            "initial_turn_snapshot": _compact_turn_snapshot(turn),
            "final_turn_snapshot": final_snapshot,
            "fallback_attempts": fallback_rows,
            "turn_committed": _is_committed(final_turn),
            "turn_pending": _is_pending(final_turn),
            "report_overall_status": str(report.get("overall_status", "")).strip(),
        }
        records.append(record)
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        with transcript_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

        status_label = "commit" if record["turn_committed"] else ("pending" if record["turn_pending"] else "stage")
        print(
            f"[turn {idx:03d}] {status_label} "
            f"route={final_snapshot.get('route', '')} "
            f"apply={final_snapshot.get('apply_status', '')} "
            f"fallback_attempts={len(fallback_rows)}"
        )

    total = len(records)
    committed = sum(1 for row in records if bool(row.get("turn_committed")))
    pending = sum(1 for row in records if bool(row.get("turn_pending")))
    clarification_requested = sum(
        1
        for row in records
        if str((row.get("initial_turn_snapshot") or {}).get("apply_status", "")).strip().lower()
        in {"clarification_requested", "confirmation_requested"}
    )
    commit_rate = (committed / total) if total else 0.0
    unresolved_rate = (pending / total) if total else 0.0
    fallback_resolution_rate = (
        (fallback_resolution_total / fallback_attempts_total) if fallback_attempts_total else 0.0
    )
    readiness = _readiness_grade(
        commit_rate=commit_rate,
        unresolved_rate=unresolved_rate,
        fallback_resolution_rate=fallback_resolution_rate,
    )

    summary = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "session_name": session_name,
        "session_id": session_id,
        "turns_file": str(turns_path),
        "turns_total": total,
        "settings": {
            "backend": args.backend,
            "base_url": args.base_url,
            "model": args.model,
            "runtime": args.runtime,
            "kb_name": args.kb_name,
            "kb_root": args.kb_root,
            "prompt_file": args.prompt_file,
            "context_length": int(args.context_length),
            "clarification_eagerness": float(args.clarification_eagerness),
            "max_clarification_rounds": int(args.max_clarification_rounds),
            "served_llm_model": args.served_llm_model,
            "served_llm_backend": args.served_llm_backend,
            "served_llm_base_url": args.served_llm_base_url,
            "clarification_answer_model": args.clarification_answer_model,
            "clarification_answer_backend": args.clarification_answer_backend,
            "clarification_answer_base_url": args.clarification_answer_base_url,
            "fallback_sidecar_model": args.fallback_sidecar_model,
            "fallback_sidecar_backend": args.fallback_sidecar_backend,
            "fallback_sidecar_base_url": args.fallback_sidecar_base_url,
            "fallback_sidecar_max_retries": int(args.fallback_sidecar_max_retries),
            "fallback_sidecar_min_confidence": float(args.fallback_sidecar_min_confidence),
        },
        "metrics": {
            "committed_turns": committed,
            "pending_turns": pending,
            "clarification_requested_turns": clarification_requested,
            "fallback_attempts_total": fallback_attempts_total,
            "fallback_resolution_total": fallback_resolution_total,
            "commit_rate": round(commit_rate, 4),
            "unresolved_rate": round(unresolved_rate, 4),
            "fallback_resolution_rate": round(fallback_resolution_rate, 4),
            "in_world_readiness_grade": readiness,
        },
        "artifacts": {
            "session_dir": str(session_dir),
            "transcript_jsonl": str(transcript_path),
        },
        "records": records,
    }
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("")
    print(
        "Session summary: "
        f"commit={committed}/{total} pending={pending} "
        f"fallback_resolved={fallback_resolution_total}/{fallback_attempts_total} "
        f"grade={readiness}"
    )
    print(f"Summary: {summary_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
