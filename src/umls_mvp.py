from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_MULTISPACE_RE = re.compile(r"\s+")

DEFAULT_GLOBAL_SOURCE_PRIORITY = ["SNOMEDCT_US", "RXNORM", "LOINC"]
TTY_PRIORITY = {
    "PT": 100,
    "PN": 96,
    "IN": 94,
    "MIN": 92,
    "MH": 90,
    "ET": 88,
    "SY": 70,
    "AB": 60,
    "FN": 56,
}


def normalize_lookup_text(text: str) -> str:
    lowered = str(text or "").casefold()
    lowered = _NON_ALNUM_RE.sub(" ", lowered)
    lowered = _MULTISPACE_RE.sub(" ", lowered).strip()
    return lowered


def atomize(text: str) -> str:
    lowered = str(text or "").casefold()
    lowered = _NON_ALNUM_RE.sub("_", lowered)
    lowered = re.sub(r"_+", "_", lowered).strip("_")
    return lowered or "unknown"


def iter_rrf_rows(path: Path) -> Iterable[list[str]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\r\n")
            if not line:
                continue
            cols = line.split("|")
            if cols and cols[-1] == "":
                cols.pop()
            yield cols


def parse_mrconso_row(cols: list[str]) -> dict[str, Any]:
    return {
        "cui": cols[0] if len(cols) > 0 else "",
        "lat": cols[1] if len(cols) > 1 else "",
        "ispref": cols[6] if len(cols) > 6 else "",
        "sab": cols[11] if len(cols) > 11 else "",
        "tty": cols[12] if len(cols) > 12 else "",
        "code": cols[13] if len(cols) > 13 else "",
        "str": cols[14] if len(cols) > 14 else "",
        "suppress": cols[16] if len(cols) > 16 else "",
    }


def parse_mrsty_row(cols: list[str]) -> dict[str, Any]:
    return {
        "cui": cols[0] if len(cols) > 0 else "",
        "tui": cols[1] if len(cols) > 1 else "",
        "sty": cols[3] if len(cols) > 3 else "",
    }


def parse_mrsab_row(cols: list[str]) -> dict[str, Any]:
    return {
        "vsab": cols[2] if len(cols) > 2 else "",
        "rsab": cols[3] if len(cols) > 3 else "",
        "name": cols[4] if len(cols) > 4 else "",
        "lat": cols[19] if len(cols) > 19 else "",
    }


def parse_mrrel_row(cols: list[str]) -> dict[str, Any]:
    return {
        "cui1": cols[0] if len(cols) > 0 else "",
        "rel": cols[3] if len(cols) > 3 else "",
        "cui2": cols[4] if len(cols) > 4 else "",
        "rela": cols[7] if len(cols) > 7 else "",
        "sab": cols[10] if len(cols) > 10 else "",
        "suppress": cols[14] if len(cols) > 14 else "",
    }


def is_active_row(suppress: str) -> bool:
    token = str(suppress or "").strip().upper()
    return token in {"", "N"}


def source_rank(
    sab: str,
    *,
    preferred_sources: list[str] | None = None,
    global_priority: list[str] | None = None,
) -> int:
    preferred = preferred_sources or []
    global_order = global_priority or DEFAULT_GLOBAL_SOURCE_PRIORITY
    if sab in preferred:
        return preferred.index(sab)
    if sab in global_order:
        return len(preferred) + global_order.index(sab)
    return len(preferred) + len(global_order) + 100


def tty_rank(tty: str) -> int:
    return -TTY_PRIORITY.get(str(tty or "").strip().upper(), 0)


def seed_alias_map(battery: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    alias_index: dict[str, list[dict[str, Any]]] = {}
    for seed in battery.get("concept_seeds", []):
        seed_id = str(seed.get("seed_id", "")).strip()
        aliases: list[str] = []
        for alias in list(seed.get("seed_aliases", []) or []) + list(seed.get("probe_aliases", []) or []):
            text = str(alias or "").strip()
            if text and text not in aliases:
                aliases.append(text)
        for index, alias in enumerate(aliases):
            normalized = normalize_lookup_text(alias)
            if not normalized:
                continue
            alias_index.setdefault(normalized, []).append(
                {
                    "seed_id": seed_id,
                    "alias_rank": index,
                    "preferred_sources": list(seed.get("preferred_sources", []) or []),
                }
            )
    return alias_index


def choose_best_candidate(
    candidates: list[dict[str, Any]],
    *,
    preferred_sources: list[str] | None = None,
    global_priority: list[str] | None = None,
) -> dict[str, Any] | None:
    if not candidates:
        return None

    def _key(row: dict[str, Any]) -> tuple[Any, ...]:
        return (
            source_rank(
                str(row.get("sab", "")).strip(),
                preferred_sources=preferred_sources,
                global_priority=global_priority,
            ),
            int(row.get("alias_rank", 999)),
            tty_rank(str(row.get("tty", "")).strip()),
            0 if str(row.get("ispref", "")).strip().upper() == "Y" else 1,
            len(str(row.get("str", "")).strip()),
            str(row.get("cui", "")).strip(),
        )

    return min(candidates, key=_key)


def distinct_alias_rows(
    rows: list[dict[str, Any]],
    *,
    limit: int = 30,
    preferred_sources: list[str] | None = None,
    global_priority: list[str] | None = None,
) -> list[dict[str, Any]]:
    ordered = sorted(
        rows,
        key=lambda row: (
            source_rank(
                str(row.get("sab", "")).strip(),
                preferred_sources=preferred_sources,
                global_priority=global_priority,
            ),
            tty_rank(str(row.get("tty", "")).strip()),
            0 if str(row.get("ispref", "")).strip().upper() == "Y" else 1,
            len(str(row.get("str") or row.get("text") or "").strip()),
        ),
    )
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in ordered:
        alias = normalize_lookup_text(str(row.get("str") or row.get("text") or "").strip())
        if not alias or alias in seen:
            continue
        seen.add(alias)
        deduped.append(row)
        if len(deduped) >= limit:
            break
    return deduped


def build_alias_records(slice_manifest: dict[str, Any], concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_seed_id = {str(seed.get("seed_id", "")).strip(): seed for seed in slice_manifest.get("resolved_seeds", [])}
    rows: list[dict[str, Any]] = []
    for concept in concepts:
        seed_id = str(concept.get("seed_id", "")).strip()
        seed_meta = by_seed_id.get(seed_id, {})
        preferred_name = str(concept.get("preferred_name", "")).strip()
        semantic_types = list(concept.get("semantic_types", []) or [])
        aliases = list(concept.get("aliases", []) or [])
        for alias_row in aliases:
            alias = normalize_lookup_text(alias_row.get("text", ""))
            if not alias:
                continue
            rows.append(
                {
                    "alias": alias,
                    "seed_id": seed_id,
                    "cui": str(concept.get("cui", "")).strip(),
                    "preferred_name": preferred_name,
                    "sab": str(alias_row.get("sab", "")).strip(),
                    "tty": str(alias_row.get("tty", "")).strip(),
                    "semantic_types": semantic_types,
                    "storage_default": str(seed_meta.get("storage_default", "sharp_memory_candidate")).strip(),
                }
            )
    # Longer aliases win first so we do not overmatch short forms inside bigger phrases.
    rows.sort(key=lambda row: (-len(row["alias"]), row["alias"]))
    return rows


def inject_requested_alias_rows(
    alias_rows: list[dict[str, Any]],
    wanted_aliases: set[str],
) -> list[dict[str, Any]]:
    out = list(alias_rows)
    normalized_existing = {
        normalize_lookup_text(str(row.get("text", "")).strip())
        for row in out
        if str(row.get("text", "")).strip()
    }
    for alias in sorted(alias for alias in wanted_aliases if alias):
        if alias in normalized_existing:
            continue
        out.append(
            {
                "text": alias,
                "sab": "DERIVED",
                "tty": "ALIAS",
                "ispref": "N",
                "derived_from_requested_alias": True,
            }
        )
        normalized_existing.add(alias)
    return out


def extract_grounded_mentions(text: str, alias_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = normalize_lookup_text(text)
    if not normalized:
        return []
    occupied: list[tuple[int, int]] = []
    matches: list[dict[str, Any]] = []
    seen_seed_ids: set[str] = set()
    ordered_records = sorted(
        alias_records,
        key=lambda row: (-len(str(row.get("alias", ""))), str(row.get("alias", ""))),
    )
    for record in ordered_records:
        alias = record["alias"]
        pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])"
        hit = re.search(pattern, normalized)
        if not hit:
            continue
        start, end = hit.span()
        if any(not (end <= used_start or start >= used_end) for used_start, used_end in occupied):
            continue
        seed_id = str(record.get("seed_id", "")).strip()
        if seed_id in seen_seed_ids:
            continue
        occupied.append((start, end))
        seen_seed_ids.add(seed_id)
        row = dict(record)
        row["matched_alias"] = alias
        matches.append(row)
    matches.sort(key=lambda row: row["seed_id"])
    return matches


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def render_sharp_memory_facts(
    concepts: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> str:
    lines: list[str] = [
        "% Derived from licensed UMLS content. Keep this file local unless licensing is reviewed.",
        "",
    ]
    for concept in concepts:
        seed_atom = atomize(concept.get("seed_id", ""))
        cui = str(concept.get("cui", "")).strip()
        pref = str(concept.get("preferred_name", "")).replace("'", "\\'")
        lines.append(f"umls_seed({seed_atom}, '{cui}').")
        lines.append(f"umls_pref_name({seed_atom}, '{pref}').")
        for sty in concept.get("semantic_types", []) or []:
            tui = str(sty.get("tui", "")).strip()
            sty_name = str(sty.get("sty", "")).replace("'", "\\'")
            lines.append(f"umls_semantic_type({seed_atom}, '{tui}', '{sty_name}').")
        for alias_row in concept.get("aliases", []) or []:
            alias_text = str(alias_row.get("text", "")).replace("'", "\\'")
            lines.append(f"umls_alias({seed_atom}, '{alias_text}').")
        lines.append("")

    for relation in relations:
        src = atomize(relation.get("seed_id_1", ""))
        dst = atomize(relation.get("seed_id_2", ""))
        rel = atomize(relation.get("relation_label", "related_to"))
        source = str(relation.get("sab", "")).strip()
        lines.append(f"umls_relation({src}, {dst}, {rel}, '{source}').")
    return "\n".join(lines).rstrip() + "\n"
