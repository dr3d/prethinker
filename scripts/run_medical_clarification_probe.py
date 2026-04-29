#!/usr/bin/env python3
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

from kb_pipeline import _build_extractor_prompt, _call_model_prompt, _parse_model_json  # noqa: E402
from src import medical_profile, umls_mvp  # noqa: E402
from scripts.run_medical_prompt_probe import _build_medical_guide  # noqa: E402


DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen/qwen3.6-35b-a3b"
DEFAULT_CONTEXT = 8192
DEFAULT_TIMEOUT = 90
DEFAULT_SHARED_PROMPT = ROOT / "modelfiles" / "blank_prompt.md"
DEFAULT_MEDICAL_SUPPLEMENT = ROOT / "modelfiles" / "medical_compiler_prompt_supplement.md"
DEFAULT_BATTERY = ROOT / "docs" / "data" / "medical_clarification_probe_battery.json"
DEFAULT_SLICE_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp"
DEFAULT_OUT_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp" / "medical_clarification_probe_latest"

MEDICAL_PREDICATES = medical_profile.canonical_predicate_signatures(
    medical_profile.load_profile_manifest()
)


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _run_parse(
    *,
    utterance: str,
    route: str,
    prompt_guide: str,
    known_predicates: list[str],
    base_url: str,
    model: str,
    context_length: int,
    timeout: int,
) -> tuple[dict[str, Any] | None, str]:
    prompt = _build_extractor_prompt(
        utterance,
        route,
        known_predicates=known_predicates,
        prompt_guide=prompt_guide,
    )
    response = _call_model_prompt(
        backend="ollama",
        base_url=base_url,
        model=model,
        prompt_text=prompt,
        context_length=context_length,
        timeout=timeout,
        api_key=None,
        response_format="json",
    )
    parsed, raw = _parse_model_json(response, ["intent", "logic_string"])
    return parsed, raw


def _score_initial(case: dict[str, Any], parsed: dict[str, Any] | None) -> dict[str, Any]:
    expect_clar = bool(case.get("initial_expect_needs_clarification", True))
    needs_clar = bool(parsed.get("needs_clarification", False)) if isinstance(parsed, dict) else False
    logic_string = str(parsed.get("logic_string", "")).strip() if isinstance(parsed, dict) else ""
    points = 0
    if needs_clar == expect_clar:
        points += 1
    if needs_clar and logic_string == "":
        points += 1
    return {
        "needs_clarification": needs_clar,
        "logic_string": logic_string,
        "score": points,
        "score_max": 2,
    }


def _score_final(case: dict[str, Any], parsed: dict[str, Any] | None) -> dict[str, Any]:
    expect_clar = bool(case.get("final_expect_needs_clarification", False))
    expected = [str(item).strip() for item in case.get("final_expected_logic_contains", []) or [] if str(item).strip()]
    forbidden = [str(item).strip() for item in case.get("final_forbidden_logic_contains", []) or [] if str(item).strip()]
    needs_clar = bool(parsed.get("needs_clarification", False)) if isinstance(parsed, dict) else False
    logic_string = str(parsed.get("logic_string", "")).strip() if isinstance(parsed, dict) else ""
    matched = [token for token in expected if token in logic_string]
    hit_forbidden = [token for token in forbidden if token in logic_string]
    points = 0
    score_max = 1 + len(expected) + len(forbidden)
    if needs_clar == expect_clar:
        points += 1
    points += len(matched)
    points += len(forbidden) - len(hit_forbidden)
    return {
        "needs_clarification": needs_clar,
        "logic_string": logic_string,
        "matched_expected": matched,
        "missing_expected": [token for token in expected if token not in matched],
        "hit_forbidden": hit_forbidden,
        "score": points,
        "score_max": score_max,
    }


def _effective_utterance(case: dict[str, Any]) -> str:
    utterance = str(case.get("utterance", "")).strip()
    question = str(case.get("clarification_question", "")).strip()
    answer = str(case.get("clarification_answer", "")).strip()
    return (
        f"{utterance}\n"
        f"Clarification question: {question}\n"
        f"Clarification answer: {answer}"
    ).strip()


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Medical Clarification Probe",
        "",
        f"- generated_at_utc: `{summary['generated_at_utc']}`",
        f"- cases: `{summary['counts']['cases']}`",
        f"- baseline total score: `{summary['counts']['baseline_score']}` / `{summary['counts']['score_max']}`",
        f"- medical total score: `{summary['counts']['medical_score']}` / `{summary['counts']['score_max']}`",
        f"- delta: `{summary['counts']['medical_score'] - summary['counts']['baseline_score']}`",
        "",
        "## Case Outcomes",
        "",
    ]
    for case in summary["cases"]:
        lines.append(
            f"- `{case['case_id']}` baseline={case['baseline_total_score']}/{case['total_score_max']} "
            f"medical={case['medical_total_score']}/{case['total_score_max']}"
        )
        lines.append(f"  - utterance: `{case['utterance']}`")
        lines.append(f"  - clarification answer: `{case['clarification_answer']}`")
        lines.append(f"  - baseline final logic: `{case['baseline_final']['logic_string']}`")
        lines.append(f"  - medical final logic: `{case['medical_final']['logic_string']}`")
    return "\n".join(lines) + "\n"


