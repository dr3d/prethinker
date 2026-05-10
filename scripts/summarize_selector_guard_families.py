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
DEFAULT_LEDGER_JSON = REPO_ROOT / "tmp" / "selector_guard_ledger.json"
DEFAULT_LEDGER_MD = REPO_ROOT / "docs" / "SELECTOR_GUARD_LEDGER.md"

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
            "unrenewed-expiry",
            "permitted-hours",
            "permit-action list",
            "suspension-trigger",
            "override-rule",
            "approved-display",
            "valid-period",
            "appeal-hearing",
            "appeal-tolling",
            "revised-plan monitoring",
            "rescission-request eligibility",
            "failed-reinspection",
            "rule-effect",
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
            "adjusted-expiration",
            "request filing",
            "commit-readiness",
            "current-expiration",
            "priority",
            "decision-status",
            "board-concern",
            "current-constitution",
            "deaccession-yet",
            "resubmission",
            "not-formally-completed",
            "hold/readiness",
            "public-use extension",
            "student-count",
            "temporary-team",
            "no-touch hazard",
            "group-designation",
            "temporary-supervisor absence",
            "temporary-availability",
            "post-reassignment group-count",
            "unrestricted-active",
            "station-arrival-time",
            "temporary-role",
            "completion-report",
            "planning-application",
            "current-application",
            "proposal-version",
            "procedural-status",
            "prior-proposal disposition",
            "appeal-status",
            "response-content",
            "contract-rescission status",
            "timekeeping clock-out",
            "medication lot-number",
            "unresolved policy-deviation",
            "court-determination",
            "resolved-status",
            "order-series identifier",
            "erratum report-of-record",
            "date-event anchor",
            "governing-board vote-status",
            "review-completion",
            "raw-timestamp",
            "snapshot-state",
            "trip-date",
            "corrected-timestamp",
            "corrected-duration",
            "expected-order",
            "communications-officer",
            "sampler-offline interval",
            "chronological-event-row",
            "audit-exception",
            "pending-rather-than-approved",
            "clear-sample clock snapshot",
            "homeroom-reassignment",
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
            "intake-actor",
            "festival-director",
            "station-supervisor",
            "credential",
            "parent-sample identifier",
            "sample-ID surface",
            "panel-chair",
            "combined role-identity",
            "applicant identity",
            "school role/driver",
            "school-principal identity",
            "authority/source identity",
            "badge-id",
            "authoritative-homeroom",
            "student-identifier",
            "publication-authority",
            "arbitrator-unresolved-question",
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
            "provisional-control",
            "disputed-strip",
            "client-ledger pickup",
            "dated physical-location",
            "tree-amendment measurement",
            "barcode-supersession",
            "same-item",
            "near-duplicate bin-code",
            "custody-release",
            "location-plus-publication-pause",
            "MOU-scope expansion",
            "photograph-album interval",
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
            "split-lot",
            "quarantine-scope",
            "placed-under-quarantine",
            "initial-affected greenhouse",
            "reading-access",
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
            "source-belief",
            "conservator-date",
            "display-authority",
            "discrepancy-explanation",
            "surveyor-certification",
            "maintenance-evidence",
            "fictional-order",
            "boundary-discrepancy",
            "yellow-to-blue",
            "day-3 found-object",
            "source-specific witness",
            "failed-vendor rationale",
            "vendor-deficiency",
            "display-outcome",
            "second-violation duration",
            "alternative-inscription",
            "missing-evidence",
            "source-claim",
            "permission-request",
            "survey-commission",
            "correction-authorship",
            "source-provenance",
            "message-source",
            "position-source",
            "reply-memo theory",
            "false-conflict consistency",
            "memo-resolution",
            "memo-establish",
            "negative-reliability",
            "phone-ping granularity",
            "evidence-source count",
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
            "plant-count",
            "lot/count",
            "lot-3b lab-result",
            "claim-value",
            "physical inventory count",
            "candidate-vessel",
            "corrected-rank-order",
            "attendance-count",
            "density-calculation",
            "build-out timeline",
            "dimensional-standards",
            "zoning-designation",
            "deadline-filing",
            "board-review-period",
            "scoped roster-count",
            "deed item-count",
            "packet-time measurement",
            "active-lot count",
            "focused semantic surface",
            "application-number identifier",
            "document-identification",
            "current-versus-withdrawn claim",
            "operative-permit",
            "tree-list/count",
            "remedy-imposition",
            "hearing-held",
            "exhibit-identification",
            "roster-of-record",
            "withdrawn-draft governance",
            "student-location supervision",
            "adult-roster count",
            "headcount elapsed-time",
            "parent-letter determination",
            "newsletter-versus-roster",
            "headcount-scan reconciliation",
            "witness-scan reconciliation",
            "threshold question",
            "application-count",
            "application-disposition",
            "roster-entry count",
            "correction-notice replacement",
            "date-alone rule",
            "projection-supersession",
            "packet-close open-item",
            "active-held count",
            "distinct-student count-change",
            "cap-application",
            "counterfactual no-cap",
            "distinct-student registrar count",
            "roster-table count support",
            "adult-total roster",
            "qualifying-chaperone count",
            "ratio-compliance",
            "compliance_status",
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
    reason_counts = Counter(record["reason"] for record in records)
    duplicate_reasons: list[dict[str, Any]] = []
    for reason, count in sorted(reason_counts.items(), key=lambda item: (-item[1], item[0])):
        if count <= 1:
            continue
        duplicate_reasons.append(
            {
                "reason": reason,
                "count": count,
                "sites": [
                    {
                        "function": record["function"],
                        "line": record["line"],
                        "family": record["family"],
                    }
                    for record in records
                    if record["reason"] == reason
                ],
            }
        )
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
    health = build_health_summary(
        guard_reason_count=len(records),
        unique_guard_reason_count=len({record["reason"] for record in records}),
        family_records=family_records,
        unclassified_count=counts.get("unclassified", 0),
    )
    return {
        "schema_version": "selector_guard_family_rollup_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": str(source_path),
        "guard_reason_count": len(records),
        "unique_guard_reason_count": len({record["reason"] for record in records}),
        "family_count": len([family for family in counts if family != "unclassified"]),
        "unclassified_count": counts.get("unclassified", 0),
        "duplicate_reason_count": sum(item["count"] - 1 for item in duplicate_reasons),
        "duplicate_reasons": duplicate_reasons,
        "health": health,
        "families": family_records,
    }


