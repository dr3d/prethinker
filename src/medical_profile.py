from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from src import umls_mvp


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEDICAL_PROFILE = REPO_ROOT / "modelfiles" / "profile.medical.v0.json"
_MEDICAL_PRONOUN_RE = re.compile(r"\b(he|she|his|her|they|their|them|him)\b", re.IGNORECASE)
_BRIDGE_FACT_RE = re.compile(r"^([a-z_][a-z0-9_]*)\((.*)\)\.$")
_FACT_RE = re.compile(r"^([a-z_][a-z0-9_]*)\((.*)\)\.?$")

PREDICATE_ARGUMENT_GROUPS = {
    "taking": {1: {"medication"}},
    "has_condition": {1: {"condition"}},
    "has_symptom": {1: {"symptom_or_finding"}},
    "has_allergy": {1: {"allergy", "medication"}},
    "underwent_lab_test": {1: {"lab_or_procedure"}},
    "lab_result_high": {1: {"lab_or_procedure"}},
    "lab_result_rising": {1: {"lab_or_procedure"}},
    "lab_result_abnormal": {1: {"lab_or_procedure"}},
}

VAGUE_MEDICAL_SURFACE_FORMS = {
    "pressure": "pressure could mean blood pressure, chest pressure, or stress",
    "sugar": "sugar could mean diabetes, blood glucose, or a lab result",
    "kidney": "kidney wording needs a condition, symptom, or lab context",
    "kidneys": "kidney wording needs a condition, symptom, or lab context",
}


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_profile_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = Path(path) if isinstance(path, Path) else DEFAULT_MEDICAL_PROFILE
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def resolve_profile_paths(path: Path | None = None) -> dict[str, Path]:
    manifest_path = Path(path) if isinstance(path, Path) else DEFAULT_MEDICAL_PROFILE
    manifest = load_profile_manifest(manifest_path)

    def _resolve(key: str) -> Path:
        rel = str(manifest.get(key, "")).strip()
        if not rel:
            return Path()
        candidate = Path(rel)
        if not candidate.is_absolute():
            candidate = (REPO_ROOT / candidate).resolve()
        return candidate

    return {
        "profile_manifest": manifest_path.resolve(),
        "predicate_registry": _resolve("predicate_registry"),
        "type_schema_example": _resolve("type_schema_example"),
        "prompt_supplement": _resolve("prompt_supplement"),
        "ontology_prospector_prompt": _resolve("ontology_prospector_prompt"),
        "umls_slice_dir": _resolve("umls_slice_dir"),
        "umls_bridge_facts": _resolve("umls_bridge_facts"),
    }


def canonical_palette(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in manifest.get("canonical_palette", []) or [] if isinstance(row, dict)]


def canonical_predicate_signatures(manifest: dict[str, Any]) -> list[str]:
    signatures: list[str] = []
    for row in canonical_palette(manifest):
        signature = str(row.get("signature", "")).strip()
        if signature and signature not in signatures:
            signatures.append(signature)
    return signatures


def predicate_argument_groups(manifest: dict[str, Any] | None = None) -> dict[str, dict[int, set[str]]]:
    source = manifest if isinstance(manifest, dict) else load_profile_manifest()
    out: dict[str, dict[int, set[str]]] = {}
    for row in canonical_palette(source):
        signature = str(row.get("signature", "")).strip()
        if not signature or "/" not in signature:
            continue
        predicate = signature.split("/", 1)[0]
        raw_groups = row.get("umls_argument_groups", {})
        if not isinstance(raw_groups, dict):
            continue
        converted: dict[int, set[str]] = {}
        for raw_index, raw_values in raw_groups.items():
            try:
                index = int(raw_index)
            except Exception:
                continue
            if not isinstance(raw_values, list):
                continue
            groups = {str(item).strip() for item in raw_values if str(item).strip()}
            if groups:
                converted[index] = groups
        if converted:
            out[predicate] = converted
    return out


def load_profile_concepts(slice_dir: Path) -> list[dict[str, Any]]:
    concepts_path = Path(slice_dir) / "concepts.jsonl"
    if not concepts_path.exists():
        return []
    return _load_jsonl(concepts_path)


