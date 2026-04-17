#!/usr/bin/env python3
"""
Run a raw story stress cycle across split packaging and temporal modes.

This script calls scripts/run_story_raw.py for each selected configuration and
produces:
1) a machine-readable summary JSON,
2) a markdown scoreboard,
3) a human-facing HTML audit artifact.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN_STORY_RAW = ROOT / "scripts" / "run_story_raw.py"


def _slug(text: str, *, max_len: int = 80) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or ""))
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    cleaned = cleaned.strip("_") or "story"
    return cleaned[:max_len].strip("_") or "story"


def _utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _resolve_modes(text: str, allowed: set[str]) -> list[str]:
    out: list[str] = []
    for raw in str(text or "").split(","):
        mode = raw.strip().lower()
        if not mode or mode not in allowed:
            continue
        if mode not in out:
            out.append(mode)
    return out


def _resolve_temporal_modes(text: str) -> list[bool]:
    out: list[bool] = []
    for raw in str(text or "").split(","):
        token = raw.strip().lower()
        if token in {"on", "true", "1", "temporal"} and True not in out:
            out.append(True)
        if token in {"off", "false", "0", "plain"} and False not in out:
            out.append(False)
    return out


def _resolve_kb_path(report: dict[str, Any]) -> Path | None:
    ns = report.get("kb_namespace")
    if isinstance(ns, dict):
        corpus_path = ns.get("corpus_path")
        if isinstance(corpus_path, str) and corpus_path.strip():
            candidate = Path(corpus_path.strip())
            candidate = candidate if candidate.is_absolute() else (ROOT / candidate).resolve()
            return candidate
        kb_dir = ns.get("kb_dir")
        if isinstance(kb_dir, str) and kb_dir.strip():
            base = Path(kb_dir.strip())
            base = base if base.is_absolute() else (ROOT / base).resolve()
            return base / "kb.pl"
    return None


def _read_kb_preview(path: Path, *, max_lines: int = 240) -> tuple[str, int, int]:
    if not path.exists():
        return "", 0, 0
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    clause_count = 0
    for raw in lines:
        line = str(raw or "").strip()
        if not line or line.startswith("%") or line.startswith(":-"):
            continue
        if line.endswith("."):
            clause_count += 1
    shown = "\n".join(lines[: max(0, int(max_lines))])
    return shown, len(lines), clause_count


def _score_row(
    row: dict[str, Any],
    *,
    requested_exam_questions: int,
    story_char_count: int,
) -> float:
    pipeline_ok = 1.0 if str(row.get("pipeline_status", "")).lower() == "passed" else 0.0
    coverage = float(row.get("coverage", 0.0) or 0.0)
    precision = float(row.get("precision", 0.0) or 0.0)
    exam = float(row.get("exam_pass_rate", 0.0) or 0.0)
    temporal_exam = float(row.get("temporal_exam_pass_rate", 0.0) or 0.0)
    clause_coverage_ratio = float(row.get("kb_clause_coverage_ratio", 0.0) or 0.0)
    generated_questions = int(row.get("exam_question_count", 0) or 0)
    expected_questions = max(1, int(requested_exam_questions))
    question_count_ratio = min(1.0, float(generated_questions) / float(expected_questions))

    score = (
        (0.18 * pipeline_ok)
        + (0.22 * coverage)
        + (0.22 * precision)
        + (0.14 * exam)
        + (0.07 * temporal_exam)
        + (0.10 * clause_coverage_ratio)
        + (0.07 * question_count_ratio)
    )

    if question_count_ratio < 0.5:
        score *= 0.40
    if int(story_char_count) >= 3000 and clause_coverage_ratio < 0.25:
        score *= 0.20
    if int(story_char_count) >= 3000 and clause_coverage_ratio < 0.25 and question_count_ratio < 0.5:
        score = min(score, 0.05)
    if pipeline_ok < 1.0:
        score *= 0.50
    if int(story_char_count) >= 3000 and coverage < 0.10 and precision < 0.10:
        score = min(score, 0.08)

    return round(max(0.0, min(1.0, score)), 6)


def _answer_preview(value: Any, *, max_chars: int = 280) -> str:
    text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value or "")
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "…"


def _extract_ce_rows(pipeline_report: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    turns = pipeline_report.get("turns")
    if not isinstance(turns, list):
        return rows
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        rounds = turn.get("clarification_rounds")
        if not isinstance(rounds, list):
            rounds = []
        question = str(turn.get("clarification_question") or "").strip()
        if not question and not rounds and not bool(turn.get("clarification_pending", False)):
            continue
        rows.append(
            {
                "turn_index": int(turn.get("turn_index", 0) or 0),
                "utterance": str(turn.get("utterance_original") or turn.get("utterance") or "").strip(),
                "question": question,
                "pending": bool(turn.get("clarification_pending", False)),
                "rounds": [
                    {
                        "round": int(r.get("round", 0) or 0),
                        "question": str(r.get("question") or "").strip(),
                        "answer": str(r.get("answer") or "").strip(),
                        "answer_source": str(r.get("answer_source") or "").strip(),
                        "answer_confidence": r.get("answer_confidence"),
                    }
                    for r in rounds
                    if isinstance(r, dict)
                ],
            }
        )
    return rows


def _render_html_report(
    *,
    title: str,
    story_path: Path,
    story_text: str,
    rows: list[dict[str, Any]],
    best_row: dict[str, Any] | None,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    table_rows = []
    for row in rows:
        table_rows.append(
            "<tr>"
            f"<td><code>{html.escape(str(row.get('run_id', '')))}</code></td>"
            f"<td>{html.escape(str(row.get('split_mode', '')))}</td>"
            f"<td>{'on' if bool(row.get('temporal_dual_write')) else 'off'}</td>"
            f"<td><code>{html.escape(str(row.get('pipeline_status', 'missing')))}</code></td>"
            f"<td>{int(row.get('parse_failures', 0) or 0)}</td>"
            f"<td>{int(row.get('apply_failures', 0) or 0)}</td>"
            f"<td>{int(row.get('clarification_requests', 0) or 0)}</td>"
            f"<td>{float(row.get('coverage', 0.0) or 0.0):.3f}</td>"
            f"<td>{float(row.get('precision', 0.0) or 0.0):.3f}</td>"
            f"<td>{float(row.get('exam_pass_rate', 0.0) or 0.0):.3f}</td>"
            f"<td>{float(row.get('temporal_exam_pass_rate', 0.0) or 0.0):.3f}</td>"
            f"<td>{float(row.get('kb_clause_coverage_ratio', 0.0) or 0.0):.3f}</td>"
            f"<td>{float(row.get('exam_question_count_ratio', 0.0) or 0.0):.3f}</td>"
            f"<td><strong>{float(row.get('final_score', 0.0) or 0.0):.3f}</strong></td>"
            "</tr>"
        )

    best_section = "<p>No successful run artifacts found.</p>"
    if isinstance(best_row, dict):
        kb_text = str(best_row.get("kb_preview") or "")
        kb_line_count = int(best_row.get("kb_line_count", 0) or 0)
        exam_rows = best_row.get("exam_questions")
        if not isinstance(exam_rows, list):
            exam_rows = []
        ce_rows = best_row.get("ce_rows")
        if not isinstance(ce_rows, list):
            ce_rows = []

        exam_html_rows: list[str] = []
        for q in exam_rows:
            if not isinstance(q, dict):
                continue
            exam_html_rows.append(
                "<tr>"
                f"<td>{html.escape(str(q.get('id', '')))}</td>"
                f"<td>{html.escape(str(q.get('question', '')))}</td>"
                f"<td><code>{html.escape(str(q.get('query', '')))}</code></td>"
                f"<td>{'PASS' if bool(q.get('passed')) else 'FAIL'}</td>"
                f"<td><code>{html.escape(str(((q.get('result') or {}) if isinstance(q.get('result'), dict) else {}).get('status', '')))}</code></td>"
                f"<td><code>{html.escape(_answer_preview(q.get('answer_preview_rows')))}</code></td>"
                "</tr>"
            )
        if not exam_html_rows:
            exam_html_rows.append("<tr><td colspan='6'>No exam question records.</td></tr>")

        ce_html_rows: list[str] = []
        for ce in ce_rows:
            rounds = ce.get("rounds")
            if not isinstance(rounds, list):
                rounds = []
            rounds_text = []
            for r in rounds:
                if not isinstance(r, dict):
                    continue
                conf = r.get("answer_confidence")
                conf_text = f"{conf}" if conf is not None else "-"
                rounds_text.append(
                    f"r{int(r.get('round', 0) or 0)} | q={r.get('question','')} | "
                    f"a={r.get('answer','')} | src={r.get('answer_source','')} | conf={conf_text}"
                )
            ce_html_rows.append(
                "<tr>"
                f"<td>{int(ce.get('turn_index', 0) or 0)}</td>"
                f"<td>{html.escape(str(ce.get('utterance', '')))}</td>"
                f"<td>{html.escape(str(ce.get('question', '')))}</td>"
                f"<td>{'yes' if bool(ce.get('pending')) else 'no'}</td>"
                f"<td><pre>{html.escape(chr(10).join(rounds_text) if rounds_text else '(none)')}</pre></td>"
                "</tr>"
            )
        if not ce_html_rows:
            ce_html_rows.append("<tr><td colspan='5'>No clarification events.</td></tr>")

        best_section = f"""
