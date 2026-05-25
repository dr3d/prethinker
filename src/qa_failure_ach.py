"""ACH-style diagnostic triage for QA non-exact rows.

This module does not call an LLM, mutate QA verdicts, or write KB state. It
builds a populated ACH matrix over fixed failure-location hypotheses from
already archived QA row telemetry, then uses the deterministic ACH scorer to
rank the most likely patch location.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import json
import re
from typing import Any

from src.ach_overlay import analyze_ach_overlay


HYPOTHESES = [
    {
        "id": "h_compile_preservation",
        "label": "Direct compile surface failed to preserve the reusable evidence coordinate.",
    },
    {
        "id": "h_query_route",
        "label": "Evidence may exist, but the query or evidence-plan route failed.",
    },
    {
        "id": "h_join_computation",
        "label": "Evidence fragments exist, but ordering, arithmetic, grouping, or joining failed.",
    },
    {
        "id": "h_answer_assessment",
        "label": "The remaining issue is answer rendering, judge strictness, or oracle ambiguity.",
    },
]


def analyze_qa_failure_batch(
    summary_payload: dict[str, Any],
    *,
    artifact_root: Path | None = None,
    include_failure_label: bool = False,
) -> dict[str, Any]:
    """Return ACH-style diagnostic triage for all non-exact rows in a QA batch."""

    rows = []
    for fixture, run_payload in _iter_runs(summary_payload, artifact_root=artifact_root):
        for row in run_payload.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            verdict = _verdict(row)
            if verdict == "exact":
                continue
            rows.append(
                analyze_qa_failure_row(
                    row,
                    fixture=fixture,
                    include_failure_label=include_failure_label,
                )
            )

    top_counts = Counter()
    surface_counts = Counter()
    envelope_counts = Counter()
    family_counts: dict[str, Counter[str]] = defaultdict(Counter)
    agreement_counts = Counter()
    for item in rows:
        top = item.get("top_hypotheses", [])
        top_key = ",".join(top) if top else "none"
        top_counts[top_key] += 1
        surface = str(item.get("failure_surface") or "unknown")
        surface_counts[surface] += 1
        envelope_counts[str(item.get("response_status") or "unknown")] += 1
        family_counts[_fixture_family(str(item.get("fixture") or ""))][top_key] += 1
        agreement_counts[str(item.get("classifier_agreement") or "unknown")] += 1

    return {
        "schema_version": "qa_failure_ach_probe_v1",
        "policy": [
            "Diagnostic only: does not call an LLM, mutate QA verdicts, write KB facts, or change scores.",
            "Ranks fixed patch-location hypotheses with deterministic ACH over archived row telemetry.",
            "The existing failure-surface classifier is compared to the ACH top hypothesis, not treated as truth unless requested.",
        ],
        "summary": {
            "row_count": len(rows),
            "top_hypothesis_counts": dict(sorted(top_counts.items())),
            "failure_surface_counts": dict(sorted(surface_counts.items())),
            "response_status_counts": dict(sorted(envelope_counts.items())),
            "classifier_agreement_counts": dict(sorted(agreement_counts.items())),
            "family_top_hypothesis_counts": {
                family: dict(sorted(counter.items()))
                for family, counter in sorted(family_counts.items())
            },
        },
        "rows": rows,
    }


def analyze_qa_failure_row(
    row: dict[str, Any],
    *,
    fixture: str,
    include_failure_label: bool = False,
) -> dict[str, Any]:
    """Return a diagnostic ACH report for one QA row."""

    features = _row_features(row)
    payload = _build_payload(features, include_failure_label=include_failure_label)
    ach = analyze_ach_overlay(payload)
    top = [
        item["hypothesis_id"]
        for item in ach.get("hypothesis_scores", [])
        if isinstance(item, dict) and item.get("rank") == 1
    ]
    classifier_hypothesis = _classifier_hypothesis(features["failure_surface"])
    agreement = "not_available"
    if classifier_hypothesis:
        agreement = "agree" if classifier_hypothesis in top else "disagree"
    return {
        "fixture": fixture,
        "id": str(row.get("id") or ""),
        "verdict": features["verdict"],
        "failure_surface": features["failure_surface"],
        "classifier_hypothesis": classifier_hypothesis,
        "classifier_agreement": agreement,
        "response_status": features["response_status"],
        "question": str(row.get("utterance") or ""),
        "reference_answer": str(row.get("reference_answer") or ""),
        "top_hypotheses": top,
        "feature_summary": {
            key: features[key]
            for key in [
                "query_count",
                "nonempty_query_count",
                "direct_nonempty_count",
                "source_record_nonempty_count",
                "support_surface_count",
                "query_error_count",
                "question_shapes",
            ]
        },
        "ach_summary": {
            "matrix_complete": ach["matrix_complete"],
            "warning_count": len(ach.get("warnings", []) or []),
            "diagnostic_evidence": ach.get("diagnostic_evidence", [])[:5],
            "hypothesis_scores": ach.get("hypothesis_scores", []),
        },
    }


def _iter_runs(
    summary_payload: dict[str, Any],
    *,
    artifact_root: Path | None,
) -> list[tuple[str, dict[str, Any]]]:
    runs: list[tuple[str, dict[str, Any]]] = []
    if isinstance(summary_payload.get("rows"), list):
        runs.append((str(summary_payload.get("fixture") or "single_fixture"), summary_payload))
        return runs
    for result in summary_payload.get("results", []) or []:
        if not isinstance(result, dict):
            continue
        fixture = str(result.get("fixture") or "").strip()
        qa_json = str(result.get("qa_json") or "").strip()
        if not fixture or not qa_json:
            continue
        path = _resolve_artifact_path(Path(qa_json), artifact_root=artifact_root)
        if not path.exists():
            continue
        try:
            runs.append((fixture, json.loads(path.read_text(encoding="utf-8"))))
        except Exception:
            continue
    return runs


def _resolve_artifact_path(path: Path, *, artifact_root: Path | None) -> Path:
    if path.exists() or artifact_root is None:
        return path
    root = artifact_root if artifact_root.is_absolute() else Path.cwd() / artifact_root
    text = str(path)
    lowered = text.lower()
    archive_marker = "prethinker_tmp_archive"
    if archive_marker in lowered:
        suffix = text[lowered.index(archive_marker) + len(archive_marker) :].lstrip("\\/")
        candidate = root / Path(suffix)
        if candidate.exists():
            return candidate
    return path


def _row_features(row: dict[str, Any]) -> dict[str, Any]:
    failure = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
    envelope = row.get("response_envelope") if isinstance(row.get("response_envelope"), dict) else {}
    query_stats = _query_stats(row)
    question_shapes = _question_shapes(str(row.get("utterance") or ""))
    return {
        "verdict": _verdict(row),
        "failure_surface": str(failure.get("surface") or envelope.get("failure_surface") or "unknown"),
        "response_status": str(envelope.get("status") or "unknown"),
        "question_shapes": question_shapes,
        **query_stats,
    }


def _verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    return str(judge.get("verdict") or "unknown")


def _query_stats(row: dict[str, Any]) -> dict[str, Any]:
    query_count = 0
    nonempty_query_count = 0
    direct_nonempty_count = 0
    source_record_nonempty_count = 0
    support_surface_count = 0
    query_error_count = 0
    support_predicates: set[str] = set()
    for query_result in row.get("query_results", []) or []:
        if not isinstance(query_result, dict):
            continue
        result = query_result.get("result")
        if not isinstance(result, dict):
            continue
        query_count += 1
        predicate = str(result.get("predicate") or "").strip()
        status = str(result.get("status") or "").strip().casefold()
        if status and status not in {"success", "ok"}:
            query_error_count += 1
        rows = result.get("rows")
        has_rows = isinstance(rows, list) and bool(rows)
        if not has_rows:
            continue
        nonempty_query_count += 1
        if _is_support_surface(predicate):
            support_surface_count += 1
            support_predicates.add(predicate)
        elif predicate.startswith("source_record_"):
            source_record_nonempty_count += 1
        elif not _is_support_surface(predicate):
            direct_nonempty_count += 1
    return {
        "query_count": query_count,
        "nonempty_query_count": nonempty_query_count,
        "direct_nonempty_count": direct_nonempty_count,
        "source_record_nonempty_count": source_record_nonempty_count,
        "support_surface_count": support_surface_count,
        "support_predicates": sorted(support_predicates),
        "query_error_count": query_error_count,
    }


def _is_support_surface(predicate: str) -> bool:
    return (
        predicate.endswith("_support")
        or predicate.endswith("_companion")
        or predicate.endswith("_helper")
        or "_helper_" in predicate
    )


def _question_shapes(question: str) -> list[str]:
    text = question.casefold()
    shapes = []
    if re.search(r"\b(list|every|all|each)\b", text):
        shapes.append("list_inventory")
    if re.search(r"\b(section|heading|paragraph|field|block|where|under|precedes|immediately)\b", text):
        shapes.append("source_coordinate")
    if re.search(r"\b(date|deadline|duration|days?|chronological|order|before|after|between)\b", text):
        shapes.append("date_sequence")
    if re.search(r"\b(sign|signed|signer|title|address|email|contact|recipient)\b", text):
        shapes.append("formal_block")
    if re.search(r"\b(compare|difference|cross-check|cross check|same|distinct|variation)\b", text):
        shapes.append("cross_context")
    return shapes


def _build_payload(features: dict[str, Any], *, include_failure_label: bool) -> dict[str, Any]:
    evidence = _evidence_from_features(features, include_failure_label=include_failure_label)
    judgments = []
    for item in evidence:
        for hypothesis in HYPOTHESES:
            judgments.append(
                {
                    "evidence_id": item["id"],
                    "hypothesis_id": hypothesis["id"],
                    **_judgment_for(item["kind"], hypothesis["id"]),
                }
            )
    return {
        "schema_version": "qa_failure_ach_probe_payload_v1",
        "hypotheses": HYPOTHESES,
        "evidence": evidence,
        "judgments": judgments,
    }


def _evidence_from_features(features: dict[str, Any], *, include_failure_label: bool) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []

    status = features["response_status"]
    if status == "coverage_gap":
        evidence.append(_e("e_response_coverage_gap", "Response envelope reports a coverage gap.", "high"))
    elif status == "not_established":
        evidence.append(_e("e_response_not_established", "Response envelope reports not established.", "medium"))
    elif status == "partially_established":
        evidence.append(_e("e_response_partially_established", "Response envelope reports partial support.", "medium"))
    elif status in {"clarification_required", "ambiguous"}:
        evidence.append(_e("e_response_answer_boundary", "Response envelope reports clarification or ambiguity.", "high"))

    if features["query_count"] == 0 or features["nonempty_query_count"] == 0:
        evidence.append(_e("e_no_nonempty_query_evidence", "No nonempty query evidence reached the row.", "high"))
    if features["source_record_nonempty_count"] > 0 and features["direct_nonempty_count"] == 0:
        evidence.append(
            _e(
                "e_source_record_without_direct_rows",
                "Source-record rows were available, but no direct non-source-record rows were nonempty.",
                "high",
            )
        )
    if features["direct_nonempty_count"] > 0 and features["verdict"] != "exact":
        evidence.append(
            _e(
                "e_direct_rows_but_nonexact",
                "Direct compiled rows were nonempty, but the row was still non-exact.",
                "high",
            )
        )
    if features["support_surface_count"] > 0 and features["verdict"] != "exact":
        evidence.append(
            _e(
                "e_support_surface_but_nonexact",
                "Deterministic support surfaces appeared but did not produce an exact row.",
                "medium",
            )
        )
    if features["query_error_count"] > 0:
        evidence.append(_e("e_query_error", "At least one query result reported a non-success status.", "high"))

    for shape in features.get("question_shapes", []):
        evidence.append(_e(f"e_question_shape_{shape}", f"Question shape: {shape}.", "medium"))

    if include_failure_label:
        surface = str(features.get("failure_surface") or "unknown")
        if surface != "unknown":
            evidence.append(
                {
                    "id": "e_existing_failure_surface_label",
                    "kind": f"existing_label:{surface}",
                    "label": f"Existing failure-surface classifier label: {surface}.",
                    "diagnosticity": "medium",
                }
            )

    return evidence or [_e("e_sparse_diagnostics", "No strong deterministic diagnostic feature fired.", "low")]


def _e(item_id: str, label: str, diagnosticity: str) -> dict[str, Any]:
    return {
        "id": item_id,
        "kind": item_id,
        "label": label,
        "diagnosticity": diagnosticity,
    }


def _judgment_for(kind: str, hypothesis_id: str) -> dict[str, str]:
    table: dict[str, dict[str, str]] = {
        "e_response_coverage_gap": {
            "h_compile_preservation": "consistent",
            "h_query_route": "neutral",
            "h_join_computation": "neutral",
            "h_answer_assessment": "inconsistent",
        },
        "e_response_not_established": {
            "h_compile_preservation": "neutral",
            "h_query_route": "consistent",
            "h_join_computation": "consistent",
            "h_answer_assessment": "inconsistent",
        },
        "e_response_partially_established": {
            "h_compile_preservation": "neutral",
            "h_query_route": "neutral",
            "h_join_computation": "consistent",
            "h_answer_assessment": "consistent",
        },
        "e_response_answer_boundary": {
            "h_compile_preservation": "neutral",
            "h_query_route": "neutral",
            "h_join_computation": "neutral",
            "h_answer_assessment": "consistent",
        },
        "e_no_nonempty_query_evidence": {
            "h_compile_preservation": "consistent",
            "h_query_route": "consistent",
            "h_join_computation": "inconsistent",
            "h_answer_assessment": "inconsistent",
        },
        "e_source_record_without_direct_rows": {
            "h_compile_preservation": "consistent",
            "h_query_route": "neutral",
            "h_join_computation": "neutral",
            "h_answer_assessment": "inconsistent",
        },
        "e_direct_rows_but_nonexact": {
            "h_compile_preservation": "inconsistent",
            "h_query_route": "consistent",
            "h_join_computation": "consistent",
            "h_answer_assessment": "neutral",
        },
        "e_support_surface_but_nonexact": {
            "h_compile_preservation": "neutral",
            "h_query_route": "consistent",
            "h_join_computation": "consistent",
            "h_answer_assessment": "neutral",
        },
        "e_query_error": {
            "h_compile_preservation": "inconsistent",
            "h_query_route": "consistent",
            "h_join_computation": "consistent",
            "h_answer_assessment": "neutral",
        },
        "e_question_shape_list_inventory": {
            "h_compile_preservation": "consistent",
            "h_query_route": "neutral",
            "h_join_computation": "consistent",
            "h_answer_assessment": "neutral",
        },
        "e_question_shape_source_coordinate": {
            "h_compile_preservation": "consistent",
            "h_query_route": "consistent",
            "h_join_computation": "consistent",
            "h_answer_assessment": "neutral",
        },
        "e_question_shape_date_sequence": {
            "h_compile_preservation": "neutral",
            "h_query_route": "neutral",
            "h_join_computation": "consistent",
            "h_answer_assessment": "neutral",
        },
        "e_question_shape_formal_block": {
            "h_compile_preservation": "consistent",
            "h_query_route": "neutral",
            "h_join_computation": "neutral",
            "h_answer_assessment": "neutral",
        },
        "e_question_shape_cross_context": {
            "h_compile_preservation": "neutral",
            "h_query_route": "neutral",
            "h_join_computation": "consistent",
            "h_answer_assessment": "consistent",
        },
        "e_sparse_diagnostics": {
            "h_compile_preservation": "neutral",
            "h_query_route": "neutral",
            "h_join_computation": "neutral",
            "h_answer_assessment": "neutral",
        },
    }
    if kind.startswith("existing_label:"):
        target = _classifier_hypothesis(kind.split(":", 1)[1])
        return {
            "assessment": "consistent" if target == hypothesis_id else "neutral",
            "rationale": "Existing failure-surface label used as caged diagnostic evidence only.",
        }
    assessment = table.get(kind, {}).get(hypothesis_id, "neutral")
    return {
        "assessment": assessment,
        "rationale": f"{kind} is {assessment} with {hypothesis_id}.",
    }


def _classifier_hypothesis(surface: str) -> str:
    mapping = {
        "compile_surface_gap": "h_compile_preservation",
        "query_surface_gap": "h_query_route",
        "hybrid_join_gap": "h_join_computation",
        "answer_surface_gap": "h_answer_assessment",
        "judge_uncertain": "h_answer_assessment",
        "not_applicable": "",
        "unknown": "",
    }
    return mapping.get(str(surface or ""), "")


def _fixture_family(fixture: str) -> str:
    if "_" not in fixture:
        return fixture or "unknown"
    return fixture.split("_", 1)[0] or "unknown"
