#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import umls_mvp  # noqa: E402


DEFAULT_META_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "META"
DEFAULT_BATTERY = ROOT / "docs" / "data" / "umls_mvp_sharp_memory_battery.json"
DEFAULT_OUT_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "prethinker_mvp"


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _load_battery(path: Path) -> dict[str, Any]:
    payload = umls_mvp.load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Battery must be a JSON object: {path}")
    return payload


def _source_catalog(meta_dir: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for cols in umls_mvp.iter_rrf_rows(meta_dir / "MRSAB.RRF"):
        row = umls_mvp.parse_mrsab_row(cols)
        rsab = str(row.get("rsab", "")).strip()
        if not rsab:
            continue
        out[rsab] = row
    return out


def _resolve_seed_concepts(meta_dir: Path, battery: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    seeds_by_id = {str(seed.get("seed_id", "")).strip(): seed for seed in battery.get("concept_seeds", [])}
    alias_index = umls_mvp.seed_alias_map(battery)
    global_priority = list(battery.get("allowed_sources", []) or umls_mvp.DEFAULT_GLOBAL_SOURCE_PRIORITY)
    candidate_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unresolved: list[str] = []

    mrconso_path = meta_dir / "MRCONSO.RRF"
    for cols in umls_mvp.iter_rrf_rows(mrconso_path):
        row = umls_mvp.parse_mrconso_row(cols)
        if row["lat"] != "ENG" or not umls_mvp.is_active_row(row["suppress"]):
            continue
        normalized = umls_mvp.normalize_lookup_text(row["str"])
        if not normalized:
            continue
        matches = alias_index.get(normalized, [])
        if not matches:
            continue
        for match in matches:
            seed_id = match["seed_id"]
            seed = seeds_by_id.get(seed_id, {})
            preferred_sources = list(seed.get("preferred_sources", []) or [])
            allowed_sources = list(dict.fromkeys(preferred_sources + global_priority))
            if allowed_sources and row["sab"] not in allowed_sources:
                continue
            candidate = dict(row)
            candidate["seed_id"] = seed_id
            candidate["alias_rank"] = int(match["alias_rank"])
            candidate_rows[seed_id].append(candidate)

    resolved: list[dict[str, Any]] = []
    for seed in battery.get("concept_seeds", []):
        seed_id = str(seed.get("seed_id", "")).strip()
        preferred_sources = list(seed.get("preferred_sources", []) or [])
        best = umls_mvp.choose_best_candidate(
            candidate_rows.get(seed_id, []),
            preferred_sources=preferred_sources,
            global_priority=global_priority,
        )
        if best is None:
            unresolved.append(seed_id)
            continue
        resolved.append(
            {
                "seed_id": seed_id,
                "cui": str(best.get("cui", "")).strip(),
                "preferred_name": str(best.get("str", "")).strip(),
                "sab": str(best.get("sab", "")).strip(),
                "tty": str(best.get("tty", "")).strip(),
                "code": str(best.get("code", "")).strip(),
                "seed_aliases": list(seed.get("seed_aliases", []) or []),
                "probe_aliases": list(seed.get("probe_aliases", []) or []),
                "preferred_sources": preferred_sources,
                "storage_default": str(seed.get("storage_default", "sharp_memory_candidate")).strip(),
            }
        )
    return resolved, unresolved


def _collect_concepts(meta_dir: Path, battery: dict[str, Any], resolved: list[dict[str, Any]]) -> list[dict[str, Any]]:
    global_priority = list(battery.get("allowed_sources", []) or umls_mvp.DEFAULT_GLOBAL_SOURCE_PRIORITY)
    alias_bridge_relations = set(
        list(battery.get("alias_bridge_relations", []) or ["tradename_of", "has_tradename", "ingredient_of", "has_ingredient"])
    )
    resolved_by_cui = {str(row["cui"]).strip(): row for row in resolved}
    alias_rows_by_cui: dict[str, list[dict[str, Any]]] = defaultdict(list)
    wanted_aliases_by_cui: dict[str, set[str]] = {}
    for row in resolved:
        all_aliases = set()
        for alias in list(row.get("seed_aliases", []) or []) + list(row.get("probe_aliases", []) or []):
            normalized = umls_mvp.normalize_lookup_text(alias)
            if normalized:
                all_aliases.add(normalized)
        wanted_aliases_by_cui[str(row["cui"]).strip()] = all_aliases

    mrconso_path = meta_dir / "MRCONSO.RRF"
    for cols in umls_mvp.iter_rrf_rows(mrconso_path):
        row = umls_mvp.parse_mrconso_row(cols)
        cui = str(row["cui"]).strip()
        if cui not in resolved_by_cui:
            continue
        if row["lat"] != "ENG" or not umls_mvp.is_active_row(row["suppress"]):
            continue
        seed_meta = resolved_by_cui[cui]
        allowed_sources = list(
            dict.fromkeys(list(seed_meta.get("preferred_sources", []) or []) + global_priority)
        )
        if allowed_sources and row["sab"] not in allowed_sources:
            continue
        alias_row = {
            "text": str(row["str"]).strip(),
            "sab": str(row["sab"]).strip(),
            "tty": str(row["tty"]).strip(),
            "ispref": str(row["ispref"]).strip(),
        }
        alias_rows_by_cui[cui].append(alias_row)

    neighbor_cuis_by_cui: dict[str, set[str]] = defaultdict(set)
    if alias_bridge_relations:
        for cols in umls_mvp.iter_rrf_rows(meta_dir / "MRREL.RRF"):
            row = umls_mvp.parse_mrrel_row(cols)
            if not umls_mvp.is_active_row(row["suppress"]):
                continue
            relation_label = str(row["rela"]).strip() or str(row["rel"]).strip()
            if relation_label not in alias_bridge_relations:
                continue
            sab = str(row["sab"]).strip()
            if sab not in set(global_priority):
                continue
            cui1 = str(row["cui1"]).strip()
            cui2 = str(row["cui2"]).strip()
            if cui1 in resolved_by_cui and cui2 not in resolved_by_cui:
                neighbor_cuis_by_cui[cui1].add(cui2)
            elif cui2 in resolved_by_cui and cui1 not in resolved_by_cui:
                neighbor_cuis_by_cui[cui2].add(cui1)

    missing_probe_aliases_by_cui: dict[str, set[str]] = {}
    for seed_meta in resolved:
        cui = str(seed_meta["cui"]).strip()
        preferred_sources = list(seed_meta.get("preferred_sources", []) or [])
        base_alias_rows = umls_mvp.distinct_alias_rows(
            alias_rows_by_cui.get(cui, []),
            limit=30,
            preferred_sources=preferred_sources,
            global_priority=global_priority,
        )
        normalized_base_aliases = {
            umls_mvp.normalize_lookup_text(row.get("text", ""))
            for row in base_alias_rows
        }
        missing_probe_aliases_by_cui[cui] = {
            alias
            for alias in wanted_aliases_by_cui.get(cui, set())
            if alias and alias not in normalized_base_aliases
        }

    if any(missing_probe_aliases_by_cui.values()):
        neighbor_to_hosts: dict[str, set[str]] = defaultdict(set)
        for host_cui, neighbor_cuis in neighbor_cuis_by_cui.items():
            missing_aliases = missing_probe_aliases_by_cui.get(host_cui, set())
            if not missing_aliases:
                continue
            for neighbor_cui in neighbor_cuis:
                neighbor_to_hosts[neighbor_cui].add(host_cui)

        if neighbor_to_hosts:
            for cols in umls_mvp.iter_rrf_rows(meta_dir / "MRCONSO.RRF"):
                row = umls_mvp.parse_mrconso_row(cols)
                cui = str(row["cui"]).strip()
                if cui not in neighbor_to_hosts:
                    continue
                if row["lat"] != "ENG" or not umls_mvp.is_active_row(row["suppress"]):
                    continue
                normalized = umls_mvp.normalize_lookup_text(row["str"])
                if not normalized:
                    continue
                for host_cui in neighbor_to_hosts[cui]:
                    if normalized not in missing_probe_aliases_by_cui.get(host_cui, set()):
                        continue
                    alias_rows_by_cui[host_cui].append(
                        {
                            "text": str(row["str"]).strip(),
                            "sab": str(row["sab"]).strip(),
                            "tty": str(row["tty"]).strip(),
                            "ispref": str(row["ispref"]).strip(),
                            "relation_bridge": True,
                            "bridged_from_cui": cui,
                        }
                    )

    semantic_types_by_cui: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cols in umls_mvp.iter_rrf_rows(meta_dir / "MRSTY.RRF"):
        row = umls_mvp.parse_mrsty_row(cols)
        cui = str(row["cui"]).strip()
        if cui not in resolved_by_cui:
            continue
        semantic_types_by_cui[cui].append(
            {"tui": str(row["tui"]).strip(), "sty": str(row["sty"]).strip()}
        )

    concepts: list[dict[str, Any]] = []
    for seed_meta in resolved:
        cui = str(seed_meta["cui"]).strip()
        preferred_sources = list(seed_meta.get("preferred_sources", []) or [])
        alias_rows = umls_mvp.distinct_alias_rows(
            alias_rows_by_cui.get(cui, []),
            limit=30,
            preferred_sources=preferred_sources,
            global_priority=global_priority,
        )
        normalized_existing = {
            umls_mvp.normalize_lookup_text(row.get("text", ""))
            for row in alias_rows
        }
        derived_phrase_aliases: list[dict[str, Any]] = []
        for alias in sorted(wanted_aliases_by_cui.get(cui, set())):
            if alias in normalized_existing:
                continue
            if any(
                alias
                and re.search(
                    rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])",
                    umls_mvp.normalize_lookup_text(row.get("text", "")),
                )
                for row in alias_rows
            ):
                derived_phrase_aliases.append(
                    {
                        "text": alias,
                        "sab": "DERIVED",
                        "tty": "ALIAS",
                        "ispref": "N",
                        "derived_from_phrase": True,
                    }
                )
        alias_rows.extend(derived_phrase_aliases)
        alias_rows = umls_mvp.inject_requested_alias_rows(
            alias_rows,
            wanted_aliases_by_cui.get(cui, set()),
        )
        alias_rows = umls_mvp.distinct_alias_rows(
            alias_rows,
            limit=36,
            preferred_sources=preferred_sources,
            global_priority=global_priority,
        )
        wanted_aliases = wanted_aliases_by_cui.get(cui, set())
        normalized_aliases = {umls_mvp.normalize_lookup_text(row["text"]) for row in alias_rows}
        missing_wanted = sorted(alias for alias in wanted_aliases if alias not in normalized_aliases)
        concepts.append(
            {
                "seed_id": seed_meta["seed_id"],
                "cui": cui,
                "preferred_name": seed_meta["preferred_name"],
                "preferred_source": seed_meta["sab"],
                "preferred_tty": seed_meta["tty"],
                "aliases": alias_rows,
                "missing_requested_aliases": missing_wanted,
                "semantic_types": sorted(
                    semantic_types_by_cui.get(cui, []),
                    key=lambda row: (row["tui"], row["sty"]),
                ),
            }
        )
    concepts.sort(key=lambda row: row["seed_id"])
    return concepts


