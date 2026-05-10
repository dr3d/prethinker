#!/usr/bin/env python3
"""Create Axis-2 assemblies around semantic A/B probe fixtures."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEMANTIC_PLAN = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "semantic_probes" / "semantic_ab_probe_plan.json"
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "semantic_probes" / "axis2_hard_absence"

FILLER_FIXTURES = [
    "rule_activation_exception_matrix",
    "temporal_state_ledger",
    "contradictory_evidence_packet",
    "count_composition_roster",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semantic-plan-json", type=Path, default=DEFAULT_SEMANTIC_PLAN)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--runs-per-model", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = build_plan(
        _read_json(_resolve(args.semantic_plan_json)),
        out_dir=_resolve(args.out_dir),
        runs_per_model=int(args.runs_per_model),
    )
    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_json = out_dir / "semantic_axis2_probe_plan.json"
    recipes_json = out_dir / "semantic_axis2_probe_recipes.json"
    plan_md = out_dir / "semantic_axis2_probe_plan.md"
    plan_json.write_text(json.dumps(plan["runner_plan"], ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    recipes_json.write_text(json.dumps(plan["recipes"], ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    plan_md.write_text(render_markdown(plan["runner_plan"], plan["recipes"]), encoding="utf-8")
    print(json.dumps({"fixtures": len(plan["runner_plan"]["fixtures"]), "rows": plan["runner_plan"]["expected_rows_per_model"], "json": str(plan_json), "markdown": str(plan_md)}, indent=2))
    return 0


def build_plan(semantic_plan: dict[str, Any], *, out_dir: Path, runs_per_model: int) -> dict[str, Any]:
    targets = [
        item
        for item in semantic_plan.get("fixtures", [])
        if item.get("probe_id") == "absence_negative_evidence_vs_unresolved" and str(item.get("variant_id", "")).endswith("_hard")
    ]
    if not targets:
        raise ValueError("no hard absence semantic probe targets found")
    recipes: list[dict[str, Any]] = []
    fixtures: list[dict[str, Any]] = []
    assembly_root = out_dir / "assemblies"
    for target in targets:
        target_fixture = str(target["fixture"])
        for recipe in _recipes(target_fixture):
            assembly_dir = assembly_root / recipe["assembly_id"]
            assembly_dir.mkdir(parents=True, exist_ok=True)
            source, sections = _assemble_source(target, recipe)
            (assembly_dir / "source.md").write_text(source, encoding="utf-8")
            target_path = Path(str(target["dataset_path"]))
            shutil.copyfile(target_path / "qa_questions.jsonl", assembly_dir / "qa_questions.jsonl")
            shutil.copyfile(target_path / "oracle.jsonl", assembly_dir / "oracle.jsonl")
            row_count = _count_jsonl(assembly_dir / "qa_questions.jsonl")
            recipes.append({**recipe, "target_fixture": target_fixture, "sections": sections, "assembly_dir": str(assembly_dir)})
            fixtures.append(
                {
                    "fixture": recipe["assembly_id"],
                    "bucket": "semantic_axis2_probe",
                    "probe_id": target.get("probe_id", ""),
                    "variant_id": f"{target.get('variant_id', '')}__{recipe['condition']}",
                    "dataset_path": str(assembly_dir),
                    "source_file": "source.md",
                    "question_file": "qa_questions.jsonl",
                    "oracle_file": "oracle.jsonl",
                    "planned_rows": row_count,
                    "semantic_axis2_target_fixture": target_fixture,
                    "semantic_axis2_condition": recipe["condition"],
                }
            )
    runner_plan = {
        "schema_version": "semantic_axis2_probe_plan_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "run_settings": {"runs_per_model": runs_per_model},
        "fixtures": fixtures,
        "expected_rows_per_model": sum(int(item["planned_rows"]) for item in fixtures) * runs_per_model,
    }
    return {"runner_plan": runner_plan, "recipes": {"schema_version": "semantic_axis2_probe_recipes_v1", "recipes": recipes}}


def render_markdown(runner_plan: dict[str, Any], recipes: dict[str, Any]) -> str:
    lines = [
        "# Semantic Axis-2 Probe Plan",
        "",
        f"- Generated UTC: `{runner_plan.get('generated_utc', '')}`",
        f"- Fixtures: `{len(runner_plan.get('fixtures', []))}`",
        f"- Expected rows per model: `{runner_plan.get('expected_rows_per_model', 0)}`",
        "",
        "| Fixture | Target | Condition | Rows |",
        "| --- | --- | --- | ---: |",
    ]
    recipe_map = {recipe["assembly_id"]: recipe for recipe in recipes.get("recipes", [])}
    for fixture in runner_plan.get("fixtures", []):
        recipe = recipe_map.get(fixture["fixture"], {})
        lines.append(f"| `{fixture['fixture']}` | `{recipe.get('target_fixture', '')}` | `{fixture['semantic_axis2_condition']}` | {fixture['planned_rows']} |")
    lines.append("")
    return "\n".join(lines)


def _recipes(target_fixture: str) -> list[dict[str, Any]]:
    return [
        {"assembly_id": f"{target_fixture}__axis2_standalone", "condition": "standalone", "ordered": [target_fixture]},
        {"assembly_id": f"{target_fixture}__axis2_first", "condition": "stuffed_first", "ordered": [target_fixture, *FILLER_FIXTURES]},
        {"assembly_id": f"{target_fixture}__axis2_middle", "condition": "stuffed_middle", "ordered": [FILLER_FIXTURES[0], FILLER_FIXTURES[1], target_fixture, FILLER_FIXTURES[2], FILLER_FIXTURES[3]]},
        {"assembly_id": f"{target_fixture}__axis2_last", "condition": "stuffed_last", "ordered": [*FILLER_FIXTURES, target_fixture]},
    ]


def _assemble_source(target: dict[str, Any], recipe: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    target_fixture = str(target["fixture"])
    lines = [
        "# Semantic Axis-2 Context Assembly",
        "",
        f"Assembly ID: {recipe['assembly_id']}",
        f"Condition: {recipe['condition']}",
        "",
        "Answer the target questions using the relevant target source section. Other sections are distractor context.",
        "",
    ]
    sections: list[dict[str, Any]] = []
    for index, fixture_name in enumerate(recipe["ordered"], start=1):
        if fixture_name == target_fixture:
            source_path = Path(str(target["dataset_path"])) / "source.md"
            role = "target"
        else:
            source_path = REPO_ROOT / "datasets" / "story_worlds" / str(fixture_name) / "source.md"
            role = "filler"
        source = source_path.read_text(encoding="utf-8")
        lines.extend([f"## Source {index}: {fixture_name}", "", source.strip(), ""])
        sections.append({"index": index, "fixture": fixture_name, "role": role, "source_file": str(source_path), "approx_tokens": _estimate_tokens(source)})
    return "\n".join(lines).strip() + "\n", sections


def _estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))


def _count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
