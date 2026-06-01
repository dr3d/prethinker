#!/usr/bin/env python3
"""Validate an incoming domain-transfer micro-fixture package.

This is a preflight check before moving a generated package into
datasets/compile_micro_fixtures or spending inference budget on it.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_kb_atom_inventory import build_report as build_atom_inventory_report  # noqa: E402
from scripts.validate_typed_micro_fixtures import _load_fact_lines, _parse_fact  # noqa: E402


REQUIRED_FILES = {
    "manifest.json",
    "source.md",
    "expected_facts.pl",
    "forbidden_facts.pl",
    "source_notes.md",
}
CORE_FDA_SIGNATURES = {
    "fda_warning_letter/5",
    "fda_correspondence_party/5",
    "fda_inspection_event/6",
    "fda_violation/5",
    "fda_violation_citation/4",
    "fda_response_requirement/6",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument(
        "--profile-registry",
        type=Path,
        default=ROOT / "datasets" / "domain_profiles" / "fda_warning_letter_v1" / "ontology_registry.json",
    )
    parser.add_argument("--expected-min", type=int, default=18)
    parser.add_argument("--expected-max", type=int, default=28)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        package_dir=args.package_dir.resolve(),
        profile_registry=args.profile_registry.resolve(),
        expected_min=max(0, int(args.expected_min)),
        expected_max=max(0, int(args.expected_max)),
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.exit_zero or report["summary"]["status"] == "pass" else 1


def build_report(
    *,
    package_dir: Path,
    profile_registry: Path,
    expected_min: int = 18,
    expected_max: int = 28,
) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    registry = json.loads(profile_registry.read_text(encoding="utf-8"))
    allowed_signatures = {
        str(item.get("signature", "")).strip()
        for item in registry.get("predicates", [])
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }

    if not package_dir.exists() or not package_dir.is_dir():
        blockers.append(_row("missing_package_dir", str(package_dir)))
        return _report(package_dir, profile_registry, blockers, warnings, {}, [], [], allowed_signatures)

    present_files = {path.name for path in package_dir.iterdir() if path.is_file()}
    for name in sorted(REQUIRED_FILES - present_files):
        blockers.append(_row("missing_required_file", name))

    manifest = _load_manifest(package_dir / "manifest.json", blockers)
    fixture_id = str(manifest.get("fixture_id") or package_dir.name).strip()
    if fixture_id != package_dir.name:
        blockers.append(_row("fixture_id_folder_mismatch", f"{fixture_id} != {package_dir.name}"))
    for key, expected in {
        "source": "source.md",
        "expected_facts": "expected_facts.pl",
        "forbidden_facts": "forbidden_facts.pl",
    }.items():
        if manifest and str(manifest.get(key) or "").strip() != expected:
            blockers.append(_row("manifest_path_mismatch", f"{key} should be {expected}"))

    source_text = _read_text(package_dir / "source.md")
    notes_text = _read_text(package_dir / "source_notes.md")
    if source_text and "Source URL:" not in source_text:
        blockers.append(_row("source_missing_source_url", "source.md"))
    if source_text and "Accessed:" not in source_text:
        blockers.append(_row("source_missing_accessed_date", "source.md"))
    if notes_text and "why" not in notes_text.casefold():
        warnings.append(_row("source_notes_selection_reason_not_obvious", "source_notes.md"))

    expected_facts = _safe_fact_lines(package_dir / "expected_facts.pl", blockers, "expected")
    forbidden_facts = _safe_fact_lines(package_dir / "forbidden_facts.pl", blockers, "forbidden")
    if expected_facts and not (expected_min <= len(expected_facts) <= expected_max):
        blockers.append(_row("expected_fact_count_out_of_range", f"{len(expected_facts)} not in {expected_min}-{expected_max}"))

    expected_signatures = _fact_signature_rows(expected_facts, allowed_signatures, blockers, "expected")
    _fact_signature_rows(forbidden_facts, allowed_signatures, blockers, "forbidden")
    missing_core = sorted(CORE_FDA_SIGNATURES - {row["signature"] for row in expected_signatures})
    for signature in missing_core:
        warnings.append(_row("missing_core_fda_signature", signature))

    atom_shape = _expected_atom_shape_report(package_dir.name, expected_facts) if expected_facts else {}
    atom_blockers = int(atom_shape.get("atom_shape", {}).get("blocker_count", 0) or 0)
    if atom_blockers:
        blockers.append(_row("expected_fact_atom_shape_blockers", str(atom_blockers)))

    return _report(
        package_dir,
        profile_registry,
        blockers,
        warnings,
        manifest,
        expected_signatures,
        forbidden_facts,
        allowed_signatures,
        atom_shape=atom_shape.get("atom_shape", {}),
    )


def _load_manifest(path: Path, blockers: list[dict[str, str]]) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        blockers.append(_row("manifest_invalid_json", str(exc)))
        return {}
    return data if isinstance(data, dict) else {}


def _safe_fact_lines(path: Path, blockers: list[dict[str, str]], label: str) -> list[str]:
    if not path.exists():
        return []
    try:
        return _load_fact_lines(path)
    except Exception as exc:  # pragma: no cover - defensive for malformed local packages.
        blockers.append(_row(f"{label}_facts_unreadable", str(exc)))
        return []


def _fact_signature_rows(
    facts: list[str],
    allowed_signatures: set[str],
    blockers: list[dict[str, str]],
    label: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact(fact)
        if parsed is None:
            blockers.append(_row(f"invalid_{label}_fact", fact))
            continue
        signature = f"{parsed['predicate']}/{len(parsed['args'])}"
        rows.append({"fact": fact, "signature": signature})
        if signature not in allowed_signatures:
            blockers.append(_row(f"{label}_signature_outside_profile_registry", signature))
    return rows


def _expected_atom_shape_report(fixture_id: str, expected_facts: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        compile_dir = Path(tmp) / fixture_id
        compile_dir.mkdir(parents=True)
        (compile_dir / "compile.json").write_text(
            json.dumps({"source_compile": {"facts": expected_facts}}, indent=2),
            encoding="utf-8",
        )
        return build_atom_inventory_report(
            compile_root=Path(tmp),
            fixtures={fixture_id},
            include_source_record=False,
            include_prose_like=False,
            max_examples=100,
        )


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _row(kind: str, detail: str) -> dict[str, str]:
    return {"kind": kind, "detail": detail}


def _report(
    package_dir: Path,
    profile_registry: Path,
    blockers: list[dict[str, str]],
    warnings: list[dict[str, str]],
    manifest: dict[str, Any],
    expected_signatures: list[dict[str, str]],
    forbidden_facts: list[str],
    allowed_signatures: set[str],
    *,
    atom_shape: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "domain_transfer_package_validation_v1",
        "package_dir": str(package_dir),
        "profile_registry": str(profile_registry),
        "summary": {
            "status": "fail" if blockers else "pass",
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
            "expected_fact_count": len(expected_signatures),
            "forbidden_fact_count": len(forbidden_facts),
            "allowed_signature_count": len(allowed_signatures),
            "expected_signature_count": len({row["signature"] for row in expected_signatures}),
        },
        "manifest": manifest,
        "blockers": blockers,
        "warnings": warnings,
        "expected_signatures": sorted({row["signature"] for row in expected_signatures}),
        "atom_shape": atom_shape or {},
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Domain Transfer Package Validation",
        "",
        f"- Package: `{report['package_dir']}`",
        f"- Profile registry: `{report['profile_registry']}`",
        f"- Status: `{summary['status']}`",
        f"- Blockers: `{summary['blocker_count']}`",
        f"- Warnings: `{summary['warning_count']}`",
        f"- Expected facts: `{summary['expected_fact_count']}`",
        f"- Forbidden facts: `{summary['forbidden_fact_count']}`",
        f"- Expected signatures: `{summary['expected_signature_count']}`",
    ]
    if report.get("blockers"):
        lines.extend(["", "## Blockers", "", "| Kind | Detail |", "| --- | --- |"])
        for row in report["blockers"]:
            lines.append(f"| `{row['kind']}` | `{_md(row['detail'])}` |")
    if report.get("warnings"):
        lines.extend(["", "## Warnings", "", "| Kind | Detail |", "| --- | --- |"])
        for row in report["warnings"]:
            lines.append(f"| `{row['kind']}` | `{_md(row['detail'])}` |")
    if report.get("expected_signatures"):
        lines.extend(["", "## Expected Signatures", ""])
        for signature in report["expected_signatures"]:
            lines.append(f"- `{signature}`")
    return "\n".join(lines) + "\n"


def _md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
