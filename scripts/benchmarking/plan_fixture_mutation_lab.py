#!/usr/bin/env python3
"""Create deterministic fixture-mutation lab plans.

The mutation lab produces synthetic fixture directories under tmp. Mutations
that do not change the underlying source commitments reuse the original oracle,
so existing row scorers can measure degradation without inventing a new scoring
world.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab"
DEFAULT_FIXTURES = [
    "contradictory_evidence_packet",
    "rule_activation_exception_matrix",
    "temporal_state_ledger",
    "thornfield_variance",
]

EXECUTION_PLATFORMS = [
    {
        "platform": "POWER",
        "role": "primary_local_35b_workhorse",
        "backend": "lmstudio",
        "base_url": "http://127.0.0.1:1234/v1",
        "model": "qwen/qwen3.6-35b-a3b",
        "budget": "local",
    },
    {
        "platform": "POWER",
        "role": "local_ollama_fallback",
        "backend": "ollama",
        "base_url": "http://127.0.0.1:11434",
        "model": "qwen3.6:35b",
        "budget": "local",
    },
    {
        "platform": "OpenRouter",
        "role": "occasional_frontier_or_hosted_calibration",
        "backend": "openrouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "explicit_provider_model_id_required",
        "budget": "paid",
    },
    {
        "platform": "NITRO",
        "role": "sidecar_annex_small_model_stress_lane",
        "backend": "verified_at_runtime",
        "base_url": "verified_at_runtime",
        "model": "verified_at_runtime",
        "budget": "local_annex",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--fixture", action="append", default=[])
    parser.add_argument("--runs-per-model", type=int, default=1)
    parser.add_argument("--rows-per-fixture", type=int, default=40)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixtures = args.fixture or DEFAULT_FIXTURES
    out_dir = _resolve(args.out_dir)
    plan = build_mutation_lab_plan(
        fixtures=fixtures,
        out_dir=out_dir,
        runs_per_model=int(args.runs_per_model),
        rows_per_fixture=int(args.rows_per_fixture),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_json = out_dir / "fixture_mutation_lab_plan.json"
    recipe_json = out_dir / "fixture_mutation_lab_recipes.json"
    plan_md = out_dir / "fixture_mutation_lab_plan.md"
    plan_json.write_text(json.dumps(plan["runner_plan"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    recipe_json.write_text(json.dumps(plan["recipe_artifact"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_md.write_text(render_markdown(plan["recipe_artifact"], plan["runner_plan"]), encoding="utf-8")
    print(json.dumps({"plan_json": str(plan_json), "recipe_json": str(recipe_json), "plan_md": str(plan_md)}, indent=2))
    return 0


def build_mutation_lab_plan(
    *,
    fixtures: list[str],
    out_dir: Path,
    runs_per_model: int,
    rows_per_fixture: int,
) -> dict[str, Any]:
    generated: list[dict[str, Any]] = []
    recipes: list[dict[str, Any]] = []
    synthetic_root = out_dir / "fixtures"
    for fixture_name in fixtures:
        source_dir = REPO_ROOT / "datasets" / "story_worlds" / fixture_name
        if not source_dir.exists():
            raise FileNotFoundError(source_dir)
        source_text = (source_dir / "source.md").read_text(encoding="utf-8")
        questions, oracle_rows = _load_fixture_questions_and_oracle(source_dir)
        for mutation_id, mutated_source, mutated_questions, description in _mutations(source_text, questions):
            synthetic_id = f"{fixture_name}__{mutation_id}"
            synthetic_dir = synthetic_root / synthetic_id
            synthetic_dir.mkdir(parents=True, exist_ok=True)
            (synthetic_dir / "source.md").write_text(mutated_source.strip() + "\n", encoding="utf-8")
            _write_jsonl(synthetic_dir / "qa_questions.jsonl", mutated_questions)
            _write_jsonl(synthetic_dir / "oracle.jsonl", oracle_rows)
            recipe = {
                "synthetic_fixture": synthetic_id,
                "source_fixture": fixture_name,
                "lane_label": "mutation_fixture",
                "mutation_class": _mutation_class(mutation_id),
                "mutation_id": mutation_id,
                "description": description,
                "answer_oracle_policy": "unchanged_oracle_reused",
                "publication_policy": "exploratory_research_not_sealed_score",
                "source_char_count": len(mutated_source),
                "approx_source_tokens": _estimate_tokens(mutated_source),
                "question_count": len(mutated_questions),
                "synthetic_dir": str(synthetic_dir),
            }
            recipes.append(recipe)
            generated.append(
                {
                    "fixture": synthetic_id,
                    "bucket": "fixture_mutation_lab",
                    "bucket_label": "Deterministic fixture mutation lab",
                    "source_file": "source.md",
                    "question_file": "qa_questions.jsonl",
                    "scoring_file": "oracle.jsonl",
                    "question_count": len(mutated_questions),
                    "oracle_count": len(oracle_rows),
                    "planned_rows": min(rows_per_fixture, len(mutated_questions)),
                    "dataset_path": str(synthetic_dir),
                    "mutation_source_fixture": fixture_name,
                    "mutation_id": mutation_id,
                    "mutation_class": _mutation_class(mutation_id),
                }
            )
    runner_plan = {
        "schema_version": "fixture_mutation_lab_plan_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "policy": [
            "Exploratory local-model mutation lab; not publication methodology.",
            "Reuse original oracle only for mutations that preserve source commitments.",
            "Keep all synthetic fixtures under tmp/public_benchmark/mutation_lab.",
            "Prefer local 35B runs; frontier runs are calibration only.",
        ],
        "prompt_contract": {
            "system": "Answer only from the provided source document. If the source does not support an answer, say what is unresolved or not stated.",
            "user_template": "SOURCE DOCUMENT:\n{source}\n\nQUESTION:\n{question}\n\nReturn a concise answer and cite the source evidence in plain language.",
        },
        "run_settings": {
            "temperature": 0.0,
            "rows_per_fixture": rows_per_fixture,
            "runs_per_model": runs_per_model,
        },
        "fixtures": generated,
        "expected_rows_per_model": sum(int(item["planned_rows"]) for item in generated) * runs_per_model,
    }
    recipe_artifact = {
        "schema_version": "fixture_mutation_lab_recipes_v1",
        "generated_utc": runner_plan["generated_utc"],
        "source_fixtures": fixtures,
        "execution_platforms": EXECUTION_PLATFORMS,
        "recipes": recipes,
        "semantic_perturbation_candidates": _semantic_perturbation_candidates(fixtures),
    }
    return {"runner_plan": runner_plan, "recipe_artifact": recipe_artifact}


def _mutations(source: str, questions: list[dict[str, Any]]) -> list[tuple[str, str, list[dict[str, Any]], str]]:
    return [
        ("control", source, questions, "Original source and original question order."),
        ("strip_headings", _strip_headings(source), questions, "Remove Markdown heading markers while preserving text."),
        ("reverse_top_sections", _reverse_top_sections(source), questions, "Reverse top-level source sections after the title/header block."),
        ("punctuation_flattened", _punctuation_flattened(source), questions, "Flatten selected punctuation and list markers while preserving words."),
        ("typo_light_source", _typo_noise(source, heavy=False), questions, "Inject a small deterministic set of common typos into the source."),
        ("typo_heavy_source", _typo_noise(source, heavy=True), questions, "Inject a denser deterministic set of common typos into the source."),
        ("telegraphic_grammar_source", _telegraphic_grammar(source), questions, "Remove selected articles and connectors to create telegraphic grammar."),
        ("multilingual_headings", _multilingual_headings(source), questions, "Add Spanish/French/German section labels to Markdown headings."),
        ("international_dates", _international_dates(source), questions, "Convert ISO dates to day-month-name-year forms where possible."),
        ("reverse_questions", source, list(reversed(questions)), "Keep source unchanged but reverse question order."),
        (
            "qualifier_questions_last",
            source,
            _qualifier_questions_last(questions),
            "Move qualifier-sensitive categories to the end of the battery.",
        ),
        (
            "question_wrapper_es",
            source,
            _wrap_questions(questions, "Pregunta / Question"),
            "Wrap each question with a Spanish/English label while preserving the English question.",
        ),
        (
            "question_wrapper_fr_de",
            source,
            _wrap_questions(questions, "Question / Frage"),
            "Wrap each question with French/German labels while preserving the English question.",
        ),
    ]


def _mutation_class(mutation_id: str) -> str:
    if mutation_id in {"reverse_questions", "qualifier_questions_last", "question_wrapper_es", "question_wrapper_fr_de"}:
        return "question_battery_mangle"
    if mutation_id in {"strip_headings", "reverse_top_sections"}:
        return "source_layout_mangle"
    if mutation_id in {
        "punctuation_flattened",
        "typo_light_source",
        "typo_heavy_source",
        "telegraphic_grammar_source",
        "multilingual_headings",
        "international_dates",
    }:
        return "perception_surface_mangle"
    return "control"


def _semantic_perturbation_candidates(fixtures: list[str]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for fixture in fixtures:
        candidates.extend(_fixture_semantic_candidates(fixture))
    return candidates


def _fixture_semantic_candidates(fixture: str) -> list[dict[str, Any]]:
    generic = [
        {
            "source_fixture": fixture,
            "lane_label": "a_b_semantic_perturbation",
            "status": "candidate_requires_oracle_delta",
            "perturbation": "rename_identifier_near_collision",
            "intended_semantic_feature": "exact identifier preservation under near-collision pressure",
            "oracle_policy": "write affected-row oracle delta before scoring",
        },
        {
            "source_fixture": fixture,
            "lane_label": "lens_sensitivity_probe",
            "status": "candidate_requires_oracle_delta",
            "perturbation": "add_withdrawn_draft_with_tempting_wrong_answer",
            "intended_semantic_feature": "withdrawn/draft status must not become authority",
            "oracle_policy": "write affected-row oracle delta before scoring",
        },
    ]
    specific: dict[str, list[dict[str, Any]]] = {
        "contradictory_evidence_packet": [
            {
                "source_fixture": fixture,
                "lane_label": "a_b_semantic_perturbation",
                "status": "candidate_requires_oracle_delta",
                "perturbation": "move_BAS_clock_drift_across_date_boundary",
                "intended_semantic_feature": "timestamp correction changes date-qualified answers",
                "likely_affected_rows": ["q009", "q013", "q014", "q015", "q016"],
                "oracle_policy": "new oracle must preserve old raw timestamp, new corrected timestamp, and conflict status",
            },
            {
                "source_fixture": fixture,
                "lane_label": "a_b_semantic_perturbation",
                "status": "candidate_requires_oracle_delta",
                "perturbation": "change_CCTV_reliability_scope",
                "intended_semantic_feature": "source reliability scope changes identity/negative-existential answers",
                "likely_affected_rows": ["q017", "q018", "q035", "q036"],
                "oracle_policy": "new oracle must distinguish what CCTV establishes vs does not establish",
            },
        ],
        "rule_activation_exception_matrix": [
            {
                "source_fixture": fixture,
                "lane_label": "a_b_semantic_perturbation",
                "status": "candidate_requires_oracle_delta",
                "perturbation": "confirm_pending_payment_plan_before_deadline",
                "intended_semantic_feature": "unresolved/pending state becomes resolved and grant disposition recomputes",
                "likely_affected_rows": ["q017", "q029", "q030", "q034", "q035", "q037"],
                "oracle_policy": "new oracle must update pending count, approved/denied status, and dollar total",
            },
        ],
        "temporal_state_ledger": [
            {
                "source_fixture": fixture,
                "lane_label": "a_b_semantic_perturbation",
                "status": "candidate_requires_oracle_delta",
                "perturbation": "shift_sampler_timestamp_correction_across_snapshot",
                "intended_semantic_feature": "state snapshot answers follow corrected event time",
                "likely_affected_rows": ["q027", "q030", "q033"],
                "oracle_policy": "new oracle must distinguish as-logged time, corrected time, and operative rule",
            },
        ],
        "thornfield_variance": [
            {
                "source_fixture": fixture,
                "lane_label": "a_b_semantic_perturbation",
                "status": "candidate_requires_oracle_delta",
                "perturbation": "vote_correction_changes_threshold_outcome",
                "intended_semantic_feature": "correction impact flips outcome rather than merely correcting minutes",
                "likely_affected_rows": ["TV-020", "TV-021"],
                "oracle_policy": "new oracle must update both corrected vote and outcome threshold answer",
            },
        ],
    }
    return [*generic, *specific.get(fixture, [])]


def _strip_headings(source: str) -> str:
    lines = []
    for line in source.splitlines():
        lines.append(re.sub(r"^\s{0,3}#{1,6}\s+", "", line))
    return "\n".join(lines)


def _punctuation_flattened(source: str) -> str:
    text = source.replace("—", "-").replace("–", "-")
    text = re.sub(r"(?m)^\s*[-*]\s+", "- ", text)
    text = re.sub(r"[;:]", ",", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


TYPO_LIGHT = {
    "evidence": "evidnece",
    "investigation": "investigatoin",
    "authorized": "authroized",
    "unauthorized": "unauthroized",
    "timestamp": "timesatmp",
    "application": "applicaiton",
    "confirmed": "confimred",
    "committee": "commitee",
    "separate": "seperate",
    "occurred": "occured",
}

TYPO_HEAVY_EXTRA = {
    "building": "buidling",
    "maintenance": "maintenence",
    "supervisor": "superviosr",
    "reliable": "relaiable",
    "corrected": "corected",
    "according": "acording",
    "eligible": "eligble",
    "deadline": "deadlien",
    "authority": "authroity",
    "decision": "decison",
}


def _typo_noise(source: str, *, heavy: bool) -> str:
    replacements = dict(TYPO_LIGHT)
    if heavy:
        replacements.update(TYPO_HEAVY_EXTRA)
    text = source
    for original, typo in replacements.items():
        text = re.sub(rf"\b{re.escape(original)}\b", typo, text, flags=re.IGNORECASE)
    return text


def _telegraphic_grammar(source: str) -> str:
    text = re.sub(r"\b(the|a|an)\b\s+", "", source, flags=re.IGNORECASE)
    text = re.sub(r"\bthat\b\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bwhich\b\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def _multilingual_headings(source: str) -> str:
    labels = ["Seccion", "Section", "Abschnitt"]
    counter = 0
    lines = []
    for line in source.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            label = labels[counter % len(labels)]
            counter += 1
            lines.append(f"{match.group(1)} {label}: {match.group(2)}")
        else:
            lines.append(line)
    return "\n".join(lines)


MONTHS = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "Jun",
    "07": "Jul",
    "08": "Aug",
    "09": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}


def _international_dates(source: str) -> str:
    def replace(match: re.Match[str]) -> str:
        year, month, day = match.group(1), match.group(2), match.group(3)
        return f"{day} {MONTHS.get(month, month)} {year}"

    return re.sub(r"(?<![A-Za-z0-9_-])(20\d{2})-(\d{2})-(\d{2})(?![A-Za-z0-9_-])", replace, source)


def _reverse_top_sections(source: str) -> str:
    lines = source.splitlines()
    chunks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if re.match(r"^##\s+", line) and current:
            chunks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append(current)
    if len(chunks) <= 2:
        return source
    header = chunks[0]
    body = chunks[1:]
    return "\n".join(line for chunk in [header, *reversed(body)] for line in chunk)


def _qualifier_questions_last(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sensitive = {"unresolved", "negative_existential", "temporal", "temporal_interval", "authority", "composition"}
    early = [row for row in questions if str(row.get("category", "")) not in sensitive]
    late = [row for row in questions if str(row.get("category", "")) in sensitive]
    return early + late


def _wrap_questions(questions: list[dict[str, Any]], label: str) -> list[dict[str, Any]]:
    wrapped: list[dict[str, Any]] = []
    for row in questions:
        copy = dict(row)
        copy["question"] = f"{label}: {row.get('question', '')}"
        wrapped.append(copy)
    return wrapped


def render_markdown(recipe_artifact: dict[str, Any], runner_plan: dict[str, Any]) -> str:
    lines = [
        "# Fixture Mutation Lab Plan",
        "",
        f"- Generated UTC: `{recipe_artifact.get('generated_utc', '')}`",
        f"- Source fixtures: `{len(recipe_artifact.get('source_fixtures', []))}`",
        f"- Synthetic fixtures: `{len(runner_plan.get('fixtures', []))}`",
        f"- Expected rows per model: `{runner_plan.get('expected_rows_per_model', 0)}`",
        "",
        "## Execution Platforms",
        "",
        "| Platform | Role | Backend | Base URL | Model | Budget |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for platform in recipe_artifact.get("execution_platforms", []):
        lines.append(
            f"| `{platform.get('platform', '')}` | `{platform.get('role', '')}` | "
            f"`{platform.get('backend', '')}` | `{platform.get('base_url', '')}` | "
            f"`{platform.get('model', '')}` | `{platform.get('budget', '')}` |"
        )
    lines.extend(
        [
            "",
        "## Recipes",
        "",
        "| Synthetic Fixture | Source Fixture | Mutation | Questions | Approx Source Tokens |",
        "| --- | --- | --- | ---: | ---: |",
        ]
    )
    for recipe in recipe_artifact.get("recipes", []):
        lines.append(
            f"| `{recipe.get('synthetic_fixture', '')}` | `{recipe.get('source_fixture', '')}` | "
            f"`{recipe.get('mutation_id', '')}` | {recipe.get('question_count', 0)} | "
            f"{recipe.get('approx_source_tokens', 0)} |"
        )
    lines.extend(["", "## Intended Runner", "", "Use local 35B first, for example:", ""])
    lines.append(
        "```powershell\n"
        "python scripts/benchmarking/run_frontier_battery_qa.py `\n"
        "  --plan-json tmp/public_benchmark/mutation_lab/fixture_mutation_lab_plan.json `\n"
        "  --model qwen/qwen3.6-35b-a3b `\n"
        "  --provider lmstudio `\n"
        "  --base-url http://127.0.0.1:1234/v1 `\n"
        "  --runs-per-model 1 `\n"
        "  --out-dir tmp/public_benchmark/mutation_lab/battery_outputs\n"
        "```"
    )
    candidates = recipe_artifact.get("semantic_perturbation_candidates", [])
    lines.extend(
        [
            "",
            "## Semantic Perturbation Candidates",
            "",
            "These are not runnable with the unchanged oracle. They require explicit oracle deltas first.",
            "",
            "| Source Fixture | Lane | Perturbation | Intended Feature | Likely Rows |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for candidate in candidates:
        lines.append(
            f"| `{candidate.get('source_fixture', '')}` | `{candidate.get('lane_label', '')}` | "
            f"`{candidate.get('perturbation', '')}` | {candidate.get('intended_semantic_feature', '')} | "
            f"`{candidate.get('likely_affected_rows', [])}` |"
        )
    return "\n".join(lines)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_fixture_questions_and_oracle(source_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    questions_path = source_dir / "qa_questions.jsonl"
    oracle_path = source_dir / "oracle.jsonl"
    if questions_path.exists() and oracle_path.exists():
        return _load_jsonl(questions_path), _load_jsonl(oracle_path)
    for battery_name in ("qa_battery_40.json", "qa_battery.json"):
        battery_path = source_dir / battery_name
        if battery_path.exists():
            return _split_battery_json(battery_path, source_id=source_dir.name)
    battery_jsonl = source_dir / "qa_battery.jsonl"
    if battery_jsonl.exists():
        return _split_battery_rows(_load_jsonl(battery_jsonl), source_id=source_dir.name)
    raise FileNotFoundError(f"no supported QA/oracle files under {source_dir}")


def _split_battery_json(path: Path, *, source_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for key in ("questions", "items", "rows", "battery"):
            if isinstance(data.get(key), list):
                return _split_battery_rows(data[key], source_id=source_id)
    if isinstance(data, list):
        return _split_battery_rows(data, source_id=source_id)
    raise ValueError(f"unsupported battery shape: {path}")


def _split_battery_rows(rows: list[dict[str, Any]], *, source_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    questions: list[dict[str, Any]] = []
    oracle: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        qid = str(row.get("id") or row.get("question_id") or f"q{index:03d}").strip()
        question = str(row.get("question") or row.get("prompt") or "").strip()
        answer = str(row.get("reference_answer") or row.get("answer") or "").strip()
        category = str(row.get("category") or "").strip()
        if not qid or not question or not answer:
            continue
        questions.append({"id": qid, "question": question, "category": category, "source_id": source_id})
        oracle.append({"id": qid, "reference_answer": answer, "category": category, "source_id": source_id})
    return questions, oracle


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip()) if path.exists() else 0


def _estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
