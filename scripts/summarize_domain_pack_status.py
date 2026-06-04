#!/usr/bin/env python3
"""Summarize closed domain predicate packs and nearby micro-fixtures.

This is an inventory/control-panel report, not a compile or QA score. It reads
domain registries, fixture manifests, and expected/forbidden typed fact files.
It deliberately does not read source prose or QA question text.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_domain_predicate_schema import build_report as build_schema_report  # noqa: E402
from scripts.validate_typed_micro_fixtures import _load_fact_lines, _parse_fact  # noqa: E402
from scripts.report_freshness import apply_markdown_freshness_check  # noqa: E402


DEFAULT_PROFILE_ROOT = REPO_ROOT / "datasets" / "domain_profiles"
DEFAULT_FIXTURE_ROOT = REPO_ROOT / "datasets" / "compile_micro_fixtures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-root", type=Path, default=DEFAULT_PROFILE_ROOT)
    parser.add_argument("--fixture-root", type=Path, default=DEFAULT_FIXTURE_ROOT)
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
    report = build_report(profile_root=args.profile_root, fixture_root=args.fixture_root)
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
    if args.exit_zero:
        return 0
    return 0 if report["summary"]["status"] == "pass" else 1


def build_report(
    *,
    profile_root: Path = DEFAULT_PROFILE_ROOT,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
) -> dict[str, Any]:
    registry_paths = sorted(profile_root.glob("*/ontology_registry.json"))
    schema_report = build_schema_report(registry_paths)
    domains = [_domain_from_schema_row(row) for row in schema_report.get("registries", [])]
    fixtures = [_fixture_row(path) for path in sorted(fixture_root.rglob("manifest.json"))]
    _assign_fixtures(domains, fixtures)

    assigned_ids = {
        fixture["fixture_id"]
        for domain in domains
        for fixture in domain.get("fixtures", [])
    }
    unassigned = [fixture for fixture in fixtures if fixture["fixture_id"] not in assigned_ids]
    expected_total = sum(int(domain["expected_fact_count"]) for domain in domains)
    forbidden_total = sum(int(domain["forbidden_fact_count"]) for domain in domains)
    predicate_total = sum(int(domain["predicate_count"]) for domain in domains)
    lens_total = sum(int(domain["lens_count"]) for domain in domains)

    return {
        "schema_version": "domain_pack_status_v1",
        "profile_root": str(profile_root),
        "fixture_root": str(fixture_root),
        "summary": {
            "domain_count": len(domains),
            "predicate_count": predicate_total,
            "domain_specific_predicate_count": sum(
                int(domain["domain_specific_predicate_count"]) for domain in domains
            ),
            "lens_count": lens_total,
            "associated_fixture_count": sum(len(domain.get("fixtures", [])) for domain in domains),
            "unassigned_fixture_count": len(unassigned),
            "expected_fact_count": expected_total,
            "forbidden_fact_count": forbidden_total,
            "schema_blocking_errors": int(schema_report["summary"]["blocking_errors"]),
            "schema_warning_count": int(schema_report["summary"]["warning_count"]),
            "schema_status": str(schema_report["summary"]["status"]),
            "blocking_reasons": [],
            "status": "fail" if int(schema_report["summary"]["blocking_errors"]) else "pass",
        },
        "domains": domains,
        "unassigned_fixtures": unassigned,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Domain Pack Status",
        "",
        "Generated from closed domain registries and typed micro-fixture oracles.",
        "This report does not read source prose, QA questions, or judge outputs.",
        "",
        "## Summary",
        "",
        f"- Domains: `{summary['domain_count']}`",
        f"- Predicates: `{summary['predicate_count']}` "
        f"(`{summary['domain_specific_predicate_count']}` domain-specific plus shared carriers)",
        f"- Lenses: `{summary['lens_count']}`",
        f"- Associated fixtures: `{summary['associated_fixture_count']}`",
        f"- Unassigned fixtures: `{summary['unassigned_fixture_count']}`",
        f"- Expected facts in associated fixtures: `{summary['expected_fact_count']}`",
        f"- Forbidden facts in associated fixtures: `{summary['forbidden_fact_count']}`",
        f"- Schema status: `{summary['schema_status']}` "
        f"({summary['schema_blocking_errors']} errors, {summary['schema_warning_count']} warnings)",
        f"- Status: `{summary['status']}`",
        "",
        "| Domain | Predicates | Domain-specific | Lenses | Fixtures | Expected | Forbidden |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for domain in report.get("domains", []):
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} | {} |".format(
                domain["profile_id"],
                domain["predicate_count"],
                domain["domain_specific_predicate_count"],
                domain["lens_count"],
                len(domain.get("fixtures", [])),
                domain["expected_fact_count"],
                domain["forbidden_fact_count"],
            )
        )

    for domain in report.get("domains", []):
        lines.extend(["", f"## {domain['profile_id']}", ""])
        lines.extend(
            [
                f"- Registry: `{_display_path(domain['registry'])}`",
                f"- Predicates: `{domain['predicate_count']}`",
                f"- Domain-specific predicates: `{domain['domain_specific_predicate_count']}`",
                f"- Lenses: `{domain['lens_count']}`",
                f"- Accountability requirements: `{domain['accountability_requirement_count']}`",
                "",
                "### Lenses",
                "",
                "| Lens | Allowed signatures |",
                "| --- | --- |",
            ]
        )
        for lens in domain.get("lenses", []):
            signatures = ", ".join(f"`{item}`" for item in lens.get("allowed_signatures", []))
            lines.append(f"| `{lens['id']}` | {signatures} |")

        lines.extend(["", "### Fixture Oracles", ""])
        fixtures = domain.get("fixtures", [])
        if not fixtures:
            lines.append("_No associated typed micro-fixtures found._")
        else:
            lines.extend(
                [
                    "| Fixture | Association | Expected | Forbidden | Expected signatures |",
                    "| --- | --- | ---: | ---: | --- |",
                ]
            )
            for fixture in fixtures:
                expected_signatures = ", ".join(
                    f"`{signature}`:{count}"
                    for signature, count in fixture.get("expected_signature_counts", {}).items()
                )
                lines.append(
                    "| `{}` | `{}` | {} | {} | {} |".format(
                        fixture["fixture_id"],
                        fixture["association"],
                        fixture["expected_fact_count"],
                        fixture["forbidden_fact_count"],
                        expected_signatures,
                    )
                )

    unassigned = report.get("unassigned_fixtures", [])
    lines.extend(["", "## Unassigned Typed Micro-Fixtures", ""])
    if not unassigned:
        lines.append("_None._")
    else:
        lines.extend(
            [
                "These fixtures are retained, but they are not currently associated with a closed domain registry.",
                "",
                "| Fixture | Expected | Forbidden |",
                "| --- | ---: | ---: |",
            ]
        )
        for fixture in unassigned:
            lines.append(
                "| `{}` | {} | {} |".format(
                    fixture["fixture_id"],
                    fixture["expected_fact_count"],
                    fixture["forbidden_fact_count"],
                )
            )
    return "\n".join(lines) + "\n"


def _domain_from_schema_row(row: dict[str, Any]) -> dict[str, Any]:
    profile_id = str(row.get("fixture") or "").strip()
    predicates = list(row.get("predicates", []))
    lenses = list(row.get("lenses", []))
    predicate_signatures = [str(item.get("signature") or "").strip() for item in predicates]
    return {
        "profile_id": profile_id,
        "registry": str(row.get("registry") or ""),
        "prefix": _profile_prefix(profile_id),
        "predicate_count": int(row.get("predicate_count") or 0),
        "domain_specific_predicate_count": sum(
            1 for signature in predicate_signatures if signature != "domain_omission/5"
        ),
        "lens_count": int(row.get("lens_count") or 0),
        "accountability_requirement_count": int(row.get("accountability_requirement_count") or 0),
        "predicates": predicates,
        "lenses": lenses,
        "fixtures": [],
        "expected_fact_count": 0,
        "forbidden_fact_count": 0,
        "expected_signature_counts": {},
        "forbidden_signature_counts": {},
    }


def _fixture_row(manifest_path: Path) -> dict[str, Any]:
    fixture_dir = manifest_path.parent
    manifest = _load_json(manifest_path)
    fixture_id = str(manifest.get("fixture_id") or fixture_dir.name).strip()
    expected_path = fixture_dir / str(manifest.get("expected_facts") or "expected_facts.pl")
    forbidden_path = fixture_dir / str(manifest.get("forbidden_facts") or "forbidden_facts.pl")
    expected_facts = _load_fact_lines(expected_path)
    forbidden_facts = _load_fact_lines(forbidden_path)
    expected_counts = _signature_counts(expected_facts)
    forbidden_counts = _signature_counts(forbidden_facts)
    return {
        "fixture_id": fixture_id,
        "path": str(fixture_dir),
        "manifest": str(manifest_path),
        "manifest_domain_profile": str(manifest.get("domain_profile") or "").strip(),
        "association": "",
        "expected_fact_count": len(expected_facts),
        "forbidden_fact_count": len(forbidden_facts),
        "expected_signature_counts": dict(sorted(expected_counts.items())),
        "forbidden_signature_counts": dict(sorted(forbidden_counts.items())),
    }


def _assign_fixtures(domains: list[dict[str, Any]], fixtures: list[dict[str, Any]]) -> None:
    by_registry = {_normalize_path(domain["registry"]): domain for domain in domains}
    for fixture in fixtures:
        domain = None
        manifest_profile = fixture.get("manifest_domain_profile", "")
        if manifest_profile:
            normalized_profile = _normalize_path((REPO_ROOT / manifest_profile).resolve())
            domain = by_registry.get(normalized_profile)
            if domain is not None:
                fixture["association"] = "manifest_domain_profile"
        if domain is None:
            candidates = [
                item for item in domains if fixture["fixture_id"].startswith(str(item.get("prefix") or ""))
            ]
            if len(candidates) == 1:
                domain = candidates[0]
                fixture["association"] = "fixture_id_prefix"
        if domain is None:
            continue
        domain["fixtures"].append(fixture)

    for domain in domains:
        expected_counter: Counter[str] = Counter()
        forbidden_counter: Counter[str] = Counter()
        expected_total = 0
        forbidden_total = 0
        domain["fixtures"] = sorted(domain["fixtures"], key=lambda item: item["fixture_id"])
        for fixture in domain["fixtures"]:
            expected_total += int(fixture["expected_fact_count"])
            forbidden_total += int(fixture["forbidden_fact_count"])
            expected_counter.update(fixture.get("expected_signature_counts", {}))
            forbidden_counter.update(fixture.get("forbidden_signature_counts", {}))
        domain["expected_fact_count"] = expected_total
        domain["forbidden_fact_count"] = forbidden_total
        domain["expected_signature_counts"] = dict(sorted(expected_counter.items()))
        domain["forbidden_signature_counts"] = dict(sorted(forbidden_counter.items()))


def _signature_counts(facts: list[str]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for fact in facts:
        parsed = _parse_fact(fact)
        if parsed is None:
            counter["<invalid>"] += 1
            continue
        counter[f"{parsed['predicate']}/{len(parsed['args'])}"] += 1
    return counter


def _profile_prefix(profile_id: str) -> str:
    return re.sub(r"_v[0-9]+$", "", str(profile_id or "").strip())


def _normalize_path(value: str | Path) -> str:
    return str(Path(value).resolve()).lower()


def _display_path(value: str | Path) -> str:
    path = Path(value)
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


if __name__ == "__main__":
    raise SystemExit(main())
