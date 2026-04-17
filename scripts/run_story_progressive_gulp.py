#!/usr/bin/env python3
"""
Progressive gulp runner for dense raw-story ingestion.

Purpose:
- ingest a single raw story in increasing chunks,
- keep one cumulative KB namespace across stages,
- run interrogator at each stage,
- verify earlier-stage exams still pass at later stages,
- emit machine and human artifacts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_STORY_RAW = ROOT / "scripts" / "run_story_raw.py"
KB_STORE_ROOT = ROOT / "kb_store"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str((ROOT / "scripts").resolve()) not in sys.path:
    sys.path.insert(0, str((ROOT / "scripts").resolve()))

import kb_interrogator as ki  # noqa: E402

try:
    from story_registry_guard import registry_profile_mismatch_message  # noqa: E402
except ImportError:  # pragma: no cover - import path differs for package-style test imports
    from scripts.story_registry_guard import registry_profile_mismatch_message  # noqa: E402


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
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


_CRITICAL_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "by",
    "did",
    "for",
    "from",
    "had",
    "has",
    "have",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "then",
    "there",
    "they",
    "this",
    "to",
    "under",
    "was",
    "were",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
    "yes",
}
ENGLISH_STRICT_GATE_DEFAULTS = {
    "coverage": 0.85,
    "precision": 0.90,
    "exam_pass_rate": 0.80,
    "temporal_pass_rate": 0.70,
    "critical_pass_rate": 0.70,
    "carry_pass_rate": 0.80,
}
MULTILINGUAL_EXPERIMENTAL_GATES = {
    "coverage": 0.72,
    "precision": 0.80,
    "exam_pass_rate": 0.65,
    "temporal_pass_rate": 0.55,
    "critical_pass_rate": 0.55,
    "carry_pass_rate": 0.65,
}
LANGUAGE_PROFILE_MARKERS_FOREIGN = {
    "estaba",
    "estaban",
    "fue",
    "ayer",
    "hoy",
    "manana",
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "septiembre",
    "noviembre",
    "madre",
    "padre",
    "hermano",
    "hermana",
    "contable",
    "terrenos",
    "invernadero",
    "asistente",
    "interina",
    "superavit",
    "clausulas",
    "reunion",
    "premio",
    "juvenil",
    "gano",
    "tenia",
    "dirigia",
    "planificadora",
    "nao",
    "filho",
    "filha",
    "mae",
    "etait",
    "frere",
    "soeur",
    "gestern",
    "heute",
    "vater",
    "mutter",
}
LANGUAGE_PROFILE_MARKERS_ENGLISH = {"the", "is", "are", "was", "were", "and", "with", "from", "someone"}


def _resolve_percentages(raw: str) -> list[int]:
    out: list[int] = []
    for part in str(raw or "").split(","):
        token = part.strip()
        if not token:
            continue
        try:
            value = int(float(token))
        except (TypeError, ValueError):
            continue
        value = max(1, min(100, value))
        if value not in out:
            out.append(value)
    if 100 not in out:
        out.append(100)
    out = sorted(out)
    return out or [10, 25, 50, 100]


def _fold_text_ascii(text: str) -> str:
    import unicodedata

    raw = str(text or "")
    if not raw:
        return ""
    normalized = unicodedata.normalize("NFKD", raw)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _detect_story_language_profile(raw_text: str) -> dict[str, Any]:
    text = str(raw_text or "")
    letters = [ch for ch in text if ch.isalpha()]
    non_ascii_letters = sum(1 for ch in letters if ord(ch) > 127)
    non_ascii_ratio = non_ascii_letters / max(1, len(letters))

    lowered_folded = _fold_text_ascii(text).lower()
    words = re.findall(r"[a-z][a-z0-9_'-]*", lowered_folded)
    english_hits = sum(1 for token in words if token in LANGUAGE_PROFILE_MARKERS_ENGLISH)
    foreign_hits = sum(1 for token in words if token in LANGUAGE_PROFILE_MARKERS_FOREIGN)

    profile = "english"
    confidence = 0.62
    if foreign_hits >= 2 and english_hits == 0:
        profile = "non_english"
        confidence = 0.87
    elif non_ascii_ratio >= 0.18 and foreign_hits >= 1 and english_hits == 0:
        profile = "non_english"
        confidence = 0.84
    elif foreign_hits >= 2 and english_hits >= 1:
        profile = "mixed"
        confidence = 0.81
    elif foreign_hits >= 1 and english_hits >= 10:
        profile = "mixed"
        confidence = 0.72
    elif non_ascii_ratio >= 0.10 and (foreign_hits >= 1 or english_hits >= 1):
        profile = "mixed"
        confidence = 0.74
    elif foreign_hits >= 1 and english_hits == 0:
        profile = "mixed"
        confidence = 0.68

    return {
        "profile": profile,
        "confidence": round(float(confidence), 3),
        "marker_hits_foreign": int(foreign_hits),
        "marker_hits_english": int(english_hits),
        "non_ascii_ratio": round(float(non_ascii_ratio), 3),
    }


def _resolve_gate_value(*, requested: float, english_default: float, profile_default: float) -> float:
    value = float(requested)
    if abs(value - float(english_default)) < 1e-9:
        return float(profile_default)
    return value


def _split_story(raw_text: str, *, split_mode: str) -> list[str]:
    source = str(raw_text or "")
    if split_mode == "full":
        return [source] if source.strip() else []
    if split_mode == "paragraph":
        blocks = source.replace("\r\n", "\n").replace("\r", "\n").split("\n\n")
        return [b for b in blocks if b.strip()]
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return [ln for ln in lines if ln.strip()]


def _sentence_lines_from_text(raw_text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", str(raw_text or "").strip())
    if not compact:
        return []
    parts = re.split(r"(?<=[.!?])\s+", compact)
    rows = [p.strip() for p in parts if p and p.strip()]
    return rows or [compact]


def _slice_units(units: list[str], pct: int) -> list[str]:
    if not units:
        return []
    total = len(units)
    take = max(1, int(round(total * (float(pct) / 100.0))))
    take = min(total, take)
    return units[:take]


def _stage_text_from_units(units: list[str], *, split_mode: str) -> str:
    if not units:
        return ""
    mode = str(split_mode).strip().lower()
    if mode == "paragraph":
        return "\n\n".join(units)
    if mode == "line":
        return "\n".join(units)
    return "\n".join(units)


def _resolve_kb_path(report: dict[str, Any], kb_name: str) -> Path:
    ns = report.get("kb_namespace")
    if isinstance(ns, dict):
        corpus_path = ns.get("corpus_path")
        if isinstance(corpus_path, str) and corpus_path.strip():
            p = Path(corpus_path.strip())
            return p if p.is_absolute() else (ROOT / p).resolve()
        kb_dir = ns.get("kb_dir")
        if isinstance(kb_dir, str) and kb_dir.strip():
            base = Path(kb_dir.strip())
            base = base if base.is_absolute() else (ROOT / base).resolve()
            return base / "kb.pl"
    return (ROOT / "kb_store" / kb_name / "kb.pl").resolve()


def _kb_dir_for_name(kb_name: str) -> Path:
    return (KB_STORE_ROOT / str(kb_name or "").strip()).resolve()


def _copy_kb_state(*, src_kb_name: str, dst_kb_name: str) -> None:
    src = _kb_dir_for_name(src_kb_name)
    dst = _kb_dir_for_name(dst_kb_name)
    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    if src.exists():
        shutil.copytree(src, dst)
    else:
        dst.mkdir(parents=True, exist_ok=True)


def _promote_kb_state(*, src_kb_name: str, dst_kb_name: str) -> None:
    _copy_kb_state(src_kb_name=src_kb_name, dst_kb_name=dst_kb_name)


def _summarize_ce(pipeline_report: dict[str, Any]) -> list[dict[str, Any]]:
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
        pending = bool(turn.get("clarification_pending", False))
        if not question and not rounds and not pending:
            continue
        rows.append(
            {
                "turn_index": int(turn.get("turn_index", 0) or 0),
                "utterance": str(turn.get("utterance_original") or turn.get("utterance") or "").strip(),
                "question": question,
                "pending": pending,
                "rounds": [
                    {
                        "round": int(r.get("round", 0) or 0),
                        "question": str(r.get("question") or "").strip(),
                        "answer": str(r.get("answer") or "").strip(),
                        "answer_source": str(r.get("answer_source") or "").strip(),
                    }
                    for r in rounds
                    if isinstance(r, dict)
                ],
            }
        )
    return rows


def _evaluate_question_pack(kb_path: Path, questions: list[dict[str, Any]]) -> dict[str, Any]:
    runtime, _, _ = ki._build_runtime_from_kb(kb_path)  # type: ignore[attr-defined]
    eval_report = ki._evaluate_questions(runtime, questions)  # type: ignore[attr-defined]
    return {
        "pass_count": int(eval_report.get("pass_count", 0) or 0),
        "question_count": int(eval_report.get("question_count", 0) or 0),
        "pass_rate": float(eval_report.get("pass_rate", 0.0) or 0.0),
        "temporal_pass_count": int(eval_report.get("temporal_pass_count", 0) or 0),
        "temporal_question_count": int(eval_report.get("temporal_question_count", 0) or 0),
        "temporal_pass_rate": float(eval_report.get("temporal_pass_rate", 0.0) or 0.0),
    }


def _normalize_words(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", str(text or "").lower())
    out: set[str] = set()
    for token in tokens:
        if token in _CRITICAL_STOPWORDS:
            continue
        if len(token) <= 1 and not token.isdigit():
            continue
        out.add(token)
    return out


def _extract_anchor_tokens(expected: str) -> set[str]:
    raw = str(expected or "").strip()
    if not raw:
        return set()

    anchors: set[str] = set()
    for token in re.findall(r"\b[A-Z][a-zA-Z0-9_']*\b", raw):
        norm = re.sub(r"[^a-z0-9]+", "", token.lower())
        if norm and norm not in _CRITICAL_STOPWORDS:
            anchors.add(norm)
    for token in re.findall(r"\b\d+\b", raw):
        anchors.add(token)

    if anchors:
        return anchors
    fallback = _normalize_words(raw)
    constrained = {tok for tok in fallback if tok.isdigit() or "_" in tok or "-" in tok}
    if constrained:
        return set(sorted(constrained)[:4])
    return set()


def _parse_critical_checks_from_pack(pack_markdown_path: Path, *, max_items: int = 30) -> list[dict[str, str]]:
    if not pack_markdown_path.exists():
        return []
    text = pack_markdown_path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()

    in_exam = False
    table_rows: list[str] = []
    for raw in lines:
        line = str(raw or "")
        stripped = line.strip()
        if stripped.lower().startswith("## ") and "exam battery" in stripped.lower():
            in_exam = True
            continue
        if in_exam and stripped.lower().startswith("## "):
            break
        if in_exam and stripped.startswith("|"):
            table_rows.append(stripped)

    if len(table_rows) < 3:
        return []

    checks: list[dict[str, str]] = []
    for row in table_rows[2:]:
        cols = [c.strip() for c in row.strip("|").split("|")]
        if len(cols) < 3:
            continue
        check_id, question, expected = cols[0], cols[1], cols[2]
        if not expected:
            continue
        checks.append(
            {
                "id": str(check_id or f"q{len(checks)+1}").strip(),
                "question": str(question).strip(),
                "expected": str(expected).strip(),
            }
        )
        if len(checks) >= max_items:
            break
    return checks


def _evaluate_critical_checks(
    kb_path: Path,
    checks: list[dict[str, str]],
    *,
    source_text: str = "",
) -> dict[str, Any]:
    if not checks:
        return {"check_count": 0, "pass_count": 0, "pass_rate": 0.0, "checks": []}
    if not kb_path.exists():
        return {"check_count": len(checks), "pass_count": 0, "pass_rate": 0.0, "checks": []}

    kb_text = kb_path.read_text(encoding="utf-8", errors="replace")
    kb_tokens = _normalize_words(kb_text)
    source_tokens = _normalize_words(source_text)
    rows: list[dict[str, Any]] = []
    pass_count = 0
    active_count = 0
    for check in checks:
        expected = str(check.get("expected", "")).strip()
        expected_tokens = _extract_anchor_tokens(expected)

        if not expected_tokens:
            rows.append(
                {
                    "id": str(check.get("id", "")).strip(),
                    "question": str(check.get("question", "")).strip(),
                    "expected": expected,
                    "expected_tokens": [],
                    "active": False,
                    "passed": None,
                    "missing_tokens": [],
                }
            )
            continue

        is_active = True
        if source_tokens and expected_tokens:
            is_active = expected_tokens.issubset(source_tokens)
        if not is_active:
            rows.append(
                {
                    "id": str(check.get("id", "")).strip(),
                    "question": str(check.get("question", "")).strip(),
                    "expected": expected,
                    "expected_tokens": sorted(expected_tokens),
                    "active": False,
                    "passed": None,
                    "missing_tokens": [],
                }
            )
            continue

        active_count += 1
        passed = bool(expected_tokens) and expected_tokens.issubset(kb_tokens)
        if passed:
            pass_count += 1
        missing = sorted(expected_tokens - kb_tokens) if expected_tokens else []
        rows.append(
            {
                "id": str(check.get("id", "")).strip(),
                "question": str(check.get("question", "")).strip(),
                "expected": expected,
                "expected_tokens": sorted(expected_tokens),
                "active": True,
                "passed": passed,
                "missing_tokens": missing,
            }
        )
    total = active_count
    return {
        "check_count": total,
        "pass_count": pass_count,
        "pass_rate": float(pass_count / total) if total else 0.0,
        "checks": rows,
    }


def _render_html(
    *,
    title: str,
    source_story_path: Path,
    source_story_text: str,
    stage_rows: list[dict[str, Any]],
    out_path: Path,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    stage_cards: list[str] = []
    for row in stage_rows:
        ce = row.get("ce_summary", [])
        if not isinstance(ce, list):
            ce = []
        ce_lines: list[str] = []
        for item in ce[:20]:
            if not isinstance(item, dict):
                continue
            q = str(item.get("question", "")).strip()
            ce_lines.append(f"turn {int(item.get('turn_index', 0) or 0)} | q={q or '(none)'}")
            rounds = item.get("rounds")
            if isinstance(rounds, list):
                for rr in rounds:
                    if not isinstance(rr, dict):
                        continue
                    ce_lines.append(
                        f"  r{int(rr.get('round', 0) or 0)} | {rr.get('question','')} -> {rr.get('answer','')}"
                    )
        if not ce_lines:
            ce_lines = ["(none)"]

        carry_rows = row.get("carry_forward", [])
        if not isinstance(carry_rows, list):
            carry_rows = []
        carry_html = []
        for c in carry_rows:
            if not isinstance(c, dict):
                continue
            carry_html.append(
                "<tr>"
                f"<td>{html.escape(str(c.get('from_stage', '')))}</td>"
                f"<td>{int(c.get('pass_count', 0) or 0)}/{int(c.get('question_count', 0) or 0)}</td>"
                f"<td>{float(c.get('pass_rate', 0.0) or 0.0):.3f}</td>"
                "</tr>"
            )
        if not carry_html:
            carry_html = ["<tr><td colspan='3'>(none)</td></tr>"]

        kb_preview = str(row.get("kb_preview", "") or "")
        stage_cards.append(
            f"""
