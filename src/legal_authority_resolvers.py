"""Citation resolver primitives for legal authority verification."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


TRANSIENT_LOOKUP_STATUSES = {408, 425, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class CitationResolution:
    authority_matches: list[dict[str, Any]]
    lookup_row: dict[str, Any]


class LegalAuthorityResolver(Protocol):
    """Resolver contract used by the deterministic verifier."""

    def lookup_citation(
        self,
        *,
        citation: str,
        start_index: int,
        end_index: int,
    ) -> CitationResolution:
        ...


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


class CourtListenerCitationLookupResolver:
    """Resolver adapter for CourtListener citation lookup rows.

    The adapter intentionally keeps CourtListener as a resolver substrate, not
    a legal verifier. It can resolve a citation to a cluster/authority identity,
    while quote, pin, metadata, and proposition checks still happen downstream
    in the deterministic verifier. If local authority inventory rows are
    supplied, they are preferred because they carry retained authority text.
    """

    def __init__(
        self,
        *,
        client: Any,
        inventory: dict[str, list[dict[str, Any]]] | None = None,
    ) -> None:
        self.client = client
        self.inventory = inventory or {}

    @classmethod
    def from_inventory_path(
        cls,
        *,
        client: Any,
        path: Path,
    ) -> "CourtListenerCitationLookupResolver":
        return cls(client=client, inventory=_load_inventory(path))

    def lookup_citation(
        self,
        *,
        citation: str,
        start_index: int,
        end_index: int,
    ) -> CitationResolution:
        try:
            lookup_rows = self.client.citation_lookup(text=citation)
        except Exception as exc:
            status = _exception_status(exc)
            if status in TRANSIENT_LOOKUP_STATUSES:
                return CitationResolution(
                    authority_matches=[],
                    lookup_row=external_lookup_unavailable_row(
                        citation=citation,
                        start_index=start_index,
                        end_index=end_index,
                        status=status,
                        error_message=str(exc) or "external citation lookup unavailable",
                    ),
                )
            raise
        lookup_row = _select_lookup_row(
            lookup_rows=lookup_rows,
            citation=citation,
            start_index=start_index,
            end_index=end_index,
        )
        if lookup_row is None:
            return CitationResolution(
                authority_matches=[],
                lookup_row=courtlistener_like_lookup_row(
                    citation=citation,
                    start_index=start_index,
                    end_index=end_index,
                    authority_matches=[],
                ),
            )

        normalized = _normalized_lookup_row(
            lookup_row=lookup_row,
            citation=citation,
            start_index=start_index,
            end_index=end_index,
        )
        status = int(normalized.get("status") or 0)
        if status not in {200, 300}:
            return CitationResolution(authority_matches=[], lookup_row=normalized)

        authority_matches = _authority_matches_from_lookup(
            lookup_row=normalized,
            inventory=self.inventory,
        )
        return CitationResolution(authority_matches=authority_matches, lookup_row=normalized)


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


def external_lookup_unavailable_row(
    *,
    citation: str,
    start_index: int,
    end_index: int,
    status: int = 429,
    error_message: str = "external citation lookup unavailable",
) -> dict[str, Any]:
    return {
        "citation": citation,
        "normalized_citations": [citation],
        "start_index": start_index,
        "end_index": end_index,
        "status": status,
        "error_message": error_message,
        "clusters": [],
    }


def _exception_status(exc: Exception) -> int:
    for attr in ("status", "code"):
        value = getattr(exc, attr, None)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            continue
    return 0


def _select_lookup_row(
    *,
    lookup_rows: list[dict[str, Any]],
    citation: str,
    start_index: int,
    end_index: int,
    ) -> dict[str, Any] | None:
    if not lookup_rows:
        return None
    for row in lookup_rows:
        row_start = _int_or_default(row.get("start_index"), start_index)
        row_end = _int_or_default(row.get("end_index"), end_index)
        if row_start == start_index and row_end == end_index:
            return row
    normalized_targets = {_normalize_citation_key(citation)}
    for row in lookup_rows:
        row_values = [
            str(row.get("citation") or ""),
            *[str(value) for value in row.get("normalized_citations") or []],
        ]
        if normalized_targets & {_normalize_citation_key(value) for value in row_values if value}:
            return row
    return lookup_rows[0]


def _normalized_lookup_row(
    *,
    lookup_row: dict[str, Any],
    citation: str,
    start_index: int,
    end_index: int,
) -> dict[str, Any]:
    normalized_citations = lookup_row.get("normalized_citations")
    if not isinstance(normalized_citations, list) or not normalized_citations:
        normalized_citations = [str(lookup_row.get("citation") or citation)]
    clusters = lookup_row.get("clusters")
    if not isinstance(clusters, list):
        clusters = []
    return {
        "citation": str(lookup_row.get("citation") or citation),
        "normalized_citations": [str(value) for value in normalized_citations],
        "start_index": _int_or_default(lookup_row.get("start_index"), start_index),
        "end_index": _int_or_default(lookup_row.get("end_index"), end_index),
        "status": _int_or_default(lookup_row.get("status"), 404),
        "error_message": str(lookup_row.get("error_message") or ""),
        "clusters": clusters,
    }


def _authority_matches_from_lookup(
    *,
    lookup_row: dict[str, Any],
    inventory: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    status = int(lookup_row.get("status") or 0)
    if status == 300:
        return _authority_matches_from_clusters(lookup_row=lookup_row, inventory=inventory)
    inventory_matches = _inventory_matches_for_lookup(lookup_row=lookup_row, inventory=inventory)
    if inventory_matches:
        return inventory_matches
    return [
        _authority_row_from_cluster(cluster, fallback_citation=str(lookup_row.get("citation") or ""))
        for cluster in lookup_row.get("clusters", [])
        if isinstance(cluster, dict)
    ]


def _authority_matches_from_clusters(
    *,
    lookup_row: dict[str, Any],
    inventory: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for cluster in lookup_row.get("clusters", []):
        if not isinstance(cluster, dict):
            continue
        cluster_citations = _cluster_citations(cluster)
        matches = _inventory_matches_for_candidates(candidates=cluster_citations, inventory=inventory)
        rows = matches or [_authority_row_from_cluster(cluster, fallback_citation=str(lookup_row.get("citation") or ""))]
        for row in rows:
            key = str(row.get("authority_id") or row.get("canonical_citation") or "")
            if key and key not in seen:
                seen.add(key)
                out.append(row)
    if out:
        return out
    return _inventory_matches_for_lookup(lookup_row=lookup_row, inventory=inventory)


def _inventory_matches_for_lookup(
    *,
    lookup_row: dict[str, Any],
    inventory: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    candidate_citations = [
        str(lookup_row.get("citation") or ""),
        *[str(value) for value in lookup_row.get("normalized_citations") or []],
    ]
    for cluster in lookup_row.get("clusters", []):
        if isinstance(cluster, dict):
            candidate_citations.extend(_cluster_citations(cluster))
    return _inventory_matches_for_candidates(candidates=candidate_citations, inventory=inventory)


def _inventory_matches_for_candidates(
    *,
    candidates: list[str],
    inventory: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    matches: list[dict[str, Any]] = []
    for candidate in candidates:
        for row in inventory.get(candidate, []):
            key = str(row.get("authority_id") or row.get("canonical_citation") or candidate)
            if key not in seen:
                seen.add(key)
                matches.append(row)
    return matches


def _authority_row_from_cluster(cluster: dict[str, Any], *, fallback_citation: str) -> dict[str, Any]:
    canonical = _cluster_citations(cluster)
    canonical_citation = canonical[0] if canonical else fallback_citation
    parsed = _parse_citation_parts(canonical_citation)
    cluster_id = cluster.get("id") or cluster.get("cluster_id") or cluster.get("absolute_url") or canonical_citation
    date_filed = str(cluster.get("date_filed") or cluster.get("dateFiled") or "")
    year = str(cluster.get("year") or (date_filed[:4] if re.match(r"\d{4}", date_filed) else ""))
    row = {
        "authority_id": _authority_id_from_cluster_id(cluster_id),
        "canonical_citation": canonical_citation,
        "case_name": str(cluster.get("case_name") or cluster.get("caseName") or cluster.get("case_name_full") or ""),
        "court": str(cluster.get("court") or ""),
        "year": year,
        "reporter": parsed.get("reporter", ""),
        "volume": parsed.get("volume", ""),
        "page": parsed.get("page", ""),
        "pages": {},
    }
    source_url = _cluster_source_url(cluster)
    if source_url:
        row["source_url"] = source_url
    return row


def _cluster_source_url(cluster: dict[str, Any]) -> str:
    for key in ("absolute_url", "source_url", "url", "frontend_url"):
        value = str(cluster.get(key) or "").strip()
        if value.startswith("https://") or value.startswith("http://"):
            return value
        if value.startswith("/"):
            return f"https://www.courtlistener.com{value}"
    return ""


def _cluster_citations(cluster: dict[str, Any]) -> list[str]:
    out: list[str] = []
    citations = cluster.get("citations")
    if isinstance(citations, list):
        for row in citations:
            if isinstance(row, dict):
                citation = _citation_from_parts(row.get("volume"), row.get("reporter"), row.get("page"))
                if citation:
                    out.append(citation)
            elif row:
                out.append(str(row))
    for key in ("canonical_citation", "citation", "cite"):
        value = cluster.get(key)
        if value:
            out.append(str(value))
    return list(dict.fromkeys(out))


def _citation_from_parts(volume: Any, reporter: Any, page: Any) -> str:
    if volume is None or reporter is None or page is None:
        return ""
    return f"{volume} {reporter} {page}".strip()


def _parse_citation_parts(citation: str) -> dict[str, str]:
    match = re.match(r"^\s*(?P<volume>\d+)\s+(?P<reporter>.+?)\s+(?P<page>\d+)\s*$", citation)
    if not match:
        return {}
    return {
        "volume": match.group("volume"),
        "reporter": _normalized_reporter_text(match.group("reporter")),
        "page": match.group("page"),
    }


def _authority_id_from_cluster_id(cluster_id: Any) -> str:
    value = str(cluster_id or "").strip().casefold()
    value = re.sub(r"^https?://www\.courtlistener\.com/", "", value)
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return f"courtlistener_cluster_{value or 'unknown'}"


def _normalize_citation_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _normalized_reporter_text(reporter: str) -> str:
    compact = re.sub(r"\s+", "", reporter)
    if compact in {"U.S.", "US"}:
        return "U.S."
    mapping = {
        "F.2d": "F.2d",
        "F.3d": "F.3d",
        "F.4th": "F.4th",
        "F.Supp.": "F. Supp.",
        "F.Supp.2d": "F. Supp. 2d",
        "F.Supp.3d": "F. Supp. 3d",
        "S.Ct.": "S. Ct.",
        "A.D.3d": "A.D.3d",
        "AD3d": "A.D.3d",
        "WL": "WL",
        "ILApp": "IL App",
    }
    if compact in mapping:
        return mapping[compact]
    return re.sub(r"\s+", " ", reporter).strip()


def _int_or_default(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def unsupported_reporter_lookup_row(
    *,
    citation: str,
    start_index: int,
    end_index: int,
) -> dict[str, Any]:
    return {
        "citation": citation,
        "normalized_citations": [citation],
        "start_index": start_index,
        "end_index": end_index,
        "status": 400,
        "error_message": "unsupported_reporter",
        "clusters": [],
    }


def _load_inventory(path: Path) -> dict[str, list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, list[dict[str, Any]]] = {}
    for row in data.get("authorities", []):
        citation = str(row.get("canonical_citation") or "").strip()
        if citation:
            out.setdefault(citation, []).append(row)
    return out