def _split_prolog_args(raw_args: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote = ""
    depth = 0
    for char in str(raw_args or ""):
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == "(":
            depth += 1
            current.append(char)
            continue
        if char == ")" and depth > 0:
            depth -= 1
            current.append(char)
            continue
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        args.append(tail)
    return args


def _strip_prolog_token(value: str) -> str:
    token = str(value or "").strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        token = token[1:-1]
    return token.strip()


def load_umls_bridge_facts(path: Path) -> dict[str, Any]:
    bridge_path = Path(path)
    if not bridge_path.exists():
        return {"path": str(bridge_path), "concepts": {}, "aliases": {}, "loaded": False}

    concepts: dict[str, dict[str, Any]] = {}
    aliases: dict[str, str] = {}
    for raw_line in bridge_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%"):
            continue
        match = _BRIDGE_FACT_RE.match(line)
        if not match:
            continue
        predicate = match.group(1)
        args = [_strip_prolog_token(arg) for arg in _split_prolog_args(match.group(2))]
        if predicate == "umls_concept" and len(args) == 2:
            seed_id, cui = args
            concepts.setdefault(seed_id, {"seed_id": seed_id, "aliases": [], "semantic_groups": []})
            concepts[seed_id]["cui"] = cui
        elif predicate == "umls_preferred_atom" and len(args) == 2:
            seed_id, preferred_atom = args
            concepts.setdefault(seed_id, {"seed_id": seed_id, "aliases": [], "semantic_groups": []})
            concepts[seed_id]["preferred_atom"] = preferred_atom
        elif predicate == "umls_semantic_group" and len(args) == 2:
            seed_id, group = args
            row = concepts.setdefault(seed_id, {"seed_id": seed_id, "aliases": [], "semantic_groups": []})
            if group and group not in row["semantic_groups"]:
                row["semantic_groups"].append(group)
        elif predicate == "umls_alias_norm" and len(args) == 2:
            seed_id, alias = args
            row = concepts.setdefault(seed_id, {"seed_id": seed_id, "aliases": [], "semantic_groups": []})
            if alias and alias not in row["aliases"]:
                row["aliases"].append(alias)
            if alias:
                aliases[alias] = seed_id

    for row in concepts.values():
        row["aliases"] = sorted(row.get("aliases", []), key=lambda item: (-len(item), item))
        row["semantic_groups"] = sorted(row.get("semantic_groups", []))
    return {
        "path": str(bridge_path),
        "concepts": concepts,
        "aliases": aliases,
        "loaded": True,
    }


def render_bridge_hints(bridge: dict[str, Any]) -> str:
    concepts = bridge.get("concepts", {}) if isinstance(bridge, dict) else {}
    if not isinstance(concepts, dict) or not concepts:
        return "MEDICAL_UMLS_BRIDGE_HINTS: unavailable"
    lines = ["MEDICAL_UMLS_BRIDGE_HINTS:"]
    for seed_id in sorted(concepts):
        row = concepts.get(seed_id, {}) if isinstance(concepts.get(seed_id), dict) else {}
        groups = ", ".join(str(item) for item in row.get("semantic_groups", []) or [] if str(item).strip())
        aliases = ", ".join(str(item) for item in list(row.get("aliases", []) or [])[:8] if str(item).strip())
        lines.append(
            f"- {seed_id}"
            + (f": groups={groups}" if groups else "")
            + (f"; alias_atoms={aliases}" if aliases else "")
        )
    return "\n".join(lines)


def render_concept_hints(concepts: list[dict[str, Any]]) -> str:
    lines = ["MEDICAL_CONCEPT_HINTS:"]
    for concept in concepts:
        seed_id = str(concept.get("seed_id", "")).strip()
        preferred_name = str(concept.get("preferred_name", "")).strip()
        semantic_types = ", ".join(
            sorted(
                {
                    str(row.get("sty", "")).strip()
                    for row in concept.get("semantic_types", []) or []
                    if str(row.get("sty", "")).strip()
                }
            )
        )
        aliases = ", ".join(
            sorted(
                {
                    str(row.get("text", "")).strip()
                    for row in concept.get("aliases", []) or []
                    if str(row.get("text", "")).strip()
                }
            )[:8]
        )
        lines.append(
            f"- {seed_id}: preferred='{preferred_name}'"
            + (f"; semantic_types={semantic_types}" if semantic_types else "")
            + (f"; aliases={aliases}" if aliases else "")
        )
    return "\n".join(lines)


def build_medical_profile_guide(
    *,
    shared_prompt: str,
    supplement: str,
    concepts: list[dict[str, Any]],
    umls_bridge: dict[str, Any] | None = None,
    known_predicates: list[str] | None = None,
) -> str:
    predicate_lines = ""
    if known_predicates:
        predicate_lines = (
            "Prefer the canonical medical predicate palette when semantically compatible:\n"
            + "\n".join(f"- {item}" for item in known_predicates)
            + "\n\n"
        )
    return (
        shared_prompt.strip()
        + "\n\n"
        + supplement.strip()
        + "\n\n"
        + render_concept_hints(concepts)
        + "\n\n"
        + render_bridge_hints(umls_bridge or {})
        + "\n\n"
        + predicate_lines
        + "The current utterance and clarification answer are the only sources of patient identity.\n"
        + "Medical concept hints and supplement examples are ontology aids, not discourse context.\n"
        + "Use MEDICAL_UMLS_BRIDGE_HINTS for concept normalization and type steering only.\n"
        + "Do not create new predicates from UMLS concept names or alias atoms.\n"
        + "If clarification is still required, set needs_clarification=true and keep logic_string empty.\n"
        + "Do not invent a patient identity from unresolved pronouns.\n"
        + "Do not emit pronoun atoms like she, he, her, his, patient, or person in logic_string.\n"
        + "Do not copy example patient names from the supplement unless they appear in the current utterance or clarification answer.\n"
    )


def bridge_mentions_for_text(text: str, bridge: dict[str, Any]) -> list[dict[str, Any]]:
    aliases = bridge.get("aliases", {}) if isinstance(bridge, dict) else {}
    concepts = bridge.get("concepts", {}) if isinstance(bridge, dict) else {}
    if not isinstance(aliases, dict) or not isinstance(concepts, dict):
        return []
    normalized = umls_mvp.normalize_lookup_text(text)
    if not normalized:
        return []

    occupied: list[tuple[int, int]] = []
    mentions: list[dict[str, Any]] = []
    for alias_atom in sorted(aliases, key=lambda item: (-len(str(item)), str(item))):
        alias_text = str(alias_atom).replace("_", " ")
        if not alias_text:
            continue
        pattern = rf"(?<![a-z0-9]){re.escape(alias_text)}(?![a-z0-9])"
        hit = re.search(pattern, normalized)
        if not hit:
            continue
        start, end = hit.span()
        if any(not (end <= used_start or start >= used_end) for used_start, used_end in occupied):
            continue
        seed_id = str(aliases.get(alias_atom, "")).strip()
        concept = concepts.get(seed_id, {}) if isinstance(concepts.get(seed_id), dict) else {}
        occupied.append((start, end))
        mentions.append(
            {
                "seed_id": seed_id,
                "matched_alias_atom": str(alias_atom),
                "matched_text": alias_text,
                "start": start,
                "end": end,
                "semantic_groups": list(concept.get("semantic_groups", []) or []),
            }
        )
    mentions.sort(key=lambda row: (int(row.get("start", 0) or 0), row["seed_id"]))
    return mentions


def bridge_admission_guidance(text: str, bridge: dict[str, Any]) -> dict[str, Any]:
    mentions = bridge_mentions_for_text(text, bridge)
    normalized = umls_mvp.normalize_lookup_text(text)
    vague_hits = [
        {"surface": surface, "reason": reason}
        for surface, reason in VAGUE_MEDICAL_SURFACE_FORMS.items()
        if re.search(rf"(?<![a-z0-9]){re.escape(surface)}(?![a-z0-9])", normalized)
    ]
    return {
        "mentions": mentions,
        "vague_surfaces": vague_hits,
        "needs_clarification": bool(vague_hits and not mentions),
    }


def _parse_fact_clause(clause: str) -> tuple[str, list[str]] | None:
    match = _FACT_RE.match(str(clause or "").strip())
    if not match:
        return None
    return match.group(1), [_strip_prolog_token(arg) for arg in _split_prolog_args(match.group(2))]


def _bridge_groups_for_atom(atom: str, bridge: dict[str, Any]) -> set[str]:
    concepts = bridge.get("concepts", {}) if isinstance(bridge, dict) else {}
    if not isinstance(concepts, dict):
        return set()
    atomized = umls_mvp.atomize(atom)
    row = concepts.get(atomized)
    if isinstance(row, dict):
        return {str(item).strip() for item in row.get("semantic_groups", []) or [] if str(item).strip()}
    aliases = bridge.get("aliases", {}) if isinstance(bridge, dict) else {}
    if isinstance(aliases, dict):
        seed_id = str(aliases.get(atomized, "")).strip()
        row = concepts.get(seed_id)
        if isinstance(row, dict):
            return {str(item).strip() for item in row.get("semantic_groups", []) or [] if str(item).strip()}
    return set()


def sanitize_medical_parse_for_bridge(
    parsed: dict[str, Any] | None,
    *,
    utterance: str = "",
    bridge: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(parsed, dict) or not isinstance(bridge, dict):
        return parsed
    if not bridge.get("loaded"):
        return parsed
    intent = str(parsed.get("intent", "")).strip().lower()
    if intent != "assert_fact":
        return parsed

    problems: list[str] = []
    clauses = [str(item).strip() for item in parsed.get("facts", []) or [] if str(item).strip()]
    if not clauses:
        logic = str(parsed.get("logic_string", "")).strip()
        if logic:
            clauses = [logic]
    for clause in clauses:
        parsed_clause = _parse_fact_clause(clause)
        if parsed_clause is None:
            continue
        predicate, args = parsed_clause
        expected_by_index = predicate_argument_groups().get(
            predicate,
            PREDICATE_ARGUMENT_GROUPS.get(predicate, {}),
        )
        for index, expected_groups in expected_by_index.items():
            if index >= len(args):
                continue
            actual_groups = _bridge_groups_for_atom(args[index], bridge)
            if actual_groups and actual_groups.isdisjoint(expected_groups):
                expected = "/".join(sorted(expected_groups))
                actual = "/".join(sorted(actual_groups))
                problems.append(
                    f"{predicate}/{len(args)} argument {index + 1} uses {args[index]} as {actual}, expected {expected}."
                )

    guidance = bridge_admission_guidance(utterance, bridge)
    if guidance.get("needs_clarification"):
        surfaces = ", ".join(row["surface"] for row in guidance.get("vague_surfaces", []) if row.get("surface"))
        if surfaces:
            problems.append(f"Utterance contains medically vague surface form(s): {surfaces}.")

    if not problems:
        return parsed

    out = deepcopy(parsed)
    out["needs_clarification"] = True
    out["clarification_question"] = (
        "Which medical meaning should be stored here: medication use, diagnosis, symptom/finding, allergy, or lab result?"
    )
    out["clarification_reason"] = "UMLS bridge type steering found an ambiguous or incompatible medical concept."
    out["logic_string"] = ""
    out["facts"] = []
    out["rules"] = []
    out["queries"] = []
    try:
        current_uncertainty = float(out.get("uncertainty_score", 0.0) or 0.0)
    except Exception:
        current_uncertainty = 0.0
    out["uncertainty_score"] = max(current_uncertainty, 0.8)
    out["uncertainty_label"] = "high"
    ambiguities = [str(item).strip() for item in out.get("ambiguities", []) or [] if str(item).strip()]
    for problem in problems:
        if problem not in ambiguities:
            ambiguities.append(problem)
    out["ambiguities"] = ambiguities
    rationale = str(out.get("rationale", "")).strip()
    suffix = "Medical profile guard cleared logic after UMLS bridge type steering."
    out["rationale"] = f"{rationale} {suffix}".strip() if rationale else suffix
    return out


def _medical_unresolved_identity_signal(parsed: dict[str, Any]) -> bool:
    blobs: list[str] = []
    blobs.append(str(parsed.get("clarification_reason", "")).strip())
    blobs.append(str(parsed.get("rationale", "")).strip())
    blobs.extend(str(item).strip() for item in parsed.get("ambiguities", []) or [] if str(item).strip())
    text = " ".join(blobs).casefold()
    if not text:
        return False
    triggers = [
        "unresolved pronoun",
        "patient identity unresolved",
        "patient identity",
        "lacks grounded antecedent",
        "cannot invent patient atom",
        "cannot invent patient identity",
        "using canonical example patient",
        "using placeholder",
        "antecedent",
    ]
    return any(token in text for token in triggers)


def sanitize_medical_parse_for_clarification(
    parsed: dict[str, Any] | None,
    *,
    utterance: str = "",
) -> dict[str, Any] | None:
    if not isinstance(parsed, dict):
        return parsed
    intent = str(parsed.get("intent", "")).strip().lower()
    if intent != "assert_fact":
        return parsed
    if not _medical_unresolved_identity_signal(parsed):
        return parsed

    out = deepcopy(parsed)
    out["needs_clarification"] = True
    question = str(out.get("clarification_question", "")).strip()
    match = _MEDICAL_PRONOUN_RE.search(str(utterance or ""))
    if match:
        pronoun = match.group(1).lower()
        question_lower = question.casefold()
        if not question or not ("who does" in question_lower and "refer" in question_lower):
            out["clarification_question"] = f"Who does '{pronoun}' refer to?"
            out["clarification_reason"] = f"Pronoun '{pronoun}' is unresolved."
    elif not question:
        out["clarification_question"] = "Which patient does this refer to?"
        out["clarification_reason"] = "Patient identity is unresolved."
    out["logic_string"] = ""
    out["facts"] = []
    out["rules"] = []
    out["queries"] = []
    try:
        current_uncertainty = float(out.get("uncertainty_score", 0.0) or 0.0)
    except Exception:
        current_uncertainty = 0.0
    out["uncertainty_score"] = max(current_uncertainty, 0.75)
    out["uncertainty_label"] = "high"
    ambiguities = [str(item).strip() for item in out.get("ambiguities", []) or [] if str(item).strip()]
    note = "Medical profile guard cleared logic until patient identity is clarified."
    if note not in ambiguities:
        ambiguities.append(note)
    out["ambiguities"] = ambiguities
    rationale = str(out.get("rationale", "")).strip()
    suffix = "Medical profile guard kept logic empty because patient identity is unresolved."
    out["rationale"] = f"{rationale} {suffix}".strip() if rationale else suffix
    return out


def rescue_medical_clarified_lab_result(
    parsed: dict[str, Any] | None,
    *,
    utterance: str = "",
    clarification_answer: str = "",
) -> dict[str, Any] | None:
    if not isinstance(parsed, dict):
        return parsed
    answer = str(clarification_answer or "").strip()
    if not answer:
        return parsed
    combined = f"{utterance} {answer}".casefold()
    if "blood pressure" not in combined:
        return parsed
    if not re.search(r"\b(reading|readings|measurement|measurements|result|results)\b", combined):
        return parsed
    if not re.search(r"\b(high|bad|elevated)\b", combined):
        return parsed

    patient_match = re.search(
        r"\b([A-Z][A-Za-z0-9_-]*)'?s\s+blood\s+pressure\b",
        f"{answer} {utterance}",
    )
    if not patient_match:
        patient_match = re.search(
            r"\b(?:for|patient)\s+([A-Z][A-Za-z0-9_-]*)\b",
            f"{answer} {utterance}",
        )
    if not patient_match:
        return parsed

    patient = umls_mvp.atomize(patient_match.group(1))
    if not patient:
        return parsed
    fact = f"lab_result_high({patient}, blood_pressure_measurement)."
    out = deepcopy(parsed)
    out["intent"] = "assert_fact"
    out["logic_string"] = fact
    out["facts"] = [fact]
    out["rules"] = []
    out["queries"] = []
    out["needs_clarification"] = False
    out["clarification_question"] = ""
    out["clarification_reason"] = ""
    out["uncertainty_score"] = min(float(out.get("uncertainty_score", 0.2) or 0.2), 0.25)
    out["uncertainty_label"] = "low"
    out["components"] = {
        "atoms": [patient, "blood_pressure_measurement"],
        "variables": [],
        "predicates": ["lab_result_high"],
    }
    out["ambiguities"] = []
    out["rationale"] = "Resolved clarified blood pressure reading as a high lab result."
    return out
