#!/usr/bin/env python3
"""Summarize domain omission/accountability contracts and fixture coverage.

This is a static accountability report. It reads domain registries and typed
fixture oracles only. It does not read source prose, QA questions, judge output,
or model self-check text. Compile-artifact enforcement remains in
audit_domain_omission_accountability.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.summarize_domain_pack_status import build_report as build_pack_report  # noqa: E402
from scripts.validate_typed_micro_fixtures import _load_fact_lines, _parse_fact  # noqa: E402


DEFAULT_PROFILE_ROOT = REPO_ROOT / "datasets" / "domain_profiles"
DEFAULT_FIXTURE_ROOT = REPO_ROOT / "datasets" / "compile_micro_fixtures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-root", type=Path, default=DEFAULT_PROFILE_ROOT)
    parser.add_argument("--fixture-root", type=Path, default=DEFAULT_FIXTURE_ROOT)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(profile_root=args.profile_root, fixture_root=args.fixture_root)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.exit_zero or not report["summary"]["blocking_errors"] else 1


def build_report(
    *,
    profile_root: Path = DEFAULT_PROFILE_ROOT,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
) -> dict[str, Any]:
    pack_report = build_pack_report(profile_root=profile_root, fixture_root=fixture_root)
    domains: list[dict[str, Any]] = []
    for domain in pack_report.get("domains", []):
        domains.append(_domain_accountability_row(domain))

    requirement_total = sum(len(domain["requirements"]) for domain in domains)
    fixture_omission_total = sum(int(domain["fixture_omission_fact_count"]) for domain in domains)
    covered_requirement_total = sum(
        1 for domain in domains for requirement in domain["requirements"] if requirement["fixture_support_count"]
    )
    fixture_only_total = sum(len(domain["fixture_only_omission_patterns"]) for domain in domains)
    return {
        "schema_version": "domain_accountability_status_v1",
        "summary": {
            "domain_count": len(domains),
            "registry_requirement_count": requirement_total,
            "covered_registry_requirement_count": covered_requirement_total,
            "uncovered_registry_requirement_count": requirement_total - covered_requirement_total,
            "fixture_omission_fact_count": fixture_omission_total,
            "fixture_only_omission_pattern_count": fixture_only_total,
            "blocking_errors": int(pack_report["summary"]["schema_blocking_errors"]),
            "status": "fail" if int(pack_report["summary"]["schema_blocking_errors"]) else "pass",
        },
        "domains": domains,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Domain Accountability Status",
        "",
        "Generated from closed domain registries and typed fixture oracles.",
        "This report does not read source prose, QA questions, judge output, or model self-check text.",
        "",
        "Compile-time enforcement remains the job of `scripts/audit_domain_omission_accountability.py`.",
        "This page shows which omission contracts exist and which typed fixture oracles exercise them.",
        "",
        "## Summary",
        "",
        f"- Domains: `{summary['domain_count']}`",
        f"- Registry accountability requirements: `{summary['registry_requirement_count']}`",
        f"- Requirements covered by fixture omissions: `{summary['covered_registry_requirement_count']}`",
        f"- Requirements not yet covered by fixture omissions: `{summary['uncovered_registry_requirement_count']}`",
        f"- Fixture omission facts: `{summary['fixture_omission_fact_count']}`",
        f"- Fixture-only omission patterns: `{summary['fixture_only_omission_pattern_count']}`",
        f"- Status: `{summary['status']}`",
        "",
        "| Domain | Requirements | Covered | Fixture omissions | Fixture-only patterns |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for domain in report.get("domains", []):
        lines.append(
            "| `{}` | {} | {} | {} | {} |".format(
                domain["profile_id"],
                len(domain["requirements"]),
                sum(1 for item in domain["requirements"] if item["fixture_support_count"]),
                domain["fixture_omission_fact_count"],
                len(domain["fixture_only_omission_patterns"]),
            )
        )

    for domain in report.get("domains", []):
        lines.extend(["", f"## {domain['profile_id']}", ""])
        lines.extend(["### Registry Requirements", ""])
        if not domain["requirements"]:
            lines.append("_No registry accountability requirements declared._")
        else:
            lines.extend(
                [
                    "| ID | Carrier | Kind | Reason | Fixture support |",
                    "| --- | --- | --- | --- | ---: |",
                ]
            )
            for requirement in domain["requirements"]:
                lines.append(
                    "| `{}` | `{}` | `{}` | `{}` | {} |".format(
                        requirement["id"],
                        requirement["carrier_signature"],
                        requirement["omission_kind"],
                        requirement["reason_code"],
                        requirement["fixture_support_count"],
                    )
                )

        lines.extend(["", "### Fixture Omission Patterns", ""])
        patterns = domain["fixture_omission_patterns"]
        if not patterns:
            lines.append("_No expected `domain_omission/5` facts in associated fixtures._")
        else:
            lines.extend(
                [
                    "| Carrier | Kind | Reason | Count | Registry status | Fixtures |",
                    "| --- | --- | --- | ---: | --- | --- |",
                ]
            )
            for pattern in patterns:
                fixtures = ", ".join(f"`{item}`" for item in pattern["fixtures"])
                lines.append(
                    "| `{}` | `{}` | `{}` | {} | `{}` | {} |".format(
                        pattern["carrier_signature"],
                        pattern["omission_kind"],
                        pattern["reason_code"],
                        pattern["count"],
                        pattern["registry_status"],
                        fixtures,
                    )
                )

        lines.extend(["", "### Accountability Read", ""])
        uncovered = [item for item in domain["requirements"] if not item["fixture_support_count"]]
        fixture_only = domain["fixture_only_omission_patterns"]
        if not uncovered and not fixture_only:
            lines.append("All declared requirements have fixture coverage, and no fixture-only omission patterns are present.")
        else:
            if uncovered:
                lines.append("Uncovered registry requirements:")
                for item in uncovered:
                    lines.append(
                        f"- `{item['id']}`: `{item['carrier_signature']}` / `{item['omission_kind']}` / `{item['reason_code']}`"
                    )
            if fixture_only:
                lines.append("Fixture-only omission patterns:")
                for item in fixture_only:
                    lines.append(
                        f"- `{item['carrier_signature']}` / `{item['omission_kind']}` / `{item['reason_code']}` "
                        f"appears in `{item['count']}` expected omission fact(s) but is not declared as a registry requirement."
                    )
    return "\n".join(lines) + "\n"


def _domain_accountability_row(domain: dict[str, Any]) -> dict[str, Any]:
    registry_path = Path(str(domain.get("registry") or ""))
    registry = _load_json(registry_path)
    requirements = [_requirement_row(item) for item in registry.get("accountability_requirements", []) if isinstance(item, dict)]
    requirement_keys = {_requirement_key(item): item for item in requirements}
    pattern_counter: Counter[tuple[str, str, str]] = Counter()
    pattern_fixtures: dict[tuple[str, str, str], set[str]] = defaultdict(set)

    for fixture in domain.get("fixtures", []):
        expected_path = Path(str(fixture.get("path") or "")) / "expected_facts.pl"
        for omission in _omission_rows(_load_fact_lines(expected_path)):
            key = _omission_key(omission)
            pattern_counter[key] += 1
            pattern_fixtures[key].add(str(fixture.get("fixture_id") or ""))

    patterns: list[dict[str, Any]] = []
    for key, count in sorted(pattern_counter.items()):
        carrier_signature, omission_kind, reason_code = key
        requirement = requirement_keys.get(key)
        pattern = {
            "carrier_signature": carrier_signature,
            "omission_kind": omission_kind,
            "reason_code": reason_code,
            "count": count,
            "fixtures": sorted(pattern_fixtures[key]),
            "registry_status": "declared" if requirement else "fixture_only",
        }
        patterns.append(pattern)
        if requirement is not None:
            requirement["fixture_support_count"] = count
            requirement["fixtures"] = sorted(pattern_fixtures[key])

    fixture_only = [item for item in patterns if item["registry_status"] == "fixture_only"]
    return {
        "profile_id": domain.get("profile_id", ""),
        "registry": domain.get("registry", ""),
        "requirements": requirements,
        "fixture_omission_fact_count": sum(pattern_counter.values()),
        "fixture_omission_patterns": patterns,
        "fixture_only_omission_patterns": fixture_only,
    }


def _requirement_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("id") or "").strip(),
        "carrier_signature": str(item.get("carrier_signature") or "").strip(),
        "omission_kind": str(item.get("omission_kind") or "").strip(),
        "reason_code": str(item.get("reason_code") or "").strip(),
        "trigger": str(item.get("trigger") or "").strip(),
        "fixture_support_count": 0,
        "fixtures": [],
    }


def _omission_rows(facts: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact(fact)
        if parsed is None or parsed.get("predicate") != "domain_omission":
            continue
        args = [str(arg).strip() for arg in parsed.get("args", [])]
        if len(args) != 5:
            continue
        rows.append(
            {
                "carrier_signature": _strip_quotes(args[1]),
                "omission_kind": _strip_quotes(args[2]),
                "reason_code": _strip_quotes(args[3]),
            }
        )
    return rows


def _requirement_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(item.get("carrier_signature") or "").strip(),
        str(item.get("omission_kind") or "").strip(),
        str(item.get("reason_code") or "").strip(),
    )


def _omission_key(item: dict[str, str]) -> tuple[str, str, str]:
    return (
        str(item.get("carrier_signature") or "").strip(),
        str(item.get("omission_kind") or "").strip(),
        str(item.get("reason_code") or "").strip(),
    )


def _strip_quotes(value: str) -> str:
    text = str(value or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        return text[1:-1].strip()
    return text


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


if __name__ == "__main__":
    raise SystemExit(main())
