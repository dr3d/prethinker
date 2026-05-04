#!/usr/bin/env python3
"""Build a cold-run plan for staged incoming challenge fixtures."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "tmp" / "incoming_staged" / "stage_manifest.json"
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "incoming_staged" / "cold_run_plan.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "incoming_staged" / "cold_run_plan.md"


DOMAIN_HINTS = {
    "copperfall_deadline_docket": "legal docket temporal deadlines status corrections",
    "harrowgate_witness_file": "investigation witness claims findings provenance",
    "larkspur_clockwork_fair": "story world event spine object state causality aliases",
    "meridian_permit_board": "municipal permit rules overlays exceptions unresolved interpretations",
    "northbridge_authority_packet": "cross document public infrastructure authority conflicts corrections",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--compile-out-root", type=Path, default=REPO_ROOT / "tmp" / "incoming_cold_runs")
    parser.add_argument("--qa-out-root", type=Path, default=REPO_ROOT / "tmp" / "incoming_cold_qa")
    parser.add_argument("--qa-limit", type=int, default=10)
    parser.add_argument("--max-plan-passes", type=int, default=6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest if args.manifest.is_absolute() else REPO_ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    plan = build_plan(
        manifest=manifest,
        model=str(args.model),
        base_url=str(args.base_url),
        compile_out_root=args.compile_out_root if args.compile_out_root.is_absolute() else REPO_ROOT / args.compile_out_root,
        qa_out_root=args.qa_out_root if args.qa_out_root.is_absolute() else REPO_ROOT / args.qa_out_root,
        qa_limit=int(args.qa_limit),
        max_plan_passes=int(args.max_plan_passes),
    )
    out_json = args.out_json if args.out_json.is_absolute() else REPO_ROOT / args.out_json
    out_md = args.out_md if args.out_md.is_absolute() else REPO_ROOT / args.out_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(plan), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(plan["summary"], sort_keys=True))
    return 0


def build_plan(
    *,
    manifest: dict[str, Any],
    model: str,
    base_url: str,
    compile_out_root: Path,
    qa_out_root: Path,
    qa_limit: int,
    max_plan_passes: int,
) -> dict[str, Any]:
    fixtures = []
    category_counts: Counter[str] = Counter()
    for item in manifest.get("fixtures", []) if isinstance(manifest.get("fixtures"), list) else []:
        if not isinstance(item, dict) or str(item.get("status", "")) != "staged":
            continue
        fixture = str(item.get("fixture", ""))
        categories = item.get("categories", {}) if isinstance(item.get("categories"), dict) else {}
        category_counts.update({str(key): int(value or 0) for key, value in categories.items()})
        compile_out = compile_out_root / fixture
        qa_out = qa_out_root / fixture
        source = _repo_path(item.get("source", ""))
        qa_file = _repo_path(item.get("qa_file", ""))
        oracle = _repo_path(item.get("oracle_jsonl", ""))
        domain_hint = DOMAIN_HINTS.get(fixture, "incoming challenge fixture")
        compile_command = (
            f"python scripts/run_domain_bootstrap_file.py --text-file {source} "
            f"--domain-hint \"{domain_hint}\" --compile-source --compile-flat-plus-plan-passes "
            f"--focused-pass-ops-schema --max-plan-passes {max_plan_passes} "
            f"--model {model} --base-url {base_url} --out-dir {_display_path(compile_out)}"
        )
        qa_command_template = (
            "python scripts/run_domain_bootstrap_qa.py --run-json <COMPILE_RUN_JSON> "
            f"--qa-file {qa_file} --oracle-jsonl {oracle} --judge-reference-answers "
            f"--limit {qa_limit} --model {model} --base-url {base_url} --out-dir {_display_path(qa_out)}"
        )
        fixtures.append(
            {
                "fixture": fixture,
                "challenge_categories": categories,
                "domain_hint": domain_hint,
                "source": source,
                "qa_file": qa_file,
                "oracle_jsonl": oracle,
                "compile_out_dir": _display_path(compile_out),
                "qa_out_dir": _display_path(qa_out),
                "compile_command": compile_command,
                "qa_command_template": qa_command_template,
            }
        )
    return {
        "schema_version": "incoming_fixture_cold_run_plan_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Uses staged no-answer qa.md for query planning.",
            "Uses oracle.jsonl only for after-the-fact scoring.",
            "Commands preserve multi-pass semantic parallax via flat-plus-plan-passes.",
        ],
        "summary": {
            "fixture_count": len(fixtures),
            "qa_limit": qa_limit,
            "max_plan_passes": max_plan_passes,
            "category_counts": dict(category_counts),
        },
        "fixtures": fixtures,
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Incoming Fixture Cold Run Plan",
        "",
        f"Generated: {plan.get('generated_at', '')}",
        "",
        "## Summary",
        "",
        f"- Fixtures: `{(plan.get('summary') or {}).get('fixture_count', 0)}`",
        f"- QA smoke limit: `{(plan.get('summary') or {}).get('qa_limit', 0)}`",
        f"- Max plan passes: `{(plan.get('summary') or {}).get('max_plan_passes', 0)}`",
        f"- Category counts: `{(plan.get('summary') or {}).get('category_counts', {})}`",
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
                f"- Categories: `{item.get('challenge_categories', {})}`",
                "",
                "Compile:",
                "",
                "```powershell",
                str(item.get("compile_command", "")),
                "```",
                "",
                "QA smoke:",
                "",
                "```powershell",
                str(item.get("qa_command_template", "")),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def _repo_path(value: Any) -> str:
    return _display_path(REPO_ROOT / str(value)) if not Path(str(value)).is_absolute() else str(value)


def _display_path(value: Path | str) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