def run_probe(
    *,
    base_url: str,
    model: str,
    context_length: int,
    timeout: int,
    shared_prompt_path: Path,
    medical_supplement_path: Path,
    battery_path: Path,
    slice_dir: Path,
    out_dir: Path,
) -> dict[str, Any]:
    shared_prompt = shared_prompt_path.read_text(encoding="utf-8")
    supplement = medical_supplement_path.read_text(encoding="utf-8")
    concepts = medical_profile.load_profile_concepts(slice_dir)
    battery = umls_mvp.load_json(battery_path)
    medical_guide = _build_medical_guide(shared_prompt, supplement, concepts)

    rows: list[dict[str, Any]] = []
    baseline_total = 0
    medical_total = 0
    total_max = 0

    for case in battery.get("cases", []) or []:
        utterance = str(case.get("utterance", "")).strip()
        route = str(case.get("route", "assert_fact")).strip()
        effective = _effective_utterance(case)

        baseline_initial_parsed, baseline_initial_raw = _run_parse(
            utterance=utterance,
            route=route,
            prompt_guide=shared_prompt,
            known_predicates=[],
            base_url=base_url,
            model=model,
            context_length=context_length,
            timeout=timeout,
        )
        baseline_final_parsed, baseline_final_raw = _run_parse(
            utterance=effective,
            route=route,
            prompt_guide=shared_prompt,
            known_predicates=[],
            base_url=base_url,
            model=model,
            context_length=context_length,
            timeout=timeout,
        )

        medical_initial_parsed, medical_initial_raw = _run_parse(
            utterance=utterance,
            route=route,
            prompt_guide=medical_guide,
            known_predicates=MEDICAL_PREDICATES,
            base_url=base_url,
            model=model,
            context_length=context_length,
            timeout=timeout,
        )
        medical_initial_parsed = medical_profile.sanitize_medical_parse_for_clarification(
            medical_initial_parsed,
            utterance=utterance,
        )
        medical_final_parsed, medical_final_raw = _run_parse(
            utterance=effective,
            route=route,
            prompt_guide=medical_guide,
            known_predicates=MEDICAL_PREDICATES,
            base_url=base_url,
            model=model,
            context_length=context_length,
            timeout=timeout,
        )
        medical_final_parsed = medical_profile.sanitize_medical_parse_for_clarification(
            medical_final_parsed,
            utterance=effective,
        )

        baseline_initial = _score_initial(case, baseline_initial_parsed)
        baseline_final = _score_final(case, baseline_final_parsed)
        medical_initial = _score_initial(case, medical_initial_parsed)
        medical_final = _score_final(case, medical_final_parsed)

        baseline_score = baseline_initial["score"] + baseline_final["score"]
        medical_score = medical_initial["score"] + medical_final["score"]
        score_max = baseline_initial["score_max"] + baseline_final["score_max"]

        baseline_total += baseline_score
        medical_total += medical_score
        total_max += score_max

        rows.append(
            {
                "case_id": str(case.get("case_id", "")).strip(),
                "utterance": utterance,
                "clarification_question": str(case.get("clarification_question", "")).strip(),
                "clarification_answer": str(case.get("clarification_answer", "")).strip(),
                "baseline_total_score": baseline_score,
                "medical_total_score": medical_score,
                "total_score_max": score_max,
                "baseline_initial": {**baseline_initial, "raw_json": str(baseline_initial_raw or "").strip()},
                "baseline_final": {**baseline_final, "raw_json": str(baseline_final_raw or "").strip()},
                "medical_initial": {**medical_initial, "raw_json": str(medical_initial_raw or "").strip()},
                "medical_final": {**medical_final, "raw_json": str(medical_final_raw or "").strip()},
            }
        )

    summary = {
        "generated_at_utc": _utc_now(),
        "model": model,
        "battery_path": str(battery_path),
        "slice_dir": str(slice_dir),
        "counts": {
            "cases": len(rows),
            "baseline_score": baseline_total,
            "medical_score": medical_total,
            "score_max": total_max,
        },
        "cases": rows,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    umls_mvp.write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(_render_summary_md(summary), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a clarification-aware medical prompt probe.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--context-length", type=int, default=DEFAULT_CONTEXT)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--shared-prompt", type=Path, default=DEFAULT_SHARED_PROMPT)
    parser.add_argument("--medical-supplement", type=Path, default=DEFAULT_MEDICAL_SUPPLEMENT)
    parser.add_argument("--battery", type=Path, default=DEFAULT_BATTERY)
    parser.add_argument("--slice-dir", type=Path, default=DEFAULT_SLICE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    summary = run_probe(
        base_url=args.base_url,
        model=args.model,
        context_length=args.context_length,
        timeout=args.timeout,
        shared_prompt_path=args.shared_prompt,
        medical_supplement_path=args.medical_supplement,
        battery_path=args.battery,
        slice_dir=args.slice_dir,
        out_dir=args.out_dir,
    )
    print(json.dumps(summary["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
