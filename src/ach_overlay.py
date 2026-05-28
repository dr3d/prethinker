"""Deterministic Analysis of Competing Hypotheses overlay.

The overlay scores an ACH matrix that has already been populated with
evidence-vs-hypothesis judgments. It does not call an LLM, read source text, or
write KB state; it only enforces matrix completeness and ranks hypotheses by
least disconfirming evidence.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


VALID_ASSESSMENTS = {"consistent", "inconsistent", "neutral", "not_applicable"}
DEFAULT_DIAGNOSTIC_WEIGHTS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 5,
}
SUPPORT_DROP_SENSITIVITY_RATIO = 0.3
FAMILY_SUPPORT_DROP_SENSITIVITY_RATIO = 0.4
AXIS_FIT_PENALTIES = {
    "direct": 0,
    "partial": 3,
    "off_axis": 6,
}


def analyze_ach_overlay(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic ACH report for a populated matrix payload."""

    hypotheses = _indexed_items(payload.get("hypotheses", []), "hypotheses")
    evidence = _indexed_items(payload.get("evidence", []), "evidence")
    hypothesis_ids = list(hypotheses)
    evidence_ids = list(evidence)

    matrix: dict[str, dict[str, dict[str, Any]]] = {
        evidence_id: {} for evidence_id in evidence_ids
    }
    warnings: list[dict[str, Any]] = []
    seen_judgments: set[tuple[str, str]] = set()

    for judgment in payload.get("judgments", []):
        if not isinstance(judgment, dict):
            warnings.append({"kind": "invalid_judgment", "judgment": judgment})
            continue
        hypothesis_id = str(judgment.get("hypothesis_id", "")).strip()
        evidence_id = str(judgment.get("evidence_id", "")).strip()
        if hypothesis_id not in hypotheses or evidence_id not in evidence:
            warnings.append(
                {
                    "kind": "unknown_judgment_reference",
                    "hypothesis_id": hypothesis_id,
                    "evidence_id": evidence_id,
                }
            )
            continue
        key = (evidence_id, hypothesis_id)
        if key in seen_judgments:
            warnings.append(
                {
                    "kind": "duplicate_judgment",
                    "hypothesis_id": hypothesis_id,
                    "evidence_id": evidence_id,
                }
            )
            continue
        seen_judgments.add(key)
        assessment = _assessment(judgment.get("assessment"))
        matrix[evidence_id][hypothesis_id] = {
            "assessment": assessment,
            "weight": _judgment_weight(judgment, evidence[evidence_id]),
            "rationale": str(judgment.get("rationale", "")).strip(),
        }

    missing_judgments: list[dict[str, str]] = []
    for evidence_id in evidence_ids:
        for hypothesis_id in hypothesis_ids:
            if hypothesis_id in matrix[evidence_id]:
                continue
            missing_judgments.append({"evidence_id": evidence_id, "hypothesis_id": hypothesis_id})
            matrix[evidence_id][hypothesis_id] = {
                "assessment": "missing",
                "weight": _evidence_weight(evidence[evidence_id]),
                "rationale": "",
            }
    if missing_judgments:
        warnings.append({"kind": "missing_judgments", "items": missing_judgments})
    omission_effects = _omission_effects(
        payload.get("omission_effects", []),
        hypothesis_ids=set(hypothesis_ids),
        evidence_ids=set(evidence_ids),
        warnings=warnings,
    )

    hypothesis_scores = _score_hypotheses(
        hypotheses=hypotheses,
        evidence=evidence,
        matrix=matrix,
    )
    sensitivity = _sensitivity_analysis(
        hypotheses=hypotheses,
        evidence=evidence,
        matrix=matrix,
        baseline_scores=hypothesis_scores,
        omission_effects=omission_effects,
    )

    return {
        "schema_version": "ach_overlay_report_v1",
        "hypothesis_count": len(hypotheses),
        "evidence_count": len(evidence),
        "judgment_count": len(seen_judgments),
        "matrix_complete": not missing_judgments,
        "warnings": warnings,
        "hypotheses": list(hypotheses.values()),
        "evidence": list(evidence.values()),
        "matrix": matrix,
        "omission_effects": omission_effects,
        "hypothesis_scores": hypothesis_scores,
        "diagnostic_evidence": _diagnostic_evidence(evidence=evidence, matrix=matrix),
        "top_support_contributions": _top_support_contributions(
            evidence=evidence,
            matrix=matrix,
            hypothesis_scores=hypothesis_scores,
        ),
        "sensitivity": sensitivity,
        "surviving_hypotheses": [
            item
            for item in hypothesis_scores
            if item["rank"] == 1 and item["missing_judgment_count"] == 0
        ],
    }


