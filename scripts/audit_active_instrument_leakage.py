#!/usr/bin/env python3
"""Audit active runtime code for research-fixture leakage markers.

This scan intentionally ignores docs, tests, datasets, and archived artifacts.
It is a tripwire for accidental promotion of fixture names, row ids, answer
phrases, or one-document constants into the active instrument.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATHS = (
    REPO_ROOT / "scripts" / "run_domain_bootstrap_qa.py",
    REPO_ROOT / "scripts" / "run_domain_bootstrap_file.py",
    REPO_ROOT / "scripts" / "run_domain_bootstrap_file_batch.py",
    REPO_ROOT / "src",
)

FORBIDDEN_PATTERNS = {
    "dataset_or_batch_name": re.compile(
        r"\b(?:fresh_ugly|ugly_public|sealed_unseen|native_corpus|story_worlds_draw|"
        r"fda_warning_ugly|ntsb_(?:aviation|marine|surface)_ugly|osha_incident_ugly|"
        r"sec_material_event_ugly)\b",
        re.IGNORECASE,
    ),
    "native_fixture_name": re.compile(
        r"\b(?:black_lantern_maze|identifier_ledger_torture|lantern_school_field_trip|"
        r"greenhouse_quarantine|amended_lease_register|thornfield_variance|oxalis)\b",
        re.IGNORECASE,
    ),
    "narrative_probe_name": re.compile(r"\b(?:sherlock|holmes|red_headed_league|airlock)\b", re.IGNORECASE),
    "public_fixture_answer_phrase": re.compile(
        r"\b(?:Medical Products Laboratories|Baylor J\.? Tregre|Pool Corporation|"
        r"American Airlines flight 191|Plexion|Hydro-Q)\b",
        re.IGNORECASE,
    ),
}

DOCUMENT_CLASS_WARNINGS = {
    "agency_or_domain_token": re.compile(r"\b(?:FDA|OSHA|NTSB|SEC|CFR|CGMP|NWS|MNOSHA|FEI|MARCS|CMS)\b"),
    "document_specific_code": re.compile(r"\b(?:KGLS|UPS Flight 2976|Flight 191)\b", re.IGNORECASE),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", type=Path, default=[])
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = tuple(args.path) if args.path else DEFAULT_PATHS
    report = build_report(paths)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["summary"]["forbidden_hit_count"] else 0


def build_report(paths: tuple[Path, ...]) -> dict[str, Any]:
    files = list(_iter_files(paths))
    forbidden_hits = _scan(files, FORBIDDEN_PATTERNS)
    warning_hits = _scan(files, DOCUMENT_CLASS_WARNINGS)
    return {
        "schema_version": "active_instrument_leakage_audit_v1",
        "scope": "active runtime scripts and src only; docs/tests/datasets excluded",
        "summary": {
            "file_count": len(files),
            "forbidden_hit_count": len(forbidden_hits),
            "warning_hit_count": len(warning_hits),
            "status": "fail" if forbidden_hits else "pass",
        },
        "forbidden_hits": forbidden_hits,
        "warning_hits": warning_hits,
    }


def _iter_files(paths: tuple[Path, ...]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        path = raw if raw.is_absolute() else REPO_ROOT / raw
        if path.is_file() and path.suffix == ".py":
            out.append(path)
        elif path.is_dir():
            out.extend(sorted(item for item in path.rglob("*.py") if _is_active_path(item)))
    return sorted(set(out))


def _is_active_path(path: Path) -> bool:
    parts = {part.casefold() for part in path.parts}
    return not ({"tests", "docs", "datasets", "tmp", "__pycache__"} & parts)


def _scan(files: list[Path], patterns: dict[str, re.Pattern[str]]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        for lineno, line in enumerate(lines, start=1):
            for label, pattern in patterns.items():
                for match in pattern.finditer(line):
                    hits.append(
                        {
                            "file": str(path.relative_to(REPO_ROOT)),
                            "line": lineno,
                            "class": label,
                            "match": match.group(0),
                            "text": line.strip()[:220],
                        }
                    )
    return hits


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Active Instrument Leakage Audit",
        "",
        f"- Schema: `{report.get('schema_version')}`",
        f"- Scope: {report.get('scope')}",
        f"- Status: `{summary.get('status')}`",
        f"- Files scanned: `{summary.get('file_count')}`",
        f"- Forbidden hits: `{summary.get('forbidden_hit_count')}`",
        f"- Warning hits: `{summary.get('warning_hit_count')}`",
    ]
    for title, key in (("Forbidden Hits", "forbidden_hits"), ("Warnings", "warning_hits")):
        rows = report.get(key, [])
        if not rows:
            continue
        lines.extend(["", f"## {title}", "", "| File | Line | Class | Match |", "| --- | ---: | --- | --- |"])
        for row in rows:
            lines.append(
                "| `{file}` | {line} | `{cls}` | `{match}` |".format(
                    file=row.get("file", ""),
                    line=row.get("line", ""),
                    cls=row.get("class", ""),
                    match=row.get("match", ""),
                )
            )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
