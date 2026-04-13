#!/usr/bin/env python3
"""
Grade a candidate KB for coverage/precision.

Modes:
- strict: compare against a golden KB
- semantic: compare source prose against candidate KB using a model
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import kb_pipeline as kp  # noqa: E402
import golden_kb  # noqa: E402

DEFAULT_BASE_URLS = {
    "ollama": "http://127.0.0.1:11434",
    "lmstudio": "http://127.0.0.1:1234",
}


def _clip_01(value: Any, fallback: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return max(0.0, min(1.0, parsed))


def _score_to_letter(score: float) -> str:
    if score >= 0.985:
        return "A+"
    if score >= 0.95:
        return "A"
    if score >= 0.9:
        return "A-"
    if score >= 0.87:
        return "B+"
    if score >= 0.83:
        return "B"
    if score >= 0.8:
        return "B-"
    if score >= 0.77:
        return "C+"
    if score >= 0.73:
        return "C"
    if score >= 0.7:
        return "C-"
    if score >= 0.67:
        return "D+"
    if score >= 0.63:
        return "D"
    if score >= 0.6:
        return "D-"
    return "F"


def _letter_to_score(letter: str) -> float:
    table = {
        "A+": 0.99,
        "A": 0.95,
        "A-": 0.9,
        "B+": 0.87,
        "B": 0.83,
        "B-": 0.8,
        "C+": 0.77,
        "C": 0.73,
        "C-": 0.7,
        "D+": 0.67,
        "D": 0.63,
        "D-": 0.6,
        "F": 0.4,
    }
    return table.get(str(letter).strip().upper(), 0.4)


def _build_semantic_prompt(*, source_text: str, candidate_clauses: list[str]) -> str:
    kb_text = "\n".join(f"- {row}" for row in candidate_clauses) if candidate_clauses else "(none)"
    return (
        "/no_think\n"
        "You are evaluating whether a symbolic Prolog KB preserves source semantics.\n"
        "Return minified JSON only with keys:\n"
        "overall_grade,coverage_score,precision_score,missing_facts,wrong_facts,predicate_drift,summary\n"
        "Rules:\n"
        "- overall_grade must be one of A+,A,A-,B+,B,B-,C+,C,C-,D+,D,D-,F\n"
        "- coverage_score and precision_score must be numbers in [0,1]\n"
        "- missing_facts, wrong_facts, predicate_drift must be arrays of short strings\n"
        "- summary must be <=40 words\n"
        "Do not output markdown or extra keys.\n"
        f"Source prose:\n{source_text}\n"
        f"Candidate KB clauses:\n{kb_text}\n"
    )


def _strict_grade(compare: dict[str, Any]) -> dict[str, Any]:
    matched = int(compare.get("matched_clause_count", 0) or 0)
    golden_count = int(compare.get("golden_clause_count", 0) or 0)
    candidate_count = int(compare.get("candidate_clause_count", 0) or 0)
    precision = (matched / candidate_count) if candidate_count else 1.0
    recall = (matched / golden_count) if golden_count else 1.0
    if precision + recall <= 0:
        f1 = 0.0
    else:
        f1 = (2 * precision * recall) / (precision + recall)
    strict_score = f1
    return {
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "score": round(strict_score, 6),
        "grade": _score_to_letter(strict_score),
    }


def _semantic_grade(
    *,
    source_text: str,
    candidate_clauses: list[str],
    backend: str,
    base_url: str,
    model: str,
    context_length: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    prompt = _build_semantic_prompt(source_text=source_text, candidate_clauses=candidate_clauses)
    api_key = kp._get_api_key() if hasattr(kp, "_get_api_key") else None
    response = kp._call_model_prompt(
        backend=backend,
        base_url=base_url,
        model=model,
        prompt_text=prompt,
        context_length=max(1024, int(context_length)),
        timeout=max(10, int(timeout_seconds)),
        api_key=api_key,
    )
    parsed, _ = kp._parse_model_json(response, required_keys=["overall_grade"])
    if not isinstance(parsed, dict):
        return {
            "status": "parse_error",
            "grade": "F",
            "score": 0.4,
            "coverage_score": 0.0,
            "precision_score": 0.0,
            "missing_facts": [],
            "wrong_facts": [],
            "predicate_drift": [],
            "summary": "Semantic grader did not return parseable JSON.",
            "raw_message": str(getattr(response, "message", "") or "")[:1200],
        }

    grade = str(parsed.get("overall_grade", "F")).strip().upper()
    if grade not in {"A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"}:
        grade = "F"
    coverage = _clip_01(parsed.get("coverage_score"), fallback=0.0)
    precision = _clip_01(parsed.get("precision_score"), fallback=0.0)
    missing_facts = parsed.get("missing_facts", []) if isinstance(parsed.get("missing_facts"), list) else []
    wrong_facts = parsed.get("wrong_facts", []) if isinstance(parsed.get("wrong_facts"), list) else []
    predicate_drift = (
        parsed.get("predicate_drift", []) if isinstance(parsed.get("predicate_drift"), list) else []
    )
    score = (0.55 * coverage) + (0.45 * precision)
    score = max(score, _letter_to_score(grade) * 0.85)
    penalty = min(0.5, (0.08 * len(missing_facts)) + (0.08 * len(wrong_facts)) + (0.04 * len(predicate_drift)))
    score = max(0.0, score - penalty)
    return {
        "status": "ok",
        "grade": grade,
        "score": round(score, 6),
        "coverage_score": round(coverage, 6),
        "precision_score": round(precision, 6),
        "missing_facts": missing_facts,
        "wrong_facts": wrong_facts,
        "predicate_drift": predicate_drift,
        "summary": str(parsed.get("summary", "")).strip(),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Grade a candidate KB from golden truth and/or prose semantics.")
    p.add_argument("--candidate-kb", required=True, help="Candidate kb.pl path.")
    p.add_argument("--golden-kb", default="", help="Optional golden kb.pl path for strict diff grading.")
    p.add_argument("--source-text-file", default="", help="Optional source prose path for semantic grading.")
    p.add_argument("--source-max-chars", type=int, default=12000)
    p.add_argument("--kb-max-clauses", type=int, default=300)
    p.add_argument("--backend", choices=["ollama", "lmstudio"], default="ollama")
    p.add_argument("--base-url", default=DEFAULT_BASE_URLS["ollama"])
    p.add_argument("--model", default="qwen3.5:9b")
    p.add_argument("--context-length", type=int, default=8192)
    p.add_argument("--timeout-seconds", type=int, default=120)
    p.add_argument("--out", default="", help="Optional JSON output path.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    candidate_path = Path(args.candidate_kb).resolve()
    if not candidate_path.exists():
        print(f"Candidate KB not found: {candidate_path}")
        return 2
    if not str(args.golden_kb).strip() and not str(args.source_text_file).strip():
        print("Provide at least one of --golden-kb or --source-text-file.")
        return 2

    candidate_clauses = golden_kb.load_canonical_clauses(candidate_path)
    if int(args.kb_max_clauses) > 0:
        candidate_for_semantic = candidate_clauses[-int(args.kb_max_clauses) :]
    else:
        candidate_for_semantic = candidate_clauses

    strict_compare: dict[str, Any] | None = None
    strict_grade: dict[str, Any] | None = None
    if str(args.golden_kb).strip():
        golden_path = Path(args.golden_kb).resolve()
        if not golden_path.exists():
            print(f"Golden KB not found: {golden_path}")
            return 2
        strict_compare = golden_kb.compare_kbs(golden_path, candidate_path)
        strict_grade = _strict_grade(strict_compare)

    semantic_grade: dict[str, Any] | None = None
    source_text = ""
    if str(args.source_text_file).strip():
        source_path = Path(args.source_text_file).resolve()
        if not source_path.exists():
            print(f"Source text file not found: {source_path}")
            return 2
        source_text = source_path.read_text(encoding="utf-8-sig")
        if int(args.source_max_chars) > 0 and len(source_text) > int(args.source_max_chars):
            source_text = source_text[: int(args.source_max_chars)]
        semantic_grade = _semantic_grade(
            source_text=source_text,
            candidate_clauses=candidate_for_semantic,
            backend=args.backend,
            base_url=args.base_url,
            model=args.model,
            context_length=int(args.context_length),
            timeout_seconds=int(args.timeout_seconds),
        )

    if strict_grade and semantic_grade:
        overall_score = (0.75 * float(strict_grade["score"])) + (0.25 * float(semantic_grade["score"]))
    elif strict_grade:
        overall_score = float(strict_grade["score"])
    elif semantic_grade:
        overall_score = float(semantic_grade["score"])
    else:
        overall_score = 0.0
    overall_grade = _score_to_letter(overall_score)

    payload = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "candidate_kb": str(candidate_path),
        "candidate_clause_count": len(candidate_clauses),
        "strict_compare": strict_compare,
        "strict_grade": strict_grade,
        "semantic_grade": semantic_grade,
        "overall": {
            "score": round(overall_score, 6),
            "grade": overall_grade,
        },
    }

    out_path = Path(args.out).resolve() if str(args.out).strip() else None
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Overall grade: {overall_grade} ({overall_score:.3f})")
    if strict_grade:
        print(
            "Strict grade: "
            f"{strict_grade['grade']} "
            f"(precision={strict_grade['precision']:.3f}, recall={strict_grade['recall']:.3f}, f1={strict_grade['f1']:.3f})"
        )
        if strict_compare:
            print(
                "Strict diff: "
                f"missing={strict_compare.get('missing_clause_count', 0)} "
                f"extra={strict_compare.get('extra_clause_count', 0)}"
            )
    if semantic_grade:
        print(
            "Semantic grade: "
            f"{semantic_grade.get('grade', 'F')} "
            f"(coverage={float(semantic_grade.get('coverage_score', 0.0)):.3f}, "
            f"precision={float(semantic_grade.get('precision_score', 0.0)):.3f})"
        )
        summary = str(semantic_grade.get("summary", "")).strip()
        if summary:
            print(f"Semantic summary: {summary}")
    if out_path is not None:
        print(f"Report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
