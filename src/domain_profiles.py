from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOMAIN_PROFILE_CATALOG = REPO_ROOT / "modelfiles" / "domain_profile_catalog.v0.json"


def load_domain_profile_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = Path(path) if isinstance(path, Path) else DEFAULT_DOMAIN_PROFILE_CATALOG
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def thin_profile_roster(catalog: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    source = catalog if isinstance(catalog, dict) else load_domain_profile_catalog()
    profiles = source.get("profiles", []) if isinstance(source, dict) else []
    roster: list[dict[str, Any]] = []
    if not isinstance(profiles, list):
        return roster
    for row in profiles:
        if not isinstance(row, dict):
            continue
        profile_id = str(row.get("profile_id", "")).strip()
        description = str(row.get("description", "")).strip()
        if not profile_id or not description:
            continue
        roster.append(
            {
                "profile_id": profile_id,
                "status": str(row.get("status", "")).strip(),
                "description": description,
                "use_when": _string_list(row.get("use_when")),
                "avoid_when": _string_list(row.get("avoid_when")),
            }
        )
    return roster


def load_profile_package(profile_id: str, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    profile = profile_catalog_entry(profile_id, catalog)
    source = str(profile.get("thick_context_source", "")).strip()
    if not source or source.startswith("future "):
        return {}
    path = Path(source)
    if not path.is_absolute():
        path = REPO_ROOT / "modelfiles" / path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def profile_catalog_entry(profile_id: str, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    wanted = str(profile_id or "").strip()
    if not wanted:
        return {}
    source = catalog if isinstance(catalog, dict) else load_domain_profile_catalog()
    profiles = source.get("profiles", []) if isinstance(source, dict) else []
    if not isinstance(profiles, list):
        return {}
    for row in profiles:
        if isinstance(row, dict) and str(row.get("profile_id", "")).strip() == wanted:
            return dict(row)
    return {}


def profile_package_contracts(profile: dict[str, Any]) -> list[dict[str, Any]]:
    palette = profile.get("canonical_palette", []) if isinstance(profile, dict) else []
    if not isinstance(palette, list):
        return []
    contracts: list[dict[str, Any]] = []
    for row in palette:
        if not isinstance(row, dict):
            continue
        signature = str(row.get("signature", "")).strip()
        if not signature:
            continue
        contract = {
            "signature": signature,
            "arguments": _string_list(row.get("arguments")),
        }
        validators = row.get("validators", row.get("admission_validators", []))
        if isinstance(validators, list) and validators:
            contract["validators"] = [item for item in validators if isinstance(item, dict)]
        notes = str(row.get("notes", "")).strip()
        if notes:
            contract["notes"] = notes
        contracts.append(contract)
    return contracts


def profile_package_context(profile: dict[str, Any]) -> list[str]:
    return _string_list(profile.get("semantic_ir_context") if isinstance(profile, dict) else [])


def select_domain_profile(
    utterance: str,
    *,
    context: list[str] | None = None,
    catalog: dict[str, Any] | None = None,
    min_score: float = 3.0,
) -> dict[str, Any]:
    """Select a likely domain profile from the thin roster.

    This is intentionally boring and inspectable. It is a control-plane helper
    for deciding which thick context package to load; it does not authorize KB
    writes or override mapper admission.
    """

    source = catalog if isinstance(catalog, dict) else load_domain_profile_catalog()
    profiles = source.get("profiles", []) if isinstance(source, dict) else []
    utterance_text = str(utterance or "").casefold()
    context_text = " ".join(str(item) for item in (context or [])).casefold()
    best: dict[str, Any] = {}
    best_score = 0.0
    second_score = 0.0
    for profile in profiles if isinstance(profiles, list) else []:
        if not isinstance(profile, dict):
            continue
        profile_id = str(profile.get("profile_id", "")).strip()
        source_path = str(profile.get("thick_context_source", "")).strip()
        if not profile_id or not source_path or source_path.startswith("future "):
            continue
        utterance_score, reasons = _profile_match_score(utterance_text, profile, catalog=source)
        context_score, context_reasons = _profile_match_score(context_text, profile, catalog=source)
        if _utterance_depends_on_context(utterance_text):
            context_nudge = min(4.0, context_score * 0.8)
        else:
            context_nudge = min(2.0, context_score * 0.2)
        score = utterance_score + context_nudge
        if context_nudge:
            reasons.extend(f"context: {item}" for item in context_reasons[:3])
        if score > best_score:
            second_score = best_score
            best_score = score
            best = {
                "profile_id": profile_id,
                "score": round(score, 2),
                "runner_up_score": round(second_score, 2),
                "reasons": reasons[:8],
            }
        elif score > second_score:
            second_score = score
            if best:
                best["runner_up_score"] = round(second_score, 2)
    if not best or best_score < float(min_score):
        return {
            "profile_id": "general",
            "score": round(best_score, 2),
            "runner_up_score": round(second_score, 2),
            "reasons": ["no catalog profile crossed selection threshold"],
        }
    if best_score - second_score < 1.0:
        return {
            "profile_id": "general",
            "score": round(best_score, 2),
            "runner_up_score": round(second_score, 2),
            "reasons": ["top profile scores were too close for automatic selection", *best.get("reasons", [])[:6]],
        }
    return best


def _profile_match_score(
    text: str,
    profile: dict[str, Any],
    *,
    catalog: dict[str, Any] | None = None,
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    profile_id = str(profile.get("profile_id", "")).strip()
    package = load_profile_package(profile_id, catalog) if profile_id else {}
    selection_hints = package.get("selection_hints", {}) if isinstance(package, dict) else {}
    haystack = " ".join(
        [
            str(profile.get("description", "")),
            " ".join(_string_list(profile.get("use_when"))),
            " ".join(_string_list(selection_hints.get("use_when") if isinstance(selection_hints, dict) else [])),
            " ".join(_string_list(package.get("selection_keywords") if isinstance(package, dict) else [])),
        ]
    ).casefold()
    profile_terms = _term_set(haystack)
    input_terms = _term_set(text)
    overlap = sorted(profile_terms & input_terms)
    if overlap:
        score += min(6.0, len(overlap) * 0.75)
        reasons.append("term overlap: " + ", ".join(overlap[:8]))
    for hint in [
        *_string_list(profile.get("use_when")),
        *_string_list(selection_hints.get("use_when") if isinstance(selection_hints, dict) else []),
    ]:
        hint_score = _hint_score(text, hint)
        if hint_score:
            score += hint_score
            reasons.append(f"use_when matched: {hint}")
    for keyword in _string_list(package.get("selection_keywords") if isinstance(package, dict) else []):
        keyword_score = _keyword_score(text, keyword)
        if keyword_score:
            score += keyword_score
            reasons.append(f"profile keyword: {keyword}")
    for hint in [
        *_string_list(profile.get("avoid_when")),
        *_string_list(selection_hints.get("avoid_when") if isinstance(selection_hints, dict) else []),
    ]:
        hint_score = _hint_score(text, hint)
        if hint_score:
            score -= hint_score * 1.25
            reasons.append(f"avoid_when matched: {hint}")
    score += _profile_specific_bonus(profile_id, text, input_terms, reasons)
    return score, reasons


def _hint_score(text: str, hint: str) -> float:
    raw = str(hint or "").casefold().strip()
    if not raw:
        return 0.0
    if raw in text:
        return 5.0
    terms = _term_set(raw)
    if not terms:
        return 0.0
    hits = terms & _term_set(text)
    if len(hits) >= max(2, min(4, len(terms))):
        return min(4.0, len(hits) * 0.8)
    return 0.0


def _keyword_score(text: str, keyword: str) -> float:
    raw = str(keyword or "").casefold().strip()
    if not raw:
        return 0.0
    if raw in text:
        return 2.5
    terms = _term_set(raw)
    if terms and terms <= _term_set(text):
        return min(2.0, len(terms) * 0.7)
    return 0.0


def _profile_specific_bonus(profile_id: str, text: str, terms: set[str], reasons: list[str]) -> float:
    bonuses: dict[str, set[str]] = {
        "medical@v0": {
            "patient",
            "priya",
            "mara",
            "coumadin",
            "warfarin",
            "creatinine",
            "serum",
            "glucose",
            "pressure",
            "bp",
            "allergy",
            "penicillin",
            "amoxicillin",
            "stomach",
            "upset",
            "rash",
            "intolerance",
            "symptom",
            "pregnant",
        },
        "legal_courtlistener@v0": {
            "courtlistener",
            "court",
            "complaint",
            "alleged",
            "finding",
            "found",
            "holding",
            "docket",
            "opinion",
            "judge",
            "citation",
            "motion",
            "summary",
            "judgment",
            "access",
            "invalidate",
            "transfer",
            "mira",
            "vale",
            "appellant",
            "appellee",
            "case",
        },
        "sec_contracts@v0": {
            "sec",
            "edgar",
            "filing",
            "exhibit",
            "contract",
            "agreement",
            "borrower",
            "lender",
            "shall",
            "must",
            "subject",
            "unless",
            "default",
            "maturity",
            "obligation",
            "covenant",
        },
        "story_world@v0": {
            "story",
            "goldilocks",
            "bears",
            "bear",
            "porridge",
            "bowl",
            "chair",
            "bed",
            "wood",
            "glitch",
            "airlock",
            "jax",
            "widget",
            "fatherbot",
            "nanocell",
            "nano",
            "cell",
            "sonic",
            "zips",
            "fuse",
            "jetpack",
            "boots",
        },
        "probate@v0": {
            "silverton",
            "probate",
            "estate",
            "inheritance",
            "will",
            "beneficiary",
            "charter",
            "amendment",
            "witness",
            "forfeit",
            "forfeiture",
            "ledger",
            "heathrow",
            "stamp",
            "return",
            "trust",
            "half",
            "share",
            "dock",
            "taxes",
            "constable",
            "quentin",
            "quinn",
            "tomas",
            "iris",
            "compass",
            "keeper",
            "archivist",
            "jonas",
            "celia",
            "pavel",
            "leona",
            "crown",
            "arthur",
            "beatrice",
            "alfred",
        },
    }
    hits = sorted(bonuses.get(profile_id, set()) & terms)
    if not hits:
        return 0.0
    reasons.append("profile terms: " + ", ".join(hits[:8]))
    return min(8.0, len(hits) * 1.5)


def _utterance_depends_on_context(text: str) -> bool:
    terms = _term_set(text)
    context_markers = {
        "it",
        "its",
        "they",
        "them",
        "he",
        "she",
        "his",
        "her",
        "this",
        "that",
        "those",
        "same",
        "again",
        "repeat",
        "repeated",
        "back",
        "correction",
        "actually",
        "instead",
    }
    return bool(terms & context_markers)


def _term_set(text: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-z0-9]+", str(text or "").casefold())
        if len(term) > 2 and term not in {"the", "and", "for", "that", "with", "from", "this"}
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
