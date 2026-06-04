#!/usr/bin/env python3
"""Audit SEC skeleton value slots for axis mixing.

This audit does not read source prose, questions, or answers. It checks typed
facts and expected/forbidden fact files for SEC carrier slots whose value domain
has drifted across semantic axes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


FACT_RE = re.compile(r"^\s*([a-z][A-Za-z0-9_]*)\((.*)\)\.\s*$")

ITEM_STRUCTURAL_ROLES = {
    "substantive",
    "exhibit",
    "incorporated_reference",
    "other_role",
}
ITEM_TREATMENT_VALUES = {
    "filed",
    "furnished",
    "incorporated_by_reference",
    "not_deemed_filed",
    "not_stated",
}

EXHIBIT_LEGAL_TREATMENTS = {
    "filed",
    "furnished",
    "incorporated_by_reference",
    "not_stated",
}
EXHIBIT_CONTENT_FORMAT_VALUES = {
    "embedded_ixbrl",
    "inline_xbrl",
    "cover_page_ixbrl",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-root", type=Path, default=None)
    parser.add_argument("--compile-json", action="append", default=[], type=Path)
    parser.add_argument("--fact-file", action="append", default=[], type=Path)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        compile_roots=[args.compile_root] if args.compile_root else [],
        compile_jsons=args.compile_json,
        fact_files=args.fact_file,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.exit_zero or not report["summary"]["issue_count"] else 1


def build_report(
    *,
    compile_roots: list[Path],
    compile_jsons: list[Path],
    fact_files: list[Path],
) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    for path in fact_files:
        sources.append({"kind": "fact_file", "path": str(path), "facts": _facts_from_fact_file(path)})
    for path in compile_jsons:
        sources.append({"kind": "compile_json", "path": str(path), "facts": _facts_from_compile_json(path)})
    for root in compile_roots:
        for path in _compile_json_paths(root):
            sources.append({"kind": "compile_json", "path": str(path), "facts": _facts_from_compile_json(path)})

    issues: list[dict[str, Any]] = []
    fact_count = 0
    checked_fact_count = 0
    for source in sources:
        for fact in source["facts"]:
            fact_count += 1
            parsed = _parse_fact(fact)
            if parsed is None:
                continue
            if parsed["predicate"] == "sec_filing_item" and len(parsed["args"]) == 5:
                checked_fact_count += 1
                issues.extend(_audit_sec_filing_item(source, fact, parsed["args"]))
            elif parsed["predicate"] == "sec_exhibit" and len(parsed["args"]) == 5:
                checked_fact_count += 1
                issues.extend(_audit_sec_exhibit(source, fact, parsed["args"]))
            elif parsed["predicate"] == "sec_filing_item_treatment" and len(parsed["args"]) == 4:
                checked_fact_count += 1
                issues.extend(_audit_sec_filing_item_treatment(source, fact, parsed["args"]))

    return {
        "schema_version": "sec_value_axis_integrity_audit_v1",
        "summary": {
            "sources": len(sources),
            "fact_count": fact_count,
            "checked_sec_fact_count": checked_fact_count,
            "issue_count": len(issues),
            "status": "fail" if issues else "pass",
        },
        "issues": issues,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# SEC Value-Axis Integrity Audit",
        "",
        f"- Sources: `{summary['sources']}`",
        f"- Facts: `{summary['fact_count']}`",
        f"- Checked SEC item/exhibit/treatment facts: `{summary['checked_sec_fact_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Status: `{summary['status']}`",
        "",
        "| Source | Predicate | Slot | Value | Issue |",
        "| --- | --- | --- | --- | --- |",
    ]
    for issue in report.get("issues", []):
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                issue.get("source", ""),
                issue.get("predicate", ""),
                issue.get("slot", ""),
                issue.get("value", ""),
                issue.get("issue", ""),
            )
        )
    return "\n".join(lines) + "\n"


def _audit_sec_filing_item(source: dict[str, Any], fact: str, args: list[str]) -> list[dict[str, Any]]:
    role = _normalize_arg(args[3])
    issues: list[dict[str, Any]] = []
    if role in ITEM_TREATMENT_VALUES:
        issues.append(
            _issue(
                source=source,
                fact=fact,
                predicate="sec_filing_item/5",
                slot="item_role",
                value=role,
                issue="legal_treatment_in_item_role",
                expected_axis="structural_item_role",
            )
        )
    elif role not in ITEM_STRUCTURAL_ROLES:
        issues.append(
            _issue(
                source=source,
                fact=fact,
                predicate="sec_filing_item/5",
                slot="item_role",
                value=role,
                issue="unknown_item_role_axis",
                expected_axis="structural_item_role",
            )
        )
    return issues


def _audit_sec_exhibit(source: dict[str, Any], fact: str, args: list[str]) -> list[dict[str, Any]]:
    exhibit_kind = _normalize_arg(args[2])
    role = _normalize_arg(args[3])
    issues: list[dict[str, Any]] = []
    if role in EXHIBIT_CONTENT_FORMAT_VALUES:
        issues.append(
            _issue(
                source=source,
                fact=fact,
                predicate="sec_exhibit/5",
                slot="exhibit_role",
                value=role,
                issue="content_format_in_exhibit_legal_treatment_slot",
                expected_axis="legal_treatment",
            )
        )
    elif exhibit_kind == "cover_page_ixbrl" and role != "not_stated":
        issues.append(
            _issue(
                source=source,
                fact=fact,
                predicate="sec_exhibit/5",
                slot="exhibit_role",
                value=role,
                issue="cover_page_ixbrl_treatment_inferred",
                expected_axis="source_stated_exhibit_legal_treatment",
            )
        )
    elif role not in EXHIBIT_LEGAL_TREATMENTS:
        issues.append(
            _issue(
                source=source,
                fact=fact,
                predicate="sec_exhibit/5",
                slot="exhibit_role",
                value=role,
                issue="unknown_exhibit_role_axis",
                expected_axis="legal_treatment",
            )
        )
    return issues


def _audit_sec_filing_item_treatment(source: dict[str, Any], fact: str, args: list[str]) -> list[dict[str, Any]]:
    item_code = _normalize_arg(args[1])
    treatment = _normalize_arg(args[2])
    source_or_scope = _normalize_arg(args[3])
    issues: list[dict[str, Any]] = []
    if item_code == "item_9_01":
        issues.append(
            _issue(
                source=source,
                fact=fact,
                predicate="sec_filing_item_treatment/4",
                slot="item_code",
                value=item_code,
                issue="exhibit_item_treatment_misattached",
                expected_axis="substantive_item_treatment",
            )
        )
    if source_or_scope.startswith("exhibit_table_row_"):
        issues.append(
            _issue(
                source=source,
                fact=fact,
                predicate="sec_filing_item_treatment/4",
                slot="source_or_scope",
                value=source_or_scope,
                issue="item_treatment_from_exhibit_table_scope",
                expected_axis="substantive_item_treatment",
            )
        )
    if treatment not in ITEM_TREATMENT_VALUES:
        issues.append(
            _issue(
                source=source,
                fact=fact,
                predicate="sec_filing_item_treatment/4",
                slot="item_treatment",
                value=treatment,
                issue="unknown_item_treatment_axis",
                expected_axis="legal_treatment",
            )
        )
    return issues


def _issue(
    *,
    source: dict[str, Any],
    fact: str,
    predicate: str,
    slot: str,
    value: str,
    issue: str,
    expected_axis: str,
) -> dict[str, Any]:
    return {
        "source_kind": source["kind"],
        "source": source["path"],
        "predicate": predicate,
        "slot": slot,
        "value": value,
        "issue": issue,
        "expected_axis": expected_axis,
        "fact": fact,
    }


def _compile_json_paths(root: Path) -> list[Path]:
    if not root.exists():
        return []
    paths: list[Path] = []
    for path in root.rglob("*.json"):
        if _has_source_compile(path):
            paths.append(path)
    return sorted(paths)


def _has_source_compile(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(data, dict) and isinstance(data.get("source_compile"), dict)


def _facts_from_compile_json(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    source_compile = data.get("source_compile") if isinstance(data, dict) else {}
    if isinstance(source_compile, dict) and isinstance(source_compile.get("facts"), list):
        return [str(item).strip() for item in source_compile["facts"] if str(item).strip()]
    return []


def _facts_from_fact_file(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("%") and not line.lstrip().startswith("#")
    ]


def _parse_fact(fact: str) -> dict[str, Any] | None:
    match = FACT_RE.match(str(fact).strip())
    if not match:
        return None
    return {"predicate": match.group(1), "args": _split_args(match.group(2))}


def _split_args(payload: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in payload:
        if quote:
            current.append(char)
            if char == quote:
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
    tail = "".join(current).strip()
    if tail:
        args.append(tail)
    return args


def _normalize_arg(value: str) -> str:
    text = str(value).strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        text = text[1:-1]
    return text.strip().lower()


if __name__ == "__main__":
    raise SystemExit(main())
