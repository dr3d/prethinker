#!/usr/bin/env python3
"""Validate domain predicate schema registries.

Domain registries are customization layers over the central carrier contract
registry. This validator checks schema shape and contract alignment without
reading source prose, QA questions, or oracle answers.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.carrier_contract_registry import carrier_contract, validate_carrier_contract_registry  # noqa: E402


DEFAULT_ROOT = REPO_ROOT / "datasets" / "domain_profiles"
SIGNATURE_RE = re.compile(r"^[a-z][a-z0-9_]*/[1-9][0-9]*$")
ARG_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--registry", action="append", default=[], type=Path)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = _registry_paths(root=args.root, explicit=args.registry)
    report = build_report(paths)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.exit_zero or not report["summary"]["blocking_errors"] else 1


def build_report(paths: list[Path]) -> dict[str, Any]:
    carrier_registry_errors = validate_carrier_contract_registry()
    rows = [_validate_registry(path) for path in paths]
    blocking_errors = sum(len(row["errors"]) for row in rows) + len(carrier_registry_errors)
    warning_count = sum(len(row["warnings"]) for row in rows)
    predicate_count = sum(int(row["predicate_count"]) for row in rows)
    return {
        "schema_version": "domain_predicate_schema_validation_v1",
        "summary": {
            "registry_count": len(rows),
            "predicate_count": predicate_count,
            "blocking_errors": blocking_errors,
            "warning_count": warning_count,
            "status": "fail" if blocking_errors else "pass",
        },
        "carrier_registry_errors": carrier_registry_errors,
        "registries": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Domain Predicate Schema Validation",
        "",
        f"- Registries: `{summary['registry_count']}`",
        f"- Predicates: `{summary['predicate_count']}`",
        f"- Blocking errors: `{summary['blocking_errors']}`",
        f"- Warnings: `{summary['warning_count']}`",
        f"- Status: `{summary['status']}`",
        "",
    ]
    if report.get("carrier_registry_errors"):
        lines.extend(["## Carrier Registry Errors", ""])
        for error in report["carrier_registry_errors"]:
            lines.append(f"- `{error}`")
        lines.append("")
    lines.extend(
        [
            "| Registry | Predicates | Errors | Warnings |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for row in report.get("registries", []):
        lines.append(
            "| `{}` | {} | `{}` | `{}` |".format(
                row.get("registry", ""),
                row.get("predicate_count", 0),
                row.get("errors", []),
                row.get("warnings", []),
            )
        )
    return "\n".join(lines) + "\n"


def _registry_paths(*, root: Path, explicit: list[Path]) -> list[Path]:
    paths = [path.resolve() for path in explicit]
    root_path = root.resolve()
    if root_path.exists():
        paths.extend(sorted(root_path.glob("*/ontology_registry.json")))
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path)] = path
    return list(unique.values())


def _validate_registry(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive CLI path
        return {
            "registry": str(path),
            "fixture": "",
            "predicate_count": 0,
            "errors": [f"invalid_json:{exc}"],
            "warnings": [],
            "predicates": [],
        }

    if not isinstance(data, dict):
        return {
            "registry": str(path),
            "fixture": "",
            "predicate_count": 0,
            "errors": ["registry_root_not_object"],
            "warnings": [],
            "predicates": [],
        }

    schema = str(data.get("schema") or "").strip()
    if schema != "candidate_profile_registry_v1":
        errors.append(f"unexpected_schema:{schema or '<missing>'}")
    fixture = str(data.get("fixture") or "").strip()
    if not fixture:
        errors.append("missing_fixture")
    predicates = data.get("predicates")
    if not isinstance(predicates, list) or not predicates:
        errors.append("missing_predicates")
        predicates = []

    seen: set[str] = set()
    predicate_rows: list[dict[str, Any]] = []
    for index, item in enumerate(predicates):
        row_errors: list[str] = []
        row_warnings: list[str] = []
        if not isinstance(item, dict):
            errors.append(f"predicate_{index + 1}:not_object")
            continue
        signature = str(item.get("signature") or "").strip()
        args = [str(arg).strip() for arg in item.get("args", [])] if isinstance(item.get("args"), list) else []
        if not SIGNATURE_RE.match(signature):
            row_errors.append("invalid_signature_shape")
        if signature in seen:
            row_errors.append("duplicate_signature")
        seen.add(signature)
        contract = carrier_contract(signature)
        if contract is None:
            row_errors.append("unregistered_signature")
        else:
            contract_args = [str(arg).strip() for arg in contract.get("args", [])]
            if args != contract_args:
                row_errors.append("args_do_not_match_carrier_contract")
            contract_domains = contract.get("value_domains")
            if isinstance(contract_domains, dict):
                for arg_name in contract_domains:
                    if arg_name not in contract_args:
                        row_errors.append(f"value_domain_arg_not_in_contract:{arg_name}")
        if not args:
            row_errors.append("missing_args")
        for arg in args:
            if not ARG_RE.match(arg):
                row_errors.append(f"invalid_arg_name:{arg}")
        category = str(item.get("category") or "").strip()
        if not category:
            row_warnings.append("missing_category")
        notes = str(item.get("notes") or "").strip()
        if not notes:
            row_warnings.append("missing_notes")
        if _looks_like_fact_slot(notes):
            row_warnings.append("notes_look_like_fact_payload")
        errors.extend(f"{signature or f'predicate_{index + 1}'}:{error}" for error in row_errors)
        warnings.extend(f"{signature or f'predicate_{index + 1}'}:{warning}" for warning in row_warnings)
        predicate_rows.append(
            {
                "signature": signature,
                "args": args,
                "category": category,
                "errors": row_errors,
                "warnings": row_warnings,
            }
        )

    return {
        "registry": str(path),
        "fixture": fixture,
        "predicate_count": len(predicate_rows),
        "errors": errors,
        "warnings": warnings,
        "predicates": predicate_rows,
    }


def _looks_like_fact_slot(text: str) -> bool:
    normalized = " ".join(str(text or "").split())
    if len(normalized) > 360:
        return True
    quote_count = normalized.count('"') + normalized.count("'")
    if quote_count >= 6:
        return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
