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
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.carrier_contract_registry import carrier_contract  # noqa: E402


FACT_RE = re.compile(r"^\s*([a-z][A-Za-z0-9_]*)\((.*)\)\.\s*$")
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
        facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()] if isinstance(source_compile.get("facts"), list) else []
        domain_omission_available = _domain_omission_available(data) or _facts_include_domain_omission(facts)
        if not domain_omission_available:
            continue
        for fact in facts:
            placeholder = _ordinary_omission_placeholder(fact)
            if placeholder:
                rows.append(
                    {
                        "fixture": path.parent.name,
                        "compile_json": str(path),
                        "class": "ordinary_carrier_omission_placeholder",
                        "fact": fact,
                        "carrier_signature": placeholder,
                        "self_check_omission_notes": [],
                    }
                )
        domain_omission_rows = _domain_omission_rows(facts)
        has_domain_omission = bool(domain_omission_rows)
        allowed_omissions = _registered_domain_omission_triples()
        for row in domain_omission_rows:
            if carrier_contract(str(row.get("carrier_signature", ""))) is None:
                rows.append(
                    {
                        "fixture": path.parent.name,
                        "compile_json": str(path),
                        "class": "invalid_domain_omission_carrier_signature",
                        "fact": row.get("fact", ""),
                        "carrier_signature": row.get("carrier_signature", ""),
                        "self_check_omission_notes": [],
                    }
                )
            elif (
                str(row.get("carrier_signature", "")),
                str(row.get("omission_kind", "")),
                str(row.get("reason_code", "")),
            ) not in allowed_omissions:
                rows.append(
                    {
                        "fixture": path.parent.name,
                        "compile_json": str(path),
                        "class": "invalid_domain_omission_registry_value",
                        "fact": row.get("fact", ""),
                        "carrier_signature": row.get("carrier_signature", ""),
                        "self_check_omission_notes": [],
                    }
                )
        for fact in _sec_signature_omission_contradictions(facts):
            rows.append(
                {
                    "fixture": path.parent.name,
                    "compile_json": str(path),
                    "class": "domain_omission_contradicts_emitted_carrier",
                    "fact": fact,
                    "carrier_signature": "sec_signatory/5",
                    "self_check_omission_notes": [],
                }
            )
        for fact in _osha_accident_omission_contradictions(facts):
            rows.append(
                {
                    "fixture": path.parent.name,
                    "compile_json": str(path),
                    "class": "domain_omission_contradicts_emitted_carrier",
                    "fact": fact,
                    "carrier_signature": "osha_accident/7",
                    "self_check_omission_notes": [],
                }
            )
        for fact in _ntsb_report_omission_contradictions(facts):
            rows.append(
                {
                    "fixture": path.parent.name,
                    "compile_json": str(path),
                    "class": "domain_omission_contradicts_emitted_carrier",
                    "fact": fact,
                    "carrier_signature": "ntsb_report/5",
                    "self_check_omission_notes": [],
                }
            )
        if _self_check_omission_requires_domain_omission(data):
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
        "| Fixture | Class | Detail |",
        "| --- | --- | --- |",
    ]
    for row in report.get("rows", []):
        notes = "; ".join(str(item).replace("|", "/") for item in row.get("self_check_omission_notes", []))
        detail = notes or str(row.get("carrier_signature", "")).replace("|", "/") or str(row.get("fact", "")).replace("|", "/")
        lines.append(f"| `{row.get('fixture', '')}` | `{row.get('class', '')}` | {detail} |")
    return "\n".join(lines) + "\n"


def _domain_omission_available(data: dict[str, Any]) -> bool:
    parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
    predicates = parsed.get("candidate_predicates") if isinstance(parsed.get("candidate_predicates"), list) else []
    return any(
        isinstance(item, dict) and str(item.get("signature", "")).strip() == "domain_omission/5"
        for item in predicates
    )


def _facts_include_domain_omission(facts: list[str]) -> bool:
    for fact in facts:
        match = FACT_RE.match(str(fact).strip())
        if match and match.group(1) == "domain_omission":
            return True
    return False


