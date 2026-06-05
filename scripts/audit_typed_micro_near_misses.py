#!/usr/bin/env python3
"""Classify typed micro expected-fact near misses.

This diagnostic reads typed micro summary JSON reports, compares unsupported
expected facts to same-predicate emitted variants, and reports which typed
argument slots drift. It does not read source prose, call an LLM, inspect QA
questions, or change support scores.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.report_freshness import apply_markdown_freshness_check

FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")

SOURCE_SLOT_TERMS = {"source", "scope", "coordinate", "provenance", "src"}
DATE_SLOT_TERMS = {"date", "deadline", "timing", "effective"}
ROLE_SLOT_TERMS = {"role", "kind", "type", "status"}
PARTY_SLOT_TERMS = {"party", "payor", "payee", "respondent", "authority", "contact", "signatory"}
SUBJECT_SLOT_NAMES = {"subject_id", "instrument_id", "domain_or_subject_id"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary-json",
        action="append",
        type=Path,
        required=True,
        help="Typed micro series summary JSON. May be provided more than once.",
    )
    parser.add_argument(
        "--profile-registry",
        type=Path,
        default=None,
        help="Optional closed domain profile registry used to label predicate argument slots.",
    )
    parser.add_argument(
        "--support-threshold",
        type=int,
        default=None,
        help="Override the stable-variant support threshold. Defaults to each summary's support_threshold or 2.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument(
        "--expect-md",
        type=Path,
        default=None,
        help="Fail if this markdown file differs from the freshly rendered report.",
    )
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        summary_paths=args.summary_json,
        profile_registry_path=args.profile_registry,
        support_threshold=args.support_threshold,
    )
    rendered_md = render_markdown(report)
    if args.expect_md:
        apply_markdown_freshness_check(
            report=report,
            expected_path=args.expect_md,
            rendered_md=rendered_md,
        )
        rendered_md = render_markdown(report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(rendered_md, encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    blocked = report["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not blocked else 1


def build_report(
    *,
    summary_paths: list[Path],
    profile_registry_path: Path | None = None,
    support_threshold: int | None = None,
) -> dict[str, Any]:
    slot_names_by_signature = _slot_names_by_signature(profile_registry_path)
    reports = [_load_json(path) for path in summary_paths]
    rows: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    errors: list[str] = []
    for path, summary in zip(summary_paths, reports):
        fixture_id = str(summary.get("fixture_id") or "")
        threshold = int(support_threshold or summary.get("support_threshold") or 2)
        file_rows: list[dict[str, Any]] = []
        for index, row in enumerate(summary.get("rows") or [], start=1):
            if not isinstance(row, dict) or row.get("meets_threshold"):
                continue
            classified = _classify_row(
                row=row,
                fixture_id=fixture_id,
                row_index=index,
                threshold=threshold,
                slot_names_by_signature=slot_names_by_signature,
            )
            file_rows.append(classified)
            if classified["parse_status"] != "pass":
                errors.append(
                    f"{path}:row_{index}:{classified['parse_status']}:{classified.get('expected_fact', '')}"
                )
        rows.extend(file_rows)
        files.append(
            {
                "path": str(path),
                "fixture_id": fixture_id,
                "support_threshold": threshold,
                "unsupported_row_count": len(file_rows),
                "unsupported_with_stable_variant_count": sum(
                    1 for item in file_rows if item["stable_variant_count"] > 0
                ),
                "source_coordinate_only_count": sum(
                    1 for item in file_rows if item["source_coordinate_only"]
                ),
                "same_primary_subject_stable_count": sum(
                    1 for item in file_rows if item["same_primary_subject_stable"]
                ),
            }
        )
    return {
        "schema_version": "typed_micro_near_miss_audit_v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "profile_registry": str(profile_registry_path or ""),
        "summary": _summary(rows=rows, errors=errors, file_count=len(summary_paths)),
        "files": files,
        "by_predicate": _by_predicate(rows),
        "by_slot": _by_slot(rows),
        "rows": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Typed Micro Near-Miss Audit",
        "",
        "Generated from typed micro summary JSON reports.",
        "This diagnostic reads typed facts only; it does not read source prose, QA questions, judge output, or oracle answers beyond expected fact strings already present in the typed summary.",
        "",
        "## Summary",
        "",
        f"- Status: `{summary['status']}`",
        f"- Files: `{summary['file_count']}`",
        f"- Unsupported rows: `{summary['unsupported_row_count']}`",
        f"- Rows with stable same-predicate variants: `{summary['unsupported_with_stable_variant_count']}`",
        f"- Rows with same-primary-subject stable variants: `{summary['same_primary_subject_stable_count']}`",
        f"- Source-coordinate-only rows: `{summary['source_coordinate_only_count']}`",
        f"- Rows with no stable variant: `{summary['no_stable_variant_count']}`",
        f"- Parse errors: `{summary['parse_error_count']}`",
        "",
        "## Files",
        "",
        "| Fixture | Unsupported | Stable Variant | Same Primary Subject | Source-Only | Threshold | Path |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in report["files"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_code(item["fixture_id"]),
                    str(item["unsupported_row_count"]),
                    str(item["unsupported_with_stable_variant_count"]),
                    str(item["same_primary_subject_stable_count"]),
                    str(item["source_coordinate_only_count"]),
                    str(item["support_threshold"]),
                    _md_code(item["path"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## By Predicate",
            "",
            "| Predicate | Rows | Stable Variant | Same Primary Subject | Source-Only | No Stable Variant |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in report["by_predicate"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_code(item["signature"]),
                    str(item["row_count"]),
                    str(item["stable_variant_count"]),
                    str(item["same_primary_subject_stable_count"]),
                    str(item["source_coordinate_only_count"]),
                    str(item["no_stable_variant_count"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
        "## By Drift Slot",
        "",
        "| Slot | Class | Count |",
        "| --- | --- | ---: |",
        ]
    )
    for item in report["by_slot"]:
        lines.append(
            "| "
            + " | ".join([_md_code(item["slot"]), _md_code(item["slot_class"]), str(item["count"])])
            + " |"
        )
    lines.extend(
        [
            "",
            "## By Diagnosis",
            "",
            "| Diagnosis | Rows |",
            "| --- | ---: |",
        ]
    )
    for diagnosis, count in report["summary"]["diagnosis_counts"].items():
        lines.append("| " + " | ".join([_md_code(diagnosis), str(count)]) + " |")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Fixture | Predicate | Diagnosis | Stable | Same Primary Subject | Source-Only | Drift Slots | Best Stable Variant | Expected |",
            "| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in report["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_code(row["fixture_id"]),
                    _md_code(row["signature"]),
                    _md_code(row.get("diagnosis") or ""),
                    str(row["stable_variant_count"]),
                    _bool(row["same_primary_subject_stable"]),
                    _bool(row["source_coordinate_only"]),
                    _md_code(", ".join(row["best_stable_mismatch_slots"]) or ""),
                    _md_code(row["best_stable_variant_fact"] or ""),
                    _md_code(row["expected_fact"]),
                ]
            )
            + " |"
        )
    if summary["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- `{error}`" for error in summary["errors"])
    return "\n".join(lines) + "\n"


def _classify_row(
    *,
    row: dict[str, Any],
    fixture_id: str,
    row_index: int,
    threshold: int,
    slot_names_by_signature: dict[str, list[str]],
) -> dict[str, Any]:
    expected_fact = str(row.get("expected_fact") or "")
    parsed_expected = _parse_fact(expected_fact)
    if not parsed_expected:
        return {
            "fixture_id": fixture_id,
            "row_index": row_index,
            "expected_fact": expected_fact,
            "parse_status": "expected_fact_parse_error",
            "predicate": "",
            "signature": "",
            "stable_variant_count": 0,
            "same_primary_subject_stable": False,
            "source_coordinate_only": False,
            "best_stable_variant_fact": "",
            "best_stable_mismatch_slots": [],
            "diagnosis": "parse_error",
        }
    predicate, expected_args = parsed_expected
    signature = f"{predicate}/{len(expected_args)}"
    slot_names = slot_names_by_signature.get(signature) or [
        f"arg{index}" for index in range(1, len(expected_args) + 1)
    ]
    variants = [_variant_with_parse(item) for item in row.get("same_predicate_variants") or []]
    variants = [item for item in variants if item["parse_status"] == "pass"]
    stable_variants = [item for item in variants if int(item.get("run_count") or 0) >= threshold]
    best_stable = _best_variant(
        expected_args=expected_args,
        variants=stable_variants,
        slot_names=slot_names,
    )
    best_any = _best_variant(expected_args=expected_args, variants=variants, slot_names=slot_names)
    source_coordinate_only = bool(
        best_stable
        and best_stable["mismatch_slots"]
        and all(_slot_class(slot) == "source_coordinate" for slot in best_stable["mismatch_slots"])
    )
    same_primary_subject_stable = any(
        _same_primary_subject(expected_args=expected_args, variant_args=item["args"])
        for item in stable_variants
    )
    return {
        "fixture_id": fixture_id,
        "row_index": row_index,
        "expected_fact": expected_fact,
        "parse_status": "pass",
        "predicate": predicate,
        "signature": signature,
        "support_count": int(row.get("support_count") or 0),
        "threshold": threshold,
        "same_predicate_variant_count": len(variants),
        "stable_variant_count": len(stable_variants),
        "same_primary_subject_stable": same_primary_subject_stable,
        "source_coordinate_only": source_coordinate_only,
        "best_stable_variant_fact": (best_stable or {}).get("fact", ""),
        "best_stable_variant_run_count": int((best_stable or {}).get("run_count") or 0),
        "best_stable_mismatch_count": len((best_stable or {}).get("mismatch_slots") or []),
        "best_stable_mismatch_slots": (best_stable or {}).get("mismatch_slots") or [],
        "best_stable_mismatch_slot_classes": [
            _slot_class(slot) for slot in (best_stable or {}).get("mismatch_slots") or []
        ],
        "diagnosis": _diagnosis(
            stable_variant_count=len(stable_variants),
            same_primary_subject_stable=same_primary_subject_stable,
            source_coordinate_only=source_coordinate_only,
            best_stable_mismatch_slots=(best_stable or {}).get("mismatch_slots") or [],
        ),
        "best_any_variant_fact": (best_any or {}).get("fact", ""),
        "best_any_variant_run_count": int((best_any or {}).get("run_count") or 0),
        "best_any_mismatch_count": len((best_any or {}).get("mismatch_slots") or []),
        "best_any_mismatch_slots": (best_any or {}).get("mismatch_slots") or [],
    }


def _variant_with_parse(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {"parse_status": "variant_not_object"}
    fact = str(item.get("fact") or "")
    parsed = _parse_fact(fact)
    if not parsed:
        return {"fact": fact, "parse_status": "variant_fact_parse_error", "run_count": item.get("run_count") or 0}
    predicate, args = parsed
    return {
        "fact": fact,
        "parse_status": "pass",
        "predicate": predicate,
        "args": args,
        "run_count": int(item.get("run_count") or 0),
        "runs": item.get("runs") or [],
    }


def _best_variant(
    *,
    expected_args: list[str],
    variants: list[dict[str, Any]],
    slot_names: list[str],
) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for item in variants:
        mismatches = _mismatch_slots(expected_args=expected_args, variant_args=item["args"], slot_names=slot_names)
        candidate = {**item, "mismatch_slots": mismatches}
        if best is None:
            best = candidate
            continue
        if (len(mismatches), -int(item.get("run_count") or 0), str(item.get("fact") or "")) < (
            len(best["mismatch_slots"]),
            -int(best.get("run_count") or 0),
            str(best.get("fact") or ""),
        ):
            best = candidate
    return best


def _mismatch_slots(*, expected_args: list[str], variant_args: list[str], slot_names: list[str]) -> list[str]:
    mismatches: list[str] = []
    for index, expected in enumerate(expected_args):
        actual = variant_args[index] if index < len(variant_args) else ""
        if _is_variable(expected) or _is_variable(actual):
            continue
        if expected != actual:
            mismatches.append(slot_names[index] if index < len(slot_names) else f"arg{index + 1}")
    if len(variant_args) > len(expected_args):
        for index in range(len(expected_args), len(variant_args)):
            mismatches.append(slot_names[index] if index < len(slot_names) else f"arg{index + 1}")
    return mismatches


def _same_primary_subject(*, expected_args: list[str], variant_args: list[str]) -> bool:
    if not expected_args or not variant_args:
        return False
    if _is_variable(expected_args[0]) or _is_variable(variant_args[0]):
        return False
    return expected_args[0] == variant_args[0]


def _diagnosis(
    *,
    stable_variant_count: int,
    same_primary_subject_stable: bool,
    source_coordinate_only: bool,
    best_stable_mismatch_slots: list[str],
) -> str:
    if stable_variant_count <= 0:
        return "no_stable_same_predicate_variant"
    if source_coordinate_only:
        return "source_coordinate_only"
    if same_primary_subject_stable:
        return "same_subject_value_or_slot_drift"
    if best_stable_mismatch_slots:
        return "subject_or_key_drift"
    return "stable_variant_unclassified"


def _summary(*, rows: list[dict[str, Any]], errors: list[str], file_count: int) -> dict[str, Any]:
    diagnosis_counts = Counter(str(row.get("diagnosis") or "") for row in rows)
    return {
        "status": "pass" if not errors else "fail",
        "blocking_reasons": ["parse_errors_present"] if errors else [],
        "file_count": file_count,
        "unsupported_row_count": len(rows),
        "unsupported_with_stable_variant_count": sum(1 for row in rows if row["stable_variant_count"] > 0),
        "same_primary_subject_stable_count": sum(1 for row in rows if row["same_primary_subject_stable"]),
        "source_coordinate_only_count": sum(1 for row in rows if row["source_coordinate_only"]),
        "no_stable_variant_count": sum(1 for row in rows if row["stable_variant_count"] <= 0),
        "parse_error_count": len(errors),
        "diagnosis_counts": dict(sorted(diagnosis_counts.items())),
        "errors": errors,
    }


def _by_predicate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("signature") or ""), []).append(row)
    out: list[dict[str, Any]] = []
    for signature, items in sorted(grouped.items()):
        out.append(
            {
                "signature": signature,
                "row_count": len(items),
                "stable_variant_count": sum(1 for item in items if item["stable_variant_count"] > 0),
                "same_primary_subject_stable_count": sum(1 for item in items if item["same_primary_subject_stable"]),
                "source_coordinate_only_count": sum(1 for item in items if item["source_coordinate_only"]),
                "no_stable_variant_count": sum(1 for item in items if item["stable_variant_count"] <= 0),
            }
        )
    return out


def _by_slot(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        for slot in row.get("best_stable_mismatch_slots") or []:
            counts[(slot, _slot_class(slot))] += 1
    return [
        {"slot": slot, "slot_class": slot_class, "count": count}
        for (slot, slot_class), count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _slot_names_by_signature(profile_registry_path: Path | None) -> dict[str, list[str]]:
    if not profile_registry_path:
        return {}
    registry = _load_json(profile_registry_path)
    out: dict[str, list[str]] = {}
    for row in registry.get("predicates") or []:
        if not isinstance(row, dict):
            continue
        signature = str(row.get("signature") or "").strip()
        args = row.get("args") or []
        if signature and isinstance(args, list):
            out[signature] = [str(arg) for arg in args]
    return out


def _parse_fact(fact: str) -> tuple[str, list[str]] | None:
    match = FACT_RE.match(str(fact or "").strip())
    if not match:
        return None
    return match.group(1), _split_fact_args(match.group(2))


def _split_fact_args(raw_args: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    in_single_quote = False
    in_double_quote = False
    escape = False
    depth = 0
    for char in raw_args:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            current.append(char)
            escape = True
            continue
        if char == "'" and not in_double_quote:
            current.append(char)
            in_single_quote = not in_single_quote
            continue
        if char == '"' and not in_single_quote:
            current.append(char)
            in_double_quote = not in_double_quote
            continue
        if not in_single_quote and not in_double_quote and char == "(":
            depth += 1
        elif not in_single_quote and not in_double_quote and char == ")" and depth:
            depth -= 1
        if char == "," and not in_single_quote and not in_double_quote and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current or raw_args.strip():
        args.append("".join(current).strip())
    return args


def _is_variable(value: str) -> bool:
    value = str(value or "").strip()
    return bool(value and (value[0].isupper() or value == "_"))


def _slot_class(slot: str) -> str:
    slot = str(slot or "")
    tokens = set(slot.lower().split("_"))
    if slot in SUBJECT_SLOT_NAMES:
        return "subject_id"
    if tokens & SOURCE_SLOT_TERMS:
        return "source_coordinate"
    if tokens & DATE_SLOT_TERMS:
        return "date_time"
    if tokens & ROLE_SLOT_TERMS:
        return "role_or_kind"
    if tokens & PARTY_SLOT_TERMS:
        return "party_or_person"
    if "amount" in tokens:
        return "amount"
    return "value"


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Cannot read JSON file {path}: {exc}") from exc


def _md_code(value: Any) -> str:
    text = str(value).replace("`", "\\`")
    return f"`{text}`"


def _bool(value: Any) -> str:
    return "yes" if bool(value) else "no"


if __name__ == "__main__":
    raise SystemExit(main())
