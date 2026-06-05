#!/usr/bin/env python3
"""Summarize retained real-world fixtures by metadata family.

This is a domain-selection aid, not a compile or QA score. It reads fixture
metadata and closed profile selection paths. It deliberately does not read
source prose, QA question text, oracle answers, or judge outputs.
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

from scripts.report_freshness import apply_markdown_freshness_check  # noqa: E402


DEFAULT_TRANSFER_ROOT = REPO_ROOT / "datasets" / "real_world_transfer"
DEFAULT_PROFILE_ROOT = REPO_ROOT / "datasets" / "domain_profiles"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transfer-root", type=Path, default=DEFAULT_TRANSFER_ROOT)
    parser.add_argument("--profile-root", type=Path, default=DEFAULT_PROFILE_ROOT)
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
    report = build_report(transfer_root=args.transfer_root, profile_root=args.profile_root)
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
    return 0 if args.exit_zero or report["summary"]["status"] == "pass" else 1


def build_report(
    *,
    transfer_root: Path = DEFAULT_TRANSFER_ROOT,
    profile_root: Path = DEFAULT_PROFILE_ROOT,
) -> dict[str, Any]:
    profile_rows = _profile_rows(profile_root)
    fixture_rows = _fixture_rows(transfer_root=transfer_root, profile_rows=profile_rows)
    family_rows = _family_rows(fixture_rows, profile_rows=profile_rows)
    parse_error_count = sum(1 for row in fixture_rows if row["metadata_status"] != "ok")
    selected_fixture_count = sum(1 for row in fixture_rows if row["selected_by_profiles"])
    candidate_unprofiled = [
        row
        for row in family_rows
        if not row["selected_profile_ids"] and not row["related_profile_ids"] and row["fixture_count"] >= 2
    ]
    qa_bearing_candidate_unprofiled = [
        row for row in candidate_unprofiled if int(row["question_count"]) > 0
    ]
    summary = {
        "fixture_count": len(fixture_rows),
        "family_count": len(family_rows),
        "profile_count": len(profile_rows),
        "selected_fixture_count": selected_fixture_count,
        "unselected_fixture_count": len(fixture_rows) - selected_fixture_count,
        "candidate_unprofiled_family_count": len(candidate_unprofiled),
        "qa_bearing_candidate_unprofiled_family_count": len(qa_bearing_candidate_unprofiled),
        "metadata_parse_error_count": parse_error_count,
        "llm_authored_or_rewritten_count": sum(
            1 for row in fixture_rows if row["llm_authored_source"] or row["llm_rewritten_source"]
        ),
        "declared_non_english_fixture_count": sum(
            1
            for row in fixture_rows
            if row["language"] and row["language"].casefold() not in {"en", "eng", "english"}
        ),
        "unknown_language_fixture_count": sum(1 for row in fixture_rows if not row["language"]),
        "blocking_reasons": [],
        "status": "fail" if parse_error_count else "pass",
    }
    if parse_error_count:
        summary["blocking_reasons"].append("metadata_parse_errors_present")
    return {
        "schema_version": "fixture_bank_domain_inventory_v1",
        "transfer_root": str(transfer_root),
        "profile_root": str(profile_root),
        "summary": summary,
        "profiles": profile_rows,
        "families": family_rows,
        "fixtures": fixture_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Fixture Bank Domain Inventory",
        "",
        "Generated from retained real-world fixture metadata and closed profile selection paths.",
        "This report does not read source prose, QA questions, oracle answers, or judge outputs.",
        "",
        "Use this as a domain-selection map, not as evidence that a domain pack transfers.",
        "",
        "## Summary",
        "",
        f"- Fixtures with metadata: `{summary['fixture_count']}`",
        f"- Metadata families: `{summary['family_count']}`",
        f"- Closed profiles: `{summary['profile_count']}`",
        f"- Fixtures selected by at least one closed profile: `{summary['selected_fixture_count']}`",
        f"- Fixtures not selected by a closed profile: `{summary['unselected_fixture_count']}`",
        f"- Unprofiled and profile-unrelated families with at least two fixtures: `{summary['candidate_unprofiled_family_count']}`",
        f"- QA-bearing unprofiled/profile-unrelated multi-fixture families: `{summary['qa_bearing_candidate_unprofiled_family_count']}`",
        f"- Declared non-English fixtures: `{summary['declared_non_english_fixture_count']}`",
        f"- Fixtures with no declared language: `{summary['unknown_language_fixture_count']}`",
        f"- LLM-authored or rewritten fixtures: `{summary['llm_authored_or_rewritten_count']}`",
        f"- Metadata parse errors: `{summary['metadata_parse_error_count']}`",
        f"- Status: `{summary['status']}`",
        "",
        "## Family Inventory",
        "",
        "| Family | Fixtures | Questions | Languages | Exact-selected profiles | Related profiles | Status | Sample fixture IDs |",
        "| --- | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for family in report.get("families", []):
        profiles = ", ".join(f"`{item}`" for item in family["selected_profile_ids"]) or "-"
        related = ", ".join(f"`{item}`" for item in family["related_profile_ids"]) or "-"
        languages = ", ".join(f"`{item}`" for item in family["languages"]) or "-"
        samples = ", ".join(f"`{item}`" for item in family["sample_fixture_ids"])
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} | `{}` | {} |".format(
                family["family_key"],
                family["fixture_count"],
                family["question_count"],
                languages,
                profiles,
                related,
                family["status"],
                samples,
            )
        )

    candidates = [
        family
        for family in report.get("families", [])
        if not family["selected_profile_ids"] and not family["related_profile_ids"] and family["fixture_count"] >= 2
    ]
    qa_candidates = [family for family in candidates if int(family["question_count"]) > 0]
    lines.extend(["", "## QA-Bearing Unprofiled Multi-Fixture Families", ""])
    if not qa_candidates:
        lines.append("_No QA-bearing unprofiled metadata family has two or more retained fixtures._")
    else:
        lines.extend(
            [
                "These are the most relevant retained candidates for future closed-pack work.",
                "They still need a named research reason, a compact seed scope, and independent",
                "expected/forbidden oracles before they can support a claim.",
                "",
                "| Family | Fixtures | Questions | Languages | Sample paths |",
                "| --- | ---: | ---: | --- | --- |",
            ]
        )
        for family in qa_candidates:
            languages = ", ".join(f"`{item}`" for item in family["languages"]) or "-"
            paths = ", ".join(f"`{item}`" for item in family["sample_paths"])
            lines.append(
                "| `{}` | {} | {} | {} | {} |".format(
                    family["family_key"],
                    family["fixture_count"],
                    family["question_count"],
                    languages,
                    paths,
                )
            )

    lines.extend(["", "## All Unprofiled Multi-Fixture Families", ""])
    if not candidates:
        lines.append("_No unprofiled metadata family has two or more retained fixtures._")
    else:
        lines.extend(
            [
                "These are possible future closed-pack candidates. Families related to an existing profile are omitted here",
                "unless they also need a deliberately separate pack. Candidates still need a named research reason,",
                "a compact seed scope, and independent expected/forbidden oracles before they can support a claim.",
                "",
                "| Family | Fixtures | Questions | Languages | Sample paths |",
                "| --- | ---: | ---: | --- | --- |",
            ]
        )
        for family in candidates:
            languages = ", ".join(f"`{item}`" for item in family["languages"]) or "-"
            paths = ", ".join(f"`{item}`" for item in family["sample_paths"])
            lines.append(
                "| `{}` | {} | {} | {} | {} |".format(
                    family["family_key"],
                    family["fixture_count"],
                    family["question_count"],
                    languages,
                    paths,
                )
            )

    lines.extend(["", "## Closed Profile Selection Coverage", ""])
    lines.extend(
        [
            "| Profile | Selection paths in registry | Exact matched metadata fixtures |",
            "| --- | ---: | ---: |",
        ]
    )
    selected_by_profile = Counter(
        profile_id
        for fixture in report.get("fixtures", [])
        for profile_id in fixture["selected_by_profiles"]
    )
    for profile in report.get("profiles", []):
        lines.append(
            "| `{}` | {} | {} |".format(
                profile["profile_id"],
                len(profile["selection_paths"]),
                selected_by_profile.get(profile["profile_id"], 0),
            )
        )

    return "\n".join(lines) + "\n"


def _profile_rows(profile_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(profile_root.glob("*/ontology_registry.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        selection = data.get("selection") if isinstance(data.get("selection"), dict) else {}
        selection_paths = [
            _normalize_rel_path(item)
            for item in selection.get("source_families", [])
            if isinstance(item, str) and item.strip()
        ]
        rows.append(
            {
                "profile_id": str(data.get("fixture") or path.parent.name),
                "registry": str(path),
                "selection_mode": str(selection.get("mode") or ""),
                "selection_paths": selection_paths,
            }
        )
    return rows


def _fixture_rows(*, transfer_root: Path, profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metadata_path in sorted(transfer_root.rglob("metadata.json")):
        fixture_dir = metadata_path.parent
        status = "ok"
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            metadata = {}
            status = "parse_error"
        rel_path = _normalize_rel_path(_display_path(fixture_dir))
        family_raw = str(metadata.get("source_family") or "").strip()
        family_key = _family_key(family_raw or _infer_family_from_path(fixture_dir))
        fixture_id = str(metadata.get("fixture_id") or metadata.get("document_id") or fixture_dir.name)
        question_count = _int_or_zero(metadata.get("question_count") or metadata.get("answer_count"))
        selected_by_profiles = [
            profile["profile_id"]
            for profile in profile_rows
            if _path_is_selected(rel_path, profile["selection_paths"])
        ]
        rows.append(
            {
                "fixture_id": fixture_id,
                "path": str(fixture_dir),
                "display_path": rel_path,
                "metadata_status": status,
                "batch_id": str(metadata.get("batch_id") or ""),
                "source_family": family_raw,
                "family_key": family_key,
                "language": str(metadata.get("language") or "").strip().casefold(),
                "question_count": question_count,
                "public_source": bool(
                    metadata.get("public_source")
                    or metadata.get("public_domain_or_public_record")
                    or metadata.get("public_record")
                ),
                "llm_authored_source": bool(metadata.get("llm_authored_source")),
                "llm_rewritten_source": bool(metadata.get("llm_rewritten_source")),
                "has_source_md": (fixture_dir / "source.md").exists(),
                "has_fixture_notes": (fixture_dir / "fixture_notes.md").exists(),
                "selected_by_profiles": selected_by_profiles,
            }
        )
    return rows


def _family_rows(fixture_rows: list[dict[str, Any]], *, profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in fixture_rows:
        grouped[row["family_key"]].append(row)

    rows: list[dict[str, Any]] = []
    for family_key, fixtures in sorted(grouped.items()):
        profile_ids = sorted({item for fixture in fixtures for item in fixture["selected_by_profiles"]})
        related_profile_ids = _related_profiles(family_key, profile_rows=profile_rows)
        question_count = sum(int(fixture["question_count"]) for fixture in fixtures)
        languages = sorted({fixture["language"] for fixture in fixtures if fixture["language"]})
        sample_fixtures = fixtures[:6]
        if profile_ids:
            status = "selected_by_closed_profile"
        elif related_profile_ids:
            status = "profile_family_related"
        elif len(fixtures) >= 2:
            status = "candidate_unprofiled"
        else:
            status = "singleton_unprofiled"
        rows.append(
            {
                "family_key": family_key,
                "fixture_count": len(fixtures),
                "question_count": question_count,
                "languages": languages,
                "selected_profile_ids": profile_ids,
                "related_profile_ids": related_profile_ids,
                "public_source_count": sum(1 for fixture in fixtures if fixture["public_source"]),
                "llm_authored_or_rewritten_count": sum(
                    1
                    for fixture in fixtures
                    if fixture["llm_authored_source"] or fixture["llm_rewritten_source"]
                ),
                "sample_fixture_ids": [fixture["fixture_id"] for fixture in sample_fixtures],
                "sample_paths": [fixture["display_path"] for fixture in sample_fixtures],
                "status": status,
            }
        )
    rows.sort(key=lambda row: (-int(row["fixture_count"]), row["family_key"]))
    return rows


def _path_is_selected(fixture_rel_path: str, selection_paths: list[str]) -> bool:
    # Count exact fixture-path selections only. Some older registries used broad
    # batch roots as selection hints; treating those as recursive matches would
    # attribute unrelated same-batch fixtures to the wrong closed profile.
    return fixture_rel_path in set(selection_paths)


def _related_profiles(family_key: str, *, profile_rows: list[dict[str, Any]]) -> list[str]:
    related: list[str] = []
    for profile in profile_rows:
        profile_id = str(profile["profile_id"])
        aliases = _profile_aliases(profile_id)
        if any(
            family_key == alias
            or family_key.startswith(alias + "_")
            or alias.startswith(family_key + "_")
            for alias in aliases
        ):
            related.append(profile_id)
    return related


def _profile_aliases(profile_id: str) -> set[str]:
    base = re.sub(r"_v\d+$", "", profile_id.casefold())
    parts = [part for part in base.split("_") if part]
    aliases = {base}
    if parts:
        aliases.add(parts[0])
    if len(parts) >= 2:
        aliases.add("_".join(parts[:2]))
    return aliases


def _normalize_rel_path(value: str | Path) -> str:
    text = str(value).replace("\\", "/")
    if text.startswith(str(REPO_ROOT).replace("\\", "/")):
        text = text[len(str(REPO_ROOT).replace("\\", "/")) :].lstrip("/")
    return text.strip("/")


def _display_path(path: str | Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except (OSError, ValueError):
        return str(path)


def _family_key(value: str) -> str:
    text = value.strip().casefold()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"


def _infer_family_from_path(path: Path) -> str:
    name = path.name.casefold()
    for marker in ("_ugly_", "_transfer_", "_domain_", "_skeleton_"):
        if marker in name:
            return name.split(marker, 1)[0]
    return name


def _int_or_zero(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
