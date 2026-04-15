#!/usr/bin/env python3
"""
Feature-flagged ingestion frontend scaffold inspired by GraphMERT-style constraints.

Stages:
1) discover_spans
2) rank_allowed_predicates
3) assemble_constrained_arguments
4) produce parse proposal for deterministic admission checks

This module intentionally stays lightweight and deterministic.
It does not mutate KB state and does not call external models.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "had",
    "has",
    "have",
    "if",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "there",
    "they",
    "this",
    "to",
    "was",
    "were",
    "while",
    "with",
}

QUESTION_PREFIXES = {
    "who",
    "what",
    "when",
    "where",
    "why",
    "how",
    "which",
    "is",
    "are",
    "was",
    "were",
    "do",
    "does",
    "did",
    "can",
    "could",
    "should",
    "would",
    "has",
    "have",
    "had",
}

WRITE_RETRACT_TERMS = {
    "retract",
    "remove",
    "undo",
    "delete",
    "cancel",
}

PREDICATE_HINTS: dict[str, tuple[str, ...]] = {
    "parent": ("parent", "mom", "mother", "dad", "father"),
    "brother": ("brother",),
    "sister": ("sister",),
    "sibling": ("sibling", "brother", "sister"),
    "ancestor": ("ancestor",),
    "belongs_to": ("belongs", "owned", "owner"),
    "has_bed": ("bed",),
    "has_chair": ("chair",),
    "has_porridge": ("porridge", "bowl"),
    "walked_through": ("walked", "through"),
    "found": ("found",),
    "saw": ("saw", "seen"),
    "ate": ("ate", "eaten"),
    "sat_in": ("sat", "sitting"),
    "lay_in": ("lay", "lying"),
    "fell_asleep_in": ("asleep", "slept", "sleep"),
    "returned_home": ("returned", "home"),
    "went_upstairs": ("upstairs",),
    "broke": ("broke", "broken"),
}


@dataclass(frozen=True)
class Signature:
    name: str
    arity: int


def _atomize(text: str) -> str:
    lowered = str(text or "").strip().lower()
    lowered = re.sub(r"'s\b", "", lowered)
    lowered = re.sub(r"[^a-z0-9]+", "_", lowered)
    lowered = re.sub(r"_+", "_", lowered).strip("_")
    return lowered


def _tokenize(text: str) -> list[str]:
    return [
        tok
        for tok in re.findall(r"[a-z][a-z0-9_]*", text.lower())
        if tok and tok not in STOPWORDS
    ]


def _parse_signature(raw: str) -> Signature | None:
    text = str(raw or "").strip().lower()
    if not text or "/" not in text:
        return None
    name, arity_text = text.split("/", 1)
    name = name.strip()
    arity_text = arity_text.strip()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        return None
    if not arity_text.isdigit():
        return None
    return Signature(name=name, arity=int(arity_text))


def infer_intent(text: str) -> str:
    lowered = str(text or "").strip().lower()
    if not lowered:
        return "other"

    if any(term in lowered for term in WRITE_RETRACT_TERMS):
        return "retract"

    if re.search(r"\bif\b", lowered) and (
        re.search(r"\bthen\b", lowered)
        or "," in lowered
        or re.search(r"\bimplies\b", lowered)
        or re.search(r"\bwhenever\b", lowered)
    ):
        return "assert_rule"

    prefix = lowered.split(maxsplit=1)[0] if lowered.split() else ""
    if lowered.endswith("?") or prefix in QUESTION_PREFIXES:
        return "query"

    if lowered.startswith("/"):
        return "other"

    return "assert_fact"


def discover_spans(text: str, known_atoms: list[str] | set[str]) -> dict[str, Any]:
    raw = str(text or "")
    lowered = raw.lower()

    quoted_raw = re.findall(r"['\"]([^'\"]{2,80})['\"]", raw)
    quoted = []
    for q in quoted_raw:
        atom = _atomize(q)
        if atom:
            quoted.append(atom)

    possessive_raw = re.findall(r"\b([A-Za-z][A-Za-z0-9_-]{1,40})'s\b", raw)
    possessive = []
    for p in possessive_raw:
        atom = _atomize(p)
        if atom:
            possessive.append(atom)

    tokens = _tokenize(lowered)

    known_hits: list[str] = []
    known_space_map = {
        str(atom): str(atom).replace("_", " ") for atom in (known_atoms or []) if str(atom).strip()
    }
    for atom, phrase in known_space_map.items():
        if phrase and re.search(rf"\b{re.escape(phrase)}\b", lowered):
            known_hits.append(atom)

    candidate_entities: list[str] = []
    for row in quoted + possessive + known_hits + tokens:
        atom = _atomize(row)
        if atom and atom not in candidate_entities:
            candidate_entities.append(atom)

    return {
        "quoted": quoted,
        "possessive": possessive,
        "known_hits": known_hits,
        "candidate_entities": candidate_entities,
        "tokens": tokens,
    }


def rank_allowed_predicates(
    text: str,
    allowed_signatures: list[str] | set[str],
    *,
    max_candidates: int = 8,
) -> list[dict[str, Any]]:
    tokens = set(_tokenize(text))
    scored: list[dict[str, Any]] = []

    for raw in sorted({str(x).strip() for x in allowed_signatures if str(x).strip()}):
        sig = _parse_signature(raw)
        if sig is None:
            continue
        name_tokens = [tok for tok in sig.name.split("_") if tok]
        hints = set(name_tokens)
        extra_hints = PREDICATE_HINTS.get(sig.name, ())
        for hint in extra_hints:
            hint_atom = _atomize(hint)
            if hint_atom:
                hints.add(hint_atom)

        overlap = len(tokens.intersection(hints))
        score = 0.1 + (0.18 * overlap)

        if infer_intent(text) == "query" and sig.arity >= 1:
            score += 0.04
        if infer_intent(text) in {"assert_fact", "retract"} and sig.arity in {1, 2, 3}:
            score += 0.03

        if score <= 0.0:
            continue

        scored.append(
            {
                "signature": f"{sig.name}/{sig.arity}",
                "predicate": sig.name,
                "arity": sig.arity,
                "score": round(min(1.0, score), 6),
                "matched_hints": sorted(tokens.intersection(hints)),
            }
        )

    scored.sort(key=lambda row: (float(row["score"]), row["signature"]), reverse=True)
    return scored[: max(1, int(max_candidates))]


def _format_clause(predicate: str, args: list[str]) -> str:
    return f"{predicate}({', '.join(args)})."


def _variables_for_arity(arity: int) -> list[str]:
    alphabet = "XYZUVWABCDEFGHIJKLMNOPQRST"
    rows: list[str] = []
    for idx in range(max(0, int(arity))):
        if idx < len(alphabet):
            rows.append(alphabet[idx])
        else:
            rows.append(f"V{idx+1}")
    return rows


def assemble_constrained_parse(
    *,
    utterance: str,
    ranked_predicates: list[dict[str, Any]],
    span_bundle: dict[str, Any],
    intent: str,
    min_score: float,
) -> tuple[dict[str, Any] | None, list[str]]:
    notes: list[str] = []
    if intent == "other":
        notes.append("intent_other")
        return None, notes
    if intent == "assert_rule":
        notes.append("assert_rule_not_scaffolded")
        return None, notes
    if not ranked_predicates:
        notes.append("no_ranked_predicates")
        return None, notes

    top = ranked_predicates[0]
    if float(top.get("score", 0.0) or 0.0) < float(min_score):
        notes.append("top_predicate_below_min_score")
        return None, notes

    predicate = str(top.get("predicate", "")).strip()
    arity = int(top.get("arity", 0) or 0)
    if not predicate or arity <= 0:
        notes.append("invalid_top_predicate")
        return None, notes

    entities_raw = span_bundle.get("candidate_entities", [])
    entities = [str(x) for x in entities_raw if str(x).strip()]

    if intent == "query":
        args = entities[:arity]
        if len(args) < arity:
            args.extend(_variables_for_arity(arity - len(args)))
    else:
        if len(entities) < arity:
            notes.append("insufficient_ground_entities_for_write")
            return None, notes
        args = entities[:arity]

    clause = _format_clause(predicate, args)

    facts: list[str] = []
    rules: list[str] = []
    queries: list[str] = []
    logic_string = clause
    if intent == "query":
        queries = [clause]
    elif intent == "retract":
        facts = [clause]
        fact_term = clause[:-1] if clause.endswith(".") else clause
        logic_string = f"retract({fact_term})."
    else:
        facts = [clause]

    atoms = [arg for arg in args if not re.fullmatch(r"[A-Z][A-Za-z0-9_]*", arg)]
    variables = [arg for arg in args if re.fullmatch(r"[A-Z][A-Za-z0-9_]*", arg)]

    confidence_score = round(min(0.95, max(0.25, float(top.get("score", 0.25)))), 6)

    payload = {
        "intent": intent,
        "logic_string": logic_string,
        "components": {
            "atoms": sorted(set(atoms)),
            "variables": sorted(set(variables)),
            "predicates": [predicate],
        },
        "facts": facts,
        "rules": rules,
        "queries": queries,
        "confidence": {
            "overall": confidence_score,
            "intent": min(1.0, confidence_score + 0.08),
            "logic": max(0.0, confidence_score - 0.03),
        },
        "ambiguities": [],
        "needs_clarification": False,
        "uncertainty_score": round(max(0.0, 1.0 - confidence_score), 6),
        "uncertainty_label": "low" if confidence_score >= 0.66 else "medium",
        "clarification_question": "",
        "clarification_reason": "",
        "rationale": "Frontend proposal from constrained slot assembly.",
    }
    return payload, notes


def propose_frontend_parse(
    *,
    utterance: str,
    allowed_signatures: list[str] | set[str],
    known_atoms: list[str] | set[str],
    max_candidates: int = 8,
    min_score: float = 0.35,
) -> dict[str, Any]:
    text = str(utterance or "").strip()
    if not text:
        return {
            "status": "no_input",
            "intent": "other",
            "stages": {},
            "notes": ["empty_utterance"],
            "parse_payload": None,
        }

    intent = infer_intent(text)
    span_bundle = discover_spans(text, known_atoms)
    ranked = rank_allowed_predicates(text, allowed_signatures, max_candidates=max_candidates)
    parse_payload, notes = assemble_constrained_parse(
        utterance=text,
        ranked_predicates=ranked,
        span_bundle=span_bundle,
        intent=intent,
        min_score=min_score,
    )

    status = "proposed" if isinstance(parse_payload, dict) else "no_candidate"
    if status == "no_candidate" and not notes:
        notes = ["no_candidate_generated"]

    top = ranked[0] if ranked else None
    return {
        "status": status,
        "intent": intent,
        "top_predicate": top,
        "stages": {
            "discover_spans": span_bundle,
            "rank_allowed_predicates": ranked,
            "assemble_constrained_arguments": {
                "intent": intent,
                "min_score": float(min_score),
                "max_candidates": int(max_candidates),
                "top_signature": top.get("signature") if isinstance(top, dict) else "",
            },
        },
        "notes": notes,
        "parse_payload": parse_payload,
    }
