"""Citation resolver primitives for legal authority verification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CitationResolution:
    authority_matches: list[dict[str, Any]]
    lookup_row: dict[str, Any]


class LocalAuthorityInventoryResolver:
    """Deterministic resolver backed by a declared local authority inventory."""

    def __init__(self, inventory: dict[str, list[dict[str, Any]]]) -> None:
        self.inventory = inventory

    @classmethod
    def from_path(cls, path: Path) -> "LocalAuthorityInventoryResolver":
        return cls(_load_inventory(path))

    def lookup_citation(
        self,
        *,
        citation: str,
        start_index: int,
        end_index: int,
    ) -> CitationResolution:
        authority_matches = self.inventory.get(citation, [])
        return CitationResolution(
            authority_matches=authority_matches,
            lookup_row=courtlistener_like_lookup_row(
                citation=citation,
                start_index=start_index,
                end_index=end_index,
                authority_matches=authority_matches,
            ),
        )


def courtlistener_like_lookup_row(
    *,
    citation: str,
    start_index: int,
    end_index: int,
    authority_matches: list[dict[str, Any]],
) -> dict[str, Any]:
    if not authority_matches:
        status = 404
        error = "citation_not_found"
    elif len(authority_matches) > 1:
        status = 300
        error = "ambiguous_citation"
    else:
        status = 200
        error = ""
    return {
        "citation": citation,
        "normalized_citations": [citation],
        "start_index": start_index,
        "end_index": end_index,
        "status": status,
        "error_message": error,
        "clusters": [
            {
                "authority_id": row.get("authority_id"),
                "case_name": row.get("case_name"),
                "canonical_citation": row.get("canonical_citation"),
                "year": row.get("year"),
            }
            for row in authority_matches
        ],
    }


def _load_inventory(path: Path) -> dict[str, list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, list[dict[str, Any]]] = {}
    for row in data.get("authorities", []):
        citation = str(row.get("canonical_citation") or "").strip()
        if citation:
            out.setdefault(citation, []).append(row)
    return out