def build_guard_ledger(report: dict[str, Any]) -> dict[str, Any]:
    """Build an explicit audit ledger for every guard reason.

    This ledger intentionally does not pretend to know transfer status from the
    source file alone. It gives each guard a visible audit slot so future replay
    evidence can promote, merge, or retire it.
    """
    reason_counts = Counter()
    for family in report.get("families", []):
        for guard in family.get("guards", []):
            reason_counts[str(guard.get("reason", ""))] += 1

    entries: list[dict[str, Any]] = []
    for family in report.get("families", []):
        family_id = str(family.get("family", ""))
        for guard in family.get("guards", []):
            reason = str(guard.get("reason", ""))
            duplicate_count = reason_counts[reason]
            entries.append(
                {
                    "reason": reason,
                    "family": family_id,
                    "source": _repo_rel(Path(report["source"])),
                    "line": int(guard.get("line", 0) or 0),
                    "function": str(guard.get("function", "")),
                    "duplicate_count": duplicate_count,
                    "audit_status": _initial_guard_audit_status(reason=reason, duplicate_count=duplicate_count),
                    "birth_fixture": "unknown",
                    "birth_row": "unknown",
                    "score_delta": "unknown",
                    "transfer_evidence": "not yet audited",
                    "regression_evidence": "not yet audited",
                    "retirement_bucket": _retirement_bucket(reason),
                    "retirement_priority": _retirement_priority(reason),
                    "retirement_condition": _suggest_retirement_condition(reason),
                }
            )

    status_counts = Counter(entry["audit_status"] for entry in entries)
    family_counts = Counter(entry["family"] for entry in entries)
    retirement_bucket_counts = Counter(entry["retirement_bucket"] for entry in entries)
    retirement_priority_counts = Counter(entry["retirement_priority"] for entry in entries)
    return {
        "schema_version": "selector_guard_ledger_v1",
        "generated_at": report.get("generated_at", ""),
        "source": report.get("source", ""),
        "summary": {
            "entry_count": len(entries),
            "unique_reason_count": report.get("unique_guard_reason_count", 0),
            "family_count": report.get("family_count", 0),
            "unclassified_count": report.get("unclassified_count", 0),
            "status_counts": dict(sorted(status_counts.items())),
            "family_counts": dict(sorted(family_counts.items())),
            "retirement_bucket_counts": dict(sorted(retirement_bucket_counts.items())),
            "retirement_priority_counts": dict(sorted(retirement_priority_counts.items())),
        },
        "audit_policy": {
            "transfer_guard": "Promote only after replay evidence shows the guard helps more than one fixture or domain without known regression.",
            "candidate_guard": "Default status for a measured guard whose transfer evidence has not yet been audited.",
            "merge_candidate": "Duplicate or near-duplicate reason; inspect branch conditions and replay birth rows before merging.",
            "scar_guard": "A local accident or guard made unnecessary by stronger compile, helper, pinboard, or query surfaces; retire when replay passes without it.",
        },
        "entries": sorted(entries, key=lambda item: (item["family"], item["reason"], item["line"])),
    }


