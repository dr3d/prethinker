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


DEFAULT_BATTERY = ROOT / "docs" / "data" / "umls_mvp_sharp_memory_battery.json"
DEFAULT_SLICE_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp"
DEFAULT_OUT_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp" / "probe_latest"


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


def _case_outcome(case: dict[str, Any], alias_records: list[dict[str, Any]]) -> dict[str, Any]:
    utterance = str(case.get("utterance", "")).strip()
    expected = set(str(item).strip() for item in case.get("expected_seed_ids", []) or [] if str(item).strip())
    optional = set(str(item).strip() for item in case.get("optional_seed_ids", []) or [] if str(item).strip())
    matches = umls_mvp.extract_grounded_mentions(utterance, alias_records)
    found = {str(row.get("seed_id", "")).strip() for row in matches}
    missing = sorted(expected - found)
    unexpected = sorted(found - expected - optional)
    if expected:
        recall = (len(expected) - len(missing)) / float(len(expected))
    else:
        recall = 1.0 if not found else 0.0
    if found:
        precision = (len(found) - len(unexpected)) / float(len(found))
    else:
        precision = 1.0 if not expected else 0.0
    storage_expectation = str(case.get("storage_expectation", "sharp_memory_candidate")).strip()
    if missing or unexpected:
        verdict = "warn" if (not missing and unexpected) or (missing and not unexpected) else "fail"
    else:
        verdict = "pass"
    if storage_expectation == "abstain" and found:
        verdict = "fail"
    if storage_expectation == "abstain" and not found:
        verdict = "pass"
    if storage_expectation == "context_only" and missing:
        verdict = "warn"
    return {
        "case_id": str(case.get("case_id", "")).strip(),
        "utterance": utterance,
        "difficulty": str(case.get("difficulty", "core")).strip(),
        "storage_expectation": storage_expectation,
        "expected_seed_ids": sorted(expected),
        "found_seed_ids": sorted(found),
        "missing_seed_ids": missing,
        "unexpected_seed_ids": unexpected,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "verdict": verdict,
        "matches": [
            {
                "seed_id": str(row.get("seed_id", "")).strip(),
                "matched_alias": str(row.get("matched_alias", "")).strip(),
                "preferred_name": str(row.get("preferred_name", "")).strip(),
                "semantic_types": list(row.get("semantic_types", []) or []),
            }
            for row in matches
        ],
        "notes": str(case.get("notes", "")).strip(),
    }


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UMLS MVP Probe",
        "",
        f"- generated_at_utc: `{summary['generated_at_utc']}`",
        f"- resolved seeds: `{summary['manifest_counts'].get('resolved_seeds', 0)}`",
        f"- concept count: `{summary['manifest_counts'].get('concepts', 0)}`",
        f"- relation count: `{summary['manifest_counts'].get('relations', 0)}`",
        f"- cases: `{summary['counts']['cases']}`",
        f"- pass / warn / fail: `{summary['counts']['pass']}` / `{summary['counts']['warn']}` / `{summary['counts']['fail']}`",
        f"- average precision: `{summary['averages']['precision']:.3f}`",
        f"- average recall: `{summary['averages']['recall']:.3f}`",
        "",
        "## Case Outcomes",
        "",
    ]
    for case in summary["cases"]:
        lines.append(
            f"- `{case['case_id']}` `{case['verdict']}` "
            f"expected={case['expected_seed_ids']} found={case['found_seed_ids']} "
            f"missing={case['missing_seed_ids']} unexpected={case['unexpected_seed_ids']}"
        )
    return "\n".join(lines) + "\n"


def run_probe(slice_dir: Path, battery_path: Path, out_dir: Path) -> dict[str, Any]:
    manifest = umls_mvp.load_json(slice_dir / "manifest.json")
    concepts = _load_jsonl(slice_dir / "concepts.jsonl")
    battery = umls_mvp.load_json(battery_path)
    alias_records = umls_mvp.build_alias_records(manifest, concepts)
    cases = [
        _case_outcome(case, alias_records)
        for case in battery.get("utterance_cases", []) or []
    ]
    counts = {
        "cases": len(cases),
        "pass": sum(1 for case in cases if case["verdict"] == "pass"),
        "warn": sum(1 for case in cases if case["verdict"] == "warn"),
        "fail": sum(1 for case in cases if case["verdict"] == "fail"),
    }
    averages = {
        "precision": sum(case["precision"] for case in cases) / float(len(cases) or 1),
        "recall": sum(case["recall"] for case in cases) / float(len(cases) or 1),
    }
    summary = {
        "generated_at_utc": _utc_now(),
        "slice_dir": str(slice_dir),
        "battery_path": str(battery_path),
        "manifest_counts": dict(manifest.get("counts", {})),
        "counts": counts,
        "averages": averages,
        "cases": cases,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    umls_mvp.write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(_render_summary_md(summary), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded UMLS MVP sharp-memory probe.")
    parser.add_argument("--slice-dir", type=Path, default=DEFAULT_SLICE_DIR)
    parser.add_argument("--battery", type=Path, default=DEFAULT_BATTERY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    summary = run_probe(args.slice_dir, args.battery, args.out_dir)
    print(json.dumps(summary["counts"], indent=2))
    return 0 if summary["counts"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
