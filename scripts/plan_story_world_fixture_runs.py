#!/usr/bin/env python3
"""Build a cold-run plan for promoted story-world fixtures."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = REPO_ROOT / "datasets" / "story_worlds"
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "story_world_runs" / "cold_run_plan.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "story_world_runs" / "cold_run_plan.md"


DOMAIN_HINTS = {
    "copperfall_deadline_docket": "legal docket temporal deadlines status corrections",
    "harrowgate_witness_file": "investigation witness claims findings provenance",
    "larkspur_clockwork_fair": "story world event spine object state causality aliases",
    "meridian_permit_board": "municipal permit rules overlays exceptions unresolved interpretations",
    "northbridge_authority_packet": "cross document public infrastructure authority conflicts corrections",
    "sable_creek_budget": "municipal charter budget rules voting thresholds exceptions",
    "avalon_grant_committee": "grant committee governance rule exceptions votes deadlines",
    "glass_tide_charter": "charter rule ingestion exceptions permissions temporal status",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument(
        "--fixture",
        action="append",
        default=[],
        help="Fixture directory name to include. Repeat to include multiple. Defaults to all runnable fixtures.",
    )
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--compile-out-root", type=Path, default=REPO_ROOT / "tmp" / "story_world_cold_runs")
    parser.add_argument("--qa-out-root", type=Path, default=REPO_ROOT / "tmp" / "story_world_cold_qa")
    parser.add_argument("--qa-limit", type=int, default=10)
    parser.add_argument("--max-plan-passes", type=int, default=6)
    parser.add_argument(
        "--no-evidence-bundle",
        action="store_true",
        help="Omit the current evidence-bundle query choreography from QA commands.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dataset_root = _absolute_repo_path(args.dataset_root)
    plan = build_plan(
        dataset_root=dataset_root,
        fixture_names=[str(name) for name in args.fixture],
        model=str(args.model),
        base_url=str(args.base_url),
        compile_out_root=_absolute_repo_path(args.compile_out_root),
        qa_out_root=_absolute_repo_path(args.qa_out_root),
        qa_limit=int(args.qa_limit),
        max_plan_passes=int(args.max_plan_passes),
        include_evidence_bundle=not bool(args.no_evidence_bundle),
    )
    out_json = _absolute_repo_path(args.out_json)
    out_md = _absolute_repo_path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(plan), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(plan["summary"], sort_keys=True))
    return 0


def build_plan(
    *,
    dataset_root: Path,
    fixture_names: list[str],
    model: str,
    base_url: str,
    compile_out_root: Path,
    qa_out_root: Path,
    qa_limit: int,
    max_plan_passes: int,
    include_evidence_bundle: bool = True,
) -> dict[str, Any]:
    selected = {name for name in fixture_names if name}
    fixture_dirs = _fixture_paths_with_required_assets(dataset_root, selected)
    fixtures = [
        _fixture_run_item(
            fixture_dir=fixture_dir,
            model=model,
            base_url=base_url,
            compile_out_root=compile_out_root,
            qa_out_root=qa_out_root,
            qa_limit=qa_limit,
            max_plan_passes=max_plan_passes,
            include_evidence_bundle=include_evidence_bundle,
        )
        for fixture_dir in fixture_dirs
    ]
    missing = sorted(selected - {item["fixture"] for item in fixtures})
    return {
        "schema_version": "story_world_fixture_cold_run_plan_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads promoted fixtures from datasets/story_worlds, not tmp/incoming staging.",
            "Uses source.md when present, otherwise story.md, as the cold compile source.",
            "Uses qa.md for question planning and oracle.jsonl only for after-the-fact scoring when present.",
            "Commands preserve multi-pass semantic parallax via flat-plus-plan-passes.",
        ],
        "summary": {
            "fixture_count": len(fixtures),
            "missing_requested_fixtures": missing,
            "qa_limit": qa_limit,
            "max_plan_passes": max_plan_passes,
            "include_evidence_bundle": include_evidence_bundle,
        },
        "fixtures": fixtures,
    }


def render_markdown(plan: dict[str, Any]) -> str:
    summary = plan.get("summary") or {}
    lines = [
        "# Story-World Fixture Cold Run Plan",
        "",
        f"Generated: {plan.get('generated_at', '')}",
        "",
        "## Summary",
        "",
        f"- Fixtures: `{summary.get('fixture_count', 0)}`",
        f"- Missing requested fixtures: `{summary.get('missing_requested_fixtures', [])}`",
        f"- QA limit: `{summary.get('qa_limit', 0)}`",
        f"- Max plan passes: `{summary.get('max_plan_passes', 0)}`",
        f"- Evidence bundle QA: `{summary.get('include_evidence_bundle', False)}`",
        "",
        "## Commands",
        "",
    ]
    for item in plan.get("fixtures", []):
        if not isinstance(item, dict):
            continue
        lines.extend(
            [
                f"### {item.get('fixture', '')}",
                "",
                f"- Domain hint: `{item.get('domain_hint', '')}`",
                f"- Source: `{item.get('source', '')}`",
                f"- QA file: `{item.get('qa_file', '')}`",
                f"- Oracle: `{item.get('oracle_jsonl') or 'none'}`",
                "",
                "Compile:",
                "",
                "```powershell",
                str(item.get("compile_command", "")),
                "```",
                "",
                "QA:",
                "",
                "```powershell",
                str(item.get("qa_command_template", "")),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def _fixture_paths_with_required_assets(dataset_root: Path, selected: set[str]) -> list[Path]:
    if not dataset_root.exists():
        return []
    fixtures = []
    for fixture_dir in sorted(path for path in dataset_root.iterdir() if path.is_dir()):
        if selected and fixture_dir.name not in selected:
            continue
        if not _cold_source_path(fixture_dir).exists():
            continue
        if not (fixture_dir / "qa.md").exists():
            continue
        fixtures.append(fixture_dir)
    return fixtures


def _fixture_run_item(
    *,
    fixture_dir: Path,
    model: str,
    base_url: str,
    compile_out_root: Path,
    qa_out_root: Path,
    qa_limit: int,
    max_plan_passes: int,
    include_evidence_bundle: bool,
) -> dict[str, Any]:
    fixture = fixture_dir.name
    source = _cold_source_path(fixture_dir)
    qa_file = fixture_dir / "qa.md"
    oracle = fixture_dir / "oracle.jsonl"
    compile_out = compile_out_root / fixture
    qa_out = qa_out_root / fixture
    domain_hint = DOMAIN_HINTS.get(fixture, "story-world source fidelity temporal rule fixture")
    compile_command = (
        f"python scripts/run_domain_bootstrap_file.py --text-file {_display_path(source)} "
        f"--domain-hint \"{domain_hint}\" --compile-source --compile-flat-plus-plan-passes "
        f"--focused-pass-ops-schema --max-plan-passes {max_plan_passes} "
        f"--model {model} --base-url {base_url} --out-dir {_display_path(compile_out)}"
    )
    qa_parts = [
        "python scripts/run_domain_bootstrap_qa.py --run-json <COMPILE_RUN_JSON>",
        f"--qa-file {_display_path(qa_file)}",
    ]
    if oracle.exists():
        qa_parts.append(f"--oracle-jsonl {_display_path(oracle)}")
        qa_parts.append("--judge-reference-answers")
    if include_evidence_bundle:
        qa_parts.extend(
            [
                "--evidence-bundle-plan",
                "--execute-evidence-bundle-plan",
                "--evidence-bundle-context-filter",
            ]
        )
    qa_parts.extend(
        [
            f"--limit {qa_limit}",
            f"--model {model}",
            f"--base-url {base_url}",
            f"--out-dir {_display_path(qa_out)}",
        ]
    )
    return {
        "fixture": fixture,
        "domain_hint": domain_hint,
        "source": _display_path(source),
        "qa_file": _display_path(qa_file),
        "oracle_jsonl": _display_path(oracle) if oracle.exists() else None,
        "compile_out_dir": _display_path(compile_out),
        "qa_out_dir": _display_path(qa_out),
        "compile_command": compile_command,
        "qa_command_template": " ".join(qa_parts),
    }


def _cold_source_path(fixture_dir: Path) -> Path:
    source = fixture_dir / "source.md"
    return source if source.exists() else fixture_dir / "story.md"


def _absolute_repo_path(value: Path) -> Path:
    return value if value.is_absolute() else REPO_ROOT / value


def _display_path(value: Path | str) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