def _initial_guard_audit_status(*, reason: str, duplicate_count: int) -> str:
    if duplicate_count > 1:
        return "merge_candidate"
    folded = reason.casefold()
    if any(marker in folded for marker in ("identifier", "document-identifier", "source-provenance")):
        return "candidate_guard:pinboard_pressure"
    if any(marker in folded for marker in ("count", "arithmetic", "threshold", "average", "density")):
        return "candidate_guard:helper_pressure"
    return "candidate_guard"


def _retirement_bucket(reason: str) -> str:
    folded = reason.casefold()
    if any(marker in folded for marker in ("identifier", "document-identifier", "source-provenance", "printed", "source-id")):
        return "pinboard_or_source_addressability"
    if any(
        marker in folded
        for marker in (
            "count",
            "arithmetic",
            "average",
            "density",
            "threshold",
            "interval",
            "deadline",
            "duration",
            "elapsed",
            "clock",
            "timestamp",
        )
    ):
        return "helper_or_constraint_substrate"
    if any(marker in folded for marker in ("row-volume", "broad", "expanded source-row", "volume")):
        return "selector_scoring_or_surface_penalty"
    if any(
        marker in folded
        for marker in (
            "status",
            "completed",
            "current",
            "resolved",
            "pending",
            "role",
            "authority",
            "custody",
            "ownership",
            "possession",
        )
    ):
        return "compile_surface"
    return "manual_audit"


def _retirement_priority(reason: str) -> str:
    bucket = _retirement_bucket(reason)
    folded = reason.casefold()
    if bucket in {"pinboard_or_source_addressability", "helper_or_constraint_substrate"}:
        return "high"
    if "row-volume" in folded or "broad" in folded or "volume" in folded:
        return "medium"
    if bucket == "compile_surface":
        return "medium"
    return "low"


def _suggest_retirement_condition(reason: str) -> str:
    folded = reason.casefold()
    if any(marker in folded for marker in ("identifier", "document-identifier", "source-provenance", "printed")):
        return "Retire if deterministic identifier/source pinboards make the selector choose correctly without this guard."
    if any(marker in folded for marker in ("count", "arithmetic", "average", "density", "threshold")):
        return "Retire if helper/query substrate returns the required quantity directly and selector replay passes without this guard."
    if "archival row-volume" in folded or "row-volume" in folded:
        return "Retire if structural scoring penalizes broad row-volume well enough to pass the birth rows without this guard."
    if any(marker in folded for marker in ("status", "completed", "current", "resolved", "pending")):
        return "Retire if compile surfaces admit explicit status predicates that make the selector choose correctly without this guard."
    return "Specify during audit: name the upstream compile, helper, pinboard, or scoring change that would make this guard unnecessary."


