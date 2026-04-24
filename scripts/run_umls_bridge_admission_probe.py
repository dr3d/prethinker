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

from src import medical_profile, umls_mvp  # noqa: E402


DEFAULT_BRIDGE = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp" / "umls_bridge_facts.pl"
DEFAULT_BATTERY = ROOT / "docs" / "data" / "umls_bridge_admission_battery.json"
DEFAULT_OUT_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp" / "bridge_admission_latest"


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _base_parse(case: dict[str, Any]) -> dict[str, Any]:
    facts = [str(item).strip() for item in case.get("facts", []) or [] if str(item).strip()]
    logic_string = str(case.get("logic_string", "")).strip()
    if logic_string and not facts:
        facts = [logic_string]
    return {
        "intent": "assert_fact",
        "needs_clarification": False,
        "logic_string": logic_string,
        "facts": facts,
        "rules": [],
        "queries": [],
        "components": {},
        "ambiguities": [],
        "clarification_question": "",
        "clarification_reason": "",
        "rationale": "Synthetic parse for deterministic bridge admission probe.",
        "uncertainty_score": 0.1,
        "uncertainty_label": "low",
    }


def _case_outcome(case: dict[str, Any], bridge: dict[str, Any]) -> dict[str, Any]:
    utterance = str(case.get("utterance", "")).strip()
    expected_action = str(case.get("expected_action", "")).strip()
    guidance = medical_profile.bridge_admission_guidance(utterance, bridge)
    sanitized = medical_profile.sanitize_medical_parse_for_bridge(
        _base_parse(case),
        utterance=utterance,
        bridge=bridge,
    )
    needs_clarification = bool((sanitized or {}).get("needs_clarification", False))
    actual_action = "clarify" if needs_clarification else "admit"
    found_mentions = sorted({str(row.get("seed_id", "")).strip() for row in guidance.get("mentions", []) if str(row.get("seed_id", "")).strip()})
    expected_mentions = sorted(str(item).strip() for item in case.get("expected_mentions", []) or [] if str(item).strip())
    found_vague = sorted(str(row.get("surface", "")).strip() for row in guidance.get("vague_surfaces", []) if str(row.get("surface", "")).strip())
    blocking_vague = found_vague if bool(guidance.get("needs_clarification")) else []
    expected_vague = sorted(str(item).strip() for item in case.get("expected_vague_surfaces", []) or [] if str(item).strip())
    errors: list[str] = []
    if actual_action != expected_action:
        errors.append(f"expected action {expected_action}, got {actual_action}")
    if found_mentions != expected_mentions:
        errors.append(f"expected mentions {expected_mentions}, got {found_mentions}")
    if expected_vague and found_vague != expected_vague:
        errors.append(f"expected vague surfaces {expected_vague}, got {found_vague}")
    verdict = "pass" if not errors else "fail"
    return {
        "case_id": str(case.get("case_id", "")).strip(),
        "utterance": utterance,
        "expected_action": expected_action,
        "actual_action": actual_action,
        "expected_mentions": expected_mentions,
        "found_mentions": found_mentions,
        "expected_vague_surfaces": expected_vague,
        "found_vague_surfaces": found_vague,
        "blocking_vague_surfaces": blocking_vague,
        "clarification_reason": str((sanitized or {}).get("clarification_reason", "")).strip(),
        "ambiguities": list((sanitized or {}).get("ambiguities", []) or []),
        "verdict": verdict,
        "errors": errors,
        "notes": str(case.get("notes", "")).strip(),
    }


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UMLS Bridge Admission Probe",
        "",
        f"- generated_at_utc: `{summary['generated_at_utc']}`",
        f"- bridge_loaded: `{summary['bridge_loaded']}`",
        f"- bridge_concepts: `{summary['bridge_concepts']}`",
        f"- cases: `{summary['counts']['cases']}`",
        f"- pass / fail: `{summary['counts']['pass']}` / `{summary['counts']['fail']}`",
        "",
        "## Case Outcomes",
        "",
    ]
    for case in summary["cases"]:
        lines.append(
            f"- `{case['case_id']}` `{case['verdict']}` "
            f"action={case['actual_action']} expected={case['expected_action']} "
            f"mentions={case['found_mentions']} blocking_vague={case['blocking_vague_surfaces']}"
        )
    return "\n".join(lines) + "\n"


def run_probe(bridge_path: Path, battery_path: Path, out_dir: Path) -> dict[str, Any]:
    bridge = medical_profile.load_umls_bridge_facts(bridge_path)
    battery = umls_mvp.load_json(battery_path)
    cases = [_case_outcome(case, bridge) for case in battery.get("cases", []) or []]
    counts = {
        "cases": len(cases),
        "pass": sum(1 for case in cases if case["verdict"] == "pass"),
        "fail": sum(1 for case in cases if case["verdict"] == "fail"),
    }
    summary = {
        "generated_at_utc": _utc_now(),
        "bridge_path": str(bridge_path),
        "battery_path": str(battery_path),
        "bridge_loaded": bool(bridge.get("loaded")),
        "bridge_concepts": len(bridge.get("concepts", {}) or {}),
        "counts": counts,
        "cases": cases,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    umls_mvp.write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(_render_summary_md(summary), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic UMLS bridge admission preflight.")
    parser.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    parser.add_argument("--battery", type=Path, default=DEFAULT_BATTERY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    summary = run_probe(args.bridge, args.battery, args.out_dir)
    print(json.dumps(summary["counts"], indent=2))
    return 0 if summary["counts"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