<div class='card'>
  <h2>Best Run Detail</h2>
  <ul>
    <li>Run: <code>{html.escape(str(best_row.get("run_id", "")))}</code></li>
    <li>Split mode: <code>{html.escape(str(best_row.get("split_mode", "")))}</code></li>
    <li>Temporal dual-write: <code>{'on' if bool(best_row.get("temporal_dual_write")) else 'off'}</code></li>
    <li>Final score: <strong>{float(best_row.get("final_score", 0.0) or 0.0):.3f}</strong></li>
    <li>KB path: <code>{html.escape(str(best_row.get("kb_path", "")))}</code></li>
    <li>KB clause lines: <code>{kb_line_count}</code></li>
    <li>KB clause count: <code>{int(best_row.get("kb_clause_count", 0) or 0)}</code></li>
    <li>KB density ratio: <code>{float(best_row.get("kb_clause_coverage_ratio", 0.0) or 0.0):.3f}</code></li>
    <li>Exam question ratio: <code>{float(best_row.get("exam_question_count_ratio", 0.0) or 0.0):.3f}</code></li>
  </ul>
</div>

<div class='card'>
  <h2>2) Generated KB.pl (Best Run)</h2>
  <pre>{html.escape(kb_text)}</pre>
</div>

<div class='card'>
  <h2>3) Interrogation Exam (Best Run)</h2>
  <table>
    <thead><tr><th>ID</th><th>Question</th><th>Query</th><th>Pass</th><th>Status</th><th>Answer Preview</th></tr></thead>
    <tbody>
      {''.join(exam_html_rows)}
    </tbody>
  </table>