def _indexed_items(items: Any, field_name: str) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list) or not items:
        raise ValueError(f"{field_name} must be a non-empty list")
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"{field_name} entries must be objects")
        item_id = str(item.get("id", "")).strip()
        if not item_id:
            raise ValueError(f"{field_name} entries require id")
        if item_id in indexed:
            raise ValueError(f"{field_name} contains duplicate id: {item_id}")
        indexed[item_id] = {**item, "id": item_id}
    return indexed


def _assessment(value: Any) -> str:
    text = str(value or "").strip().casefold()
    aliases = {
        "c": "consistent",
        "+": "consistent",
        "i": "inconsistent",
        "-": "inconsistent",
        "n/a": "not_applicable",
        "na": "not_applicable",
        "not applicable": "not_applicable",
        "not-applicable": "not_applicable",
    }
    text = aliases.get(text, text)
    if text not in VALID_ASSESSMENTS:
        raise ValueError(f"invalid ACH assessment: {value!r}")
    return text


def _judgment_weight(judgment: dict[str, Any], evidence_item: dict[str, Any]) -> int:
    if "weight" in judgment:
        return _positive_int(judgment["weight"], field_name="judgment.weight")
    return _evidence_weight(evidence_item)


def _evidence_weight(evidence_item: dict[str, Any]) -> int:
    if "weight" in evidence_item:
        return _positive_int(evidence_item["weight"], field_name="evidence.weight")
    diagnosticity = str(evidence_item.get("diagnosticity", "medium")).strip().casefold()
    return DEFAULT_DIAGNOSTIC_WEIGHTS.get(diagnosticity, DEFAULT_DIAGNOSTIC_WEIGHTS["medium"])


def _positive_int(value: Any, *, field_name: str) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive integer") from exc
    if out <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return out


