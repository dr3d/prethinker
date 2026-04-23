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

from src import umls_mvp  # noqa: E402


DEFAULT_SLICE_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp"
DEFAULT_BATTERY = ROOT / "docs" / "data" / "umls_mvp_clinical_checks_battery.json"
DEFAULT_OUT_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp" / "clinical_probe_latest"


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _fired_checks(found_seed_ids: set[str], checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fired: list[dict[str, Any]] = []
    for check in checks:
        required = set(str(item).strip() for item in check.get("required_seed_ids", []) or [] if str(item).strip())
        if required and required.issubset(found_seed_ids):
            fired.append(
                {
                    "check_id": str(check.get("check_id", "")).strip(),
                    "label": str(check.get("label", "")).strip(),
                    "kind": str(check.get("kind", "")).strip(),
                    "required_seed_ids": sorted(required),
                }
            )
    fired.sort(key=lambda row: row["check_id"])
    return fired


def _case_outcome(case: dict[str, Any], checks: list[dict[str, Any]], alias_records: list[dict[str, Any]]) -> dict[str, Any]:
    utterance = str(case.get("utterance", "")).strip()
    matches = umls_mvp.extract_grounded_mentions(utterance, alias_records)
    found_seed_ids = {str(row.get("seed_id", "")).strip() for row in matches}
    fired = _fired_checks(found_seed_ids, checks)
    actual = {str(row.get("check_id", "")).strip() for row in fired}
    expected = {str(item).strip() for item in case.get("expected_checks", []) or [] if str(item).strip()}
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        verdict = "warn" if (not missing and unexpected) or (missing and not unexpected) else "fail"
    else:
        verdict = "pass"
    return {
        "case_id": str(case.get("case_id", "")).strip(),
        "utterance": utterance,
        "found_seed_ids": sorted(found_seed_ids),
        "expected_checks": sorted(expected),
        "fired_checks": fired,
        "missing_checks": missing,
        "unexpected_checks": unexpected,
        "verdict": verdict,
        "notes": str(case.get("notes", "")).strip(),
    }


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UMLS MVP Clinical Probe",
        "",
        f"- generated_at_utc: `{summary['generated_at_utc']}`",
        f"- cases: `{summary['counts']['cases']}`",
        f"- pass / warn / fail: `{summary['counts']['pass']}` / `{summary['counts']['warn']}` / `{summary['counts']['fail']}`",
        "",
        "## Case Outcomes",
        "",
    ]
    for case in summary["cases"]:
        fired_ids = [row["check_id"] for row in case["fired_checks"]]
        lines.append(
            f"- `{case['case_id']}` `{case['verdict']}` "
            f"expected={case['expected_checks']} fired={fired_ids} "
            f"found={case['found_seed_ids']}"
        )
    return "\n".join(lines) + "\n"


def run_probe(slice_dir: Path, battery_path: Path, out_dir: Path) -> dict[str, Any]:
    manifest = umls_mvp.load_json(slice_dir / "manifest.json")
    concepts = _load_jsonl(slice_dir / "concepts.jsonl")
    battery = umls_mvp.load_json(battery_path)
    checks = list(battery.get("checks", []) or [])
    alias_records = umls_mvp.build_alias_records(manifest, concepts)
    cases = [_case_outcome(case, checks, alias_records) for case in battery.get("cases", []) or []]
    counts = {
        "cases": len(cases),
        "pass": sum(1 for case in cases if case["verdict"] == "pass"),
        "warn": sum(1 for case in cases if case["verdict"] == "warn"),
        "fail": sum(1 for case in cases if case["verdict"] == "fail"),
    }
    summary = {
        "generated_at_utc": _utc_now(),
        "slice_dir": str(slice_dir),
        "battery_path": str(battery_path),
        "counts": counts,
        "cases": cases,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    umls_mvp.write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(_render_summary_md(summary), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded UMLS MVP clinical-check probe.")
    parser.add_argument("--slice-dir", type=Path, default=DEFAULT_SLICE_DIR)
    parser.add_argument("--battery", type=Path, default=DEFAULT_BATTERY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    summary = run_probe(args.slice_dir, args.battery, args.out_dir)
    print(json.dumps(summary["counts"], indent=2))
    return 0 if summary["counts"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
