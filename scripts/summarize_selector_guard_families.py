from __future__ import annotations

import argparse
import ast
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SELECTOR = REPO_ROOT / "scripts" / "select_qa_mode_without_oracle.py"
DEFAULT_JSON = REPO_ROOT / "tmp" / "selector_guard_families.json"
DEFAULT_MD = REPO_ROOT / "docs" / "SELECTOR_GUARD_FAMILY_ROLLUP.md"

GUARD_FUNCTIONS = {
    "structural_baseline_answer_surface_guard_reason",
    "structural_specialized_answer_surface_override",
}


@dataclass(frozen=True)
class GuardFamily:
    family_id: str
    purpose: str
    keywords: tuple[str, ...]


FAMILIES: tuple[GuardFamily, ...] = (
    GuardFamily(
        family_id="rule_activation_surface",
        purpose=(
            "Route promoted rule, eligibility, recall, recusal, window, rejection, and reserve "
            "questions to the evidence surface that contains both the governing condition and "
            "the instance facts needed to apply it."
        ),
        keywords=(
            "deferment",
            "deferred",
            "component-problem",
            "rule-condition",
            "recusal",
            "recuse",
            "window-merit",
            "amendment-recall",
            "recall-authority",
            "rejection-cause",
            "reserve-status",
            "eligibility surface",
        ),
    ),
    GuardFamily(
        family_id="operational_record_status",
        purpose=(
            "Protect current status, request timing, commit readiness, decision, priority, "
            "concern, constitution, and resubmission rows from nearby but less answer-bearing "
            "record/event surfaces."
        ),
        keywords=(
            "operational status",
            "status/rule support",
            "application/status",
            "request filing",
            "commit-readiness",
            "priority",
            "decision-status",
            "board-concern",
            "current-constitution",
            "deaccession-yet",
            "resubmission",
            "not-formally-completed",
            "hold/readiness",
        ),
    ),
    GuardFamily(
        family_id="entity_role_authority",
        purpose=(
            "Separate identity, role definition, acting authority, collector, contract authority, "
            "and guardianship rows from broad action or title-only evidence."
        ),
        keywords=(
            "identity",
            "collector",
            "official",
            "role",
            "contract-validity",
            "acting-authority",
            "authority-source",
            "guardianship",
            "name/role",
        ),
    ),
    GuardFamily(
        family_id="state_custody_ownership",
        purpose=(
            "Separate current object state, custody transfer, possession, ownership, legal title, "
            "and award/result surfaces from generic event, property, or person rows."
        ),
        keywords=(
            "object-component",
            "current-state/component",
            "custody",
            "why-have",
            "award",
            "reinstatement",
            "carry",
            "possession",
            "ownership",
            "legal-title",
            "title",
        ),
    ),
    GuardFamily(
        family_id="regulatory_access_scope",
        purpose=(
            "Route all/any scope, termination denial, affected-lot exclusion, and "
            "reclassification-deadline questions to access surfaces that carry the right set, "
            "threshold, target, or temporal boundary."
        ),
        keywords=(
            "universal-scope",
            "termination-denial",
            "lot-affected",
            "target-lot",
            "reclassification deadline",
            "classification-bound deadline",
        ),
    ),
    GuardFamily(
        family_id="rationale_evidence_contrast",
        purpose=(
            "Route why/cause, witness/report, source-note, split rationale, viability contrast, "
            "and pending test questions to explicit rationale or evidentiary support instead of "
            "adjacent status rows."
        ),
        keywords=(
            "rationale",
            "cause question",
            "evidentiary-status",
            "witness/report",
            "source-note",
            "split rationale",
            "viability-concern",
            "not-yet-tested",
            "test-status",
        ),
    ),
    GuardFamily(
        family_id="threshold_policy_arithmetic",
        purpose=(
            "Prefer direct threshold, quantity, storage, policy-action, and arithmetic inputs "
            "when a broader policy or derived-status surface is tempting but incomplete."
        ),
        keywords=(
            "quantity-threshold",
            "threshold/storage",
            "threshold/action policy",
            "arithmetic inputs",
            "completion-window",
        ),
    ),
)


