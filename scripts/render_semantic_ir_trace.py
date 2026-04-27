#!/usr/bin/env python3
"""Render semantic_ir_v1 JSONL runs into readable layer-by-layer traces.

The runner artifacts are intentionally local and machine-oriented. This script
turns them into an inspection transcript that follows one utterance through:

1. focused model input and context;
2. raw semantic_ir_v1 workspace proposal;
3. mapper/admission projection;
4. facts/rules/retracts/queries that would reach the runtime;
5. skipped/challenged operations and their rationale codes.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.semantic_ir import semantic_ir_to_legacy_parse  # noqa: E402


DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "semantic_ir_trace_views"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _truncate(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n... [truncated]"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL: {exc}") from exc
            if not isinstance(parsed, dict):
                raise ValueError(f"{path}:{line_number}: expected object, got {type(parsed).__name__}")
            records.append(parsed)
    return records


def _scenario_lookup() -> dict[str, dict[str, Any]]:
    try:
        from scripts.run_semantic_ir_prompt_bakeoff import WILD_SCENARIOS  # noqa: WPS433
    except Exception:
        return {}
    return {str(row.get("id", "")): row for row in WILD_SCENARIOS if str(row.get("id", "")).strip()}


def _nested_get(value: Any, path: list[str]) -> Any:
    current = value
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _extract_semantic_side(record: dict[str, Any], side: str) -> dict[str, Any]:
    if side == "root":
        return record
    node = record.get(side)
    if isinstance(node, dict):
        out = dict(record)
        out.update(node)
        out["_source_side"] = side
        return out
    return record


def _extract_parsed(record: dict[str, Any]) -> dict[str, Any] | None:
    parsed = record.get("parsed")
    if isinstance(parsed, dict):
        return parsed

    for path in (
        ["raw", "compiler_trace", "parse", "semantic_ir", "parsed"],
        ["raw", "compiler_trace", "prethink", "semantic_ir", "parsed"],
        ["compiler_trace", "parse", "semantic_ir", "parsed"],
        ["compiler_trace", "prethink", "semantic_ir", "parsed"],
        ["result", "compiler_trace", "parse", "semantic_ir", "parsed"],
    ):
        candidate = _nested_get(record, path)
        if isinstance(candidate, dict):
            return candidate
    return None


def _extract_raw_content(record: dict[str, Any]) -> str:
    for key in ("content", "raw_message", "response_text"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for path in (
        ["raw", "compiler_trace", "parse", "semantic_ir", "raw_message"],
        ["raw", "compiler_trace", "prethink", "semantic_ir", "raw_message"],
        ["compiler_trace", "parse", "semantic_ir", "raw_message"],
        ["compiler_trace", "prethink", "semantic_ir", "raw_message"],
    ):
        value = _nested_get(record, path)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _extract_model_input(record: dict[str, Any]) -> dict[str, Any]:
    candidate = record.get("model_input")
    if isinstance(candidate, dict):
        return candidate
    for path in (
        ["raw", "compiler_trace", "parse", "semantic_ir", "model_input"],
        ["raw", "compiler_trace", "prethink", "semantic_ir", "model_input"],
        ["compiler_trace", "parse", "semantic_ir", "model_input"],
        ["compiler_trace", "prethink", "semantic_ir", "model_input"],
    ):
        value = _nested_get(record, path)
        if isinstance(value, dict):
            return value
    return {}


def _extract_mapped(
    record: dict[str, Any],
    parsed: dict[str, Any] | None,
    allowed_predicates: list[str],
    predicate_contracts: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[str]]:
    mapped = record.get("mapped")
    if isinstance(mapped, dict):
        warnings = [str(item) for item in _as_list(record.get("mapper_warnings"))]
        return mapped, warnings

    for path in (
        ["execution", "parse"],
        ["raw", "execution", "parse"],
        ["raw", "compiler_trace", "parse", "normalized"],
        ["raw", "compiler_trace", "parse", "admitted"],
    ):
        candidate = _nested_get(record, path)
        if isinstance(candidate, dict) and isinstance(candidate.get("admission_diagnostics"), dict):
            return candidate, []

    if isinstance(parsed, dict):
        try:
            return semantic_ir_to_legacy_parse(
                parsed,
                allowed_predicates=allowed_predicates,
                predicate_contracts=predicate_contracts,
            )
        except Exception as exc:
            return {"render_error": f"semantic_ir_to_legacy_parse failed: {exc}"}, []
    return {}, []


def _input_from_record(
    record: dict[str, Any],
    scenario_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    scenario_id = str(record.get("scenario_id", "") or record.get("case_id", "") or record.get("id", "")).strip()
    scenario = scenario_map.get(scenario_id, {})
    model_input = _extract_model_input(record)
    input_payload = model_input.get("input_payload") if isinstance(model_input.get("input_payload"), dict) else {}
    input_scenario = model_input.get("scenario") if isinstance(model_input.get("scenario"), dict) else {}

    utterance = (
        _text(record.get("utterance")).strip()
        or _text(input_payload.get("utterance")).strip()
        or _text(input_scenario.get("utterance")).strip()
        or _text(model_input.get("utterance")).strip()
        or _text(scenario.get("utterance")).strip()
    )
    context_source = record.get("context") if "context" in record else None
    if context_source is None:
        context_source = input_payload.get("context") if "context" in input_payload else None
    if context_source is None:
        context_source = input_scenario.get("context") if "context" in input_scenario else None
    if context_source is None:
        context_source = model_input.get("context") if "context" in model_input else scenario.get("context")
    context = _as_list(context_source)
    allowed = _as_list(
        record.get("allowed_predicates")
        if "allowed_predicates" in record
        else (
            input_payload.get("allowed_predicates")
            if "allowed_predicates" in input_payload
            else (
                input_scenario.get("allowed_predicates")
                if "allowed_predicates" in input_scenario
                else model_input.get("allowed_predicates", scenario.get("allowed_predicates"))
            )
        )
    )
    contracts = _as_list(
        record.get("predicate_contracts")
        if "predicate_contracts" in record
        else (
            input_payload.get("predicate_contracts")
            if "predicate_contracts" in input_payload
            else (
                input_scenario.get("predicate_contracts")
                if "predicate_contracts" in input_scenario
                else model_input.get("predicate_contracts", scenario.get("predicate_contracts"))
            )
        )
    )
    expect = record.get("expect") if isinstance(record.get("expect"), dict) else scenario.get("expect", {})
    if not isinstance(expect, dict):
        expect = {}
    expected_decision = (
        _text(record.get("expected_decision")).strip()
        or _text(expect.get("decision")).strip()
        or _text((record.get("score") or {}).get("expected_decision") if isinstance(record.get("score"), dict) else "").strip()
    )
    return {
        "scenario_id": scenario_id,
        "domain": _text(
            record.get("domain")
            or input_payload.get("domain")
            or input_scenario.get("domain")
            or model_input.get("domain")
            or scenario.get("domain")
        ).strip(),
        "utterance": utterance,
        "context": [str(item) for item in context],
        "allowed_predicates": [str(item) for item in allowed],
        "predicate_contracts": [item for item in contracts if isinstance(item, dict)],
        "expected_decision": expected_decision,
        "expect": expect,
    }


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    def cell(value: Any) -> str:
        text = _text(value).replace("\n", "<br>").replace("|", "\\|").strip()
        return text if text else " "

    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(cell(item) for item in row) + " |")
    return out


def _details(summary: str, body: str, *, open_by_default: bool = False) -> list[str]:
    open_attr = " open" if open_by_default else ""
    return [
        f"<details{open_attr}><summary>{html.escape(summary)}</summary>",
        "",
        body,
        "",
        "</details>",
    ]


def _code_block(value: Any, language: str = "json", *, max_chars: int = 0) -> str:
    text = value if isinstance(value, str) else _json_dumps(value)
    text = _truncate(text, max_chars)
    return f"```{language}\n{text}\n```"


def _render_entities(parsed: dict[str, Any]) -> list[str]:
    rows = []
    for entity in _as_list(parsed.get("entities")):
        if isinstance(entity, dict):
            rows.append(
                [
                    entity.get("id", ""),
                    entity.get("surface", ""),
                    entity.get("normalized", ""),
                    entity.get("type", ""),
                    entity.get("confidence", ""),
                ]
            )
    if not rows:
        return ["No entities proposed."]
    return _markdown_table(["id", "surface", "normalized", "type", "confidence"], rows)


def _render_referents(parsed: dict[str, Any]) -> list[str]:
    rows = []
    for ref in _as_list(parsed.get("referents")):
        if isinstance(ref, dict):
            rows.append(
                [
                    ref.get("surface", ""),
                    ref.get("status", ""),
                    ", ".join(str(item) for item in _as_list(ref.get("candidates"))),
                    ref.get("chosen", ""),
                ]
            )
    if not rows:
        return ["No referent ambiguity/resolution entries."]
    return _markdown_table(["surface", "status", "candidates", "chosen"], rows)


def _render_assertions(parsed: dict[str, Any]) -> list[str]:
    rows = []
    for assertion in _as_list(parsed.get("assertions")):
        if isinstance(assertion, dict):
            rows.append(
                [
                    assertion.get("kind", ""),
                    assertion.get("subject", ""),
                    assertion.get("relation_concept", ""),
                    assertion.get("object", ""),
                    assertion.get("polarity", ""),
                    assertion.get("certainty", ""),
                ]
            )
    if not rows:
        return ["No assertions proposed."]
    return _markdown_table(["kind", "subject", "relation", "object", "polarity", "certainty"], rows)


def _render_unsafe(parsed: dict[str, Any]) -> list[str]:
    rows = []
    for item in _as_list(parsed.get("unsafe_implications")):
        if isinstance(item, dict):
            rows.append([item.get("candidate", ""), item.get("commit_policy", ""), item.get("why_unsafe", "")])
    if not rows:
        return ["No unsafe implications flagged by the model."]
    return _markdown_table(["candidate", "policy", "why unsafe"], rows)


def _render_truth_maintenance(parsed: dict[str, Any]) -> list[str]:
    tm = parsed.get("truth_maintenance")
    if not isinstance(tm, dict):
        return ["No truth-maintenance proposal emitted."]
    lines: list[str] = []

    support_rows = []
    for item in _as_list(tm.get("support_links")):
        if isinstance(item, dict):
            support_rows.append(
                [
                    item.get("operation_index", ""),
                    item.get("support_kind", ""),
                    item.get("role", ""),
                    item.get("support_ref", ""),
                    item.get("confidence", ""),
                ]
            )
    lines.append("**Support / dependency links:**")
    lines.append("")
    lines.extend(
        _markdown_table(["op #", "kind", "role", "support ref", "confidence"], support_rows)
        if support_rows
        else ["- none"]
    )
    lines.append("")

    conflict_rows = []
    for item in _as_list(tm.get("conflicts")):
        if isinstance(item, dict):
            conflict_rows.append(
                [
                    item.get("new_operation_index", ""),
                    item.get("existing_ref", ""),
                    item.get("conflict_kind", ""),
                    item.get("recommended_policy", ""),
                    item.get("why", ""),
                ]
            )
    lines.append("**Conflict proposals:**")
    lines.append("")
    lines.extend(
        _markdown_table(["op #", "existing/context ref", "kind", "policy", "why"], conflict_rows)
        if conflict_rows
        else ["- none"]
    )
    lines.append("")

    retract_rows = []
    for item in _as_list(tm.get("retraction_plan")):
        if isinstance(item, dict):
            retract_rows.append([item.get("operation_index", ""), item.get("target_ref", ""), item.get("reason", "")])
    lines.append("**Retraction plan:**")
    lines.append("")
    lines.extend(
        _markdown_table(["op #", "target", "reason"], retract_rows)
        if retract_rows
        else ["- none"]
    )
    lines.append("")

    consequence_rows = []
    for item in _as_list(tm.get("derived_consequences")):
        if isinstance(item, dict):
            consequence_rows.append(
                [
                    item.get("statement", ""),
                    ", ".join(str(entry) for entry in _as_list(item.get("basis"))),
                    item.get("commit_policy", ""),
                ]
            )
    lines.append("**Derived consequences:**")
    lines.append("")
    lines.extend(
        _markdown_table(["statement", "basis", "commit policy"], consequence_rows)
        if consequence_rows
        else ["- none"]
    )
    return lines


def _render_candidate_ops(parsed: dict[str, Any]) -> list[str]:
    rows = []
    for index, op in enumerate(_as_list(parsed.get("candidate_operations"))):
        if isinstance(op, dict):
            rows.append(
                [
                    index,
                    op.get("operation", ""),
                    op.get("predicate", ""),
                    ", ".join(str(item) for item in _as_list(op.get("args"))),
                    op.get("source", ""),
                    op.get("safety", ""),
                    op.get("polarity", ""),
                    op.get("clause", ""),
                ]
            )
    if not rows:
        return ["No candidate operations proposed."]
    return _markdown_table(["#", "op", "predicate", "args", "source", "safety", "polarity", "clause"], rows)


def _render_admission_ops(diagnostics: dict[str, Any]) -> list[str]:
    rows = []
    for op in _as_list(diagnostics.get("operations")):
        if not isinstance(op, dict):
            continue
        rows.append(
            [
                op.get("index", ""),
                "yes" if op.get("admitted") else "no",
                op.get("effect", ""),
                op.get("operation", ""),
                op.get("predicate", ""),
                ", ".join(str(item) for item in _as_list(op.get("args"))),
                "; ".join(str(item) for item in _as_list(op.get("clauses"))),
                op.get("skip_reason", ""),
                ", ".join(str(item) for item in _as_list(op.get("rationale_codes"))),
            ]
        )
    if not rows:
        return ["No operation-level admission diagnostics."]
    return _markdown_table(
        ["#", "admit", "effect", "op", "predicate", "args", "clauses", "skip/challenge", "rationale"],
        rows,
    )


def _render_clause_list(title: str, clauses: list[Any]) -> list[str]:
    lines = [f"**{title}:**", ""]
    values = [str(item).strip() for item in clauses if str(item).strip()]
    if not values:
        return lines + ["- none", ""]
    return lines + [f"- `{item}`" for item in values] + [""]


def _render_clause_supports(mapped: dict[str, Any], diagnostics: dict[str, Any]) -> list[str]:
    supports = mapped.get("clause_supports")
    if not isinstance(supports, dict):
        supports = diagnostics.get("clause_supports")
    if not isinstance(supports, dict):
        return ["**Clause support records:**", "", "- none"]
    rows = []
    for effect in ("facts", "rules", "retracts", "queries"):
        for row in _as_list(supports.get(effect)):
            if not isinstance(row, dict):
                continue
            rows.append(
                [
                    effect,
                    row.get("clause", ""),
                    row.get("operation_index", ""),
                    row.get("operation", ""),
                    row.get("predicate", ""),
                    row.get("source", ""),
                    ", ".join(str(item) for item in _as_list(row.get("rationale_codes"))),
                ]
            )
    if not rows:
        return ["**Clause support records:**", "", "- none"]
    return ["**Clause support records:**", ""] + _markdown_table(
        ["effect", "clause", "op #", "op", "predicate", "source", "rationale"],
        rows,
    )


def _render_truth_alignment(diagnostics: dict[str, Any]) -> list[str]:
    alignment = diagnostics.get("truth_maintenance_alignment")
    if not isinstance(alignment, dict):
        return ["No truth-maintenance/admission alignment diagnostics."]
    lines = [
        "**Truth-maintenance/admission alignment:**",
        "",
        f"- support links: `{alignment.get('support_link_count', 0)}`",
        f"- conflicts: `{alignment.get('conflict_count', 0)}`",
        f"- retraction-plan entries: `{alignment.get('retraction_plan_count', 0)}`",
        f"- derived consequences: `{alignment.get('derived_consequence_count', 0)}`",
        f"- admitted operations with support: `{alignment.get('admitted_with_support_count', 0)}`",
        f"- admitted operations without support: `{alignment.get('admitted_without_support_count', 0)}`",
        f"- skipped operations with model support: `{alignment.get('skipped_with_support_count', 0)}`",
        f"- needs-clarification operations with support: `{alignment.get('needs_clarification_with_support_count', 0)}`",
        f"- conflicts on admitted operations: `{alignment.get('conflict_on_admitted_count', 0)}`",
        "",
    ]
    rows = []
    for item in _as_list(alignment.get("fuzzy_edges")):
        if isinstance(item, dict):
            rows.append(
                [
                    item.get("severity", ""),
                    item.get("kind", ""),
                    item.get("operation_index", ""),
                    item.get("detail", ""),
                ]
            )
    lines.append("**Fuzzy edges:**")
    lines.append("")
    lines.extend(
        _markdown_table(["severity", "kind", "op #", "detail"], rows)
        if rows
        else ["- none"]
    )
    return lines


def _render_conflict_pressure(input_info: dict[str, Any], parsed: dict[str, Any], diagnostics: dict[str, Any]) -> list[str]:
    context_markers = (
        "existing",
        "current",
        "previous",
        "previously",
        "known",
        "context",
        "already",
        "prior",
        "old",
    )
    old_state = [
        item
        for item in input_info.get("context", [])
        if any(marker in str(item).lower() for marker in context_markers)
    ]
    unsafe = _as_list(parsed.get("unsafe_implications"))
    skipped = [
        op
        for op in _as_list(diagnostics.get("operations"))
        if isinstance(op, dict) and not op.get("admitted")
    ]
    if not old_state and not unsafe and not skipped:
        return ["No explicit old-state, unsafe implication, or skipped-operation pressure visible in this record."]

    lines = []
    lines.append("**Old/current state visible to the model:**")
    lines.append("")
    lines.extend([f"- {_text(item)}" for item in old_state] or ["- none marked in context"])
    lines.append("")
    lines.append("**Unsafe implications challenged before KB admission:**")
    lines.append("")
    if unsafe:
        for item in unsafe:
            if isinstance(item, dict):
                lines.append(
                    f"- `{_text(item.get('candidate')).strip() or 'candidate'}` -> "
                    f"{_text(item.get('commit_policy')).strip() or 'policy'}: "
                    f"{_text(item.get('why_unsafe')).strip()}"
                )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("**Skipped operations / conflict gates:**")
    lines.append("")
    if skipped:
        for op in skipped:
            reason = _text(op.get("skip_reason")).strip() or "skipped"
            codes = ", ".join(str(item) for item in _as_list(op.get("rationale_codes"))) or "no rationale code"
            pred = _text(op.get("predicate")).strip()
            args = ", ".join(str(item) for item in _as_list(op.get("args")))
            lines.append(f"- `{pred}({args})`: {reason} [{codes}]")
    else:
        lines.append("- none")
    return lines


def _diagnostics_from_mapped(mapped: dict[str, Any]) -> dict[str, Any]:
    diagnostics = mapped.get("admission_diagnostics")
    return diagnostics if isinstance(diagnostics, dict) else {}


def _render_record(
    record: dict[str, Any],
    *,
    index: int,
    scenario_map: dict[str, dict[str, Any]],
    raw_chars: int,
    side: str,
) -> list[str]:
    record = _extract_semantic_side(record, side)
    input_info = _input_from_record(record, scenario_map)
    model_input = _extract_model_input(record)
    parsed = _extract_parsed(record)
    raw_content = _extract_raw_content(record)
    mapped, mapper_warnings = _extract_mapped(
        record,
        parsed,
        input_info["allowed_predicates"],
        input_info["predicate_contracts"],
    )
    diagnostics = _diagnostics_from_mapped(mapped)
    score = record.get("score") if isinstance(record.get("score"), dict) else {}
    admission_score = record.get("admission_score") if isinstance(record.get("admission_score"), dict) else {}

    scenario_label = input_info["scenario_id"] or f"record_{index}"
    model = _text(record.get("model") or record.get("semantic_model") or record.get("backend")).strip()
    actual = _text(score.get("decision") or (parsed or {}).get("decision")).strip()
    expected = input_info["expected_decision"]
    projected = _text(diagnostics.get("projected_decision")).strip()
    layer_summary = [
        f"model=`{model or 'unknown'}`",
        f"decision model=`{actual or 'unknown'}`",
        f"projected=`{projected or 'unknown'}`",
    ]
    if expected:
        layer_summary.append(f"expected=`{expected}`")
    if score:
        layer_summary.append(f"score=`{score.get('rough_score', '')}`")
    if admission_score and admission_score.get("contract_present"):
        layer_summary.append(
            f"admission=`{admission_score.get('check_count', 0)}/{admission_score.get('check_total', 0)}`"
        )

    lines: list[str] = [
        f"## {index}. `{scenario_label}`",
        "",
        " ".join(layer_summary),
        "",
        "### Layer 0 - Focused Model Input",
        "",
        f"Domain: `{input_info['domain'] or 'unknown'}`",
        "",
        "**Utterance:**",
        "",
        f"> {_text(input_info['utterance']) or '[not recorded]'}",
        "",
    ]
    if input_info["context"]:
        lines.append("**Context visible to model:**")
        lines.append("")
        lines.extend(f"- {_text(item)}" for item in input_info["context"])
        lines.append("")
    else:
        lines.extend(["**Context visible to model:** none recorded", ""])
    if input_info["allowed_predicates"]:
        lines.append("**Allowed predicate palette:**")
        lines.append("")
        lines.append(", ".join(f"`{item}`" for item in input_info["allowed_predicates"]))
        lines.append("")
    else:
        lines.extend(["**Allowed predicate palette:** not recorded", ""])
    if model_input:
        prompt_bits = []
        if isinstance(model_input.get("input_payload"), dict):
            prompt_bits.extend(["**Input JSON payload:**", "", _code_block(model_input["input_payload"], "json", max_chars=raw_chars)])
        if isinstance(model_input.get("messages"), list):
            prompt_bits.extend(["", "**Exact chat messages sent to model:**", "", _code_block(model_input["messages"], "json", max_chars=raw_chars)])
        if isinstance(model_input.get("options"), dict):
            prompt_bits.extend(["", "**Generation/runtime options:**", "", _code_block(model_input["options"], "json")])
        if not prompt_bits:
            prompt_bits.append(_code_block(model_input, "json", max_chars=raw_chars))
        lines.extend(_details("Recorded model input / request envelope", "\n".join(prompt_bits)))
        lines.append("")

    lines.extend(["### Layer 1 - Raw Semantic Workspace Proposal", ""])
    if raw_content:
        lines.extend(_details("Raw model JSON/text", _code_block(raw_content, "json", max_chars=raw_chars)))
    else:
        lines.append("Raw model output was not recorded.")
    lines.append("")

    lines.extend(["### Layer 2 - Parsed `semantic_ir_v1` Workspace", ""])
    if not isinstance(parsed, dict):
        lines.append(f"Parse unavailable. Error: `{_text(record.get('parse_error')).strip() or 'unknown'}`")
        return lines + [""]

    lines.append(
        f"Model decision: `{parsed.get('decision', '')}`; turn type: `{parsed.get('turn_type', '')}`; "
        f"bad commit risk: `{((parsed.get('self_check') or {}) if isinstance(parsed.get('self_check'), dict) else {}).get('bad_commit_risk', '')}`"
    )
    lines.append("")
    lines.extend(_render_entities(parsed))
    lines.append("")
    lines.extend(_render_referents(parsed))
    lines.append("")
    lines.extend(_render_assertions(parsed))
    lines.append("")
    lines.extend(_render_unsafe(parsed))
    lines.append("")
    lines.extend(_render_truth_maintenance(parsed))
    lines.append("")
    lines.extend(_render_candidate_ops(parsed))
    lines.append("")

    clarification_questions = [str(item).strip() for item in _as_list(parsed.get("clarification_questions")) if str(item).strip()]
    lines.append("**Clarification questions:**")
    lines.append("")
    lines.extend([f"- {item}" for item in clarification_questions] or ["- none"])
    lines.append("")
    self_check = parsed.get("self_check") if isinstance(parsed.get("self_check"), dict) else {}
    notes = [str(item).strip() for item in _as_list(self_check.get("notes")) if str(item).strip()]
    missing = [str(item).strip() for item in _as_list(self_check.get("missing_slots")) if str(item).strip()]
    lines.append("**Self-check:**")
    lines.append("")
    lines.append(f"- missing slots: {', '.join(missing) if missing else 'none'}")
    lines.extend([f"- note: {item}" for item in notes] or ["- note: none"])
    lines.append("")

    lines.extend(["### Layer 3 - Deterministic Mapper / Admission Gate", ""])
    if "render_error" in mapped:
        lines.append(f"Mapper unavailable: `{mapped['render_error']}`")
        return lines + [""]

    lines.append(f"Legacy intent: `{mapped.get('intent', '')}`")
    logic_string = str(mapped.get("logic_string", "")).strip()
    if logic_string:
        lines.extend(["", "**Projected logic string:**", "", _code_block(logic_string, "prolog")])
    lines.append("")

    if diagnostics:
        features = diagnostics.get("features") if isinstance(diagnostics.get("features"), dict) else {}
        lines.extend(
            [
                f"Model decision: `{diagnostics.get('model_decision', '')}`",
                f"Projected decision: `{diagnostics.get('projected_decision', '')}`",
                f"Projection reason: `{diagnostics.get('projection_reason', '')}`",
                f"Operations: `{diagnostics.get('operation_count', 0)}` total, "
                f"`{diagnostics.get('admitted_count', 0)}` admitted, "
                f"`{diagnostics.get('skipped_count', 0)}` skipped/challenged",
                f"Mapper pressure: unresolved_referents=`{features.get('has_unresolved_referents', '')}`, "
                f"unsafe_implications=`{features.get('has_unsafe_implications', '')}`, "
                f"palette_enabled=`{features.get('predicate_palette_enabled', '')}`, "
                f"out_of_palette_write=`{features.get('has_out_of_palette_safe_write', '')}`, "
                f"contract_enabled=`{features.get('predicate_contract_enabled', '')}`, "
                f"contract_invalid_write=`{features.get('has_contract_invalid_safe_write', '')}`, "
                f"contract_policy_invalid=`{features.get('has_contract_policy_invalid_safe_write', '')}`, "
                f"temporal_order_mismatch=`{features.get('has_temporal_interval_order_mismatch', '')}`, "
                f"risk=`{features.get('bad_commit_risk', '')}`",
                "",
            ]
        )
        lines.extend(_render_admission_ops(diagnostics))
        lines.append("")
    else:
        lines.append("No admission diagnostics recorded.")
        lines.append("")

    lines.extend(["### Layer 3b - Conflict / Fact-Age Pressure", ""])
    lines.extend(_render_conflict_pressure(input_info, parsed, diagnostics))
    lines.append("")

    lines.extend(["### Layer 3c - Truth-Maintenance / Admission Delta", ""])
    lines.extend(_render_truth_alignment(diagnostics))
    lines.append("")

    lines.extend(["### Layer 4 - Runtime Payload / KB Surface", ""])
    lines.extend(_render_clause_list("Facts passivated for KB assertion", _as_list(mapped.get("facts"))))
    lines.extend(_render_clause_list("Rules passivated for KB assertion", _as_list(mapped.get("rules"))))
    lines.extend(_render_clause_list("Retract targets / correction clauses", _as_list(mapped.get("correction_retract_clauses"))))
    lines.extend(_render_clause_list("Queries extracted for KB read", _as_list(mapped.get("queries"))))
    lines.extend(_render_clause_supports(mapped, diagnostics))
    lines.append("")

    warnings = [str(item).strip() for item in mapper_warnings if str(item).strip()]
    lines.append("**Mapper warnings:**")
    lines.append("")
    lines.extend([f"- {item}" for item in warnings] or ["- none"])
    lines.append("")

    final_kb = record.get("final_kb")
    if isinstance(final_kb, list):
        lines.extend(_render_clause_list("Final KB snapshot from run record", final_kb))
        lines.append("")
    elif isinstance(record.get("raw"), dict) and isinstance(record["raw"].get("final_kb"), list):
        lines.extend(_render_clause_list("Final KB snapshot from run record", record["raw"]["final_kb"]))
        lines.append("")

    if score or admission_score:
        lines.extend(["### Layer 5 - Scenario Scoring", "", _code_block(score, "json")])
        if admission_score:
            lines.extend(["", "**Admission contract score:**", "", _code_block(admission_score, "json")])
        lines.append("")
    return lines


def render_markdown(
    records: list[dict[str, Any]],
    *,
    source: Path,
    raw_chars: int,
    side: str,
    limit: int,
) -> str:
    scenario_map = _scenario_lookup()
    selected = records[:limit] if limit > 0 else records
    lines: list[str] = [
        "# Semantic IR Trace",
        "",
        f"Generated: {_utc_now()}",
        f"Source: `{source}`",
        f"Records rendered: `{len(selected)}` of `{len(records)}`",
        "",
        "This transcript is diagnostic. The LLM proposes the semantic workspace; "
        "the mapper/admission layer remains the authority for KB mutation and query extraction.",
        "",
    ]
    for index, record in enumerate(selected, start=1):
        lines.extend(
            _render_record(
                record,
                index=index,
                scenario_map=scenario_map,
                raw_chars=raw_chars,
                side=side,
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def render_html(markdown_text: str, *, title: str) -> str:
    try:
        import markdown as markdown_lib  # type: ignore[import-not-found]

        body = markdown_lib.markdown(
            markdown_text,
            extensions=["extra", "tables", "fenced_code", "md_in_html"],
            output_format="html5",
        )
    except Exception:
        body = f"<pre>{html.escape(markdown_text)}</pre>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #101820;
      --panel: #1c252d;
      --panel-2: #26313a;
      --border: #46515c;
      --text: #efe9dd;
      --muted: #cbbda8;
      --accent: #d8914f;
      --green: #77c9a1;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, Segoe UI, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.48;
    }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 30px 20px 64px; }}
    h1 {{ margin: 0 0 14px; font-size: 30px; }}
    h2 {{
      margin: 34px 0 12px;
      padding: 18px 20px;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: linear-gradient(180deg, #23303a, #1b242d);
      font-size: 22px;
    }}
    h3 {{ margin: 28px 0 10px; font-size: 17px; color: #f6dcc0; }}
    p, ul {{ color: var(--text); }}
    code {{
      color: #f3d7ad;
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 4px;
      padding: 1px 4px;
    }}
    pre {{
      white-space: pre;
      overflow: auto;
      overflow-wrap: normal;
      max-height: 28rem;
      background: #151e26;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      line-height: 1.4;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
    }}
    pre code {{
      display: block;
      min-width: max-content;
      padding: 0;
      border: 0;
      background: transparent;
      color: #f4e6d0;
    }}
    details {{
      margin: 14px 0 22px;
      border: 1px solid var(--border);
      border-radius: 9px;
      background: rgba(255,255,255,0.035);
      overflow: hidden;
    }}
    summary {{
      cursor: pointer;
      padding: 10px 14px;
      background: #303942;
      color: #f5ddbc;
      font-weight: 700;
      user-select: none;
    }}
    details > *:not(summary) {{ margin-left: 14px; margin-right: 14px; }}
    table {{
      display: block;
      max-height: 30rem;
      overflow: auto;
      border-collapse: collapse;
      width: 100%;
      margin: 12px 0 24px;
      font-size: 14px;
      border: 1px solid var(--border);
      border-radius: 8px;
    }}
    thead {{ position: sticky; top: 0; z-index: 1; }}
    th, td {{ border: 1px solid var(--border); padding: 7px 9px; vertical-align: top; min-width: 120px; }}
    th {{ background: var(--panel-2); text-align: left; color: #f4d9b2; }}
    td {{ background: rgba(255,255,255,0.015); }}
    blockquote {{
      border-left: 4px solid var(--accent);
      margin-left: 0;
      padding: 10px 14px;
      background: rgba(216,145,79,0.09);
      color: #fff7eb;
      border-radius: 0 8px 8px 0;
    }}
    strong {{ color: #f6dfbf; }}
    a {{ color: #90c8ff; }}
  </style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render semantic_ir_v1 JSONL artifacts into a layered trace.")
    parser.add_argument("jsonl", help="Input JSONL from semantic IR bakeoff, incremental, or guardrail runs.")
    parser.add_argument("--out", default="", help="Output Markdown path. Defaults under tmp/semantic_ir_trace_views.")
    parser.add_argument("--html", action="store_true", help="Also write a simple HTML wrapper next to the Markdown.")
    parser.add_argument(
        "--raw-chars",
        type=int,
        default=12000,
        help="Maximum raw model-output characters per record; 0 means no truncation.",
    )
    parser.add_argument(
        "--side",
        choices=["root", "semantic_ir", "legacy"],
        default="root",
        help="For A/B records, render the selected nested side. Plain records use root.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Render only the first N records; 0 renders all.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.jsonl)
    if not source.is_absolute():
        source = (REPO_ROOT / source).resolve()
    records = _load_jsonl(source)

    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = (REPO_ROOT / out).resolve()
    else:
        DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = DEFAULT_OUT_DIR / f"{source.stem}.trace.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    markdown_text = render_markdown(
        records,
        source=source,
        raw_chars=int(args.raw_chars),
        side=str(args.side),
        limit=int(args.limit),
    )
    out.write_text(markdown_text, encoding="utf-8")
    print(f"Wrote {out}")
    if args.html:
        html_path = out.with_suffix(".html")
        html_path.write_text(render_html(markdown_text, title=out.stem), encoding="utf-8")
        print(f"Wrote {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
