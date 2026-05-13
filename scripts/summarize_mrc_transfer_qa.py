#!/usr/bin/env python3
"""Summarize external MRC transfer QA runs into reusable boundary coordinates."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


PROPOSITION_TYPE_CRITERIA: dict[str, str] = {
    "factual": (
        "Answer is a directly stated event, entity, attribute, value, location, "
        "or relation; no comparison, category choice, synthesis, or unstated "
        "mental/causal inference is required."
    ),
    "comparative": (
        "Answer requires ordering, contrast, arithmetic, duration, count, date, "
        "threshold, before/after, more/less, first/last, or other relation among "
        "two or more extracted facts."
    ),
    "categorical": (
        "Answer selects or maps an extracted fact to a type, role, class, label, "
        "meaning, audience, object kind, or option category."
    ),
    "synthesis": (
        "Answer condenses multiple facts into a title, theme, main idea, passage "
        "purpose, summary, rhetorical point, or best overall description."
    ),
    "inference": (
        "Answer depends on an unstated consequence, attitude, motivation, belief, "
        "intent, cause, implication, or reader conclusion licensed by evidence."
    ),
}

PROPOSITION_TYPE_OPERATIONAL_RULES: list[str] = [
    "Classify the proposition the question asks the system to evaluate, not the dataset format or answer option text.",
    "Remove multiple-choice options before detecting the asked proposition; use options only as answer evidence when needed.",
    "Apply precedence in this order: synthesis, comparative, categorical, inference, factual.",
    "Use synthesis only when the answer must summarize purpose, theme, title, main idea, or overall rhetorical role.",
    "Use comparative when the answer requires an ordered, numeric, temporal, threshold, count, duration, or before/after relation, even if the final answer is a named option.",
    "Use categorical when the answer maps a stated fact to a class, role, label, meaning, audience, or object kind.",
    "Use inference when the answer depends on an unstated attitude, motivation, cause, consequence, belief, intent, or licensed reader conclusion.",
    "Use factual only when the answer is directly stated as an event, entity, attribute, value, location, or relation after the higher-precedence tests do not apply.",
]


def main() -> int:
    args = _parse_args()
    qa_root = _abs(args.qa_root)
    summary = summarize_run(qa_root)
    out_json = _abs(args.out_json) if args.out_json else qa_root / "transfer_coordinate_summary.json"
    out_md = _abs(args.out_md) if args.out_md else qa_root / "transfer_coordinate_summary.md"
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_md(summary), encoding="utf-8")
    print(json.dumps(summary["totals"], sort_keys=True))
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-root", type=Path, required=True)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def summarize_run(qa_root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    by_surface: Counter[str] = Counter()
    by_coordinate: Counter[str] = Counter()
    by_proposition_type: Counter[str] = Counter()
    by_config: dict[str, Counter[str]] = {"high": Counter(), "middle": Counter()}

    for qa_json in sorted(qa_root.glob("*/domain_bootstrap_qa_*.json")):
        payload = json.loads(qa_json.read_text(encoding="utf-8"))
        fixture = qa_json.parent.name
        config = "middle" if fixture.startswith("race_middle_") else "high" if fixture.startswith("race_high_") else "unknown"
        for row in payload.get("rows", []):
            verdict = _verdict(row)
            totals[verdict] += 1
            if config in by_config:
                by_config[config][verdict] += 1
            if verdict == "exact":
                continue
            surface = str((row.get("failure_surface") or {}).get("surface") or "unknown")
            coordinate = classify_transfer_coordinate(row)
            proposition_type = classify_proposition_type(row)
            by_surface[surface] += 1
            by_coordinate[coordinate] += 1
            by_proposition_type[proposition_type] += 1
            rows.append(
                {
                    "fixture": fixture,
                    "id": row.get("id"),
                    "verdict": verdict,
                    "surface": surface,
                    "coordinate": coordinate,
                    "proposition_type": proposition_type,
                    "question": row.get("utterance"),
                    "reference_answer": row.get("reference_answer"),
                    "rationale": str((row.get("failure_surface") or {}).get("rationale") or "")[:600],
                    "qa_json": str(qa_json),
                }
            )

    question_count = sum(totals.values())
    exact = totals.get("exact", 0)
    partial = totals.get("partial", 0)
    miss = totals.get("miss", 0)
    not_judged = totals.get("not_judged", 0)
    return {
        "schema_version": "mrc_transfer_coordinate_summary_v2",
        "qa_root": str(qa_root),
        "proposition_type_criteria": PROPOSITION_TYPE_CRITERIA,
        "proposition_type_operational_rules": PROPOSITION_TYPE_OPERATIONAL_RULES,
        "totals": {
            "question_count": question_count,
            "exact": exact,
            "partial": partial,
            "miss": miss,
            "not_judged": not_judged,
            "non_exact": partial + miss + not_judged,
            "exact_rate": round(exact / question_count, 4) if question_count else 0.0,
        },
        "by_config": {key: dict(value) for key, value in by_config.items()},
        "proposition_type_counts": dict(by_proposition_type),
        "failure_surface_counts": dict(by_surface),
        "transfer_coordinate_counts": dict(by_coordinate),
        "non_exact_rows": rows,
    }


def classify_proposition_type(row: dict[str, Any]) -> str:
    """Classify the proposition being asked, independent of QA format.

    The operational contract is intentionally precedence ordered. A question
    can contain words that look factual or comparative while still asking for a
    synthesis or inference proposition.
    """
    question = _strip_options(str(row.get("utterance") or ""))
    answer = str(row.get("reference_answer") or "")
    rationale = str((row.get("failure_surface") or {}).get("rationale") or "")
    coordinate = classify_transfer_coordinate(row)
    text = " ".join([question, answer, rationale]).casefold()

    if coordinate == "title_theme_or_summary_answer" or _has_any(
        text,
        [
            "best title",
            "main idea",
            "mainly about",
            "theme",
            "subject of the passage",
            "passage is about",
            "purpose of the passage",
            "why does the author mention",
            "why did the author mention",
            "writer wrote this passage",
            "author wrote this passage",
            "what can we learn from the passage",
            "what can you learn from the passage",
            "best summary",
        ],
    ):
        return "synthesis"

    if _is_comparative_proposition(question, answer, coordinate):
        return "comparative"

    if _is_categorical_proposition(question, answer, coordinate):
        return "categorical"

    if coordinate == "implicit_attitude_or_consequence" or _has_any(
        text,
        [
            "state of",
            "infer",
            "imply",
            "suggest",
            "conclude",
            "feel",
            "felt",
            "thought",
            "think",
            "believ",
            "attitude",
            "emotion",
            "consequence",
            "why",
            "because",
            "reason",
            "motivation",
            "intent",
            "likely",
            "probably",
            "relief",
            "touched",
            "pessimistic",
            "optimistic",
            "confident",
            "disappointed",
            "anxiety",
            "anger",
            "afraid",
            "happy",
            "sad",
        ],
    ):
        return "inference"

    return "factual"


def _is_comparative_proposition(question: str, answer: str, coordinate: str) -> bool:
    question_text = question.casefold()
    text = " ".join([question, answer]).casefold()
    if coordinate == "formula_or_rule_application":
        return True
    if _has_any(
        text,
        [
            "compare",
            "comparison",
            "more than",
            "less than",
            "no more than",
            "at least",
            "at most",
            "earlier",
            "later",
            "older",
            "younger",
        ],
    ):
        return True
    if re.search(r"\bwhich\b.*\b(fewest|most|least|largest|smallest)\b", question_text):
        return True
    if re.search(r"\b(how many|how much|how long)\b", text):
        return True
    if re.search(r"^\s*(when|what time|which day|which year|what year)\b", question_text):
        return True
    if re.search(r"\b\d+\b", answer) or re.search(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\b", answer.casefold()):
        return True
    return False


def _is_categorical_proposition(question: str, answer: str, coordinate: str) -> bool:
    question_text = question.casefold()
    text = " ".join([question, answer]).casefold()
    if _has_any(
        text,
        [
            "what kind",
            "what type",
            "which kind",
            "which type",
            "described as",
            "best described as",
            "meaning of",
            "means",
            "stands for",
            "category",
            "label",
        ],
    ):
        return True
    if _has_any(question_text, ["intended for", "seems to be", "appears to be", "relationship"]):
        return True
    if coordinate == "background_role_or_audience_fact" and re.search(r"\b(who|what)\s+(is|are|was|were)\b", question_text):
        return True
    return False


def classify_transfer_coordinate(row: dict[str, Any]) -> str:
    question = str(row.get("utterance") or "")
    answer = str(row.get("reference_answer") or "")
    surface = str((row.get("failure_surface") or {}).get("surface") or "")
    rationale = str((row.get("failure_surface") or {}).get("rationale") or "")
    question_text = _strip_options(question).casefold()
    text = " ".join([question, answer, surface, rationale]).casefold()

    if _has_any(text, ["title", "main idea", "mainly about", "best describes", "theme", "subject of the passage"]):
        return "title_theme_or_summary_answer"
    if _has_any(text, ["not true", "not correct", "incorrect", "false", "except", "contradict", "refut"]):
        return "false_or_exception_option_selection"
    if _has_any(text, ["formula", "calculate", "computed", "multiply", "times the", "no more than", "how many minutes", "how long"]):
        return "formula_or_rule_application"
    if _has_any(question_text, ["feel", "felt", "thought", "believ", "attitude", "emotion", "infer", "imply", "consequence"]) or re.search(
        r"^\s*why\b", question_text
    ):
        return "implicit_attitude_or_consequence"
    if _has_any(text, ["feel", "felt", "thought", "believ", "attitude", "emotion", "infer", "imply", "consequence"]):
        return "implicit_attitude_or_consequence"
    if re.search(r"^\s*(how far|how many|how much|how long|which came first|what came first)\b", question_text):
        return "comparative_or_temporal_resolution"
    if _has_any(text, ["compare", "comparison", "more than", "less than", "earlier", "later", "than men", "than women"]):
        return "comparative_or_temporal_resolution"
    if re.search(r"\b(before|after)\b", text) and _has_any(text, ["sequence", "order", "duration", "distance", "route", "timeline"]):
        return "comparative_or_temporal_resolution"
    if _has_any(text, ["audience", "parent", "writer", "author", "narrator", "relationship", "role", "college", "student", "teacher"]):
        return "background_role_or_audience_fact"
    if surface == "query_surface_gap":
        return "query_surface_resolution"
    if surface == "hybrid_join_gap":
        return "hybrid_join_resolution"
    if surface == "answer_surface_gap":
        return "answer_surface_mapping"
    if surface == "compile_surface_gap":
        return "direct_compile_surface_gap"
    return "unclassified_transfer_coordinate"


def _verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    verdict = str(judge.get("verdict") or "").casefold().strip()
    if verdict in {"exact", "partial", "miss", "not_judged"}:
        return verdict
    if row.get("ok") is True:
        return "exact"
    return "miss"


def _has_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def _strip_options(question: str) -> str:
    marker = " Options:"
    return question.split(marker, 1)[0] if marker in question else question


def _render_md(summary: dict[str, Any]) -> str:
    totals = summary.get("totals", {})
    lines = [
        "# MRC Transfer Coordinate Summary",
        "",
        f"QA root: `{summary.get('qa_root', '')}`",
        "",
        "## Totals",
        "",
        f"- Questions: `{totals.get('question_count', 0)}`",
        f"- Exact / partial / miss / not judged: `{totals.get('exact', 0)} / {totals.get('partial', 0)} / {totals.get('miss', 0)} / {totals.get('not_judged', 0)}`",
        f"- Exact rate: `{totals.get('exact_rate', 0.0)}`",
        "",
        "## Proposition Type Criteria",
        "",
    ]
    for key, value in (summary.get("proposition_type_criteria") or {}).items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Proposition Type Operational Rules", ""])
    for value in summary.get("proposition_type_operational_rules") or []:
        lines.append(f"- {value}")
    lines.extend(
        [
            "",
            "## Proposition Types",
            "",
        ]
    )
    for key, value in sorted((summary.get("proposition_type_counts") or {}).items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Transfer Coordinates",
            "",
        ]
    )
    for key, value in sorted((summary.get("transfer_coordinate_counts") or {}).items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Failure Surfaces", ""])
    for key, value in sorted((summary.get("failure_surface_counts") or {}).items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Non-Exact Rows", ""])
    for row in summary.get("non_exact_rows", []):
        lines.extend(
            [
                f"### {row.get('fixture', '')} {row.get('id', '')}",
                "",
                f"- Verdict: `{row.get('verdict', '')}`",
                f"- Surface: `{row.get('surface', '')}`",
                f"- Proposition type: `{row.get('proposition_type', '')}`",
                f"- Coordinate: `{row.get('coordinate', '')}`",
                f"- Question: {row.get('question', '')}",
                f"- Reference: {row.get('reference_answer', '')}",
                f"- Rationale: {row.get('rationale', '')}",
                "",
            ]
        )
    return "\n".join(lines)


def _abs(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


if __name__ == "__main__":
    raise SystemExit(main())