def extract_guard_reasons(source_path: Path) -> list[dict[str, str]]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    reasons: list[dict[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in GUARD_FUNCTIONS:
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Return):
                continue
            for constant in ast.walk(child):
                if not isinstance(constant, ast.Constant) or not isinstance(constant.value, str):
                    continue
                reason = constant.value.strip()
                if _looks_like_guard_reason(reason):
                    reasons.append(
                        {
                            "function": node.name,
                            "line": str(constant.lineno),
                            "reason": reason,
                        }
                    )
    return sorted(reasons, key=lambda item: (item["function"], int(item["line"]), item["reason"]))


def classify_reason(reason: str) -> str:
    folded = reason.casefold()
    for family in FAMILIES:
        if any(keyword.casefold() in folded for keyword in family.keywords):
            return family.family_id
    return "unclassified"


def build_report(source_path: Path) -> dict[str, Any]:
    reasons = extract_guard_reasons(source_path)
    records: list[dict[str, str]] = []
    for reason in reasons:
        family_id = classify_reason(reason["reason"])
        records.append({**reason, "family": family_id})
    counts = Counter(record["family"] for record in records)
    family_records = []
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in records:
        by_family[record["family"]].append(record)
    purpose_by_family = {family.family_id: family.purpose for family in FAMILIES}
    purpose_by_family["unclassified"] = "Guard reasons that need a family before promotion."
    for family_id in sorted(by_family):
        family_records.append(
            {
                "family": family_id,
                "count": counts[family_id],
                "purpose": purpose_by_family.get(family_id, ""),
                "guards": by_family[family_id],
            }
        )
    return {
        "schema_version": "selector_guard_family_rollup_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": str(source_path),
        "guard_reason_count": len(records),
        "unique_guard_reason_count": len({record["reason"] for record in records}),
        "family_count": len([family for family in counts if family != "unclassified"]),
        "unclassified_count": counts.get("unclassified", 0),
        "families": family_records,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Selector Guard Family Rollup",
        "",
        "This report keeps the selector guard surface from turning into a pile of",
        "fixture-shaped knobs. Individual guards are allowed while they are being",
        "measured, but they should collapse into a small number of semantic families",
        "before they become daily-driver harness doctrine.",
        "",
        "Generated from `scripts/select_qa_mode_without_oracle.py`.",
        "",
        "## Summary",
        "",
        f"- guard return sites: `{report['guard_reason_count']}`",
        f"- unique guard reasons: `{report['unique_guard_reason_count']}`",
        f"- classified families: `{report['family_count']}`",
        f"- unclassified reasons: `{report['unclassified_count']}`",
        "",
        "## Family Counts",
        "",
        "| Family | Count | Purpose |",
        "| --- | ---: | --- |",
    ]
    for family in report["families"]:
        lines.append(f"| `{family['family']}` | {family['count']} | {family['purpose']} |")
    lines.extend(["", "## Guard Reasons", ""])
    for family in report["families"]:
        lines.extend([f"### `{family['family']}`", ""])
        for guard in family["guards"]:
            rel_source = _repo_rel(Path(report["source"]))
            lines.append(f"- `{guard['reason']}` ({rel_source}:{guard['line']})")
        lines.append("")
    lines.extend(
        [
            "## Promotion Discipline",
            "",
            "- Add a guard freely when it protects a measured row-level failure.",
            "- Do not call a guard a new lens until it transfers or clearly belongs to a family.",
            "- If a family grows past a readable size, split by semantic reason, not by fixture.",
            "- If a guard remains unclassified, either retire it, rename it, or add a family with a purpose.",
            "",
        ]
    )
    return "\n".join(lines)


def _looks_like_guard_reason(value: str) -> bool:
    if len(value) < 20:
        return False
    folded = value.casefold()
    markers = ("question", "surface", "evidence", "support", "candidate")
    return any(marker in folded for marker in markers)


def _repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SELECTOR)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source if args.source.is_absolute() else (REPO_ROOT / args.source).resolve()
    report = build_report(source)
    out_json = args.out_json if args.out_json.is_absolute() else (REPO_ROOT / args.out_json).resolve()
    out_md = args.out_md if args.out_md.is_absolute() else (REPO_ROOT / args.out_md).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(
        json.dumps(
            {
                k: report[k]
                for k in ("guard_reason_count", "unique_guard_reason_count", "family_count", "unclassified_count")
            }
        )
    )
    return 0 if report["unclassified_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
