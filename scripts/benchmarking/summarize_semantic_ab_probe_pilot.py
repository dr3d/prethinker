#!/usr/bin/env python3
"""Summarize lightweight expected-distinction checks for semantic A/B probes."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_JSONL = (
    REPO_ROOT
    / "tmp"
    / "public_benchmark"
    / "mutation_lab"
    / "semantic_probes"
    / "power_pilot_v2"
    / "frontier_battery_qa_qwen-qwen3.6-35b-a3b.jsonl"
)
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "semantic_probes" / "power_pilot_v2_summary.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "semantic_probes" / "power_pilot_v2_summary.md"
DEFAULT_OUT_CSV = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "semantic_probes" / "power_pilot_v2_summary.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-jsonl", type=Path, default=DEFAULT_RAW_JSONL)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = _load_rows(_resolve(args.raw_jsonl))
    summary = summarize(rows, source_path=str(_resolve(args.raw_jsonl)))
    out_json = _resolve(args.out_json)
    out_md = _resolve(args.out_md)
    out_csv = _resolve(args.out_csv)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(summary), encoding="utf-8")
    write_csv(summary, out_csv)
    print(json.dumps({"rows": len(rows), "json": str(out_json), "markdown": str(out_md), "csv": str(out_csv)}, indent=2))
    return 0


def summarize(rows: list[dict[str, Any]], *, source_path: str = "") -> dict[str, Any]:
    checked = [check_row(row) for row in rows]
    probe_rows = [row for row in checked if row["check_id"]]
    by_probe_variant: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in probe_rows:
        by_probe_variant.setdefault((row["probe_id"], row["variant_id"]), []).append(row)
    variants = []
    for (probe_id, variant_id), items in sorted(by_probe_variant.items()):
        variants.append(
            {
                "probe_id": probe_id,
                "variant_id": variant_id,
                "checked_rows": len(items),
                "passed_rows": sum(1 for item in items if item["passed"]),
                "failed_rows": sum(1 for item in items if not item["passed"]),
            }
        )
    return {
        "schema_version": "semantic_ab_probe_summary_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_path": source_path,
        "rows": len(rows),
        "checked_rows": len(probe_rows),
        "passed_rows": sum(1 for row in probe_rows if row["passed"]),
        "failed_rows": sum(1 for row in probe_rows if not row["passed"]),
        "variants": variants,
        "checks": probe_rows,
    }


def check_row(row: dict[str, Any]) -> dict[str, Any]:
    fixture = str(row.get("fixture", ""))
    probe_id, variant_id = _split_fixture(fixture)
    qid = str(row.get("question_id", ""))
    answer = str(row.get("answer", ""))
    check_id = ""
    passed = True
    reason = ""
    if probe_id == "absence_negative_evidence_vs_unresolved" and qid in {"q001", "q003", "q004", "q005", "q007"}:
        check_id = "absence_status"
        if qid == "q003":
            passed = _has_any(answer, ["no"]) and not _has_any(answer, ["north pine", "north pier glazing"])
            reason = "expects target applicant, not near-collision applicant"
        elif variant_id.startswith("unresolved_absence"):
            passed = _has_any(answer, ["pending", "unresolved", "confirm"])
            reason = "expects pending/unresolved status"
        elif variant_id.startswith("negative_absence"):
            passed = _has_any(answer, ["unavailable", "disqual", "not eligible", "denied", "no"]) and not _has_any(answer, ["pending", "unresolved"])
            reason = "expects disqualifying negative evidence"
    elif probe_id == "condition_time_vs_certification_time" and qid in {"q003", "q004", "q007"}:
        check_id = "clock_start"
        if variant_id.startswith("condition_clock"):
            passed = _has_time(answer, "17:00") and not _has_time(answer, "17:30")
            reason = "expects condition time to control"
        elif variant_id.startswith("certification_clock"):
            passed = _has_time(answer, "17:30")
            reason = "expects certification time to control"
    return {
        **row,
        "probe_id": probe_id,
        "variant_id": variant_id,
        "check_id": check_id,
        "passed": passed,
        "reason": reason,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Semantic A/B Probe Pilot Summary",
        "",
        f"- Generated UTC: `{summary.get('generated_utc', '')}`",
        f"- Rows: `{summary.get('rows', 0)}`",
        f"- Checked rows: `{summary.get('checked_rows', 0)}`",
        f"- Passed rows: `{summary.get('passed_rows', 0)}`",
        f"- Failed rows: `{summary.get('failed_rows', 0)}`",
        "",
        "## Variants",
        "",
        "| Probe | Variant | Checked | Passed | Failed |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for variant in summary.get("variants", []):
        lines.append(
            f"| `{variant['probe_id']}` | `{variant['variant_id']}` | {variant['checked_rows']} | {variant['passed_rows']} | {variant['failed_rows']} |"
        )
    failures = [row for row in summary.get("checks", []) if not row.get("passed")]
    lines.extend(["", "## Failures", ""])
    if not failures:
        lines.append("No failed distinction checks.")
    else:
        lines.extend(["| Fixture | Question | Reason | Answer |", "| --- | --- | --- | --- |"])
        for row in failures:
            lines.append(f"| `{row.get('fixture', '')}` | `{row.get('question_id', '')}` | {row.get('reason', '')} | {_cell(row.get('answer', ''))} |")
    lines.append("")
    return "\n".join(lines)


def write_csv(summary: dict[str, Any], path: Path) -> None:
    fieldnames = ["fixture", "probe_id", "variant_id", "question_id", "check_id", "passed", "reason", "answer"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary.get("checks", []):
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _split_fixture(fixture: str) -> tuple[str, str]:
    if "__" not in fixture:
        return fixture, ""
    probe_id, variant_id = fixture.split("__", 1)
    return probe_id, variant_id


def _has_any(text: str, needles: list[str]) -> bool:
    haystack = text.casefold()
    return any(needle.casefold() in haystack for needle in needles)


def _has_time(text: str, hhmm: str) -> bool:
    return re.search(rf"(?<!\d){re.escape(hhmm)}(?!\d)", text) is not None


def _cell(value: Any) -> str:
    return str(value or "").replace("\n", " ").replace("|", "/")[:240]


def _load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
