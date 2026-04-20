#!/usr/bin/env python3
"""
Interrogate a compiled KB against source text.

Pipeline:
1) Fact audit: model-assisted grading for missed vs bogus facts.
2) Exam synthesis: generate query-based reasoning questions.
3) Runtime evaluation: execute queries against the KB with deterministic pass/fail.
4) Optional scenario export: emit validations as a reusable scenario JSON.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import kb_pipeline as kp  # noqa: E402
import golden_kb  # noqa: E402

DEFAULT_BASE_URLS = {
    "ollama": "http://127.0.0.1:11434",
    "lmstudio": "http://127.0.0.1:1234",
}

EXAM_STYLE_GUIDANCE = {
    "general": (
        "Balance retrieval, composition, contradiction checks, and lightweight temporal probes."
    ),
    "detective": (
        "Emphasize clue chaining, suspect elimination, alibi consistency, and contradiction exposure."
    ),
    "medical": (
        "Emphasize symptom->finding->diagnosis reasoning, contraindication checks, temporal progression, and differential exclusion."
    ),
}

ALLOWED_REASONING_TYPES = {
    "retrieval",
    "composition",
    "counterexample",
    "temporal",
    "deductive",
    "causal",
    "diagnostic",
    "differential",
}


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _clip_01(value: Any, fallback: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return max(0.0, min(1.0, parsed))


def _coerce_string_list(value: Any, *, max_items: int = 25) -> list[str]:
    if not isinstance(value, list):
        return []
    rows: list[str] = []
    for raw in value:
        text = str(raw).strip()
        if not text:
            continue
        rows.append(text)
    return rows[:max_items]


def _coerce_text_lines(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if not isinstance(value, list):
        return []
    rows: list[str] = []
    for raw in value:
        if isinstance(raw, str):
            text = raw.strip()
            if text:
                rows.append(text)
            continue
        if isinstance(raw, dict):
            text = (
                str(
                    raw.get("utterance")
                    or raw.get("utterance_original")
                    or raw.get("text")
                    or raw.get("content")
                    or ""
                )
                .strip()
            )
            if text:
                rows.append(text)
    return rows


def _normalize_symbol_token(value: Any) -> str:
    text = str(value).strip()
    if len(text) >= 2 and ((text[0] == "'" and text[-1] == "'") or (text[0] == '"' and text[-1] == '"')):
        text = text[1:-1].strip()
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def _extract_utterances_from_payload(payload: dict[str, Any], *, source_json_key: str = "") -> list[str]:
    key = str(source_json_key).strip()
    if key and key in payload:
        rows = _coerce_text_lines(payload.get(key))
        if rows:
            return rows

    for candidate in ("utterances", "story_lines", "input_story_lines"):
        rows = _coerce_text_lines(payload.get(candidate))
        if rows:
            return rows

    turns = payload.get("turns")
    if isinstance(turns, list):
        rows = _coerce_text_lines(turns)
        if rows:
            return rows

    messages = payload.get("messages")
    if isinstance(messages, list):
        rows = _coerce_text_lines(messages)
        if rows:
            return rows

    for candidate in ("source_text", "input_story", "story", "text", "content"):
        maybe = payload.get(candidate)
        if isinstance(maybe, str) and maybe.strip():
            return [maybe.strip()]
    return []


def _resolve_candidate_kb_from_payload(payload: dict[str, Any] | None) -> Path | None:
    if not isinstance(payload, dict):
        return None
    kb_namespace = payload.get("kb_namespace")
    if isinstance(kb_namespace, dict):
        corpus_path = kb_namespace.get("corpus_path")
        if isinstance(corpus_path, str) and corpus_path.strip():
            return Path(corpus_path).resolve()
    corpus_write = payload.get("corpus_write")
    if isinstance(corpus_write, dict):
        path_value = corpus_write.get("path")
        if isinstance(path_value, str) and path_value.strip():
            return Path(path_value).resolve()
    candidate = payload.get("candidate_kb")
    if isinstance(candidate, str) and candidate.strip():
        return Path(candidate).resolve()
    return None


def _load_source_text(
    source_path: Path,
    *,
    source_json_key: str = "",
    through_turn: int = 0,
) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
    metadata: dict[str, Any] = {
        "source_path": str(source_path),
        "source_kind": "text",
        "through_turn": max(0, int(through_turn)),
        "source_json_key": str(source_json_key).strip(),
        "utterance_count": 0,
        "utterance_count_used": 0,
    }

    if source_path.suffix.lower() != ".json":
        raw_text = source_path.read_text(encoding="utf-8-sig")
        metadata["source_kind"] = "text_file"
        return raw_text, metadata, None

    try:
        payload = json.loads(source_path.read_text(encoding="utf-8-sig"))
    except Exception:
        raw_text = source_path.read_text(encoding="utf-8-sig")
        metadata["source_kind"] = "json_unparsed_text_fallback"
        return raw_text, metadata, None

    if not isinstance(payload, dict):
        metadata["source_kind"] = "json_non_object_text_fallback"
        return source_path.read_text(encoding="utf-8-sig"), metadata, None

    utterances = _extract_utterances_from_payload(payload, source_json_key=source_json_key)
    metadata["utterance_count"] = len(utterances)

    through = max(0, int(through_turn))
    if through > 0 and utterances:
        utterances = utterances[:through]
        metadata["source_kind"] = "json_utterance_prefix"
    elif utterances:
        metadata["source_kind"] = "json_utterances"
    metadata["utterance_count_used"] = len(utterances)

    if utterances:
        return "\n".join(utterances), metadata, payload

    raw_text = source_path.read_text(encoding="utf-8-sig")
    metadata["source_kind"] = "json_raw_text_fallback"
    return raw_text, metadata, payload


def _split_top_level(text: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    paren_depth = 0
    bracket_depth = 0
    for ch in text:
        if ch == "(":
            paren_depth += 1
            current.append(ch)
            continue
        if ch == ")":
            paren_depth = max(0, paren_depth - 1)
            current.append(ch)
            continue
        if ch == "[":
            bracket_depth += 1
            current.append(ch)
            continue
        if ch == "]":
            bracket_depth = max(0, bracket_depth - 1)
            current.append(ch)
            continue
        if ch == delimiter and paren_depth == 0 and bracket_depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(ch)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _head_signature(clause: str) -> str:
    text = clause.strip()
    if text.endswith("."):
        text = text[:-1].strip()
    if ":-" in text:
        text = text.split(":-", 1)[0].strip()
    if "(" not in text:
        return f"{text}/0"
    name, args_raw = text.split("(", 1)
    args_text = args_raw[:-1] if args_raw.endswith(")") else args_raw
    arity = len(_split_top_level(args_text, ",")) if args_text.strip() else 0
    return f"{name.strip()}/{arity}"


def _build_runtime_from_kb(kb_path: Path) -> tuple[kp.CorePrologRuntime, list[str], list[dict[str, Any]]]:
    clauses = golden_kb.load_canonical_clauses(kb_path)
    runtime = kp.CorePrologRuntime()
    runtime.empty_kb()
    load_errors: list[dict[str, Any]] = []
    for index, clause in enumerate(clauses, start=1):
        if ":-" in clause:
            result = runtime.assert_rule(clause)
        else:
            result = runtime.assert_fact(clause)
        status = str(result.get("status", "")).strip().lower()
        if status not in {"success", "no_results"}:
            load_errors.append(
                {
                    "index": index,
                    "clause": clause,
                    "status": result.get("status"),
                    "message": result.get("message"),
                    "result": result,
                }
            )
    return runtime, clauses, load_errors


def _call_model_json(
    *,
    backend: str,
    base_url: str,
    model: str,
    prompt: str,
    context_length: int,
    timeout_seconds: int,
    required_keys: list[str],
) -> tuple[dict[str, Any] | None, str]:
    def _one_pass(prompt_text: str) -> tuple[dict[str, Any] | None, str]:
        response = kp._call_model_prompt(
            backend=backend,
            base_url=base_url,
            model=model,
            prompt_text=prompt_text,
            context_length=max(1024, int(context_length)),
            timeout=max(10, int(timeout_seconds)),
            api_key=kp._get_api_key(),
        )
        return kp._parse_model_json(response, required_keys=required_keys)

    parsed, raw = _one_pass(prompt)
    if isinstance(parsed, dict):
        return parsed, raw

    retry_prompt = (
        f"{prompt}\n"
        "The previous reply was invalid. Return ONLY minified JSON with the required keys."
    )
    parsed_retry, raw_retry = _one_pass(retry_prompt)
    if isinstance(parsed_retry, dict):
        return parsed_retry, raw_retry
    if raw_retry and not raw:
        raw = raw_retry
    return parsed_retry, raw


def _build_fact_audit_prompt(*, source_text: str, clauses: list[str]) -> str:
    kb_body = "\n".join(f"- {row}" for row in clauses) if clauses else "(none)"
    return (
        "/no_think\n"
        "You are a strict neuro-symbolic auditor.\n"
        "Compare source text semantics against candidate Prolog KB clauses.\n"
        "Return minified JSON only with keys:\n"
        "coverage_score,precision_score,missed_facts,bogus_facts,uncertain_facts,strengths,weaknesses,summary\n"
        "Rules:\n"
        "- coverage_score and precision_score must be numbers in [0,1]\n"
        "- each *_facts array must contain concise English bullet fragments\n"
        "- strengths and weaknesses must be short arrays\n"
        "- summary <= 45 words\n"
        "- no markdown, no extra keys\n"
        f"Source text:\n{source_text}\n"
        f"Candidate KB clauses:\n{kb_body}\n"
    )


def _normalize_fact_audit(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "status": "parse_error",
            "coverage_score": 0.0,
            "precision_score": 0.0,
            "missed_facts": [],
            "bogus_facts": [],
            "uncertain_facts": [],
            "strengths": [],
            "weaknesses": [],
            "summary": "Fact audit model output could not be parsed.",
        }
    return {
        "status": "ok",
        "coverage_score": round(_clip_01(payload.get("coverage_score"), fallback=0.0), 6),
        "precision_score": round(_clip_01(payload.get("precision_score"), fallback=0.0), 6),
        "missed_facts": _coerce_string_list(payload.get("missed_facts")),
        "bogus_facts": _coerce_string_list(payload.get("bogus_facts")),
        "uncertain_facts": _coerce_string_list(payload.get("uncertain_facts")),
        "strengths": _coerce_string_list(payload.get("strengths"), max_items=12),
        "weaknesses": _coerce_string_list(payload.get("weaknesses"), max_items=12),
        "summary": str(payload.get("summary", "")).strip(),
    }


def _fallback_fact_audit_from_exam(
    *,
    fact_audit: dict[str, Any],
    exam_eval: dict[str, Any],
    load_errors: list[dict[str, Any]],
    clause_count: int,
) -> dict[str, Any]:
    status = str(fact_audit.get("status", "")).strip().lower()
    if status != "parse_error":
        return fact_audit

    question_count = max(1, int(exam_eval.get("question_count", 0) or 0))
    pass_count = max(0, int(exam_eval.get("pass_count", 0) or 0))
    temporal_question_count = max(0, int(exam_eval.get("temporal_question_count", 0) or 0))
    temporal_pass_count = max(0, int(exam_eval.get("temporal_pass_count", 0) or 0))

    pass_rate = pass_count / float(question_count)
    if temporal_question_count > 0:
        temporal_rate = temporal_pass_count / float(temporal_question_count)
        coverage_proxy = (0.6 * pass_rate) + (0.4 * temporal_rate)
    else:
        coverage_proxy = pass_rate

    load_error_ratio = (len(load_errors) / float(max(1, clause_count))) if clause_count > 0 else 0.0
    precision_proxy = max(0.0, pass_rate - min(0.2, load_error_ratio * 2.0))

    return {
        "status": "heuristic_fallback",
        "coverage_score": round(_clip_01(coverage_proxy, fallback=0.0), 6),
        "precision_score": round(_clip_01(precision_proxy, fallback=0.0), 6),
        "missed_facts": _coerce_string_list(fact_audit.get("missed_facts")),
        "bogus_facts": _coerce_string_list(fact_audit.get("bogus_facts")),
        "uncertain_facts": _coerce_string_list(fact_audit.get("uncertain_facts")),
        "strengths": ["Exam-derived fallback used after fact-audit parse failure."],
        "weaknesses": ["Primary fact-audit JSON parsing failed; treat scores as proxy estimates."],
        "summary": "Fact audit parse failed; coverage/precision estimated from exam performance and load errors.",
    }


def _build_exam_prompt(
    *,
    source_text: str,
    clauses: list[str],
    predicate_signatures: list[str],
    question_count: int,
    min_temporal_questions: int,
    exam_style: str,
) -> str:
    kb_body = "\n".join(f"- {row}" for row in clauses) if clauses else "(none)"
    sig_text = ", ".join(predicate_signatures) if predicate_signatures else "(none)"
    style_key = str(exam_style).strip().lower()
    if style_key not in EXAM_STYLE_GUIDANCE:
        style_key = "general"
    style_guidance = EXAM_STYLE_GUIDANCE[style_key]
    return (
        "/no_think\n"
        "You are a logic exam writer for a Prolog KB.\n"
        "Generate query-based exam questions that stress retrieval, composition, and contradiction checks.\n"
        f"Exam style: {style_key}\n"
        f"Style guidance: {style_guidance}\n"
        "Return minified JSON only with keys:\n"
        "questions,notes\n"
        "Question schema per item:\n"
        "id,question,query,expect_status,min_rows,max_rows,contains_row,reasoning_type,temporal,rationale\n"
        "Rules:\n"
        "- questions must be a JSON array\n"
        f"- generate exactly {int(question_count)} questions\n"
        f"- include at least {int(min_temporal_questions)} temporal=true questions when possible\n"
        "- query must be a valid Prolog goal ending with '.'\n"
        "- use expect_status from {success,no_results}\n"
        "- for success checks, set min_rows>=1 unless exact row check is enough\n"
        "- for no_results checks, set max_rows=0\n"
        "- contains_row is either null or an object of expected bindings (string values)\n"
        "- reasoning_type one of {retrieval,composition,counterexample,temporal,deductive,causal,diagnostic,differential}\n"
        "- do not use predicates outside these signatures unless unavoidable\n"
        "- no markdown, no extra top-level keys\n"
        f"Available predicate signatures:\n{sig_text}\n"
        f"Source text:\n{source_text}\n"
        f"Candidate KB clauses:\n{kb_body}\n"
    )


def _goal_signature(goal: str) -> str | None:
    text = _normalize_goal(goal).strip()
    if not text:
        return None
    if "(" not in text:
        return f"{text}/0"
    name, args_raw = text.split("(", 1)
    args_text = args_raw[:-1] if args_raw.endswith(")") else args_raw
    arity = len(_split_top_level(args_text, ",")) if args_text.strip() else 0
    return f"{name.strip()}/{arity}"


def _parse_call_expr(expr: str) -> tuple[str, list[str]] | None:
    text = _normalize_goal(expr).strip()
    if not text:
        return None
    if "(" not in text:
        return text, []
    name, args_raw = text.split("(", 1)
    name = name.strip()
    if not name:
        return None
    args_text = args_raw[:-1] if args_raw.endswith(")") else args_raw
    args = _split_top_level(args_text, ",") if args_text.strip() else []
    return name, [str(arg).strip() for arg in args]


def _fallback_question_candidates(
    predicate_signatures: list[str],
    *,
    clauses: list[str],
    question_count: int,
    temporal_first: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    limit = max(1, int(question_count))
    seen_queries: set[str] = set()

    def _var_name(index: int) -> str:
        base = ["X", "Y", "Z", "U", "V", "W"]
        if index < len(base):
            return base[index]
        return f"V{index+1}"

    def _parse_signature(sig: str) -> tuple[str, int] | None:
        text = str(sig or "").strip().lower()
        if not text or "/" not in text:
            return None
        name, arity_raw = text.rsplit("/", 1)
        name = name.strip()
        if not name:
            return None
        try:
            arity = max(0, int(arity_raw))
        except (TypeError, ValueError):
            return None
        return name, arity

    def add(
        query: str,
        *,
        question: str,
        expect_status: str = "success",
        min_rows: int | None = None,
        max_rows: int | None = None,
        reasoning_type: str = "retrieval",
        temporal: bool = False,
    ) -> None:
        if len(rows) >= limit:
            return
        normalized_query = kp._normalize_clause(query)
        if not normalized_query or normalized_query in seen_queries:
            return
        seen_queries.add(normalized_query)
        rows.append(
            {
                "id": f"q{len(rows)+1:02d}",
                "question": question,
                "query": normalized_query,
                "expect_status": expect_status,
                "min_rows": min_rows if min_rows is not None else (1 if expect_status == "success" else None),
                "max_rows": max_rows if max_rows is not None else (0 if expect_status == "no_results" else None),
                "contains_row": None,
                "reasoning_type": reasoning_type,
                "temporal": temporal,
                "rationale": "fallback generated",
            }
        )

    def _query_variants_from_expr(expr: str, *, temporal: bool) -> list[str]:
        parsed = _parse_call_expr(expr)
        if parsed is None:
            return [f"{expr}."]
        name, args = parsed
        variants: list[str] = []
        seen_variant_queries: set[str] = set()

        def push(query: str) -> None:
            normalized_query = kp._normalize_clause(query)
            if not normalized_query or normalized_query in seen_variant_queries:
                return
            seen_variant_queries.add(normalized_query)
            variants.append(normalized_query)

        base_expr = expr.strip()
        push(f"{base_expr}.")
        push(f"{base_expr}, 1 < 2.")
        if not args:
            push(f"{base_expr}, true.")
            return variants

        vars_raw = [_var_name(i) for i in range(len(args))]
        full_var_expr = f"{name}({', '.join(vars_raw)})"
        bindings = ", ".join(f"{vars_raw[i]} = {args[i]}" for i in range(len(args)))
        push(f"{full_var_expr}, {bindings}.")
        push(f"{full_var_expr}, 1 < 2, {bindings}.")

        for idx, arg in enumerate(args):
            partial_args = list(args)
            partial_args[idx] = vars_raw[idx]
            partial_expr = f"{name}({', '.join(partial_args)})"
            push(f"{partial_expr}, {vars_raw[idx]} = {arg}.")
            push(f"{partial_expr}, 1 < 2, {vars_raw[idx]} = {arg}.")

        if len(args) >= 2:
            push(f"{name}({args[0]}, {vars_raw[1]}), {vars_raw[1]} = {args[1]}.")
            push(f"{name}({vars_raw[0]}, {args[1]}), {vars_raw[0]} = {args[0]}.")

        if temporal and len(args) >= 2:
            push(f"{name}({args[0]}, Event).")
            push(f"{name}(Step, {args[1]}), Step = {args[0]}.")
            push(f"{name}(Step, Event), Step = {args[0]}, Event = {args[1]}.")

        return variants

    temporal_clauses = [clause for clause in clauses if str(clause).strip().startswith("at_step(")]
    plain_clauses = [clause for clause in clauses if not str(clause).strip().startswith("at_step(")]
    ordered_clauses = (temporal_clauses + plain_clauses) if temporal_first else list(clauses)

    for clause in ordered_clauses:
        normalized_clause = kp._normalize_clause(str(clause or "").strip())
        if not normalized_clause:
            continue
        expr = _normalize_goal(normalized_clause)
        if not expr or ":-" in expr:
            continue
        signature = _goal_signature(expr) or ""
        temporal = signature.lower() == "at_step/2" or expr.startswith("at_step(")
        question = (
            f"Does the KB preserve this temporal clause: `{expr}`?"
            if temporal
            else f"Does the KB contain this clause: `{expr}`?"
        )
        reasoning_type = "temporal" if temporal else "retrieval"
        for variant in _query_variants_from_expr(expr, temporal=temporal):
            add(
                variant,
                question=question,
                reasoning_type=reasoning_type,
                temporal=temporal,
            )
            if len(rows) >= limit:
                return rows

    def _query_variants(name: str, arity: int) -> list[str]:
        temporal = name == "at_step"
        if arity == 0:
            return [
                f"{name}.",
                f"{name}, 1 < 2.",
                f"{name}, true.",
            ]
        args = ", ".join(_var_name(i) for i in range(arity))
        base = f"{name}({args})"
        variants = [
            f"{base}.",
            f"{base}, {_var_name(0)} = {_var_name(0)}.",
            f"{base}, 1 < 2.",
        ]
        if arity >= 2:
            variants.append(f"{base}, {_var_name(0)} = {_var_name(0)}, {_var_name(1)} = {_var_name(1)}.")
        if temporal:
            variants.append(f"{base}, 1 < 2, {_var_name(0)} = {_var_name(0)}.")
        return variants

    for sig in predicate_signatures:
        parsed = _parse_signature(sig)
        if parsed is None:
            continue
        name, arity = parsed
        temporal = name == "at_step"
        for query in _query_variants(name, arity):
            add(
                query,
                question=f"Does the KB contain solutions for `{sig}`?",
                reasoning_type="temporal" if temporal else "retrieval",
                temporal=temporal,
            )
            if len(rows) >= limit:
                return rows

    if not rows:
        add("true.", question="Can the runtime answer a trivial query?")

    return rows[:limit]


def _is_simple_constraint_goal(goal: str) -> bool:
    text = _normalize_goal(goal).strip()
    if not text:
        return False
    if "=" in text and ":-" not in text and "==" not in text and "\\=" not in text:
        return True
    if "<" in text and ">" not in text and "=" not in text:
        return True
    return False


def _query_uses_known_signatures(query: str, known_signatures: set[str]) -> bool:
    body = _normalize_goal(kp._normalize_clause(query))
    goals = _split_top_level(body, ",")
    saw_predicate_goal = False
    for goal in goals:
        text = _normalize_goal(goal).strip()
        if not text:
            continue
        if text in {"true", "fail"}:
            continue
        if _is_simple_constraint_goal(text):
            continue
        sig = _goal_signature(text)
        if not sig:
            continue
        saw_predicate_goal = True
        if sig.lower() not in known_signatures:
            return False
    return saw_predicate_goal


def _normalize_question_payload(
    payload: dict[str, Any] | None,
    *,
    fallback_signatures: list[str],
    fallback_clauses: list[str],
    question_count: int,
    min_temporal_questions: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    notes: list[str] = []
    fallback_rows = _fallback_question_candidates(
        fallback_signatures,
        clauses=fallback_clauses,
        question_count=max(question_count * 3, question_count + 8),
    )
    temporal_priority_rows = _fallback_question_candidates(
        fallback_signatures,
        clauses=fallback_clauses,
        question_count=max(question_count * 3, question_count + 8),
        temporal_first=True,
    )
    if not isinstance(payload, dict):
        return fallback_rows[: max(1, int(question_count))], ["exam_parse_error_fallback_used"]

    questions_raw = payload.get("questions", [])
    if not isinstance(questions_raw, list):
        questions_raw = payload.get("exam_questions", [])
    if not isinstance(questions_raw, list):
        questions_raw = []

    known_signatures = {str(sig).strip().lower() for sig in fallback_signatures if str(sig).strip()}
    dropped_invalid_signature = 0
    dropped_rule_queries = 0
    repaired_truthy_contains_row = 0
    repaired_boolean_row_bounds = 0
    normalized: list[dict[str, Any]] = []

    def _query_has_variables(query_text: str) -> bool:
        for token in re.findall(r"\b[_A-Za-z][_A-Za-z0-9]*\b", _normalize_goal(query_text)):
            if _is_variable_token(token):
                return True
        return False

    for idx, row in enumerate(questions_raw, start=1):
        if not isinstance(row, dict):
            continue
        query = kp._normalize_clause(str(row.get("query", "")).strip())
        if not query:
            continue
        if ":-" in query:
            dropped_rule_queries += 1
            continue
        if known_signatures and not _query_uses_known_signatures(query, known_signatures):
            dropped_invalid_signature += 1
            continue
        expect_status = str(row.get("expect_status", "success")).strip().lower() or "success"
        if expect_status not in {"success", "no_results"}:
            expect_status = "success"

        min_rows = row.get("min_rows")
        max_rows = row.get("max_rows")
        try:
            min_rows_value = int(min_rows) if min_rows is not None else None
        except (TypeError, ValueError):
            min_rows_value = None
        try:
            max_rows_value = int(max_rows) if max_rows is not None else None
        except (TypeError, ValueError):
            max_rows_value = None

        if expect_status == "success" and min_rows_value is None:
            min_rows_value = 1
        if expect_status == "no_results" and max_rows_value is None:
            max_rows_value = 0

        contains_row = row.get("contains_row")
        if not isinstance(contains_row, dict):
            contains_row = None
        else:
            contains_row = {str(k): str(v) for k, v in contains_row.items()}
        query_has_variables = _query_has_variables(query)
        if contains_row and not query_has_variables and {str(key).strip().lower() for key in contains_row.keys()} == {"true"}:
            contains_row = None
            repaired_truthy_contains_row += 1

        if expect_status == "success" and not query_has_variables:
            desired_bound = 1
            if min_rows_value is None or min_rows_value != desired_bound:
                min_rows_value = desired_bound
                repaired_boolean_row_bounds += 1
            if max_rows_value is not None and max_rows_value != desired_bound:
                max_rows_value = desired_bound
                repaired_boolean_row_bounds += 1

        question_text = str(row.get("question", "")).strip() or f"Question {idx}"
        reasoning_type = str(row.get("reasoning_type", "")).strip().lower() or "retrieval"
        if reasoning_type not in ALLOWED_REASONING_TYPES:
            reasoning_type = "retrieval"
        temporal = bool(row.get("temporal", False)) or "at_step(" in query

        normalized.append(
            {
                "id": str(row.get("id", f"q{idx:02d}")).strip() or f"q{idx:02d}",
                "question": question_text,
                "query": query,
                "expect_status": expect_status,
                "min_rows": min_rows_value,
                "max_rows": max_rows_value,
                "contains_row": contains_row,
                "reasoning_type": reasoning_type,
                "temporal": temporal,
                "rationale": str(row.get("rationale", "")).strip(),
            }
        )

    if dropped_invalid_signature > 0:
        notes.append(f"exam_model_invalid_signature_dropped:{dropped_invalid_signature}")
    if dropped_rule_queries > 0:
        notes.append(f"exam_model_rule_query_dropped:{dropped_rule_queries}")
    if repaired_truthy_contains_row > 0:
        notes.append(f"exam_model_truthy_contains_row_ignored:{repaired_truthy_contains_row}")
    if repaired_boolean_row_bounds > 0:
        notes.append(f"exam_model_boolean_row_bounds_repaired:{repaired_boolean_row_bounds}")

    if not normalized:
        notes.append("exam_model_returned_no_questions_fallback_used")

    deduped: list[dict[str, Any]] = []
    seen_queries: set[str] = set()
    for row in normalized:
        key = row["query"]
        if key in seen_queries:
            continue
        seen_queries.add(key)
        deduped.append(row)

    if len(deduped) > question_count:
        deduped = deduped[:question_count]

    def _temporal_count(rows: list[dict[str, Any]]) -> int:
        return sum(1 for row in rows if bool(row.get("temporal")))

    def _append_unique_rows(candidates: list[dict[str, Any]], *, temporal_only: bool | None = None) -> int:
        seen_ids = {str(row.get("id", "")).strip() for row in deduped}
        fallback_index = 1
        added = 0
        for row in candidates:
            if temporal_only is not None and bool(row.get("temporal")) != temporal_only:
                continue
            if len(deduped) >= question_count:
                break
            query = str(row.get("query", "")).strip()
            if not query or query in seen_queries:
                continue
            clone = dict(row)
            clone_id = str(clone.get("id", "")).strip()
            if not clone_id or clone_id in seen_ids:
                clone_id = f"fill_q{fallback_index:02d}"
                fallback_index += 1
            clone["id"] = clone_id
            deduped.append(clone)
            seen_queries.add(query)
            seen_ids.add(clone_id)
            added += 1
        return added

    temporal_target = max(0, min(int(question_count), int(min_temporal_questions)))
    if temporal_target > 0 and _temporal_count(deduped) < temporal_target:
        temporal_candidates = [row for row in temporal_priority_rows if bool(row.get("temporal"))]
        if temporal_candidates:
            replaced = 0
            for candidate in temporal_candidates:
                if _temporal_count(deduped) >= temporal_target:
                    break
                query = str(candidate.get("query", "")).strip()
                if not query or query in seen_queries:
                    continue
                replace_index = None
                for idx in range(len(deduped) - 1, -1, -1):
                    if not bool(deduped[idx].get("temporal")):
                        replace_index = idx
                        break
                if replace_index is None:
                    break
                old_query = str(deduped[replace_index].get("query", "")).strip()
                if old_query:
                    seen_queries.discard(old_query)
                deduped[replace_index] = dict(candidate)
                seen_queries.add(query)
                replaced += 1
            appended = _append_unique_rows(temporal_candidates, temporal_only=True)
            if replaced > 0 or appended > 0:
                notes.append(
                    f"exam_temporal_floor_fill_used:{_temporal_count(deduped)}/{int(min_temporal_questions)}"
                )

    if len(deduped) < question_count:
        notes.append("exam_model_returned_fewer_questions_fallback_fill_used")
        _append_unique_rows(fallback_rows)

    if temporal_target > 0 and _temporal_count(deduped) < temporal_target:
        notes.append(
            f"exam_temporal_floor_unmet:{_temporal_count(deduped)}/{int(min_temporal_questions)}"
        )

    return deduped, notes


def _relax_shared_step_temporal_query(query: str) -> str | None:
    normalized = kp._normalize_clause(query)
    body = _normalize_goal(normalized)
    goals = _split_top_level(body, ",")
    if len(goals) < 2:
        return None
    if any(_is_simple_constraint_goal(goal) for goal in goals):
        return None

    shared_step_var = ""
    temporal_indexes: list[int] = []

    for idx, goal in enumerate(goals):
        parsed = _parse_call_expr(goal)
        if parsed is None:
            continue
        name, args = parsed
        if name != "at_step" or len(args) != 2:
            continue
        step_var = str(args[0]).strip()
        if not _is_variable_token(step_var):
            return None
        if not shared_step_var:
            shared_step_var = step_var
        elif step_var != shared_step_var:
            return None
        temporal_indexes.append(idx)

    if len(temporal_indexes) < 2 or not shared_step_var:
        return None

    rewritten_goals: list[str] = []
    temporal_counter = 1
    for goal in goals:
        parsed = _parse_call_expr(goal)
        if parsed is None:
            rewritten_goals.append(str(goal).strip())
            continue
        name, args = parsed
        if name == "at_step" and len(args) == 2 and str(args[0]).strip() == shared_step_var:
            rewritten_goals.append(f"at_step(Step{temporal_counter}, {str(args[1]).strip()})")
            temporal_counter += 1
            continue
        rewritten_goals.append(str(goal).strip())

    repaired = kp._normalize_clause(", ".join(rewritten_goals))
    if repaired and repaired != normalized:
        return repaired
    return None


def _assess_question_result(row: dict[str, Any], result: dict[str, Any]) -> tuple[bool, list[str]]:
    expected_status = str(row.get("expect_status", "success")).strip().lower() or "success"
    observed_status = str(result.get("status", "")).strip().lower()
    num_rows = int(result.get("num_rows", 0) or 0)
    reasons: list[str] = []
    passed = observed_status == expected_status
    if not passed:
        reasons.append(f"Expected status={expected_status}, observed={observed_status}")

    min_rows = row.get("min_rows")
    max_rows = row.get("max_rows")
    if min_rows is not None:
        min_rows_i = int(min_rows)
        if num_rows < min_rows_i:
            passed = False
            reasons.append(f"num_rows {num_rows} < min_rows {min_rows_i}")

    contains_row = row.get("contains_row")
    contains_row_matched = False
    if isinstance(contains_row, dict):
        rows_data = result.get("rows", [])
        if isinstance(rows_data, list):
            for candidate in rows_data:
                if not isinstance(candidate, dict):
                    continue
                candidate_raw = {str(k): str(v) for k, v in candidate.items()}
                candidate_by_norm_key: dict[str, str] = {}
                for key, value in candidate_raw.items():
                    candidate_by_norm_key.setdefault(_normalize_symbol_token(key), value)

                ok = True
                for key, value in contains_row.items():
                    key_raw = str(key)
                    expected_norm = _normalize_symbol_token(value)
                    observed_value: str | None = None

                    if key_raw in candidate_raw:
                        observed_value = candidate_raw.get(key_raw)
                    else:
                        observed_value = candidate_by_norm_key.get(_normalize_symbol_token(key_raw))

                    if observed_value is None:
                        ok = False
                        break
                    if _normalize_symbol_token(observed_value) != expected_norm:
                        ok = False
                        break
                if ok:
                    contains_row_matched = True
                    break
        if not contains_row_matched:
            passed = False
            reasons.append(f"Expected row not found: {contains_row}")

    if max_rows is not None:
        max_rows_i = int(max_rows)
        enforce_max_rows = True
        if isinstance(contains_row, dict) and contains_row_matched and expected_status == "success":
            enforce_max_rows = False
        if enforce_max_rows and num_rows > max_rows_i:
            passed = False
            reasons.append(f"num_rows {num_rows} > max_rows {max_rows_i}")

    return passed, reasons


def _evaluate_questions(runtime: kp.CorePrologRuntime, questions: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated: list[dict[str, Any]] = []
    passed_count = 0
    for row in questions:
        query = str(row.get("query", "")).strip()
        result = _query_rows_with_conjunction_support(runtime, query)
        passed, reasons = _assess_question_result(row, result)
        effective_query = query
        repair_applied: dict[str, Any] | None = None

        if not passed and bool(row.get("temporal")):
            repaired_query = _relax_shared_step_temporal_query(query)
            if repaired_query and repaired_query != query:
                repaired_result = _query_rows_with_conjunction_support(runtime, repaired_query)
                repaired_passed, repaired_reasons = _assess_question_result(row, repaired_result)
                if repaired_passed:
                    result = repaired_result
                    passed = True
                    reasons = []
                    effective_query = repaired_query
                    repair_applied = {
                        "kind": "shared_step_relaxed",
                        "original_query": query,
                        "effective_query": repaired_query,
                    }
                else:
                    reasons.extend(
                        [
                            f"temporal_repair_attempt_failed:{reason}"
                            for reason in repaired_reasons
                            if reason not in reasons
                        ]
                    )

        if passed:
            passed_count += 1

        evaluated.append(
            {
                **row,
                "passed": passed,
                "reasons": reasons,
                "result": result,
                "effective_query": effective_query,
                "repair_applied": repair_applied,
                "answer_preview_rows": (result.get("rows", [])[:3] if isinstance(result.get("rows"), list) else []),
            }
        )

    total = len(evaluated)
    pass_rate = (passed_count / total) if total else 0.0
    temporal_total = sum(1 for row in evaluated if bool(row.get("temporal")))
    temporal_passed = sum(1 for row in evaluated if bool(row.get("temporal")) and bool(row.get("passed")))

    by_type: dict[str, dict[str, int]] = {}
    for row in evaluated:
        key = str(row.get("reasoning_type", "unknown")).strip().lower() or "unknown"
        slot = by_type.setdefault(key, {"total": 0, "passed": 0})
        slot["total"] += 1
        if row.get("passed"):
            slot["passed"] += 1

    return {
        "questions": evaluated,
        "question_count": total,
        "pass_count": passed_count,
        "pass_rate": round(pass_rate, 6),
        "temporal_question_count": temporal_total,
        "temporal_pass_count": temporal_passed,
        "temporal_pass_rate": round((temporal_passed / temporal_total) if temporal_total else 0.0, 6),
        "by_reasoning_type": by_type,
    }


def _is_variable_token(text: str) -> bool:
    token = str(text).strip()
    if not token:
        return False
    if token == "_":
        return True
    return token[0].isupper() or token[0] == "_"


def _normalize_goal(goal: str) -> str:
    text = str(goal).strip()
    if text.endswith("."):
        text = text[:-1].strip()
    return text


def _eval_simple_constraint(rows: list[dict[str, str]], goal: str) -> list[dict[str, str]]:
    text = _normalize_goal(goal)

    # Numeric less-than fast path (for fixed constants only).
    if "<" in text and ">" not in text and "=" not in text:
        left, right = [part.strip() for part in text.split("<", 1)]
        if left.isdigit() and right.isdigit():
            return rows if int(left) < int(right) else []

    # Simple equality constraint, usually X = constant or X = Y.
    if "=" in text and ":-" not in text and "==" not in text and "\\=" not in text:
        left, right = [part.strip() for part in text.split("=", 1)]
        if not left or not right:
            return rows

        left_is_var = _is_variable_token(left)
        right_is_var = _is_variable_token(right)
        constrained: list[dict[str, str]] = []
        for row in rows:
            merged = dict(row)
            left_value = merged.get(left) if left_is_var else left
            right_value = merged.get(right) if right_is_var else right

            if left_is_var and left_value is None and not right_is_var:
                merged[left] = right
                constrained.append(merged)
                continue
            if right_is_var and right_value is None and not left_is_var:
                merged[right] = left
                constrained.append(merged)
                continue
            if left_is_var and right_is_var and left_value is None and right_value is None:
                # Underdetermined equality: keep row unchanged.
                constrained.append(merged)
                continue
            if left_is_var and left_value is None and right_is_var and right_value is not None:
                merged[left] = right_value
                constrained.append(merged)
                continue
            if right_is_var and right_value is None and left_is_var and left_value is not None:
                merged[right] = left_value
                constrained.append(merged)
                continue
            if str(left_value) == str(right_value):
                constrained.append(merged)
        return constrained

    return rows


def _join_rows(left_rows: list[dict[str, str]], right_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    joined: list[dict[str, str]] = []
    seen: set[str] = set()
    for left in left_rows:
        for right in right_rows:
            merged = dict(left)
            compatible = True
            for key, value in right.items():
                existing = merged.get(key)
                if existing is not None and str(existing) != str(value):
                    compatible = False
                    break
                merged[key] = str(value)
            if not compatible:
                continue
            marker = json.dumps(merged, sort_keys=True)
            if marker in seen:
                continue
            seen.add(marker)
            joined.append(merged)
    return joined


def _query_rows_with_conjunction_support(runtime: kp.CorePrologRuntime, query: str) -> dict[str, Any]:
    normalized = kp._normalize_clause(query)
    body = _normalize_goal(normalized)
    goals = _split_top_level(body, ",")
    if len(goals) <= 1:
        return runtime.query_rows(normalized)

    current_rows: list[dict[str, str]] = [{}]
    for goal in goals:
        stripped = _normalize_goal(goal)
        if not stripped:
            continue

        # Constraint goals operate on current row bindings.
        if (
            ("=" in stripped and ":-" not in stripped and "==" not in stripped and "\\=" not in stripped)
            or ("<" in stripped and ">" not in stripped and "=" not in stripped)
        ):
            current_rows = _eval_simple_constraint(current_rows, stripped)
            if not current_rows:
                return {
                    "status": "no_results",
                    "result_type": "no_result",
                    "predicate": body,
                    "prolog_query": normalized,
                    "variables": sorted({k for row in current_rows for k in row.keys()}),
                    "rows": [],
                    "num_rows": 0,
                    "reasoning_basis": {"kind": "core-local-conjunction"},
                }
            continue

        sub_result = runtime.query_rows(kp._normalize_clause(stripped))
        sub_status = str(sub_result.get("status", "")).strip().lower()
        if sub_status == "error":
            return sub_result
        if sub_status != "success":
            return {
                "status": "no_results",
                "result_type": "no_result",
                "predicate": body,
                "prolog_query": normalized,
                "variables": sorted({k for row in current_rows for k in row.keys()}),
                "rows": [],
                "num_rows": 0,
                "reasoning_basis": {"kind": "core-local-conjunction"},
            }
        sub_rows = sub_result.get("rows", [])
        if not isinstance(sub_rows, list):
            sub_rows = []
        prepared_rows: list[dict[str, str]] = []
        for row in sub_rows:
            if isinstance(row, dict):
                prepared_rows.append({str(k): str(v) for k, v in row.items()})
            else:
                prepared_rows.append({})
        if not prepared_rows:
            prepared_rows = [{}]
        current_rows = _join_rows(current_rows, prepared_rows)
        if not current_rows:
            return {
                "status": "no_results",
                "result_type": "no_result",
                "predicate": body,
                "prolog_query": normalized,
                "variables": sorted({k for row in current_rows for k in row.keys()}),
                "rows": [],
                "num_rows": 0,
                "reasoning_basis": {"kind": "core-local-conjunction"},
            }

    variables = sorted({key for row in current_rows for key in row.keys()})
    return {
        "status": "success" if current_rows else "no_results",
        "result_type": "table" if current_rows else "no_result",
        "predicate": body,
        "prolog_query": normalized,
        "variables": variables,
        "rows": current_rows if current_rows else [],
        "num_rows": len(current_rows),
        "reasoning_basis": {"kind": "core-local-conjunction"},
    }


def _emit_exam_scenario(path: Path, questions: list[dict[str, Any]], *, scenario_name: str, ontology_name: str) -> None:
    validations: list[dict[str, Any]] = []
    for idx, row in enumerate(questions, start=1):
        validation: dict[str, Any] = {
            "id": str(row.get("id", f"exam_q{idx:02d}")),
            "query": str(row.get("query", "")).strip(),
            "expect_status": str(row.get("expect_status", "success")),
        }
        if row.get("min_rows") is not None:
            validation["min_rows"] = int(row["min_rows"])
        if row.get("max_rows") is not None:
            validation["max_rows"] = int(row["max_rows"])
        if isinstance(row.get("contains_row"), dict):
            validation["contains_row"] = row["contains_row"]
        validations.append(validation)

    payload = {
        "name": scenario_name,
        "ontology_name": ontology_name,
        "utterances": [
            "Translate this sentence to Spanish: interrogator validation probe only."
        ],
        "validations": validations,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _render_markdown(report: dict[str, Any]) -> str:
    audit = report.get("fact_audit", {})
    exam = report.get("exam", {})
    kb_stats = report.get("kb_stats", {})
    source_meta = report.get("source_metadata", {})
    settings = report.get("settings", {})
    lines: list[str] = []
    lines.append("# KB Interrogator Report")
    lines.append("")
    lines.append(f"- Generated: `{report.get('generated_at_utc', '')}`")
    lines.append(f"- Source text: `{report.get('source_text_file', '')}`")
    lines.append(f"- Source kind: `{source_meta.get('source_kind', 'unknown')}`")
    if int(source_meta.get("utterance_count", 0) or 0) > 0:
        lines.append(
            f"- Source utterances: `{source_meta.get('utterance_count_used', 0)}`/"
            f"`{source_meta.get('utterance_count', 0)}`"
        )
    lines.append(f"- Candidate KB: `{report.get('candidate_kb', '')}`")
    lines.append(f"- Exam style: `{settings.get('exam_style', 'general')}`")
    lines.append("")
    lines.append("## KB Stats")
    lines.append("")
    lines.append(f"- Clause count: `{kb_stats.get('clause_count', 0)}`")
    lines.append(f"- Temporal clauses (`at_step`): `{kb_stats.get('temporal_clause_count', 0)}`")
    lines.append(f"- Plain clauses: `{kb_stats.get('plain_clause_count', 0)}`")
    lines.append(f"- Predicate signatures: `{len(kb_stats.get('predicate_signatures', []))}`")
    lines.append("")
    lines.append("## Fact Audit")
    lines.append("")
    lines.append(f"- Coverage score: `{audit.get('coverage_score', 0.0)}`")
    lines.append(f"- Precision score: `{audit.get('precision_score', 0.0)}`")
    lines.append(f"- Summary: {audit.get('summary', '')}")
    lines.append("")
    lines.append("Missed facts:")
    for row in audit.get("missed_facts", [])[:20]:
        lines.append(f"- {row}")
    if not audit.get("missed_facts"):
        lines.append("- (none)")
    lines.append("")
    lines.append("Bogus facts:")
    for row in audit.get("bogus_facts", [])[:20]:
        lines.append(f"- {row}")
    if not audit.get("bogus_facts"):
        lines.append("- (none)")
    lines.append("")
    lines.append("## Reasoning Exam")
    lines.append("")
    lines.append(
        f"- Pass: `{exam.get('pass_count', 0)}/{exam.get('question_count', 0)}` "
        f"(`{exam.get('pass_rate', 0.0)}`)"
    )
    lines.append(
        f"- Temporal pass: `{exam.get('temporal_pass_count', 0)}/{exam.get('temporal_question_count', 0)}` "
        f"(`{exam.get('temporal_pass_rate', 0.0)}`)"
    )
    lines.append(
        f"- Temporal floor: `{exam.get('temporal_question_count', 0)}`/`{exam.get('temporal_floor_required', 0)}` "
        f"({'met' if bool(exam.get('temporal_floor_met', False)) else 'UNMET'})"
    )
    generation_notes = exam.get("generation_notes", [])
    if isinstance(generation_notes, list) and generation_notes:
        lines.append(f"- Generation notes: `{'; '.join(str(note) for note in generation_notes[:8])}`")
    lines.append("")
    lines.append("| ID | Type | Temporal | Passed | Query |")
    lines.append("|---|---|---:|---:|---|")
    for row in exam.get("questions", []):
        q = str(row.get("query", "")).replace("|", "\\|")
        lines.append(
            f"| `{row.get('id', '')}` | `{row.get('reasoning_type', '')}` | "
            f"{'yes' if row.get('temporal') else 'no'} | "
            f"{'yes' if row.get('passed') else 'no'} | `{q}` |"
        )
    lines.append("")
    lines.append("Failed question notes:")
    failed_rows = [row for row in exam.get("questions", []) if not row.get("passed")]
    if failed_rows:
        for row in failed_rows[:20]:
            lines.append(f"- `{row.get('id', '')}` {row.get('question', '')}")
            for reason in row.get("reasons", []):
                lines.append(f"  - reason: {reason}")
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit KB fidelity and synthesize executable reasoning exams.")
    parser.add_argument("--source-text-file", required=True, help="Source prose path (.txt/.md/.json).")
    parser.add_argument(
        "--candidate-kb",
        default="",
        help="Candidate kb.pl path. Optional when source JSON contains kb_namespace.corpus_path or corpus_write.path.",
    )
    parser.add_argument(
        "--source-json-key",
        default="",
        help="Optional key to extract source utterances/text from JSON files.",
    )
    parser.add_argument(
        "--through-turn",
        type=int,
        default=0,
        help="When source JSON has utterances/turns, keep only first N turns (0 means full source).",
    )
    parser.add_argument("--backend", choices=["ollama", "lmstudio"], default="ollama")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URLS["ollama"])
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--context-length", type=int, default=8192)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--exam-style", choices=["general", "detective", "medical"], default="general")
    parser.add_argument("--source-max-chars", type=int, default=16000)
    parser.add_argument("--kb-max-clauses", type=int, default=300)
    parser.add_argument("--exam-question-count", type=int, default=12)
    parser.add_argument("--exam-min-temporal-questions", type=int, default=3)
    parser.add_argument("--out-json", default="", help="Optional output JSON report path.")
    parser.add_argument("--out-md", default="", help="Optional output Markdown report path.")
    parser.add_argument("--emit-exam-scenario", default="", help="Optional path to emit exam scenario JSON.")
    parser.add_argument("--scenario-name", default="kb_interrogator_exam")
    parser.add_argument("--ontology-name", default="kb_interrogator_exam")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    source_path = Path(args.source_text_file).resolve()
    if not source_path.exists():
        print(f"Source text file not found: {source_path}")
        return 2

    source_text, source_metadata, source_payload = _load_source_text(
        source_path,
        source_json_key=str(args.source_json_key),
        through_turn=int(args.through_turn),
    )
    if int(args.source_max_chars) > 0 and len(source_text) > int(args.source_max_chars):
        source_text = source_text[: int(args.source_max_chars)]

    kb_path: Path | None = None
    if str(args.candidate_kb).strip():
        kb_path = Path(args.candidate_kb).resolve()
    else:
        kb_path = _resolve_candidate_kb_from_payload(source_payload)

    if kb_path is None:
        print(
            "Candidate KB path is required. Provide --candidate-kb or a source JSON "
            "that includes kb_namespace.corpus_path/corpus_write.path."
        )
        return 2
    if not kb_path.exists():
        print(f"Candidate KB not found: {kb_path}")
        return 2

    runtime, clauses, load_errors = _build_runtime_from_kb(kb_path)
    if int(args.kb_max_clauses) > 0 and len(clauses) > int(args.kb_max_clauses):
        clauses_for_model = clauses[-int(args.kb_max_clauses) :]
    else:
        clauses_for_model = clauses

    predicate_signatures = sorted({_head_signature(clause) for clause in clauses if clause.strip()})
    temporal_clause_count = sum(1 for clause in clauses if clause.startswith("at_step("))
    plain_clause_count = len(clauses) - temporal_clause_count
    temporal_expected = max(0, int(args.exam_min_temporal_questions))
    if temporal_clause_count == 0:
        temporal_expected = 0

    audit_prompt = _build_fact_audit_prompt(source_text=source_text, clauses=clauses_for_model)
    audit_raw, audit_raw_json = _call_model_json(
        backend=args.backend,
        base_url=args.base_url,
        model=args.model,
        prompt=audit_prompt,
        context_length=int(args.context_length),
        timeout_seconds=int(args.timeout_seconds),
        required_keys=["coverage_score", "precision_score"],
    )
    fact_audit = _normalize_fact_audit(audit_raw)

    exam_prompt = _build_exam_prompt(
        source_text=source_text,
        clauses=clauses_for_model,
        predicate_signatures=predicate_signatures,
        question_count=int(args.exam_question_count),
        min_temporal_questions=temporal_expected,
        exam_style=str(args.exam_style),
    )
    exam_raw, exam_raw_json = _call_model_json(
        backend=args.backend,
        base_url=args.base_url,
        model=args.model,
        prompt=exam_prompt,
        context_length=int(args.context_length),
        timeout_seconds=int(args.timeout_seconds),
        required_keys=["questions"],
    )
    questions, exam_notes = _normalize_question_payload(
        exam_raw,
        fallback_signatures=predicate_signatures,
        fallback_clauses=clauses_for_model,
        question_count=int(args.exam_question_count),
        min_temporal_questions=temporal_expected,
    )
    exam_eval = _evaluate_questions(runtime, questions)
    exam_eval["generation_notes"] = exam_notes
    exam_eval["temporal_floor_required"] = int(temporal_expected)
    exam_eval["temporal_floor_met"] = (
        int(exam_eval.get("temporal_question_count", 0) or 0) >= int(temporal_expected)
        if int(temporal_expected) > 0
        else True
    )
    exam_eval["temporal_floor_shortfall"] = max(
        0,
        int(temporal_expected) - int(exam_eval.get("temporal_question_count", 0) or 0),
    )
    fact_audit = _fallback_fact_audit_from_exam(
        fact_audit=fact_audit,
        exam_eval=exam_eval,
        load_errors=load_errors,
        clause_count=len(clauses),
    )

    report: dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "source_text_file": str(source_path),
        "source_metadata": source_metadata,
        "candidate_kb": str(kb_path),
        "settings": {
            "backend": args.backend,
            "base_url": args.base_url,
            "model": args.model,
            "exam_style": args.exam_style,
            "context_length": int(args.context_length),
            "timeout_seconds": int(args.timeout_seconds),
            "source_max_chars": int(args.source_max_chars),
            "source_json_key": str(args.source_json_key),
            "through_turn": int(args.through_turn),
            "kb_max_clauses": int(args.kb_max_clauses),
            "exam_question_count": int(args.exam_question_count),
            "exam_min_temporal_questions": int(args.exam_min_temporal_questions),
        },
        "kb_stats": {
            "clause_count": len(clauses),
            "temporal_clause_count": temporal_clause_count,
            "plain_clause_count": plain_clause_count,
            "predicate_signatures": predicate_signatures,
            "load_errors": load_errors,
        },
        "fact_audit": {
            **fact_audit,
            "raw_model_json": audit_raw_json,
        },
        "exam": {
            **exam_eval,
            "raw_model_json": exam_raw_json,
        },
    }

    if args.emit_exam_scenario:
        scenario_path = Path(args.emit_exam_scenario).resolve()
        _emit_exam_scenario(
            scenario_path,
            questions,
            scenario_name=str(args.scenario_name).strip() or "kb_interrogator_exam",
            ontology_name=str(args.ontology_name).strip() or "kb_interrogator_exam",
        )
        report["exam"]["scenario_path"] = str(scenario_path)

    out_json = Path(args.out_json).resolve() if args.out_json else Path.cwd() / "kb_interrogator_report.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    out_md: Path | None = Path(args.out_md).resolve() if args.out_md else None
    if out_md is not None:
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(_render_markdown(report), encoding="utf-8")

    print(
        "Interrogator summary: "
        f"source={source_metadata.get('source_kind', 'unknown')} "
        f"clauses={len(clauses)} "
        f"audit(coverage={fact_audit['coverage_score']:.3f},precision={fact_audit['precision_score']:.3f}) "
        f"exam(pass={exam_eval['pass_count']}/{exam_eval['question_count']},"
        f"temporal={exam_eval['temporal_pass_count']}/{exam_eval['temporal_question_count']},"
        f"style={str(args.exam_style).strip().lower() or 'general'})"
    )
    print(f"JSON report: {out_json}")
    if out_md is not None:
        print(f"Markdown report: {out_md}")
    if args.emit_exam_scenario:
        print(f"Exam scenario: {Path(args.emit_exam_scenario).resolve()}")
    if not bool(exam_eval.get("temporal_floor_met", True)):
        print(
            "[kb-interrogator] warning: temporal question floor unmet "
            f"({int(exam_eval.get('temporal_question_count', 0) or 0)}/"
            f"{int(exam_eval.get('temporal_floor_required', 0) or 0)})",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