def build_health_summary(
    *,
    guard_reason_count: int,
    unique_guard_reason_count: int,
    family_records: list[dict[str, Any]],
    unclassified_count: int,
) -> dict[str, Any]:
    """Summarize whether guard growth is still semantic compression, not sprawl."""
    classified_families = [family for family in family_records if family["family"] != "unclassified"]
    family_count = len(classified_families)
    largest_family = max(classified_families, key=lambda item: int(item["count"]), default={})
    largest_count = int(largest_family.get("count", 0) or 0)
    largest_share = (largest_count / guard_reason_count) if guard_reason_count else 0.0
    unique_ratio = (unique_guard_reason_count / guard_reason_count) if guard_reason_count else 0.0
    guards_per_family = (guard_reason_count / family_count) if family_count else 0.0
    unique_reasons_per_family = (unique_guard_reason_count / family_count) if family_count else 0.0
    status = "pass"
    warnings: list[str] = []
    if unclassified_count:
        status = "fail"
        warnings.append("unclassified guards must be renamed, retired, or assigned to a family")
    if family_count > 8:
        status = "warn" if status == "pass" else status
        warnings.append("family count is above the current pegboard budget of 8")
    if largest_share >= 0.40:
        status = "warn" if status == "pass" else status
        warnings.append("one guard family is absorbing too many instances; consider splitting by semantic reason")
    if unique_reasons_per_family > 25:
        status = "warn" if status == "pass" else status
        warnings.append(
            "enumeration pressure is high; parameterizing families may hide guard sprawl unless instances retire or transfer"
        )
    return {
        "status": status,
        "family_budget": 8,
        "family_count": family_count,
        "guard_return_sites": guard_reason_count,
        "unique_guard_reasons": unique_guard_reason_count,
        "unique_reason_ratio": round(unique_ratio, 3),
        "guards_per_family": round(guards_per_family, 2),
        "unique_reasons_per_family": round(unique_reasons_per_family, 2),
        "unclassified_count": unclassified_count,
        "largest_family": str(largest_family.get("family", "")),
        "largest_family_count": largest_count,
        "largest_family_share": round(largest_share, 3),
        "warnings": warnings,
        "interpretation": (
            "Raw guard instances may grow during fixture farming, but semantic compression "
            "depends on low family count, zero unclassified reasons, no single family "
            "becoming a dumping ground, and no parameterized family hiding a large private "
            "enumeration table."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    health = report.get("health") if isinstance(report.get("health"), dict) else {}
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
        "Companion audit ledger: [SELECTOR_GUARD_LEDGER.md](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_LEDGER.md).",
        "",
        "## Summary",
        "",
        f"- guard return sites: `{report['guard_reason_count']}`",
        f"- unique guard reasons: `{report['unique_guard_reason_count']}`",
        f"- classified families: `{report['family_count']}`",
        f"- unclassified reasons: `{report['unclassified_count']}`",
        f"- duplicate guard reasons: `{report.get('duplicate_reason_count', 0)}`",
        "",
        "## Growth Health",
        "",
        f"- status: `{health.get('status', 'unknown')}`",
        f"- family budget: `{health.get('family_count', report['family_count'])} / {health.get('family_budget', 8)}`",
        f"- largest family: `{health.get('largest_family', '')}` with `{health.get('largest_family_count', 0)}` guards "
        f"(`{health.get('largest_family_share', 0)}` share)",
        f"- unique reason ratio: `{health.get('unique_reason_ratio', 0)}`",
        f"- guards per family: `{health.get('guards_per_family', 0)}`",
        f"- unique reasons per family: `{health.get('unique_reasons_per_family', 0)}`",
        "",
        str(
            health.get(
                "interpretation",
                "Guard growth is healthy only when it compresses into a small number of families.",
            )
        ),
        "",
    ]
    warnings = health.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.extend(["Warnings:", ""])
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")
    lines.extend(
        [
        "## Family Counts",
        "",
        "| Family | Count | Purpose |",
        "| --- | ---: | --- |",
        ]
    )
    for family in report["families"]:
        lines.append(f"| `{family['family']}` | {family['count']} | {family['purpose']} |")
    duplicate_reasons = report.get("duplicate_reasons", [])
    if isinstance(duplicate_reasons, list) and duplicate_reasons:
        lines.extend(["", "## Exact Duplicate Reasons", ""])
        lines.append("These are first-pass merge candidates. A duplicate reason is not automatically safe to delete; confirm the underlying branch conditions and replay the rows that created each site.")
        lines.append("")
        for item in duplicate_reasons:
            if not isinstance(item, dict):
                continue
            site_text = ", ".join(
                f"{_repo_rel(Path(report['source']))}:{site.get('line')}"
                for site in item.get("sites", [])
                if isinstance(site, dict)
            )
            lines.append(f"- `{item.get('reason', '')}` (`{item.get('count', 0)}` sites: {site_text})")
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
            "- Do not hide guard growth inside parameter bags. A family generator must report its enumerated surfaces, transfer evidence, and retirement candidates.",
            "- Prefer retiring guards when compile/query/helper improvements make the originating failure pass without selector intervention.",
            "- If a guard remains unclassified, either retire it, rename it, or add a family with a purpose.",
            "",
        ]
    )
    return "\n".join(lines)


