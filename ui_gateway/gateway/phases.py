from __future__ import annotations

import re
import time
from typing import Any

from gateway.runtime_hooks import RuntimeHooks
from gateway.session_store import SessionState


def _phase(name: str, status: str, summary: str, data: dict) -> dict:
    return {
        "phase": name,
        "status": status,
        "summary": summary,
        "data": data,
    }


MAX_STORY_SEGMENTS = 80
MIN_STORY_SEGMENTS = 4
MIN_STORY_CHARS = 700
MAX_QUERY_BOUNDARY_SEGMENTS = 24
MIN_QUERY_BOUNDARY_CHARS = 80


def _strip_markdown_noise(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def _split_story_segments(utterance: str) -> list[str]:
    text = str(utterance or "").strip()
    if not text:
        return []
    lines = _strip_markdown_noise(text)
    if len(lines) >= MIN_STORY_SEGMENTS:
        return lines[:MAX_STORY_SEGMENTS]
    sentence_segments = [
        segment.strip()
        for segment in re.split(r"(?<=[.!?])\s+", text)
        if segment.strip()
    ]
    if len(sentence_segments) >= MIN_STORY_SEGMENTS:
        return sentence_segments[:MAX_STORY_SEGMENTS]
    return []


def _split_sentence_segments(text: str, *, limit: int) -> list[str]:
    return [
        segment.strip()
        for segment in re.split(r"(?<=[.!?])\s+", str(text or "").strip())
        if segment.strip()
    ][:limit]


def _split_query_boundary_segments(utterance: str) -> list[str]:
    text = str(utterance or "").strip()
    if not text or "?" not in text:
        return []
    segments = _split_sentence_segments(text, limit=MAX_QUERY_BOUNDARY_SEGMENTS)
    if len(segments) < 2:
        return []
    query_indexes = [index for index, segment in enumerate(segments) if "?" in segment]
    if not query_indexes:
        return []
    # A final single query can stay as one workspace; the useful boundary is a
    # question that has setup before it, follow-up text after it, or siblings.
    if len(segments) == 1 or (len(query_indexes) == 1 and query_indexes[0] == len(segments) - 1 and len(text) < MIN_QUERY_BOUNDARY_CHARS):
        return []
    return segments


def _should_segment_story(utterance: str, config: dict) -> bool:
    if not bool(config.get("semantic_ir_enabled", False)):
        return False
    text = str(utterance or "").strip()
    if len(text) < MIN_STORY_CHARS:
        return False
    segments = _split_story_segments(text)
    if len(segments) < MIN_STORY_SEGMENTS:
        return False
    lowered = f" {text.lower()} "
    if text.count("?") >= max(2, len(segments) // 2):
        return False
    return any(
        marker in lowered
        for marker in (
            " once upon a time ",
            " goldilocks ",
            " there were ",
            " returned home",
            " had ",
            " was ",
            " were ",
        )
    )


def _should_segment_query_boundaries(utterance: str, config: dict) -> bool:
    if not bool(config.get("semantic_ir_enabled", False)):
        return False
    text = str(utterance or "").strip()
    if len(text) < MIN_QUERY_BOUNDARY_CHARS:
        return False
    segments = _split_query_boundary_segments(text)
    if len(segments) < 2:
        return False
    return True


def _semantic_ir_layers(compiler_trace: dict | None) -> tuple[dict, dict, dict]:
    if not isinstance(compiler_trace, dict):
        return {}, {}, {}
    parse = compiler_trace.get("parse") if isinstance(compiler_trace.get("parse"), dict) else {}
    prethink = compiler_trace.get("prethink") if isinstance(compiler_trace.get("prethink"), dict) else {}
    parse_semantic = parse.get("semantic_ir") if isinstance(parse.get("semantic_ir"), dict) else {}
    prethink_semantic = prethink.get("semantic_ir") if isinstance(prethink.get("semantic_ir"), dict) else {}
    semantic = parse_semantic if isinstance(parse_semantic.get("parsed"), dict) else prethink_semantic
    ir = semantic.get("parsed") if isinstance(semantic.get("parsed"), dict) else {}
    admission = {}
    normalized = parse.get("normalized") if isinstance(parse.get("normalized"), dict) else {}
    if isinstance(normalized.get("admission_diagnostics"), dict):
        admission = normalized["admission_diagnostics"]
    if not admission:
        for rescue in parse.get("rescues", []) if isinstance(parse.get("rescues"), list) else []:
            if isinstance(rescue, dict) and isinstance(rescue.get("admission_diagnostics"), dict):
                admission = rescue["admission_diagnostics"]
                break
    return semantic, ir, admission


def _append_semantic_ir_phases(phases: list[dict], compiler_trace: dict | None) -> None:
    semantic, ir, admission = _semantic_ir_layers(compiler_trace)
    if not ir:
        return

    decision = str(ir.get("decision", "")).strip() or "unknown"
    turn_type = str(ir.get("turn_type", "")).strip() or "unknown"
    model = str(semantic.get("model", "")).strip() or "semantic_ir_v1"
    risk = str(((ir.get("self_check") or {}).get("bad_commit_risk", ""))).strip()
    questions = ir.get("clarification_questions") if isinstance(ir.get("clarification_questions"), list) else []
    phases.append(
        _phase(
            "workspace",
            decision,
            f"Semantic IR workspace proposed {decision}/{turn_type} with {model}.",
            {
                "model": model,
                "backend": semantic.get("backend", ""),
                "latency_ms": semantic.get("latency_ms", 0),
                "decision": decision,
                "turn_type": turn_type,
                "bad_commit_risk": risk,
                "clarification_questions": questions,
                "entities": ir.get("entities", []),
                "referents": ir.get("referents", []),
                "assertions": ir.get("assertions", []),
                "unsafe_implications": ir.get("unsafe_implications", []),
                "candidate_operations": ir.get("candidate_operations", []),
                "self_check": ir.get("self_check", {}),
            },
        )
    )


def _operation_clause_text(op: dict) -> str:
    if not isinstance(op, dict):
        return ""
    result = op.get("result") if isinstance(op.get("result"), dict) else {}
    return str(
        result.get("fact")
        or result.get("rule")
        or result.get("query")
        or result.get("prolog_query")
        or op.get("clause")
        or op.get("query")
        or ""
    ).strip()


def _segment_admission_counts(trace: dict | None) -> tuple[int, int, str]:
    _semantic, ir, admission = _semantic_ir_layers(trace)
    admitted = 0
    skipped = 0
    if admission:
        try:
            admitted = int(admission.get("admitted_count", 0) or 0)
            skipped = int(admission.get("skipped_count", 0) or 0)
        except Exception:
            admitted = 0
            skipped = 0
    decision = str(ir.get("decision", "")).strip() if isinstance(ir, dict) else ""
    return admitted, skipped, decision


def _process_segmented_story(
    *,
    utterance: str,
    session: SessionState,
    config: dict,
    runtime: RuntimeHooks,
    started_at: float,
) -> dict:
    segments = _split_story_segments(utterance)
    return _process_segmented_utterance(
        utterance=utterance,
        segments=segments,
        session=session,
        config=config,
        runtime=runtime,
        started_at=started_at,
        strategy="line_or_sentence_semantic_ir_ingestion",
        trace_key="segmented_story",
        ingest_summary=f"Long narrative split into {len(segments)} focused Semantic IR segment(s).",
        workspace_summary=f"Processed {len(segments)} semantic workspace proposal(s) instead of one summary-shaped proposal.",
        commit_summary="Deterministic commit attempted for all story segments.",
        answer_prefix="Segmented story ingestion complete",
        route_name="segmented_semantic_ir",
    )


def _process_segmented_query_boundaries(
    *,
    utterance: str,
    session: SessionState,
    config: dict,
    runtime: RuntimeHooks,
    started_at: float,
) -> dict:
    segments = _split_query_boundary_segments(utterance)
    return _process_segmented_utterance(
        utterance=utterance,
        segments=segments,
        session=session,
        config=config,
        runtime=runtime,
        started_at=started_at,
        strategy="query_boundary_semantic_ir_ingestion",
        trace_key="segmented_query_boundaries",
        ingest_summary=f"Mixed turn split at query boundaries into {len(segments)} focused Semantic IR segment(s).",
        workspace_summary=f"Processed {len(segments)} focused workspace proposal(s) so queries do not pile up with writes.",
        commit_summary="Deterministic execution attempted for each query-boundary segment.",
        answer_prefix="Segmented query-boundary ingestion complete",
        route_name="query_boundary_semantic_ir",
    )


def _process_segmented_utterance(
    *,
    utterance: str,
    segments: list[str],
    session: SessionState,
    config: dict,
    runtime: RuntimeHooks,
    started_at: float,
    strategy: str,
    trace_key: str,
    ingest_summary: str,
    workspace_summary: str,
    commit_summary: str,
    answer_prefix: str,
    route_name: str,
) -> dict:
    operations: list[dict] = []
    segment_records: list[dict] = []
    clauses_seen: set[str] = set()
    held_count = 0
    error_count = 0
    admitted_total = 0
    skipped_total = 0
    query_count = 0

    for index, segment in enumerate(segments, start=1):
        result = runtime.process_utterance(
            utterance=segment,
            config=config,
            session={
                "session_id": session.session_id,
                "turns": session.turns,
                "pending_clarification": None,
            },
        )
        trace = result.get("compiler_trace") if isinstance(result.get("compiler_trace"), dict) else {}
        admitted, skipped, decision = _segment_admission_counts(trace)
        admitted_total += admitted
        skipped_total += skipped
        front_door = result.get("front_door") if isinstance(result.get("front_door"), dict) else {}
        execution = result.get("execution") if isinstance(result.get("execution"), dict) else {}
        status = str(result.get("status", "")).strip()
        execution_status = str(execution.get("status", "")).strip()

        if status == "clarification_required":
            held_count += 1
            if hasattr(runtime, "clear_pending_prethink"):
                runtime.clear_pending_prethink(config=config)
        elif execution_status and execution_status != "success":
            error_count += 1

        segment_ops = execution.get("operations") if isinstance(execution.get("operations"), list) else []
        if not segment_ops and execution_status == "success":
            parse_trace = trace.get("parse") if isinstance(trace.get("parse"), dict) else {}
            normalized = (
                parse_trace.get("normalized")
                if isinstance(parse_trace.get("normalized"), dict)
                else {}
            )
            synthesized_ops: list[dict] = []
            for fact in normalized.get("facts", []) if isinstance(normalized.get("facts"), list) else []:
                clause = str(fact).strip()
                if clause:
                    synthesized_ops.append({"tool": "assert_fact", "result": {"status": "success", "fact": clause}})
            for rule in normalized.get("rules", []) if isinstance(normalized.get("rules"), list) else []:
                clause = str(rule).strip()
                if clause:
                    synthesized_ops.append({"tool": "assert_rule", "result": {"status": "success", "rule": clause}})
            for query in normalized.get("queries", []) if isinstance(normalized.get("queries"), list) else []:
                clause = str(query).strip()
                if clause:
                    synthesized_ops.append({"tool": "query_rows", "result": {"status": "success", "query": clause}})
            segment_ops = synthesized_ops
        new_operation_count = 0
        for op in segment_ops:
            if not isinstance(op, dict):
                continue
            clause = _operation_clause_text(op)
            tool = str(op.get("tool", "")).strip()
            result_obj = op.get("result") if isinstance(op.get("result"), dict) else {}
            op_status = str(result_obj.get("status") or op.get("status") or execution_status or "").strip()
            if tool in {"assert_fact", "assert_rule"} and op_status == "success" and clause:
                if clause in clauses_seen:
                    continue
                clauses_seen.add(clause)
            if tool == "query_rows":
                query_count += 1
            operations.append(op)
            new_operation_count += 1
        segment_records.append(
            {
                "index": index,
                "utterance": segment,
                "status": status,
                "route": str(front_door.get("route", "")).strip(),
                "decision": decision,
                "admitted_count": admitted,
                "skipped_count": skipped,
                "writes_applied": int(execution.get("writes_applied", 0) or 0),
                "operation_count": new_operation_count,
                "clarification_question": str(front_door.get("clarification_question", "")).strip(),
                "errors": list(execution.get("errors", [])) if isinstance(execution.get("errors"), list) else [],
                "trace": trace,
            }
        )

    deduped_operations: list[dict] = []
    final_seen_clauses: set[str] = set()
    for op in operations:
        tool = str(op.get("tool", "")).strip() if isinstance(op, dict) else ""
        clause = _operation_clause_text(op)
        if tool in {"assert_fact", "assert_rule"} and clause:
            if clause in final_seen_clauses:
                continue
            final_seen_clauses.add(clause)
        deduped_operations.append(op)
    operations = deduped_operations

    writes_applied = sum(
        1
        for op in operations
        if isinstance(op, dict)
        and str(op.get("tool", "")).strip() in {"assert_fact", "assert_rule", "retract_fact"}
    )
    query_count = query_count or sum(
        1
        for op in operations
        if isinstance(op, dict) and str(op.get("tool", "")).strip() == "query_rows"
    )

    execution = {
        "status": "success" if (writes_applied > 0 or query_count > 0) else ("error" if error_count else "no_results"),
        "intent": "assert_fact" if writes_applied > 0 else "other",
        "writes_applied": writes_applied,
        "operations": operations,
        "query_result": None,
        "parse": {
            "intent": "assert_fact" if writes_applied > 0 else "other",
            "facts": [
                _operation_clause_text(op)
                for op in operations
                if isinstance(op, dict) and str(op.get("tool", "")).strip() == "assert_fact"
            ],
        },
        "errors": [
            f"{held_count} segment(s) held for clarification.",
            f"{error_count} segment(s) had execution errors.",
        ]
        if held_count or error_count
        else [],
    }
    route = "write" if writes_applied > 0 else ("query" if query_count > 0 else "other")
    phases = [
        _phase(
            "ingest",
            "segmented",
            ingest_summary,
            {
                "front_door_uri": config["front_door_uri"],
                "segment_count": len(segments),
                "strategy": strategy,
            },
        ),
        _phase(
            "workspace",
            "segmented",
            workspace_summary,
            {
                "segment_count": len(segments),
                "admitted_count": admitted_total,
                "skipped_count": skipped_total,
                "held_count": held_count,
                "error_count": error_count,
                "query_count": query_count,
                "segments": [
                    {key: value for key, value in record.items() if key != "trace"}
                    for record in segment_records
                ],
            },
        ),
        _phase(
            "admission",
            "ok" if writes_applied else "empty",
            f"Segmented admission produced {writes_applied} applied mutation(s).",
            {
                "admitted_count": admitted_total,
                "skipped_count": skipped_total,
                "writes_applied": writes_applied,
                "query_count": query_count,
            },
        ),
        _phase(
            "clarify",
            "partial" if held_count else "skipped",
            "Some segments held for clarification." if held_count else "No segment-level clarification is pending.",
            {"held_count": held_count},
        ),
        _phase(
            "commit",
            "applied" if writes_applied else ("queried" if query_count else "skipped"),
            commit_summary,
            execution,
        ),
    ]
    answer = {
        "speaker": "prethink-gateway",
        "text": (
            f"{answer_prefix}: {writes_applied} mutation(s) applied "
            f"and {query_count} query operation(s) executed "
            f"across {len(segments)} segment(s)."
            + (f" {held_count} segment(s) held for clarification." if held_count else "")
        ),
        "mode": "answer",
    }
    phases.append(_phase("answer", "ok", "Prepared final response envelope.", answer))
    trace = {
        trace_key: {
            "strategy": strategy,
            "segment_count": len(segments),
            "admitted_count": admitted_total,
            "skipped_count": skipped_total,
            "writes_applied": writes_applied,
            "query_count": query_count,
            "held_count": held_count,
            "error_count": error_count,
            "segments": segment_records,
        },
        "summary": {
            "overall": (
                f"{trace_key}={len(segments)} segments; "
                f"writes={writes_applied}; queries={query_count}; held={held_count}; errors={error_count}"
            ),
            "prethink_source": route_name,
        },
    }
    turn = {
        "turn_index": len(session.turns) + 1,
        "timestamp": started_at,
        "utterance": utterance,
        "route": route,
        "phases": phases,
        "assistant": answer,
        "trace": trace,
    }
    session.turns.append(turn)
    session.pending_clarification = None
    return {
        "status": "ok",
        "front_door_uri": config["front_door_uri"],
        "session_id": session.session_id,
        "turn": turn,
        "pending_clarification": None,
    }

    if not admission:
        phases.append(
            _phase(
                "admission",
                "not_reached",
                "Deterministic mapper has not run yet for this held turn.",
                {"reason": "prethink_only_semantic_workspace"},
            )
        )
        return

    operations = admission.get("operations") if isinstance(admission.get("operations"), list) else []
    admitted_count = int(admission.get("admitted_count", 0) or 0)
    skipped_count = int(admission.get("skipped_count", 0) or 0)
    if not (admitted_count or skipped_count) and operations:
        admitted_count = sum(1 for op in operations if isinstance(op, dict) and bool(op.get("admitted")))
        skipped_count = len(operations) - admitted_count
    phases.append(
        _phase(
            "admission",
            "ok" if admitted_count else ("held" if skipped_count or decision in {"clarify", "quarantine", "reject"} else "empty"),
            f"Deterministic mapper admitted {admitted_count} operation(s) and skipped {skipped_count}.",
            admission if isinstance(admission, dict) else {},
        )
    )


def process_turn(
    utterance: str,
    session: SessionState,
    config: dict,
    runtime: RuntimeHooks,
    config_store: Any | None = None,
) -> dict:
    started_at = time.time()
    phases: list[dict] = []
    execution: dict | None = None
    clarification: dict | None = None
    compiler_trace: dict | None = None
    route = "other"

    slash_result = _handle_slash_command(
        utterance=utterance,
        session=session,
        config=config,
        runtime=runtime,
        config_store=config_store,
    )
    if slash_result is not None:
        phases.append(
            _phase(
                "ingest",
                "ok",
                "Slash command accepted.",
                {
                    "front_door_uri": config["front_door_uri"],
                    "command": slash_result["command"],
                },
            )
        )
        phases.append(
            _phase(
                "clarify",
                "skipped",
                "Slash command bypassed clarification gate.",
                {"reason": "operator_command"},
            )
        )
        phases.append(
            _phase(
                "commit",
                "skipped",
                "Slash command bypassed deterministic commit pipeline.",
                {"reason": "operator_command"},
            )
        )
        phases.append(
            _phase(
                "answer",
                "ok",
                "Prepared slash command response.",
                slash_result["answer"],
            )
        )

        turn = {
            "turn_index": len(session.turns) + 1,
            "timestamp": started_at,
            "utterance": utterance,
            "route": "command",
            "phases": phases,
            "assistant": slash_result["answer"],
            "trace": None,
        }
        session.turns.append(turn)
        return {
            "status": "ok",
            "front_door_uri": config["front_door_uri"],
            "session_id": session.session_id,
            "turn": turn,
            "pending_clarification": session.pending_clarification,
        }

    if not session.pending_clarification and _should_segment_story(utterance, config):
        return _process_segmented_story(
            utterance=utterance,
            session=session,
            config=config,
            runtime=runtime,
            started_at=started_at,
        )

    if not session.pending_clarification and _should_segment_query_boundaries(utterance, config):
        return _process_segmented_query_boundaries(
            utterance=utterance,
            session=session,
            config=config,
            runtime=runtime,
            started_at=started_at,
        )

    if session.pending_clarification:
        pending = session.pending_clarification
        lowered = utterance.strip().lower()
        phases.append(
            _phase(
                "ingest",
                "ok",
                "Received clarification follow-up.",
                {
                    "front_door_uri": config["front_door_uri"],
                    "pending_question": pending["question"],
                    "original_utterance": pending["original_utterance"],
                },
            )
        )
        if lowered in {"no", "cancel", "stop"}:
            phases.append(
                _phase(
                    "clarify",
                    "cancelled",
                    "User cancelled the staged write.",
                    {"resolution": "cancelled"},
                )
            )
            phases.append(
                _phase(
                    "commit",
                    "skipped",
                    "No commit produced after cancellation.",
                    {"reason": "user_cancelled"},
                )
            )
            execution = {
                "status": "error",
                "intent": "other",
                "errors": ["User cancelled staged write."],
            }
            route = "write"
            session.pending_clarification = None
        else:
            resolution = "confirmed" if lowered in {"yes", "y", "confirm", "go ahead", "commit it"} else "reframed"
            phases.append(
                _phase(
                    "clarify",
                    "resolved",
                    f"Clarification resolved via {resolution}.",
                    {
                        "resolution": resolution,
                        "follow_up": utterance,
                    },
                )
            )
            process_result = runtime.process_utterance(
                utterance=str(pending.get("original_utterance", "")).strip(),
                config=config,
                session={
                    "session_id": session.session_id,
                    "turns": session.turns,
                    "pending_clarification": session.pending_clarification,
                },
                clarification_answer=utterance,
                prethink_id=str(pending.get("prethink_id", "")).strip(),
            )
            compiler_trace = (
                process_result.get("compiler_trace")
                if isinstance(process_result.get("compiler_trace"), dict)
                else None
            )
            front_door = process_result.get("front_door") if isinstance(process_result.get("front_door"), dict) else {}
            route = str(front_door.get("route", "other")).strip() or "other"
            execution = process_result.get("execution") if isinstance(process_result.get("execution"), dict) else {
                "status": "error",
                "intent": "other",
                "errors": [str(process_result.get("message", "utterance processing failed")).strip() or "utterance processing failed"],
            }
            _append_semantic_ir_phases(phases, compiler_trace)
            phases.append(
                _phase(
                    "commit",
                    "applied" if str(execution.get("status", "")).strip() == "success" else "failed",
                    "Deterministic execution completed after clarification."
                    if str(execution.get("status", "")).strip() == "success"
                    else "Deterministic execution failed after clarification.",
                    execution,
                )
            )
            if str(execution.get("status", "")).strip() == "success":
                session.pending_clarification = None
    else:
        process_result = runtime.process_utterance(
            utterance=utterance,
            config=config,
            session={
                "session_id": session.session_id,
                "turns": session.turns,
                "pending_clarification": session.pending_clarification,
            },
        )
        compiler_trace = (
            process_result.get("compiler_trace")
            if isinstance(process_result.get("compiler_trace"), dict)
            else None
        )
        front_door = process_result.get("front_door") if isinstance(process_result.get("front_door"), dict) else {
            "route": "other",
            "reasons": [str(process_result.get("message", "utterance processing failed")).strip() or "utterance processing failed"],
            "clarification_question": "",
            "needs_clarification": False,
        }
        route = front_door["route"]
        phases.append(
            _phase(
                "ingest",
                "ok",
                "prethink:// front door classified the utterance.",
                front_door,
            )
        )
        _append_semantic_ir_phases(phases, compiler_trace)
        if str(process_result.get("status", "")).strip() == "clarification_required" and front_door["needs_clarification"]:
            if runtime.should_handoff_instead_of_clarify(route=route, config=config):
                phases.append(
                    _phase(
                        "clarify",
                        "skipped",
                        "Clarification suppressed; forwarding the turn to the served assistant.",
                        {
                            "reason": "served_handoff_instead_of_clarify",
                            "served_handoff_mode": str(config.get("served_handoff_mode", "")).strip(),
                        },
                    )
                )
                execution = {
                    "status": "success",
                    "intent": str(front_door.get("compiler_intent", "other")).strip() or "other",
                    "writes_applied": 0,
                    "operations": [],
                    "query_result": None,
                    "parse": {},
                    "errors": [],
                }
                phases.append(
                    _phase(
                        "commit",
                        "skipped",
                        "Deterministic commit skipped; unresolved turn will be handled by served LLM.",
                        {"reason": "served_handoff_instead_of_clarify"},
                    )
                )
            else:
                question = _clarification_question(front_door, utterance)
                clarification = {
                    "question": question,
                    "reasons": front_door["reasons"],
                }
                phases.append(
                    _phase(
                        "clarify",
                        "required",
                        "Strict gateway is holding the turn for clarification.",
                        clarification,
                    )
                )
                phases.append(
                    _phase(
                        "commit",
                        "blocked",
                        "Commit blocked until clarification resolves.",
                        {"reason": "needs_clarification"},
                    )
                )
                session.pending_clarification = {
                    "question": question,
                    "original_utterance": utterance,
                    "front_door": front_door,
                    "prethink_id": str(front_door.get("prethink_id", "")).strip(),
                }
        else:
            phases.append(
                _phase(
                    "clarify",
                    "skipped",
                    "No clarification needed for this turn.",
                    {"reason": "confidence_above_threshold"},
                )
            )
            execution = process_result.get("execution") if isinstance(process_result.get("execution"), dict) else {
                "status": "error",
                "intent": str(front_door.get("compiler_intent", "other")).strip() or "other",
                "errors": [str(process_result.get("message", "utterance processing failed")).strip() or "utterance processing failed"],
            }
            if route == "write":
                phases.append(
                    _phase(
                        "commit",
                        "applied" if str(execution.get("status", "")).strip() == "success" else "failed",
                        "Deterministic commit attempted."
                        if str(execution.get("status", "")).strip() == "success"
                        else "Deterministic commit failed.",
                        execution,
                    )
                )
            else:
                phases.append(
                    _phase(
                        "commit",
                        "skipped",
                        "No mutation commit needed for this route; deterministic query/no-op executed.",
                        execution,
                    )
                )

    answer = runtime.answer(
        utterance=utterance,
        route=route,
        execution=execution,
        clarification=clarification,
        config=config,
    )
    phases.append(
        _phase(
            "answer",
            "ok",
            "Prepared final response envelope.",
            answer,
        )
    )

    turn = {
        "turn_index": len(session.turns) + 1,
        "timestamp": started_at,
        "utterance": utterance,
        "route": route,
        "phases": phases,
        "assistant": answer,
        "trace": compiler_trace,
    }
    session.turns.append(turn)
    return {
        "status": "ok",
        "front_door_uri": config["front_door_uri"],
        "session_id": session.session_id,
        "turn": turn,
        "pending_clarification": session.pending_clarification,
    }


def _clarification_question(front_door: dict, utterance: str) -> str:
    compiler_question = str(front_door.get("clarification_question", "")).strip()
    if compiler_question:
        return compiler_question
    if front_door["route"] == "write":
        return (
            "Clarify before commit: name the concrete subject, predicate, and object "
            f"for '{utterance}'."
        )
    return (
        "I could not confidently route that turn. Should I treat it as a query, a write, "
        "or a no-op?"
    )


def _format_config_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _coerce_bool_token(raw: str) -> bool | None:
    value = str(raw or "").strip().lower()
    if value in {"1", "true", "yes", "on", "enabled"}:
        return True
    if value in {"0", "false", "no", "off", "disabled"}:
        return False
    return None


def _coerce_config_value(key: str, raw_value: str, current_value: Any) -> tuple[bool, Any, str]:
    text = str(raw_value or "").strip()
    if text == "":
        return False, None, f"Value required for '{key}'."

    if isinstance(current_value, bool):
        parsed = _coerce_bool_token(text)
        if parsed is None:
            return False, None, f"'{key}' expects boolean (true/false)."
        return True, parsed, ""
    if isinstance(current_value, int):
        try:
            return True, int(text), ""
        except ValueError:
            return False, None, f"'{key}' expects integer."
    if isinstance(current_value, float):
        try:
            return True, float(text), ""
        except ValueError:
            return False, None, f"'{key}' expects number."
    return True, text, ""


def _apply_config_updates(*, config: dict[str, Any], config_store: Any | None, updates: dict[str, Any]) -> dict[str, Any]:
    if config_store is not None and hasattr(config_store, "update"):
        updated = config_store.update(updates)
        if hasattr(updated, "to_dict"):
            return dict(updated.to_dict())
    merged = dict(config)
    merged.update(updates)
    return merged


def _format_config_snapshot(config: dict[str, Any]) -> str:
    lines = ["gateway dials:"]
    for key in sorted(config.keys()):
        lines.append(f"{key}={_format_config_value(config.get(key))}")
    return "\n".join(lines)


def _kb_list_text(runtime: RuntimeHooks, config: dict[str, Any], limit: int) -> str:
    snapshot = runtime.inspect_kb(config=config, limit=limit)
    clauses = snapshot.get("clauses", [])
    if not isinstance(clauses, list):
        clauses = []
    total = int(snapshot.get("clause_count", len(clauses)) or len(clauses))
    truncated = int(snapshot.get("truncated", 0) or 0)
    kb_path = str(snapshot.get("kb_path", "")).strip()
    if not clauses:
        return (
            f"KB clauses: 0 (path: {kb_path or 'in-memory'})\n"
            "No clauses currently loaded."
        )
    lines = [f"KB clauses shown: {len(clauses)} / total {total} (path: {kb_path or 'in-memory'})"]
    for idx, clause in enumerate(clauses, start=1):
        lines.append(f"{idx}. {clause}")
    if truncated > 0:
        lines.append(f"... {truncated} older clause(s) not shown.")
    return "\n".join(lines)


def _normalize_slash_input(raw: str) -> str:
    text = str(raw or "")
    # Remove common invisible characters that can break command detection.
    for token in ("\ufeff", "\u200b", "\u200c", "\u200d", "\u2060"):
        text = text.replace(token, "")
    text = text.strip()
    if text.startswith("／"):  # full-width slash
        text = "/" + text[1:]
    return text


def _handle_slash_command(
    *,
    utterance: str,
    session: SessionState,
    config: dict,
    runtime: RuntimeHooks,
    config_store: Any | None = None,
) -> dict | None:
    text = _normalize_slash_input(utterance)
    if not text.startswith("/"):
        return None

    parts = text.split(maxsplit=1)
    command = str(parts[0]).strip().lower()
    argument = str(parts[1]).strip() if len(parts) > 1 else ""
    active_config = dict(config)
    known_keys = sorted(active_config.keys())
    pending = bool(session.pending_clarification)
    answer_text = ""

    if command == "/help":
        answer_text = (
            "Slash commands:\n"
            "/help - show this command list\n"
            "/dials - list all tunable gateway settings\n"
            "/show <key> - show one dial value\n"
            "/set <key> <value> - update a dial (persisted)\n"
            "/ce <0..1> - set clarification_eagerness\n"
            "/kb [limit] - list KB clauses (default 80)\n"
            "/kb clear - empty runtime KB\n"
            "/state - show session state and pending clarification status\n"
            "/cancel - cancel current pending clarification"
        )
    elif command in {"/config", "/dials"}:
        answer_text = _format_config_snapshot(active_config)
    elif command == "/show":
        key = argument.strip()
        if not key:
            answer_text = _format_config_snapshot(active_config)
        elif key not in active_config:
            answer_text = (
                f"Unknown dial: {key}\n"
                f"Available keys: {', '.join(known_keys)}"
            )
        else:
            answer_text = f"{key}={_format_config_value(active_config.get(key))}"
    elif command == "/set":
        set_parts = text.split(maxsplit=2)
        if len(set_parts) < 3:
            answer_text = "Usage: /set <key> <value>"
        else:
            key = str(set_parts[1]).strip()
            raw_value = str(set_parts[2]).strip()
            if key not in active_config:
                answer_text = (
                    f"Unknown dial: {key}\n"
                    f"Available keys: {', '.join(known_keys)}"
                )
            else:
                ok, parsed_value, error = _coerce_config_value(key, raw_value, active_config.get(key))
                if not ok:
                    answer_text = error
                else:
                    updated_config = _apply_config_updates(
                        config=active_config,
                        config_store=config_store,
                        updates={key: parsed_value},
                    )
                    applied = updated_config.get(key)
                    answer_text = f"Updated {key}={_format_config_value(applied)}."
                    if _format_config_value(applied) != _format_config_value(parsed_value):
                        answer_text += (
                            f"\nRequested {key}={_format_config_value(parsed_value)} "
                            f"but invariant/sanitizer applied {key}={_format_config_value(applied)}."
                        )
                    if key == "strict_mode" and bool(applied):
                        answer_text += (
                            "\nStrict mode invariants active: compiler_mode=strict, "
                            "served_handoff_mode=never, require_final_confirmation=true."
                        )
    elif command == "/ce":
        if not argument:
            answer_text = "Usage: /ce <0..1>"
        else:
            ok, parsed_value, error = _coerce_config_value(
                "clarification_eagerness",
                argument,
                active_config.get("clarification_eagerness", 0.75),
            )
            if not ok:
                answer_text = error
            else:
                updated_config = _apply_config_updates(
                    config=active_config,
                    config_store=config_store,
                    updates={"clarification_eagerness": parsed_value},
                )
                answer_text = (
                    "Updated clarification_eagerness="
                    f"{_format_config_value(updated_config.get('clarification_eagerness'))}."
                )
    elif command in {"/kb", "/emptykb"}:
        kb_parts = argument.split()
        kb_action = kb_parts[0].lower() if kb_parts else "list"
        if command == "/emptykb":
            kb_action = "clear"

        if kb_action in {"clear", "empty", "reset"}:
            clear_result = runtime.clear_kb(config=active_config)
            answer_text = (
                f"KB cleared: {int(clear_result.get('cleared_count', 0) or 0)} clause(s) removed.\n"
                f"before={int(clear_result.get('before_count', 0) or 0)} "
                f"after={int(clear_result.get('after_count', 0) or 0)}\n"
                f"path={str(clear_result.get('kb_path', '')).strip() or 'in-memory'}"
            )
        elif kb_action in {"list", "ls", "show"} or kb_action.isdigit():
            limit = 80
            if kb_action.isdigit():
                limit = max(1, min(500, int(kb_action)))
            elif len(kb_parts) > 1:
                try:
                    limit = max(1, min(500, int(kb_parts[1])))
                except ValueError:
                    limit = 80
            answer_text = _kb_list_text(runtime, active_config, limit)
        elif not kb_action:
            answer_text = _kb_list_text(runtime, active_config, 80)
        else:
            answer_text = "Usage: /kb [limit] | /kb clear"
    elif command == "/state":
        answer_text = (
            f"session_id={session.session_id}\n"
            f"turn_count={len(session.turns)}\n"
            f"pending_clarification={pending}\n"
            f"front_door_uri={active_config.get('front_door_uri', '')}"
        )
    elif command == "/cancel":
        if session.pending_clarification:
            session.pending_clarification = None
            answer_text = "Pending clarification cancelled."
        else:
            answer_text = "No pending clarification to cancel."
    else:
        answer_text = (
            f"Unknown slash command: {command}\n"
            "Use /help to see available commands."
        )

    return {
        "command": command,
        "answer": {
            "speaker": "prethink-gateway",
            "text": answer_text,
            "mode": "slash_command",
        },
    }
