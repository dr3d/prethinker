#!/usr/bin/env python3
"""Audit closed carrier value domains in compile artifacts.

This is a typed-artifact audit. It does not read source text, QA questions, or
oracle answers. It checks only whether emitted facts use allowed compact values
for carrier slots that declare a value domain in the carrier registry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.carrier_contract_registry import carrier_contract  # noqa: E402


FACT_RE = re.compile(r"^\s*([a-z][A-Za-z0-9_]*)\((.*)\)\.\s*$")
CITATION_PAYLOAD_RE = re.compile(r"^(?:cfr_|fdca_|usc_|u_s_c_|us_c_|\d+_cfr_|\d+_usc_)", re.IGNORECASE)


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
    return 0 if args.exit_zero or not report["summary"]["violation_count"] else 1


def build_report(paths: list[Path]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    checked_slot_count = 0
    fact_count = 0
    facts_with_value_domains = 0
    for path in paths:
        facts = _facts_from_compile_json(path)
        fact_count += len(facts)
        fixture = path.parent.name
        for fact in facts:
            parsed = _parse_fact(fact)
            if parsed is None:
                continue
            signature = f"{parsed['predicate']}/{len(parsed['args'])}"
            contract = carrier_contract(signature)
            if not isinstance(contract, dict):
                continue
            arg_names = list(contract.get("args") or [])
            for index, raw_arg in enumerate(parsed["args"]):
                if index >= len(arg_names):
                    continue
                arg_name = str(arg_names[index]).strip()
                value = _normalize_arg(raw_arg)
                provenance_issue = _provenance_payload_issue(arg_name, value)
                if provenance_issue:
                    rows.append(
                        {
                            "fixture": fixture,
                            "compile_json": str(path),
                            "signature": signature,
                            "predicate": parsed["predicate"],
                            "arg_index": index + 1,
                            "arg_name": arg_name,
                            "value": value,
                            "allowed_values": [],
                            "issue": provenance_issue,
                            "fact": fact,
                        }
                    )
            domains = contract.get("value_domains")
            if not isinstance(domains, dict) or not domains:
                continue
            facts_with_value_domains += 1
            for index, raw_arg in enumerate(parsed["args"]):
                if index >= len(arg_names):
                    continue
                arg_name = str(arg_names[index]).strip()
                value = _normalize_arg(raw_arg)
                allowed_values = [
                    str(item).strip()
                    for item in domains.get(arg_name, [])
                    if str(item).strip()
                ]
                if not allowed_values:
                    continue
                checked_slot_count += 1
                if value not in set(allowed_values):
                    rows.append(
                        {
                            "fixture": fixture,
                            "compile_json": str(path),
                            "signature": signature,
                            "predicate": parsed["predicate"],
                            "arg_index": index + 1,
                            "arg_name": arg_name,
                            "value": value,
                            "allowed_values": allowed_values,
                            "issue": "value_not_allowed",
                            "fact": fact,
                        }
                    )
    return {
        "schema_version": "carrier_value_domain_audit_v1",
        "summary": {
            "compile_artifacts": len(paths),
            "fact_count": fact_count,
            "facts_with_value_domains": facts_with_value_domains,
            "checked_slot_count": checked_slot_count,
            "violation_count": len(rows),
            "status": "fail" if rows else "pass",
        },
        "violations": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Carrier Value-Domain Audit",
        "",
        f"- Compile artifacts: `{summary['compile_artifacts']}`",
        f"- Facts: `{summary['fact_count']}`",
        f"- Facts with value-domain slots: `{summary['facts_with_value_domains']}`",
        f"- Checked slots: `{summary['checked_slot_count']}`",
        f"- Violations: `{summary['violation_count']}`",
        f"- Status: `{summary['status']}`",
        "",
        "| Fixture | Signature | Arg | Issue | Value |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.get("violations", []):
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row.get("fixture", ""),
                row.get("signature", ""),
                row.get("arg_name", ""),
                row.get("issue", ""),
                row.get("value", ""),
            )
        )
    return "\n".join(lines) + "\n"


def _compile_paths(*, compile_root: Path | None, compile_jsons: list[Path], fixtures: set[str] | None) -> list[Path]:
    paths: list[Path] = [path.resolve() for path in compile_jsons]
    if compile_root is not None:
        root = compile_root.resolve()
        by_dir: dict[str, list[Path]] = {}
        for candidate in root.rglob("*.json"):
            if fixtures and not _path_matches_fixture(candidate, root=root, fixtures=fixtures):
                continue
            if not _has_source_compile(candidate):
                continue
            by_dir.setdefault(str(candidate.parent.resolve()), []).append(candidate)
        for candidates in by_dir.values():
            paths.append(sorted(candidates, key=lambda item: item.stat().st_mtime)[-1].resolve())
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path)] = path
    return list(unique.values())


def _path_matches_fixture(path: Path, *, root: Path, fixtures: set[str]) -> bool:
    try:
        parts = set(path.relative_to(root).parts)
    except ValueError:
        parts = set(path.parts)
    return bool(parts & fixtures)


def _has_source_compile(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(data, dict) and isinstance(data.get("source_compile"), dict)


def _facts_from_compile_json(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    source_compile = data.get("source_compile") if isinstance(data, dict) else {}
    if isinstance(source_compile, dict) and isinstance(source_compile.get("facts"), list):
        return [str(item).strip() for item in source_compile["facts"] if str(item).strip()]
    if isinstance(data, dict) and isinstance(data.get("facts"), list):
        return [str(item).strip() for item in data["facts"] if str(item).strip()]
    return []


def _parse_fact(fact: str) -> dict[str, Any] | None:
    match = FACT_RE.match(str(fact).strip())
    if not match:
        return None
    return {"predicate": match.group(1), "args": _split_args(match.group(2))}


def _normalize_arg(value: str) -> str:
    text = str(value or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        text = text[1:-1]
    return text.strip()


def _provenance_payload_issue(arg_name: str, value: str) -> str | None:
    if arg_name != "source_or_scope":
        return None
    normalized = str(value or "").strip().casefold()
    if CITATION_PAYLOAD_RE.match(normalized):
        return "citation_payload_in_source_or_scope"
    return None


def _split_args(raw: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escape = False
    depth = 0
    for char in raw:
        if quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == "(":
            depth += 1
            current.append(char)
            continue
        if char == ")":
            depth = max(0, depth - 1)
            current.append(char)
            continue
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current or raw.strip():
        args.append("".join(current).strip())
    return args


if __name__ == "__main__":
    raise SystemExit(main())