</div>

<div class='card'>
  <h2>4) Clarification Engine Dialog (Best Run)</h2>
  <table>
    <thead><tr><th>Turn</th><th>Utterance</th><th>Question</th><th>Pending</th><th>Rounds</th></tr></thead>
    <tbody>
      {''.join(ce_html_rows)}
    </tbody>
  </table>
</div>
"""

    html_doc = f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width, initial-scale=1'/>
<title>{html.escape(title)}</title>
<style>
body {{ font-family: ui-sans-serif,Segoe UI,Arial; margin:24px; background:#0f1720; color:#e6edf3; }}
.card {{ background:#151f2b; border:1px solid #2b3b4d; border-radius:12px; padding:16px; margin:14px 0; }}
pre {{ white-space:pre-wrap; background:#0b1118; border:1px solid #243447; padding:12px; border-radius:8px; }}
code {{ background:#0b1118; padding:2px 4px; border-radius:4px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ border:1px solid #2b3b4d; padding:8px; vertical-align:top; }}
th {{ background:#1b2735; text-align:left; }}
.small {{ color:#9fb3c8; font-size:12px; }}
.score {{ font-size:30px; font-weight:700; }}
</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
<div class='small'>Generated: {generated}</div>

<div class='card'>
  <h2>1) Raw Blob Handed to Prethinker</h2>
  <div class='small'>Source: {html.escape(str(story_path))}</div>
  <pre>{html.escape(story_text)}</pre>
</div>

<div class='card'>
  <h2>Run Matrix Scoreboard</h2>
  <table>
    <thead>
      <tr>
        <th>Run</th><th>Split</th><th>Temporal</th><th>Pipeline</th><th>Parse Fails</th><th>Apply Fails</th><th>CE Req</th>
        <th>Coverage</th><th>Precision</th><th>Exam</th><th>Temporal Exam</th><th>KB Density</th><th>Exam Q Ratio</th><th>Final Score</th>
      </tr>
    </thead>
    <tbody>{''.join(table_rows)}</tbody>
  </table>
</div>

{best_section}
</body>
</html>
"""
    output_path.write_text(html_doc, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="Run raw story stress cycle and emit summary artifacts.")
    p.add_argument("--story-file", required=True)
    p.add_argument("--label", default="", help="Optional custom label for artifact names.")
    p.add_argument("--modes", default="full,paragraph,line", help="Comma-separated split modes.")
    p.add_argument("--temporal", default="off,on", help="Comma-separated: off,on.")
    p.add_argument("--backend", default="ollama")
    p.add_argument("--base-url", default="http://127.0.0.1:11434")
    p.add_argument("--model", default="qwen3.5:9b")
    p.add_argument("--prompt-file", default="modelfiles/semantic_parser_system_prompt.md")
    p.add_argument("--context-length", type=int, default=8192)
    p.add_argument("--clarification-eagerness", type=float, default=0.2)
    p.add_argument("--clarification-eagerness-mode", choices=["adaptive", "static"], default="static")
    p.add_argument("--clarification-eagerness-new-kb-boost", type=float, default=0.35)
    p.add_argument("--clarification-eagerness-existing-kb-boost", type=float, default=0.05)
    p.add_argument("--clarification-eagerness-decay-turns", type=int, default=8)
    p.add_argument("--clarification-eagerness-decay-clauses", type=int, default=20)
    p.add_argument("--max-clarification-rounds", type=int, default=2)
    p.add_argument("--clarification-answer-min-confidence", type=float, default=0.0)
    p.add_argument("--frontend-proposal-mode", choices=["off", "shadow", "active"], default="off")
    p.add_argument("--predicate-registry", default="")
    p.add_argument("--strict-registry", action="store_true")
    p.add_argument("--type-schema", default="")
    p.add_argument("--temporal-predicate", default="at_step")
    p.add_argument("--exam-style", choices=["general", "detective", "medical"], default="detective")
    p.add_argument("--exam-question-count", type=int, default=14)
    p.add_argument("--exam-min-temporal-questions", type=int, default=2)
    p.add_argument("--summary-json", default="", help="Optional output path.")
    p.add_argument("--summary-md", default="", help="Optional output path.")
    p.add_argument("--report-html", default="", help="Optional output path.")
    p.add_argument(
        "--write-latest-alias",
        action="store_true",
        default=True,
        help="Also write docs/reports/<label>-stress-latest.html when report target is in docs/reports.",
    )
    args = p.parse_args()

    story_path = Path(args.story_file)
    if not story_path.is_absolute():
        story_path = (ROOT / story_path).resolve()
    if not story_path.exists():
        print(f"[story-stress] missing story file: {story_path}", file=sys.stderr)
        return 2

    modes = _resolve_modes(args.modes, {"full", "paragraph", "line"})
    temporal_modes = _resolve_temporal_modes(args.temporal)
    if not modes:
        print("[story-stress] no valid split modes selected", file=sys.stderr)
        return 3
    if not temporal_modes:
        print("[story-stress] no valid temporal modes selected", file=sys.stderr)
        return 4

    stamp = _utc_stamp()
    label = _slug(args.label.strip() or story_path.stem)
    summary_json = (
        Path(args.summary_json).resolve()
        if str(args.summary_json).strip()
        else (ROOT / "tmp" / f"{label}_stress_{stamp}.summary.json")
    )
    summary_md = (
        Path(args.summary_md).resolve()
        if str(args.summary_md).strip()
        else (ROOT / "tmp" / f"{label}_stress_{stamp}.summary.md")
    )
    report_html = (
        Path(args.report_html).resolve()
        if str(args.report_html).strip()
        else (ROOT / "docs" / "reports" / f"{label}-stress-{stamp}.html")
    )

    story_text = story_path.read_text(encoding="utf-8-sig", errors="replace")
    story_char_count = len(story_text)
    expected_min_clauses = max(1, min(120, int(story_char_count / 700)))
    requested_exam_questions = max(1, int(args.exam_question_count))
    rows: list[dict[str, Any]] = []
    run_order = [(mode, temporal) for mode in modes for temporal in temporal_modes]

    for index, (mode, temporal_on) in enumerate(run_order, start=1):
        run_id = f"raw_{label}_{mode}_{'temporal' if temporal_on else 'plain'}_{stamp}"
        scenario_out = ROOT / "tmp" / "scenarios" / f"{run_id}.json"
        pipeline_out = ROOT / "tmp" / f"{run_id}.pipeline.json"
        interrogator_out = ROOT / "tmp" / f"{run_id}.interrogator.json"
        cmd = [
            sys.executable,
            str(RUN_STORY_RAW),
            "--story-file",
            str(story_path),
            "--scenario-name",
            run_id,
            "--scenario-out",
            str(scenario_out),
            "--pipeline-out",
            str(pipeline_out),
            "--backend",
            str(args.backend),
            "--base-url",
            str(args.base_url),
            "--model",
            str(args.model),
            "--prompt-file",
            str(args.prompt_file),
            "--context-length",
            str(int(args.context_length)),
            "--split-mode",
            mode,
            "--clarification-eagerness",
            str(float(args.clarification_eagerness)),
            "--clarification-eagerness-mode",
            str(args.clarification_eagerness_mode),
            "--clarification-eagerness-new-kb-boost",
            str(float(args.clarification_eagerness_new_kb_boost)),
            "--clarification-eagerness-existing-kb-boost",
            str(float(args.clarification_eagerness_existing_kb_boost)),
            "--clarification-eagerness-decay-turns",
            str(int(args.clarification_eagerness_decay_turns)),
            "--clarification-eagerness-decay-clauses",
            str(int(args.clarification_eagerness_decay_clauses)),
            "--max-clarification-rounds",
            str(int(args.max_clarification_rounds)),
            "--clarification-answer-model",
            str(args.model),
            "--clarification-answer-backend",
            str(args.backend),
            "--clarification-answer-base-url",
            str(args.base_url),
            "--clarification-answer-context-length",
            str(int(args.context_length)),
            "--clarification-answer-min-confidence",
            str(float(args.clarification_answer_min_confidence)),
            "--frontend-proposal-mode",
            str(args.frontend_proposal_mode),
            "--temporal-predicate",
            str(args.temporal_predicate),
            "--exam-style",
            str(args.exam_style),
            "--exam-question-count",
            str(int(args.exam_question_count)),
            "--exam-min-temporal-questions",
            str(int(args.exam_min_temporal_questions)),
            "--write-corpus-on-fail",
            "--run-interrogator",
            "--run-interrogator-on-fail",
        ]
        if temporal_on:
            cmd.append("--temporal-dual-write")
        if str(args.predicate_registry).strip():
            cmd.extend(["--predicate-registry", str(args.predicate_registry)])
        if bool(args.strict_registry):
            cmd.append("--strict-registry")
        if str(args.type_schema).strip():
            cmd.extend(["--type-schema", str(args.type_schema)])

        print(f"[story-stress {index}/{len(run_order)}] run={run_id}")
        proc = subprocess.run(cmd, cwd=str(ROOT), check=False)

        pipeline_report = _load_json(pipeline_out) if pipeline_out.exists() else {}
        interrogator_report = _load_json(interrogator_out) if interrogator_out.exists() else {}

        fact_audit = interrogator_report.get("fact_audit") if isinstance(interrogator_report.get("fact_audit"), dict) else {}
        exam = interrogator_report.get("exam") if isinstance(interrogator_report.get("exam"), dict) else {}
        kb_path = _resolve_kb_path(pipeline_report)
        kb_preview, kb_line_count, kb_clause_count = (
            _read_kb_preview(kb_path) if isinstance(kb_path, Path) and kb_path.exists() else ("", 0, 0)
        )
        exam_question_count = int(exam.get("question_count", 0) or 0)
        exam_question_count_ratio = min(1.0, float(exam_question_count) / float(requested_exam_questions))
        kb_clause_coverage_ratio = min(1.0, float(kb_clause_count) / float(expected_min_clauses))

        row: dict[str, Any] = {
            "run_id": run_id,
            "split_mode": mode,
            "temporal_dual_write": bool(temporal_on),
            "exit_code": int(proc.returncode),
            "scenario_path": str(scenario_out),
            "pipeline_output": str(pipeline_out),
            "interrogator_output": str(interrogator_out),
            "pipeline_status": str(pipeline_report.get("overall_status", "missing")),
            "parse_failures": int(pipeline_report.get("turn_parse_failures", 0) or 0),
            "apply_failures": int(pipeline_report.get("turn_apply_failures", 0) or 0),
            "clarification_requests": int(pipeline_report.get("turns_clarification_requested", 0) or 0),
            "clarification_rounds_total": int(pipeline_report.get("clarification_rounds_total", 0) or 0),
            "coverage": float(fact_audit.get("coverage_score", 0.0) or 0.0),
            "precision": float(fact_audit.get("precision_score", 0.0) or 0.0),
            "exam_pass_rate": float(exam.get("pass_rate", 0.0) or 0.0),
            "temporal_exam_pass_rate": float(exam.get("temporal_pass_rate", 0.0) or 0.0),
            "exam_pass_count": int(exam.get("pass_count", 0) or 0),
            "exam_question_count": exam_question_count,
            "exam_question_count_ratio": exam_question_count_ratio,
            "kb_path": str(kb_path) if isinstance(kb_path, Path) else "",
            "kb_line_count": kb_line_count,
            "kb_clause_count": kb_clause_count,
            "kb_clause_coverage_ratio": kb_clause_coverage_ratio,
            "kb_preview": kb_preview,
            "exam_questions": exam.get("questions", []) if isinstance(exam.get("questions"), list) else [],
            "ce_rows": _extract_ce_rows(pipeline_report),
        }
        row["final_score"] = _score_row(
            row,
            requested_exam_questions=requested_exam_questions,
            story_char_count=story_char_count,
        )
        rows.append(row)

    rows_sorted = sorted(rows, key=lambda r: float(r.get("final_score", 0.0) or 0.0), reverse=True)
    best_row = rows_sorted[0] if rows_sorted else None

    summary = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "story_file": str(story_path),
        "label": label,
        "settings": {
            "backend": args.backend,
            "base_url": args.base_url,
            "model": args.model,
            "prompt_file": str(args.prompt_file),
            "context_length": int(args.context_length),
            "modes": modes,
            "temporal_modes": ["on" if x else "off" for x in temporal_modes],
            "clarification_eagerness": float(args.clarification_eagerness),
            "clarification_eagerness_mode": str(args.clarification_eagerness_mode),
            "clarification_eagerness_new_kb_boost": float(args.clarification_eagerness_new_kb_boost),
            "clarification_eagerness_existing_kb_boost": float(args.clarification_eagerness_existing_kb_boost),
            "clarification_eagerness_decay_turns": int(args.clarification_eagerness_decay_turns),
            "clarification_eagerness_decay_clauses": int(args.clarification_eagerness_decay_clauses),
            "max_clarification_rounds": int(args.max_clarification_rounds),
            "clarification_answer_min_confidence": float(args.clarification_answer_min_confidence),
            "frontend_proposal_mode": str(args.frontend_proposal_mode),
            "temporal_predicate": str(args.temporal_predicate),
            "predicate_registry": str(args.predicate_registry),
            "strict_registry": bool(args.strict_registry),
            "type_schema": str(args.type_schema),
            "exam_style": str(args.exam_style),
            "exam_question_count": int(args.exam_question_count),
            "exam_min_temporal_questions": int(args.exam_min_temporal_questions),
            "story_char_count": int(story_char_count),
            "expected_min_clauses": int(expected_min_clauses),
        },
        "run_count": len(rows),
        "pipeline_pass_count": sum(1 for r in rows if str(r.get("pipeline_status", "")).lower() == "passed"),
        "avg_coverage": round(
            sum(float(r.get("coverage", 0.0) or 0.0) for r in rows) / len(rows), 6
        )
        if rows
        else 0.0,
        "avg_precision": round(
            sum(float(r.get("precision", 0.0) or 0.0) for r in rows) / len(rows), 6
        )
        if rows
        else 0.0,
        "avg_exam_pass_rate": round(
            sum(float(r.get("exam_pass_rate", 0.0) or 0.0) for r in rows) / len(rows), 6
        )
        if rows
        else 0.0,
        "avg_temporal_exam_pass_rate": round(
            sum(float(r.get("temporal_exam_pass_rate", 0.0) or 0.0) for r in rows) / len(rows), 6
        )
        if rows
        else 0.0,
        "best_run_id": str(best_row.get("run_id")) if isinstance(best_row, dict) else "",
        "best_final_score": float(best_row.get("final_score", 0.0) or 0.0) if isinstance(best_row, dict) else 0.0,
        "rows": rows,
    }

    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Story Stress Summary",
        "",
        f"- Story file: `{story_path}`",
        f"- Runs: `{len(rows)}`",
        f"- Pipeline pass: `{summary['pipeline_pass_count']}/{len(rows)}`",
        f"- Avg coverage: `{summary['avg_coverage']}`",
        f"- Avg precision: `{summary['avg_precision']}`",
        f"- Avg exam pass: `{summary['avg_exam_pass_rate']}`",
        f"- Avg temporal exam pass: `{summary['avg_temporal_exam_pass_rate']}`",
        f"- Best run: `{summary['best_run_id']}` (`{summary['best_final_score']}`)",
        f"- Story chars: `{story_char_count}`",
        f"- Expected minimum clauses (density guard): `{expected_min_clauses}`",
        "",
        "| Run | Split | Temporal | Pipeline | Coverage | Precision | Exam | Temporal Exam | KB Density | Exam Q Ratio | Final Score |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows_sorted:
        lines.append(
            "| "
            + f"`{row.get('run_id','')}` | "
            + f"`{row.get('split_mode','')}` | "
            + f"`{'on' if bool(row.get('temporal_dual_write')) else 'off'}` | "
            + f"`{row.get('pipeline_status','')}` | "
            + f"{float(row.get('coverage',0.0) or 0.0):.3f} | "
            + f"{float(row.get('precision',0.0) or 0.0):.3f} | "
            + f"{float(row.get('exam_pass_rate',0.0) or 0.0):.3f} | "
            + f"{float(row.get('temporal_exam_pass_rate',0.0) or 0.0):.3f} | "
            + f"{float(row.get('kb_clause_coverage_ratio',0.0) or 0.0):.3f} | "
            + f"{float(row.get('exam_question_count_ratio',0.0) or 0.0):.3f} | "
            + f"{float(row.get('final_score',0.0) or 0.0):.3f} |"
        )
    summary_md.parent.mkdir(parents=True, exist_ok=True)
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    _render_html_report(
        title=f"Raw Story Stress Audit - {label}",
        story_path=story_path,
        story_text=story_text,
        rows=rows_sorted,
        best_row=best_row,
        output_path=report_html,
    )

    latest_alias_path: Path | None = None
    reports_dir = (ROOT / "docs" / "reports").resolve()
    if bool(args.write_latest_alias) and report_html.parent.resolve() == reports_dir:
        latest_alias_path = reports_dir / f"{label}-stress-latest.html"
        shutil.copyfile(report_html, latest_alias_path)

    print(f"[story-stress] summary_json={summary_json}")
    print(f"[story-stress] summary_md={summary_md}")
    print(f"[story-stress] report_html={report_html}")
    if isinstance(latest_alias_path, Path):
        print(f"[story-stress] report_html_latest={latest_alias_path}")
    if isinstance(best_row, dict):
        print(
            "[story-stress] best",
            f"run={best_row.get('run_id')}",
            f"score={best_row.get('final_score')}",
            f"pipeline={best_row.get('pipeline_status')}",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
