#!/usr/bin/env python3
"""Audit domain omission accountability in compile artifacts.

This governance check reads only typed compile artifacts and model-authored
self_check fields. It does not read source prose, QA questions, or oracle
answers. If a compile profile offers domain_omission/5 and the model's
self_check describes an explicit missing/absent/not-shown domain item, the
typed facts must include a domain_omission/5 row.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


OMISSION_TEXT_RE = re.compile(
    r"\b(absent|absence|missing|not\s+shown|not\s+stated|not\s+available|none\s+found|no\s+[a-z0-9_ -]+(?:shown|stated|provided|emitted))\b",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-root", type=Path, default=None)
    parser.add_argument("--compile-json", action="append", default=[], type=Path)
    parser.add_argument("--fixture", action="append", default=[])
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = _compile_paths(
        compile_root=args.compile_root,
        compile_jsons=args.compile_json,
        fixtures={str(item).strip() for item in args.fixture if str(item).strip()} or None,
    )
    report = build_report(paths)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.exit_zero or not report["summary"]["blocker_count"] else 1


def build_report(paths: list[Path]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        source_compile = data.get("source_compile") if isinstance(data, dict) else {}
        if not isinstance(source_compile, dict):
            continue
        if not _domain_omission_available(data):
            continue
        facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()] if isinstance(source_compile.get("facts"), list) else []
        has_domain_omission = any(fact.startswith("domain_omission(") for fact in facts)
        omission_notes = [
            text
            for text in _self_check_texts(source_compile.get("self_check"))
            if OMISSION_TEXT_RE.search(text)
        ]
        if omission_notes and not has_domain_omission:
            rows.append(
                {
                    "fixture": path.parent.name,
                    "compile_json": str(path),
                    "class": "self_check_omission_without_domain_omission_fact",
                    "self_check_omission_notes": omission_notes,
                }
            )
    return {
        "schema_version": "domain_omission_accountability_audit_v1",
        "summary": {
            "compile_artifacts": len(paths),
            "blocker_count": len(rows),
            "status": "fail" if rows else "pass",
        },
        "rows": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Domain Omission Accountability Audit",
        "",
        f"- Compile artifacts: `{summary['compile_artifacts']}`",
        f"- Blockers: `{summary['blocker_count']}`",
        f"- Status: `{summary['status']}`",
        "",
        "| Fixture | Class | Self-check omission notes |",
        "| --- | --- | --- |",
    ]
    for row in report.get("rows", []):
        notes = "; ".join(str(item).replace("|", "/") for item in row.get("self_check_omission_notes", []))
        lines.append(f"| `{row.get('fixture', '')}` | `{row.get('class', '')}` | {notes} |")
    return "\n".join(lines) + "\n"


def _domain_omission_available(data: dict[str, Any]) -> bool:
    parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
    predicates = parsed.get("candidate_predicates") if isinstance(parsed.get("candidate_predicates"), list) else []
    return any(
        isinstance(item, dict) and str(item.get("signature", "")).strip() == "domain_omission/5"
        for item in predicates
    )


def _self_check_texts(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        for item in value.values():
            out.extend(_self_check_texts(item))
    elif isinstance(value, list):
        for item in value:
            out.extend(_self_check_texts(item))
    elif isinstance(value, str):
        text = value.strip()
        if text:
            out.append(text)
    return out


def _compile_paths(*, compile_root: Path | None, compile_jsons: list[Path], fixtures: set[str] | None) -> list[Path]:
    paths: list[Path] = [path.resolve() for path in compile_jsons]
    if compile_root is not None:
        root = compile_root.resolve()
        for fixture_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            if fixtures and fixture_dir.name not in fixtures:
                continue
            candidates = sorted(fixture_dir.glob("*.json"), key=lambda item: item.stat().st_mtime)
            if candidates:
                paths.append(candidates[-1].resolve())
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path)] = path
    return list(unique.values())


if __name__ == "__main__":
    raise SystemExit(main())
