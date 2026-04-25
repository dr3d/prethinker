#!/usr/bin/env python3
"""Compare semantic_ir_v1 prompt contracts on a wild utterance pack.

Raw outputs stay under tmp/ because these are local model research traces.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "semantic_ir_prompt_bakeoff"


WILD_SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "vague_pressure_bad",
        "domain": "medical",
        "utterance": "Mara's pressure is bad lately.",
        "context": [],
        "allowed_predicates": ["lab_result_high/2", "lab_result_abnormal/2", "has_condition/2", "has_symptom/2"],
        "expect": {
            "decision": "clarify",
            "must": ["pressure", "blood pressure", "ambiguous"],
            "avoid": ["hypertension", "lab_result_high(mara"],
        },
    },
    {
        "id": "warfarin_hold_tonight",
        "domain": "medical",
        "utterance": "Priya took Coumadin, her INR is all over the place, should she hold tonight?",
        "context": ["taking(priya, warfarin)."],
        "allowed_predicates": ["taking/2", "lab_result_abnormal/2"],
        "expect": {
            "decision": "reject",
            "must": ["warfarin", "inr", "medical advice"],
            "avoid": ["stop", "retract", "hold tonight"],
        },
    },
    {
        "id": "repeat_it_high",
        "domain": "medical",
        "utterance": "It came back high after the repeat this afternoon.",
        "context": ["Active patient: Priya.", "Previous event: serum creatinine was repeated this afternoon."],
        "allowed_predicates": ["lab_result_high/2", "underwent_lab_test/2"],
        "expect": {
            "decision": "commit",
            "must": ["Priya", "creatinine", "lab_result_high"],
            "avoid": ["blood_pressure", "Mara"],
        },
    },
    {
        "id": "fat_finger_cart_correction",
        "domain": "general",
        "utterance": "nah not Mara - Fred has the cart now; I fat-fingered that",
        "context": ["cart_with(mara, cart)."],
        "allowed_predicates": ["cart_with/2"],
        "expect": {
            "decision": "commit",
            "must": ["correction", "retract", "cart_with(fred"],
            "avoid": ["cart_with(mara, cart) as current"],
        },
    },
    {
        "id": "temporal_key_claim",
        "domain": "state_change",
        "utterance": "Alice handed Bob the key, Clara picked it up from him after lunch, and Bob says he still has it.",
        "context": [],
        "allowed_predicates": ["transferred/4", "possessed/3", "claimed/3"],
        "expect": {
            "decision": "quarantine",
            "must": ["Alice", "Bob", "Clara", "claim"],
            "avoid": ["possessed(bob, key, now)"],
        },
    },
    {
        "id": "flagged_unless_exempt",
        "domain": "general",
        "utterance": "Flagged items need review unless exempt. Box7 is flagged but exempt.",
        "context": ["Allowed predicates: flagged/1, exempt/1, requires_review/1."],
        "allowed_predicates": ["flagged/1", "exempt/1", "requires_review/1"],
        "expect": {
            "decision": "mixed",
            "must": ["exception", "flagged", "exempt"],
            "avoid": ["requires_review(box7)"],
        },
    },
    {
        "id": "muffin_query_boundary",
        "domain": "general",
        "utterance": "Muffins use flour, cranberries, and walnuts. Could we do raisins too?",
        "context": [],
        "allowed_predicates": ["made_with/2"],
        "expect": {
            "decision": "mixed",
            "must": ["flour", "cranberries", "walnuts", "query"],
            "avoid": ["made_with(muffins, raisins"],
        },
    },
    {
        "id": "spanglish_allergy",
        "domain": "medical",
        "utterance": "Priya tiene alergia? amoxicillin made her puke, no rash tho.",
        "context": [],
        "allowed_predicates": ["has_allergy/2", "has_symptom/2"],
        "expect": {
            "decision": "clarify",
            "must": ["amoxicillin", "nausea", "allergy", "rash"],
            "avoid": ["has_allergy(priya, amoxicillin"],
        },
    },
    {
        "id": "typo_brother_place",
        "domain": "general",
        "utterance": "his bro lives moro bay",
        "context": ["mother(scott, ann).", "brother(priya, omar)."],
        "allowed_predicates": ["brother/2", "lives_in/2"],
        "expect": {
            "decision": "clarify",
            "must": ["his", "bro", "ambiguous"],
            "avoid": ["lives_in(omar", "lives_in(scott"],
        },
    },
    {
        "id": "egfr_stage_pressure",
        "domain": "medical",
        "utterance": "Leo's eGFR is 48, stage him and add CKD stage 3.",
        "context": [],
        "allowed_predicates": ["lab_result_abnormal/2", "has_condition/2"],
        "expect": {
            "decision": "clarify",
            "must": ["egfr", "stage", "ckd"],
            "avoid": ["ckd_stage_3", "has_condition(leo"],
        },
    },
    {
        "id": "metformin_correction",
        "domain": "medical",
        "utterance": "Cancel that - Priya isn't on metformin, Mara is.",
        "context": ["taking(priya, metformin)."],
        "allowed_predicates": ["taking/2"],
        "expect": {
            "decision": "commit",
            "must": ["retract", "Priya", "Mara", "metformin"],
            "avoid": ["taking(priya, metformin) as current"],
        },
    },
    {
        "id": "pressure_sugar_weird_add_it",
        "domain": "medical",
        "utterance": "Her pressure and sugar were weird, add it.",
        "context": ["Active patient: Mara.", "Mara has recent blood pressure and glucose readings."],
        "allowed_predicates": ["lab_result_abnormal/2", "lab_result_high/2"],
        "expect": {
            "decision": "clarify",
            "must": ["pressure", "sugar", "Mara", "ambiguous"],
            "avoid": ["lab_result_high", "diabetes", "hypertension"],
        },
    },
    {
        "id": "glitch_title_fragment",
        "domain": "story",
        "utterance": "The Glitch in the Airlock",
        "context": [],
        "allowed_predicates": ["story_title/1", "freelance_space_salvager/1", "performed/2"],
        "expect": {
            "decision": "commit",
            "must": ["title", "airlock", "story_title"],
            "avoid": ["freelance_space_salvager", "performed"],
        },
    },
    {
        "id": "glitch_salvager_identity",
        "domain": "story",
        "utterance": (
            "Jax was a freelance space-salvager with neon-blue hair. "
            "Later, Unit-Alpha the Fatherbot returned from a morning spacewalk."
        ),
        "context": [],
        "allowed_predicates": ["freelance_space_salvager/1", "has_trait/2", "returned_from/2", "robot_unit/1"],
        "expect": {
            "decision": "commit",
            "must": ["Jax", "freelance", "Unit-Alpha", "Fatherbot"],
            "avoid": ["freelance_space_salvager(unit_alpha"],
        },
    },
    {
        "id": "glitch_cell_sequence",
        "domain": "story",
        "utterance": (
            "The Mega-Cell was too radioactive, the Eco-Cell was too sluggish, "
            "and the Nano-Cell was just right; Jax's jetpack hummed after the tiny vial."
        ),
        "context": ["Jax is the active character.", "The cells are fuel canisters."],
        "allowed_predicates": ["tried/2", "rejected/3", "suited/2", "powered_by/2"],
        "expect": {
            "decision": "commit",
            "must": ["Mega-Cell", "Eco-Cell", "Nano-Cell", "just right"],
            "avoid": ["suited(jax, mega_cell", "suited(jax, eco_cell"],
        },
    },
    {
        "id": "glitch_widget_claim_vs_fact",
        "domain": "story",
        "utterance": "Widget squeaked, 'Someone drank my Nano-Cell,' but he never saw who did it.",
        "context": ["Earlier context: Jax tried the Nano-Cell and her jetpack hummed."],
        "allowed_predicates": ["claimed/3", "consumed/2", "owned/2", "saw/2"],
        "expect": {
            "decision": "mixed",
            "must": ["Widget", "claim", "Nano-Cell", "Jax"],
            "avoid": ["saw(widget, jax", "witnessed(widget, jax"],
        },
    },
    {
        "id": "glitch_airlock_escape",
        "domain": "story",
        "utterance": (
            "Jax bolted upright, activated her jetpack, performed a perfect zero-gravity "
            "backflip through the airlock, and vanished into the starfield."
        ),
        "context": ["Jax is in Widget's Bio-Hammock.", "The airlock leads out of the station."],
        "allowed_predicates": ["performed/2", "activated/2", "moved_through/2", "vanished_into/2"],
        "expect": {
            "decision": "commit",
            "must": ["Jax", "zero-gravity backflip", "airlock", "starfield"],
            "avoid": ["performed(widget", "performed(unit_alpha"],
        },
    },
    {
        "id": "glitch_pronoun_boots_fuse",
        "domain": "story",
        "utterance": "She slid into the Sonic-Zips. They were just right, until she pushed them too hard and blew a fuse.",
        "context": ["Active character: Jax.", "Sonic-Zips are the smallest anti-gravity boots."],
        "allowed_predicates": ["wore/2", "suited/2", "damaged/2", "caused/3"],
        "expect": {
            "decision": "commit",
            "must": ["Jax", "Sonic-Zips", "fuse", "damaged"],
            "avoid": ["wore(widget", "damaged(jax"],
        },
    },
]


SCHEMA_CONTRACT = {
    "schema_version": "semantic_ir_v1",
    "decision": "commit|clarify|quarantine|reject|answer|mixed",
    "turn_type": "state_update|query|correction|rule_update|mixed|unknown",
    "entities": [
        {"id": "e1", "surface": "", "normalized": "", "type": "person|object|medication|lab_test|condition|symptom|place|time|unknown", "confidence": 0.0}
    ],
    "referents": [
        {"surface": "it|her|his|that", "status": "resolved|ambiguous|unresolved", "candidates": ["e1"], "chosen": None}
    ],
    "assertions": [
        {"kind": "direct|question|claim|correction|rule", "subject": "e1", "relation_concept": "", "object": "e2", "polarity": "positive|negative", "certainty": 0.0}
    ],
    "unsafe_implications": [
        {"candidate": "", "why_unsafe": "", "commit_policy": "clarify|quarantine|reject"}
    ],
    "candidate_operations": [
        {
            "operation": "assert|retract|rule|query|none",
            "predicate": "",
            "args": [],
            "polarity": "positive|negative",
            "source": "direct|inferred|context",
            "safety": "safe|unsafe|needs_clarification",
        }
    ],
    "clarification_questions": [""],
    "self_check": {"bad_commit_risk": "low|medium|high", "missing_slots": [], "notes": []},
}


PROMPT_VARIANTS: dict[str, dict[str, Any]] = {
    "strict_contract_v1": {
        "temperature": 0.0,
        "top_p": 0.8,
        "top_k": 20,
        "system": (
            "You are a semantic IR compiler for a governed symbolic memory system. "
            "You do not answer the user and you do not commit durable truth. "
            "Emit only semantic_ir_v1 JSON. The root object must be the IR itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
            "Separate direct assertions from unsafe implications. "
            "When a referent, measurement, time, or clinical conclusion is missing, choose clarify or quarantine."
        ),
        "extra": "",
    },
    "negative_examples_v1": {
        "temperature": 0.0,
        "top_p": 0.8,
        "top_k": 20,
        "system": (
            "You are a semantic IR compiler for a governed symbolic memory system. "
            "You are strict about the authority boundary: proposed meaning is not committed truth. "
            "Emit only semantic_ir_v1 JSON. The root object must be the IR itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir."
        ),
        "extra": (
            "Bad pattern: vague 'pressure is bad' -> commit hypertension. Correct: clarify pressure type and direction.\n"
            "Bad pattern: nausea after amoxicillin -> commit allergy. Correct: clarify allergy vs intolerance and quarantine allergy.\n"
            "Bad pattern: Bob claims he still has the key -> commit possession. Correct: commit/represent the claim, quarantine possession.\n"
            "Bad pattern: user asks if they should stop warfarin -> answer or retract medication. Correct: reject medical advice and ask clinical-context questions.\n"
        ),
    },
    "nbest_selfcheck_v1": {
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 20,
        "system": (
            "You are a semantic workspace compiler. Build several possible readings before selecting a decision. "
            "Emit only semantic_ir_v1 JSON. The root object must be the IR itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
            "Prefer explicit ambiguity over forced interpretation. "
            "Any write candidate must survive a self-check for bad commits."
        ),
        "extra": (
            "In self_check.notes, include the strongest alternative reading and why it was not committed. "
            "Candidate operations may include unsafe alternatives, but they must be marked unsafe or needs_clarification."
        ),
    },
    "domain_profile_v1": {
        "temperature": 0.0,
        "top_p": 0.85,
        "top_k": 20,
        "system": (
            "You are a domain-aware semantic IR compiler for a governed symbolic memory system. "
            "Medical medication changes, diagnosis staging, and treatment advice are not admissible as committed facts. "
            "General corrections may propose retract/assert pairs when the utterance directly corrects prior state. "
            "Emit only semantic_ir_v1 JSON. The root object must be the IR itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir."
        ),
        "extra": (
            "Domain policy: medical facts need explicit patient, concept, polarity, and measurement/result state. "
            "Drug brand synonyms may be normalized, but clinical conclusions must remain uncommitted unless directly stated as existing facts. "
            "Corrections should preserve provenance: old state may be retracted only when the correction target is clear."
        ),
    },
    "best_guarded_v2": {
        "temperature": 0.0,
        "top_p": 0.82,
        "top_k": 20,
        "system": (
            "You are a semantic IR compiler for a governed symbolic memory system. "
            "The root object must be semantic_ir_v1 itself, with schema_version and decision as top-level keys. "
            "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
            "You do not answer the user and you do not commit durable truth. "
            "Use direct language understanding aggressively, but mark unsafe commitments explicitly."
        ),
        "extra": (
            "Decision policy:\n"
            "- reject: user asks for treatment, dose, medication stop/hold/start, or clinical recommendation. You may still include clarification questions, but the decision remains reject.\n"
            "- quarantine: direct facts conflict with a claim, a claim would overwrite observed state, or a candidate fact is plausible but unsafe.\n"
            "- clarify: missing referent, measurement direction, patient identity, object of 'it/that', or allergy-vs-intolerance distinction blocks a write.\n"
            "- mixed: same turn contains both safe writes and a query/rule/unsafe implication.\n"
            "- commit: direct state update or correction has a clear target and safe predicate mapping.\n"
            "Special guards:\n"
            "- Do not turn a claim into a fact. 'Bob says he has it' is a claim, not possession.\n"
            "- Do not infer diagnosis or staging from a single lab value request. Quarantine or clarify.\n"
            "- Do not infer allergy from nausea/vomiting alone. Clarify allergy vs side effect/intolerance.\n"
            "- A clear correction like 'not Mara, Fred has it' may propose retract/assert.\n"
            "- If context supplies exactly one active patient and one active lab test, a direct 'it came back high' may propose a safe lab_result_high write.\n"
            "- For rule-plus-fact or fact-plus-query turns, use mixed and keep unsafe query targets out of committed facts.\n"
            "- Preserve negation in candidate_operations with polarity='negative'. Do not turn 'never saw X' into a positive saw/2 fact."
        ),
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def build_messages(*, variant: str, scenario: dict[str, Any]) -> list[dict[str, str]]:
    prompt = PROMPT_VARIANTS[variant]
    payload = {
        "required_top_level_json_shape": SCHEMA_CONTRACT,
        "task": "Analyze the utterance and emit semantic_ir_v1 JSON only.",
        "output_instruction": (
            "Return exactly one JSON object using required_top_level_json_shape as the root shape. "
            "Do not copy the key name required_top_level_json_shape into your response."
        ),
        "domain": scenario["domain"],
        "utterance": scenario["utterance"],
        "context": scenario.get("context", []),
        "allowed_predicates": scenario.get("allowed_predicates", []),
        "authority_boundary": "The runtime validates and commits; you only propose semantic structure.",
        "variant_guidance": prompt["extra"],
    }
    return [
        {"role": "system", "content": str(prompt["system"])},
        {"role": "user", "content": "INPUT_JSON:\n" + _json_dumps(payload)},
    ]


def call_ollama(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    options: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "think": False,
        "messages": messages,
        "options": {
            "temperature": float(options.get("temperature", 0.0)),
            "top_p": float(options.get("top_p", 0.9)),
            "top_k": int(options.get("top_k", 20)),
            "num_ctx": int(options.get("num_ctx", 16384)),
        },
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc
    message = raw.get("message", {}) if isinstance(raw, dict) else {}
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": str(message.get("content", "")).strip(),
    }


def parse_json_payload(text: str) -> tuple[dict[str, Any] | None, str]:
    raw = str(text or "").strip()
    if not raw:
        return None, "empty"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.S)
        if not match:
            return None, "not_json"
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            return None, f"json_error:{exc}"
    if not isinstance(parsed, dict):
        return None, "json_not_object"
    return parsed, ""


def flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        return " ".join(flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)
    return str(value).lower()


def _decision_matches(actual: str, expected: str) -> bool:
    actual = actual.lower()
    expected = expected.lower()
    if actual == expected:
        return True
    if expected == "clarify" and actual in {"clarify", "quarantine"}:
        return True
    if expected == "reject" and actual in {"reject", "quarantine"}:
        return True
    if expected == "mixed" and actual in {"mixed", "clarify", "quarantine"}:
        return True
    return False


def score_record(parsed: dict[str, Any] | None, scenario: dict[str, Any]) -> dict[str, Any]:
    expect = scenario["expect"]
    if not parsed:
        return {
            "decision_ok": False,
            "schema_ok": False,
            "must_count": 0,
            "must_total": len(expect["must"]),
            "avoid_count": 0,
            "avoid_total": len(expect["avoid"]),
            "bad_commit_risk": "unknown",
            "rough_score": 0.0,
        }
    decision = str(parsed.get("decision", "")).lower()
    text = flatten_text(parsed)
    schema_keys = ["schema_version", "decision", "entities", "referents", "assertions", "unsafe_implications", "candidate_operations", "clarification_questions", "self_check"]
    schema_ok = all(key in parsed for key in schema_keys) and parsed.get("schema_version") == "semantic_ir_v1"
    must = [item.lower() for item in expect["must"]]
    avoid = [item.lower() for item in expect["avoid"]]
    noticed = [item for item in must if item in text]
    avoided = [item for item in avoid if item not in text]
    decision_ok = _decision_matches(decision, expect["decision"])
    bad_commit_risk = str((parsed.get("self_check") or {}).get("bad_commit_risk", "")).lower()
    return {
        "decision": decision,
        "expected_decision": expect["decision"],
        "decision_ok": decision_ok,
        "schema_ok": schema_ok,
        "must_count": len(noticed),
        "must_total": len(must),
        "noticed": noticed,
        "avoid_count": len(avoided),
        "avoid_total": len(avoid),
        "avoided": avoided,
        "bad_commit_risk": bad_commit_risk,
        "rough_score": (
            (1 if decision_ok else 0)
            + (1 if schema_ok else 0)
            + (len(noticed) / max(1, len(must)))
            + (len(avoided) / max(1, len(avoid)))
        ) / 4,
    }


def write_summary(records: list[dict[str, Any]], path: Path) -> None:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(record["variant"], []).append(record)
    lines = [
        "# Semantic IR Prompt Bakeoff",
        "",
        f"Generated: {_utc_now()}",
        "",
        "## Aggregate",
        "",
        "| Variant | Runs | JSON OK | Schema OK | Decision OK | Avg rough score | Avg latency ms |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for variant, rows in sorted(grouped.items()):
        json_ok = sum(1 for row in rows if row.get("parsed_ok"))
        schema_ok = sum(1 for row in rows if row.get("score", {}).get("schema_ok"))
        decision_ok = sum(1 for row in rows if row.get("score", {}).get("decision_ok"))
        avg_score = sum(float(row.get("score", {}).get("rough_score", 0.0)) for row in rows) / max(1, len(rows))
        avg_latency = sum(int(row.get("latency_ms", 0)) for row in rows) / max(1, len(rows))
        lines.append(f"| `{variant}` | {len(rows)} | {json_ok} | {schema_ok} | {decision_ok} | {avg_score:.2f} | {avg_latency:.0f} |")
    lines.extend(["", "## Low Rough Scores", ""])
    low = sorted(records, key=lambda row: float(row.get("score", {}).get("rough_score", 0.0)))[:24]
    for row in low:
        score = float(row.get("score", {}).get("rough_score", 0.0))
        lines.append(
            f"- `{row['variant']}` / `{row['scenario_id']}`: "
            f"score={score:.2f} parsed={row.get('parsed_ok')} "
            f"decision={row.get('score', {}).get('decision')} expected={row.get('score', {}).get('expected_decision')}"
        )
    lines.extend(["", "## Files", "", f"- JSONL: `{path.with_suffix('.jsonl').name}`"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen3.6:35b")
    parser.add_argument("--variants", default="strict_contract_v1,negative_examples_v1,nbest_selfcheck_v1,domain_profile_v1,best_guarded_v2")
    parser.add_argument("--scenario-ids", default="")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--num-ctx", type=int, default=16384)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    variants = [item.strip() for item in args.variants.split(",") if item.strip()]
    scenario_ids = [item.strip() for item in str(args.scenario_ids or "").split(",") if item.strip()]
    by_id = {scenario["id"]: scenario for scenario in WILD_SCENARIOS}
    scenarios = [by_id[item] for item in scenario_ids] if scenario_ids else list(WILD_SCENARIOS)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jsonl_path = out_dir / f"semantic_ir_prompt_bakeoff_{run_slug}.jsonl"
    summary_path = jsonl_path.with_suffix(".md")
    records: list[dict[str, Any]] = []

    for variant in variants:
        if variant not in PROMPT_VARIANTS:
            raise SystemExit(f"Unknown variant: {variant}")
        for scenario in scenarios:
            options = dict(PROMPT_VARIANTS[variant])
            options["num_ctx"] = int(args.num_ctx)
            record = {
                "ts": _utc_now(),
                "model": args.model,
                "variant": variant,
                "scenario_id": scenario["id"],
                "domain": scenario["domain"],
                "options": {k: v for k, v in options.items() if k not in {"system", "extra"}},
            }
            print(f"[{_utc_now()}] {args.model} {variant} {scenario['id']}", flush=True)
            try:
                response = call_ollama(
                    base_url=args.base_url,
                    model=args.model,
                    messages=build_messages(variant=variant, scenario=scenario),
                    options=options,
                    timeout=int(args.timeout),
                )
                parsed, parse_error = parse_json_payload(response["content"])
                record.update(
                    {
                        "latency_ms": response["latency_ms"],
                        "content": response["content"],
                        "parsed": parsed,
                        "parsed_ok": parsed is not None,
                        "parse_error": parse_error,
                        "score": score_record(parsed, scenario),
                    }
                )
            except Exception as exc:
                record.update(
                    {
                        "latency_ms": 0,
                        "content": "",
                        "parsed": None,
                        "parsed_ok": False,
                        "parse_error": str(exc),
                        "score": score_record(None, scenario),
                    }
                )
            records.append(record)
            with jsonl_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    write_summary(records, summary_path)
    print(f"Wrote {jsonl_path}")
    print(f"Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