<div class="card">
  <h2>Stage {int(row.get("stage_index", 0) or 0)} - {int(row.get("pct", 0) or 0)}%</h2>
  <ul>
    <li>Stage text: <code>{html.escape(str(row.get("stage_story_path", "")))}</code></li>
    <li>Pipeline: <code>{html.escape(str(row.get("pipeline_status", "")))}</code> (parse={int(row.get("parse_failures", 0) or 0)}, apply={int(row.get("apply_failures", 0) or 0)})</li>
    <li>Gate: <code>{'pass' if bool(row.get('gate_passed')) else 'fail'}</code></li>
    <li>Gate failures: <code>{html.escape(','.join(str(x) for x in row.get('gate_failures', []) if str(x).strip()) or '(none)')}</code></li>
    <li>Interrogator coverage/precision: <code>{float(row.get("coverage", 0.0) or 0.0):.3f}</code> / <code>{float(row.get("precision", 0.0) or 0.0):.3f}</code></li>
    <li>Stage exam pass: <code>{int(row.get("exam_pass_count", 0) or 0)}/{int(row.get("exam_question_count", 0) or 0)}</code></li>
    <li>Temporal exam pass: <code>{int(row.get("temporal_exam_pass_count", 0) or 0)}/{int(row.get("temporal_exam_question_count", 0) or 0)}</code></li>
    <li>Critical exam pass: <code>{int(row.get("critical_exam_pass_count", 0) or 0)}/{int(row.get("critical_exam_check_count", 0) or 0)}</code></li>
    <li>KB path: <code>{html.escape(str(row.get("kb_path", "")))}</code></li>
    <li>KB clause count: <code>{int(row.get("kb_clause_count", 0) or 0)}</code></li>
    <li>Recovery used: <code>{'yes' if bool(row.get('recovery_used', False)) else 'no'}</code></li>
    <li>Recovery trigger: <code>{html.escape(str(row.get('recovery_trigger', 'none')))}</code></li>
  </ul>
  <h3>KB Preview</h3>
  <pre>{html.escape(kb_preview)}</pre>
  <h3>Carry-Forward (Earlier Exams Replayed On Current KB)</h3>
  <table>
    <thead><tr><th>From Stage</th><th>Pass</th><th>Rate</th></tr></thead>
    <tbody>{''.join(carry_html)}</tbody>
  </table>
  <h3>CE Dialog Summary</h3>
  <pre>{html.escape(chr(10).join(ce_lines))}</pre>
