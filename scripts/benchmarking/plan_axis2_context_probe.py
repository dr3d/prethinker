#!/usr/bin/env python3
"""Create minimal Axis-2 context-assembly probe fixtures and plan.

The probe keeps the target questions and oracle fixed, changing only the
context assembly. It writes synthetic fixture directories under tmp so the
existing direct frontier runner and scorer can be reused unchanged.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PILOT_PLAN = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_pilot_plan.json"
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "public_benchmark" / "axis2_probe"

TARGET_FIXTURE = "contradictory_evidence_packet"
FILLER_FIXTURES = [
    "rule_activation_exception_matrix",
    "hospital_shift_exception_log",
    "authority_possession_custody_packet",
    "count_composition_roster",
    "larkspur_clockwork_fair",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-plan-json", type=Path, default=DEFAULT_PILOT_PLAN)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--target-fixture", default=TARGET_FIXTURE)
    parser.add_argument("--runs-per-model", type=int, default=3)
    parser.add_argument("--rows-per-fixture", type=int, default=40)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pilot_plan_path = _resolve(args.pilot_plan_json)
    out_dir = _resolve(args.out_dir)
    plan = build_axis2_plan(
        _read_json(pilot_plan_path),
        out_dir=out_dir,
        target_fixture=str(args.target_fixture),
        runs_per_model=int(args.runs_per_model),
        rows_per_fixture=int(args.rows_per_fixture),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_json = out_dir / "axis2_context_probe_plan.json"
    recipe_json = out_dir / "axis2_context_probe_recipes.json"
    plan_md = out_dir / "axis2_context_probe_plan.md"
    plan_json.write_text(json.dumps(plan["runner_plan"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    recipe_json.write_text(json.dumps(plan["recipe_artifact"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_md.write_text(render_markdown(plan["recipe_artifact"], plan["runner_plan"]), encoding="utf-8")
    print(json.dumps({"plan_json": str(plan_json), "recipe_json": str(recipe_json), "plan_md": str(plan_md)}, indent=2))
    return 0


def build_axis2_plan(
    pilot_plan: dict[str, Any],
    *,
    out_dir: Path,
    target_fixture: str,
    runs_per_model: int,
    rows_per_fixture: int,
) -> dict[str, Any]:
    fixture_map = {str(item.get("fixture", "")): item for item in pilot_plan.get("fixtures", []) if isinstance(item, dict)}
    for name in [target_fixture, *FILLER_FIXTURES]:
        if name not in fixture_map:
            fixture_path = REPO_ROOT / "datasets" / "story_worlds" / name
            if fixture_path.exists():
                fixture_map[name] = {
                    "fixture": name,
                    "dataset_path": str(fixture_path),
                    "source_file": "source.md",
                    "question_file": "qa_questions.jsonl",
                    "scoring_file": "oracle.jsonl",
                    "question_count": _count_jsonl(fixture_path / "qa_questions.jsonl"),
                    "oracle_count": _count_jsonl(fixture_path / "oracle.jsonl"),
                    "planned_rows": rows_per_fixture,
                }
    if target_fixture not in fixture_map:
        raise ValueError(f"target fixture not found in pilot plan: {target_fixture}")
    target = fixture_map[target_fixture]
    filler_names = [name for name in FILLER_FIXTURES if name in fixture_map and name != target_fixture]
    if len(filler_names) < 4:
        raise ValueError(f"need at least four filler fixtures, found: {filler_names}")
    recipes = _recipes(target_fixture, filler_names)
    assembly_root = out_dir / "assemblies"
    generated_fixtures: list[dict[str, Any]] = []
    recipe_rows: list[dict[str, Any]] = []
    for recipe in recipes:
        assembly_dir = assembly_root / str(recipe["assembly_id"])
        assembly_dir.mkdir(parents=True, exist_ok=True)
        source_text, sections = _assemble_source(recipe, fixture_map)
        (assembly_dir / "source.md").write_text(source_text, encoding="utf-8")
        _copy_target_files(target, assembly_dir)
        token_estimate = _estimate_tokens(source_text)
        recipe_record = {
            **recipe,
            "target_position": _target_position(recipe),
            "section_count": len(sections),
            "sections": sections,
            "approx_prompt_tokens_source_only": token_estimate,
            "assembly_dir": str(assembly_dir),
        }
        recipe_rows.append(recipe_record)
        generated_fixtures.append(
            {
                "fixture": recipe["assembly_id"],
                "bucket": "axis2_context_probe",
                "bucket_label": "Axis 2 context assembly probe",
                "source_file": "source.md",
                "question_file": "qa_questions.jsonl",
                "scoring_file": "oracle.jsonl",
                "question_count": int(target.get("question_count", rows_per_fixture) or rows_per_fixture),
                "oracle_count": int(target.get("oracle_count", rows_per_fixture) or rows_per_fixture),
                "planned_rows": rows_per_fixture,
                "dataset_path": str(assembly_dir),
                "axis2_recipe_id": recipe["assembly_id"],
                "axis2_target_fixture": target_fixture,
                "axis2_condition": recipe["condition"],
            }
        )
    runner_plan = {
        "schema_version": "axis2_context_probe_plan_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_pilot_plan": str(_resolve(DEFAULT_PILOT_PLAN)),
        "policy": [
            "Axis-2 minimum probe: change context assembly only.",
            "Target questions and target oracle are copied unchanged into each synthetic fixture.",
            "No fixture strategy notes, anti-leakage manifests, Prethinker traces, or oracle answers are included in model context.",
            "Score with the same direct QA scorer used for the frontier pilot.",
            "Store assembly recipes with every result so context conditions are reproducible.",
        ],
        "prompt_contract": pilot_plan.get("prompt_contract", {}),
        "run_settings": {
            **(pilot_plan.get("run_settings") if isinstance(pilot_plan.get("run_settings"), dict) else {}),
            "rows_per_fixture": rows_per_fixture,
            "runs_per_model": runs_per_model,
        },
        "models": pilot_plan.get("models", []),
        "fixtures": generated_fixtures,
        "expected_rows_per_model": len(generated_fixtures) * rows_per_fixture * runs_per_model,
    }
    recipe_artifact = {
        "schema_version": "axis2_context_probe_recipes_v1",
        "generated_utc": runner_plan["generated_utc"],
        "target_fixture": target_fixture,
        "target_question_file": str(_fixture_path(target) / str(target.get("question_file") or "qa_questions.jsonl")),
        "target_oracle_file": str(_fixture_path(target) / str(target.get("scoring_file") or "oracle.jsonl")),
        "recipes": recipe_rows,
    }
    return {"runner_plan": runner_plan, "recipe_artifact": recipe_artifact}


def _recipes(target_fixture: str, filler_names: list[str]) -> list[dict[str, Any]]:
    first_four = filler_names[:4]
    return [
        {
            "assembly_id": f"{target_fixture}__standalone",
            "condition": "standalone",
            "description": "Target fixture alone, matching the direct single-document condition.",
            "ordered_fixtures": [target_fixture],
            "filler_fixtures": [],
        },
        {
            "assembly_id": f"{target_fixture}__stuffed_first",
            "condition": "stuffed_first",
            "description": "Target fixture first, followed by four filler fixtures.",
            "ordered_fixtures": [target_fixture, *first_four],
            "filler_fixtures": first_four,
        },
        {
            "assembly_id": f"{target_fixture}__stuffed_middle",
            "condition": "stuffed_middle",
            "description": "Target fixture buried in the middle of four filler fixtures.",
            "ordered_fixtures": [first_four[0], first_four[1], target_fixture, first_four[2], first_four[3]],
            "filler_fixtures": first_four,
        },
        {
            "assembly_id": f"{target_fixture}__stuffed_last",
            "condition": "stuffed_last",
            "description": "Target fixture last, after four filler fixtures.",
            "ordered_fixtures": [*first_four, target_fixture],
            "filler_fixtures": first_four,
        },
    ]


def _assemble_source(recipe: dict[str, Any], fixture_map: dict[str, dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    lines = [
        "# Axis-2 Context Assembly",
        "",
        f"Assembly ID: {recipe['assembly_id']}",
        f"Condition: {recipe['condition']}",
        "",
        "The following source documents are provided as separate sections. Answer target questions using the relevant source section only.",
        "",
    ]
    sections: list[dict[str, Any]] = []
    target_fixture = str(recipe["assembly_id"]).split("__", 1)[0]
    for index, fixture_name in enumerate(recipe["ordered_fixtures"], start=1):
        fixture = fixture_map[str(fixture_name)]
        source_path = _fixture_path(fixture) / str(fixture.get("source_file") or "source.md")
        source_text = source_path.read_text(encoding="utf-8")
        section_heading = f"## Source {index}: {fixture_name}"
        lines.extend([section_heading, "", source_text.strip(), ""])
        sections.append(
            {
                "index": index,
                "fixture": fixture_name,
                "source_file": str(source_path),
                "role": "target" if str(fixture_name) == target_fixture else "filler",
                "char_count": len(source_text),
                "approx_tokens": _estimate_tokens(source_text),
            }
        )
    return "\n".join(lines).strip() + "\n", sections


def _copy_target_files(target: dict[str, Any], assembly_dir: Path) -> None:
    target_dir = _fixture_path(target)
    for filename in ("qa_questions.jsonl", "oracle.jsonl"):
        source = target_dir / filename
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copyfile(source, assembly_dir / filename)


def _target_position(recipe: dict[str, Any]) -> int:
    ordered = [str(item) for item in recipe.get("ordered_fixtures", [])]
    target = str(recipe["assembly_id"]).split("__", 1)[0]
    return ordered.index(target) + 1


def render_markdown(recipe_artifact: dict[str, Any], runner_plan: dict[str, Any]) -> str:
    lines = [
        "# Axis-2 Context Probe Plan",
        "",
        f"- Generated UTC: `{recipe_artifact.get('generated_utc', '')}`",
        f"- Target fixture: `{recipe_artifact.get('target_fixture', '')}`",
        f"- Synthetic fixtures: `{len(runner_plan.get('fixtures', []))}`",
        f"- Expected rows per model: `{runner_plan.get('expected_rows_per_model', 0)}`",
        "",
        "## Recipes",
        "",
        "| Assembly | Condition | Target Position | Sections | Approx Source Tokens | Ordered Fixtures |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for recipe in recipe_artifact.get("recipes", []):
        lines.append(
            "| `{assembly}` | `{condition}` | {position} | {sections} | {tokens} | {ordered} |".format(
                assembly=recipe.get("assembly_id", ""),
                condition=recipe.get("condition", ""),
                position=recipe.get("target_position", ""),
                sections=recipe.get("section_count", ""),
                tokens=recipe.get("approx_prompt_tokens_source_only", ""),
                ordered=", ".join(f"`{item}`" for item in recipe.get("ordered_fixtures", [])),
            )
        )
    lines.extend(
        [
            "",
            "## Runner",
            "",
            "Use `scripts/benchmarking/run_frontier_direct_qa.py` with this plan, then score with `score_frontier_direct_qa.py`.",
            "The only intended experimental change is source context assembly.",
            "",
        ]
    )
    return "\n".join(lines)


def _estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def _fixture_path(fixture: dict[str, Any]) -> Path:
    path = Path(str(fixture.get("dataset_path", "")))
    return path if path.is_absolute() else REPO_ROOT / path


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
