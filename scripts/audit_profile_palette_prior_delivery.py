#!/usr/bin/env python3
"""Audit whether a profile palette prior was offered and delivered.

This is a vocabulary-only audit. It compares a candidate profile registry to
one or more compile artifacts and reports schema overlap. It does not inspect
answers, expected rows, or source prose.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SIGNATURE_RE = re.compile(r"^([a-z][a-z0-9_]*)/([1-9][0-9]*)$")
FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")


def audit_prior_delivery(registry_json: Path, compile_paths: list[Path]) -> dict[str, Any]:
    registry = _load_json(registry_json)
    prior_signatures = _registry_signatures(registry)
    compile_files = _expand_compile_paths(compile_paths)
    rows = [_audit_compile(path, prior_signatures) for path in compile_files]
    return {
        "schema": "profile_palette_prior_delivery_audit_v1",
        "registry_json": str(registry_json),
        "registry_fixture": str(registry.get("fixture", "")),
        "prior_signature_count": len(prior_signatures),
        "prior_signatures": sorted(prior_signatures),
        "compile_count": len(rows),
        "summary": _summarize(rows, prior_signatures),
        "compiles": rows,
    }


def _load_json(path: Path) -> dict[str, Any]:
    resolved = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    payload = json.loads(resolved.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _registry_signatures(registry: dict[str, Any]) -> set[str]:
    rows = registry.get("predicates", [])
    if not isinstance(rows, list):
        return set()
    out = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        signature = str(row.get("signature", "")).strip().casefold()
        if SIGNATURE_RE.fullmatch(signature):
            out.add(signature)
    return out


def _expand_compile_paths(inputs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for item in inputs:
        path = item if item.is_absolute() else (REPO_ROOT / item).resolve()
        if path.is_file():
            out.append(path)
        elif path.is_dir():
            direct = sorted(path.glob("domain_bootstrap_file_*.json"))
            if direct:
                out.append(direct[-1])
            else:
                out.extend(sorted(path.glob("*/domain_bootstrap_file_*.json")))
    return sorted(dict.fromkeys(out))


def _audit_compile(path: Path, prior_signatures: set[str]) -> dict[str, Any]:
    payload = _load_json(path)
    parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
    offered = _candidate_signatures(parsed)
    delivered = _delivered_signatures(payload)
    prior_offered = prior_signatures & offered
    prior_delivered = prior_signatures & delivered
    offered_not_delivered = offered - delivered
    delivered_not_offered = delivered - offered
    return {
        "compile_json": str(path),
        "fixture": path.parent.name,
        "offered_signature_count": len(offered),
        "delivered_signature_count": len(delivered),
        "prior_offered_count": len(prior_offered),
        "prior_delivered_count": len(prior_delivered),
        "prior_missing_signatures": sorted(prior_signatures - offered),
        "prior_zero_yield_signatures": sorted(prior_offered - delivered),
        "prior_delivered_signatures": sorted(prior_delivered),
        "offered_non_prior_signatures": sorted(offered - prior_signatures),
        "delivered_non_prior_signatures": sorted(delivered - prior_signatures),
        "offered_not_delivered_signatures": sorted(offered_not_delivered),
        "delivered_not_offered_signatures": sorted(delivered_not_offered),
    }


def _candidate_signatures(parsed: dict[str, Any]) -> set[str]:
    out = set()
    rows = parsed.get("candidate_predicates", [])
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        signature = str(row.get("signature", "")).strip().casefold()
        if SIGNATURE_RE.fullmatch(signature):
            out.add(signature)
            continue
        name = str(row.get("name") or row.get("predicate") or "").strip().casefold()
        args = row.get("args", [])
        if name and re.fullmatch(r"[a-z][a-z0-9_]*", name) and isinstance(args, list) and args:
            out.add(f"{name}/{len(args)}")
    return out


def _delivered_signatures(payload: dict[str, Any]) -> set[str]:
    source_compile = payload.get("source_compile") if isinstance(payload.get("source_compile"), dict) else {}
    facts = source_compile.get("facts")
    if not isinstance(facts, list):
        parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
        facts = parsed.get("facts", [])
    out = set()
    for fact in facts if isinstance(facts, list) else []:
        match = FACT_RE.match(str(fact))
        if not match:
            continue
        predicate = match.group(1).strip().casefold()
        if predicate.startswith("source_record"):
            continue
        args = _split_args(match.group(2))
        out.add(f"{predicate}/{len(args)}")
    return out


def _split_args(text: str) -> list[str]:
    args: list[str] = []
    current = []
    depth = 0
    for char in text:
        if char == "," and depth == 0:
            value = "".join(current).strip()
            if value:
                args.append(value)
            current = []
            continue
        if char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        current.append(char)
    value = "".join(current).strip()
    if value:
        args.append(value)
    return args


def _summarize(rows: list[dict[str, Any]], prior_signatures: set[str]) -> dict[str, Any]:
    if not rows:
        return {
            "all_prior_offered_compile_count": 0,
            "all_prior_delivered_compile_count": 0,
            "ever_missing_prior_signatures": sorted(prior_signatures),
            "ever_zero_yield_prior_signatures": [],
        }
    ever_missing = set()
    ever_zero_yield = set()
    for row in rows:
        ever_missing.update(row["prior_missing_signatures"])
        ever_zero_yield.update(row["prior_zero_yield_signatures"])
    return {
        "all_prior_offered_compile_count": sum(1 for row in rows if not row["prior_missing_signatures"]),
        "all_prior_delivered_compile_count": sum(
            1 for row in rows if not row["prior_missing_signatures"] and not row["prior_zero_yield_signatures"]
        ),
        "ever_missing_prior_signatures": sorted(ever_missing),
        "ever_zero_yield_prior_signatures": sorted(ever_zero_yield),
        "offered_non_prior_signature_union_count": len(
            {sig for row in rows for sig in row["offered_non_prior_signatures"]}
        ),
        "delivered_non_prior_signature_union_count": len(
            {sig for row in rows for sig in row["delivered_non_prior_signatures"]}
        ),
    }


def render_markdown(audit: dict[str, Any]) -> str:
    summary = audit.get("summary") if isinstance(audit.get("summary"), dict) else {}
    lines = [
        "# Profile Palette Prior Delivery Audit",
        "",
        f"- Registry: `{audit.get('registry_json', '')}`",
        f"- Registry fixture: `{audit.get('registry_fixture', '')}`",
        f"- Prior signatures: `{audit.get('prior_signature_count', 0)}`",
        f"- Compiles: `{audit.get('compile_count', 0)}`",
        f"- Compiles with all prior signatures offered: `{summary.get('all_prior_offered_compile_count', 0)}`",
        f"- Compiles with all prior signatures delivered: `{summary.get('all_prior_delivered_compile_count', 0)}`",
        f"- Ever-missing prior signatures: `{summary.get('ever_missing_prior_signatures', [])}`",
        f"- Ever zero-yield prior signatures: `{summary.get('ever_zero_yield_prior_signatures', [])}`",
        "",
        "This audit is vocabulary-only. It does not make prior signatures facts.",
        "",
        "| Compile | Offered | Delivered | Prior offered | Prior delivered | Missing prior | Zero-yield prior | Non-prior offered |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in audit.get("compiles", []) if isinstance(audit.get("compiles"), list) else []:
        lines.append(
            "| `{}` | {} | {} | {} | {} | `{}` | `{}` | `{}` |".format(
                Path(str(row.get("compile_json", ""))).parent.name,
                row.get("offered_signature_count", 0),
                row.get("delivered_signature_count", 0),
                row.get("prior_offered_count", 0),
                row.get("prior_delivered_count", 0),
                row.get("prior_missing_signatures", []),
                row.get("prior_zero_yield_signatures", []),
                row.get("offered_non_prior_signatures", []),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry-json", type=Path, required=True)
    parser.add_argument("--compile-json", action="append", type=Path, default=[])
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()

    audit = audit_prior_delivery(args.registry_json, args.compile_json)
    out_json = args.out_json if args.out_json.is_absolute() else (REPO_ROOT / args.out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        out_md = args.out_md if args.out_md.is_absolute() else (REPO_ROOT / args.out_md).resolve()
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(audit), encoding="utf-8")
    print(json.dumps({"compile_count": audit["compile_count"], "summary": audit["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