def _omission_effects(
    items: Any,
    *,
    hypothesis_ids: set[str],
    evidence_ids: set[str],
    warnings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not items:
        return []
    if not isinstance(items, list):
        warnings.append({"kind": "invalid_omission_effects", "value": items})
        return []
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            warnings.append({"kind": "invalid_omission_effect", "effect": item})
            continue
        omitted_evidence_id = str(item.get("omitted_evidence_id", "")).strip()
        evidence_id = str(item.get("evidence_id", "")).strip()
        hypothesis_id = str(item.get("hypothesis_id", "")).strip()
        if omitted_evidence_id not in evidence_ids or evidence_id not in evidence_ids or hypothesis_id not in hypothesis_ids:
            warnings.append(
                {
                    "kind": "unknown_omission_effect_reference",
                    "omitted_evidence_id": omitted_evidence_id,
                    "evidence_id": evidence_id,
                    "hypothesis_id": hypothesis_id,
                }
            )
            continue
        if evidence_id == omitted_evidence_id:
            warnings.append(
                {
                    "kind": "self_omission_effect_ignored",
                    "omitted_evidence_id": omitted_evidence_id,
                    "evidence_id": evidence_id,
                    "hypothesis_id": hypothesis_id,
                }
            )
            continue
        out.append(
            {
                "omitted_evidence_id": omitted_evidence_id,
                "evidence_id": evidence_id,
                "hypothesis_id": hypothesis_id,
                "assessment": _assessment(item.get("assessment")),
                "weight": _positive_int(item.get("weight", 1), field_name="omission_effect.weight"),
                "rationale": str(item.get("rationale", "")).strip(),
            }
        )
    return out


def _score_hypotheses(
    *,
    hypotheses: dict[str, dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
    matrix: dict[str, dict[str, dict[str, Any]]],
    omitted_evidence_id: str | None = None,
    omitted_evidence_ids: set[str] | None = None,
    omission_effects: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    omitted_ids = set(omitted_evidence_ids or set())
    if omitted_evidence_id:
        omitted_ids.add(omitted_evidence_id)
    counters: dict[str, dict[str, int]] = {
        hypothesis_id: defaultdict(int) for hypothesis_id in hypotheses
    }
    for evidence_id in evidence:
        if evidence_id in omitted_ids:
            continue
        for hypothesis_id in hypotheses:
            judgment = _sensitivity_judgment(
                evidence_id=evidence_id,
                hypothesis_id=hypothesis_id,
                matrix=matrix,
                omitted_evidence_ids=omitted_ids,
                omission_effects=omission_effects or [],
            )
            assessment = judgment["assessment"]
            weight = int(judgment["weight"])
            if assessment == "inconsistent":
                counters[hypothesis_id]["inconsistency_weight"] += weight
                counters[hypothesis_id]["inconsistent_count"] += 1
            elif assessment == "consistent":
                counters[hypothesis_id]["consistency_weight"] += weight
                counters[hypothesis_id]["consistent_count"] += 1
            elif assessment == "neutral":
                counters[hypothesis_id]["neutral_count"] += 1
            elif assessment == "not_applicable":
                counters[hypothesis_id]["not_applicable_count"] += 1
            elif assessment == "missing":
                counters[hypothesis_id]["missing_judgment_count"] += 1

    scored = []
    for hypothesis_id, hypothesis in hypotheses.items():
        item = {
            "hypothesis_id": hypothesis_id,
            "label": str(hypothesis.get("label", hypothesis_id)),
            "axis_fit": _axis_fit(hypothesis),
            "axis_fit_penalty": _axis_fit_penalty(hypothesis),
            "inconsistency_weight": int(counters[hypothesis_id]["inconsistency_weight"]),
            "inconsistent_count": int(counters[hypothesis_id]["inconsistent_count"]),
            "consistency_weight": int(counters[hypothesis_id]["consistency_weight"]),
            "consistent_count": int(counters[hypothesis_id]["consistent_count"]),
            "neutral_count": int(counters[hypothesis_id]["neutral_count"]),
            "not_applicable_count": int(counters[hypothesis_id]["not_applicable_count"]),
            "missing_judgment_count": int(counters[hypothesis_id]["missing_judgment_count"]),
        }
        item["disconfirmation_score"] = item["inconsistency_weight"] + item["axis_fit_penalty"]
        scored.append(item)

    scored.sort(
        key=lambda item: (
            item["disconfirmation_score"],
            item["missing_judgment_count"],
            -item["consistency_weight"],
            item["hypothesis_id"],
        )
    )
    previous_key: tuple[int, int, int] | None = None
    rank = 0
    for index, item in enumerate(scored, start=1):
        key = (
            item["disconfirmation_score"],
            item["missing_judgment_count"],
            -item["consistency_weight"],
        )
        if key != previous_key:
            rank = index
            previous_key = key
        item["rank"] = rank
    return scored


def _axis_fit(hypothesis: dict[str, Any]) -> str:
    fit = str(hypothesis.get("axis_fit", "direct")).strip().casefold()
    if fit not in AXIS_FIT_PENALTIES:
        return "direct"
    return fit


def _axis_fit_penalty(hypothesis: dict[str, Any]) -> int:
    return AXIS_FIT_PENALTIES[_axis_fit(hypothesis)]


def _sensitivity_judgment(
    *,
    evidence_id: str,
    hypothesis_id: str,
    matrix: dict[str, dict[str, dict[str, Any]]],
    omitted_evidence_ids: set[str],
    omission_effects: list[dict[str, Any]],
) -> dict[str, Any]:
    if not omitted_evidence_ids:
        return matrix[evidence_id][hypothesis_id]
    for effect in omission_effects:
        if (
            effect["omitted_evidence_id"] in omitted_evidence_ids
            and effect["evidence_id"] == evidence_id
            and effect["hypothesis_id"] == hypothesis_id
        ):
            return {
                "assessment": effect["assessment"],
                "weight": effect["weight"],
                "rationale": effect.get("rationale", ""),
            }
    return matrix[evidence_id][hypothesis_id]


def _diagnostic_evidence(
    *,
    evidence: dict[str, dict[str, Any]],
    matrix: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows = []
    for evidence_id, evidence_item in evidence.items():
        assessments = [judgment["assessment"] for judgment in matrix[evidence_id].values()]
        inconsistency_count = assessments.count("inconsistent")
        distinct = {item for item in assessments if item not in {"missing", "not_applicable"}}
        weight = _evidence_weight(evidence_item)
        rows.append(
            {
                "evidence_id": evidence_id,
                "label": str(evidence_item.get("label", evidence_id)),
                "weight": weight,
                "inconsistent_hypothesis_count": inconsistency_count,
                "assessment_spread": sorted(distinct),
                "diagnostic_score": weight * (inconsistency_count + max(0, len(distinct) - 1)),
            }
        )
    rows.sort(key=lambda item: (-item["diagnostic_score"], item["evidence_id"]))
    return rows


def _top_support_contributions(
    *,
    evidence: dict[str, dict[str, Any]],
    matrix: dict[str, dict[str, dict[str, Any]]],
    hypothesis_scores: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    top_ids = [
        str(item.get("hypothesis_id", ""))
        for item in hypothesis_scores
        if item.get("rank") == 1
    ]
    if len(top_ids) != 1:
        return []
    top_id = top_ids[0]
    top_score = next((item for item in hypothesis_scores if item.get("hypothesis_id") == top_id), {})
    total_support = int(top_score.get("consistency_weight", 0) or 0)
    rows: list[dict[str, Any]] = []
    for evidence_id, evidence_item in evidence.items():
        judgment = matrix[evidence_id][top_id]
        assessment = str(judgment.get("assessment", ""))
        weight = int(judgment.get("weight", 0) or 0)
        support_weight = weight if assessment == "consistent" else 0
        rows.append(
            {
                "evidence_id": evidence_id,
                "label": str(evidence_item.get("label", evidence_id)),
                "role": str(evidence_item.get("role", "")),
                "top_hypothesis_id": top_id,
                "assessment": assessment,
                "weight": weight,
                "support_weight": support_weight,
                "support_share": round(support_weight / total_support, 4) if total_support > 0 else 0.0,
            }
        )
    rows.sort(key=lambda item: (-item["support_weight"], item["evidence_id"]))
    return rows


def _sensitivity_analysis(
    *,
    hypotheses: dict[str, dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
    matrix: dict[str, dict[str, dict[str, Any]]],
    baseline_scores: list[dict[str, Any]],
    omission_effects: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    baseline_top = {
        item["hypothesis_id"]
        for item in baseline_scores
        if item["rank"] == 1
    }
    sensitivity_rows = []
    for evidence_id in evidence:
        rescored = _score_hypotheses(
            hypotheses=hypotheses,
            evidence=evidence,
            matrix=matrix,
            omitted_evidence_id=evidence_id,
            omission_effects=omission_effects,
        )
        new_top = {item["hypothesis_id"] for item in rescored if item["rank"] == 1}
        applied_effects = [
            effect
            for effect in omission_effects
            if effect.get("omitted_evidence_id") == evidence_id
        ]
        if new_top != baseline_top:
            sensitivity_rows.append(
                {
                    "evidence_id": evidence_id,
                    "label": str(evidence[evidence_id].get("label", evidence_id)),
                    "baseline_top": sorted(baseline_top),
                    "top_without_evidence": sorted(new_top),
                    "reason": (
                        "top_hypothesis_set_changes_after_evidence_omission_effects"
                        if applied_effects
                        else "top_hypothesis_set_changes_if_evidence_removed"
                    ),
                    "applied_omission_effect_count": len(applied_effects),
                }
            )
            continue
        support_drop = _top_support_drop(
            baseline_scores=baseline_scores,
            rescored_scores=rescored,
            baseline_top=baseline_top,
        )
        if applied_effects and support_drop["drop_ratio"] >= SUPPORT_DROP_SENSITIVITY_RATIO:
            sensitivity_rows.append(
                {
                    "evidence_id": evidence_id,
                    "label": str(evidence[evidence_id].get("label", evidence_id)),
                    "baseline_top": sorted(baseline_top),
                    "top_without_evidence": sorted(new_top),
                    "reason": "top_hypothesis_support_drops_after_evidence_omission_effects",
                    "applied_omission_effect_count": len(applied_effects),
                    "support_drop": support_drop["drop"],
                    "support_drop_ratio": support_drop["drop_ratio"],
                }
            )
    sensitivity_rows.extend(
        _family_sensitivity_analysis(
            hypotheses=hypotheses,
            evidence=evidence,
            matrix=matrix,
            baseline_scores=baseline_scores,
            baseline_top=baseline_top,
            existing_rows=sensitivity_rows,
            omission_effects=omission_effects,
        )
    )
    return sensitivity_rows


def _family_sensitivity_analysis(
    *,
    hypotheses: dict[str, dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
    matrix: dict[str, dict[str, dict[str, Any]]],
    baseline_scores: list[dict[str, Any]],
    baseline_top: set[str],
    existing_rows: list[dict[str, Any]],
    omission_effects: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if len(baseline_top) != 1 or not omission_effects:
        return []
    nearest_margin = _nearest_disconfirmation_margin(
        baseline_scores=baseline_scores,
        baseline_top=baseline_top,
    )
    if nearest_margin > AXIS_FIT_PENALTIES["off_axis"]:
        return []
    top_id = next(iter(baseline_top))
    already_sensitive = {
        str(row.get("evidence_id", ""))
        for row in existing_rows
        if isinstance(row.get("evidence_id", ""), str)
    }
    candidate_ids = _family_sensitivity_candidate_ids(
        matrix=matrix,
        top_id=top_id,
        omission_effects=omission_effects,
    )
    out: list[dict[str, Any]] = []
    for group in _family_candidate_groups(candidate_ids, already_sensitive=already_sensitive):
        rescored = _score_hypotheses(
            hypotheses=hypotheses,
            evidence=evidence,
            matrix=matrix,
            omitted_evidence_ids=set(group),
            omission_effects=omission_effects,
        )
        new_top = {item["hypothesis_id"] for item in rescored if item["rank"] == 1}
        applied_effects = [
            effect
            for effect in omission_effects
            if effect.get("omitted_evidence_id") in group
            and effect.get("evidence_id") not in group
        ]
        top_support_effects = [
            effect
            for effect in applied_effects
            if effect.get("hypothesis_id") in baseline_top
            and matrix[str(effect.get("evidence_id"))][str(effect.get("hypothesis_id"))]["assessment"]
            == "consistent"
            and str(effect.get("assessment")) != "consistent"
        ]
        if not top_support_effects:
            continue
        support_drop = _top_support_drop(
            baseline_scores=baseline_scores,
            rescored_scores=rescored,
            baseline_top=baseline_top,
        )
        if new_top == baseline_top and support_drop["drop_ratio"] < FAMILY_SUPPORT_DROP_SENSITIVITY_RATIO:
            continue
        out.append(
            {
                "evidence_id": "+".join(group),
                "evidence_ids": list(group),
                "label": " + ".join(str(evidence[evidence_id].get("label", evidence_id)) for evidence_id in group),
                "baseline_top": sorted(baseline_top),
                "top_without_evidence": sorted(new_top),
                "reason": (
                    "top_hypothesis_set_changes_after_evidence_family_omission"
                    if new_top != baseline_top
                    else "top_hypothesis_support_drops_after_evidence_family_omission"
                ),
                "applied_omission_effect_count": len(applied_effects),
                "support_drop": support_drop["drop"],
                "support_drop_ratio": support_drop["drop_ratio"],
            }
        )
    return out


def _nearest_disconfirmation_margin(
    *,
    baseline_scores: list[dict[str, Any]],
    baseline_top: set[str],
) -> int:
    if len(baseline_top) != 1:
        return 999
    top_id = next(iter(baseline_top))
    top = next((item for item in baseline_scores if item.get("hypothesis_id") == top_id), None)
    if not top:
        return 999
    top_score = int(top.get("disconfirmation_score", 0) or 0)
    alternatives = [
        int(item.get("disconfirmation_score", 0) or 0) - top_score
        for item in baseline_scores
        if item.get("hypothesis_id") != top_id
    ]
    return min(alternatives) if alternatives else 999


def _family_sensitivity_candidate_ids(
    *,
    matrix: dict[str, dict[str, dict[str, Any]]],
    top_id: str,
    omission_effects: list[dict[str, Any]],
) -> list[str]:
    ids: list[str] = []
    for effect in omission_effects:
        for field in ("omitted_evidence_id", "evidence_id"):
            evidence_id = str(effect.get(field, "")).strip()
            if not evidence_id or evidence_id in ids:
                continue
            if evidence_id not in matrix:
                continue
            if matrix[evidence_id][top_id]["assessment"] != "consistent":
                continue
            ids.append(evidence_id)
    return ids


def _family_candidate_groups(
    candidate_ids: list[str],
    *,
    already_sensitive: set[str],
) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for left_index, left in enumerate(candidate_ids):
        for right in candidate_ids[left_index + 1 :]:
            if left in already_sensitive and right in already_sensitive:
                continue
            out.append(tuple(sorted((left, right))))
    return sorted(set(out))


def _top_support_drop(
    *,
    baseline_scores: list[dict[str, Any]],
    rescored_scores: list[dict[str, Any]],
    baseline_top: set[str],
) -> dict[str, Any]:
    if len(baseline_top) != 1:
        return {"drop": 0, "drop_ratio": 0.0}
    hypothesis_id = next(iter(baseline_top))
    baseline = next((item for item in baseline_scores if item["hypothesis_id"] == hypothesis_id), None)
    rescored = next((item for item in rescored_scores if item["hypothesis_id"] == hypothesis_id), None)
    if not baseline or not rescored:
        return {"drop": 0, "drop_ratio": 0.0}
    baseline_support = int(baseline.get("consistency_weight", 0) or 0)
    new_support = int(rescored.get("consistency_weight", 0) or 0)
    if baseline_support <= 0:
        return {"drop": 0, "drop_ratio": 0.0}
    drop = max(0, baseline_support - new_support)
    return {"drop": drop, "drop_ratio": round(drop / baseline_support, 4)}
