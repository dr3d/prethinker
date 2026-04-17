from __future__ import annotations

import re
from pathlib import Path


def infer_registry_profile(registry_path: str) -> str:
    token = str(registry_path or "").strip()
    if not token:
        return ""
    name = Path(token).name.strip().lower()
    if name in {"predicate_registry.json", "predicate_registry.general.json"}:
        return "general"
    match = re.fullmatch(r"predicate_registry\.([a-z0-9_]+)\.json", name)
    if not match:
        return ""
    profile = str(match.group(1) or "").strip().lower()
    return "general" if profile == "general" else profile


def registry_profile_mismatch_message(
    registry_path: str,
    *,
    label: str = "",
    story_path: str = "",
    allow_cross_domain_registry: bool = False,
) -> str:
    if allow_cross_domain_registry:
        return ""
    profile = infer_registry_profile(registry_path)
    if profile in {"", "general"}:
        return ""

    story_ref = Path(str(story_path or "").strip()) if str(story_path or "").strip() else None
    context_bits = [str(label or "").strip().lower()]
    if story_ref is not None:
        context_bits.append(story_ref.stem.strip().lower())
        context_bits.append(story_ref.name.strip().lower())
    context = " ".join(bit for bit in context_bits if bit)
    if context and profile in context:
        return ""

    run_name = str(label or (story_ref.stem if story_ref is not None else "story")).strip() or "story"
    return (
        f"Refusing domain-specific registry profile '{profile}' for story run '{run_name}'. "
        "Pass --allow-cross-domain-registry to override."
    )
