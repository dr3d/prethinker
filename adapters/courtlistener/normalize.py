from __future__ import annotations

import re
from typing import Any

from adapters.courtlistener.models import LegalSourceRecord


_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


def normalize_opinion_record(raw: dict[str, Any]) -> LegalSourceRecord:
    """Normalize a CourtListener opinion/search result-like payload.

    CourtListener API shapes differ by endpoint. This function accepts a small
    tolerant subset suitable for first-pass harness generation.
    """

    source_id = _first_text(raw, "id", "absolute_url", "cluster_id", default="unknown")
    title = _first_text(raw, "caseName", "case_name", "caseNameFull", "caption", "name")
    court = _court_name(raw)
    date_filed = _first_text(raw, "dateFiled", "date_filed", "date_created", "dateArgued")
    judges = _listish(raw.get("judge") or raw.get("judges") or raw.get("panel"))
    citations = _citations(raw)
    text_excerpt = _excerpt(raw)
    provenance_url = _provenance_url(raw)
    return LegalSourceRecord(
        source="courtlistener",
        source_kind="opinion",
        source_id=str(source_id),
        title=title,
        court=court,
        date_filed=date_filed,
        judges=judges,
        parties=[],
        attorneys=[],
        citations=citations,
        text_excerpt=text_excerpt,
        provenance_url=provenance_url,
        metadata={
            "cluster_id": raw.get("cluster_id") or raw.get("cluster"),
            "absolute_url": raw.get("absolute_url"),
            "download_url": raw.get("download_url"),
        },
    )


def _first_text(raw: dict[str, Any], *keys: str, default: str | None = None) -> str | None:
    for key in keys:
        value = raw.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def _court_name(raw: dict[str, Any]) -> str | None:
    court = raw.get("court")
    if isinstance(court, dict):
        return _first_text(court, "full_name", "short_name", "id")
    return _first_text(raw, "court", "court_id", "court_citation_string")


def _listish(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    parts = re.split(r"\s*;\s*|\s*,\s+(?=[A-Z][A-Za-z. -]+$)", text)
    return [part.strip() for part in parts if part.strip()]


def _citations(raw: dict[str, Any]) -> list[str]:
    citations = raw.get("citation") or raw.get("citations") or raw.get("neutral_cite")
    if isinstance(citations, list):
        out: list[str] = []
        for item in citations:
            if isinstance(item, dict):
                text = _first_text(item, "cite", "citation", "volume")
            else:
                text = str(item).strip()
            if text:
                out.append(text)
        return out
    text = str(citations or "").strip()
    return [text] if text else []


def _excerpt(raw: dict[str, Any]) -> str:
    text = _first_text(raw, "snippet", "plain_text", "html", "html_with_citations", "text", default="") or ""
    text = _TAG_RE.sub(" ", text)
    text = _SPACE_RE.sub(" ", text).strip()
    return text[:2000]


def _provenance_url(raw: dict[str, Any]) -> str | None:
    absolute = str(raw.get("absolute_url") or "").strip()
    if absolute.startswith("http"):
        return absolute
    if absolute.startswith("/"):
        return "https://www.courtlistener.com" + absolute
    return None
