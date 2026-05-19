#!/usr/bin/env python3
"""Audit fixture-shaped vocabulary in active architecture surfaces.

The goal is not to ban every domain word. It is to distinguish structural
terms from compatibility adapters and live architecture names that still smell
like the fixture that first exposed them.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "datasets" / "story_worlds"


@dataclass(frozen=True)
class TermPolicy:
    term: str
    status: str
    risk: str
    replacement: str
    note: str


@dataclass
class Hit:
    path: str
    line: int
    context: str
    area: str


TERM_POLICIES: tuple[TermPolicy, ...] = (
    TermPolicy(
        term="explicit_table_membership",
        status="structural",
        risk="low",
        replacement="n/a",
        note="Primary fixture-free surface for explicit grouping/member tables.",
    ),
    TermPolicy(
        term="explicit_table_member_label",
        status="structural",
        risk="low",
        replacement="n/a",
        note="Primary fixture-free label surface for explicit table members.",
    ),
    TermPolicy(
        term="explicit_table_count_support",
        status="structural",
        risk="low",
        replacement="n/a",
        note="Primary fixture-free count surface over explicit table membership.",
    ),
    TermPolicy(
        term="roster_table_member",
        status="compatibility_alias",
        risk="medium",
        replacement="explicit_table_membership",
        note="Allowed only as legacy school-roster compatibility output or old-artifact input.",
    ),
    TermPolicy(
        term="roster_table_member_label",
        status="compatibility_alias",
        risk="medium",
        replacement="explicit_table_member_label",
        note="Allowed only as legacy school-roster compatibility output or old-artifact input.",
    ),
    TermPolicy(
        term="roster_table_count_support",
        status="compatibility_alias",
        risk="medium",
        replacement="explicit_table_count_support",
        note="Old selector/test vocabulary; new support should use explicit_table_count_support.",
    ),
    TermPolicy(
        term="roster_table_student_group_assignment",
        status="compatibility_alias",
        risk="high",
        replacement="explicit_table_group_assignment",
        note="School-shaped support kind. Keep only when reading old roster_table_member rows.",
    ),
    TermPolicy(
        term="source_record_student_group_assignment",
        status="quarantined_compatibility_adapter",
        risk="high",
        replacement="direct group_assignment/group_membership/explicit_table_membership compile surfaces",
        note="Candidate parser over school roster prose; should stay disabled by default.",
    ),
    TermPolicy(
        term="student_group_assignment",
        status="compatibility_predicate",
        risk="high",
        replacement="group_assignment(Person, Version, Group) or group_membership(Person, Group, Start, End)",
        note="School-shaped admitted predicate name. Keep for old compiles while preferring generic assignment names.",
    ),
    TermPolicy(
        term="student_in_homeroom",
        status="compatibility_predicate",
        risk="high",
        replacement="explicit_table_membership or group_assignment",
        note="School-shaped query predicate. Keep only for old compiles/tests.",
    ),
    TermPolicy(
        term="homeroom_member",
        status="compatibility_predicate",
        risk="high",
        replacement="explicit_table_membership or group_assignment",
        note="School-shaped query predicate. Keep only for old compiles/tests.",
    ),
    TermPolicy(
        term="adult_role",
        status="compatibility_predicate",
        risk="medium",
        replacement="person_role(Person, Role) or role_assignment(Person, Role, Scope)",
        note="Not fixture-specific by itself, but the old adult-roster adapter around it is fixture-shaped.",
    ),
    TermPolicy(
        term="source_record_adult_role",
        status="quarantined_compatibility_adapter",
        risk="high",
        replacement="direct person_role/role_assignment compile surfaces",
        note="Derived by the legacy school-roster adult parser; should stay disabled by default.",
    ),
    TermPolicy(
        term="staff_statement",
        status="compatibility_predicate",
        risk="medium",
        replacement="recorded_statement(StatementId, Speaker, Content)",
        note="Role-shaped, not fully fixture-shaped; generic statement vocabulary should be preferred.",
    ),
    TermPolicy(
        term="industrial_sensor_support",
        status="retired_native_compatibility_adapter",
        risk="high",
        replacement="direct device/instrument, measurement, timestamp, correction-rule, and status compile surfaces",
        note="Query-time compatibility adapter over one sensor-log family. It must not become the normal path for instrument records.",
    ),
    TermPolicy(
        term="_industrial_sensor_companion",
        status="retired_native_compatibility_adapter",
        risk="high",
        replacement="direct device/instrument, measurement, timestamp, correction-rule, and status compile surfaces",
        note="Implementation hook for industrial_sensor_support; keep disabled unless transfer evidence promotes a generic replacement.",
    ),
    TermPolicy(
        term="sensor_id",
        status="domain_predicate_under_transfer",
        risk="medium",
        replacement="item_identifier/device_identifier/instrument_identifier surfaces when the profile is not sensor-specific",
        note="Potentially transferable inside sensor/instrument logs, but should not be a privileged global identifier contract.",
    ),
    TermPolicy(
        term="sensor_calibration_date",
        status="domain_predicate_under_transfer",
        risk="medium",
        replacement="calibration_event/device_status_date with governed device and source anchor",
        note="Valid for sensor logs, but still needs unlike-device transfer evidence before becoming a general architecture term.",
    ),
    TermPolicy(
        term="sensor_certified_scope",
        status="domain_predicate_under_transfer",
        risk="medium",
        replacement="certification_scope(Device, Scope) or authority/status scoped to a governed device",
        note="Valid domain vocabulary when source states certification scope; watch for fixture-specific trigger conditions.",
    ),
    TermPolicy(
        term="sensor_next_calibration_due",
        status="domain_predicate_under_transfer",
        risk="medium",
        replacement="scheduled_event/device_due_date with event type and governed device",
        note="Transfer candidate for maintenance records, not proof of a global sensor-specific path.",
    ),
    TermPolicy(
        term="sensor_not_certified_for",
        status="domain_predicate_under_transfer",
        risk="medium",
        replacement="negative_certification_scope(Device, Scope, Source) or exclusion/status surface",
        note="Negative certification is structural, but the sensor-named predicate still needs transfer evidence beyond one family.",
    ),
    TermPolicy(
        term="roster_state_support",
        status="retired_native_compatibility_adapter",
        risk="high",
        replacement="direct compile surfaces plus explicit_table_* ledger facts",
        note="Broad compatibility adapter. It is acceptable only because default delivery is disabled.",
    ),
    TermPolicy(
        term="trip_leader_",
        status="quarantined_parser_marker",
        risk="high",
        replacement="direct person_role/role_assignment compile surfaces",
        note="Fixture-shaped source atom prefix inside the legacy roster adult parser.",
    ),
    TermPolicy(
        term="chaperone_",
        status="quarantined_parser_marker",
        risk="high",
        replacement="direct person_role/role_assignment compile surfaces",
        note="Fixture-shaped source atom prefix inside the legacy roster adult parser.",
    ),
    TermPolicy(
        term="medical_",
        status="quarantined_parser_marker",
        risk="medium",
        replacement="direct person_role/role_assignment compile surfaces",
        note="Domain-shaped source atom prefix inside the legacy roster adult parser.",
    ),
)


SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "prethinker_tmp_archive",
    "tmp",
}


TEXT_SUFFIXES = {".html", ".json", ".jsonl", ".md", ".py", ".txt", ".yml", ".yaml"}


def area_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel in {
        "scripts/plan_incoming_fixture_runs.py",
        "scripts/plan_story_world_fixture_runs.py",
        "scripts/summarize_selector_guard_families.py",
        "scripts/summarize_story_world_progress.py",
    }:
        return "fixture_operator"
    if rel.startswith(("src/", "scripts/")):
        return "active_code"
    if rel.startswith("tests/"):
        return "tests"
    if rel.startswith("docs/") and rel.endswith("WORKSHEET.md"):
        return "worksheet"
    if rel.startswith("docs/"):
        return "current_docs"
    if rel.startswith("experiments/"):
        return "probe"
    return "other"


def should_scan(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.name == Path(__file__).name:
        return False
    if not path.is_file():
        return False
    return path.suffix.lower() in TEXT_SUFFIXES


def scan_term(term: str) -> list[Hit]:
    hits: list[Hit] = []
    for path in ROOT.rglob("*"):
        if not should_scan(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(ROOT).as_posix()
        area = area_for(path)
        for index, line in enumerate(lines, start=1):
            if term in line:
                hits.append(Hit(path=rel, line=index, context=line.strip()[:220], area=area))
    return hits


def summarize_hits(hits: list[Hit]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for hit in hits:
        summary[hit.area] = summary.get(hit.area, 0) + 1
    return dict(sorted(summary.items()))


def active_surface_hits(hits: list[Hit]) -> list[Hit]:
    return [hit for hit in hits if hit.area in {"active_code", "current_docs"}]


def fixture_names() -> list[str]:
    if not FIXTURE_ROOT.exists():
        return []
    return sorted(path.name for path in FIXTURE_ROOT.iterdir() if path.is_dir())


def scan_fixture_name_leaks() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name in fixture_names():
        hits = scan_term(name)
        active_hits = active_surface_hits(hits)
        if not active_hits:
            continue
        rows.append(
            {
                "fixture": name,
                "risk": "high",
                "status": "fixture_name_leak",
                "counts": summarize_hits(active_hits),
                "hits": [asdict(hit) for hit in active_hits],
            }
        )
    return rows


def render_markdown(rows: list[dict[str, object]], *, fixture_name_leaks: list[dict[str, object]] | None = None) -> str:
    lines = [
        "# Fixture Vocabulary Leak Audit",
        "",
        "This audit separates live architecture vocabulary from legacy compatibility and historical strata.",
        "A hit is not automatically a bug; the `status` and `replacement` columns define the current contract.",
        "",
        "| Term | Status | Risk | Active code | Tests | Current docs | Worksheets | Replacement |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        counts = row["counts"]
        assert isinstance(counts, dict)
        lines.append(
            "| `{term}` | `{status}` | `{risk}` | {active} | {tests} | {docs} | {worksheets} | {replacement} |".format(
                term=row["term"],
                status=row["status"],
                risk=row["risk"],
                active=counts.get("active_code", 0),
                tests=counts.get("tests", 0),
                docs=counts.get("current_docs", 0),
                worksheets=counts.get("worksheet", 0),
                replacement=str(row["replacement"]).replace("|", "\\|"),
            )
        )
    lines.extend(["", "## High-Risk Active Hits", ""])
    for row in rows:
        if row["risk"] != "high":
            continue
        active_hits = [hit for hit in row["hits"] if hit["area"] == "active_code"]
        if not active_hits:
            continue
        lines.append(f"### `{row['term']}`")
        lines.append("")
        lines.append(str(row["note"]))
        lines.append("")
        for hit in active_hits[:12]:
            lines.append(f"- `{hit['path']}:{hit['line']}` - {hit['context']}")
        if len(active_hits) > 12:
            lines.append(f"- ... {len(active_hits) - 12} more active-code hits")
        lines.append("")
    fixture_name_leaks = fixture_name_leaks or []
    lines.extend(["## Fixture Name Leaks", ""])
    if not fixture_name_leaks:
        lines.append("No dataset fixture directory names were found in active code or current docs.")
        lines.append("")
    else:
        lines.extend(
            [
                "| Fixture name | Active code | Current docs |",
                "| --- | ---: | ---: |",
            ]
        )
        for row in fixture_name_leaks:
            counts = row["counts"]
            assert isinstance(counts, dict)
            lines.append(
                "| `{fixture}` | {active} | {docs} |".format(
                    fixture=row["fixture"],
                    active=counts.get("active_code", 0),
                    docs=counts.get("current_docs", 0),
                )
            )
        lines.append("")
        for row in fixture_name_leaks[:20]:
            lines.append(f"### `{row['fixture']}`")
            lines.append("")
            for hit in row["hits"][:8]:
                lines.append(f"- `{hit['path']}:{hit['line']}` - {hit['context']}")
            if len(row["hits"]) > 8:
                lines.append(f"- ... {len(row['hits']) - 8} more active-surface hits")
            lines.append("")
    lines.extend(
        [
            "## Operating Rule",
            "",
            "- `structural`: allowed as architecture.",
            "- `compatibility_alias` / `compatibility_predicate`: allowed for old artifacts and old compile outputs; new surfaces should prefer the replacement.",
            "- `quarantined_compatibility_adapter` / `quarantined_parser_marker`: allowed only behind disabled retired-compatibility paths or in historical documentation.",
            "- Any new high-risk active-code hit needs transfer evidence or a generic replacement before it can be promoted.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    for policy in TERM_POLICIES:
        hits = scan_term(policy.term)
        rows.append(
            {
                **asdict(policy),
                "counts": summarize_hits(hits),
                "hits": [asdict(hit) for hit in hits],
            }
        )

    fixture_name_leaks = scan_fixture_name_leaks()
    payload = {
        "audit": "fixture_vocabulary_leaks",
        "term_count": len(rows),
        "rows": rows,
        "fixture_name_leak_count": len(fixture_name_leaks),
        "fixture_name_leaks": fixture_name_leaks,
    }
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(rows, fixture_name_leaks=fixture_name_leaks), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
