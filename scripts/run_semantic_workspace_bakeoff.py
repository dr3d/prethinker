#!/usr/bin/env python3
"""Run a local model bakeoff for Prethinker semantic-workspace research.

Outputs stay under tmp/ by default because raw model traces are local research data.
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
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "semantic_bakeoff"


SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "medical_pressure_vague",
        "domain": "medical",
        "utterance": "Mara's pressure is bad lately.",
        "context": [],
        "allowed_predicates": [
            "taking/2",
            "has_condition/2",
            "has_symptom/2",
            "has_allergy/2",
            "underwent_lab_test/2",
            "lab_result_high/2",
            "lab_result_rising/2",
            "lab_result_abnormal/2",
            "pregnant/1",
        ],
        "expect": {
            "action": "clarify",
            "must_notice": ["pressure", "blood pressure", "chest pressure"],
            "avoid_commit": ["hypertension", "lab_result_high"],
        },
    },
    {
        "id": "medical_pressure_clarified",
        "domain": "medical",
        "utterance": "Mara's blood pressure reading was high.",
        "context": ["Previous held turn: Mara's pressure is bad lately."],
        "allowed_predicates": ["lab_result_high/2", "has_condition/2", "has_symptom/2"],
        "expect": {
            "action": "commit",
            "must_notice": ["lab_result_high", "blood_pressure_measurement"],
            "avoid_commit": ["hypertension"],
        },
    },
    {
        "id": "medical_pronoun_creatinine_after_two_patients",
        "domain": "medical",
        "utterance": "Her creatinine was repeated this afternoon.",
        "context": ["taking(priya, warfarin).", "has_condition(mara, asthma)."],
        "allowed_predicates": ["underwent_lab_test/2"],
        "expect": {
            "action": "clarify",
            "must_notice": ["her", "Priya", "Mara", "serum_creatinine_measurement"],
            "avoid_commit": ["underwent_lab_test(priya", "underwent_lab_test(mara"],
        },
    },
    {
        "id": "medical_brand_pregnancy_context",
        "domain": "medical",
        "utterance": "Priya is taking Coumadin and she is pregnant.",
        "context": [],
        "allowed_predicates": ["taking/2", "pregnant/1"],
        "expect": {
            "action": "commit",
            "must_notice": ["warfarin", "pregnant", "Priya"],
            "avoid_commit": ["advice", "stop"],
        },
    },
    {
        "id": "medical_sugar_shorthand",
        "domain": "medical",
        "utterance": "Priya's sugar looked bad this morning.",
        "context": [],
        "allowed_predicates": ["lab_result_high/2", "has_condition/2"],
        "expect": {
            "action": "clarify",
            "must_notice": ["sugar", "blood glucose", "diabetes"],
            "avoid_commit": ["type_2_diabetes_mellitus", "lab_result_high"],
        },
    },
    {
        "id": "medical_allergy_vs_side_effect",
        "domain": "medical",
        "utterance": "Priya says amoxicillin made her nauseous, so she avoids it.",
        "context": [],
        "allowed_predicates": ["has_allergy/2", "taking/2", "has_symptom/2"],
        "expect": {
            "action": "clarify",
            "must_notice": ["amoxicillin", "nauseous", "allergy", "intolerance"],
            "avoid_commit": ["has_allergy(priya, amoxicillin"],
        },
    },
    {
        "id": "medical_active_patient_it_high",
        "domain": "medical",
        "utterance": "It came back high, and she is still taking metformin.",
        "context": ["Maya is the active patient.", "Maya underwent an A1C test."],
        "allowed_predicates": ["lab_result_high/2", "taking/2"],
        "expect": {
            "action": "commit",
            "must_notice": ["Maya", "A1C", "metformin", "lab_result_high"],
            "avoid_commit": ["diabetes", "she"],
        },
    },
    {
        "id": "correction_cart_holder",
        "domain": "general",
        "utterance": "Actually, the cart is with Fred now, not Mara.",
        "context": ["cart_with(mara, cart)."],
        "allowed_predicates": ["cart_with/2"],
        "expect": {
            "action": "commit",
            "must_notice": ["retract", "cart_with(mara", "cart_with(fred"],
            "avoid_commit": ["cart_with(mara, cart)", "without retract"],
        },
    },
    {
        "id": "shipping_it_unresolved",
        "domain": "general",
        "utterance": "Remember that it ships next week.",
        "context": [],
        "allowed_predicates": ["ships/2"],
        "expect": {
            "action": "clarify",
            "must_notice": ["it", "referent"],
            "avoid_commit": ["ships(it", "launch_plan"],
        },
    },
    {
        "id": "family_pronoun_ambiguous",
        "domain": "general",
        "utterance": "His brother lives in Morro Bay.",
        "context": ["mother(scott, ann).", "brother(priya, omar)."],
        "allowed_predicates": ["brother/2", "lives_in/2"],
        "expect": {
            "action": "clarify",
            "must_notice": ["his", "Scott", "Priya"],
            "avoid_commit": ["brother_of_scott", "brother_of_priya"],
        },
    },
    {
        "id": "ancestor_rule_safe_recursion",
        "domain": "general",
        "utterance": (
            "If someone is a parent of a person, they are an ancestor of that person. "
            "And if someone is a parent of an ancestor, they are also an ancestor."
        ),
        "context": ["parent(cora, dax).", "parent(dax, emma)."],
        "allowed_predicates": ["parent/2", "ancestor/2"],
        "expect": {
            "action": "commit",
            "must_notice": ["ancestor", "parent", "recursion"],
            "avoid_commit": ["ancestor(X, Y), ancestor(Y, Z)"],
        },
    },
    {
        "id": "policy_exception_rule",
        "domain": "general",
        "utterance": "If an item is flagged, it requires review. Exempt items do not require review. Box7 is flagged and exempt.",
        "context": ["Use requires_review/1, flagged/1, exempt/1."],
        "allowed_predicates": ["requires_review/1", "flagged/1", "exempt/1"],
        "expect": {
            "action": "mixed",
            "must_notice": ["flagged", "exempt", "exception", "requires_review"],
            "avoid_commit": ["requires_review(box7)"],
        },
    },
    {
        "id": "ingredient_bundle_query_boundary",
        "domain": "general",
        "utterance": "Muffins are made with flour, cranberries, and walnuts. Can you make muffins with raisins?",
        "context": [],
        "allowed_predicates": ["made_with/2"],
        "expect": {
            "action": "mixed",
            "must_notice": ["flour", "cranberries", "walnuts", "raisins", "query"],
            "avoid_commit": ["made_with(muffins, raisins"],
        },
    },
    {
        "id": "temporal_false_claim",
        "domain": "state_change",
        "utterance": "Alice gave the key to Bob. Bob later gave it to Clara. Bob says he still has it.",
        "context": [],
        "allowed_predicates": ["transferred/4", "possessed/3", "claimed/3"],
        "expect": {
            "action": "quarantine",
            "must_notice": ["state change", "claim", "Bob", "Clara"],
            "avoid_commit": ["possessed(bob, key, now)"],
        },
    },
    {
        "id": "medical_advice_boundary",
        "domain": "medical",
        "utterance": "Should Priya stop taking warfarin?",
        "context": ["taking(priya, warfarin)."],
        "allowed_predicates": ["taking/2"],
        "expect": {
            "action": "reject",
            "must_notice": ["advice", "question", "not commit"],
            "avoid_commit": ["stop", "retract"],
        },
    },
    {
        "id": "medical_unknown_predicate_pressure",
        "domain": "medical",
        "utterance": "Leo's eGFR is 48, stage him and add CKD stage 3.",
        "context": [],
        "allowed_predicates": ["lab_result_abnormal/2", "has_condition/2"],
        "expect": {
            "action": "clarify",
            "must_notice": ["egfr", "stage", "ckd", "predicate"],
            "avoid_commit": ["ckd_stage", "has_condition(leo, ckd_stage_3"],
        },
    },
]


MODES: dict[str, dict[str, Any]] = {
    "semantic_workspace": {
        "temperature": 0.2,
        "top_p": 0.9,
        "top_k": 20,
        "think": True,
    },
    "ambiguity_critic": {
        "temperature": 0.1,
        "top_p": 0.85,
        "top_k": 20,
        "think": True,
    },
    "strict_compiler": {
        "temperature": 0.0,
        "top_p": 0.8,
        "top_k": 20,
        "think": False,
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def build_prompt(*, mode: str, scenario: dict[str, Any]) -> str:
    context = scenario.get("context", [])
    allowed = scenario.get("allowed_predicates", [])
    base = {
        "domain": scenario["domain"],
        "utterance": scenario["utterance"],
        "context": context,
        "allowed_predicates": allowed,
        "authority_boundary": (
            "You are not allowed to commit durable KB state. You may only analyze, "
            "propose candidates, and recommend commit/clarify/quarantine/reject."
        ),
    }
    if mode == "semantic_workspace":
        return (
            "You are a semantic workspace builder for a governed neuro-symbolic memory system.\n"
            "Do not answer the user. Do not commit facts. Analyze possible meanings richly.\n"
            "Return JSON only with keys: route, possible_readings, asserted, implied_unsafe, "
            "missing_slots, candidate_operations, clarification_questions, risks, recommended_action.\n"
            "candidate_operations items must include: operation, clause, support, commit_policy.\n"
            "Use commit_policy values: commit, clarify, quarantine, reject.\n\n"
            f"INPUT_JSON:\n{_json_dumps(base)}"
        )
    if mode == "ambiguity_critic":
        return (
            "You are a conservative ambiguity critic for a governed symbolic KB.\n"
            "Your job is to identify what would go wrong if a parser committed too eagerly.\n"
            "Return JSON only with keys: unsafe_assumptions, ambiguity_map, direct_assertions, "
            "implied_only, contradiction_risks, missing_questions, recommended_action, best_question.\n"
            "recommended_action must be one of: commit, clarify, quarantine, reject, answer.\n\n"
            f"INPUT_JSON:\n{_json_dumps(base)}"
        )
    if mode == "strict_compiler":
        return (
            "You are a strict candidate compiler. Produce candidate Prolog-like operations, "
            "but mark unsafe candidates instead of forcing a commit.\n"
            "Return JSON only with keys: intent, facts, rules, queries, retractions, "
            "candidate_operations, needs_clarification, clarification_question, risks, commit_policy.\n"
            "Use only allowed predicates when possible. Do not invent facts to fill missing slots.\n\n"
            f"INPUT_JSON:\n{_json_dumps(base)}"
        )
    raise ValueError(f"unknown mode: {mode}")


def call_ollama(
    *,
    base_url: str,
    model: str,
    prompt: str,
    options: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    thinking_fallback = False
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "think": bool(options.get("think", False)),
        "messages": [{"role": "user", "content": prompt}],
        "options": {
            "temperature": float(options.get("temperature", 0.0)),
            "top_p": float(options.get("top_p", 0.9)),
            "top_k": int(options.get("top_k", 20)),
            "num_ctx": int(options.get("num_ctx", 16384)),
        },
    }
    started = time.perf_counter()
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 400 and payload.get("think") and "does not support thinking" in body:
            thinking_fallback = True
            payload["think"] = False
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{base_url.rstrip('/')}/api/chat",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = json.loads(response.read().decode("utf-8"))
        else:
            raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc
    latency_ms = int((time.perf_counter() - started) * 1000)
    message = raw.get("message", {}) if isinstance(raw, dict) else {}
    return {
        "latency_ms": latency_ms,
        "raw": raw,
        "content": str(message.get("content", "")).strip(),
        "thinking": str(message.get("thinking", "")).strip(),
        "thinking_fallback": thinking_fallback,
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


def score_record(parsed: dict[str, Any] | None, scenario: dict[str, Any]) -> dict[str, Any]:
    expect = scenario.get("expect", {})
    text = flatten_text(parsed or {})
    recommended = ""
    if isinstance(parsed, dict):
        recommended = str(
            parsed.get("recommended_action")
            or parsed.get("commit_policy")
            or parsed.get("intent")
            or ""
        ).lower()
    must_notice = [str(item).lower() for item in expect.get("must_notice", [])]
    avoid_commit = [str(item).lower() for item in expect.get("avoid_commit", [])]
    noticed = [item for item in must_notice if item in text]
    avoided = [item for item in avoid_commit if item not in text]
    expected_action = str(expect.get("action", "")).lower()
    action_ok = False
    action_text = f"{recommended} {text}"
    if expected_action:
        if expected_action == "mixed":
            action_ok = "mixed" in recommended or ("query" in text and ("assert" in text or "commit" in text))
        elif expected_action == "commit":
            negative_commit = "do not commit" in action_text or "not commit" in action_text
            action_ok = ("commit" in action_text or "assert" in action_text) and not negative_commit
        elif expected_action == "clarify":
            action_ok = (
                "clarify" in action_text
                or "clarification" in action_text
                or "needs_clarification" in action_text
            )
        elif expected_action == "quarantine":
            action_ok = "quarantine" in action_text or "claim" in text
        elif expected_action == "reject":
            action_ok = "reject" in action_text or "not commit" in text or "do not commit" in text
    return {
        "expected_action": expected_action,
        "recommended_signal": recommended,
        "action_ok": action_ok,
        "must_notice_count": len(noticed),
        "must_notice_total": len(must_notice),
        "noticed": noticed,
        "avoid_count": len(avoided),
        "avoid_total": len(avoid_commit),
        "avoided": avoided,
        "rough_score": (
            (1 if action_ok else 0)
            + (len(noticed) / max(1, len(must_notice)))
            + (len(avoided) / max(1, len(avoid_commit)))
        ) / 3,
    }


def write_summary(records: list[dict[str, Any]], path: Path) -> None:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault((record["model"], record["mode"]), []).append(record)
    lines = [
        "# Semantic Workspace Bakeoff",
        "",
        f"Generated: {_utc_now()}",
        "",
        "## Aggregate",
        "",
        "| Model | Mode | Runs | JSON OK | Avg rough score | Avg latency ms |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for (model, mode), rows in sorted(grouped.items()):
        json_ok = sum(1 for row in rows if row.get("parsed_ok"))
        avg_score = sum(float(row.get("score", {}).get("rough_score", 0.0)) for row in rows) / max(1, len(rows))
        avg_latency = sum(int(row.get("latency_ms", 0)) for row in rows) / max(1, len(rows))
        lines.append(f"| `{model}` | `{mode}` | {len(rows)} | {json_ok} | {avg_score:.2f} | {avg_latency:.0f} |")
    lines.extend(["", "## Notable Failures", ""])
    failures = [
        row for row in records
        if not row.get("parsed_ok") or float(row.get("score", {}).get("rough_score", 0.0)) < 0.55
    ][:30]
    if not failures:
        lines.append("No low rough-score records in this run.")
    for row in failures:
        err = row.get("parse_error") or ""
        score = float(row.get("score", {}).get("rough_score", 0.0))
        lines.append(
            f"- `{row['model']}` / `{row['mode']}` / `{row['scenario_id']}`: "
            f"score={score:.2f} parsed={row.get('parsed_ok')} {err}"
        )
    lines.extend(["", "## Files", "", f"- JSONL: `{path.with_suffix('.jsonl').name}`"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default="qwen3.5:9b,qwen3.6:27b,qwen3.6:35b")
    parser.add_argument("--modes", default="semantic_workspace,ambiguity_critic,strict_compiler")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--limit-scenarios", type=int, default=0)
    parser.add_argument(
        "--scenario-ids",
        default="",
        help="Comma-separated scenario ids to run. Defaults to all scenarios or --limit-scenarios.",
    )
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    models = [item.strip() for item in args.models.split(",") if item.strip()]
    modes = [item.strip() for item in args.modes.split(",") if item.strip()]
    scenario_ids = [item.strip() for item in str(args.scenario_ids or "").split(",") if item.strip()]
    if scenario_ids:
        by_id = {scenario["id"]: scenario for scenario in SCENARIOS}
        missing = [scenario_id for scenario_id in scenario_ids if scenario_id not in by_id]
        if missing:
            raise SystemExit(f"Unknown scenario id(s): {', '.join(missing)}")
        scenarios = [by_id[scenario_id] for scenario_id in scenario_ids]
    else:
        scenarios = SCENARIOS[: int(args.limit_scenarios)] if int(args.limit_scenarios) > 0 else list(SCENARIOS)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    seen: set[tuple[str, str, str]] = set()
    records: list[dict[str, Any]] = []
    if args.resume:
        existing_runs = sorted(out_dir.glob("semantic_bakeoff_*.jsonl"), key=lambda item: item.stat().st_mtime)
        jsonl_path = existing_runs[-1] if existing_runs else None
    else:
        jsonl_path = None
    if jsonl_path is None:
        run_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jsonl_path = out_dir / f"semantic_bakeoff_{run_slug}.jsonl"
    elif jsonl_path.exists():
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                existing = json.loads(line)
            except json.JSONDecodeError:
                continue
            records.append(existing)
            seen.add((existing.get("model", ""), existing.get("mode", ""), existing.get("scenario_id", "")))
    summary_path = jsonl_path.with_suffix(".md")

    for model in models:
        for mode in modes:
            if mode not in MODES:
                raise SystemExit(f"Unknown mode: {mode}")
            for scenario in scenarios:
                key = (model, mode, scenario["id"])
                if args.resume and key in seen:
                    continue
                options = dict(MODES[mode])
                options["num_ctx"] = int(args.num_ctx)
                prompt = build_prompt(mode=mode, scenario=scenario)
                print(f"[{_utc_now()}] {model} {mode} {scenario['id']}", flush=True)
                record = {
                    "ts": _utc_now(),
                    "model": model,
                    "mode": mode,
                    "scenario_id": scenario["id"],
                    "domain": scenario["domain"],
                    "options": options,
                }
                try:
                    response = call_ollama(
                        base_url=args.base_url,
                        model=model,
                        prompt=prompt,
                        options=options,
                        timeout=int(args.timeout),
                    )
                    parsed, parse_error = parse_json_payload(response["content"])
                    record.update(
                        {
                            "latency_ms": response["latency_ms"],
                            "content": response["content"],
                            "thinking": response["thinking"],
                            "thinking_fallback": response["thinking_fallback"],
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
                            "thinking": "",
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
