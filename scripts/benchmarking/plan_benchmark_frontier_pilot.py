#!/usr/bin/env python3
"""Plan the first data-first frontier LLM benchmark pilot.

This planner freezes a small, publication-facing comparison slice before any
curation. It reads the corpus manifest produced by
build_public_benchmark_manifest.py and emits a run plan for direct LLM baselines.
It does not read source prose or oracle answers.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO_ROOT / "tmp" / "public_benchmark" / "corpus_manifest.json"
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_pilot_plan.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_pilot_plan.md"

DEFAULT_FIXTURE_BUCKETS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "surgical",
        "Early surgical extraction/state fixtures",
        ("fenmore_seedbank", "greywell_pipeline"),
    ),
    (
        "state_tracking_story",
        "Story/state-tracking fixtures",
        ("larkspur_clockwork_fair", "dream_library_index"),
    ),
    (
        "self_authored",
        "Self-authored/sealed submission-style fixtures",
        ("lantern_school_field_trip", "tournament_borrowed_names"),
    ),
    (
        "claude8_dense",
        "Claude 8 dense operational records",
        ("hospital_shift_exception_log", "estate_archive_access_dispute"),
    ),
    (
        "precision_batch",
        "Precision stress fixtures",
        ("rule_activation_exception_matrix", "contradictory_evidence_packet"),
    ),
)

DEFAULT_MODEL_FAMILIES: tuple[dict[str, str], ...] = (
    {
        "provider_family": "openai",
        "model_role": "frontier_openai",
        "model_id": "openai/gpt-5.5",
    },
    {
        "provider_family": "anthropic",
        "model_role": "frontier_anthropic",
        "model_id": "anthropic/claude-opus-4.7",
    },
    {
        "provider_family": "google",
        "model_role": "frontier_google",
        "model_id": "google/gemini-3.1-pro-preview",
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument(
        "--fixture",
        action="append",
        default=[],
        help="Override fixture slug. Repeat to supply an explicit pilot list.",
    )
    parser.add_argument("--model", action="append", default=[], help="Optional concrete model id. Repeat.")
    parser.add_argument("--rows-per-fixture", type=int, default=40)
    parser.add_argument("--runs-per-model", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=0.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = _resolve(args.manifest_json)
    manifest = _read_json(manifest_path)
    fixture_rows = _fixture_map(manifest)
    fixtures = _select_fixtures(
        fixture_rows,
        override=[str(item) for item in args.fixture],
        rows_per_fixture=int(args.rows_per_fixture),
    )
    models = _models([str(item) for item in args.model])
    expected_rows = sum(int(item.get("planned_rows", 0) or 0) for item in fixtures)
    runs_per_model = max(1, int(args.runs_per_model))
    plan = {
        "schema_version": "benchmark_frontier_pilot_plan_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_json": str(manifest_path),
        "policy": [
            "Data-first frontier comparison before benchmark curation.",
            "Direct source-plus-question prompts only for frontier baselines.",
            "No fixture strategy notes, anti-leakage manifests, Prethinker traces, or oracle answers in model context.",
            "Score frontier outputs with the same exact/partial/miss row schema used for Prethinker.",
            "Use exact provider model ids verified at run time; do not rely on stale aliases.",
            "Default model ids were verified against the OpenRouter catalog on 2026-05-09.",
        ],
        "prompt_contract": {
            "system": "Answer only from the provided source document. If the source does not support an answer, say what is unresolved or not stated.",
            "user_template": "SOURCE DOCUMENT:\\n{source}\\n\\nQUESTION:\\n{question}\\n\\nReturn a concise answer and cite the source evidence in plain language.",
        },
        "run_settings": {
            "temperature": float(args.temperature),
            "rows_per_fixture": int(args.rows_per_fixture),
            "runs_per_model": runs_per_model,
            "retry_policy": "one retry for transport or parse failure; no answer-repair retry",
        },
        "models": models,
        "fixture_buckets": _bucket_plan(fixtures),
        "fixtures": fixtures,
        "expected_rows": expected_rows,
        "expected_model_calls": expected_rows * len(models) * runs_per_model,
        "output_columns": [
            "fixture",
            "question_id",
            "run_index",
            "category",
            "prethinker_score",
            "model_provider",
            "model_id",
            "frontier_answer",
            "frontier_score",
            "frontier_average",
            "prethinker_minus_frontier_average",
            "notes",
        ],
    }
    out_json = _resolve(args.out_json)
    out_md = _resolve(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(_render_markdown(plan), encoding="utf-8")
    print(json.dumps({"fixtures": len(fixtures), "models": len(models), "json": str(out_json), "markdown": str(out_md)}, indent=2))
    return 0


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _fixture_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = manifest.get("fixtures") if isinstance(manifest.get("fixtures"), list) else []
    return {str(row.get("fixture", "")): row for row in rows if isinstance(row, dict)}


def _select_fixtures(
    fixture_rows: dict[str, dict[str, Any]],
    *,
    override: list[str],
    rows_per_fixture: int = 40,
) -> list[dict[str, Any]]:
    if override:
        buckets = (("explicit", "Explicit fixtures", tuple(override)),)
    else:
        buckets = DEFAULT_FIXTURE_BUCKETS
    selected: list[dict[str, Any]] = []
    for bucket_id, bucket_label, slugs in buckets:
        for slug in slugs:
            row = fixture_rows.get(slug)
            if not row:
                raise ValueError(f"Fixture is not present in manifest: {slug}")
            status = str(row.get("publication_status", ""))
            if status != "ready_with_scored_history":
                raise ValueError(f"Fixture is not publication-ready for pilot: {slug} ({status})")
            planned_rows = min(
                max(1, int(rows_per_fixture)),
                int(row.get("oracle_count", row.get("question_count", 0)) or 0),
            )
            selected.append(
                {
                    "fixture": slug,
                    "bucket": bucket_id,
                    "bucket_label": bucket_label,
                    "source_file": row.get("source_file", ""),
                    "question_file": row.get("question_file", ""),
                    "scoring_file": row.get("scoring_file", ""),
                    "question_count": row.get("question_count", 0),
                    "oracle_count": row.get("oracle_count", 0),
                    "planned_rows": planned_rows,
                    "dataset_path": row.get("path", ""),
                }
            )
    return selected


def _models(model_ids: list[str]) -> list[dict[str, str]]:
    if not model_ids:
        return [dict(item) for item in DEFAULT_MODEL_FAMILIES]
    return [
        {
            "provider_family": "explicit",
            "model_role": f"frontier_model_{index:02d}",
            "model_id": model_id,
        }
        for index, model_id in enumerate(model_ids, start=1)
    ]


def _bucket_plan(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for fixture in fixtures:
        bucket = str(fixture.get("bucket", ""))
        item = buckets.setdefault(
            bucket,
            {
                "bucket": bucket,
                "label": fixture.get("bucket_label", ""),
                "fixtures": [],
                "planned_rows": 0,
            },
        )
        item["fixtures"].append(fixture.get("fixture", ""))
        item["planned_rows"] += int(fixture.get("planned_rows", 0) or 0)
    return list(buckets.values())


def _render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Frontier LLM Pilot Plan",
        "",
        f"- Generated UTC: `{plan.get('generated_utc', '')}`",
        f"- Manifest: `{plan.get('manifest_json', '')}`",
        f"- Fixtures: `{len(plan.get('fixtures', []))}`",
        f"- Planned rows: `{plan.get('expected_rows', 0)}`",
        f"- Runs per model: `{plan.get('run_settings', {}).get('runs_per_model', 1)}`",
        f"- Models: `{len(plan.get('models', []))}`",
        f"- Expected model calls: `{plan.get('expected_model_calls', 0)}`",
        "",
        "## Policy",
        "",
    ]
    for item in plan.get("policy", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Models",
            "",
            "| Role | Provider Family | Model ID |",
            "| --- | --- | --- |",
        ]
    )
    for model in plan.get("models", []):
        lines.append(
            f"| `{model.get('model_role', '')}` | `{model.get('provider_family', '')}` | `{model.get('model_id', '')}` |"
        )
    lines.extend(
        [
            "",
            "## Fixture Buckets",
            "",
            "| Bucket | Fixtures | Planned Rows |",
            "| --- | --- | ---: |",
        ]
    )
    for bucket in plan.get("fixture_buckets", []):
        fixtures = ", ".join(f"`{item}`" for item in bucket.get("fixtures", []))
        lines.append(f"| `{bucket.get('bucket', '')}` | {fixtures} | {bucket.get('planned_rows', 0)} |")
    lines.extend(
        [
            "",
            "## Fixtures",
            "",
            "| Fixture | Bucket | Source | Questions | Oracle Rows | Planned Rows |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for fixture in plan.get("fixtures", []):
        lines.append(
            "| `{fixture}` | `{bucket}` | `{source}` | {questions} | {oracle} | {planned} |".format(
                fixture=fixture.get("fixture", ""),
                bucket=fixture.get("bucket", ""),
                source=fixture.get("source_file", ""),
                questions=fixture.get("question_count", 0),
                oracle=fixture.get("oracle_count", 0),
                planned=fixture.get("planned_rows", 0),
            )
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