def _self_check_omission_requires_domain_omission(data: dict[str, Any]) -> bool:
    active_lens = data.get("active_profile_registry_lens")
    if not isinstance(active_lens, dict) or not active_lens:
        return True
    try:
        return int(active_lens.get("accountability_requirement_count") or 0) > 0
    except (TypeError, ValueError):
        return True


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


def _domain_omission_rows(facts: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for fact in facts:
        match = FACT_RE.match(str(fact).strip())
        if not match or match.group(1) != "domain_omission":
            continue
        args = _split_args(match.group(2))
        if len(args) != 5:
            rows.append({"fact": fact, "carrier_signature": ""})
            continue
        rows.append(
            {
                "fact": fact,
                "carrier_signature": _normalize_arg(args[1]),
                "omission_kind": _normalize_arg(args[2]),
                "reason_code": _normalize_arg(args[3]),
            }
        )
    return rows


def _ordinary_omission_placeholder(fact: str) -> str:
    match = FACT_RE.match(str(fact).strip())
    if not match:
        return ""
    predicate = match.group(1)
    args = [_normalize_arg(arg) for arg in _split_args(match.group(2))]
    if predicate == "fda_correspondence_party" and len(args) == 5:
        party_id, party_role, party_name = args[1], args[2], args[3]
        if party_role in {"signatory", "contact", "responsible_official"} and (
            party_id in {"not_stated", "unknown", "none_found", "not_applicable", "missing"}
            or party_name in {"not_stated", "unknown", "none_found", "not_applicable", "missing"}
        ):
            return "fda_correspondence_party/5"
    return ""


def _sec_signature_omission_contradictions(facts: list[str]) -> list[str]:
    filings_with_real_signatory: set[str] = set()
    omitted_signature_scopes: set[tuple[str, str]] = set()
    parsed_facts: list[tuple[str, list[str], str]] = []
    for fact in facts:
        match = FACT_RE.match(str(fact).strip())
        if not match:
            continue
        predicate = match.group(1)
        args = [_normalize_arg(arg) for arg in _split_args(match.group(2))]
        parsed_facts.append((predicate, args, fact))
        if predicate == "sec_signatory" and len(args) == 5 and args[0] and not _sec_signatory_is_not_stated(args):
            filings_with_real_signatory.add(args[0])
        elif (
            predicate == "domain_omission"
            and len(args) == 5
            and args[1] == "sec_signatory/5"
            and args[2] == "role_missing"
            and args[3] == "signature_block_not_stated"
            and args[0]
            and args[4]
        ):
            omitted_signature_scopes.add((args[0], args[4]))

    out: list[str] = []
    for predicate, args, fact in parsed_facts:
        if (
            predicate == "domain_omission"
            and len(args) == 5
            and args[0] in filings_with_real_signatory
            and args[1] == "sec_signatory/5"
            and args[2] == "role_missing"
            and args[3] == "signature_block_not_stated"
        ):
            out.append(fact)
        elif (
            predicate == "sec_signatory"
            and len(args) == 5
            and _sec_signatory_is_not_stated(args)
            and (args[0], args[4]) in omitted_signature_scopes
        ):
            out.append(fact)
    return out


def _sec_signatory_is_not_stated(args: list[str]) -> bool:
    return len(args) == 5 and all(_normalize_arg(value) == "not_stated" for value in args[1:4])


def _osha_accident_omission_contradictions(facts: list[str]) -> list[str]:
    omitted_subjects_by_scope: set[tuple[str, str]] = set()
    parsed_facts: list[tuple[str, list[str], str]] = []
    for fact in facts:
        match = FACT_RE.match(str(fact).strip())
        if not match:
            continue
        predicate = match.group(1)
        args = [_normalize_arg(arg) for arg in _split_args(match.group(2))]
        parsed_facts.append((predicate, args, fact))
        if (
            predicate == "domain_omission"
            and len(args) == 5
            and args[1] == "osha_accident/7"
            and args[2] == "none_found"
            and args[3] == "accident_summary_not_stated"
            and args[0]
        ):
            omitted_subjects_by_scope.add((args[0], args[4]))

    contradicted_accidents_by_scope: set[tuple[str, str]] = set()
    for predicate, args, _fact in parsed_facts:
        if predicate == "osha_accident" and len(args) == 7 and (
            (args[0], args[6]) in omitted_subjects_by_scope or (args[1], args[6]) in omitted_subjects_by_scope
        ):
            contradicted_accidents_by_scope.add((args[0], args[6]))

    out: list[str] = []
    for predicate, args, fact in parsed_facts:
        if predicate == "osha_accident" and len(args) == 7 and (
            (args[0], args[6]) in contradicted_accidents_by_scope or (args[1], args[6]) in omitted_subjects_by_scope
        ):
            out.append(fact)
        elif predicate == "osha_injured_employee" and len(args) == 7 and (
            (args[0], args[6]) in contradicted_accidents_by_scope or (args[0], args[6]) in omitted_subjects_by_scope
        ):
            out.append(fact)
    return out


def _ntsb_report_omission_contradictions(facts: list[str]) -> list[str]:
    omitted_sources: set[str] = set()
    real_report_sources: set[str] = set()
    parsed_facts: list[tuple[str, list[str], str]] = []
    for fact in facts:
        match = FACT_RE.match(str(fact).strip())
        if not match:
            continue
        predicate = match.group(1)
        args = [_normalize_arg(arg) for arg in _split_args(match.group(2))]
        parsed_facts.append((predicate, args, fact))
        if predicate == "ntsb_report" and len(args) == 5 and args[4] and not _ntsb_report_identifier_is_not_stated(args):
            real_report_sources.add(args[4])
        elif (
            predicate == "domain_omission"
            and len(args) == 5
            and args[1] == "ntsb_report/5"
            and args[2] == "role_missing"
            and args[3] == "report_identifier_not_stated"
            and args[4]
        ):
            omitted_sources.add(args[4])

    out: list[str] = []
    for predicate, args, fact in parsed_facts:
        if (
            predicate == "domain_omission"
            and len(args) == 5
            and args[4] in real_report_sources
            and args[1] == "ntsb_report/5"
            and args[2] == "role_missing"
            and args[3] == "report_identifier_not_stated"
        ):
            out.append(fact)
        elif (
            predicate == "ntsb_report"
            and len(args) == 5
            and _ntsb_report_identifier_is_not_stated(args)
            and args[4] in omitted_sources
        ):
            out.append(fact)
    return out


def _ntsb_report_identifier_is_not_stated(args: list[str]) -> bool:
    return len(args) == 5 and _normalize_arg(args[0]) in {
        "not_stated",
        "unknown",
        "none_found",
        "missing",
        "not_available",
    }


@lru_cache(maxsize=1)
def _registered_domain_omission_triples() -> frozenset[tuple[str, str, str]]:
    triples: set[tuple[str, str, str]] = set()
    root = ROOT / "datasets" / "domain_profiles"
    if not root.exists():
        return frozenset()
    for path in sorted(root.glob("*/ontology_registry.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        requirements = data.get("accountability_requirements")
        if not isinstance(requirements, list):
            continue
        for item in requirements:
            if not isinstance(item, dict):
                continue
            carrier_signature = _normalize_arg(str(item.get("carrier_signature") or ""))
            omission_kind = _normalize_arg(str(item.get("omission_kind") or ""))
            reason_code = _normalize_arg(str(item.get("reason_code") or ""))
            if carrier_contract(carrier_signature) is not None and omission_kind and reason_code:
                triples.add((carrier_signature, omission_kind, reason_code))
    return frozenset(triples)


def _normalize_arg(value: str) -> str:
    text = str(value or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        text = text[1:-1]
    return text.strip()


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


if __name__ == "__main__":
    raise SystemExit(main())