</div>
"""
        )

    matrix_rows: list[str] = []
    for row in stage_rows:
        matrix_rows.append(
            "<tr>"
            f"<td>{int(row.get('stage_index', 0) or 0)}</td>"
            f"<td>{int(row.get('pct', 0) or 0)}%</td>"
            f"<td><code>{html.escape(str(row.get('pipeline_status', '')))}</code></td>"
            f"<td><code>{'pass' if bool(row.get('gate_passed')) else 'fail'}</code></td>"
            f"<td>{float(row.get('coverage', 0.0) or 0.0):.3f}</td>"
            f"<td>{float(row.get('precision', 0.0) or 0.0):.3f}</td>"
            f"<td>{int(row.get('exam_pass_count', 0) or 0)}/{int(row.get('exam_question_count', 0) or 0)}</td>"
            f"<td>{int(row.get('temporal_exam_pass_count', 0) or 0)}/{int(row.get('temporal_exam_question_count', 0) or 0)}</td>"
            f"<td>{int(row.get('critical_exam_pass_count', 0) or 0)}/{int(row.get('critical_exam_check_count', 0) or 0)}</td>"
            f"<td>{int(row.get('kb_clause_count', 0) or 0)}</td>"
            "</tr>"
        )

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
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
</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
<div class="small">Generated: {generated}</div>

<div class="card">
  <h2>Raw Story Input</h2>
  <div class="small">Source: {html.escape(str(source_story_path))}</div>
  <pre>{html.escape(source_story_text)}</pre>
</div>

<div class="card">
  <h2>Stage Matrix</h2>
  <table>
    <thead><tr><th>Stage</th><th>Gulp</th><th>Pipeline</th><th>Gate</th><th>Coverage</th><th>Precision</th><th>Exam</th><th>Temporal Exam</th><th>Critical Exam</th><th>KB Clauses</th></tr></thead>
    <tbody>{''.join(matrix_rows)}</tbody>
  </table>
</div>

{''.join(stage_cards)}
</body>
</html>
"""
    out_path.write_text(html_doc, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="Progressive gulp runner for dense story ingestion.")
    p.add_argument("--story-file", required=True)
    p.add_argument("--label", default="")
    p.add_argument("--percentages", default="10,25,50,75,100", help="Comma-separated stage percentages.")
    p.add_argument("--split-mode", choices=["full", "paragraph", "line"], default="paragraph")
    p.add_argument(
        "--auto-fallback-split",
        action="store_true",
        default=True,
        help="When selected split yields too few units for staging, fallback to line split.",
    )
    p.add_argument("--backend", default="ollama")
    p.add_argument("--base-url", default="http://127.0.0.1:11434")
    p.add_argument("--model", default="qwen3.5:9b")
    p.add_argument("--prompt-file", default="modelfiles/semantic_parser_system_prompt.md")
    p.add_argument("--context-length", type=int, default=8192)
    p.add_argument("--predicate-registry", default="")
    p.add_argument("--strict-registry", action="store_true")
    p.add_argument("--allow-cross-domain-registry", action="store_true")
    p.add_argument("--type-schema", default="")
    p.add_argument("--max-clarification-rounds", type=int, default=2)
    p.add_argument("--clarification-answer-min-confidence", type=float, default=0.0)
    p.add_argument("--frontend-proposal-mode", choices=["off", "shadow", "active"], default="off")
    p.add_argument("--temporal-dual-write", action="store_true")
    p.add_argument("--temporal-predicate", default="at_step")
    p.add_argument("--exam-style", choices=["general", "detective", "medical"], default="detective")
    p.add_argument("--exam-question-count", type=int, default=20)
    p.add_argument("--exam-min-temporal-questions", type=int, default=4)
    p.add_argument("--pack-markdown", default="", help="Optional story-pack markdown for deterministic critical checks.")
    p.add_argument(
        "--critical-check-count",
        type=int,
        default=20,
        help="Max number of deterministic critical checks extracted from pack Exam Battery.",
    )
    p.add_argument(
        "--stage-recovery-mode",
        choices=["off", "sentence_line"],
        default="sentence_line",
        help="Recovery strategy when a stage has parser/apply failures.",
    )
    p.add_argument(
        "--stage-recovery-on-quality",
        choices=["off", "on"],
        default="on",
        help="Also trigger recovery when baseline quality misses gate thresholds.",
    )
    p.add_argument(
        "--stage-recovery-min-pct",
        type=int,
        default=40,
        help="Minimum stage percentage eligible for quality-triggered recovery.",
    )
    p.add_argument("--gate-coverage", type=float, default=0.85)
    p.add_argument("--gate-precision", type=float, default=0.90)
    p.add_argument("--gate-exam-pass-rate", type=float, default=0.80)
    p.add_argument("--gate-temporal-pass-rate", type=float, default=0.70)
    p.add_argument("--gate-critical-pass-rate", type=float, default=0.70)
    p.add_argument("--gate-carry-pass-rate", type=float, default=0.80)
    p.add_argument("--gate-min-carry-questions", type=int, default=8)
    p.add_argument(
        "--gate-profile",
        choices=["auto", "english_strict", "multilingual_experimental"],
        default="auto",
        help=(
            "Gate profile selector. 'auto' uses story language routing: english->english_strict, "
            "mixed/non_english->multilingual_experimental."
        ),
    )
    p.add_argument("--summary-json", default="")
    p.add_argument("--summary-md", default="")
    p.add_argument("--report-html", default="")
    args = p.parse_args()

    story_path = Path(args.story_file)
    if not story_path.is_absolute():
        story_path = (ROOT / story_path).resolve()
    if not story_path.exists():
        print(f"[gulp] missing story file: {story_path}", file=sys.stderr)
        return 2

    stamp = _utc_stamp()
    label = _slug(args.label.strip() or story_path.stem)
    percentages = _resolve_percentages(args.percentages)

    summary_json = (
        Path(args.summary_json).resolve()
        if str(args.summary_json).strip()
        else (ROOT / "tmp" / f"{label}_progressive_gulp_{stamp}.summary.json")
    )
    summary_md = (
        Path(args.summary_md).resolve()
        if str(args.summary_md).strip()
        else (ROOT / "tmp" / f"{label}_progressive_gulp_{stamp}.summary.md")
    )
    report_html = (
        Path(args.report_html).resolve()
        if str(args.report_html).strip()
        else (ROOT / "docs" / "reports" / f"{label}-progressive-gulp-{stamp}.html")
    )

    source_story_text = story_path.read_text(encoding="utf-8-sig", errors="replace")
    registry_mismatch = registry_profile_mismatch_message(
        str(args.predicate_registry),
        label=label,
        story_path=str(story_path),
        allow_cross_domain_registry=bool(args.allow_cross_domain_registry),
    )
    if registry_mismatch:
        print(f"[gulp] {registry_mismatch}", file=sys.stderr)
        return 2
    story_language_profile = _detect_story_language_profile(source_story_text)
    gate_profile_requested = str(args.gate_profile or "auto").strip().lower() or "auto"
    if gate_profile_requested == "auto":
        gate_profile_effective = (
            "english_strict"
            if str(story_language_profile.get("profile", "english")) == "english"
            else "multilingual_experimental"
        )
    else:
        gate_profile_effective = gate_profile_requested
    gate_defaults = (
        ENGLISH_STRICT_GATE_DEFAULTS
        if gate_profile_effective == "english_strict"
        else MULTILINGUAL_EXPERIMENTAL_GATES
    )
    effective_gate_coverage = _resolve_gate_value(
        requested=float(args.gate_coverage),
        english_default=ENGLISH_STRICT_GATE_DEFAULTS["coverage"],
        profile_default=float(gate_defaults["coverage"]),
    )
    effective_gate_precision = _resolve_gate_value(
        requested=float(args.gate_precision),
        english_default=ENGLISH_STRICT_GATE_DEFAULTS["precision"],
        profile_default=float(gate_defaults["precision"]),
    )
    effective_gate_exam_pass_rate = _resolve_gate_value(
        requested=float(args.gate_exam_pass_rate),
        english_default=ENGLISH_STRICT_GATE_DEFAULTS["exam_pass_rate"],
        profile_default=float(gate_defaults["exam_pass_rate"]),
    )
    effective_gate_temporal_pass_rate = _resolve_gate_value(
        requested=float(args.gate_temporal_pass_rate),
        english_default=ENGLISH_STRICT_GATE_DEFAULTS["temporal_pass_rate"],
        profile_default=float(gate_defaults["temporal_pass_rate"]),
    )
    effective_gate_critical_pass_rate = _resolve_gate_value(
        requested=float(args.gate_critical_pass_rate),
        english_default=ENGLISH_STRICT_GATE_DEFAULTS["critical_pass_rate"],
        profile_default=float(gate_defaults["critical_pass_rate"]),
    )
    effective_gate_carry_pass_rate = _resolve_gate_value(
        requested=float(args.gate_carry_pass_rate),
        english_default=ENGLISH_STRICT_GATE_DEFAULTS["carry_pass_rate"],
        profile_default=float(gate_defaults["carry_pass_rate"]),
    )
    print(
        "[gulp] language-profile routing:",
        f"profile={story_language_profile.get('profile')}",
        f"confidence={story_language_profile.get('confidence')}",
        f"gate_profile={gate_profile_effective}",
    )
    requested_split_mode = str(args.split_mode)
    effective_split_mode = requested_split_mode
    units = _split_story(source_story_text, split_mode=effective_split_mode)
    if bool(args.auto_fallback_split):
        if effective_split_mode in {"paragraph", "full"} and len(units) < max(2, len(percentages)):
            fallback_units = _split_story(source_story_text, split_mode="line")
            if len(fallback_units) > len(units):
                print(
                    "[gulp] split fallback:",
                    f"requested={effective_split_mode}",
                    f"units={len(units)}",
                    "-> line",
                    f"units={len(fallback_units)}",
                )
                effective_split_mode = "line"
                units = fallback_units
    if not units:
        print(f"[gulp] no non-empty units extracted from story: {story_path}", file=sys.stderr)
        return 3

    pack_markdown_path: Path | None = None
    if str(args.pack_markdown).strip():
        candidate = Path(str(args.pack_markdown).strip())
        if not candidate.is_absolute():
            candidate = (ROOT / candidate).resolve()
        if candidate.exists():
            pack_markdown_path = candidate
        else:
            print(f"[gulp] warning: pack markdown not found: {candidate}")

    critical_checks: list[dict[str, str]] = []
    if pack_markdown_path is not None:
        critical_checks = _parse_critical_checks_from_pack(
            pack_markdown_path,
            max_items=max(1, int(args.critical_check_count)),
        )
        print(
            "[gulp] deterministic critical checks:",
            f"source={pack_markdown_path}",
            f"count={len(critical_checks)}",
        )

    shared_kb = f"raw_{label}_gulp_shared_{stamp}"
    stage_rows: list[dict[str, Any]] = []
    stage_question_packs: list[dict[str, Any]] = []

    def _run_stage_attempt(
        *,
        stage_index: int,
        pct: int,
        stage_text: str,
        split_mode: str,
        kb_name: str,
        attempt_tag: str,
    ) -> dict[str, Any]:
        suffix = f"_{attempt_tag}" if attempt_tag else ""
        run_id = f"raw_{label}_gulp_{pct:03d}_{stamp}{suffix}"
        stage_story_path = ROOT / "tmp" / "stories" / f"{label}_gulp_{pct:03d}_{stamp}{suffix}.txt"
        stage_story_path.parent.mkdir(parents=True, exist_ok=True)
        stage_story_path.write_text(stage_text, encoding="utf-8")
        pipeline_out = ROOT / "tmp" / f"{run_id}.pipeline.json"
        scenario_out = ROOT / "tmp" / "scenarios" / f"{run_id}.json"

        cmd = [
            sys.executable,
            str(RUN_STORY_RAW),
            "--story-file",
            str(stage_story_path),
            "--scenario-name",
            run_id,
            "--scenario-out",
            str(scenario_out),
            "--pipeline-out",
            str(pipeline_out),
            "--kb-name",
            str(kb_name),
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
            str(split_mode),
            "--max-clarification-rounds",
            str(int(args.max_clarification_rounds)),
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
        if bool(args.temporal_dual_write):
            cmd.append("--temporal-dual-write")
        if str(args.predicate_registry).strip():
            cmd.extend(["--predicate-registry", str(args.predicate_registry)])
        if bool(args.strict_registry):
            cmd.append("--strict-registry")
        if str(args.type_schema).strip():
            cmd.extend(["--type-schema", str(args.type_schema)])

        print(
            f"[gulp {stage_index}/{len(percentages)}] stage={pct}% run_id={run_id}",
            f"split={split_mode}",
            f"attempt={attempt_tag or 'baseline'}",
        )
        proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
        pipeline_report = _load_json(pipeline_out) if pipeline_out.exists() else {}
        interrogator_out = ROOT / "tmp" / f"{run_id}.interrogator.json"
        interrogator_report = _load_json(interrogator_out) if interrogator_out.exists() else {}
        return {
            "attempt_tag": attempt_tag or "baseline",
            "split_mode": str(split_mode),
            "kb_name": str(kb_name),
            "run_id": run_id,
            "stage_story_path": str(stage_story_path),
            "scenario_path": str(scenario_out),
            "pipeline_output": str(pipeline_out),
            "interrogator_output": str(interrogator_out),
            "exit_code": int(proc.returncode),
            "pipeline_report": pipeline_report,
            "interrogator_report": interrogator_report,
        }

    def _attempt_sort_key(attempt: dict[str, Any]) -> tuple[int, float, float, float, int, int]:
        pipe = attempt.get("pipeline_report", {})
        ir = attempt.get("interrogator_report", {})
        exam = ir.get("exam", {}) if isinstance(ir.get("exam"), dict) else {}
        audit = ir.get("fact_audit", {}) if isinstance(ir.get("fact_audit"), dict) else {}
        pipeline_ok = 1 if str(pipe.get("overall_status", "")).lower() == "passed" else 0
        parse_fail = int(pipe.get("turn_parse_failures", 0) or 0)
        apply_fail = int(pipe.get("turn_apply_failures", 0) or 0)
        exam_rate = float(exam.get("pass_rate", 0.0) or 0.0)
        coverage = float(audit.get("coverage_score", 0.0) or 0.0)
        precision = float(audit.get("precision_score", 0.0) or 0.0)
        return (pipeline_ok, coverage, precision, exam_rate, -parse_fail, -apply_fail)

    shared_kb_dir = _kb_dir_for_name(shared_kb)
    if shared_kb_dir.exists():
        shutil.rmtree(shared_kb_dir, ignore_errors=True)
    shared_kb_dir.mkdir(parents=True, exist_ok=True)

    for idx, pct in enumerate(percentages, start=1):
        stage_units = _slice_units(units, pct)
        stage_text = _stage_text_from_units(stage_units, split_mode=effective_split_mode)

        baseline_kb_name = f"{shared_kb}_s{idx:02d}_baseline"
        _copy_kb_state(src_kb_name=shared_kb, dst_kb_name=baseline_kb_name)
        baseline = _run_stage_attempt(
            stage_index=idx,
            pct=int(pct),
            stage_text=stage_text,
            split_mode=effective_split_mode,
            kb_name=baseline_kb_name,
            attempt_tag="",
        )
        attempts: list[dict[str, Any]] = [baseline]
        selected = baseline

        baseline_pipe = baseline.get("pipeline_report", {})
        baseline_ir = baseline.get("interrogator_report", {})
        baseline_audit = baseline_ir.get("fact_audit", {}) if isinstance(baseline_ir.get("fact_audit"), dict) else {}
        baseline_parse_fail = int(baseline_pipe.get("turn_parse_failures", 0) or 0)
        baseline_apply_fail = int(baseline_pipe.get("turn_apply_failures", 0) or 0)
        baseline_coverage = float(baseline_audit.get("coverage_score", 0.0) or 0.0)
        baseline_precision = float(baseline_audit.get("precision_score", 0.0) or 0.0)
        baseline_kb_path = _resolve_kb_path(baseline_pipe, baseline_kb_name)
        baseline_critical_eval = _evaluate_critical_checks(baseline_kb_path, critical_checks, source_text=stage_text)
        baseline_critical_q = int(baseline_critical_eval.get("check_count", 0) or 0)
        baseline_critical_rate = float(baseline_critical_eval.get("pass_rate", 0.0) or 0.0)

        quality_recovery_enabled = (
            str(args.stage_recovery_on_quality).lower() == "on"
            and int(pct) >= max(1, int(args.stage_recovery_min_pct))
        )
        quality_miss = quality_recovery_enabled and (
            baseline_coverage < float(effective_gate_coverage)
            or baseline_precision < float(effective_gate_precision)
            or (baseline_critical_q > 0 and baseline_critical_rate < float(effective_gate_critical_pass_rate))
        )
        should_recover = (
            str(args.stage_recovery_mode) != "off"
            and (baseline_parse_fail > 0 or baseline_apply_fail > 0 or quality_miss)
        )
        recovery_trigger = "none"
        if baseline_parse_fail > 0 or baseline_apply_fail > 0:
            recovery_trigger = "failure"
        elif quality_miss:
            recovery_trigger = "quality"

        if should_recover:
            sentence_lines = _sentence_lines_from_text(stage_text)
            if len(sentence_lines) > 1:
                recovery_text = "\n".join(sentence_lines) + "\n"
                recovery_kb_name = f"{shared_kb}_s{idx:02d}_recovery"
                _copy_kb_state(src_kb_name=shared_kb, dst_kb_name=recovery_kb_name)
                recovery = _run_stage_attempt(
                    stage_index=idx,
                    pct=int(pct),
                    stage_text=recovery_text,
                    split_mode="line",
                    kb_name=recovery_kb_name,
                    attempt_tag="recovery",
                )
                attempts.append(recovery)
                if _attempt_sort_key(recovery) > _attempt_sort_key(selected):
                    selected = recovery

        selected_kb_name = str(selected.get("kb_name", "") or shared_kb).strip() or shared_kb
        _promote_kb_state(src_kb_name=selected_kb_name, dst_kb_name=shared_kb)
        promoted_kb_path = (_kb_dir_for_name(shared_kb) / "kb.pl").resolve()

        pipeline_report = selected.get("pipeline_report", {})
        interrogator_report = selected.get("interrogator_report", {})
        kb_path = promoted_kb_path

        kb_preview = ""
        kb_clause_count = 0
        if kb_path.exists():
            kb_lines = kb_path.read_text(encoding="utf-8", errors="replace").splitlines()
            kb_preview = "\n".join(kb_lines[:220])
            for raw in kb_lines:
                line = str(raw or "").strip()
                if line and not line.startswith("%") and not line.startswith(":-") and line.endswith("."):
                    kb_clause_count += 1

        fact_audit = interrogator_report.get("fact_audit") if isinstance(interrogator_report.get("fact_audit"), dict) else {}
        exam = interrogator_report.get("exam") if isinstance(interrogator_report.get("exam"), dict) else {}
        critical_eval = _evaluate_critical_checks(kb_path, critical_checks, source_text=stage_text)
        questions = exam.get("questions", []) if isinstance(exam.get("questions"), list) else []
        stage_question_packs.append({"stage_index": idx, "questions": questions})

        carry_rows: list[dict[str, Any]] = []
        if kb_path.exists():
            for prior in stage_question_packs:
                prior_stage = int(prior.get("stage_index", 0) or 0)
                prior_questions = prior.get("questions", [])
                if not isinstance(prior_questions, list) or not prior_questions:
                    continue
                carry_eval = _evaluate_question_pack(kb_path, prior_questions)
                carry_rows.append({"from_stage": prior_stage, **carry_eval})

        stage_rows.append(
            {
                "stage_index": idx,
                "pct": int(pct),
                "exit_code": int(selected.get("exit_code", 1)),
                "run_id": str(selected.get("run_id", "")),
                "stage_story_path": str(selected.get("stage_story_path", "")),
                "scenario_path": str(selected.get("scenario_path", "")),
                "pipeline_output": str(selected.get("pipeline_output", "")),
                "interrogator_output": str(selected.get("interrogator_output", "")),
                "pipeline_status": str(pipeline_report.get("overall_status", "missing")),
                "parse_failures": int(pipeline_report.get("turn_parse_failures", 0) or 0),
                "apply_failures": int(pipeline_report.get("turn_apply_failures", 0) or 0),
                "clarification_requests": int(pipeline_report.get("turns_clarification_requested", 0) or 0),
                "coverage": float(fact_audit.get("coverage_score", 0.0) or 0.0),
                "precision": float(fact_audit.get("precision_score", 0.0) or 0.0),
                "exam_pass_count": int(exam.get("pass_count", 0) or 0),
                "exam_question_count": int(exam.get("question_count", 0) or 0),
                "exam_pass_rate": float(exam.get("pass_rate", 0.0) or 0.0),
                "temporal_exam_pass_count": int(exam.get("temporal_pass_count", 0) or 0),
                "temporal_exam_question_count": int(exam.get("temporal_question_count", 0) or 0),
                "temporal_exam_pass_rate": float(exam.get("temporal_pass_rate", 0.0) or 0.0),
                "critical_exam_check_count": int(critical_eval.get("check_count", 0) or 0),
                "critical_exam_pass_count": int(critical_eval.get("pass_count", 0) or 0),
                "critical_exam_pass_rate": float(critical_eval.get("pass_rate", 0.0) or 0.0),
                "critical_exam": critical_eval.get("checks", []),
                "kb_path": str(kb_path),
                "kb_clause_count": kb_clause_count,
                "kb_preview": kb_preview,
                "carry_forward": carry_rows,
                "ce_summary": _summarize_ce(pipeline_report),
                "recovery_used": str(selected.get("attempt_tag", "")) == "recovery",
                "recovery_trigger": recovery_trigger if should_recover else "none",
                "selected_kb_name": selected_kb_name,
                "attempts": [
                    {
                        "attempt_tag": str(a.get("attempt_tag", "")),
                        "split_mode": str(a.get("split_mode", "")),
                        "kb_name": str(a.get("kb_name", "")),
                        "run_id": str(a.get("run_id", "")),
                        "exit_code": int(a.get("exit_code", 1)),
                        "pipeline_status": str((a.get("pipeline_report", {}) or {}).get("overall_status", "missing")),
                        "parse_failures": int((a.get("pipeline_report", {}) or {}).get("turn_parse_failures", 0) or 0),
                        "apply_failures": int((a.get("pipeline_report", {}) or {}).get("turn_apply_failures", 0) or 0),
                    }
                    for a in attempts
                    if isinstance(a, dict)
                ],
            }
        )

    for row in stage_rows:
        gate_failures: list[str] = []
        pipeline_ok = str(row.get("pipeline_status", "")).lower() == "passed"
        if not pipeline_ok:
            gate_failures.append("pipeline_not_passed")
        if int(row.get("parse_failures", 0) or 0) > 0:
            gate_failures.append("parse_failures_present")
        if int(row.get("apply_failures", 0) or 0) > 0:
            gate_failures.append("apply_failures_present")
        if float(row.get("coverage", 0.0) or 0.0) < float(effective_gate_coverage):
            gate_failures.append("coverage_below_gate")
        if float(row.get("precision", 0.0) or 0.0) < float(effective_gate_precision):
            gate_failures.append("precision_below_gate")
        if float(row.get("exam_pass_rate", 0.0) or 0.0) < float(effective_gate_exam_pass_rate):
            gate_failures.append("exam_pass_below_gate")

        temporal_q = int(row.get("temporal_exam_question_count", 0) or 0)
        temporal_rate = float(row.get("temporal_exam_pass_rate", 0.0) or 0.0)
        if temporal_q >= max(1, int(args.gate_min_carry_questions // 2)):
            if temporal_rate < float(effective_gate_temporal_pass_rate):
                gate_failures.append("temporal_exam_below_gate")

        critical_q = int(row.get("critical_exam_check_count", 0) or 0)
        critical_rate = float(row.get("critical_exam_pass_rate", 0.0) or 0.0)
        if critical_q > 0 and critical_rate < float(effective_gate_critical_pass_rate):
            gate_failures.append("critical_exam_below_gate")

        carry_rows = row.get("carry_forward", [])
        if not isinstance(carry_rows, list):
            carry_rows = []
        for carry in carry_rows:
            if not isinstance(carry, dict):
                continue
            q_count = int(carry.get("question_count", 0) or 0)
            if q_count < int(args.gate_min_carry_questions):
                continue
            if float(carry.get("pass_rate", 0.0) or 0.0) < float(effective_gate_carry_pass_rate):
                gate_failures.append(f"carry_forward_stage_{int(carry.get('from_stage', 0) or 0)}_below_gate")

        row["gate_failures"] = gate_failures
        row["gate_passed"] = len(gate_failures) == 0

    pipeline_pass_count = sum(1 for r in stage_rows if str(r.get("pipeline_status", "")).lower() == "passed")
    gate_pass_count = sum(1 for r in stage_rows if bool(r.get("gate_passed")))
    avg_coverage = (
        sum(float(r.get("coverage", 0.0) or 0.0) for r in stage_rows) / len(stage_rows) if stage_rows else 0.0
    )
    avg_precision = (
        sum(float(r.get("precision", 0.0) or 0.0) for r in stage_rows) / len(stage_rows) if stage_rows else 0.0
    )
    avg_exam_pass = (
        sum(float(r.get("exam_pass_rate", 0.0) or 0.0) for r in stage_rows) / len(stage_rows) if stage_rows else 0.0
    )
    avg_critical_pass = (
        sum(float(r.get("critical_exam_pass_rate", 0.0) or 0.0) for r in stage_rows) / len(stage_rows)
        if stage_rows
        else 0.0
    )

    summary: dict[str, Any] = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "story_file": str(story_path),
        "label": label,
        "settings": {
            "backend": args.backend,
            "base_url": args.base_url,
            "model": args.model,
            "predicate_registry": str(args.predicate_registry),
            "strict_registry": bool(args.strict_registry),
            "type_schema": str(args.type_schema),
            "story_language_profile": story_language_profile,
            "gate_profile_requested": gate_profile_requested,
            "gate_profile_effective": gate_profile_effective,
            "gate_thresholds_effective": {
                "coverage": round(float(effective_gate_coverage), 6),
                "precision": round(float(effective_gate_precision), 6),
                "exam_pass_rate": round(float(effective_gate_exam_pass_rate), 6),
                "temporal_pass_rate": round(float(effective_gate_temporal_pass_rate), 6),
                "critical_pass_rate": round(float(effective_gate_critical_pass_rate), 6),
                "carry_pass_rate": round(float(effective_gate_carry_pass_rate), 6),
            },
            "split_mode_requested": requested_split_mode,
            "split_mode_effective": effective_split_mode,
            "split_unit_count": len(units),
            "percentages": percentages,
            "temporal_dual_write": bool(args.temporal_dual_write),
            "temporal_predicate": args.temporal_predicate,
            "max_clarification_rounds": int(args.max_clarification_rounds),
            "clarification_answer_min_confidence": float(args.clarification_answer_min_confidence),
            "exam_style": args.exam_style,
            "exam_question_count": int(args.exam_question_count),
            "exam_min_temporal_questions": int(args.exam_min_temporal_questions),
            "stage_recovery_mode": str(args.stage_recovery_mode),
            "stage_recovery_on_quality": str(args.stage_recovery_on_quality),
            "stage_recovery_min_pct": int(args.stage_recovery_min_pct),
            "pack_markdown": str(pack_markdown_path) if pack_markdown_path is not None else "",
            "critical_check_count": int(len(critical_checks)),
            "shared_kb_name": shared_kb,
        },
        "stage_count": len(stage_rows),
        "pipeline_pass_count": pipeline_pass_count,
        "gate_pass_count": gate_pass_count,
        "avg_coverage": round(avg_coverage, 6),
        "avg_precision": round(avg_precision, 6),
        "avg_exam_pass_rate": round(avg_exam_pass, 6),
        "avg_critical_exam_pass_rate": round(avg_critical_pass, 6),
        "stages": stage_rows,
    }

    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Progressive Gulp Summary",
        "",
        f"- Story file: `{story_path}`",
        f"- Split mode requested/effective: `{requested_split_mode}` / `{effective_split_mode}`",
        f"- Split unit count: `{len(units)}`",
        f"- Stages: `{','.join(str(x) + '%' for x in percentages)}`",
        f"- Shared KB: `{shared_kb}`",
        f"- Story language profile: `{story_language_profile.get('profile')}` (confidence `{story_language_profile.get('confidence')}`)",
        f"- Gate profile requested/effective: `{gate_profile_requested}` / `{gate_profile_effective}`",
        (
            "- Gate thresholds effective: "
            f"`coverage={effective_gate_coverage:.3f}` "
            f"`precision={effective_gate_precision:.3f}` "
            f"`exam={effective_gate_exam_pass_rate:.3f}` "
            f"`temporal={effective_gate_temporal_pass_rate:.3f}` "
            f"`critical={effective_gate_critical_pass_rate:.3f}` "
            f"`carry={effective_gate_carry_pass_rate:.3f}`"
        ),
        f"- Pipeline pass: `{pipeline_pass_count}/{len(stage_rows)}`",
        f"- Gate pass: `{gate_pass_count}/{len(stage_rows)}`",
        f"- Avg coverage: `{summary['avg_coverage']}`",
        f"- Avg precision: `{summary['avg_precision']}`",
        f"- Avg exam pass: `{summary['avg_exam_pass_rate']}`",
        f"- Avg critical exam pass: `{summary['avg_critical_exam_pass_rate']}`",
        "",
        "| Stage | Gulp | Pipeline | Gate | Coverage | Precision | Exam | Temporal Exam | Critical Exam | KB Clauses |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in stage_rows:
        md_lines.append(
            "| "
            + f"{int(row.get('stage_index', 0) or 0)} | "
            + f"{int(row.get('pct', 0) or 0)}% | "
            + f"`{row.get('pipeline_status', '')}` | "
            + f"`{'pass' if bool(row.get('gate_passed')) else 'fail'}` | "
            + f"{float(row.get('coverage', 0.0) or 0.0):.3f} | "
            + f"{float(row.get('precision', 0.0) or 0.0):.3f} | "
            + f"{int(row.get('exam_pass_count', 0) or 0)}/{int(row.get('exam_question_count', 0) or 0)} | "
            + f"{int(row.get('temporal_exam_pass_count', 0) or 0)}/{int(row.get('temporal_exam_question_count', 0) or 0)} | "
            + f"{int(row.get('critical_exam_pass_count', 0) or 0)}/{int(row.get('critical_exam_check_count', 0) or 0)} | "
            + f"{int(row.get('kb_clause_count', 0) or 0)} |"
        )
    summary_md.parent.mkdir(parents=True, exist_ok=True)
    summary_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    _render_html(
        title=f"Progressive Gulp Audit - {label}",
        source_story_path=story_path,
        source_story_text=source_story_text,
        stage_rows=stage_rows,
        out_path=report_html,
    )

    print(f"[gulp] summary_json={summary_json}")
    print(f"[gulp] summary_md={summary_md}")
    print(f"[gulp] report_html={report_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
