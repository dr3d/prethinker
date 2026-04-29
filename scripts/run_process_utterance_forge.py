#!/usr/bin/env python3
"""
Dynamic forge harness for the canonical process_utterance() entryway.

This script treats src/mcp_server.py process_utterance() as the real front door
and hammers it with synthetic, stateful user turns. The goal is not to preserve
every boring interaction forever; it is to retain interesting failures, awkward
clarifications, and surprising successes while accumulating aggregate metrics.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kb_pipeline import _call_model_prompt, _get_api_key, _parse_model_json
from src.mcp_server import PrologMCPServer


LANE_DESCRIPTIONS = {
    "fresh_fact": "A fresh declarative fact, possibly oddly phrased but grounded.",
    "compound_fact": "A compound statement with multiple facts or linked clauses.",
    "temporal_state": "A time-based or step-based state update or movement claim.",
    "pronoun_carryover": "A follow-up that relies on local discourse or pronoun carry-over.",
    "correction": "A correction, revision, or undo of something implied earlier in the episode.",
    "query_after_write": "A natural follow-up query about prior facts in the episode.",
    "mixed_boundary": "A borderline utterance that mixes statement, implication, and question shape.",
    "messy_commentary": "HN-style commentary with quotes, asides, or noisy punctuation.",
    "relationship_bundle": "Family, social, or role language with directionality pressure.",
}
LANE_CHALLENGE_HINTS = {
    "temporal_state": (
        "Favor explicit temporal sequencing, especially step-indexed state changes like "
        "'at step 6 ... later moved ...', or relative-time changes like 'after the hearing ... later moved ...'."
    ),
    "correction": (
        "Prefer natural corrections of prior state such as 'actually no' or 'not X, Y' rather than formal retract language."
    ),
    "pronoun_carryover": (
        "Use plausible local discourse carry-over such as he/she/they/it where context should matter."
    ),
    "query_after_write": (
        "Ask natural follow-up questions about latest state, current location, or prior facts from the episode."
    ),
    "messy_commentary": (
        "Keep it noisy and conversational, but avoid pure gibberish or explicit meta talk."
    ),
}

INITIAL_LANES = ["fresh_fact", "compound_fact", "temporal_state", "relationship_bundle", "messy_commentary"]
FOLLOWUP_LANES = list(LANE_DESCRIPTIONS.keys())
LANE_PROFILE_WEIGHTS = {
    "balanced": {
        "initial": {
            "fresh_fact": 1.0,
            "compound_fact": 1.0,
            "temporal_state": 1.0,
            "relationship_bundle": 1.0,
            "messy_commentary": 1.0,
        },
        "followup": {lane: 1.0 for lane in FOLLOWUP_LANES},
    },
    "error_focus": {
        "initial": {
            "fresh_fact": 0.8,
            "compound_fact": 0.8,
            "temporal_state": 1.8,
            "relationship_bundle": 0.8,
            "messy_commentary": 1.4,
        },
        "followup": {
            "fresh_fact": 0.7,
            "compound_fact": 0.7,
            "temporal_state": 2.1,
            "pronoun_carryover": 2.7,
            "correction": 3.2,
            "query_after_write": 2.6,
            "mixed_boundary": 1.0,
            "messy_commentary": 1.8,
            "relationship_bundle": 0.7,
        },
    },
    "temporal_focus": {
        "initial": {
            "fresh_fact": 0.5,
            "compound_fact": 0.6,
            "temporal_state": 3.8,
            "relationship_bundle": 0.4,
            "messy_commentary": 0.7,
        },
        "followup": {
            "fresh_fact": 0.4,
            "compound_fact": 0.5,
            "temporal_state": 4.2,
            "pronoun_carryover": 1.5,
            "correction": 1.4,
            "query_after_write": 1.6,
            "mixed_boundary": 0.6,
            "messy_commentary": 0.5,
            "relationship_bundle": 0.3,
        },
    },
}
STYLES = [
    "plain",
    "colloquial",
    "compressed",
    "elliptical",
    "hn_commentary",
    "spoken",
    "time_jumbled",
]
ALLOWED_HIDDEN_INTENTS = {"assert_fact", "assert_rule", "query", "retract", "other"}
ALLOWED_EXPECTED_BEHAVIORS = {"commit", "clarify", "query_answer", "abstain"}

NAME_POOL = [
    "Hope",
    "Scott",
    "Blake",
    "Jan",
    "Selene",
    "Theo",
    "Mara",
    "Jax",
    "Wilma",
    "Fred",
    "Nora",
    "Priya",
    "Lena",
    "Noor",
]
PLACE_POOL = [
    "Salem",
    "Morro Bay",
    "Cedar House",
    "Market Hall",
    "Mudroom",
    "Galley",
    "Bay 3",
    "Pineglass Ridge",
    "Westhaven Commons",
    "Harbor City",
]
THING_POOL = [
    "cart",
    "permit",
    "launch plan",
    "archive ledger",
    "notification history",
    "drone kestrel",
    "roof reserve",
    "micro-grant",
    "muffins",
    "turnips",
]
TIME_POOL = [
    "at 9 AM Friday",
    "at step 6",
    "at step 11",
    "after the hearing",
    "before noon",
    "yesterday morning",
    "next week",
]


def _utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")


def _slug(text: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or ""))
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_") or "forge"


def _clip_01(value: Any, default: float = 0.5) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, parsed))


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return default


def _weighted_choice(weight_map: dict[str, float], rng: random.Random) -> str:
    items = [(name, float(weight)) for name, weight in weight_map.items() if float(weight) > 0.0]
    if not items:
        raise ValueError("weight_map must contain at least one positive weight")
    total = sum(weight for _, weight in items)
    target = rng.random() * total
    running = 0.0
    for name, weight in items:
        running += weight
        if target <= running:
            return name
    return items[-1][0]


def _choose_lane(transcript: list[dict[str, Any]], rng: random.Random, lane_profile: str) -> str:
    profile = LANE_PROFILE_WEIGHTS.get(str(lane_profile or "balanced").strip().lower(), LANE_PROFILE_WEIGHTS["balanced"])
    weight_map = profile["initial"] if not transcript else profile["followup"]
    return _weighted_choice(weight_map, rng)


def _random_anchors(rng: random.Random) -> dict[str, Any]:
    names = rng.sample(NAME_POOL, k=4)
    places = rng.sample(PLACE_POOL, k=3)
    things = rng.sample(THING_POOL, k=3)
    times = rng.sample(TIME_POOL, k=2)
    return {
        "names": names,
        "places": places,
        "things": things,
        "times": times,
    }


def _transcript_view(transcript: list[dict[str, Any]], limit: int = 6) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in transcript[-limit:]:
        rows.append(
            {
                "turn_index": int(row.get("turn_index", 0)),
                "utterance": str(row.get("utterance", "")).strip(),
                "status": str(row.get("result_summary", {}).get("status", "")).strip(),
                "route": str(row.get("result_summary", {}).get("route", "")).strip(),
                "intent": str(row.get("result_summary", {}).get("parse_intent", "")).strip(),
                "logic_string": str(row.get("result_summary", {}).get("logic_string", "")).strip(),
                "verdict": str(row.get("judgment", {}).get("verdict", "")).strip(),
            }
        )
    return rows


def _build_challenger_prompt(
    *,
    lane: str,
    style: str,
    anchors: dict[str, Any],
    transcript: list[dict[str, Any]],
    episode_index: int,
    turn_index: int,
) -> str:
    lane_description = LANE_DESCRIPTIONS.get(lane, lane)
    lane_hint = LANE_CHALLENGE_HINTS.get(lane, "")
    require_context = bool(transcript) and lane in {"pronoun_carryover", "correction", "query_after_write"}
    return (
        "/no_think\n"
        "You are a synthetic user challenging a governed semantic compiler.\n"
        "Return minified JSON only with keys:\n"
        "utterance,hidden_intent,hidden_meaning,expected_behavior,risk_focus,uses_context\n"
        "Rules:\n"
        "- Produce exactly one user utterance.\n"
        "- Keep the utterance under 220 characters.\n"
        "- Make it coherent but not necessarily neat.\n"
        "- expected_behavior must be one of: commit, clarify, query_answer, abstain.\n"
        "- uses_context must be true or false.\n"
        "- hidden_meaning should briefly say what the user really means in plain English.\n"
        "- risk_focus should name the main thing being tested (pronoun, temporal, correction, etc.).\n"
        "- If context is available, you may use it; if context is required, you should use it.\n"
        "- Do not mention JSON, tests, Prolog, compiler, or hidden fields in the utterance.\n\n"
        f"Episode: {episode_index}\n"
        f"Turn: {turn_index}\n"
        f"Lane: {lane}\n"
        f"Lane description: {lane_description}\n"
        f"Lane hint: {lane_hint}\n"
        f"Style: {style}\n"
        f"Context required: {'yes' if require_context else 'no'}\n"
        f"Anchors: {json.dumps(anchors, ensure_ascii=False)}\n"
        f"Recent transcript: {json.dumps(transcript, ensure_ascii=False)}\n"
    )


def _looks_meta_generator_artifact(text: str) -> bool:
    lowered = str(text or "").strip().lower()
    if not lowered:
        return True
    if "anchor list" in lowered or "list every single item" in lowered:
        return True
    if "semantic compiler" in lowered or "hidden meaning" in lowered:
        return True
    if lowered.count(",") >= 10:
        return True
    return False


def _fallback_turn_spec(
    *,
    lane: str,
    style: str,
    anchors: dict[str, Any],
    transcript: list[dict[str, Any]],
) -> dict[str, Any]:
    names = anchors.get("names", ["Hope", "Scott", "Blake", "Jan"])
    places = anchors.get("places", ["Salem", "Morro Bay", "Cedar House"])
    things = anchors.get("things", ["permit", "launch plan", "muffins"])
    times = anchors.get("times", ["at 9 AM Friday", "next week"])
    if lane == "temporal_state":
        utterance = f"{times[0]} {names[0]} was in {places[0]} and later moved to {places[1]}."
        hidden_intent = "assert_fact"
        meaning = f"{names[0]} was first in {places[0]} and then in {places[1]} at the stated time."
        expected = "commit"
        risk = "temporal"
    elif lane == "pronoun_carryover" and transcript:
        utterance = f"and now they live in {places[0]}"
        hidden_intent = "assert_fact"
        meaning = "The active previously mentioned group now lives in the supplied place."
        expected = "clarify"
        risk = "pronoun"
    elif lane == "correction" and transcript:
        utterance = f"actually no, {things[0]} is with {names[1]} not {names[0]}"
        hidden_intent = "retract"
        meaning = f"A previous ownership or possession claim should be corrected toward {names[1]}."
        expected = "clarify"
        risk = "correction"
    elif lane == "query_after_write" and transcript:
        utterance = f"so where is {names[0]} now?"
        hidden_intent = "query"
        meaning = f"The user wants the current location of {names[0]}."
        expected = "query_answer"
        risk = "query_after_write"
    elif lane == "compound_fact":
        utterance = f"{names[0]} runs the {things[0]} and {names[1]} keeps the ledger in {places[0]}"
        hidden_intent = "assert_fact"
        meaning = f"{names[0]} runs {things[0]} and {names[1]} keeps a ledger in {places[0]}."
        expected = "commit"
        risk = "compound"
    elif lane == "relationship_bundle":
        utterance = f"{names[0]}'s mom and dad are {names[1]} and {names[2]}"
        hidden_intent = "assert_fact"
        meaning = f"{names[1]} and {names[2]} are the parents of {names[0]}."
        expected = "commit"
        risk = "directionality"
    elif lane == "messy_commentary":
        utterance = (
            f"quote me maybe but the {things[0]} thing felt busted, like '{things[0]}' was supposedly fixed "
            f"yet {names[0]} still got pinged in {places[0]}?"
        )
        hidden_intent = "other"
        meaning = f"The user is expressing noisy commentary about {things[0]} and {names[0]} in {places[0]}."
        expected = "abstain"
        risk = "hn_noise"
    else:
        utterance = f"remember that {names[0]} lives in {places[0]}"
        hidden_intent = "assert_fact"
        meaning = f"{names[0]} lives in {places[0]}."
        expected = "commit"
        risk = "fresh_fact"
    return {
        "utterance": utterance,
        "hidden_intent": hidden_intent,
        "hidden_meaning": meaning,
        "expected_behavior": expected,
        "risk_focus": risk,
        "uses_context": bool(transcript and lane in {"pronoun_carryover", "correction", "query_after_write"}),
        "lane": lane,
        "style": style,
        "source": "fallback",
    }


def _generate_turn_spec(
    *,
    lane: str,
    style: str,
    anchors: dict[str, Any],
    transcript: list[dict[str, Any]],
    episode_index: int,
    turn_index: int,
    backend: str,
    base_url: str,
    model: str,
    context_length: int,
    timeout: int,
    api_key: str | None,
) -> dict[str, Any]:
    prompt = _build_challenger_prompt(
        lane=lane,
        style=style,
        anchors=anchors,
        transcript=transcript,
        episode_index=episode_index,
        turn_index=turn_index,
    )
    try:
        response = _call_model_prompt(
            backend=backend,
            base_url=base_url,
            model=model,
            prompt_text=prompt,
            context_length=context_length,
            timeout=timeout,
            api_key=api_key,
        )
        parsed, _ = _parse_model_json(
            response,
            required_keys=[
                "utterance",
                "hidden_intent",
                "hidden_meaning",
                "expected_behavior",
            ],
        )
        if isinstance(parsed, dict):
            utterance = str(parsed.get("utterance", "")).strip()
            hidden_intent = str(parsed.get("hidden_intent", "")).strip() or "other"
            expected_behavior = str(parsed.get("expected_behavior", "")).strip() or "clarify"
            hidden_meaning = str(parsed.get("hidden_meaning", "")).strip()
            if (
                utterance
                and len(utterance) <= 220
                and hidden_intent in ALLOWED_HIDDEN_INTENTS
                and expected_behavior in ALLOWED_EXPECTED_BEHAVIORS
                and not _looks_meta_generator_artifact(utterance)
                and not _looks_meta_generator_artifact(hidden_meaning)
            ):
                return {
                    "utterance": utterance,
                    "hidden_intent": hidden_intent,
                    "hidden_meaning": hidden_meaning,
                    "expected_behavior": expected_behavior,
                    "risk_focus": str(parsed.get("risk_focus", "")).strip() or lane,
                    "uses_context": _coerce_bool(parsed.get("uses_context"), False),
                    "lane": lane,
                    "style": style,
                    "source": "model",
                }
    except Exception:
        pass
    return _fallback_turn_spec(lane=lane, style=style, anchors=anchors, transcript=transcript)


def _build_clarification_answer_prompt(
    *,
    spec: dict[str, Any],
    question: str,
    transcript: list[dict[str, Any]],
) -> str:
    return (
        "/no_think\n"
        "You are the synthetic user who produced the prior utterance.\n"
        "Return minified JSON only with keys: answer,confidence\n"
        "Rules:\n"
        "- Answer the clarification question briefly from the hidden meaning and conversation context.\n"
        "- If the question cannot be answered safely from that hidden meaning, answer exactly \"I can't tell from what I meant.\" and set confidence to 0.\n"
        "- Do not explain yourself.\n\n"
        f"Original utterance: {spec.get('utterance', '')}\n"
        f"Hidden meaning: {spec.get('hidden_meaning', '')}\n"
        f"Recent transcript: {json.dumps(transcript, ensure_ascii=False)}\n"
        f"Clarification question: {question}\n"
    )


def _fallback_clarification_answer(spec: dict[str, Any]) -> str:
    hidden = str(spec.get("hidden_meaning", "")).strip()
    if not hidden:
        return ""
    if len(hidden) > 140:
        hidden = hidden[:140].rstrip()
    return hidden


def _generate_clarification_answer(
    *,
    spec: dict[str, Any],
    question: str,
    transcript: list[dict[str, Any]],
    backend: str,
    base_url: str,
    model: str,
    context_length: int,
    timeout: int,
    api_key: str | None,
) -> str:
    prompt = _build_clarification_answer_prompt(spec=spec, question=question, transcript=transcript)
    try:
        response = _call_model_prompt(
            backend=backend,
            base_url=base_url,
            model=model,
            prompt_text=prompt,
            context_length=context_length,
            timeout=timeout,
            api_key=api_key,
        )
        parsed, _ = _parse_model_json(response, required_keys=["answer", "confidence"])
        if isinstance(parsed, dict):
            answer = str(parsed.get("answer", "")).strip()
            confidence = _clip_01(parsed.get("confidence"), 0.0)
            if answer and confidence >= 0.35 and answer.lower() != "i can't tell from what i meant.":
                return answer
    except Exception:
        pass
    return _fallback_clarification_answer(spec)


def _query_row_count(query_result: Any) -> int:
    if isinstance(query_result, dict):
        rows = query_result.get("rows", [])
        if isinstance(rows, list):
            return len(rows)
    if isinstance(query_result, list):
        return len(query_result)
    return 0


def _summarize_result(result: dict[str, Any]) -> dict[str, Any]:
    front_door = result.get("front_door", {}) if isinstance(result.get("front_door"), dict) else {}
    execution = result.get("execution", {}) if isinstance(result.get("execution"), dict) else {}
    parse = execution.get("parse", {}) if isinstance(execution.get("parse"), dict) else {}
    trace_summary = (
        result.get("compiler_trace", {}).get("summary", {})
        if isinstance(result.get("compiler_trace"), dict)
        and isinstance(result.get("compiler_trace", {}).get("summary"), dict)
        else {}
    )
    return {
        "status": str(result.get("status", "")).strip(),
        "result_type": str(result.get("result_type", "")).strip(),
        "route": str(front_door.get("route", "")).strip(),
        "compiler_intent": str(front_door.get("compiler_intent", "")).strip(),
        "needs_clarification": bool(front_door.get("needs_clarification", False)),
        "clarification_question": str(front_door.get("clarification_question", "")).strip(),
        "ambiguity_score": _clip_01(front_door.get("ambiguity_score"), 0.0),
        "execution_status": str(execution.get("status", "")).strip(),
        "parse_intent": str(parse.get("intent", "")).strip(),
        "logic_string": str(parse.get("logic_string", "")).strip(),
        "writes_applied": int(execution.get("writes_applied", 0) or 0),
        "operation_count": len(execution.get("operations", [])) if isinstance(execution.get("operations"), list) else 0,
        "query_row_count": _query_row_count(execution.get("query_result")),
        "error_count": len(execution.get("errors", [])) if isinstance(execution.get("errors"), list) else 0,
        "trace_overall": str(trace_summary.get("overall", "")).strip(),
        "trace_parse_rescues": list(trace_summary.get("parse_rescues", [])) if isinstance(trace_summary.get("parse_rescues"), list) else [],
        "freethinker_action": str(trace_summary.get("freethinker_action", "")).strip(),
    }


def _build_judge_prompt(
    *,
    spec: dict[str, Any],
    result_summary: dict[str, Any],
    clarification_answer: str,
) -> str:
    return (
        "/no_think\n"
        "You are grading a governed semantic compiler front door.\n"
        "Return minified JSON only with keys: verdict,severity,tags,keep_case,rationale\n"
        "Rules:\n"
        "- verdict must be one of: pass, warn, fail.\n"
        "- severity is 0..1.\n"
        "- tags must be a short list of issue labels.\n"
        "- keep_case should be true for fails, useful warnings, or surprising passes.\n"
        "- PASS when the behavior is appropriate and grounded.\n"
        "- WARN when the system is conservative but awkward, over-clarifies, under-commits, or shows brittle behavior.\n"
        "- FAIL when it invents meaning, commits the wrong thing, asks a nonsense clarification, or produces absurd logic.\n\n"
        f"Synthetic user spec: {json.dumps(spec, ensure_ascii=False)}\n"
        f"Clarification answer used: {clarification_answer}\n"
        f"Observed result summary: {json.dumps(result_summary, ensure_ascii=False)}\n"
    )


def _fallback_judgment(spec: dict[str, Any], result_summary: dict[str, Any]) -> dict[str, Any]:
    status = str(result_summary.get("status", "")).strip()
    expected = str(spec.get("expected_behavior", "")).strip().lower()
    logic = str(result_summary.get("logic_string", "")).strip()
    clarification = bool(result_summary.get("needs_clarification", False))
    tags: list[str] = []
    verdict = "pass"
    severity = 0.2
    rationale = "Behavior looked acceptable by heuristic fallback."

    if status == "error" or int(result_summary.get("error_count", 0) or 0) > 0:
        verdict = "fail"
        severity = 0.95
        tags = ["execution_error"]
        rationale = "The canonical entryway returned an error."
    elif expected in {"commit", "query_answer"} and clarification:
        verdict = "warn"
        severity = 0.58
        tags = ["over_clarified"]
        rationale = "The system asked for clarification where the synthetic user expected usable handling."
    elif expected == "abstain" and status == "success" and logic:
        verdict = "warn"
        severity = 0.64
        tags = ["over_committed"]
        rationale = "The system produced concrete logic for a noisy or commentary-shaped turn."
    elif status == "clarification_required" and expected == "clarify":
        verdict = "pass"
        severity = 0.22
        tags = ["expected_clarification"]
        rationale = "The system asked for clarification as expected."
    elif expected == "commit" and status == "success" and not logic:
        verdict = "warn"
        severity = 0.66
        tags = ["under_committed"]
        rationale = "The system succeeded without yielding a usable parse payload."
    elif "retract(" in logic and "correction" not in str(spec.get("risk_focus", "")).lower():
        verdict = "warn"
        severity = 0.72
        tags = ["unexpected_retract_shape"]
        rationale = "The system landed on a retract shape unexpectedly."

    keep = verdict != "pass" or severity >= 0.6
    return {
        "verdict": verdict,
        "severity": round(severity, 4),
        "tags": tags,
        "keep_case": keep,
        "rationale": rationale,
        "source": "fallback",
    }


def _judge_turn(
    *,
    spec: dict[str, Any],
    result_summary: dict[str, Any],
    clarification_answer: str,
    backend: str,
    base_url: str,
    model: str,
    context_length: int,
    timeout: int,
    api_key: str | None,
) -> dict[str, Any]:
    prompt = _build_judge_prompt(
        spec=spec,
        result_summary=result_summary,
        clarification_answer=clarification_answer,
    )
    try:
        response = _call_model_prompt(
            backend=backend,
            base_url=base_url,
            model=model,
            prompt_text=prompt,
            context_length=context_length,
            timeout=timeout,
            api_key=api_key,
        )
        parsed, _ = _parse_model_json(
            response,
            required_keys=["verdict", "severity", "tags", "keep_case", "rationale"],
        )
        if isinstance(parsed, dict):
            return {
                "verdict": str(parsed.get("verdict", "")).strip() or "warn",
                "severity": round(_clip_01(parsed.get("severity"), 0.5), 4),
                "tags": list(parsed.get("tags", [])) if isinstance(parsed.get("tags"), list) else [],
                "keep_case": _coerce_bool(parsed.get("keep_case"), False),
                "rationale": str(parsed.get("rationale", "")).strip(),
                "source": "model",
            }
    except Exception:
        pass
    return _fallback_judgment(spec, result_summary)


def _interestingness_score(judgment: dict[str, Any], result_summary: dict[str, Any]) -> float:
    verdict = str(judgment.get("verdict", "")).strip().lower()
    severity = _clip_01(judgment.get("severity"), 0.0)
    score = severity
    if verdict == "fail":
        score += 0.5
    elif verdict == "warn":
        score += 0.2
    if bool(result_summary.get("needs_clarification", False)):
        score += 0.1
    if str(result_summary.get("status", "")).strip() == "error":
        score += 0.3
    if result_summary.get("trace_parse_rescues"):
        score += 0.05
    return round(score, 4)


def _should_keep_case(
    *,
    judgment: dict[str, Any],
    result_summary: dict[str, Any],
    pass_sample_rate: float,
    rng: random.Random,
) -> bool:
    verdict = str(judgment.get("verdict", "")).strip().lower()
    if verdict == "pass":
        if _interestingness_score(judgment, result_summary) >= 0.85:
            return True
        return rng.random() < max(0.0, min(1.0, float(pass_sample_rate)))
    if _coerce_bool(judgment.get("keep_case"), False):
        return True
    return _interestingness_score(judgment, result_summary) >= 0.75


def _episode_overview(transcript: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "turn_index": int(row.get("turn_index", 0)),
            "lane": str(row.get("spec", {}).get("lane", "")).strip(),
            "utterance": str(row.get("utterance", "")).strip(),
            "status": str(row.get("result_summary", {}).get("status", "")).strip(),
            "verdict": str(row.get("judgment", {}).get("verdict", "")).strip(),
        }
        for row in transcript
    ]


def _run_episode(
    *,
    episode_index: int,
    args: argparse.Namespace,
    rng: random.Random,
    challenger_api_key: str | None,
    judge_api_key: str | None,
) -> dict[str, Any]:
    server = PrologMCPServer(
        compiler_mode=args.compiler_mode,
        compiler_backend=args.compiler_backend,
        compiler_base_url=args.compiler_base_url,
        compiler_model=args.compiler_model,
        compiler_context_length=args.compiler_context_length,
        compiler_timeout=args.compiler_timeout,
        compiler_prompt_file=args.compiler_prompt_file,
        freethinker_resolution_policy=args.freethinker_resolution_policy,
        freethinker_backend=args.freethinker_backend,
        freethinker_base_url=args.freethinker_base_url,
        freethinker_model=args.freethinker_model,
        freethinker_context_length=args.freethinker_context_length,
        freethinker_timeout=args.freethinker_timeout,
        freethinker_prompt_file=args.freethinker_prompt_file,
    )
    server.empty_kb()
    transcript: list[dict[str, Any]] = []
    interesting_cases: list[dict[str, Any]] = []

    for turn_index in range(1, int(args.turns_per_episode) + 1):
        lane = _choose_lane(transcript, rng, args.lane_profile)
        style = rng.choice(STYLES)
        anchors = _random_anchors(rng)
        transcript_view = _transcript_view(transcript)
        spec = _generate_turn_spec(
            lane=lane,
            style=style,
            anchors=anchors,
            transcript=transcript_view,
            episode_index=episode_index,
            turn_index=turn_index,
            backend=args.challenger_backend,
            base_url=args.challenger_base_url,
            model=args.challenger_model,
            context_length=args.challenger_context_length,
            timeout=args.challenger_timeout,
            api_key=challenger_api_key,
        )
        utterance = str(spec.get("utterance", "")).strip()
        result = server.process_utterance({"utterance": utterance})
        clarification_answer = ""
        if str(result.get("status", "")).strip() == "clarification_required" and args.auto_answer_clarifications:
            question = str(
                result.get("clarification", {}).get("question", "")
                if isinstance(result.get("clarification"), dict)
                else result.get("front_door", {}).get("clarification_question", "")
            ).strip()
            prethink_id = str(result.get("front_door", {}).get("prethink_id", "")).strip()
            clarification_answer = _generate_clarification_answer(
                spec=spec,
                question=question,
                transcript=transcript_view,
                backend=args.challenger_backend,
                base_url=args.challenger_base_url,
                model=args.challenger_model,
                context_length=args.challenger_context_length,
                timeout=args.challenger_timeout,
                api_key=challenger_api_key,
            )
            if clarification_answer:
                result = server.process_utterance(
                    {
                        "utterance": utterance,
                        "clarification_answer": clarification_answer,
                        "prethink_id": prethink_id,
                    }
                )

        result_summary = _summarize_result(result)
        judgment = _judge_turn(
            spec=spec,
            result_summary=result_summary,
            clarification_answer=clarification_answer,
            backend=args.judge_backend,
            base_url=args.judge_base_url,
            model=args.judge_model,
            context_length=args.judge_context_length,
            timeout=args.judge_timeout,
            api_key=judge_api_key,
        )
        interestingness = _interestingness_score(judgment, result_summary)
        keep_case = _should_keep_case(
            judgment=judgment,
            result_summary=result_summary,
            pass_sample_rate=args.pass_sample_rate,
            rng=rng,
        )
        record = {
            "turn_index": turn_index,
            "utterance": utterance,
            "spec": spec,
            "clarification_answer": clarification_answer,
            "result_summary": result_summary,
            "judgment": judgment,
            "interestingness": interestingness,
            "raw_result": result,
        }
        transcript.append(record)
        if keep_case and len(interesting_cases) < int(args.max_interesting_cases_per_episode):
            interesting_cases.append(
                {
                    "turn_index": turn_index,
                    "utterance": utterance,
                    "spec": spec,
                    "clarification_answer": clarification_answer,
                    "result_summary": result_summary,
                    "judgment": judgment,
                    "interestingness": interestingness,
                    "episode_overview": _episode_overview(transcript),
                    "raw_result": result,
                }
            )
        print(
            f"[episode {episode_index:02d} turn {turn_index:02d}] "
            f"lane={lane} status={result_summary['status']} verdict={judgment['verdict']} "
            f"score={interestingness:.2f}"
        )

    verdict_counts = Counter(str(row.get("judgment", {}).get("verdict", "")).strip() for row in transcript)
    status_counts = Counter(str(row.get("result_summary", {}).get("status", "")).strip() for row in transcript)
    lane_counts = Counter(str(row.get("spec", {}).get("lane", "")).strip() for row in transcript)
    return {
        "episode_index": episode_index,
        "transcript": transcript,
        "interesting_cases": interesting_cases,
        "metrics": {
            "turns": len(transcript),
            "clarification_turns": sum(
                1 for row in transcript if bool(row.get("result_summary", {}).get("needs_clarification", False))
            ),
            "warnings": int(verdict_counts.get("warn", 0)),
            "failures": int(verdict_counts.get("fail", 0)),
            "verdict_counts": dict(verdict_counts),
            "status_counts": dict(status_counts),
            "lane_counts": dict(lane_counts),
        },
    }


def _write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Process Utterance Forge",
        "",
        f"- generated_at_utc: `{summary.get('generated_at_utc', '')}`",
        f"- episodes: `{summary.get('episodes_total', 0)}`",
        f"- turns: `{summary.get('turns_total', 0)}`",
        f"- interesting_cases: `{summary.get('interesting_cases_total', 0)}`",
        f"- verdict_counts: `{summary.get('verdict_counts', {})}`",
        f"- status_counts: `{summary.get('status_counts', {})}`",
        "",
        "## Top Tags",
        "",
    ]
    top_tags = summary.get("top_tags", [])
    if isinstance(top_tags, list) and top_tags:
        for row in top_tags:
            lines.append(f"- `{row.get('tag', '')}`: `{row.get('count', 0)}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Episodes", ""])
    for episode in summary.get("episodes", []):
        metrics = episode.get("metrics", {})
        lines.append(
            f"- episode `{episode.get('episode_index', 0)}`: turns={metrics.get('turns', 0)} "
            f"failures={metrics.get('failures', 0)} warnings={metrics.get('warnings', 0)} "
            f"clarifications={metrics.get('clarification_turns', 0)}"
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dynamic forge harness for process_utterance().")
    parser.add_argument("--episodes", type=int, default=4)
    parser.add_argument("--turns-per-episode", type=int, default=5)
    parser.add_argument("--seed", type=int, default=54)
    parser.add_argument("--out-dir", default="tmp/runs/process_utterance_forge")
    parser.add_argument("--summary-out", default="")
    parser.add_argument("--summary-md", default="")
    parser.add_argument("--max-interesting-cases-per-episode", type=int, default=8)
    parser.add_argument("--pass-sample-rate", type=float, default=0.08)
    parser.add_argument("--auto-answer-clarifications", action="store_true", default=True)
    parser.add_argument("--lane-profile", choices=sorted(LANE_PROFILE_WEIGHTS.keys()), default="balanced")

    parser.add_argument("--compiler-mode", choices=["strict", "auto", "heuristic"], default="strict")
    parser.add_argument("--compiler-backend", default="ollama")
    parser.add_argument("--compiler-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--compiler-model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--compiler-context-length", type=int, default=8192)
    parser.add_argument("--compiler-timeout", type=int, default=60)
    parser.add_argument(
        "--compiler-prompt-file",
        default=str(ROOT / "modelfiles" / "blank_prompt.md"),
    )

    parser.add_argument("--freethinker-resolution-policy", default="off")
    parser.add_argument("--freethinker-backend", default="ollama")
    parser.add_argument("--freethinker-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--freethinker-model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--freethinker-context-length", type=int, default=16384)
    parser.add_argument("--freethinker-timeout", type=int, default=60)
    parser.add_argument(
        "--freethinker-prompt-file",
        default=str(ROOT / "modelfiles" / "freethinker_system_prompt.md"),
    )

    parser.add_argument("--challenger-backend", default="ollama")
    parser.add_argument("--challenger-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--challenger-model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--challenger-context-length", type=int, default=8192)
    parser.add_argument("--challenger-timeout", type=int, default=60)

    parser.add_argument("--judge-backend", default="ollama")
    parser.add_argument("--judge-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--judge-model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--judge-context-length", type=int, default=8192)
    parser.add_argument("--judge-timeout", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rng = random.Random(int(args.seed))
    run_stamp = _utc_stamp()
    run_dir = Path(args.out_dir).resolve() / f"{run_stamp}_forge"
    run_dir.mkdir(parents=True, exist_ok=True)
    interesting_dir = run_dir / "interesting_cases"
    interesting_dir.mkdir(parents=True, exist_ok=True)

    summary_out = Path(args.summary_out).resolve() if args.summary_out else run_dir / "summary.json"
    summary_md = Path(args.summary_md).resolve() if args.summary_md else run_dir / "summary.md"

    challenger_api_key = _get_api_key()
    judge_api_key = _get_api_key()

    episodes: list[dict[str, Any]] = []
    interesting_total = 0
    verdict_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()

    for episode_index in range(1, int(args.episodes) + 1):
        episode = _run_episode(
            episode_index=episode_index,
            args=args,
            rng=rng,
            challenger_api_key=challenger_api_key,
            judge_api_key=judge_api_key,
        )
        episodes.append(episode)
        for row in episode.get("transcript", []):
            verdict_counts[str(row.get("judgment", {}).get("verdict", "")).strip()] += 1
            status_counts[str(row.get("result_summary", {}).get("status", "")).strip()] += 1
            for tag in row.get("judgment", {}).get("tags", []):
                tag_counts[str(tag).strip()] += 1
        for case in episode.get("interesting_cases", []):
            interesting_total += 1
            case_path = interesting_dir / f"episode_{episode_index:02d}_turn_{int(case.get('turn_index', 0)):02d}.json"
            case_path.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "episodes_total": len(episodes),
        "turns_total": sum(int(ep.get("metrics", {}).get("turns", 0)) for ep in episodes),
        "interesting_cases_total": interesting_total,
        "verdict_counts": dict(verdict_counts),
        "status_counts": dict(status_counts),
        "top_tags": [
            {"tag": tag, "count": count}
            for tag, count in tag_counts.most_common(12)
        ],
        "settings": {
            "compiler_model": args.compiler_model,
            "challenger_model": args.challenger_model,
            "judge_model": args.judge_model,
            "freethinker_resolution_policy": args.freethinker_resolution_policy,
            "lane_profile": args.lane_profile,
            "episodes": int(args.episodes),
            "turns_per_episode": int(args.turns_per_episode),
            "seed": int(args.seed),
        },
        "artifacts": {
            "run_dir": str(run_dir),
            "interesting_dir": str(interesting_dir),
        },
        "episodes": [
            {
                "episode_index": ep.get("episode_index", 0),
                "metrics": ep.get("metrics", {}),
            }
            for ep in episodes
        ],
    }
    summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_summary_md(summary_md, summary)

    print("")
    print(f"Forge summary: {summary_out}")
    print(f"Interesting cases: {interesting_dir}")
    print(
        f"Totals: turns={summary['turns_total']} interesting={summary['interesting_cases_total']} "
        f"verdicts={summary['verdict_counts']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