def _collect_relations(meta_dir: Path, battery: dict[str, Any], concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed_sources = set(list(battery.get("allowed_sources", []) or umls_mvp.DEFAULT_GLOBAL_SOURCE_PRIORITY))
    relation_whitelist = set(list(battery.get("relation_whitelist", []) or []))
    seed_id_by_cui = {str(row["cui"]).strip(): str(row["seed_id"]).strip() for row in concepts}
    selected_cuis = set(seed_id_by_cui)
    dedupe: set[tuple[str, str, str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for cols in umls_mvp.iter_rrf_rows(meta_dir / "MRREL.RRF"):
        row = umls_mvp.parse_mrrel_row(cols)
        if not umls_mvp.is_active_row(row["suppress"]):
            continue
        cui1 = str(row["cui1"]).strip()
        cui2 = str(row["cui2"]).strip()
        if cui1 not in selected_cuis or cui2 not in selected_cuis:
            continue
        sab = str(row["sab"]).strip()
        if allowed_sources and sab not in allowed_sources:
            continue
        relation_label = str(row["rela"]).strip() or str(row["rel"]).strip()
        if relation_whitelist and relation_label not in relation_whitelist and str(row["rel"]).strip() not in relation_whitelist:
            continue
        key = (cui1, cui2, str(row["rel"]).strip(), relation_label, sab)
        if key in dedupe:
            continue
        dedupe.add(key)
        out.append(
            {
                "seed_id_1": seed_id_by_cui[cui1],
                "seed_id_2": seed_id_by_cui[cui2],
                "cui1": cui1,
                "cui2": cui2,
                "rel": str(row["rel"]).strip(),
                "relation_label": relation_label,
                "sab": sab,
            }
        )
    out.sort(key=lambda row: (row["seed_id_1"], row["relation_label"], row["seed_id_2"]))
    return out


def build_slice(meta_dir: Path, battery_path: Path, out_dir: Path) -> dict[str, Any]:
    battery = _load_battery(battery_path)
    source_catalog = _source_catalog(meta_dir)
    resolved, unresolved = _resolve_seed_concepts(meta_dir, battery)
    concepts = _collect_concepts(meta_dir, battery, resolved)
    relations = _collect_relations(meta_dir, battery, concepts)

    manifest = {
        "mvp_id": str(battery.get("battery_id", "umls_mvp")).strip(),
        "generated_at_utc": _utc_now(),
        "meta_dir": str(meta_dir),
        "battery_path": str(battery_path),
        "allowed_sources": list(battery.get("allowed_sources", []) or []),
        "relation_whitelist": list(battery.get("relation_whitelist", []) or []),
        "resolved_seeds": resolved,
        "unresolved_seeds": unresolved,
        "counts": {
            "source_vocabularies": len(source_catalog),
            "resolved_seeds": len(resolved),
            "unresolved_seeds": len(unresolved),
            "concepts": len(concepts),
            "relations": len(relations),
        },
        "source_catalog": {
            key: {
                "vsab": str(value.get("vsab", "")).strip(),
                "name": str(value.get("name", "")).strip(),
                "lat": str(value.get("lat", "")).strip(),
            }
            for key, value in source_catalog.items()
            if key in set(list(battery.get("allowed_sources", []) or []))
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    umls_mvp.write_json(out_dir / "manifest.json", manifest)
    umls_mvp.write_jsonl(out_dir / "concepts.jsonl", concepts)
    umls_mvp.write_jsonl(out_dir / "relations.jsonl", relations)
    (out_dir / "sharp_memory_seed_facts.pl").write_text(
        umls_mvp.render_sharp_memory_facts(concepts, relations),
        encoding="utf-8",
    )
    (out_dir / "umls_bridge_facts.pl").write_text(
        umls_mvp.render_umls_bridge_facts(concepts, relations),
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a bounded UMLS MVP slice for Prethinker.")
    parser.add_argument("--meta-dir", type=Path, default=DEFAULT_META_DIR)
    parser.add_argument("--battery", type=Path, default=DEFAULT_BATTERY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    manifest = build_slice(args.meta_dir, args.battery, args.out_dir)
    print(json.dumps(manifest["counts"], indent=2))
    if manifest["unresolved_seeds"]:
        print("UNRESOLVED:", ", ".join(manifest["unresolved_seeds"]))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
