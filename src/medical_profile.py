from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEDICAL_PROFILE = REPO_ROOT / "modelfiles" / "profile.medical.v0.json"
_MEDICAL_PRONOUN_RE = re.compile(r"\b(he|she|his|her|they|their|them|him)\b", re.IGNORECASE)


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


def load_profile_concepts(slice_dir: Path) -> list[dict[str, Any]]:
    concepts_path = Path(slice_dir) / "concepts.jsonl"
    if not concepts_path.exists():
        return []
    return _load_jsonl(concepts_path)


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
        + predicate_lines
        + "The current utterance and clarification answer are the only sources of patient identity.\n"
        + "Medical concept hints and supplement examples are ontology aids, not discourse context.\n"
        + "If clarification is still required, set needs_clarification=true and keep logic_string empty.\n"
        + "Do not invent a patient identity from unresolved pronouns.\n"
        + "Do not emit pronoun atoms like she, he, her, his, patient, or person in logic_string.\n"
        + "Do not copy example patient names from the supplement unless they appear in the current utterance or clarification answer.\n"
    )


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
    if not str(out.get("clarification_question", "")).strip():
        match = _MEDICAL_PRONOUN_RE.search(str(utterance or ""))
        if match:
            pronoun = match.group(1).lower()
            out["clarification_question"] = f"Who does '{pronoun}' refer to?"
            out["clarification_reason"] = f"Pronoun '{pronoun}' is unresolved."
        else:
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
