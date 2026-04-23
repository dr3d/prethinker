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


DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3.5:9b"
DEFAULT_CONTEXT = 8192
DEFAULT_TIMEOUT = 90
DEFAULT_SHARED_PROMPT = ROOT / "modelfiles" / "semantic_parser_system_prompt.md"
DEFAULT_MEDICAL_SUPPLEMENT = ROOT / "modelfiles" / "medical_compiler_prompt_supplement.md"
DEFAULT_BATTERY = ROOT / "docs" / "data" / "medical_prompt_probe_battery.json"
DEFAULT_SLICE_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp"
DEFAULT_OUT_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp" / "medical_prompt_probe_latest"

MEDICAL_PREDICATES = medical_profile.canonical_predicate_signatures(
    medical_profile.load_profile_manifest()
)


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _render_concept_hints(concepts: list[dict[str, Any]]) -> str:
    return medical_profile.render_concept_hints(concepts)


def _build_medical_guide(shared_prompt: str, supplement: str, concepts: list[dict[str, Any]]) -> str:
    return medical_profile.build_medical_profile_guide(
        shared_prompt=shared_prompt,
        supplement=supplement,
        concepts=concepts,
        known_predicates=MEDICAL_PREDICATES,
    )


def _score_parse(case: dict[str, Any], parsed: dict[str, Any] | None) -> dict[str, Any]:
    expected_route = str(case.get("expected_route", "")).strip()
    expect_needs_clarification = bool(case.get("expect_needs_clarification", False))
    expect_empty_logic = bool(case.get("expect_empty_logic", False))
    expected_logic_contains = [str(item).strip() for item in case.get("expected_logic_contains", []) or [] if str(item).strip()]
    forbidden_logic_contains = [str(item).strip() for item in case.get("forbidden_logic_contains", []) or [] if str(item).strip()]

    logic_string = ""
    intent = ""
    needs_clarification = False
    if isinstance(parsed, dict):
        logic_string = str(parsed.get("logic_string", "")).strip()
        intent = str(parsed.get("intent", "")).strip()
        needs_clarification = bool(parsed.get("needs_clarification", False))

    matched_expected = [token for token in expected_logic_contains if token and token in logic_string]
    hit_forbidden = [token for token in forbidden_logic_contains if token and token in logic_string]

    points_possible = 3 + len(expected_logic_contains) + len(forbidden_logic_contains)
    points = 0
    if intent == expected_route:
        points += 1
    if needs_clarification == expect_needs_clarification:
        points += 1
    if (not expect_empty_logic) or (logic_string == ""):
        points += 1
    points += len(matched_expected)
    points += len(forbidden_logic_contains) - len(hit_forbidden)

    return {
        "intent": intent,
        "needs_clarification": needs_clarification,
        "expect_empty_logic": expect_empty_logic,
        "logic_string": logic_string,
        "matched_expected": matched_expected,
        "missing_expected": [token for token in expected_logic_contains if token not in matched_expected],
        "hit_forbidden": hit_forbidden,
        "score": points,
        "score_max": points_possible,
    }


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


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Medical Prompt Probe",
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
            f"- `{case['case_id']}` baseline={case['baseline']['score']}/{case['baseline']['score_max']} "
            f"medical={case['medical']['score']}/{case['medical']['score_max']}"
        )
        lines.append(f"  - utterance: `{case['utterance']}`")
        lines.append(f"  - baseline logic: `{case['baseline']['logic_string']}`")
        lines.append(f"  - medical logic: `{case['medical']['logic_string']}`")
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

    cases: list[dict[str, Any]] = []
    total_baseline = 0
    total_medical = 0
    total_max = 0

    for case in battery.get("cases", []) or []:
        utterance = str(case.get("utterance", "")).strip()
        route = str(case.get("route", "assert_fact")).strip()
        baseline_parsed, baseline_raw = _run_parse(
            utterance=utterance,
            route=route,
            prompt_guide=shared_prompt,
            known_predicates=[],
            base_url=base_url,
            model=model,
            context_length=context_length,
            timeout=timeout,
        )
        medical_parsed, medical_raw = _run_parse(
            utterance=utterance,
            route=route,
            prompt_guide=medical_guide,
            known_predicates=MEDICAL_PREDICATES,
            base_url=base_url,
            model=model,
            context_length=context_length,
            timeout=timeout,
        )
        medical_parsed = medical_profile.sanitize_medical_parse_for_clarification(
            medical_parsed,
            utterance=utterance,
        )
        baseline_score = _score_parse(case, baseline_parsed)
        medical_score = _score_parse(case, medical_parsed)
        total_baseline += baseline_score["score"]
        total_medical += medical_score["score"]
        total_max += baseline_score["score_max"]
        cases.append(
            {
                "case_id": str(case.get("case_id", "")).strip(),
                "utterance": utterance,
                "route": route,
                "baseline": {
                    **baseline_score,
                    "raw_json": raw_or_empty(baseline_raw),
                },
                "medical": {
                    **medical_score,
                    "raw_json": raw_or_empty(medical_raw),
                },
            }
        )

    summary = {
        "generated_at_utc": _utc_now(),
        "model": model,
        "shared_prompt_path": str(shared_prompt_path),
        "medical_supplement_path": str(medical_supplement_path),
        "battery_path": str(battery_path),
        "slice_dir": str(slice_dir),
        "counts": {
            "cases": len(cases),
            "baseline_score": total_baseline,
            "medical_score": total_medical,
            "score_max": total_max,
        },
        "cases": cases,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    umls_mvp.write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(_render_summary_md(summary), encoding="utf-8")
    return summary


def raw_or_empty(value: Any) -> str:
    return str(value or "").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline prompt vs bounded medical prompt supplement.")
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
