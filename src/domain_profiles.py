from __future__ import annotations

import json
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
        notes = str(row.get("notes", "")).strip()
        if notes:
            contract["notes"] = notes
        contracts.append(contract)
    return contracts


def profile_package_context(profile: dict[str, Any]) -> list[str]:
    return _string_list(profile.get("semantic_ir_context") if isinstance(profile, dict) else [])


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
