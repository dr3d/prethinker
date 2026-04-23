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

from scripts import (  # noqa: E402
    run_medical_clarification_probe,
    run_medical_prompt_probe,
    run_umls_mvp_clinical_probe,
    run_umls_mvp_probe,
)
from src import medical_profile, umls_mvp  # noqa: E402


DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3.5:9b"
DEFAULT_CONTEXT = 8192
DEFAULT_TIMEOUT = 90
DEFAULT_PROFILE = ROOT / "modelfiles" / "profile.medical.v0.json"
DEFAULT_SHARED_PROMPT = ROOT / "modelfiles" / "semantic_parser_system_prompt.md"
DEFAULT_SLICE_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp"
DEFAULT_OUT_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp" / "medical_profile_suite_latest"


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _render_summary_md(summary: dict[str, Any]) -> str:
    counts = summary["counts"]
    lines = [
        "# Medical Profile Suite",
        "",
        f"- generated_at_utc: `{summary['generated_at_utc']}`",
        f"- profile_id: `{summary['profile_id']}`",
        f"- model: `{summary['model']}`",
        "",
        "## Rollup",
        "",
        f"- sharp-memory: `{counts['sharp_memory_pass']}/{counts['sharp_memory_cases']}` pass, `{counts['sharp_memory_warn']}` warn, `{counts['sharp_memory_fail']}` fail",
        f"- clinical checks: `{counts['clinical_checks_pass']}/{counts['clinical_checks_cases']}` pass, `{counts['clinical_checks_warn']}` warn, `{counts['clinical_checks_fail']}` fail",
        f"- prompt probe: `{counts['prompt_medical_score']}/{counts['prompt_score_max']}` vs baseline `{counts['prompt_baseline_score']}/{counts['prompt_score_max']}`",
        f"- clarification probe: `{counts['clarification_medical_score']}/{counts['clarification_score_max']}` vs baseline `{counts['clarification_baseline_score']}/{counts['clarification_score_max']}`",
        "",
        "## Assets",
        "",
    ]
    for key, value in summary["profile_assets"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This suite is manifest-driven, so the bounded medical profile can now be exercised as one package rather than a set of loosely coupled probe commands.",
            "- The current profile remains a bounded normalization and clarification-aware memory lane, not a general clinical reasoning profile.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_suite(
    *,
    base_url: str,
    model: str,
    context_length: int,
    timeout: int,
    profile_path: Path,
    shared_prompt_path: Path,
    slice_dir: Path,
    out_dir: Path,
) -> dict[str, Any]:
    manifest = medical_profile.load_profile_manifest(profile_path)
    assets = medical_profile.resolve_profile_paths(profile_path)
    prompt_summary = run_medical_prompt_probe.run_probe(
        base_url=base_url,
        model=model,
        context_length=context_length,
        timeout=timeout,
        shared_prompt_path=shared_prompt_path,
        medical_supplement_path=assets["prompt_supplement"],
        battery_path=run_medical_prompt_probe.DEFAULT_BATTERY,
        slice_dir=slice_dir,
        out_dir=out_dir / "prompt_probe",
    )
    clarification_summary = run_medical_clarification_probe.run_probe(
        base_url=base_url,
        model=model,
        context_length=context_length,
        timeout=timeout,
        shared_prompt_path=shared_prompt_path,
        medical_supplement_path=assets["prompt_supplement"],
        battery_path=run_medical_clarification_probe.DEFAULT_BATTERY,
        slice_dir=slice_dir,
        out_dir=out_dir / "clarification_probe",
    )
    sharp_memory_summary = run_umls_mvp_probe.run_probe(
        slice_dir=slice_dir,
        battery_path=run_umls_mvp_probe.DEFAULT_BATTERY,
        out_dir=out_dir / "sharp_memory_probe",
    )
    clinical_summary = run_umls_mvp_clinical_probe.run_probe(
        slice_dir=slice_dir,
        battery_path=run_umls_mvp_clinical_probe.DEFAULT_BATTERY,
        out_dir=out_dir / "clinical_probe",
    )

    summary = {
        "generated_at_utc": _utc_now(),
        "profile_id": str(manifest.get("profile_id", "")).strip(),
        "model": model,
        "profile_assets": {key: str(path) for key, path in assets.items()},
        "counts": {
            "sharp_memory_cases": int(sharp_memory_summary["counts"]["cases"]),
            "sharp_memory_pass": int(sharp_memory_summary["counts"]["pass"]),
            "sharp_memory_warn": int(sharp_memory_summary["counts"]["warn"]),
            "sharp_memory_fail": int(sharp_memory_summary["counts"]["fail"]),
            "clinical_checks_cases": int(clinical_summary["counts"]["cases"]),
            "clinical_checks_pass": int(clinical_summary["counts"]["pass"]),
            "clinical_checks_warn": int(clinical_summary["counts"]["warn"]),
            "clinical_checks_fail": int(clinical_summary["counts"]["fail"]),
            "prompt_baseline_score": int(prompt_summary["counts"]["baseline_score"]),
            "prompt_medical_score": int(prompt_summary["counts"]["medical_score"]),
            "prompt_score_max": int(prompt_summary["counts"]["score_max"]),
            "clarification_baseline_score": int(clarification_summary["counts"]["baseline_score"]),
            "clarification_medical_score": int(clarification_summary["counts"]["medical_score"]),
            "clarification_score_max": int(clarification_summary["counts"]["score_max"]),
        },
        "component_outputs": {
            "prompt_probe": str(out_dir / "prompt_probe" / "summary.json"),
            "clarification_probe": str(out_dir / "clarification_probe" / "summary.json"),
            "sharp_memory_probe": str(out_dir / "sharp_memory_probe" / "summary.json"),
            "clinical_probe": str(out_dir / "clinical_probe" / "summary.json"),
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    umls_mvp.write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(_render_summary_md(summary), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded medical@v0 profile suite as one manifest-driven package.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--context-length", type=int, default=DEFAULT_CONTEXT)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--shared-prompt", type=Path, default=DEFAULT_SHARED_PROMPT)
    parser.add_argument("--slice-dir", type=Path, default=DEFAULT_SLICE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    summary = run_suite(
        base_url=args.base_url,
        model=args.model,
        context_length=args.context_length,
        timeout=args.timeout,
        profile_path=args.profile,
        shared_prompt_path=args.shared_prompt,
        slice_dir=args.slice_dir,
        out_dir=args.out_dir,
    )
    print(json.dumps(summary["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