def render_guard_ledger_markdown(ledger: dict[str, Any]) -> str:
    summary = ledger.get("summary") if isinstance(ledger.get("summary"), dict) else {}
    status_counts = summary.get("status_counts") if isinstance(summary.get("status_counts"), dict) else {}
    family_counts = summary.get("family_counts") if isinstance(summary.get("family_counts"), dict) else {}
    retirement_bucket_counts = (
        summary.get("retirement_bucket_counts")
        if isinstance(summary.get("retirement_bucket_counts"), dict)
        else {}
    )
    retirement_priority_counts = (
        summary.get("retirement_priority_counts")
        if isinstance(summary.get("retirement_priority_counts"), dict)
        else {}
    )
    entries = [entry for entry in ledger.get("entries", []) if isinstance(entry, dict)]
    lines = [
        "# Selector Guard Ledger",
        "",
        "This is the audit ledger for selector guards. It deliberately keeps guard",
        "instances visible instead of hiding them inside parameterized family",
        "generators. A visible guard can be promoted, merged, or retired.",
        "",
        "Generated from `scripts/select_qa_mode_without_oracle.py`.",
        "",
        "## Summary",
        "",
        f"- entries: `{summary.get('entry_count', 0)}`",
        f"- unique guard reasons: `{summary.get('unique_reason_count', 0)}`",
        f"- families: `{summary.get('family_count', 0)}`",
        f"- unclassified: `{summary.get('unclassified_count', 0)}`",
        "",
        "## Audit Status Counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in status_counts.items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Family Pressure", "", "| Family | Count |", "| --- | ---: |"])
    for family, count in family_counts.items():
        lines.append(f"| `{family}` | {count} |")
    lines.extend(["", "## Retirement Pressure", "", "| Bucket | Count |", "| --- | ---: |"])
    for bucket, count in retirement_bucket_counts.items():
        lines.append(f"| `{bucket}` | {count} |")
    lines.extend(["", "| Priority | Count |", "| --- | ---: |"])
    for priority, count in retirement_priority_counts.items():
        lines.append(f"| `{priority}` | {count} |")

    high_priority = [entry for entry in entries if entry.get("retirement_priority") == "high"]
    if high_priority:
        lines.extend(
            [
                "",
                "## First Retirement Slices",
                "",
                "These are not automatic deletions. They are the first replay slices to",
                "try after helper, constraint, or pinboard work lands. A guard retires",
                "only when replay passes without it.",
                "",
                "| Bucket | Family | Reason | Site |",
                "| --- | --- | --- | --- |",
            ]
        )
        for entry in high_priority[:24]:
            reason = _md_cell(str(entry.get("reason", "")))
            site = f"{entry.get('source', '')}:{entry.get('line', '')}"
            lines.append(
                f"| `{entry.get('retirement_bucket', '')}` | `{entry.get('family', '')}` | {reason} | `{site}` |"
            )
    lines.extend(
        [
            "",
            "## Audit Policy",
            "",
            "- `transfer_guard`: replay evidence shows this guard helps more than one fixture or domain without known regression.",
            "- `candidate_guard`: measured guard, transfer evidence pending.",
            "- `merge_candidate`: duplicate or near-duplicate reason; inspect branch conditions and replay before merging.",
            "- `scar_guard`: local accident or guard made obsolete by stronger compile, helper, pinboard, or query surfaces.",
            "",
            "## Ledger Entries",
            "",
            "| Status | Priority | Bucket | Family | Reason | Site | Retirement Condition |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for entry in entries:
        reason = _md_cell(str(entry.get("reason", "")))
        retirement = _md_cell(str(entry.get("retirement_condition", "")))
        site = f"{entry.get('source', '')}:{entry.get('line', '')}"
        lines.append(
            f"| `{entry.get('audit_status', '')}` | `{entry.get('retirement_priority', '')}` | "
            f"`{entry.get('retirement_bucket', '')}` | `{entry.get('family', '')}` | {reason} | "
            f"`{site}` | {retirement} |"
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "During fixture farming, each new guard should get birth fixture, birth row,",
            "score delta, transfer evidence, regression evidence, and a retirement",
            "condition. The healthy long-term shape is not an invisible seven-function",
            "selector engine. It is a visible guard surface that peaks, merges, and",
            "shrinks as upstream lenses, helpers, pinboards, and query surfaces improve.",
            "",
        ]
    )
    return "\n".join(lines)


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


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
    parser.add_argument("--ledger-json", type=Path, default=DEFAULT_LEDGER_JSON)
    parser.add_argument("--ledger-md", type=Path, default=DEFAULT_LEDGER_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source if args.source.is_absolute() else (REPO_ROOT / args.source).resolve()
    report = build_report(source)
    ledger = build_guard_ledger(report)
    out_json = args.out_json if args.out_json.is_absolute() else (REPO_ROOT / args.out_json).resolve()
    out_md = args.out_md if args.out_md.is_absolute() else (REPO_ROOT / args.out_md).resolve()
    ledger_json = args.ledger_json if args.ledger_json.is_absolute() else (REPO_ROOT / args.ledger_json).resolve()
    ledger_md = args.ledger_md if args.ledger_md.is_absolute() else (REPO_ROOT / args.ledger_md).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    ledger_json.parent.mkdir(parents=True, exist_ok=True)
    ledger_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    ledger_json.write_text(json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    ledger_md.write_text(render_guard_ledger_markdown(ledger), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(f"Wrote {ledger_json}")
    print(f"Wrote {ledger_md}")
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
